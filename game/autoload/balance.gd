extends RefCounted
class_name Balance

## Single source of truth for every tunable number in the game.
##
## The headless balance simulator and the live game both read from here, so a
## number that was tuned in simulation is the number that ships. Never hardcode
## a combat value anywhere else.

const RUN_DURATION := 300.0          ## A full run is five minutes.
const BOSS_AT := 270.0               ## Boss spawns in the final thirty seconds.

const PLAYER := {
	"max_hp": 100.0,
	"move_speed": 5.0,
	"pickup_radius": 2.5,
	"contact_armor": 0.0,
}

## Starting weapon. DPS = damage / cooldown * projectiles.
const WEAPON := {
	"damage": 14.0,
	"cooldown": 0.35,
	"projectiles": 1,
	"range": 9.0,
}

## Enemies get tougher over time rather than being hand-placed per wave.
const ENEMY := {
	"base_hp": 14.0,
	"hp_growth_per_10s": 1.0902,   ## Auto-tuned. Do not hand-edit; run sim/tune.gd.
	"contact_dps": 7.0,               ## Damage one touching enemy deals per second.
	"xp_value": 1.0,
	"gold_per_kill": 0.35,
}

## How many enemies the player can outrun before taking contact damage.
## This is the knob that decides whether low DPS actually kills you.
const KITE_CAPACITY := 12.0

const SPAWN := {
	"base_rate": 2.0,                 ## Enemies per second at t=0.
	"ramp_per_second": 0.020,         ## Linear ramp across the run.
	"max_rate": 8.0,
}

## XP needed to reach the next level: xp_base * level ^ xp_exponent
const XP := {
	"base": 2.0,
	"exponent": 1.25,
}

## Permanent upgrades bought with gold between runs.
const META := {
	"hp_per_level": 8.0,
	"damage_per_level": 0.04,         ## +4% damage per meta level.
	"speed_per_level": 0.02,
	"max_level": 20,
}

static func enemy_hp_at(t: float) -> float:
	return ENEMY.base_hp * pow(ENEMY.hp_growth_per_10s, t / 10.0)

static func spawn_rate_at(t: float) -> float:
	return minf(SPAWN.base_rate + SPAWN.ramp_per_second * t, SPAWN.max_rate)

static func xp_to_next(level: int) -> float:
	return XP.base * pow(float(level), XP.exponent)
