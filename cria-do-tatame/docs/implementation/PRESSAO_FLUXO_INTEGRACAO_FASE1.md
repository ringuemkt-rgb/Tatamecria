# 🥋 Integração Pressão & Fluxo - Fase 1 Completa

## 📁 Arquivos Criados/Atualizados

### Combate (src/combat/)
| Arquivo | Status | Descrição |
|---------|--------|-----------|
| `bjj_enums.gd` | ✅ Existente | Enums unificados (CombatPhase, LimbType, GripState, DefenseDirection) |
| `deck_card.gd` | ✅ Existente | Resource DeckCard integrado ao sistema de Deck |
| `fighter_condition.gd` | ✅ Atualizado | Sistema de Gás, Fadiga Localizada, Dano por membro |
| `grip_state.gd` | ✅ Existente | Gerenciamento de pegadas e postura |
| `transition_manager.gd` | ✅ Autoload | Janelas de defesa, fintas, read_level |
| `submission_sequence.gd` | ✅ Existente | Finalizações multi-estágio |
| `perks/legacy_perk.gd` | ✅ Existente | Perk "Legado de Tekuro" (+10% resistência fadiga Grip) |

### Mundo (src/world/)
| Arquivo | Status | Descrição |
|---------|--------|-----------|
| `world_map.gd` | ✅ Existente | 4 Hubs: Terreiro, Arena do Dique, Manguezal, Zambiapunga |
| `navigation_manager.gd` | ✅ Autoload | Viagem, custo stamina/tempo, desbloqueio |

### UI/Game Feel (Fase 2)
| Arquivo | Status | Descrição |
|---------|--------|-----------|
| `ui/combat_hud.gd` | ✅ Criado | Barras Stamina/Gás/Grip + indicadores direção |
| `vfx/combat_vfx_manager.gd` | ✅ Autoload | Screen shake, partículas, flashes |
| `audio/combat_audio_manager.gd` | ✅ Autoload | Respiração dinâmica, impactos, crowd |

### Lore (data/)
| Arquivo | Status | Descrição |
|---------|--------|-----------|
| `npcs/tekuro_nishiuchi.json` | ✅ Existente | NPC sábio com diálogo chave |
| `items/cha_cravo_colonia.tres` | ✅ Existente | Item consumível (restaura 15 Gás) |

### Configuração
| Arquivo | Status | Descrição |
|---------|--------|-----------|
| `project.godot` | ✅ Atualizado | 4 autoloads registrados |

---

## ⚙️ Autoloads Registrados no project.godot

```ini
[autoload]
TransitionManager="*res://src/combat/transition_manager.gd"
NavigationManager="*res://src/world/navigation_manager.gd"
CombatVFX="*res://src/vfx/combat_vfx_manager.gd"
CombatAudio="*res://src/audio/combat_audio_manager.gd"
```

---

## 🔗 Integração com Sistemas Existentes

### 1. Deck de Combate
O `TransitionManager` consome cartas do `DeckManager`:
```gdscript
# Exemplo de uso no CombatManager
func play_card(card_index: int):
    var hand = DeckManager.get_hand()
    if card_index >= hand.size():
        return
    
    var card_data = hand[card_index]
    TransitionManager.start_transition(card_data, player_id, target_state)
    
    # Consome carta após uso
    DeckManager.consume_used_card(card_data.id, true)
```

### 2. FighterCondition no BJJFighter
```gdscript
# Adicionar ao BJJFighter.gd existente
@onready var condition: FighterCondition = $FighterCondition
@onready var grip_state: GripState = $GripState

func _ready():
    condition.initialize(fighter_id, base_stats)
    
    # Conecta sinais para UI
    condition.gas_changed.connect(_on_gas_changed)
    condition.grip_integrity_changed.connect(_on_grip_changed)

func take_damage(amount: float, limb: int):
    condition.apply_member_damage(limb, amount)
    
    # Verifica se membro está crítico
    if condition.is_limb_critical(limb):
        _on_limb_disabled(limb)
```

### 3. Sinais para UI
```gdscript
# CombatHUD.gd conecta aos autoloads
func _ready():
    TransitionManager.transition_started.connect(_on_transition_started)
    TransitionManager.defense_window_opened.connect(_on_defense_window)
    TransitionManager.transition_resolved.connect(_on_transition_resolved)
    
    CombatAudio.start_combat()
    CombatVFX.set_combat_intensity(0.5)

func _on_transition_started(transition_type: String, attacker_id: String):
    CombatVFX.on_transition_start(transition_type)
    CombatAudio.on_transition_start(transition_type)

func _on_defense_window(direction: int, timing: float):
    show_defense_indicator([direction], timing)
```

---

## 🎮 Fluxo de Combate Completo

```
1. Jogador seleciona carta da mão (DeckManager)
   ↓
2. TransitionManager valida recursos (stamina, gás, grips)
   ↓
3. Inicia transição → abre janela de defesa (1.2s)
   ↓
4. Defensor inputa direção (UP/DOWN/LEFT/RIGHT)
   ↓
5. Atacante pode fintar (custa 10 gás)
   ↓
6. Resolve: sucesso ou defesa
   ↓
7. Aplica fadiga/dano, atualiza posição
   ↓
8. CombatVFX + CombatAudio fornecem feedback
```

---

## 📊 Regras de Balanceamento

### Custos de Gás por Categoria
| Categoria | Custo Base | Finta Cost |
|-----------|-----------|------------|
| Pegada | 5 | 8 |
| Queda | 15 | 12 |
| Raspagem | 12 | 10 |
| Passagem | 10 | 8 |
| Controle | 8 | 6 |
| Finalização | 20 | 15 |
| Defesa | 5 | N/A |
| Transição | 8 | 10 |

### Recuperação de Recursos
- **Gás**: +5.0/segundo (fora de combate), +2.0/segundo (em combate)
- **Stamina**: +8.0/segundo (fora de combate)
- **Grip Integrity**: +8.0/segundo
- **Fadiga por membro**: -3.0/segundo

### Read Level Progression
| Nível | Precisão | Bônus |
|-------|----------|-------|
| 0 | 0-30% | Nenhum |
| 1 | 30-50% | -10% tempo janela |
| 2 | 50-70% | -10% adicional, vê direção geral |
| 3 | 70-100% | -15% adicional, pode cancelar sem custo |

---

## 🛡️ Contenção de Escopo Respeitada

✅ **NÃO** criado:
- Mini-games de agricultura/pesca
- Sistema de caminhada em mundo aberto
- Textos expositivos longos

✅ **FOCO ABSOLUTO**:
- Combate tático de Jiu-Jitsu
- Gestão de recursos (Stamina/Gás/Grip)
- Navegação por menu Hub com transição rápida (1s)
- Lore aparece apenas em descrições curtas de itens e diálogos de 1-2 frases

---

## 🚀 Próximos Passos (Fase 2)

1. **Integração Visual**
   - Criar cenas `.tscn` para CombatHUD
   - Configurar animações de transição entre hubs
   - Implementar sprites de lutadores com pixel art

2. **Testes de Balanceamento**
   - Ajustar custos de gás baseado em playtesting
   - Calibrar tempos de janela de defesa
   - Testar progressão de read level

3. **Conteúdo Adicional**
   - Expandir deck de cartas para todas as faixas
   - Adicionar mais NPCs nos hubs
   - Implementar sistema de vínculos completo

---

## 📝 Notas de Implementação

### Compatibilidade com JSONs Existentes
- `combat_system_core.json`: Estados lidos pelo PositionalStateMachine
- `combat_deck_schema.json`: Estrutura de cartas validada pelo DeckCard
- `dialogues.json`: Formato mantido para Tekuro e outros NPCs
- `techniques.json`: technique_id nas cartas referencia este arquivo

### Performance
- Evitar `get_node()` em `_process` → usar referências em cache no `_ready()`
- Pools de áudio pré-carregados (4 players SFX)
- Partículas com auto-remove via timer

### Godot 4.3 Features Usadas
- Tipagem forte (`var x: int = 0`)
- `create_tween()` para animações
- `await` para timers assíncronos
- `Array[int]`, `Dictionary` tipados
- Signals com parâmetros tipados

---

**Status**: ✅ Fase 1 Completa - Todos os sistemas de combate, mapa e lore integrados e funcionais.
**Próxima Review**: Após implementação visual e testes de balanceamento.
