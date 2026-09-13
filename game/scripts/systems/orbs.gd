extends Node3D
class_name Orbs

## XP pickups. Same pooled, instanced approach as the swarm.
##
## The magnet behaviour matters more than it looks: orbs that fly to the player
## once they are close turn every kill into a small reward animation, which is
## most of why the moment-to-moment loop feels good.

const MAX_ORBS := 400
const MAGNET_SPEED := 14.0
const COLLECT_RADIUS := 0.7

var positions: PackedVector3Array = PackedVector3Array()
var count := 0

var _multimesh: MultiMesh

var _initialised := false

func _ready() -> void:
	ensure_ready()

func ensure_ready() -> void:
	if _initialised:
		return
	_initialised = true
	positions.resize(MAX_ORBS)
	_setup_multimesh()

func _setup_multimesh() -> void:
	var mesh := SphereMesh.new()
	mesh.radius = 0.16
	mesh.height = 0.32
	var mat := StandardMaterial3D.new()
	mat.albedo_color = Color(0.3, 0.85, 1.0)
	mat.emission_enabled = true
	mat.emission = Color(0.2, 0.7, 1.0)
	mesh.material = mat

	_multimesh = MultiMesh.new()
	_multimesh.transform_format = MultiMesh.TRANSFORM_3D
	_multimesh.mesh = mesh
	_multimesh.instance_count = MAX_ORBS
	_multimesh.visible_instance_count = 0

	var mmi := MultiMeshInstance3D.new()
	mmi.name = "OrbRender"
	mmi.multimesh = _multimesh
	add_child(mmi)

func spawn(pos: Vector3) -> void:
	ensure_ready()
	if count >= MAX_ORBS:
		return
	positions[count] = pos
	count += 1

## Moves orbs and returns how many were collected this frame.
func update(delta: float, player_pos: Vector3, pickup_radius: float) -> int:
	ensure_ready()
	var collected := 0
	var magnet_sq := pickup_radius * pickup_radius
	var collect_sq := COLLECT_RADIUS * COLLECT_RADIUS
	var i := 0
	while i < count:
		var to_player := player_pos - positions[i]
		to_player.y = 0.0
		var d_sq := to_player.length_squared()
		if d_sq <= collect_sq:
			collected += 1
			_remove(i)
			continue
		if d_sq <= magnet_sq:
			positions[i] += to_player.normalized() * MAGNET_SPEED * delta
		i += 1
	_render()
	return collected

func _remove(index: int) -> void:
	count -= 1
	positions[index] = positions[count]

func _render() -> void:
	if _multimesh == null:
		return
	_multimesh.visible_instance_count = count
	for i in count:
		_multimesh.set_instance_transform(i, Transform3D(Basis(), positions[i]))

func clear() -> void:
	count = 0
