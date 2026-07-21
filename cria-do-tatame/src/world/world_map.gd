extends Node
class_name WorldMap

# Lógica dos hubs: Terreiro, Arena do Dique, Manguezal, Zambiapunga
# Navegação por menu de Hub com animação rápida de transição

signal hub_changed(new_hub_id: String)
signal travel_started(from_hub: String, to_hub: String, cost: Dictionary)
signal travel_completed(hub_id: String)
signal hub_unlocked(hub_id: String)

# Hubs disponíveis
var hubs: Dictionary = {
	"terreiro_da_luta": {
		"name": "Terreiro da Luta",
		"description": "Onde tudo começou. Mestre Dendê ensina os fundamentos.",
		"unlocked": true,
		"location": "Centro do Baixo Sul",
		"features": ["treino", "tekuro_npc", "deck_builder"],
		"connections": ["arena_dique", "manguezal"]
	},
	"arena_dique": {
		"name": "Arena do Dique",
		"description": "Lutas oficiais. Público quente, pressão real.",
		"unlocked": false,
		"location": "Dique, área industrial",
		"features": ["combate_ranked", "publico", "premiacao"],
		"connections": ["terreiro_da_luta", "zambiapunga"]
	},
	"manguezal": {
		"name": "Manguezal",
		"description": "Treino de resistência em terreno irregular.",
		"unlocked": false,
		"location": "Beira-rio, mangue",
		"features": ["treino_resistencia", "pesca", "coleta"],
		"connections": ["terreiro_da_luta"]
	},
	"zambiapunga": {
		"name": "Zambiapunga",
		"description": "Comunidade pesqueira. Gente simples, coração grande.",
		"unlocked": false,
		"location": "Costa do Baixo Sul",
		"features": ["descanso", "cura", "historias"],
		"connections": ["arena_dique"]
	}
}

# Hub atual
var current_hub: String = "terreiro_da_luta"

# Custo de viagem entre hubs
var travel_costs: Dictionary = {
	"terreiro_da_luta_arena_dique": {"time": 30, "stamina": 10},
	"terreiro_da_luta_manguezal": {"time": 20, "stamina": 15},
	"arena_dique_zambiapunga": {"time": 25, "stamina": 8},
	"manguezal_terreiro_da_luta": {"time": 20, "stamina": 10},
	"zambiapunga_arena_dique": {"time": 25, "stamina": 8}
}

func _ready() -> void:
	pass

# ==================== HUB MANAGEMENT ====================

func get_current_hub() -> Dictionary:
	return hubs.get(current_hub, {})

func get_hub_by_id(hub_id: String) -> Dictionary:
	return hubs.get(hub_id, {})

func get_available_hubs() -> Array:
	var available: Array = []
	for hub_id in hubs.keys():
		if hubs[hub_id]["unlocked"]:
			available.append(hub_id)
	return available

func is_hub_unlocked(hub_id: String) -> bool:
	var hub = hubs.get(hub_id)
	return hub != null and hub["unlocked"]

func unlock_hub(hub_id: String) -> Dictionary:
	if not hubs.has(hub_id):
		return {"ok": false, "error": "hub_not_found"}
	
	if hubs[hub_id]["unlocked"]:
		return {"ok": false, "error": "already_unlocked"}
	
	hubs[hub_id]["unlocked"] = true
	hub_unlocked.emit(hub_id)
	
	return {"ok": true, "hub": hubs[hub_id]}

# ==================== TRAVEL SYSTEM ====================

func can_travel(to_hub: String) -> Dictionary:
	if not hubs.has(to_hub):
		return {"ok": false, "error": "hub_not_found"}
	
	if to_hub == current_hub:
		return {"ok": false, "error": "already_at_destination"}
	
	if not hubs[to_hub]["unlocked"]:
		return {"ok": false, "error": "hub_locked"}
	
	# Verifica conexão
	var current_data = hubs.get(current_hub, {})
	var connections: Array = current_data.get("connections", [])
	if not connections.has(to_hub):
		return {"ok": false, "error": "no_direct_connection"}
	
	return {"ok": true}

func get_travel_cost(to_hub: String) -> Dictionary:
	var route_key = "%s_%s" % [current_hub, to_hub]
	return travel_costs.get(route_key, {"time": 60, "stamina": 20})

func travel_to(to_hub: String, player_stamina: float) -> Dictionary:
	var check = can_travel(to_hub)
	if not check["ok"]:
		return check
	
	var cost = get_travel_cost(to_hub)
	
	if player_stamina < cost["stamina"]:
		return {"ok": false, "error": "insufficient_stamina", "required": cost["stamina"]}
	
	var from_hub = current_hub
	current_hub = to_hub
	
	travel_started.emit(from_hub, to_hub, cost)
	
	# Simula tempo de viagem (pode ser substituído por animação)
	await get_tree().create_timer(1.0).timeout
	
	travel_completed.emit(to_hub)
	hub_changed.emit(to_hub)
	
	return {
		"ok": true,
		"from": from_hub,
		"to": to_hub,
		"cost": cost
	}

# ==================== HUB FEATURES ====================

func get_hub_features(hub_id: String) -> Array:
	var hub = hubs.get(hub_id)
	if hub:
		return hub.get("features", [])
	return []

func has_feature(hub_id: String, feature: String) -> bool:
	var features = get_hub_features(hub_id)
	return features.has(feature)

# ==================== LORE & ATMOSPHERE ====================

func get_hub_flavor_text(hub_id: String) -> String:
	match hub_id:
		"terreiro_da_luta":
			return "Cheiro de tatame velho e determinação nova."
		"arena_dique":
			return "Grito da torcida ecoa como trovão."
		"manguezal":
			return "Raízes expostas como lições não aprendidas."
		"zambiapunga":
			return "Mar calmo esconde maré forte."
	return ""

func get_hub_music(hub_id: String) -> String:
	match hub_id:
		"terreiro_da_luta":
			return "res://assets/audio/music/terreiro_ambient.ogg"
		"arena_dique":
			return "res://assets/audio/music/arena_crowd.ogg"
		"manguezal":
			return "res://assets/audio/music/nature_sounds.ogg"
		"zambiapunga":
			return "res://assets/audio/music/coastal_calm.ogg"
	return ""

# ==================== SAVE/LOAD ====================

func save_to_dict() -> Dictionary:
	var unlocked_hubs: Array = []
	for hub_id in hubs.keys():
		if hubs[hub_id]["unlocked"]:
			unlocked_hubs.append(hub_id)
	
	return {
		"current_hub": current_hub,
		"unlocked_hubs": unlocked_hubs
	}

func load_from_dict(data: Dictionary) -> void:
	if data.has("current_hub"):
		current_hub = str(data["current_hub"])
	
	if data.has("unlocked_hubs"):
		# Reseta todos primeiro
		for hub_id in hubs.keys():
			hubs[hub_id]["unlocked"] = false
		
		# Aplica desbloqueios salvos
		for hub_id in data["unlocked_hubs"]:
			if hubs.has(hub_id):
				hubs[hub_id]["unlocked"] = true
