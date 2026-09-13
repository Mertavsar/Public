extends RefCounted
class_name CombatModel

## Headless model of one run.
##
## Deliberately has no nodes, no physics and no rendering: it advances the run
## in fixed steps using only the numbers in Balance. The live game drives the
## same stat block through the same upgrade pool, so anything tuned here is
## true on device. This is what lets the run be balanced without a human
## playing it a thousand times.

const B := preload("res://autoload/balance.gd")
const Pool := preload("res://scripts/combat/upgrade_pool.gd")

const STEP := 0.1                     ## Simulation tick, in seconds.

var rng := RandomNumberGenerator.new()

# --- Run state -------------------------------------------------------------
var t := 0.0
var hp := 0.0
var level := 1
var xp := 0.0
var kills := 0.0
var gold := 0.0
var enemies_alive := 0.0              ## Fractional on purpose: this is a flow model.
var survived := 0.0
var won := false
var taken := {}                       ## upgrade id -> times picked

var stats := {}

## Optional per-run overrides, used by the auto-tuner to sweep a value without
## editing Balance. Empty in the shipped game.
var tuning := {}

func _init(seed_value: int = 0, meta_level: int = 0, tuning_overrides: Dictionary = {}) -> void:
	rng.seed = seed_value
	tuning = tuning_overrides
	stats = {
		"damage_mult": 1.0 + B.META.damage_per_level * meta_level,
		"attack_speed_mult": 1.0,
		"projectiles": float(B.WEAPON.projectiles),
		"bonus_hp": B.META.hp_per_level * meta_level,
		"move_mult": 1.0 + B.META.speed_per_level * meta_level,
		"pickup_mult": 1.0,
		"regen": 0.0,
		"armor": 0.0,
	}
	hp = max_hp()

func max_hp() -> float:
	return B.PLAYER.max_hp + stats.bonus_hp

func dps() -> float:
	return (B.WEAPON.damage / B.WEAPON.cooldown) \
		* stats.damage_mult * stats.attack_speed_mult * stats.projectiles

## Enemies the player can stay ahead of. Beyond this, bodies start landing hits.
func kite_capacity() -> float:
	return B.KITE_CAPACITY * stats.move_mult

func _enemy_hp() -> float:
	var growth: float = tuning.get("hp_growth", B.ENEMY.hp_growth_per_10s)
	return B.ENEMY.base_hp * pow(growth, t / 10.0)

func _spawn_rate() -> float:
	var ramp: float = tuning.get("spawn_ramp", B.SPAWN.ramp_per_second)
	return minf(B.SPAWN.base_rate + ramp * t, B.SPAWN.max_rate)

func run() -> Dictionary:
	while t < B.RUN_DURATION and hp > 0.0:
		_step()
	survived = t
	won = hp > 0.0
	return {
		"won": won, "survived": survived, "level": level,
		"kills": kills, "gold": gold, "hp_left": maxf(hp, 0.0),
		"dps_end": dps(), "taken": taken.duplicate(),
	}

func _step() -> void:
	# Spawning.
	enemies_alive += _spawn_rate() * STEP

	# Killing: damage output is spread across whatever is on screen.
	var ehp := _enemy_hp()
	var killed: float = minf(enemies_alive, dps() * STEP / ehp)
	enemies_alive -= killed
	kills += killed
	gold += killed * B.ENEMY.gold_per_kill
	_gain_xp(killed * B.ENEMY.xp_value)

	# Damage taken: only the overflow the player cannot outrun connects.
	var overflow: float = maxf(0.0, enemies_alive - kite_capacity())
	var incoming: float = overflow * B.ENEMY.contact_dps * STEP * (1.0 - stats.armor)
	hp -= incoming
	hp = minf(hp + stats.regen * STEP, max_hp())

	t += STEP

func _gain_xp(amount: float) -> void:
	xp += amount
	while xp >= B.xp_to_next(level):
		xp -= B.xp_to_next(level)
		level += 1
		_level_up()

func _level_up() -> void:
	var options := Pool.draft(rng, 3)
	if options.is_empty():
		return
	var pick: Dictionary = Pool.choose(options, taken)
	stats[pick.stat] = stats[pick.stat] + pick.add
	taken[pick.id] = taken.get(pick.id, 0) + 1
	if pick.stat == "bonus_hp":
		hp += pick.add          # New max HP is granted as healing too.
