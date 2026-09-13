extends SceneTree

## Plays every character and checks none of them dominates.
##
##   godot --headless --path game --script res://sim/roster_test.gd
##
## A roster is healthy when each entry is clearly best at something and clearly
## worst at something else. What this test is really looking for is the failure
## where one character simply wins more than the rest at everything, which turns
## the unlock ladder into a single correct answer and kills the reason to keep
## playing the others.

const Pool := preload("res://scripts/combat/upgrade_pool.gd")
const Roster := preload("res://autoload/characters.gd")
const RunScene := preload("res://scenes/run.tscn")

const STEP := 1.0 / 60.0
const MAX_FRAMES := 18000
const RUNS := 8
const META := 5

var _run: Node3D
var _picks := {}

func _initialize() -> void:
	var started := Time.get_ticks_msec()
	print("\n=== ROSTER TEST: %d runs each at meta %d ===\n" % [RUNS, META])
	print("character   │ win%%  │ survive │ level │ kills │ base dps │ unlock")
	print("────────────┼───────┼─────────┼───────┼───────┼──────────┼───────")

	var results: Array = []
	for c in Roster.ROSTER:
		var r := _batch(c)
		results.append(r)
		print("%-11s │ %4.1f%% │ %6.1fs │ %5.1f │ %5.0f │ %8.0f │ %6d" % [
			c.name, r.win * 100.0, r.survive, r.level, r.kills,
			Roster.base_dps(c), c.unlock_cost])

	_verdict(results)
	print("\nelapsed %.1fs" % ((Time.get_ticks_msec() - started) / 1000.0))
	quit()

func _batch(character: Dictionary) -> Dictionary:
	var wins := 0
	var survive := 0.0
	var level := 0.0
	var kills := 0.0
	for i in RUNS:
		var r := _play(character.id, i * 104729 + META + 1)
		if r.won:
			wins += 1
		survive += r.survived
		level += r.level
		kills += r.kills
	return {
		"name": character.name,
		"win": float(wins) / RUNS,
		"survive": survive / RUNS,
		"level": level / RUNS,
		"kills": kills / RUNS,
	}

func _play(character_id: String, seed_value: int) -> Dictionary:
	_run = RunScene.instantiate()
	_run.character_id = character_id
	_run.meta_level = META
	_run.run_seed = seed_value
	_run.auto_kite = true
	_run.begin()
	_run.level_up_offered.connect(_on_level_up)
	_picks = {}

	var frame := 0
	while frame < MAX_FRAMES and _run.state.alive and not _run.state.is_over():
		_run.step(STEP)
		frame += 1

	var s = _run.state
	var out := {"won": s.alive, "survived": s.elapsed, "level": s.level, "kills": s.kills}
	_run.free()
	return out

func _on_level_up(options: Array) -> void:
	var pick: Dictionary = Pool.choose(options, _picks)
	_picks[pick.id] = _picks.get(pick.id, 0) + 1
	_run.choose_upgrade(pick)

func _verdict(results: Array) -> void:
	print("\n--- VERDICT ---")
	var best: Dictionary = results[0]
	var worst: Dictionary = results[0]
	for r in results:
		if r.win > best.win:
			best = r
		if r.win < worst.win:
			worst = r

	var spread: float = best.win - worst.win
	print("strongest %s (%.0f%%), weakest %s (%.0f%%), spread %.0f pts" % [
		best.name, best.win * 100.0, worst.name, worst.win * 100.0, spread * 100.0])

	if spread > 0.45:
		print("UNBALANCED  one character is simply better; the unlock ladder has")
		print("            a single correct answer and the rest are decoration.")
	else:
		print("ACCEPTABLE  no character dominates the field outright.")

	# A roster can be balanced on win rate and still be boring, so check that
	# the characters actually play differently.
	var kill_lo: float = results[0].kills
	var kill_hi: float = results[0].kills
	for r in results:
		kill_lo = minf(kill_lo, r.kills)
		kill_hi = maxf(kill_hi, r.kills)
	if kill_hi > 0.0 and kill_lo / kill_hi > 0.75:
		print("SAMEY       every character kills at nearly the same rate; the")
		print("            trades are not showing up in how a run actually feels.")
	else:
		print("DISTINCT    kill rates differ by %.0f%%, so the trades are real." % [
			(1.0 - kill_lo / kill_hi) * 100.0])
