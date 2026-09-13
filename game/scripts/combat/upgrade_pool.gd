extends RefCounted
class_name UpgradePool

## The three-choice level-up draft. Each entry mutates the run's stat block.
##
## "weight" is how often the option is offered; "ai_value" is how attractive it
## is to the simulated player, so headless runs approximate a competent human
## rather than picking at random.

const UPGRADES := [
	{"id": "damage", "name": "Keskin Uçlar", "desc": "Hasar +20%",
		"weight": 1.0, "ai_value": 1.00, "stat": "damage_mult", "add": 0.20},
	{"id": "attack_speed", "name": "Hızlı Tetik", "desc": "Atış hızı +15%",
		"weight": 1.0, "ai_value": 0.95, "stat": "attack_speed_mult", "add": 0.15},
	{"id": "projectile", "name": "Çatal Atış", "desc": "+1 mermi",
		"weight": 0.45, "ai_value": 1.40, "stat": "projectiles", "add": 1.0},
	{"id": "max_hp", "name": "Kalın Zırh", "desc": "Can +25",
		"weight": 0.9, "ai_value": 0.60, "stat": "bonus_hp", "add": 25.0},
	{"id": "move_speed", "name": "Hafif Ayak", "desc": "Hareket +12%",
		"weight": 0.9, "ai_value": 0.75, "stat": "move_mult", "add": 0.12},
	{"id": "pickup", "name": "Mıknatıs", "desc": "Toplama alanı +40%",
		"weight": 0.7, "ai_value": 0.45, "stat": "pickup_mult", "add": 0.40},
	{"id": "regen", "name": "Yenilenme", "desc": "Saniyede 1.2 can",
		"weight": 0.5, "ai_value": 0.70, "stat": "regen", "add": 1.2},
	{"id": "armor", "name": "Sertleşme", "desc": "Alınan hasar -8%",
		"weight": 0.6, "ai_value": 0.85, "stat": "armor", "add": 0.08},
]

## Draw `count` distinct upgrade options, weighted.
static func draft(rng: RandomNumberGenerator, count: int = 3) -> Array:
	var pool := UPGRADES.duplicate()
	var drawn: Array = []
	while drawn.size() < count and not pool.is_empty():
		var total := 0.0
		for u in pool:
			total += u.weight
		var roll := rng.randf() * total
		var acc := 0.0
		for i in pool.size():
			acc += pool[i].weight
			if roll <= acc:
				drawn.append(pool[i])
				pool.remove_at(i)
				break
	return drawn

## How a reasonably skilled player picks: best value, with diminishing returns
## on options already taken several times.
static func choose(options: Array, taken: Dictionary) -> Dictionary:
	var best: Dictionary = options[0]
	var best_score := -INF
	for opt in options:
		var owned: int = taken.get(opt.id, 0)
		var score: float = opt.ai_value * pow(0.88, float(owned))
		if score > best_score:
			best_score = score
			best = opt
	return best
