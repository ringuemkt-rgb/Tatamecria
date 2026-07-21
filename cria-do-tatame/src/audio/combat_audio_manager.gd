extends Node
class_name CombatAudioManager

# Autoload: Respiração dinâmica, som de pano e impactos
# Sistema de áudio de combate de Jiu-Jitsu

signal sfx_played(sfx_type: String)
signal music_changed(track_name: String)

# Configurações de volume
var master_volume: float = 1.0
var sfx_volume: float = 0.8
var music_volume: float = 0.6
var voice_volume: float = 0.9

# Estado atual
var current_combat_intensity: float = 0.0
var is_in_combat: bool = false

# Players de áudio (preencher no _ready)
var _music_player: AudioStreamPlayer = null
var _sfx_pool: Array[AudioStreamPlayer] = []
var _voice_player: AudioStreamPlayer = null

# Biblioteca de sons (paths relativos a assets/audio/)
const SFX_LIBRARY: Dictionary = {
	"impact_body": "sfx/combat/impact_body.wav",
	"impact_mat": "sfx/combat/impact_mat.wav",
	"grip_fabric": "sfx/combat/grip_fabric.wav",
	"footstep_tatame": "sfx/combat/footstep.wav",
	"breath_light": "sfx/combat/breath_light.wav",
	"breath_heavy": "sfx/combat/breath_heavy.wav",
	"breath_strain": "sfx/combat/breath_strain.wav",
	"sweep_woosh": "sfx/combat/sweep_woosh.wav",
	"submission_cloth": "sfx/combat/submission_cloth.wav",
	"referee_whistle": "sfx/combat/referee_whistle.wav",
	"crowd_cheer": "sfx/crowd/cheer_small.wav",
	"crowd_gasps": "sfx/crowd/gasps.wav",
	"tap_sound": "sfx/combat/tap_sound.wav"
}

const MUSIC_LIBRARY: Dictionary = {
	"combat_low": "music/combat_ambient_low.ogg",
	"combat_medium": "music/combat_ambient_medium.ogg",
	"combat_high": "music/combat_ambient_high.ogg",
	"victory": "music/victory_theme.ogg",
	"defeat": "music/defeat_theme.ogg",
	"menu": "music/menu_theme.ogg"
}

# Cache de streams carregados
var _loaded_sounds: Dictionary = {}
var _loaded_music: Dictionary = {}

func _ready() -> void:
	_setup_audio_players()
	_preload_common_sounds()

func _setup_audio_players() -> void:
	# Music player
	_music_player = AudioStreamPlayer.new()
	_music_player.bus = "Music"
	add_child(_music_player)
	
	# Voice player
	_voice_player = AudioStreamPlayer.new()
	_voice_player.bus = "Voice"
	add_child(_voice_player)
	
	# SFX pool (4 players para sobreposição)
	for i in range(4):
		var player = AudioStreamPlayer.new()
		player.bus = "SFX"
		add_child(player)
		_sfx_pool.append(player)

func _preload_common_sounds() -> void:
	# Pré-carrega sons comuns
	var common_sounds = ["impact_body", "grip_fabric", "breath_light", "footstep_tatame"]
	for sfx_key in common_sounds:
		if SFX_LIBRARY.has(sfx_key):
			_load_sound(sfx_key)

# ==================== SOUND LOADING ====================

func _load_sound(sfx_key: String) -> AudioStream:
	if _loaded_sounds.has(sfx_key):
		return _loaded_sounds[sfx_key]
	
	var path = SFX_LIBRARY.get(sfx_key, "")
	if path == "":
		push_warning("Sound not found: %s" % sfx_key)
		return null
	
	# Tenta carregar o arquivo
	if ResourceLoader.exists(path):
		var stream = ResourceLoader.load(path)
		_loaded_sounds[sfx_key] = stream
		return stream
	else:
		push_warning("Sound file not found: %s" % path)
		return null

func _load_music(music_key: String) -> AudioStream:
	if _loaded_music.has(music_key):
		return _loaded_music[music_key]
	
	var path = MUSIC_LIBRARY.get(music_key, "")
	if path == "":
		push_warning("Music not found: %s" % music_key)
		return null
	
	if ResourceLoader.exists(path):
		var stream = ResourceLoader.load(path)
		_loaded_music[music_key] = stream
		return stream
	else:
		push_warning("Music file not found: %s" % path)
		return null

# ==================== SFX PLAYBACK ====================

func play_sfx(sfx_key: String, pitch_variance: float = 0.0, volume_db: float = 0.0) -> void:
	var stream = _load_sound(sfx_key)
	if not stream:
		return
	
	# Encontra player disponível no pool
	var player: AudioStreamPlayer = null
	for p in _sfx_pool:
		if not p.playing:
			player = p
			break
	
	if not player:
		# Todos ocupados, usa o primeiro (interrompe anterior)
		player = _sfx_pool[0]
	
	player.stream = stream
	player.volume_db = volume_db
	
	# Variação de pitch para naturalidade
	if pitch_variance > 0:
		player.pitch_scale = randf_range(1.0 - pitch_variance, 1.0 + pitch_variance)
	else:
		player.pitch_scale = 1.0
	
	player.play()
	sfx_played.emit(sfx_key)

func play_impact(impact_type: String, intensity: float = 1.0) -> void:
	match impact_type:
		"body":
			play_sfx("impact_body", 0.15, linear_to_db(intensity))
		"mat":
			play_sfx("impact_mat", 0.1, linear_to_db(intensity * 0.8))
		"fabric":
			play_sfx("grip_fabric", 0.2, linear_to_db(intensity * 0.6))

func play_footstep(surface: String = "tatame") -> void:
	play_sfx("footstep_tatame", 0.1, linear_to_db(0.3))

func play_breath(breath_type: String = "light") -> void:
	match breath_type:
		"light":
			play_sfx("breath_light", 0.05, linear_to_db(0.4))
		"heavy":
			play_sfx("breath_heavy", 0.1, linear_to_db(0.6))
		"strain":
			play_sfx("breath_strain", 0.0, linear_to_db(0.8))

func play_technique_sound(technique_category: String) -> void:
	match technique_category:
		"queda":
			play_sfx("sweep_woosh", 0.2, linear_to_db(0.7))
		"raspagem":
			play_sfx("sweep_woosh", 0.15, linear_to_db(0.6))
		"finalizacao":
			play_sfx("submission_cloth", 0.1, linear_to_db(0.8))
		"passagem":
			play_sfx("grip_fabric", 0.2, linear_to_db(0.5))

func play_crowd_reaction(reaction_type: String) -> void:
	match reaction_type:
		"cheer":
			play_sfx("crowd_cheer", 0.0, linear_to_db(0.8))
		"gasps":
			play_sfx("crowd_gasps", 0.0, linear_to_db(0.7))

func play_tap_sound() -> void:
	play_sfx("tap_sound", 0.0, linear_to_db(1.0))

func play_referee_whistle() -> void:
	play_sfx("referee_whistle", 0.0, linear_to_db(0.9))

# ==================== DYNAMIC BREATHING ====================

var _breath_timer: float = 0.0
var _breath_interval: float = 2.0  # Segundos entre respirações

func _process(delta: float) -> void:
	if is_in_combat:
		_breath_timer += delta
		if _breath_timer >= _breath_interval:
			_breath_timer = 0.0
			_update_breathing()

func _update_breathing() -> void:
	# Intervalo baseado na intensidade do combate
	_breath_interval = lerp(2.0, 0.5, current_combat_intensity)
	
	# Tipo de respiração baseado na intensidade
	var breath_type: String
	if current_combat_intensity < 0.3:
		breath_type = "light"
	elif current_combat_intensity < 0.7:
		breath_type = "heavy"
	else:
		breath_type = "strain"
	
	play_breath(breath_type)

func set_combat_intensity(intensity: float) -> void:
	current_combat_intensity = clamp(intensity, 0.0, 1.0)
	
	# Ajusta volume da respiração
	if _voice_player:
		_voice_player.volume_db = linear_to_db(voice_volume * (0.5 + current_combat_intensity * 0.5))

# ==================== MUSIC MANAGEMENT ====================

func play_music(track_key: String, fade_in: float = 1.0) -> void:
	var stream = _load_music(track_key)
	if not stream:
		return
	
	if _music_player:
		_music_player.stream = stream
		
		if fade_in > 0:
			_music_player.volume_db = -80.0  # Mudo
			_music_player.play()
			
			var tween = create_tween()
			tween.tween_property(_music_player, "volume_db", linear_to_db(music_volume), fade_in)
		else:
			_music_player.volume_db = linear_to_db(music_volume)
			_music_player.play()
		
		music_changed.emit(track_key)

func stop_music(fade_out: float = 0.5) -> void:
	if not _music_player or not _music_player.playing:
		return
	
	if fade_out > 0:
		var tween = create_tween()
		tween.tween_property(_music_player, "volume_db", -80.0, fade_out)
		tween.tween_callback(_music_player.stop)
	else:
		_music_player.stop()

func transition_music(new_track_key: String, crossfade: float = 2.0) -> void:
	# Crossfade entre tracks
	var old_stream = _music_player.stream
	var new_stream = _load_music(new_track_key)
	
	if not new_stream:
		return
	
	# Cria segundo player temporário para crossfade
	var temp_player = AudioStreamPlayer.new()
	temp_player.bus = "Music"
	temp_player.stream = new_stream
	temp_player.volume_db = -80.0
	add_child(temp_player)
	temp_player.play()
	
	var tween = create_tween()
	tween.tween_property(_music_player, "volume_db", -80.0, crossfade)
	tween.tween_property(temp_player, "volume_db", linear_to_db(music_volume), crossfade)
	tween.tween_callback(func():
		_music_player.stream = new_stream
		_music_player.volume_db = linear_to_db(music_volume)
		temp_player.queue_free()
		music_changed.emit(new_track_key)
	)

func update_combat_music() -> void:
	# Atualiza música baseada na intensidade
	if current_combat_intensity < 0.3:
		play_music("combat_low", 1.0)
	elif current_combat_intensity < 0.7:
		play_music("combat_medium", 1.0)
	else:
		play_music("combat_high", 1.0)

# ==================== CONTEXTUAL AUDIO ====================

func on_transition_start(transition_type: String) -> void:
	match transition_type:
		"takedown_entry":
			play_technique_sound("queda")
		"sweep_attempt":
			play_technique_sound("raspagem")
		"submission_chain":
			play_technique_sound("finalizacao")
		"guard_pass":
			play_technique_sound("passagem")

func on_clash_result(success: bool, result_type: String) -> void:
	if success:
		match result_type:
			"takedown_landed":
				play_impact("body", 0.8)
				play_impact("mat", 0.6)
				play_crowd_reaction("cheer")
			"sweep_successful":
				play_impact("mat", 0.5)
				play_technique_sound("raspagem")
			"submission_position":
				play_sfx("submission_cloth", 0.1, linear_to_db(0.9))
				play_crowd_reaction("gasps")
	else:
		# Defesa bem sucedida
		play_sfx("grip_fabric", 0.2, linear_to_db(0.4))

func on_fighter_low_gas() -> void:
	# Feedback sonoro de gás baixo
	play_breath("strain")
	# Pode adicionar som de coração batendo

func on_tap_out() -> void:
	play_tap_sound()
	play_referee_whistle()
	stop_music(0.5)

# ==================== VOLUME CONTROL ====================

func set_master_volume(value: float) -> void:
	master_volume = clamp(value, 0.0, 1.0)
	AudioServer.set_bus_mute(0, master_volume <= 0.0)
	AudioServer.set_bus_volume_db(0, linear_to_db(master_volume))

func set_sfx_volume(value: float) -> void:
	sfx_volume = clamp(value, 0.0, 1.0)
	var sfx_bus_idx = AudioServer.get_bus_index("SFX")
	if sfx_bus_idx != -1:
		AudioServer.set_bus_volume_db(sfx_bus_idx, linear_to_db(sfx_volume))

func set_music_volume(value: float) -> void:
	music_volume = clamp(value, 0.0, 1.0)
	var music_bus_idx = AudioServer.get_bus_index("Music")
	if music_bus_idx != -1:
		AudioServer.set_bus_volume_db(music_bus_idx, linear_to_db(music_volume))

func set_voice_volume(value: float) -> void:
	voice_volume = clamp(value, 0.0, 1.0)
	var voice_bus_idx = AudioServer.get_bus_index("Voice")
	if voice_bus_idx != -1:
		AudioServer.set_bus_volume_db(voice_bus_idx, linear_to_db(voice_volume))

# ==================== COMBAT STATE ====================

func start_combat() -> void:
	is_in_combat = true
	current_combat_intensity = 0.0
	_breath_timer = 0.0
	update_combat_music()

func end_combat(victory: bool) -> void:
	is_in_combat = false
	current_combat_intensity = 0.0
	
	if victory:
		play_music("victory", 1.0)
	else:
		play_music("defeat", 1.0)

func reset() -> void:
	is_in_combat = false
	current_combat_intensity = 0.0
	_breath_timer = 0.0
	
	# Para todos os sons
	_music_player.stop()
	for player in _sfx_pool:
		player.stop()
	if _voice_player:
		_voice_player.stop()

# ==================== UTILITÁRIOS ====================

func linear_to_db(linear: float) -> float:
	if linear <= 0.0:
		return -80.0
	return 20.0 * log(linear) / log(10.0)

func get_state_dict() -> Dictionary:
	return {
		"master_volume": master_volume,
		"sfx_volume": sfx_volume,
		"music_volume": music_volume,
		"voice_volume": voice_volume,
		"is_in_combat": is_in_combat,
		"current_combat_intensity": current_combat_intensity
	}
