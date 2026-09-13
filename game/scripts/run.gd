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
const Roster := preload("res://autoload/characters.gd")

@export var character_id := "sentinel"
@export var meta_level := 0
@export var run_seed := 0        ## 0 means randomise.
@export var hp_growth_override := 0.0     ## Tuner hook; 0 means use Balance.
@export var damage_scale := 1.0           ## Tuner hook; 1.0 means use the character.
@export var headless_input := Vector3.ZERO   ## Test hook; see sim/play_test.gd.
@export var auto_kite := false               ## Test hook: flee the nearest enemy.

var state: RunState
var paused_for_level_up := false

var player: Player
var swarm: Swarm
var weapon: Weapon
var orbs: Orbs
var debris: Debris
var camera: Camera3D
var muzzle: OmniLight3D

## Feedback state. None of this changes a single balance number; all of it
## changes whether the game reads as a game.
var shake := 0.0
var hitstop := 0.0
var muzzle_flash := 0.0
var _camera_home := Vector3.ZERO

signal hurt(amount: float)
signal levelled()

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
	debris = get_node("Debris")
	camera = get_node_or_null("Player/Camera")
	muzzle = get_node_or_null("Player/Muzzle")
	if camera:
		_camera_home = camera.position
	player.apply_character(Roster.by_id(character_id))
	state = RunStateScript.new(meta_level, character_id)
	swarm.hp_growth_override = hp_growth_override
	state.damage_scale = damage_scale
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

	# Hit-stop: the game hesitates on the frame you get hurt. A handful of
	# milliseconds, and it is most of why a hit feels like a hit.
	if hitstop > 0.0:
		hitstop = maxf(0.0, hitstop - delta)
		delta *= 0.18

	state.tick(delta)
	player.move(delta, _input_direction(), state.move_speed())
	_clamp_to_arena()

	var enemy_speed := _enemy_speed()
	swarm.update(delta, state.elapsed, player.position, enemy_speed, player.facing)
	var shots_before := weapon.count
	weapon.update(delta, state, swarm, player.position, enemy_speed)
	if weapon.count > shots_before:
		muzzle_flash = 1.0

	var collected := orbs.update(delta, player.position, state.pickup_radius())
	if collected > 0:
		state.add_xp(float(collected) * B.ENEMY.xp_value)

	_apply_contact_damage(delta)
	debris.update(delta)
	_decay_feedback(delta)

	if state.is_over():
		_finish()

## Enemies move slower than the player so kiting is possible but costly.
func _enemy_speed() -> float:
	return B.PLAYER.move_speed * B.ENEMY.speed_factor

## The arena has an edge. Running in a straight line forever is not a strategy.
func _clamp_to_arena() -> void:
	var flat := Vector3(player.position.x, 0.0, player.position.z)
	if flat.length() > B.ARENA_RADIUS:
		flat = flat.normalized() * B.ARENA_RADIUS
		player.position.x = flat.x
		player.position.z = flat.z

func _apply_contact_damage(delta: float) -> void:
	var touching := swarm.touching(player.position, Player.RADIUS)
	if touching <= 0:
		return
	var taken := float(touching) * B.ENEMY.contact_dps * delta
	state.take_damage(taken)
	shake = minf(shake + taken * 0.05, 0.5)
	if taken > 0.9:
		hitstop = maxf(hitstop, 0.05)
	hurt.emit(taken)
	if not state.alive:
		shake = 0.7

## Shake moves the camera, never the world, so nothing detaches from the ground.
func _decay_feedback(delta: float) -> void:
	muzzle_flash = maxf(0.0, muzzle_flash - delta * 9.0)
	shake = maxf(0.0, shake - delta * 1.4)

	if muzzle:
		muzzle.light_energy = muzzle_flash * 7.5
	if camera:
		if shake > 0.0:
			camera.position = _camera_home + Vector3(
				randf_range(-1.0, 1.0) * shake * 2.2,
				randf_range(-1.0, 1.0) * shake * 1.6, 0.0)
		else:
			camera.position = _camera_home

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
	debris.burst(pos)
	shake = minf(shake + 0.035, 0.28)

func _on_leveled_up(options: Array) -> void:
	paused_for_level_up = true
	levelled.emit()
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
