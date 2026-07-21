extends Node
class_name NavigationManager

# Autoload: Gerencia viagem, custo de tempo/stamina e desbloqueio de hubs
# Integra com WorldState e WorldMap

signal travel_initiated(from_hub: String, to_hub: String)
signal travel_progress_changed(progress: float)
signal travel_completed(new_hub: String)
signal stamina_changed(new_stamina: float)
signal time_passed(minutes: int)

# Estado do jogador
var current_stamina: float = 100.0
var max_stamina: float = 100.0
var stamina_regen_rate: float = 5.0  # Por segundo fora de combate

# Tempo do jogo (em minutos)
var game_time_minutes: int = 480  # Começa às 8:00
var time_scale: float = 1.0  # 1 minuto real = 1 minuto jogo

# Hub atual
var current_hub: String = "terreiro_da_luta"

# Referências
var _world_map: Node = null
var _world_state: Node = null

func _ready() -> void:
	await get_tree().create_timer(0.2).timeout
	_connect_to_managers()
	_start_stamina_regen()

func _connect_to_managers() -> void:
	if has_node("/root/WorldMap"):
		_world_map = get_node("/root/WorldMap")
	if has_node("/root/WorldState"):
		_world_state = get_node("/root/WorldState")

func _start_stamina_regen() -> void:
	while true:
		await get_tree().create_timer(1.0).timeout
		if not _is_in_combat():
			regen_stamina(stamina_regen_rate)

func _is_in_combat() -> bool:
	if has_node("/root/CombatManager"):
		return get_node("/root/CombatManager").is_running
	return false

# ==================== STAMINA MANAGEMENT ====================

func consume_stamina(amount: float) -> bool:
	if current_stamina < amount:
		return false
	current_stamina = max(0.0, current_stamina - amount)
	stamina_changed.emit(current_stamina)
	return true

func add_stamina(amount: float) -> void:
	current_stamina = min(max_stamina, current_stamina + amount)
	stamina_changed.emit(current_stamina)

func regen_stamina(amount: float) -> void:
	add_stamina(amount)

func get_stamina_percent() -> float:
	return current_stamina / max_stamina if max_stamina > 0 else 0.0

func is_stamina_critical() -> bool:
	return current_stamina <= max_stamina * 0.2

# ==================== TIME MANAGEMENT ====================

func pass_time(minutes: int) -> void:
	game_time_minutes += minutes
	
	# Wrap around 24 hours
	while game_time_minutes >= 1440:
		game_time_minutes -= 1440
	
	time_passed.emit(minutes)
	
	# Atualiza WorldState se disponível
	if _world_state:
		_world_state.game_time_minutes = game_time_minutes

func get_game_time() -> Dictionary:
	var hours = game_time_minutes / 60
	var mins = game_time_minutes % 60
	return {
		"hours": hours,
		"minutes": mins,
		"display": "%02d:%02d" % [hours, mins]
	}

func set_game_time(hours: int, minutes: int) -> void:
	game_time_minutes = hours * 60 + minutes

func is_night_time() -> bool:
	var hour = game_time_minutes / 60
	return hour >= 18 or hour < 6

# ==================== TRAVEL SYSTEM ====================

func travel_to(hub_id: String) -> Dictionary:
	if not _world_map:
		return {"ok": false, "error": "world_map_unavailable"}
	
	if hub_id == current_hub:
		return {"ok": false, "error": "already_at_destination"}
	
	# Verifica se pode viajar
	var check = _world_map.can_travel(hub_id)
	if not check["ok"]:
		return check
	
	# Obtém custo
	var cost = _world_map.get_travel_cost(hub_id)
	
	# Verifica stamina
	if not consume_stamina(float(cost["stamina"])):
		return {"ok": false, "error": "insufficient_stamina", "required": cost["stamina"]}
	
	var from_hub = current_hub
	travel_initiated.emit(from_hub, hub_id)
	
	# Progresso de viagem (animação/transição)
	var travel_duration = 1.0  # segundos
	var elapsed = 0.0
	
	while elapsed < travel_duration:
		await get_tree().create_timer(0.1).timeout
		elapsed += 0.1
		var progress = elapsed / travel_duration
		travel_progress_changed.emit(progress)
	
	# Completa viagem
	current_hub = hub_id
	pass_time(cost["time"])
	
	if _world_map:
		_world_map.current_hub = hub_id
	
	travel_completed.emit(hub_id)
	
	return {
		"ok": true,
		"from": from_hub,
		"to": hub_id,
		"cost": cost,
		"time_passed": cost["time"]
	}

func get_available_destinations() -> Array:
	if not _world_map:
		return []
	
	var available: Array = []
	var current_data = _world_map.get_current_hub()
	var connections: Array = current_data.get("connections", [])
	
	for hub_id in connections:
		if _world_map.is_hub_unlocked(hub_id):
			var cost = _world_map.get_travel_cost(hub_id)
			available.append({
				"hub_id": hub_id,
				"name": _world_map.get_hub_by_id(hub_id)["name"],
				"cost": cost,
				"can_afford": current_stamina >= cost["stamina"]
			})
	
	return available

# ==================== HUB UNLOCKING ====================

func unlock_hub(hub_id: String, condition_met: bool) -> Dictionary:
	if not condition_met:
		return {"ok": false, "error": "condition_not_met"}
	
	if not _world_map:
		return {"ok": false, "error": "world_map_unavailable"}
	
	return _world_map.unlock_hub(hub_id)

# ==================== FAST TRAVEL (desbloqueável) ====================

var fast_travel_unlocked: bool = false

func fast_travel_to(hub_id: String) -> Dictionary:
	if not fast_travel_unlocked:
		return {"ok": false, "error": "fast_travel_locked"}
	
	if not _world_map:
		return {"ok": false, "error": "world_map_unavailable"}
	
	if not _world_map.is_hub_unlocked(hub_id):
		return {"ok": false, "error": "hub_locked"}
	
	# Fast travel custa mais stamina mas é instantâneo
	var cost = {"stamina": 30, "time": 5}
	
	if not consume_stamina(float(cost["stamina"])):
		return {"ok": false, "error": "insufficient_stamina"}
	
	var from_hub = current_hub
	current_hub = hub_id
	_world_map.current_hub = hub_id
	pass_time(cost["time"])
	
	travel_completed.emit(hub_id)
	
	return {
		"ok": true,
		"instant": true,
		"cost": cost
	}

# ==================== SAVE/LOAD ====================

func save_to_dict() -> Dictionary:
	return {
		"current_hub": current_hub,
		"current_stamina": current_stamina,
		"game_time_minutes": game_time_minutes,
		"fast_travel_unlocked": fast_travel_unlocked
	}

func load_from_dict(data: Dictionary) -> void:
	if data.has("current_hub"):
		current_hub = str(data["current_hub"])
	if data.has("current_stamina"):
		current_stamina = float(data["current_stamina"])
	if data.has("game_time_minutes"):
		game_time_minutes = int(data["game_time_minutes"])
	if data.has("fast_travel_unlocked"):
		fast_travel_unlocked = bool(data["fast_travel_unlocked"])
