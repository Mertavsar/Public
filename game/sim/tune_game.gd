extends SceneTree

## Auto-tuner for the real game.
##
##   godot --headless --path game --script res://sim/tune_game.gd
##
## sim/tune.gd tunes the abstract model; this tunes the thing players actually
## touch, by playing it. It binary-searches enemy speed -- the single knob that
## decides whether running away is a strategy -- until the win rate lands in
## the target band. Slower than the model tuner by three orders of magnitude,
## which is exactly why both exist.

const Pool := preload("res://scripts/combat/upgrade_pool.gd")
const RunScene := preload("res://scenes/run.tscn")

const STEP := 1.0 / 60.0
const MAX_FRAMES := 18000
const RUNS := 6
const REFERENCE_META := 5
const TARGET := 0.32
const ITERATIONS := 7

var _run: Node3D
var _picks := {}
var _finished := false

func _initialize() -> void:
	var started := Time.get_ticks_msec()
	print("\n=== AUTO-TUNER: enemy speed, played not modelled ===")
	print("target %.0f%% win at meta %d, %d runs per probe\n" % [
		TARGET * 100.0, REFERENCE_META, RUNS])

	var lo := 0.70        ## Slow enemies -> kiting always works -> player wins.
	var hi := 1.15        ## Enemies outrun you -> player dies.
	var best := lo

	for i in ITERATIONS:
		var mid := (lo + hi) * 0.5
		var win := _win_rate(mid, REFERENCE_META)
		print("  probe %d  speed_factor=%.3f  win=%5.1f%%" % [i + 1, mid, win * 100.0])
		best = mid
		if win > TARGET:
			lo = mid      ## Too easy: speed the enemies up.
		else:
			hi = mid
		if absf(win - TARGET) < 0.06:
			break

	print("\n--- RESULT ---")
	print("speed_factor = %.3f" % best)
	print("\nWin rate across meta progression:")
	for meta in [0, 5, 10, 20]:
		print("  meta %2d -> %5.1f%%" % [meta, _win_rate(best, meta) * 100.0])
	print("\nelapsed %.1fs" % ((Time.get_ticks_msec() - started) / 1000.0))
	quit()

func _win_rate(speed_factor: float, meta_level: int) -> float:
	var wins := 0
	for i in RUNS:
		if _play(speed_factor, meta_level, i * 104729 + meta_level + 1):
			wins += 1
	return float(wins) / RUNS

func _play(speed_factor: float, meta_level: int, seed_value: int) -> bool:
	_run = RunScene.instantiate()
	_run.meta_level = meta_level
	_run.run_seed = seed_value
	_run.auto_kite = true
	_run.enemy_speed_override = speed_factor
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
