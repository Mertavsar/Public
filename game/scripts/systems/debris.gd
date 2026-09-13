extends Node3D
class_name Debris

## Chunks thrown off by a dying enemy.
##
## A body that simply vanishes reads as a bug. A body that comes apart reads as
## a kill. Same pooled, instanced approach as everything else on the field, so
## a few hundred shards cost one draw call.

const MAX_PIECES := 320
const PER_KILL := 4
const GRAVITY := 16.0
const BOUNCE := -0.32
const LIFETIME := Vector2(0.45, 0.70)

var positions: PackedVector3Array = PackedVector3Array()
var velocities: PackedVector3Array = PackedVector3Array()
var lives: PackedFloat32Array = PackedFloat32Array()
var count := 0

var _rng := RandomNumberGenerator.new()
var _multimesh: MultiMesh
var _initialised := false

func _ready() -> void:
	ensure_ready()

func ensure_ready() -> void:
	if _initialised:
		return
	_initialised = true
	_rng.randomize()
	positions.resize(MAX_PIECES)
	velocities.resize(MAX_PIECES)
	lives.resize(MAX_PIECES)

	var mesh := BoxMesh.new()
	mesh.size = Vector3(0.22, 0.22, 0.22)
	var mat := StandardMaterial3D.new()
	mat.albedo_color = Color(0.88, 0.27, 0.35)
	mesh.material = mat

	_multimesh = MultiMesh.new()
	_multimesh.transform_format = MultiMesh.TRANSFORM_3D
	_multimesh.mesh = mesh
	_multimesh.instance_count = MAX_PIECES
	_multimesh.visible_instance_count = 0

	var mmi := MultiMeshInstance3D.new()
	mmi.name = "DebrisRender"
	mmi.multimesh = _multimesh
	add_child(mmi)

func burst(at: Vector3) -> void:
	ensure_ready()
	for i in PER_KILL:
		if count >= MAX_PIECES:
			return
		var angle := _rng.randf() * TAU
		var out := _rng.randf_range(1.8, 4.8)
		positions[count] = at + Vector3(0.0, 0.45, 0.0)
		velocities[count] = Vector3(cos(angle) * out,
			_rng.randf_range(2.6, 5.8), sin(angle) * out)
		lives[count] = _rng.randf_range(LIFETIME.x, LIFETIME.y)
		count += 1

func update(delta: float) -> void:
	ensure_ready()
	var i := 0
	while i < count:
		var v := velocities[i]
		v.y -= GRAVITY * delta
		var pos := positions[i] + v * delta
		if pos.y < 0.11:
			pos.y = 0.11
			v.y *= BOUNCE
			v.x *= 0.6
			v.z *= 0.6
		positions[i] = pos
		velocities[i] = v
		lives[i] -= delta
		if lives[i] <= 0.0:
			_remove(i)
			continue
		i += 1
	_render()

func _remove(index: int) -> void:
	count -= 1
	positions[index] = positions[count]
	velocities[index] = velocities[count]
	lives[index] = lives[count]

func _render() -> void:
	if _multimesh == null:
		return
	_multimesh.visible_instance_count = count
	for i in count:
		var scale := 0.35 + lives[i] * 1.3
		_multimesh.set_instance_transform(i,
			Transform3D(Basis().scaled(Vector3.ONE * scale), positions[i]))

func clear() -> void:
	count = 0
