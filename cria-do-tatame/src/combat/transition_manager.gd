extends Node
class_name TransitionManager

# Autoload: Orquestrador de janelas de defesa, fintas e read_level
# Integra cartas do Deck com execução de técnicas

signal transition_started(transition_type: String, attacker_id: String)
signal defense_window_opened(direction: int, timing: float)
signal feint_executed(feint_type: String, success: bool)
signal clash_resolved(result: Dictionary)
signal transition_completed(success: bool, result_type: String)

# Configurações de timing (em segundos)
var default_defense_window: float = 0.5
var perfect_timing_window: float = 0.15
var late_timing_threshold: float = 0.35

# Estado atual
var current_transition: Dictionary = {}
var is_in_transition: bool = false
var defense_direction: BJJEnums.DefenseDirection = BJJEnums.DefenseDirection.CENTER
var timing_quality: float = 0.0  # 0.0 a 1.0

# Read level (leitura do oponente)
var read_level: int = 0  # 0-3: Nenhum, Básico, Intermediário, Avançado
var prediction_accuracy: float = 0.0

# Fintas disponíveis
var available_feints: Array[String] = ["level_change", "grip_fake", "direction_fake", "tempo_fake"]
var last_feint_time: int = 0
var feint_cooldown: int = 2000  # ms

# Referências aos sistemas
var _combat_manager: Node = null
var _deck_manager: Node = null

func _ready() -> void:
	# Aguarda os autoloads estarem disponíveis
	await get_tree().create_timer(0.1).timeout
	_connect_to_managers()

func _connect_to_managers() -> void:
	if has_node("/root/CombatManager"):
		_combat_manager = get_node("/root/CombatManager")
	if has_node("/root/DeckManager"):
		_deck_manager = get_node("/root/DeckManager")

# ==================== TRANSITION ORCHESTRATION ====================

func start_transition(card: Dictionary, attacker_id: String, target_state: String) -> Dictionary:
	if is_in_transition:
		return {"ok": false, "error": "transition_already_active"}
	
	current_transition = {
		"card": card,
		"attacker": attacker_id,
		"target_state": target_state,
		"started_at": Time.get_ticks_msec(),
		"type": _determine_transition_type(card)
	}
	
	is_in_transition = true
	transition_started.emit(current_transition["type"], attacker_id)
	
	# Abre janela de defesa para o oponente
	var defense_time = _calculate_defense_time(card)
	_open_defense_window(defense_time)
	
	return {"ok": true, "transition": current_transition}

func _determine_transition_type(card: Dictionary) -> String:
	var category = str(card.get("category", ""))
	match category:
		"queda": return "takedown_entry"
		"raspagem": return "sweep_attempt"
		"finalizacao": return "submission_chain"
		"passagem": return "guard_pass"
		"controle": return "position_upgrade"
		"defesa": return "counter_action"
		"pegada": return "grip_fight"
	return "neutral_transition"

func _calculate_defense_time(card: Dictionary) -> float:
	var base_time = default_defense_window
	
	# Modificadores da carta
	var power = float(card.get("base_power", 10))
	base_time *= (10.0 / max(power, 1.0))  # Cartas mais poderosas = menos tempo
	
	# Modificador de nível
	var level = int(card.get("level", 1))
	base_time *= (1.0 - (level * 0.05))  # -5% por nível
	
	# Bônus de read level
	if read_level >= 2:
		base_time *= 0.9  # -10% com read intermediário
	if read_level >= 3:
		base_time *= 0.85  # -15% adicional com read avançado
	
	return max(0.2, base_time)  # Mínimo de 0.2s

func _open_defense_window(duration: float) -> void:
	defense_direction = BJJEnums.DefenseDirection.CENTER
	timing_quality = 0.0
	
	# Emite sinal para UI mostrar direção de defesa
	defense_window_opened.emit(int(defense_direction), duration)
	
	# Timer interno para fechar janela
	await get_tree().create_timer(duration).timeout
	_close_defense_window()

func _close_defense_window() -> void:
	if not is_in_transition:
		return
	
	# Resolve a transição se defesa não foi inputada
	resolve_transition(false, defense_direction)

func input_defense(direction: BJJEnums.DefenseDirection, timing: float) -> bool:
	if not is_in_transition:
		return false
	
	defense_direction = direction
	timing_quality = clamp(timing, 0.0, 1.0)
	
	# Determina qualidade do timing
	var timing_result = _evaluate_timing(timing)
	
	return true

func _evaluate_timing(input_time: float) -> String:
	if input_time <= perfect_timing_window:
		return "perfect"
	elif input_time <= late_timing_threshold:
		return "good"
	else:
		return "late"

func resolve_transition(defense_success: bool, defense_dir: BJJEnums.DefenseDirection) -> Dictionary:
	if not is_in_transition:
		return {"ok": false, "error": "no_active_transition"}
	
	is_in_transition = false
	
	var result := {
		"success": false,
		"result_type": "",
		"modifier": 0.0,
		"xp_gain": 0
	}
	
	if defense_success:
		# Defesa bem sucedida
		result["success"] = false
		result["result_type"] = "defended"
		result["modifier"] = -0.18  # Janela de contra
		
		# XP de tentativa válida para o atacante
		if _deck_manager and current_transition.has("card"):
			var card_id = str(current_transition["card"].get("id", ""))
			if card_id != "":
				_deck_manager.consume_used_card(card_id, false)
	else:
		# Ataque bem sucedido
		result["success"] = true
		result["result_type"] = _determine_result_type()
		result["modifier"] = _calculate_success_modifier()
		
		# XP de sucesso para o atacante
		if _deck_manager and current_transition.has("card"):
			var card_id = str(current_transition["card"].get("id", ""))
			if card_id != "":
				_deck_manager.consume_used_card(card_id, true)
	
	transition_completed.emit(result["success"], result["result_type"])
	clash_resolved.emit(result)
	
	current_transition = {}
	return result

func _determine_result_type() -> String:
	var trans_type = current_transition.get("type", "")
	match trans_type:
		"takedown_entry": return "takedown_landed"
		"sweep_attempt": return "sweep_successful"
		"submission_chain": return "submission_position"
		"guard_pass": return "guard_passed"
		"position_upgrade": return "position_improved"
		"counter_action": return "counter_successful"
		"grip_fight": return "grip_won"
	return "transition_successful"

func _calculate_success_modifier() -> float:
	var modifier: float = 0.03  # Base disputed
	
	# Bônus de timing
	match _evaluate_timing(timing_quality):
		"perfect": modifier += 0.15
		"good": modifier += 0.08
		"late": modifier += 0.0
	
	# Bônus de read level
	modifier += float(read_level) * 0.03
	
	# Bônus de nível da carta
	var card = current_transition.get("card", {})
	var level = int(card.get("level", 1))
	modifier += float(level) * 0.02
	
	return clamp(modifier, -0.30, 0.35)

# ==================== FEINT SYSTEM ====================

func execute_feint(feint_type: String, attacker_id: String) -> Dictionary:
	var current_time = Time.get_ticks_msec()
	if current_time - last_feint_time < feint_cooldown:
		return {"ok": false, "error": "feint_on_cooldown"}
	
	if not available_feints.has(feint_type):
		return {"ok": false, "error": "invalid_feint_type"}
	
	last_feint_time = current_time
	
	# Chance de sucesso baseada em read level e técnica
	var success_chance = 0.3 + (float(read_level) * 0.15)
	var success = randf() < success_chance
	
	feint_executed.emit(feint_type, success)
	
	if success:
		# Aumenta read level temporariamente
		read_level = mini(3, read_level + 1)
		return {"ok": true, "success": true, "read_bonus": true}
	else:
		return {"ok": true, "success": false}

func cancel_feint() -> void:
	pass  # Pode implementar penalty se necessário

# ==================== READ LEVEL SYSTEM ====================

func update_read_level(successful_reads: int, total_attempts: int) -> void:
	if total_attempts == 0:
		prediction_accuracy = 0.0
	else:
		prediction_accuracy = float(successful_reads) / float(total_attempts)
	
	# Atualiza read level baseado na precisão
	if prediction_accuracy >= 0.7:
		read_level = 3  # Avançado
	elif prediction_accuracy >= 0.5:
		read_level = 2  # Intermediário
	elif prediction_accuracy >= 0.3:
		read_level = 1  # Básico
	else:
		read_level = 0  # Nenhum

func get_prediction_hint() -> String:
	if read_level == 0:
		return ""
	elif read_level == 1:
		return "Padrão básico detectado"
	elif read_level == 2:
		return "Tendência técnica identificada"
	else:
		return "Leitura completa do oponente"

# ==================== CARD INTEGRATION ====================

func can_play_card(card: Dictionary, current_state: String) -> bool:
	if not card:
		return false
	
	# Verifica estado válido
	var valid_states: Array = card.get("valid_states", [])
	if not valid_states.is_empty() and not valid_states.has(current_state):
		return false
	
	# Verifica recursos
	if _deck_manager:
		var resources = _get_current_resources()
		return card.can_activate(resources)
	
	return true

func _get_current_resources() -> Dictionary:
	# Obtém recursos atuais do CombatManager/FighterCondition
	return {
		"gas": 50.0,  # Placeholder - integrar com FighterCondition
		"focus": 30.0
	}

func play_card_from_hand(card_index: int, attacker_id: String) -> Dictionary:
	if not _deck_manager:
		return {"ok": false, "error": "deck_manager_unavailable"}
	
	var hand = _deck_manager.get_hand()
	if card_index < 0 or card_index >= hand.size():
		return {"ok": false, "error": "invalid_card_index"}
	
	var card_data = hand[card_index]
	var current_state = _combat_manager.get_current_state_name() if _combat_manager else "PLAYER_STANDING_NEUTRAL"
	
	if not can_play_card(DeckCard.from_dict(card_data), current_state):
		return {"ok": false, "error": "card_cannot_be_played"}
	
	# Inicia transição
	return start_transition(card_data, attacker_id, _get_target_state(card_data))

func _get_target_state(card: Dictionary) -> String:
	# Mapeia categoria da carta para estado alvo
	var category = str(card.get("category", ""))
	match category:
		"queda": return "PLAYER_TOP_CLINCH"
		"raspagem": return "PLAYER_TOP_GUARD"
		"finalizacao": return "PLAYER_SUBMISSION_ATTACK"
		"passagem": return "PLAYER_TOP_SIDE"
		"controle": return "PLAYER_TOP_MOUNT"
	return "PLAYER_STANDING_NEUTRAL"

# ==================== UTILITÁRIOS ====================

func reset() -> void:
	is_in_transition = false
	current_transition = {}
	defense_direction = BJJEnums.DefenseDirection.CENTER
	timing_quality = 0.0

func get_state_dict() -> Dictionary:
	return {
		"is_in_transition": is_in_transition,
		"current_transition": current_transition,
		"defense_direction": int(defense_direction),
		"timing_quality": timing_quality,
		"read_level": read_level,
		"prediction_accuracy": prediction_accuracy
	}
