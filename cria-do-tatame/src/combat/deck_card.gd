extends Resource
class_name DeckCard

@export_group("Identificação")
@export var id: String = ""
@export var name: String = ""
@export var kind: String = "active"  # "active" ou "passive"
@export var category: String = ""     # Alinhado com TechniqueCategory

@export_group("Dados Técnicos")
@export var technique_id: String = ""  # Referencia techniques.json
@export var level: int = 1
@export var base_power: int = 10

@export_group("Custo de Ativação")
@export var activation_cost: Dictionary = {}  # {gas: X, focus: Y}

@export_group("Efeitos")
@export var passive_effect: Dictionary = {}   # Modificadores passivos
@export var clash_effect: Dictionary = {}     # Bônus em clashes
@export var response_to_families: Array = []  # Famílias que esta carta responde (defesa)

@export_group("Restrições")
@export var valid_states: Array[String] = []  # Estados onde pode ser usada

@export_group("Progressão")
@export var xp: int = 0
@export var xp_to_next: int = 100
@export var unlocked: bool = true

# Métodos utilitários

func get_gas_cost() -> float:
	return float(activation_cost.get("gas", 0))

func get_focus_cost() -> float:
	return float(activation_cost.get("focus", 0))

func is_valid_for_state(state_name: String) -> bool:
	if valid_states.is_empty():
		return true
	return valid_states.has(state_name)

func responds_to_family(family: String) -> bool:
	return response_to_families.has(family)

func get_clash_bonus(stat: String) -> float:
	return float(clash_effect.get(stat, 0.0))

func get_passive_bonus(stat: String) -> float:
	return float(passive_effect.get(stat, 0.0))

func can_activate(resources: Dictionary) -> bool:
	var gas_ok: bool = float(resources.get("gas", 0)) >= get_gas_cost()
	var focus_ok: bool = float(resources.get("focus", 0)) >= get_focus_cost()
	return gas_ok and focus_ok

func to_dict() -> Dictionary:
	return {
		"id": id,
		"name": name,
		"kind": kind,
		"category": category,
		"technique_id": technique_id,
		"level": level,
		"base_power": base_power,
		"activation_cost": activation_cost.duplicate(),
		"passive_effect": passive_effect.duplicate(),
		"clash_effect": clash_effect.duplicate(),
		"response_to_families": response_to_families.duplicate(),
		"valid_states": valid_states.duplicate(),
		"xp": xp,
		"xp_to_next": xp_to_next,
		"unlocked": unlocked
	}

static func from_dict(data: Dictionary) -> DeckCard:
	var card := DeckCard.new()
	card.id = str(data.get("id", ""))
	card.name = str(data.get("name", ""))
	card.kind = str(data.get("kind", "active"))
	card.category = str(data.get("category", ""))
	card.technique_id = str(data.get("technique_id", ""))
	card.level = int(data.get("level", 1))
	card.base_power = int(data.get("base_power", 10))
	card.activation_cost = data.get("activation_cost", {}).duplicate()
	card.passive_effect = data.get("passive_effect", {}).duplicate()
	card.clash_effect = data.get("clash_effect", {}).duplicate()
	card.response_to_families = data.get("response_to_families", []).duplicate()
	card.valid_states = data.get("valid_states", []).duplicate()
	card.xp = int(data.get("xp", 0))
	card.xp_to_next = int(data.get("xp_to_next", 100))
	card.unlocked = bool(data.get("unlocked", true))
	return card
