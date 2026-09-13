extends RefCounted
class_name RunState

## Live state of one run. Deliberately mirrors CombatModel's stat block key for
## key: the simulator tunes these numbers, this class spends them. If you add a
## stat here, add it there too or the balance report starts lying.

signal leveled_up(options: Array)
signal died()

const B := preload("res://autoload/balance.gd")
const Pool := preload("res://scripts/combat/upgrade_pool.gd")

var rng := RandomNumberGenerator.new()
var stats := {}
var hp := 0.0
var level := 1
var xp := 0.0
var kills := 0
var gold := 0.0
var elapsed := 0.0
var alive := true
var taken := {}

func _init(meta_level: int = 0) -> void:
	rng.randomize()
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

func move_speed() -> float:
	return B.PLAYER.move_speed * stats.move_mult

func pickup_radius() -> float:
	return B.PLAYER.pickup_radius * stats.pickup_mult

func weapon_damage() -> float:
	return B.WEAPON.damage * stats.damage_mult

func weapon_cooldown() -> float:
	return B.WEAPON.cooldown / stats.attack_speed_mult

func projectile_count() -> int:
	return int(stats.projectiles)

func tick(delta: float) -> void:
	elapsed += delta
	if stats.regen > 0.0:
		hp = minf(hp + stats.regen * delta, max_hp())

func take_damage(amount: float) -> void:
	if not alive:
		return
	hp -= amount * (1.0 - stats.armor)
	if hp <= 0.0:
		hp = 0.0
		alive = false
		died.emit()

func add_kill() -> void:
	kills += 1
	gold += B.ENEMY.gold_per_kill

## Returns true when this XP triggered at least one level up.
func add_xp(amount: float) -> bool:
	xp += amount
	var gained := false
	while xp >= B.xp_to_next(level):
		xp -= B.xp_to_next(level)
		level += 1
		gained = true
		leveled_up.emit(Pool.draft(rng, 3))
	return gained

func apply_upgrade(upgrade: Dictionary) -> void:
	stats[upgrade.stat] = stats[upgrade.stat] + upgrade.add
	taken[upgrade.id] = taken.get(upgrade.id, 0) + 1
	if upgrade.stat == "bonus_hp":
		hp += upgrade.add        # Extra max HP is granted as healing too.

func is_over() -> bool:
	return not alive or elapsed >= B.RUN_DURATION
