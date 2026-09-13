extends SceneTree

## Per-character auto-tuner.
##
##   godot --headless --path game --script res://sim/tune_roster.gd
##
## Hand-balancing this roster failed twice, and both times for the same reason:
## several knobs moved at once, so nothing could be attributed. Koruyucu lost
## four stats and fell from 88% to 38%; Sürgün gained three and went from 50%
## to 100%.
##
## Characters never meet each other in a run, so each one is an independent
## one-dimensional problem, and weapon damage moves win rate in a single
## direction. That is exactly the shape a binary search needs. This tunes each
## character separately to the same target and prints the damage values to
## write back into characters.gd.

const Pool := preload("res://scripts/combat/upgrade_pool.gd")
const Roster := preload("res://autoload/characters.gd")
const RunScene := preload("res://scenes/run.tscn")

const STEP := 1.0 / 60.0
const MAX_FRAMES := 18000
const RUNS := 6
const META := 5
const TARGET := 0.55          ## Mid-progression players should win a bit more
                              ## than half their runs on a character they paid for.
const TOLERANCE := 0.09
const ITERATIONS := 5

var _run: Node3D
var _picks := {}

func _initialize() -> void:
	var started := Time.get_ticks_msec()
	print("\n=== ROSTER TUNER: one character at a time ===")
	print("target %.0f%% win at meta %d, %d runs per probe\n" % [
		TARGET * 100.0, META, RUNS])

	var settled: Array = []
	for c in Roster.ROSTER:
		settled.append(_tune(c))

	print("\n--- WRITE THESE INTO characters.gd ---")
	for s in settled:
		print("  %-10s damage %5.2f  ->  %5.2f   (win %.0f%%)" % [
			s.name, s.was, s.now, s.win * 100.0])
	print("\nelapsed %.1fs" % ((Time.get_ticks_msec() - started) / 1000.0))
	quit()

func _tune(character: Dictionary) -> Dictionary:
	print("%s (damage %.1f)" % [character.name, character.weapon.damage])
	var lo := 0.45
	var hi := 2.20
	var best := 1.0
	var best_win := 0.0

	for i in ITERATIONS:
		var mid := (lo + hi) * 0.5
		var win := _win_rate(character.id, mid)
		print("   probe %d  x%.3f  win=%5.1f%%" % [i + 1, mid, win * 100.0])
		best = mid
		best_win = win
		if win < TARGET:
			lo = mid          ## Too weak: give the weapon more damage.
		else:
			hi = mid
		if absf(win - TARGET) <= TOLERANCE:
			break

	return {
		"name": character.name,
		"was": character.weapon.damage,
		"now": character.weapon.damage * best,
		"win": best_win,
	}

func _win_rate(character_id: String, scale: float) -> float:
	var wins := 0
	for i in RUNS:
		if _play(character_id, scale, i * 104729 + META + 1):
			wins += 1
	return float(wins) / RUNS

func _play(character_id: String, scale: float, seed_value: int) -> bool:
	_run = RunScene.instantiate()
	_run.character_id = character_id
	_run.meta_level = META
	_run.run_seed = seed_value
	_run.auto_kite = true
	_run.damage_scale = scale
	_run.begin()
	_run.level_up_offered.connect(_on_level_up)
	_picks = {}

	var frame := 0
	while frame < MAX_FRAMES and _run.state.alive and not _run.state.is_over():
		_run.step(STEP)
		frame += 1

	var won: bool = _run.state.alive
	_run.free()
	return won

func _on_level_up(options: Array) -> void:
	var pick: Dictionary = Pool.choose(options, _picks)
	_picks[pick.id] = _picks.get(pick.id, 0) + 1
	_run.choose_upgrade(pick)
