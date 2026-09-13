extends SceneTree

## Auto-tuner. Binary-searches the enemy health curve until the win rate lands
## inside the target band, then prints the value to paste into Balance.
##
##   godot --headless --path game --script res://sim/tune.gd
##
## This is the piece that replaces a human playtesting the run a thousand times.

const CombatModel := preload("res://scripts/combat/combat_model.gd")

const RUNS := 1200
const REFERENCE_META := 5          ## Tune against a mid-progression player.
const TARGET := 0.32               ## Aim for the middle of the 25-40% band.
const ITERATIONS := 16

func _initialize() -> void:
	print("\n=== AUTO-TUNER: enemy health curve ===")
	print("target win rate %.0f%% at meta %d, %d runs per probe\n" % [
		TARGET * 100.0, REFERENCE_META, RUNS])

	var lo := 1.050       ## Gentle curve -> player wins.
	var hi := 1.120       ## Brutal curve -> player dies.
	var best := lo

	for i in ITERATIONS:
		var mid := (lo + hi) * 0.5
		var win := _win_rate(mid, REFERENCE_META)
		print("  probe %2d  hp_growth=%.4f  win=%5.1f%%" % [i + 1, mid, win * 100.0])
		best = mid
		if win > TARGET:
			lo = mid      ## Too easy: steepen the curve.
		else:
			hi = mid      ## Too hard: soften it.
		if absf(win - TARGET) < 0.01:
			break

	print("\n--- RESULT ---")
	print("hp_growth_per_10s = %.4f" % best)
	print("\nWin rate across meta progression at this value:")
	for meta in [0, 5, 10, 20]:
		print("  meta %2d -> %5.1f%%" % [meta, _win_rate(best, meta) * 100.0])
	quit()

func _win_rate(hp_growth: float, meta_level: int) -> float:
	var wins := 0
	for i in RUNS:
		var m := CombatModel.new(i * 7919 + meta_level, meta_level, {"hp_growth": hp_growth})
		if m.run().won:
			wins += 1
	return float(wins) / RUNS
