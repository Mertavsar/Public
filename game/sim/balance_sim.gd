extends SceneTree

## Headless balance harness.
##
##   godot --headless --path game --script res://sim/balance_sim.gd
##
## Runs the combat model thousands of times and reports whether the run is
## tuned. Target band for a survivor game: players should win roughly a third
## of the time at mid meta progression -- often enough to feel achievable,
## rarely enough to keep them coming back.

const CombatModel := preload("res://scripts/combat/combat_model.gd")

const RUNS := 2000
const TARGET_WIN_LOW := 0.25
const TARGET_WIN_HIGH := 0.40

func _initialize() -> void:
	print("\n=== SURVIVOR3D BALANCE REPORT ===")
	print("%d runs per meta level\n" % RUNS)
	print("meta │ win%%  │ median survive │ avg level │ avg kills │ end DPS")
	print("─────┼───────┼────────────────┼───────────┼───────────┼────────")

	var verdicts: Array = []
	for meta in [0, 5, 10, 20]:
		var r := _batch(meta)
		verdicts.append({"meta": meta, "win": r.win_rate})
		print("%4d │ %4.1f%% │ %13.1fs │ %9.1f │ %9.0f │ %6.0f" % [
			meta, r.win_rate * 100.0, r.median_survive,
			r.avg_level, r.avg_kills, r.avg_dps])

	print("\n--- Upgrade pick rates at meta 0 ---")
	var picks := _pick_rates(0)
	var ids := picks.keys()
	ids.sort_custom(func(a, b): return picks[a] > picks[b])
	for id in ids:
		print("  %-14s %5.2f picks/run" % [id, picks[id]])

	_verdict(verdicts)
	quit()

func _batch(meta_level: int) -> Dictionary:
	var wins := 0
	var survives: Array[float] = []
	var levels := 0.0
	var kills := 0.0
	var dps := 0.0
	for i in RUNS:
		var m := CombatModel.new(i * 7919 + meta_level, meta_level)
		var res := m.run()
		if res.won:
			wins += 1
		survives.append(res.survived)
		levels += res.level
		kills += res.kills
		dps += res.dps_end
	survives.sort()
	return {
		"win_rate": float(wins) / RUNS,
		"median_survive": survives[RUNS / 2],
		"avg_level": levels / RUNS,
		"avg_kills": kills / RUNS,
		"avg_dps": dps / RUNS,
	}

func _pick_rates(meta_level: int) -> Dictionary:
	var totals := {}
	for i in RUNS:
		var m := CombatModel.new(i * 7919 + meta_level, meta_level)
		var res := m.run()
		for id in res.taken:
			totals[id] = totals.get(id, 0.0) + res.taken[id]
	for id in totals:
		totals[id] = totals[id] / RUNS
	return totals

func _verdict(verdicts: Array) -> void:
	print("\n--- VERDICT ---")
	var mid: float = verdicts[1].win          # meta level 5 is the reference point
	if mid < TARGET_WIN_LOW:
		print("TOO HARD  (meta 5 win rate %.1f%%, target %.0f-%.0f%%)" % [
			mid * 100.0, TARGET_WIN_LOW * 100.0, TARGET_WIN_HIGH * 100.0])
		print("  Raise WEAPON.damage or lower ENEMY.hp_growth_per_10s.")
	elif mid > TARGET_WIN_HIGH:
		print("TOO EASY  (meta 5 win rate %.1f%%, target %.0f-%.0f%%)" % [
			mid * 100.0, TARGET_WIN_LOW * 100.0, TARGET_WIN_HIGH * 100.0])
		print("  Raise ENEMY.hp_growth_per_10s or SPAWN.ramp_per_second.")
	else:
		print("TUNED     (meta 5 win rate %.1f%%, inside target band)" % [mid * 100.0])

	var progression: float = verdicts[3].win - verdicts[0].win
	if progression < 0.15:
		print("WEAK META (meta 0 -> 20 only +%.1f pts; grinding feels pointless)" % [
			progression * 100.0])
	else:
		print("META OK   (meta 0 -> 20 adds +%.1f pts of win rate)" % [progression * 100.0])
