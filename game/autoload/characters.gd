extends RefCounted
class_name Characters

## The playable roster.
##
## Four characters, each built around one honest trade. A roster where everyone
## is "balanced but flavoured" gives players nothing to unlock toward, so every
## entry here is genuinely better at something and genuinely worse at something
## else. Unlock costs are the spending sink that makes gold worth banking.
##
## Readability first: at this camera height a player sees a silhouette and a
## colour, not a face. Each one is a different shape and a different hue.

const ROSTER := [
	{
		"id": "sentinel",
		"name": "Nöbetçi",
		"tagline": "Dengeli. Her şeyde iyi, hiçbir şeyde en iyi değil.",
		"unlock_cost": 0,
		"color": Color(0.25, 0.76, 0.88),
		"silhouette": "tall",
		"hp": 100.0,
		"move_speed": 5.0,
		"weapon": {
			"damage": 15.0, "cooldown": 0.34, "projectiles": 1,
			"range": 9.5, "spread": 1.0, "pierce": 0,
		},
	},
	{
		"id": "hunter",
		"name": "Avcı",
		"tagline": "Uzun menzil, hızlı ve hafif atış. Kalabalık sertleşince zorlanır.",
		"unlock_cost": 800,
		"color": Color(0.95, 0.72, 0.28),
		"silhouette": "lean",
		"hp": 80.0,
		"move_speed": 5.3,
		"weapon": {
			"damage": 9.5, "cooldown": 0.20, "projectiles": 1,
			"range": 13.0, "spread": 1.0, "pierce": 0,
		},
	},
	{
		"id": "warden",
		"name": "Koruyucu",
		"tagline": "Ağır ve dayanıklı. Kalabalığın içinde durur, sırayı deler.",
		"unlock_cost": 1600,
		"color": Color(0.88, 0.42, 0.24),
		"silhouette": "wide",
		"hp": 148.0,
		"move_speed": 4.2,
		"weapon": {
			"damage": 27.0, "cooldown": 0.78, "projectiles": 1,
			"range": 7.0, "spread": 1.0, "pierce": 2,
		},
	},
	{
		"id": "exile",
		"name": "Sürgün",
		"tagline": "Çok hızlı, çok kırılgan. Geniş saçma, sürekli kaçarak oynanır.",
		"unlock_cost": 2600,
		"color": Color(0.68, 0.45, 0.92),
		"silhouette": "slight",
		"hp": 76.0,
		"move_speed": 6.1,
		"weapon": {
			"damage": 12.0, "cooldown": 0.45, "projectiles": 3,
			"range": 8.5, "spread": 1.45, "pierce": 2,
		},
	},
]

static func by_id(id: String) -> Dictionary:
	for c in ROSTER:
		if c.id == id:
			return c
	return ROSTER[0]

static func default_id() -> String:
	return ROSTER[0].id

## Nominal damage per second before any upgrades. Not the whole story for
## Koruyucu, whose piercing shots multiply this inside a dense crowd.
static func base_dps(character: Dictionary) -> float:
	var w: Dictionary = character.weapon
	return w.damage / w.cooldown * float(w.projectiles)
