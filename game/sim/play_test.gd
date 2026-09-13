extends SceneTree

## Plays the real scene, headless, many times.
##
##   godot --headless --path game --script res://sim/play_test.gd
##
## The balance simulator proves the numbers work in the abstract; this proves
## the game actually built from them behaves the same way. It drives run.tscn
## with a kiting bot at a fixed timestep and reports a win rate that can be
## compared directly against sim/balance_sim.gd. When the two disagree, the
## game has a bug the model cannot see -- which is how the missed-shot and
## infinite-kiting problems were found.

const Pool := preload("res://scripts/combat/upgrade_pool.gd")
const RunScene := preload("res://scenes/run.tscn")

const FPS := 60.0
const STEP := 1.0 / FPS
const MAX_FRAMES := 18000          ## 300 seconds at 60 fps.
const RUNS := 8

var _run: Node3D
var _picks := {}
var _finished := false

func _initialize() -> void:
	var started := Time.get_ticks_msec()
	print("\n=== PLAY TEST: real scene, %d runs per meta level ===\n" % RUNS)
	print("meta │ win%%  │ avg survive │ avg level │ avg kills │ orbs left │ peak swarm")
	print("─────┼───────┼─────────────┼───────────┼───────────┼───────────┼───────────")
	for meta in [0, 5, 10, 20]:
		_batch(meta)
	print("\nelapsed %.1fs" % ((Time.get_ticks_msec() - started) / 1000.0))
	quit()

func _batch(meta_level: int) -> void:
	var wins := 0
	var survive := 0.0
	var levels := 0.0
	var kills := 0.0
	var orbs_left := 0.0
	var peak := 0

	for i in RUNS:
		var r := _play(meta_level, i * 104729 + meta_level + 1)
		if r.won:
			wins += 1
		survive += r.survived
		levels += r.level
		kills += r.kills
		orbs_left += r.orbs_left
		peak = maxi(peak, r.peak)

	print("%4d │ %4.1f%% │ %10.1fs │ %9.1f │ %9.0f │ %9.1f │ %9d" % [
		meta_level, float(wins) / RUNS * 100.0, survive / RUNS,
		levels / RUNS, kills / RUNS, orbs_left / RUNS, peak])

func _play(meta_level: int, seed_value: int) -> Dictionary:
	_run = RunScene.instantiate()
	_run.meta_level = meta_level
	_run.run_seed = seed_value
	_run.auto_kite = true
	_run.begin()                   # No scene tree here, so open the run by hand.

	_run.level_up_offered.connect(_on_level_up)
	_picks = {}
	_finished = false

	var peak := 0
	var frame := 0
	while frame < MAX_FRAMES and not _finished and _run.state.alive:
		_run.step(STEP)
		peak = maxi(peak, _run.swarm.count)
		frame += 1

	var s = _run.state
	var result := {
		"won": s.alive, "survived": s.elapsed, "level": s.level,
		"kills": s.kills, "orbs_left": _run.orbs.count, "peak": peak,
	}
	_run.free()
	return result

func _on_level_up(options: Array) -> void:
	var pick: Dictionary = Pool.choose(options, _picks)
	_picks[pick.id] = _picks.get(pick.id, 0) + 1
	_run.choose_upgrade(pick)
