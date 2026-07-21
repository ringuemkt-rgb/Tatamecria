extends Node
class_name GripState

# Gerenciamento de pegadas e postura
# Controla grips ofensivos/defensivos, quebras de pegada e vantagens posicionais

signal grip_established(grip_type: String, dominant: bool)
signal grip_broken(grip_type: String)
signal posture_changed(new_posture: String)

enum GripType {
	COLLAR,             # Pegada na gola
	SLEEVE,             # Pegada na manga
	PANT,               # Pegada na calça
	WRIST,              # Controle de pulso
	TRICEP,             # Controle de tríceps
	SEATBELT,           # Controle de costas
	UNDERHOOK,          # Gancho por baixo
	OVERHOOK,           # Gancho por cima
	CLINCH,             # Clinch de cabeça/braço
	NONE                # Sem pegada
}

enum Posture {
	NEUTRAL,            # Postura neutra
	BASED,              # Base firme
	BROKEN,             # Postura quebrada
	LOW,                # Postura baixa (defensiva)
	HIGH                # Postura alta (ofensiva)
}

# Grips ativos do lutador
var active_grips: Dictionary = {}  # {grip_name: {type, strength, direction}}
var opponent_grips: Dictionary = {}  # Grips que o oponente tem em nós

# Postura atual
var current_posture: Posture = Posture.NEUTRAL
var posture_stability: float = 100.0
var max_posture_stability: float = 100.0

# Stats
var grip_strength: float = 50.0
var grip_technique: float = 50.0
var posture_control: float = 50.0

# Modificadores de perks
var perk_modifiers: Dictionary = {
	"grip_strength_bonus": 0.0,
	"grip_tech_bonus": 0.0,
	"posture_stability_bonus": 0.0,
	"grip_break_resistance": 0.0
}

var fighter_id: String = ""

func _ready() -> void:
	pass

func initialize(id: String, base_stats: Dictionary) -> void:
	fighter_id = id
	grip_strength = float(base_stats.get("grip_strength", base_stats.get("grip", 50)))
	grip_technique = float(base_stats.get("grip_technique", 50))
	posture_control = float(base_stats.get("posture_control", 50))
	posture_stability = max_posture_stability

# ==================== GRIP MANAGEMENT ====================

func establish_grip(grip_name: String, grip_type: GripType, target_location: String, strength: float = 1.0) -> bool:
	# Verifica se já existe grip neste local
	if active_grips.has(grip_name):
		return false
	
	var effective_strength = strength * get_effective_grip_strength()
	active_grips[grip_name] = {
		"type": grip_type,
		"target": target_location,
		"strength": effective_strength,
		"established_at": Time.get_ticks_msec()
	}
	
	grip_established.emit(grip_name, effective_strength >= 0.7)
	return true

func break_grip(grip_name: String, break_force: float) -> bool:
	var grip_data = active_grips.get(grip_name)
	if not grip_data:
		# Tenta quebrar grip do oponente
		return break_opponent_grip(grip_name, break_force)
	
	var resistance = grip_data["strength"] * (1.0 + perk_modifiers.get("grip_break_resistance", 0.0))
	
	if break_force >= resistance:
		active_grips.erase(grip_name)
		grip_broken.emit(grip_name)
		return true
	
	# Enfraquece o grip
	grip_data["strength"] = max(0.0, grip_data["strength"] - (break_force * 0.3))
	active_grips[grip_name] = grip_data
	return false

func break_opponent_grip(grip_name: String, break_force: float) -> bool:
	var grip_data = opponent_grips.get(grip_name)
	if not grip_data:
		return false
	
	if break_force >= grip_data["strength"]:
		opponent_grips.erase(grip_name)
		grip_broken.emit(grip_name)
		return true
	
	grip_data["strength"] = max(0.0, grip_data["strength"] - (break_force * 0.3))
	opponent_grips[grip_name] = grip_data
	return false

func add_opponent_grip(grip_name: String, grip_type: GripType, strength: float) -> void:
	opponent_grips[grip_name] = {
		"type": grip_type,
		"strength": strength,
		"target": "self"
	}

func get_active_grip_count() -> int:
	return active_grips.size()

func get_opponent_grip_count() -> int:
	return opponent_grips.size()

func has_dominant_grip() -> bool:
	for grip_data in active_grips.values():
		if float(grip_data.get("strength", 0)) >= 0.7:
			return true
	return false

func get_grip_score() -> float:
	var score: float = 0.0
	for grip_data in active_grips.values():
		score += float(grip_data.get("strength", 0))
	
	# Penaliza por grips do oponente
	for grip_data in opponent_grips.values():
		score -= float(grip_data.get("strength", 0)) * 0.5
	
	return score

# ==================== POSTURE MANAGEMENT ====================

func set_posture(new_posture: Posture) -> void:
	current_posture = new_posture
	var posture_str = _posture_to_string(new_posture)
	posture_changed.emit(posture_str)

func damage_posture(amount: float) -> void:
	posture_stability = max(0.0, posture_stability - amount)
	
	if posture_stability <= max_posture_stability * 0.3:
		set_posture(Posture.BROKEN)
	elif posture_stability <= max_posture_stability * 0.6:
		set_posture(Posture.LOW)
	elif posture_stability >= max_posture_stability * 0.8:
		set_posture(Posture.HIGH)

func recover_posture(amount: float) -> void:
	posture_stability = min(max_posture_stability, posture_stability + amount)
	
	if posture_stability >= max_posture_stability * 0.8:
		set_posture(Posture.HIGH)
	elif posture_stability >= max_posture_stability * 0.5:
		set_posture(Posture.NEUTRAL)

func regen_posture(delta: float) -> void:
	var regen_rate = 10.0 * (1.0 + perk_modifiers.get("posture_stability_bonus", 0.0))
	recover_posture(regen_rate * delta)

func is_posture_broken() -> bool:
	return current_posture == Posture.BROKEN or posture_stability <= max_posture_stability * 0.2

func get_posture_multiplier() -> float:
	match current_posture:
		Posture.HIGH: return 1.2
		Posture.NEUTRAL: return 1.0
		Posture.LOW: return 0.8
		Posture.BASED: return 1.1
		Posture.BROKEN: return 0.5
	return 1.0

# ==================== CLASH & RESISTANCE ====================

func contest_grip(attacker_grip_strength: float) -> bool:
	# Retorna true se defender com sucesso
	var defense_score = get_effective_grip_strength() * posture_stability / max_posture_stability
	return defense_score >= attacker_grip_strength

func get_effective_grip_strength() -> float:
	var base = grip_strength / 100.0
	var tech_bonus = grip_technique / 200.0  # Técnica vale até 50% extra
	var perk_bonus = perk_modifiers.get("grip_strength_bonus", 0.0) + perk_modifiers.get("grip_tech_bonus", 0.0)
	
	# Reduz por fadiga nos braços (se FighterCondition estiver disponível)
	var fatigue_penalty = 0.0
	if Engine.has_singleton("FighterCondition"):
		pass  # Implementação futura
	
	return clamp(base + tech_bonus + perk_bonus, 0.0, 2.0)

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

func _posture_to_string(p: Posture) -> String:
	match p:
		Posture.NEUTRAL: return "NEUTRAL"
		Posture.BASED: return "BASED"
		Posture.BROKEN: return "BROKEN"
		Posture.LOW: return "LOW"
		Posture.HIGH: return "HIGH"
	return "NEUTRAL"

func get_state_dict() -> Dictionary:
	var grips_list: Array = []
	for name in active_grips.keys():
		grips_list.append({
			"name": name,
			"type": active_grips[name]["type"],
			"strength": active_grips[name]["strength"]
		})
	
	var opp_grips_list: Array = []
	for name in opponent_grips.keys():
		opp_grips_list.append({
			"name": name,
			"type": opponent_grips[name]["type"],
			"strength": opponent_grips[name]["strength"]
		})
	
	return {
		"active_grips": grips_list,
		"opponent_grips": opp_grips_list,
		"posture": _posture_to_string(current_posture),
		"posture_stability": posture_stability,
		"grip_strength": grip_strength,
		"grip_technique": grip_technique
	}
