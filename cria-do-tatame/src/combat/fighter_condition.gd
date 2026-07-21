extends Node
class_name FighterCondition

# Sistema de Gás, Fadiga Localizada e Dano por Membro
# Integrado com o CombatManager existente

signal gas_changed(new_gas: float)
signal fatigue_changed(limb: BJJEnums.LimbType, new_fatigue: float)
signal grip_integrity_changed(new_value: float)
signal member_damaged(member: BJJEnums.LimbType, damage: float)

# Recursos principais
var max_gas: float = 100.0
var current_gas: float = 100.0
var gas_regen_rate: float = 5.0  # Por segundo

# Fadiga por membro (0-100, quanto maior mais cansado)
var limb_fatigue: Dictionary = {
	BJJEnums.LimbType.LEFT_ARM: 0.0,
	BJJEnums.LimbType.RIGHT_ARM: 0.0,
	BJJEnums.LimbType.LEFT_LEG: 0.0,
	BJJEnums.LimbType.RIGHT_LEG: 0.0,
	BJJEnums.LimbType.CORE: 0.0
}

var limb_max_fatigue: float = 100.0
var fatigue_regen_rate: float = 3.0  # Por segundo

# Grip/Postura
var grip_integrity: float = 100.0
var max_grip_integrity: float = 100.0
var grip_regen_rate: float = 8.0

# Dano estrutural por membro (afeta eficiência de técnicas)
var limb_damage: Dictionary = {
	BJJEnums.LimbType.LEFT_ARM: 0.0,
	BJJEnums.LimbType.RIGHT_ARM: 0.0,
	BJJEnums.LimbType.LEFT_LEG: 0.0,
	BJJEnums.LimbType.RIGHT_LEG: 0.0,
	BJJEnums.LimbType.CORE: 0.0
}

# Modificadores de perks (ex: Legado de Tekuro)
var perk_modifiers: Dictionary = {
	"grip_fatigue_reduction": 0.0,  # Ex: 0.10 = -10% fadiga de grip
	"gas_regen_bonus": 0.0,
	"fatigue_regen_bonus": 0.0
}

var fighter_id: String = ""

func _ready() -> void:
	pass

func initialize(id: String, base_stats: Dictionary) -> void:
	fighter_id = id
	max_gas = float(base_stats.get("gas", 100))
	current_gas = max_gas
	gas_regen_rate = float(base_stats.get("gas_regen", 5.0))
	grip_integrity = float(base_stats.get("grip", 100))
	max_grip_integrity = grip_integrity
	
	# Stats específicos podem vir do base_stats
	if base_stats.has("limb_fatigue"):
		for limb_str in base_stats["limb_fatigue"].keys():
			var limb_enum = _string_to_limb(limb_str)
			if limb_enum != -1:
				limb_fatigue[limb_enum] = float(base_stats["limb_fatigue"][limb_str])

# ==================== GAS SYSTEM ====================

func consume_gas(amount: float, source_limb: BJJEnums.LimbType = BJJEnums.LimbType.CORE) -> bool:
	if current_gas < amount:
		return false
	current_gas = max(0.0, current_gas - amount)
	
	# Gasto de gás também gera fadiga no membro usado
	var fatigue_multiplier = 1.0 - perk_modifiers.get("grip_fatigue_reduction", 0.0)
	add_fatigue(source_limb, amount * 0.5 * fatigue_multiplier)
	
	gas_changed.emit(current_gas)
	return true

func add_gas(amount: float) -> void:
	current_gas = min(max_gas, current_gas + amount)
	gas_changed.emit(current_gas)

func regen_gas(delta: float) -> void:
	if current_gas < max_gas:
		var regen = gas_regen_rate * (1.0 + perk_modifiers.get("gas_regen_bonus", 0.0)) * delta
		add_gas(regen)

func get_gas_percent() -> float:
	return current_gas / max_gas if max_gas > 0 else 0.0

# ==================== FADIGA LOCALIZADA ====================

func add_fatigue(limb: BJJEnums.LimbType, amount: float) -> void:
	var current = limb_fatigue.get(limb, 0.0)
	limb_fatigue[limb] = min(limb_max_fatigue, current + amount)
	fatigue_changed.emit(limb, limb_fatigue[limb])

func reduce_fatigue(limb: BJJEnums.LimbType, amount: float) -> void:
	var current = limb_fatigue.get(limb, 0.0)
	limb_fatigue[limb] = max(0.0, current - amount)
	fatigue_changed.emit(limb, limb_fatigue[limb])

func regen_fatigue(delta: float) -> void:
	var regen = fatigue_regen_rate * (1.0 + perk_modifiers.get("fatigue_regen_bonus", 0.0)) * delta
	for limb in limb_fatigue.keys():
		reduce_fatigue(limb, regen / limb_fatigue.size())

func get_limb_efficiency(limb: BJJEnums.LimbType) -> float:
	# Retorna multiplicador de eficiência (1.0 = 100%, 0.5 = 50%)
	var fatigue = limb_fatigue.get(limb, 0.0)
	var damage = limb_damage.get(limb, 0.0)
	var total_impairment = (fatigue / limb_max_fatigue) + (damage / 100.0)
	return max(0.3, 1.0 - total_impairment)  # Mínimo de 30% eficiência

func get_average_limb_efficiency() -> float:
	var total: float = 0.0
	for limb in limb_fatigue.keys():
		total += get_limb_efficiency(limb)
	return total / limb_fatigue.size()

# ==================== GRIP INTEGRITY ====================

func consume_grip(amount: float) -> bool:
	if grip_integrity < amount:
		return false
	var reduction = 1.0 - perk_modifiers.get("grip_fatigue_reduction", 0.0)
	grip_integrity = max(0.0, grip_integrity - (amount * reduction))
	grip_integrity_changed.emit(grip_integrity)
	return true

func add_grip(amount: float) -> void:
	grip_integrity = min(max_grip_integrity, grip_integrity + amount)
	grip_integrity_changed.emit(grip_integrity)

func regen_grip(delta: float) -> void:
	if grip_integrity < max_grip_integrity:
		grip_integrity = min(max_grip_integrity, grip_integrity + grip_regen_rate * delta)
		grip_integrity_changed.emit(grip_integrity)

func get_grip_percent() -> float:
	return grip_integrity / max_grip_integrity if max_grip_integrity > 0 else 0.0

# ==================== DANO POR MEMBRO ====================

func apply_member_damage(limb: BJJEnums.LimbType, damage: float) -> void:
	limb_damage[limb] = min(100.0, limb_damage[limb] + damage)
	member_damaged.emit(limb, damage)
	
	# Dano no CORE afeta gás máximo temporariamente
	if limb == BJJEnums.LimbType.CORE:
		var gas_penalty = damage * 0.3
		current_gas = max(0.0, current_gas - gas_penalty)
		gas_changed.emit(current_gas)

func heal_member(limb: BJJEnums.LimbType, amount: float) -> void:
	limb_damage[limb] = max(0.0, limb_damage[limb] - amount)

func is_limb_critical(limb: BJJEnums.LimbType) -> bool:
	var efficiency = get_limb_efficiency(limb)
	return efficiency <= 0.4

# ==================== PERKS ====================

func apply_perk(perk_id: String, modifiers: Dictionary) -> void:
	for key in modifiers.keys():
		if perk_modifiers.has(key):
			perk_modifiers[key] += float(modifiers[key])

func remove_perk(perk_id: String, modifiers: Dictionary) -> void:
	for key in modifiers.keys():
		if perk_modifiers.has(key):
			perk_modifiers[key] -= float(modifiers[key])

# ==================== UTILITÁRIOS ====================

func _string_to_limb(s: String) -> int:
	match s.to_lower():
		"left_arm": return BJJEnums.LimbType.LEFT_ARM
		"right_arm": return BJJEnums.LimbType.RIGHT_ARM
		"left_leg": return BJJEnums.LimbType.LEFT_LEG
		"right_leg": return BJJEnums.LimbType.RIGHT_LEG
		"core": return BJJEnums.LimbType.CORE
	return -1

func get_state_dict() -> Dictionary:
	return {
		"gas": current_gas,
		"max_gas": max_gas,
		"grip_integrity": grip_integrity,
		"limb_fatigue": {
			"left_arm": limb_fatigue[BJJEnums.LimbType.LEFT_ARM],
			"right_arm": limb_fatigue[BJJEnums.LimbType.RIGHT_ARM],
			"left_leg": limb_fatigue[BJJEnums.LimbType.LEFT_LEG],
			"right_leg": limb_fatigue[BJJEnums.LimbType.RIGHT_LEG],
			"core": limb_fatigue[BJJEnums.LimbType.CORE]
		},
		"limb_damage": {
			"left_arm": limb_damage[BJJEnums.LimbType.LEFT_ARM],
			"right_arm": limb_damage[BJJEnums.LimbType.RIGHT_ARM],
			"left_leg": limb_damage[BJJEnums.LimbType.LEFT_LEG],
			"right_leg": limb_damage[BJJEnums.LimbType.RIGHT_LEG],
			"core": limb_damage[BJJEnums.LimbType.CORE]
		},
		"perk_modifiers": perk_modifiers.duplicate()
	}

func load_from_dict(data: Dictionary) -> void:
	if data.has("gas"):
		current_gas = float(data["gas"])
	if data.has("max_gas"):
		max_gas = float(data["max_gas"])
	if data.has("grip_integrity"):
		grip_integrity = float(data["grip_integrity"])
	if data.has("limb_fatigue"):
		for limb_str in data["limb_fatigue"].keys():
			var limb_enum = _string_to_limb(limb_str)
			if limb_enum != -1:
				limb_fatigue[limb_enum] = float(data["limb_fatigue"][limb_str])
	if data.has("limb_damage"):
		for limb_str in data["limb_damage"].keys():
			var limb_enum = _string_to_limb(limb_str)
			if limb_enum != -1:
				limb_damage[limb_enum] = float(data["limb_damage"][limb_str])
	if data.has("perk_modifiers"):
		perk_modifiers = data["perk_modifiers"].duplicate()
