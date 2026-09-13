extends Node3D
class_name Weapon

## Auto-firing weapon and its projectile pool.
##
## The player never aims: the weapon picks the nearest enemy on cooldown and
## fires. That is the whole reason the genre works one-handed on a phone, and
## it is why the balance model can predict DPS without modelling aim skill.

const B := preload("res://autoload/balance.gd")

const MAX_PROJECTILES := 256
const SPEED := 18.0
const HIT_RADIUS := 0.6
const SPREAD := 0.22              ## Radians between extra projectiles.

var positions: PackedVector3Array = PackedVector3Array()
var velocities: PackedVector3Array = PackedVector3Array()
var lifetimes: PackedFloat32Array = PackedFloat32Array()
var pierces: PackedInt32Array = PackedInt32Array()
var count := 0

var _cooldown := 0.0
var _multimesh: MultiMesh

var _initialised := false

func _ready() -> void:
	ensure_ready()

func ensure_ready() -> void:
	if _initialised:
		return
	_initialised = true
	positions.resize(MAX_PROJECTILES)
	velocities.resize(MAX_PROJECTILES)
	lifetimes.resize(MAX_PROJECTILES)
	pierces.resize(MAX_PROJECTILES)
	_setup_multimesh()

func _setup_multimesh() -> void:
	var mesh := SphereMesh.new()
	mesh.radius = 0.18
	mesh.height = 0.36
	var mat := StandardMaterial3D.new()
	mat.albedo_color = Color(1.0, 0.9, 0.35)
	mat.emission_enabled = true
	mat.emission = Color(1.0, 0.8, 0.2)
	mesh.material = mat

	_multimesh = MultiMesh.new()
	_multimesh.transform_format = MultiMesh.TRANSFORM_3D
	_multimesh.mesh = mesh
	_multimesh.instance_count = MAX_PROJECTILES
	_multimesh.visible_instance_count = 0

	var mmi := MultiMeshInstance3D.new()
	mmi.name = "ProjectileRender"
	mmi.multimesh = _multimesh
	add_child(mmi)

func update(delta: float, state: RunState, swarm: Swarm, origin: Vector3,
		enemy_speed: float = 0.0) -> void:
	ensure_ready()
	_cooldown -= delta
	if _cooldown <= 0.0:
		var target := swarm.nearest(origin, state.weapon_range())
		if target >= 0:
			var aim := _lead(origin, swarm, target, enemy_speed)
			_fire(origin, aim, state)
			_cooldown = state.weapon_cooldown()
	_advance(delta, state, swarm)
	_render()

## First-order intercept: aim where the target will be when the shot arrives.
func _lead(origin: Vector3, swarm: Swarm, index: int, enemy_speed: float) -> Vector3:
	var target: Vector3 = swarm.positions[index]
	if enemy_speed <= 0.0:
		return target
	var flight := origin.distance_to(target) / SPEED
	return target + swarm.velocity_of(index, origin, enemy_speed) * flight

func _fire(origin: Vector3, target: Vector3, state: RunState) -> void:
	var shots := state.projectile_count()
	var arc := SPREAD * state.weapon_spread()
	var dir := (target - origin)
	dir.y = 0.0
	if dir.length() < 0.001:
		return
	dir = dir.normalized()
	var base_angle := atan2(dir.z, dir.x)
	# Fan the extra projectiles symmetrically around the aim line.
	for s in shots:
		if count >= MAX_PROJECTILES:
			return
		var offset := (float(s) - float(shots - 1) * 0.5) * arc
		var a := base_angle + offset
		positions[count] = origin
		velocities[count] = Vector3(cos(a), 0.0, sin(a)) * SPEED
		lifetimes[count] = state.weapon_range() / SPEED
		pierces[count] = state.weapon_pierce()
		count += 1

func _advance(delta: float, state: RunState, swarm: Swarm) -> void:
	var damage := state.weapon_damage()
	var i := 0
	while i < count:
		positions[i] += velocities[i] * delta
		lifetimes[i] -= delta

		var hit := _hit_index(positions[i], swarm)
		if hit >= 0:
			if swarm.damage(hit, damage):
				state.add_kill()
			# A piercing shot keeps going; a spent one stops here.
			if pierces[i] > 0:
				pierces[i] -= 1
			else:
				_remove(i)
				continue
		if lifetimes[i] <= 0.0:
			_remove(i)
			continue
		i += 1

func _hit_index(pos: Vector3, swarm: Swarm) -> int:
	var reach_sq := HIT_RADIUS * HIT_RADIUS
	for e in swarm.count:
		if swarm.positions[e].distance_squared_to(pos) <= reach_sq:
			return e
	return -1

func _remove(index: int) -> void:
	count -= 1
	positions[index] = positions[count]
	velocities[index] = velocities[count]
	lifetimes[index] = lifetimes[count]
	pierces[index] = pierces[count]

func _render() -> void:
	if _multimesh == null:
		return
	_multimesh.visible_instance_count = count
	for i in count:
		_multimesh.set_instance_transform(i, Transform3D(Basis(), positions[i]))

func clear() -> void:
	count = 0
	_cooldown = 0.0
