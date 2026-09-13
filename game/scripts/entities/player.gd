extends Node3D
class_name Player

## The player avatar. No physics body on purpose: the arena is open ground with
## nothing to collide against, and enemy contact is resolved by the swarm as a
## distance test. That keeps movement perfectly deterministic, which is what
## lets the headless test reproduce a run exactly.

const RADIUS := 0.45

## Proportions per silhouette. At this camera height the player reads as a
## shape and a colour, so each character has to be tellable apart from directly
## above: the roster is tall, lean, wide and slight on purpose.
const SILHOUETTES := {
	"tall":   {"radius": 0.42, "height": 1.70},
	"lean":   {"radius": 0.34, "height": 1.62},
	"wide":   {"radius": 0.58, "height": 1.35},
	"slight": {"radius": 0.30, "height": 1.45},
}

var facing := Vector3.FORWARD

var _body: MeshInstance3D

func _ready() -> void:
	if _body == null:
		apply_character({})

func apply_character(character: Dictionary) -> void:
	var shape: Dictionary = SILHOUETTES.get(
		character.get("silhouette", "tall"), SILHOUETTES.tall)
	var colour: Color = character.get("color", Color(0.25, 0.76, 0.88))

	if _body == null:
		_body = MeshInstance3D.new()
		add_child(_body)

	var capsule := CapsuleMesh.new()
	capsule.radius = shape.radius
	capsule.height = shape.height
	var mat := StandardMaterial3D.new()
	mat.albedo_color = colour
	mat.emission_enabled = true
	mat.emission = colour * 0.35
	capsule.material = mat

	_body.mesh = capsule
	_body.position.y = shape.height * 0.5

func move(delta: float, direction: Vector3, speed: float) -> void:
	if direction.length_squared() < 0.0001:
		return
	direction = direction.normalized()
	facing = direction
	position += direction * speed * delta
