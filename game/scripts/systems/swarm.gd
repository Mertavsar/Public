extends Node3D
class_name Swarm

## Every enemy in the run, held as parallel arrays and drawn with one
## MultiMeshInstance3D.
##
## A survivor game puts hundreds of bodies on screen at once. One node per
## enemy means hundreds of physics bodies and hundreds of draw calls, which is
## exactly how these games die on mid-range Android. Flat arrays plus a single
## instanced draw keeps the whole swarm to one call, and it stays testable
## headless because nothing depends on the physics server.

const B := preload("res://autoload/balance.gd")

const MAX_ENEMIES := 600
const ENEMY_RADIUS := 0.45
const SEPARATION := 0.85          ## Enemies push apart so they don't stack.

var positions: PackedVector3Array = PackedVector3Array()
var healths: PackedFloat32Array = PackedFloat32Array()
var flashes: PackedFloat32Array = PackedFloat32Array()
var count := 0

const FLASH_TIME := 0.09
const BASE_COLOR := Color(0.88, 0.27, 0.35)
const HIT_COLOR := Color(1.0, 0.92, 0.93)

## Tuner hook. 0 means use the curve in Balance.
var hp_growth_override := 0.0

var _spawn_accumulator := 0.0
var _rng := RandomNumberGenerator.new()
var _multimesh: MultiMesh

## Emitted when an enemy dies, so the run can drop XP and bank gold.
signal enemy_killed(pos: Vector3)

var _initialised := false

func _ready() -> void:
	ensure_ready()

## Idempotent setup. Called from _ready in the live game and lazily from
## update(), so the headless play test can drive this node without the engine
## ever putting it in the scene tree.
func ensure_ready() -> void:
	if _initialised:
		return
	_initialised = true
	_rng.randomize()
	positions.resize(MAX_ENEMIES)
	healths.resize(MAX_ENEMIES)
	flashes.resize(MAX_ENEMIES)
	_setup_multimesh()

func _setup_multimesh() -> void:
	var mesh := BoxMesh.new()
	mesh.size = Vector3(0.7, 0.9, 0.7)
	var mat := StandardMaterial3D.new()
	mat.albedo_color = Color.WHITE
	# Per-instance colour is what makes a hit visible inside a crowd. Without
	# this the frame a shot lands looks identical to the frame it misses.
	mat.vertex_color_use_as_albedo = true
	mesh.material = mat

	_multimesh = MultiMesh.new()
	_multimesh.transform_format = MultiMesh.TRANSFORM_3D
	_multimesh.use_colors = true
	_multimesh.mesh = mesh
	_multimesh.instance_count = MAX_ENEMIES
	_multimesh.visible_instance_count = 0

	var mmi := MultiMeshInstance3D.new()
	mmi.name = "SwarmRender"
	mmi.multimesh = _multimesh
	add_child(mmi)

## Advance the whole swarm one frame. `elapsed` drives difficulty scaling.
func update(delta: float, elapsed: float, player_pos: Vector3, speed: float,
		facing: Vector3 = Vector3.ZERO) -> void:
	ensure_ready()
	_spawn(delta, elapsed, player_pos, facing)
	_move(delta, player_pos, speed)
	for i in count:
		if flashes[i] > 0.0:
			flashes[i] = maxf(0.0, flashes[i] - delta)
	_render()

func _spawn(delta: float, elapsed: float, player_pos: Vector3, facing: Vector3) -> void:
	_spawn_accumulator += B.spawn_rate_at(elapsed) * delta
	var hp := _enemy_hp_at(elapsed)
	while _spawn_accumulator >= 1.0 and count < MAX_ENEMIES:
		_spawn_accumulator -= 1.0
		# Spawn on a ring outside the camera so they walk into view. Most of them
		# land ahead of the player: running away should cost you, not save you.
		var angle := _rng.randf() * TAU
		if facing.length_squared() > 0.001 and _rng.randf() < B.SPAWN.forward_bias:
			var heading := atan2(facing.z, facing.x)
			angle = heading + _rng.randf_range(-PI / 3.0, PI / 3.0)
		var dist := _rng.randf_range(16.0, 20.0)
		positions[count] = player_pos + Vector3(cos(angle), 0.0, sin(angle)) * dist
		healths[count] = hp
		flashes[count] = 0.0
		count += 1

func _enemy_hp_at(elapsed: float) -> float:
	if hp_growth_override > 0.0:
		return B.ENEMY.base_hp * pow(hp_growth_override, elapsed / 10.0)
	return B.enemy_hp_at(elapsed)

func _move(delta: float, player_pos: Vector3, speed: float) -> void:
	for i in count:
		var pos := positions[i]
		var to_player := player_pos - pos
		to_player.y = 0.0
		var dist := to_player.length()
		if dist > 0.001:
			pos += to_player / dist * speed * delta
		positions[i] = pos

	_separate()

## Cheap neighbour push so the swarm spreads instead of collapsing into a line.
## Only samples a stride of the array each frame; over a few frames every enemy
## gets checked, which is plenty for a visual effect.
func _separate() -> void:
	var stride := 4
	for i in range(0, count, stride):
		for j in range(i + 1, mini(i + 12, count)):
			var diff := positions[i] - positions[j]
			diff.y = 0.0
			var d := diff.length()
			if d < SEPARATION and d > 0.001:
				var push := diff / d * (SEPARATION - d) * 0.5
				positions[i] += push
				positions[j] -= push

## Apply damage to the enemy at `index`. Returns true if it died.
func damage(index: int, amount: float) -> bool:
	if index < 0 or index >= count:
		return false
	healths[index] -= amount
	flashes[index] = FLASH_TIME
	if healths[index] <= 0.0:
		enemy_killed.emit(positions[index])
		_remove(index)
		return true
	return false

func _remove(index: int) -> void:
	count -= 1
	positions[index] = positions[count]
	healths[index] = healths[count]
	flashes[index] = flashes[count]

## Where enemy `index` will be heading this frame. The weapon needs this to
## lead its shots; firing at where a target currently stands misses almost
## everything at range.
func velocity_of(index: int, player_pos: Vector3, speed: float) -> Vector3:
	if index < 0 or index >= count:
		return Vector3.ZERO
	var to_player := player_pos - positions[index]
	to_player.y = 0.0
	if to_player.length() < 0.001:
		return Vector3.ZERO
	return to_player.normalized() * speed

## Nearest enemy to `from` within `max_range`, or -1. Used for weapon targeting.
func nearest(from: Vector3, max_range: float) -> int:
	var best := -1
	var best_sq := max_range * max_range
	for i in count:
		var d := positions[i].distance_squared_to(from)
		if d < best_sq:
			best_sq = d
			best = i
	return best

## How many enemies are touching the player right now.
func touching(player_pos: Vector3, player_radius: float) -> int:
	var reach := player_radius + ENEMY_RADIUS
	var reach_sq := reach * reach
	var n := 0
	for i in count:
		if positions[i].distance_squared_to(player_pos) <= reach_sq:
			n += 1
	return n

func _render() -> void:
	if _multimesh == null:
		return
	_multimesh.visible_instance_count = count
	for i in count:
		# A struck body swells for the frame it flashes: colour alone is easy
		# to lose in a field of two hundred.
		var f := flashes[i] / FLASH_TIME
		var basis := Basis().scaled(Vector3(1.0 + f * 0.25, 1.0 + f * 0.35, 1.0 + f * 0.25))
		_multimesh.set_instance_transform(i, Transform3D(basis, positions[i]))
		_multimesh.set_instance_color(i, BASE_COLOR.lerp(HIT_COLOR, f))

func set_seed(value: int) -> void:
	ensure_ready()
	_rng.seed = value

func clear() -> void:
	count = 0
	_spawn_accumulator = 0.0
