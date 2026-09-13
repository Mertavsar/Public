extends Node3D

## Orchestrates one run: input, systems, contact damage, level ups, end state.
##
## Note on contact damage. The balance simulator approximates being hit as
## "enemies beyond what you can outrun". Here it is literal: whatever is
## actually touching you deals damage. The two agree because a player who out-
## damages the spawn rate never lets bodies reach them, which is the same
## pressure the model expresses arithmetically.

const B := preload("res://autoload/balance.gd")
const RunStateScript := preload("res://scripts/systems/run_state.gd")

@export var meta_level := 0
@export var run_seed := 0        ## 0 means randomise.
@export var enemy_speed_override := 0.0   ## Tuner hook; 0 means use Balance.
@export var headless_input := Vector3.ZERO   ## Test hook; see sim/play_test.gd.
@export var auto_kite := false               ## Test hook: flee the nearest enemy.

var state: RunState
var paused_for_level_up := false

var player: Player
var swarm: Swarm
var weapon: Weapon
var orbs: Orbs

var _begun := false

signal run_finished(result: Dictionary)
signal level_up_offered(options: Array)

func _ready() -> void:
	begin()

## Idempotent. Binds the subsystems and opens a fresh run. Set meta_level before
## calling. The live game reaches this through _ready; the headless play test
## calls it directly, because a custom main loop never enters the scene tree.
func begin() -> void:
	if _begun:
		return
	_begun = true
	player = get_node("Player")
	swarm = get_node("Swarm")
	weapon = get_node("Weapon")
	orbs = get_node("Orbs")
	state = RunStateScript.new(meta_level)
	if run_seed != 0:
		state.rng.seed = run_seed
		swarm.set_seed(run_seed)
	state.leveled_up.connect(_on_leveled_up)
	swarm.enemy_killed.connect(_on_enemy_killed)

func _process(delta: float) -> void:
	step(delta)

## One frame of the run. Split out from _process so the headless play test can
## drive thousands of frames as fast as the CPU allows instead of in real time.
func step(delta: float) -> void:
	begin()
	if paused_for_level_up or state == null or state.is_over():
		return

	state.tick(delta)
	player.move(delta, _input_direction(), state.move_speed())
	_clamp_to_arena()

	var enemy_speed := _enemy_speed()
	swarm.update(delta, state.elapsed, player.position, enemy_speed, player.facing)
	weapon.update(delta, state, swarm, player.position, enemy_speed)

	var collected := orbs.update(delta, player.position, state.pickup_radius())
	if collected > 0:
		state.add_xp(float(collected) * B.ENEMY.xp_value)

	_apply_contact_damage(delta)

	if state.is_over():
		_finish()

## Enemies move slower than the player so kiting is possible but costly.
func _enemy_speed() -> float:
	var factor: float = enemy_speed_override if enemy_speed_override > 0.0 \
		else B.ENEMY.speed_factor
	return B.PLAYER.move_speed * factor

## The arena has an edge. Running in a straight line forever is not a strategy.
func _clamp_to_arena() -> void:
	var flat := Vector3(player.position.x, 0.0, player.position.z)
	if flat.length() > B.ARENA_RADIUS:
		flat = flat.normalized() * B.ARENA_RADIUS
		player.position.x = flat.x
		player.position.z = flat.z

func _apply_contact_damage(delta: float) -> void:
	var touching := swarm.touching(player.position, Player.RADIUS)
	if touching > 0:
		state.take_damage(float(touching) * B.ENEMY.contact_dps * delta)

func _input_direction() -> Vector3:
	if auto_kite:
		return _flee_direction()
	if headless_input != Vector3.ZERO:
		return headless_input
	var v := Input.get_vector("move_left", "move_right", "move_up", "move_down")
	return Vector3(v.x, 0.0, v.y)

## Simple survival AI for headless play-testing: run away from the crowd.
func _flee_direction() -> Vector3:
	if swarm.count == 0:
		return Vector3.ZERO
	var away := Vector3.ZERO
	var sampled := 0
	for i in mini(swarm.count, 24):
		var diff := player.position - swarm.positions[i]
		diff.y = 0.0
		var d := diff.length()
		if d > 0.001:
			away += diff / (d * d)      # Closer enemies push harder.
			sampled += 1
	if sampled == 0:
		return Vector3.ZERO
	away.y = 0.0
	return away.normalized()

func _on_enemy_killed(pos: Vector3) -> void:
	orbs.spawn(pos)

func _on_leveled_up(options: Array) -> void:
	paused_for_level_up = true
	level_up_offered.emit(options)

func choose_upgrade(upgrade: Dictionary) -> void:
	state.apply_upgrade(upgrade)
	paused_for_level_up = false

func _finish() -> void:
	run_finished.emit({
		"won": state.alive,
		"survived": state.elapsed,
		"level": state.level,
		"kills": state.kills,
		"gold": state.gold,
		"taken": state.taken.duplicate(),
	})
