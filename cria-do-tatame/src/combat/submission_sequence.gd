extends Node
class_name SubmissionSequence

# Máquina de estados para finalizações multi-estágio
# Exemplo: Armlock = Setup -> Isolate -> Lock -> Finish/Tap/Escape

signal stage_changed(new_stage: String, progress: float)
signal submission_threat_updated(threat_level: float)
signal tap_imminent(is_imminent: bool)
signal escape_progress_changed(escaper_id: String, progress: float)

enum SubmissionStage {
	NONE,               # Sem finalização ativa
	SETUP,              # Criando a posição
	ISOLATE,            # Isolando membro/região
	LOCK,               # Aplicando a chave
	FINISH,             # Forçando o tap
	TAP_ESCAPE,         # Fase de tap ou escape
	COMPLETE            # Finalizada (tap ou escape)
}

enum SubmissionType {
	ARMLOCK,
	TRIANGLE,
	REAR_NAKED,
	KIMURA,
	AMERICANA,
	GUILLOTINE,
	BOW_AND_ARROW,
	OMoplata
}

# Estado atual
var current_stage: SubmissionStage = SubmissionStage.NONE
var submission_type: SubmissionType = SubmissionType.ARMLOCK
var attacker_id: String = ""
var defender_id: String = ""

# Progresso da finalização (0-100)
var submission_progress: float = 0.0
var escape_progress: float = 0.0

# Thresholds
var lock_threshold: float = 60.0    # Quando começa a doer
var tap_threshold: float = 90.0     # Quando tap é inevitável sem escape
var escape_window: float = 3.0      # Segundos para escapar após lock

# Timing
var stage_entered_at: int = 0
var current_stage_duration: float = 0.0

# Stats dos lutadores
var attacker_control: float = 50.0
var defender_strength: float = 50.0
var defender_technique: float = 50.0

# Estágios configuráveis por tipo de finalização
var stage_configs: Dictionary = {}

func _ready() -> void:
	_init_stage_configs()

func _init_stage_configs() -> void:
	# Configuração padrão para cada tipo de finalização
	stage_configs = {
		SubmissionType.ARMLOCK: {
			"stages": [SubmissionStage.SETUP, SubmissionStage.ISOLATE, SubmissionStage.LOCK, SubmissionStage.FINISH],
			"duration": {"SETUP": 2.0, "ISOLATE": 2.5, "LOCK": 3.0, "FINISH": 2.0},
			"control_required": {"SETUP": 30, "ISOLATE": 50, "LOCK": 70, "FINISH": 85}
		},
		SubmissionType.TRIANGLE: {
			"stages": [SubmissionStage.SETUP, SubmissionStage.ISOLATE, SubmissionStage.LOCK, SubmissionStage.FINISH],
			"duration": {"SETUP": 2.5, "ISOLATE": 2.0, "LOCK": 3.5, "FINISH": 2.5},
			"control_required": {"SETUP": 35, "ISOLATE": 55, "LOCK": 75, "FINISH": 90}
		},
		SubmissionType.REAR_NAKED: {
			"stages": [SubmissionStage.SETUP, SubmissionStage.ISOLATE, SubmissionStage.LOCK, SubmissionStage.FINISH],
			"duration": {"SETUP": 1.5, "ISOLATE": 2.0, "LOCK": 4.0, "FINISH": 3.0},
			"control_required": {"SETUP": 40, "ISOLATE": 60, "LOCK": 80, "FINISH": 95}
		}
	}

# ==================== SUBMISSION FLOW ====================

func start_submission(attacker: String, defender: String, sub_type: SubmissionType, initial_control: float) -> Dictionary:
	if current_stage != SubmissionStage.NONE:
		return {"ok": false, "error": "submission_already_active"}
	
	attacker_id = attacker
	defender_id = defender
	submission_type = sub_type
	current_stage = SubmissionStage.SETUP
	submission_progress = 0.0
	escape_progress = 0.0
	attacker_control = initial_control
	stage_entered_at = Time.get_ticks_msec()
	
	var config = stage_configs.get(sub_type, stage_configs[SubmissionType.ARMLOCK])
	current_stage_duration = config["duration"]["SETUP"]
	
	stage_changed.emit("SETUP", 0.0)
	submission_threat_updated.emit(0.0)
	
	return {
		"ok": true,
		"type": sub_type,
		"stages": config["stages"].size()
	}

func advance_stage() -> Dictionary:
	if current_stage == SubmissionStage.NONE:
		return {"ok": false, "error": "no_active_submission"}
	
	var config = stage_configs.get(submission_type, stage_configs[SubmissionType.ARMLOCK])
	var stages = config.get("stages", [])
	
	var current_idx = stages.find(current_stage)
	if current_idx < 0 or current_idx >= stages.size() - 1:
		return {"ok": false, "error": "cannot_advance_further"}
	
	# Verifica se atingiu controle necessário
	var next_stage = stages[current_idx + 1]
	var required_control = config["control_required"].get(next_stage, 50)
	
	if attacker_control < required_control:
		return {"ok": false, "error": "insufficient_control", "required": required_control}
	
	# Avança
	current_stage = next_stage
	submission_progress = float(current_idx + 1) / float(stages.size()) * 100.0
	stage_entered_at = Time.get_ticks_msec()
	current_stage_duration = config["duration"].get(next_stage, 2.0)
	
	stage_changed.emit(_stage_to_string(next_stage), submission_progress)
	submission_threat_updated.emit(_calculate_threat_level())
	
	if next_stage == SubmissionStage.LOCK:
		# Inicia timer de escape
		await get_tree().create_timer(escape_window).timeout
		if current_stage == SubmissionStage.LOCK:
			_check_tap_imminent()
	
	return {"ok": true, "new_stage": _stage_to_string(next_stage)}

func _check_tap_imminent() -> void:
	if current_stage == SubmissionStage.LOCK or current_stage == SubmissionStage.FINISH:
		var threat = _calculate_threat_level()
		if threat >= 0.8:
			tap_imminent.emit(true)

func update(delta: float, attacker_input: float, defender_input: float) -> Dictionary:
	if current_stage == SubmissionStage.NONE:
		return {"ok": false}
	
	var config = stage_configs.get(submission_type, stage_configs[SubmissionType.ARMLOCK])
	
	# Progresso baseado em input do atacante vs defensor
	var struggle_factor = attacker_input - defender_input
	var progress_rate = struggle_factor * delta * 10.0
	
	# Modificadores por estágio
	match current_stage:
		SubmissionStage.SETUP:
			submission_progress += progress_rate * 0.5
		SubmissionStage.ISOLATE:
			submission_progress += progress_rate * 0.7
		SubmissionStage.LOCK:
			submission_progress += progress_rate * 1.0
			escape_progress += defender_input * delta * 15.0
		SubmissionStage.FINISH:
			submission_progress += progress_rate * 1.2
			escape_progress += defender_input * delta * 20.0
	
	submission_progress = clamp(submission_progress, 0.0, 100.0)
	escape_progress = clamp(escape_progress, 0.0, 100.0)
	
	# Emite atualizações
	submission_threat_updated.emit(_calculate_threat_level())
	escape_progress_changed.emit(defender_id, escape_progress)
	
	# Verifica condições de término
	return _check_completion()

func _check_completion() -> Dictionary:
	if submission_progress >= 100.0:
		current_stage = SubmissionStage.COMPLETE
		stage_changed.emit("COMPLETE", 100.0)
		return {"ok": true, "result": "submission_complete", "winner": attacker_id}
	
	if escape_progress >= 100.0:
		current_stage = SubmissionStage.NONE
		stage_changed.emit("NONE", 0.0)
		return {"ok": true, "result": "escape_successful", "winner": defender_id}
	
	return {"ok": true, "ongoing": true}

func attempt_escape(escape_power: float) -> float:
	if current_stage not in [SubmissionStage.LOCK, SubmissionStage.FINISH]:
		return 0.0
	
	# Escape mais eficaz em estágios finais
	var stage_multiplier = 1.0
	match current_stage:
		SubmissionStage.LOCK: stage_multiplier = 1.0
		SubmissionStage.FINISH: stage_multiplier = 1.5
	
	var escape_gain = escape_power * stage_multiplier * 0.1
	escape_progress = min(100.0, escape_progress + escape_gain)
	escape_progress_changed.emit(defender_id, escape_progress)
	
	return escape_gain

func apply_damage(pain_level: float) -> void:
	# Dano aumenta pressão para o tap
	submission_progress += pain_level * 0.5
	submission_threat_updated.emit(_calculate_threat_level())

func _calculate_threat_level() -> float:
	var base_threat = submission_progress / 100.0
	
	# Aumenta drasticamente após threshold de tap
	if submission_progress >= tap_threshold:
		base_threat += 0.3
	
	return clamp(base_threat, 0.0, 1.0)

# ==================== UTILITÁRIOS ====================

func _stage_to_string(stage: SubmissionStage) -> String:
	match stage:
		SubmissionStage.NONE: return "NONE"
		SubmissionStage.SETUP: return "SETUP"
		SubmissionStage.ISOLATE: return "ISOLATE"
		SubmissionStage.LOCK: return "LOCK"
		SubmissionStage.FINISH: return "FINISH"
		SubmissionStage.TAP_ESCAPE: return "TAP_ESCAPE"
		SubmissionStage.COMPLETE: return "COMPLETE"
	return "NONE"

func reset() -> void:
	current_stage = SubmissionStage.NONE
	submission_type = SubmissionType.ARMLOCK
	attacker_id = ""
	defender_id = ""
	submission_progress = 0.0
	escape_progress = 0.0
	stage_entered_at = 0

func get_state_dict() -> Dictionary:
	return {
		"active": current_stage != SubmissionStage.NONE,
		"type": submission_type,
		"stage": _stage_to_string(current_stage),
		"attacker": attacker_id,
		"defender": defender_id,
		"progress": submission_progress,
		"escape_progress": escape_progress,
		"threat_level": _calculate_threat_level()
	}
