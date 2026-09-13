extends Node3D
class_name Player

## The player avatar. No physics body on purpose: the arena is open ground with
## nothing to collide against, and enemy contact is resolved by the swarm as a
## distance test. That keeps movement perfectly deterministic, which is what
## lets the headless test reproduce a run exactly.

const RADIUS := 0.45

var facing := Vector3.FORWARD

func _ready() -> void:
	if get_child_count() == 0:
		_build_visual()

func _build_visual() -> void:
	var mesh := MeshInstance3D.new()
	var capsule := CapsuleMesh.new()
	capsule.radius = RADIUS
	capsule.height = 1.5
	var mat := StandardMaterial3D.new()
	mat.albedo_color = Color(0.25, 0.75, 0.95)
	capsule.material = mat
	mesh.mesh = capsule
	mesh.position.y = 0.75
	add_child(mesh)

func move(delta: float, direction: Vector3, speed: float) -> void:
	if direction.length_squared() < 0.0001:
		return
	direction = direction.normalized()
	facing = direction
	position += direction * speed * delta
