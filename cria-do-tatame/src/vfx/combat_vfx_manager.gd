extends Node
class_name CombatVFXManager

# Autoload: Screen shake, partículas de poeira do tatame e suor
# Game Feel de combate de Jiu-Jitsu

signal vfx_triggered(vfx_type: String)

# Configurações de intensidade
var screen_shake_intensity: float = 1.0
var particle_density: float = 1.0
var color_grading_intensity: float = 0.5

# Referências (preencher no _ready com get_viewport())
var _camera: Camera2D = null
var _color_rect: ColorRect = null

# Timers internos
var _shake_tween: Tween = null
var _impact_flash_timer: float = 0.0

func _ready() -> void:
	# Aguarda cena principal carregar
	await get_tree().create_timer(0.5).timeout
	_find_camera()

func _find_camera() -> void:
	# Tenta encontrar a câmera principal
	if has_node("/root/CombatScene/Camera2D"):
		_camera = get_node("/root/CombatScene/Camera2D")
	elif get_viewport().get_camera_2d():
		_camera = get_viewport().get_camera_2d()

# ==================== SCREEN SHAKE ====================

func trigger_screen_shake(intensity: float, duration: float, frequency: float = 60.0) -> void:
	if not _camera:
		_find_camera()
	if not _camera:
		return
	
	intensity *= screen_shake_intensity
	
	if _shake_tween and _shake_tween.is_valid():
		_shake_tween.kill()
	
	_shake_tween = create_tween()
	_shake_tween.set_loops()
	
	var shake_amount = intensity * 10.0  # Escala para pixels
	
	for i in range(int(duration * frequency)):
		var offset = Vector2(
			randf_range(-shake_amount, shake_amount),
			randf_range(-shake_amount, shake_amount)
		)
		_shake_tween.tween_property(_camera, "offset", offset, 1.0 / frequency)
	
	# Retorna ao normal
	_shake_tween.tween_property(_camera, "offset", Vector2.ZERO, 0.1)
	vfx_triggered.emit("screen_shake")

func trigger_impact_shake(impact_type: String) -> void:
	match impact_type:
		"takedown":
			trigger_screen_shake(1.5, 0.4)
		"sweep":
			trigger_screen_shake(1.2, 0.3)
		"submission":
			trigger_screen_shake(2.0, 0.6)
		"guard_pass":
			trigger_screen_shake(0.8, 0.2)
		"escape":
			trigger_screen_shake(0.6, 0.15)
		_:
			trigger_screen_shake(0.5, 0.1)

# ==================== PARTICLES ====================

func spawn_mat_dust(position: Vector2, intensity: float = 1.0) -> void:
	# Partículas de poeira do tatame em movimentos bruscos
	var particles = GPUParticles2D.new()
	var material = ParticleProcessMaterial.new()
	
	material.amount = int(20 * intensity * particle_density)
	material.lifetime = 0.8
	material.speed_scale = 1.5
	
	# Emissão inicial
	material.emission_shape = ParticleProcessMaterial.EMISSION_SHAPE_SPHERE
	material.emission_sphere_radius = 8.0
	
	# Direção para cima
	material.direction = Vector3(0, -1, 0)
	material.spread = 45.0
	
	# Aparência
	material.scale_min = 0.3
	material.scale_max = 0.8
	material.color = Color(0.7, 0.6, 0.4, 0.6)  # Marrom claro
	
	particles.process_material = material
	particles.position = position
	
	# Adiciona à cena de combate
	if has_node("/root/CombatScene/VFXLayer"):
		get_node("/root/CombatScene/VFXLayer").add_child(particles)
	else:
		add_child(particles)
	
	# Auto-remove após lifetime
	var timer = get_tree().create_timer(material.lifetime + 0.2)
	timer.timeout.connect(particles.queue_free)
	
	vfx_triggered.emit("mat_dust")

func spawn_sweat_droplets(position: Vector2, count: int = 5) -> void:
	# Gotas de suor em esforço intenso
	var particles = GPUParticles2D.new()
	var material = ParticleProcessMaterial.new()
	
	material.amount = count
	material.lifetime = 0.6
	material.speed_scale = 2.0
	
	# Emissão direcional
	material.emission_shape = ParticleProcessMaterial.EMISSION_SHAPE_SPHERE
	material.emission_sphere_radius = 4.0
	material.direction = Vector3(1, 0, 0)  # Para o lado
	material.spread = 30.0
	
	# Aparência
	material.scale_min = 0.2
	material.scale_max = 0.5
	material.color = Color(0.8, 0.9, 1.0, 0.8)  # Azul claro translúcido
	
	particles.process_material = material
	particles.position = position
	
	if has_node("/root/CombatScene/VFXLayer"):
		get_node("/root/CombatScene/VFXLayer").add_child(particles)
	else:
		add_child(particles)
	
	var timer = get_tree().create_timer(material.lifetime + 0.2)
	timer.timeout.connect(particles.queue_free)
	
	vfx_triggered.emit("sweat")

func spawn_technique_trail(start_pos: Vector2, end_pos: Vector2, color: Color) -> void:
	# Rastro visual para técnicas rápidas
	var line = Line2D.new()
	line.add_point(start_pos)
	line.add_point(end_pos)
	line.width = 4.0
	line.default_color = color
	line.antialiased = true
	
	if has_node("/root/CombatScene/VFXLayer"):
		get_node("/root/CombatScene/VFXLayer").add_child(line)
	else:
		add_child(line)
	
	# Fade out
	var tween = create_tween()
	tween.tween_property(line, "modulate:a", 0.0, 0.3)
	tween.tween_callback(line.queue_free)
	
	vfx_triggered.emit("technique_trail")

# ==================== FLASH EFFECTS ====================

func trigger_impact_flash(position: Vector2, intensity: float = 1.0) -> void:
	# Flash branco no impacto
	var sprite = Sprite2D.new()
	var texture = PlaceholderTexture2D.new()
	texture.size = Vector2(64, 64)
	sprite.texture = texture
	sprite.modulate = Color(1.0, 1.0, 1.0, 0.8 * intensity)
	sprite.position = position
	
	if has_node("/root/CombatScene/VFXLayer"):
		get_node("/root/CombatScene/VFXLayer").add_child(sprite)
	else:
		add_child(sprite)
	
	var tween = create_tween()
	tween.tween_property(sprite, "scale", Vector2(2.0, 2.0), 0.15)
	tween.tween_property(sprite, "modulate:a", 0.0, 0.1)
	tween.tween_callback(sprite.queue_free)
	
	vfx_triggered.emit("impact_flash")

func trigger_success_flash() -> void:
	# Flash verde/ciano para sucesso de técnica
	var color_rect = ColorRect.new()
	color_rect.color = Color(0.2, 0.9, 0.6, 0.3)
	color_rect.set_anchors_preset(Control.PRESET_FULL_RECT)
	
	if has_node("/root/CombatScene/VFXLayer"):
		get_node("/root/CombatScene/VFXLayer").add_child(color_rect)
	else:
		add_child(color_rect)
	
	var tween = create_tween()
	tween.tween_property(color_rect, "modulate:a", 0.0, 0.2)
	tween.tween_callback(color_rect.queue_free)
	
	vfx_triggered.emit("success_flash")

# ==================== COLOR GRADING ====================

func set_combat_intensity(intensity: float) -> void:
	# Muda saturação/contraste baseado na intensidade do combate
	# 0.0 = calmo, 1.0 = pressão máxima
	color_grading_intensity = intensity
	
	# Implementação depende de post-processing do Godot 4
	# Pode usar ViewportTexture + ShaderMaterial
	
	vfx_triggered.emit("color_grade_change")

func set_low_health_warning(active: bool) -> void:
	# Overlay vermelho pulsante quando stamina/gás crítico
	if active:
		if not _color_rect:
			_color_rect = ColorRect.new()
			_color_rect.color = Color(1.0, 0.0, 0.0, 0.15)
			_color_rect.set_anchors_preset(Control.PRESET_FULL_RECT)
			
			if has_node("/root/CombatScene/VFXLayer"):
				get_node("/root/CombatScene/VFXLayer").add_child(_color_rect)
			else:
				add_child(_color_rect)
		
		# Pulso
		var tween = create_tween()
		tween.set_loops()
		tween.tween_property(_color_rect, "modulate:a", 0.3, 0.5)
		tween.tween_property(_color_rect, "modulate:a", 0.15, 0.5)
	else:
		if _color_rect:
			_color_rect.queue_free()
			_color_rect = null

# ==================== CONTEXTUAL VFX ====================

func on_transition_start(transition_type: String) -> void:
	match transition_type:
		"takedown_entry":
			spawn_mat_dust(get_viewport().get_visible_rect().size / 2.0, 0.8)
		"sweep_attempt":
			spawn_mat_dust(get_viewport().get_visible_rect().size / 2.0, 0.6)
		"submission_chain":
			spawn_sweat_droplets(get_viewport().get_visible_rect().size / 2.0, 8)

func on_clash_result(success: bool, result_type: String) -> void:
	if success:
		trigger_success_flash()
		match result_type:
			"takedown_landed":
				trigger_impact_shake("takedown")
			"sweep_successful":
				trigger_impact_shake("sweep")
			"submission_position":
				trigger_impact_shake("submission")
	else:
		# Falha/defesa
		trigger_screen_shake(0.3, 0.15)

# ==================== UTILITÁRIOS ====================

func reset() -> void:
	screen_shake_intensity = 1.0
	particle_density = 1.0
	color_grading_intensity = 0.5
	
	if _camera:
		_camera.offset = Vector2.ZERO
	if _shake_tween and _shake_tween.is_valid():
		_shake_tween.kill()
	
	set_low_health_warning(false)
	set_combat_intensity(0.0)

func get_state_dict() -> Dictionary:
	return {
		"screen_shake_intensity": screen_shake_intensity,
		"particle_density": particle_density,
		"color_grading_intensity": color_grading_intensity
	}
