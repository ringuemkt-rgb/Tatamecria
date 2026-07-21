extends Resource
class_name LegacyPerk

@export var id: String = "legacy_perk_tekuro"
@export var name: String = "Legado de Tekuro"
@export var description: String = "+10% resistência à fadiga de Grip. Honre os que vieram antes."

# Tipo de perk
@export var perk_type: String = "passive"  # passive, triggered, conditional

# Modificadores aplicados
@export var modifiers: Dictionary = {
	"grip_fatigue_reduction": 0.10,  # -10% fadiga ao usar grip
	"grip_regen_bonus": 0.05         # +5% regeneração de grip
}

# Requisitos para equipar
@export var requirements: Dictionary = {
	"belt_minimum": "azul",
	"relationship_threshold": 75,  # Relacionamento com Tekuro
	"story_progress": "met_terreiro"
}

# Efeitos visuais/sonoros opcionais
@export var vfx_prefab: String = ""
@export var sfx_prefab: String = ""

# Flavor text (lore)
@export var flavor_text: String = "Tekuro dizia: 'Pegada não é força, é memória dos dedos.'"

func get_modifier(key: String) -> float:
	return modifiers.get(key, 0.0)

func meets_requirements(player_data: Dictionary) -> bool:
	var belt = str(player_data.get("belt", "branca"))
	var belt_order = ["branca", "azul", "roxa", "marrom", "preta"]
	
	var min_belt_idx = belt_order.find(str(requirements.get("belt_minimum", "branca")))
	var player_belt_idx = belt_order.find(belt)
	
	if player_belt_idx < min_belt_idx:
		return false
	
	if requirements.has("relationship_threshold"):
		var relationship = int(player_data.get("tekuro_relationship", 0))
		if relationship < requirements["relationship_threshold"]:
			return false
	
	return true

func apply_to(target: Node) -> void:
	# Aplica modificadores a um FighterCondition ou GripState
	if target.has_method("apply_perk"):
		target.apply_perk(id, modifiers)

func remove_from(target: Node) -> void:
	if target.has_method("remove_perk"):
		target.remove_perk(id, modifiers)

func to_dict() -> Dictionary:
	return {
		"id": id,
		"name": name,
		"description": description,
		"perk_type": perk_type,
		"modifiers": modifiers.duplicate(),
		"requirements": requirements.duplicate(),
		"flavor_text": flavor_text
	}

static func from_dict(data: Dictionary) -> LegacyPerk:
	var perk := LegacyPerk.new()
	perk.id = str(data.get("id", ""))
	perk.name = str(data.get("name", ""))
	perk.description = str(data.get("description", ""))
	perk.perk_type = str(data.get("perk_type", "passive"))
	perk.modifiers = data.get("modifiers", {}).duplicate()
	perk.requirements = data.get("requirements", {}).duplicate()
	perk.flavor_text = str(data.get("flavor_text", ""))
	return perk
