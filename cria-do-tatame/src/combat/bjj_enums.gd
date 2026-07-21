extends RefCounted
class_name BJJEnums

# Estados de combate expandidos para Pressão & Fluxo
enum CombatPhase {
	DISTANCE,      # Distancia longa/neutra
	GRIP,          # Disputa de pegada
	CLINCH,        # Clinch neutro ou dominante
	TAKEDOWN,      # Entrada de queda em andamento
	GROUND,        # Chao (guarda, side, mount)
	TRANSITION,    # Transição entre posições
	TECHNICAL,     # Fase de finalização
	RESET          # Reset após ação
}

# Recursos do lutador (além de HP tradicional)
enum FighterResource {
	GAS,           # Energia explosiva para entradas e scrambles
	FOCUS,         # Timing e leitura técnica
	GRIP,          # Força/qualidade da pegada
	GUARD,         # Proteção defensiva no chão
	CONTROL,       # Domínio posicional
	MORAL          # Resistência mental/reputação
}

# Tipos de dano por membro (Fadiga Localizada)
enum LimbType {
	LEFT_ARM,
	RIGHT_ARM,
	LEFT_LEG,
	RIGHT_LEG,
	CORE             # Tronco/postura
}

# Estados de Grip/Pegada
enum GripState {
	NEUTRAL,         # Sem pegada estabelecida
	BREAKING,        # Tentando quebrar pegada
	ESTABLISHED,     # Pegada firme
	DOMINANT,        # Pegada vantajosa
	BROKEN           # Pegada quebrada recentemente
}

# Direções de defesa (para input mobile)
enum DefenseDirection {
	UP,              # Defesa alta (pescoço/cabeça)
	DOWN,            # Defesa baixa (quadril/pernas)
	LEFT,            # Defesa lateral esquerda
	RIGHT,           # Defesa lateral direita
	CENTER           # Defesa central/postura
}

# Tipos de transição
enum TransitionType {
	SMOOTH,          # Transição fluida sem gasto extra
	EXPLOSIVE,       # Gasta gás extra, mais rápida
	TECHNICAL,       # Gasta foco, maior precisão
	DESPERATE        # Baixo gás, risco alto
}

# Resultado de clash de técnicas
enum ClashResult {
	DOMINATION,      # >15 diferença: domínio técnico (+0.25)
	ADVANTAGE,       # 5-15 diferença: vantagem (+0.12)
	DISPUTED,        # 0-4.99: disputa (+0.03)
	COUNTER_WINDOW   # <0: janela de contra (-0.18)
}

# Categorias de técnicas (alinhado com techniques.json)
enum TechniqueCategory {
	PEGADA,          # Grip fighting
	QUEDA,           # Takedowns
	DEFESA,          # Defesas/contras
	RASPAGEM,        # Sweeps
	CONTROLE,        # Posições dominantes
	FINALIZACAO,     # Submissions
	PASSAGEM,        # Guard passes
	TRANSICAO        # Movimentos de transição
}
