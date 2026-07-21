extends CanvasLayer
class_name CombatHUD

# Interface de Combate Mobile-First
# Integração das barras de Stamina, Gás, Grip e indicadores de direção de defesa

signal ui_input_defense(direction: int)
signal ui_input_feint(feint_type: String)
signal ui_card_played(card_index: int)

# Referências de nós UI
@onready var stamina_bar: ProgressBar = $StaminaContainer/StaminaBar
@onready var gas_bar: ProgressBar = $GasContainer/GasBar
@onready var grip_bar: ProgressBar = $GripContainer/GripBar
@onready var defense_indicator: Control = $DefenseIndicator
@onready var card_hand_container: HBoxContainer = $CardHandContainer
@onready var timing_prompt: Label = $TimingPrompt
@onready var read_level_label: Label = $ReadLevelLabel

# Estado atual
var current_stamina: float = 100.0
var max_stamina: float = 100.0
var current_gas: float = 100.0
var max_gas: float = 100.0
var current_grip: float = 100.0
var max_grip: float = 100.0

var is_defense_window_open: bool = false
var defense_direction_options: Array[int] = [0, 1, 2, 3]  # UP, DOWN, LEFT, RIGHT

# Cores temáticas
const COLOR_STAMINA = Color(0.2, 0.6, 0.9)  # Ciano
const COLOR_GAS = Color(1.0, 0.58, 0.05)    # Âmbar
const COLOR_GRIP = Color(0.8, 0.8, 0.8)     # Branco acinzentado
const COLOR_CRITICAL = Color(1.0, 0.2, 0.2) # Vermelho

func _ready() -> void:
	_setup_ui_colors()
	_connect_signals()
	hide_defense_indicator()

func _setup_ui_colors() -> void:
	if stamina_bar:
		stamina_bar.get_node("Bar").modulate = COLOR_STAMINA
	if gas_bar:
		gas_bar.get_node("Bar").modulate = COLOR_GAS
	if grip_bar:
		grip_bar.get_node("Bar").modulate = COLOR_GRIP

func _connect_signals() -> void:
	# Conecta aos sinais dos managers (serão conectados no runtime)
	pass

# ==================== RESOURCE BARS ====================

func update_stamina(value: float, max_value: float) -> void:
	current_stamina = value
	max_stamina = max_value
	if stamina_bar:
		stamina_bar.max_value = max_stamina
		stamina_bar.value = current_stamina
		_update_bar_color(stamina_bar, current_stamina / max_stamina)

func update_gas(value: float, max_value: float) -> void:
	current_gas = value
	max_gas = max_value
	if gas_bar:
		gas_bar.max_value = max_gas
		gas_bar.value = current_gas
		_update_bar_color(gas_bar, current_gas / max_gas)

func update_grip(value: float, max_value: float) -> void:
	current_grip = value
	max_grip = max_value
	if grip_bar:
		grip_bar.max_value = max_grip
		grip_bar.value = current_grip
		_update_bar_color(grip_bar, current_grip / max_grip)

func _update_bar_color(bar: ProgressBar, ratio: float) -> void:
	if ratio <= 0.2:
		bar.get_node("Bar").modulate = COLOR_CRITICAL
	else:
		match bar.name:
			"StaminaBar":
				bar.get_node("Bar").modulate = COLOR_STAMINA
			"GasBar":
				bar.get_node("Bar").modulate = COLOR_GAS
			"GripBar":
				bar.get_node("Bar").modulate = COLOR_GRIP

# ==================== DEFENSE INDICATOR ====================

func show_defense_indicator(directions: Array[int], window_duration: float) -> void:
	is_defense_window_open = true
	defense_direction_options = directions
	
	if defense_indicator:
		defense_indicator.visible = true
		_highlight_defense_directions(directions)
		
		# Timer visual da janela
		var tween = create_tween()
		tween.tween_property(defense_indicator, "modulate:a", 0.3, window_duration)

func hide_defense_indicator() -> void:
	is_defense_window_open = false
	if defense_indicator:
		defense_indicator.visible = false
		defense_indicator.modulate.a = 1.0

func _highlight_defense_directions(directions: Array[int]) -> void:
	# Implementação específica depende da estrutura do nó DefenseIndicator
	# Cada direção (UP, DOWN, LEFT, RIGHT) deve ser destacada visualmente
	pass

func input_defense_direction(direction: int) -> void:
	if not is_defense_window_open:
		return
	
	ui_input_defense.emit(direction)
	hide_defense_indicator()

# ==================== TIMING PROMPT ====================

func show_timing_feedback(timing_quality: String) -> void:
	if not timing_prompt:
		return
	
	match timing_quality:
		"perfect":
			timing_prompt.text = "PERFEITO!"
			timing_prompt.add_theme_color_override("font_color", Color(0.2, 1.0, 0.5))
		"good":
			timing_prompt.text = "BOM"
			timing_prompt.add_theme_color_override("font_color", Color(0.8, 1.0, 0.2))
		"late":
			timing_prompt.text = "ATRASADO"
			timing_prompt.add_theme_color_override("font_color", Color(1.0, 0.6, 0.2))
		_:
			timing_prompt.text = ""
	
	# Fade out após 1s
	await get_tree().create_timer(1.0).timeout
	timing_prompt.text = ""

# ==================== READ LEVEL DISPLAY ====================

func update_read_level(level: int, accuracy: float) -> void:
	if not read_level_label:
		return
	
	var level_text: String = ""
	match level:
		0: level_text = "SEM LEITURA"
		1: level_text = "LEITURA BÁSICA"
		2: level_text = "LEITURA INTERM."
		3: level_text = "LEITURA AVANÇADA"
	
	read_level_label.text = "%s (%.0f%%)" % [level_text, accuracy * 100]
	
	# Cor baseada no nível
	var color: Color
	match level:
		0: color = Color(0.6, 0.6, 0.6)
		1: color = Color(0.2, 0.6, 0.9)
		2: color = Color(1.0, 0.8, 0.2)
		3: color = Color(1.0, 0.4, 0.8)
	
	read_level_label.add_theme_color_override("font_color", color)

# ==================== CARD HAND ====================

func update_card_hand(cards: Array[Dictionary]) -> void:
	if not card_hand_container:
		return
	
	# Limpa mão atual
	for child in card_hand_container.get_children():
		child.queue_free()
	
	# Adiciona cartas
	for i in range(min(cards.size(), 5)):  # Máximo 5 cartas na mão
		var card_data = cards[i]
		var card_button = _create_card_button(card_data, i)
		card_hand_container.add_child(card_button)

func _create_card_button(card_data: Dictionary, index: int) -> Button:
	var btn = Button.new()
	btn.text = str(card_data.get("name", "Carta"))
	btn.custom_minimum_size = Vector2(120, 80)
	
	# Tooltip com detalhes
	var tooltip: String = "Nível: %d\nCusto Gás: %d\nEstado: %s" % [
		card_data.get("level", 1),
		card_data.get("activation_cost", {}).get("gas", 0),
		", ".join(card_data.get("valid_states", ["Qualquer"]))
	]
	btn.tooltip_text = tooltip
	
	btn.pressed.connect(_on_card_pressed.bind(index))
	
	# Desabilita se não tiver recursos
	var gas_cost = int(card_data.get("activation_cost", {}).get("gas", 0))
	if gas_cost > current_gas:
		btn.disabled = true
		btn.modulate.a = 0.5
	
	return btn

func _on_card_pressed(index: int) -> void:
	ui_card_played.emit(index)

# ==================== COMBAT FEEDBACK ====================

func show_transition_feedback(success: bool, result_type: String) -> void:
	# Feedback visual de sucesso/falha da transição
	var feedback_label = Label.new()
	feedback_label.text = "SUCESSO!" if success else "DEFENDIDO"
	feedback_label.add_theme_color_override("font_color", Color.GREEN if success else Color.RED)
	feedback_label.position = Vector2(400, 200)
	add_child(feedback_label)
	
	var tween = create_tween()
	tween.tween_property(feedback_label, "position:y", 150, 0.5)
	tween.tween_property(feedback_label, "modulate:a", 0.0, 0.3)
	tween.tween_callback(feedback_label.queue_free)

func show_gas_spent(amount: float) -> void:
	# Feedback visual de gasto de gás
	var gas_label = Label.new()
	gas_label.text = "-%.0f GÁS" % amount
	gas_label.add_theme_color_override("font_color", COLOR_GAS)
	gas_label.position = Vector2(400, 250)
	add_child(gas_label)
	
	var tween = create_tween()
	tween.tween_property(gas_label, "position:y", 220, 0.4)
	tween.tween_property(gas_label, "modulate:a", 0.0, 0.3)
	tween.tween_callback(gas_label.queue_free)

# ==================== MOBILE INPUT HELPERS ====================

func _input(event: InputEvent) -> void:
	if event is InputEventScreenTouch and event.pressed:
		_handle_touch_input(event.position)
	elif event is InputEventMouseButton and event.pressed:
		_handle_mouse_input(event.position)

func _handle_touch_input(position: Vector2) -> void:
	if is_defense_window_open:
		# Determina direção baseada na posição do toque
		var direction = _get_direction_from_position(position)
		input_defense_direction(direction)

func _handle_mouse_input(position: Vector2) -> void:
	if is_defense_window_open:
		var direction = _get_direction_from_position(position)
		input_defense_direction(direction)

func _get_direction_from_position(position: Vector2) -> int:
	# Centro da tela como referência
	var center = get_viewport_rect().size / 2.0
	var diff = position - center
	
	# Determina direção predominante
	if abs(diff.x) > abs(diff.y):
		return BJJEnums.DefenseDirection.RIGHT if diff.x > 0 else BJJEnums.DefenseDirection.LEFT
	else:
		return BJJEnums.DefenseDirection.DOWN if diff.y > 0 else BJJEnums.DefenseDirection.UP

# ==================== STATE SYNC ====================

func sync_with_fighter_condition(condition: Node) -> void:
	if not condition:
		return
	
	# Conecta aos sinais do FighterCondition
	if condition.has_signal("gas_changed"):
		condition.gas_changed.connect(_on_gas_changed)
	if condition.has_signal("grip_integrity_changed"):
		condition.grip_integrity_changed.connect(_on_grip_changed)

func _on_gas_changed(new_gas: float) -> void:
	update_gas(new_gas, max_gas)

func _on_grip_changed(new_grip: float) -> void:
	update_grip(new_grip, max_grip)

func reset() -> void:
	update_stamina(max_stamina, max_stamina)
	update_gas(max_gas, max_gas)
	update_grip(max_grip, max_grip)
	hide_defense_indicator()
	if timing_prompt:
		timing_prompt.text = ""
