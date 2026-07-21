# 🥋 CRIA DO TATAME - INTEGRAÇÃO PRESSÃO & FLUXO (FASE 1)

## ✅ ARQUIVOS CRIADOS/ATUALIZADOS

### Etapa 1: Resources e Enums Base

| Arquivo | Caminho | Descrição |
|---------|---------|-----------|
| `bjj_enums.gd` | `src/combat/bjj_enums.gd` | Enums unificados: CombatPhase, LimbType, GripState, DefenseDirection, TransitionType, ClashResult, TechniqueCategory |
| `deck_card.gd` | `src/combat/deck_card.gd` | Resource DeckCard com propriedades de técnica, custo, efeitos e validação |

### Etapa 2: Núcleo do Combate (Pressão & Fluxo)

| Arquivo | Caminho | Descrição |
|---------|---------|-----------|
| `fighter_condition.gd` | `src/combat/fighter_condition.gd` | Sistema de Gás, Fadiga Localizada por membro, Dano por membro, Grip Integrity |
| `grip_state.gd` | `src/combat/grip_state.gd` | Gerenciamento de pegadas (collar, sleeve, pant), postura, quebras de grip |
| `transition_manager.gd` | `src/combat/transition_manager.gd` | **AUTOLOAD** - Orquestra janelas de defesa, fintas, read_level, integra cartas do Deck |
| `submission_sequence.gd` | `src/combat/submission_sequence.gd` | Máquina de estados para finalizações multi-estágio (Setup → Isolate → Lock → Finish) |

### Etapa 3: Lore Cultural e Homenagem

| Arquivo | Caminho | Descrição |
|---------|---------|-----------|
| `tekuro_nishiuchi.json` | `data/npcs/tekuro_nishiuchi.json` | NPC sábio, bisavô simbólico. Diálogo chave: "A raiz que se aprofunda não cai com o vento..." |
| `legacy_perk.gd` | `src/combat/perks/legacy_perk.gd` | Resource do Perk "Legado de Tekuro": +10% resistência à fadiga de Grip |
| `cha_cravo_colonia.tres` | `data/items/cha_cravo_colonia.tres` | Item consumível: Restaura 15 de Gás fora de combate. Lore: receita de 1953 |

### Etapa 4: Mapa e Navegação (Hubs)

| Arquivo | Caminho | Descrição |
|---------|---------|-----------|
| `world_map.gd` | `src/world/world_map.gd` | Lógica dos 4 hubs: Terreiro, Arena do Dique, Manguezal, Zambiapunga |
| `navigation_manager.gd` | `src/world/navigation_manager.gd` | **AUTOLOAD** - Gerencia viagem, custo de tempo/stamina, desbloqueio de hubs |

### Etapa 5: Atualizações de Configuração

| Arquivo | Alteração |
|---------|-----------|
| `project.godot` | Adicionado autoload `TransitionManager`. Comentários para NavigationManager, CombatVFX, CombatAudio (Fase 2) |
| `production_manifest_v02.json` | Adicionados assets_needed: `statue_jizo` (homenagem Tekuro) e `cha_cravo_icon` |

---

## 🔌 INTEGRAÇÃO COM SISTEMAS EXISTENTES

### Conexão com DeckManager

O `TransitionManager` consome cartas do `DeckManager` existente:

```gdscript
# Exemplo de uso no CombatManager
func execute_technique_with_card(card_index: int):
    var result = TransitionManager.play_card_from_hand(card_index, player_id)
    if result.ok:
        # Transição iniciada, aguarda input de defesa
        pass
```

### Conexão com CombatManager

Adicione ao `CombatManager.gd` existente:

```gdscript
# No _ready() ou após _ensure_runtime_components():
func _setup_pressure_flow_systems() -> void:
    # Instancia FighterCondition para cada lutador
    for fighter_id in fighters.keys():
        var condition = FighterCondition.new()
        condition.name = "FighterCondition_%s" % fighter_id
        condition.initialize(fighter_id, fighters[fighter_id])
        add_child(condition)
        fighters[fighter_id]["condition"] = condition
    
    # Instancia GripState para cada lutador
    for fighter_id in fighters.keys():
        var grip = GripState.new()
        grip.name = "GripState_%s" % fighter_id
        grip.initialize(fighter_id, fighters[fighter_id])
        add_child(grip)
        fighters[fighter_id]["grip"] = grip
```

### Sinais para UI (Fase 2)

Os sistemas emitem sinais para integração com HUD:

```gdscript
# FighterCondition
signal gas_changed(new_gas: float)
signal fatigue_changed(limb: BJJEnums.LimbType, new_fatigue: float)
signal grip_integrity_changed(new_value: float)

# TransitionManager
signal defense_window_opened(direction: int, timing: float)
signal transition_completed(success: bool, result_type: String)

# SubmissionSequence
signal submission_threat_updated(threat_level: float)
signal tap_imminent(is_imminent: bool)
```

---

## ⚙️ REGRAS DE INTEGRAÇÃO RESPEITADAS

1. ✅ **Deck de Combate**: `TransitionManager` usa `DeckManager.get_hand()` e `consume_used_card()`
2. ✅ **AI Lore Guardian**: 
   - NPC Tekuro alinhado ao canon (América Maru, 1953, BJJ real)
   - Nenhuma técnica inventada - todas referenciam `techniques.json`
   - Ruan "Macacão", Ituberá, Baixo Sul preservados
3. ✅ **Production Manifest**: Assets solicitados comentados em `production_manifest_v02.json`
4. ✅ **Autoloads**: `TransitionManager` registrado no `project.godot`

---

## 🛡️ CONTENÇÃO DE ESCOPO APLICADA

- ❌ SEM mini-games de agricultura/pesca/caminhada
- ❌ SEM textos expositivos longos (diálogos de 1-2 frases)
- ✅ FOCO ABSOLUTO: Combate de Jiu-Jitsu mais estratégico e imersivo
- ✅ Navegação por menu de Hub com transição rápida (1s)

---

## 🚀 PRÓXIMOS PASSOS (FASE 2 - UI/Game Feel)

1. Criar `combat_hud.gd` em `src/ui/` com barras de Stamina, Gás, Grip
2. Criar `combat_vfx_manager.gd` em `src/vfx/` (screen shake, partículas)
3. Criar `combat_audio_manager.gd` em `src/audio/` (respiração, pano, impactos)
4. Registrar novos autoloads no `project.godot`
5. Integrar indicadores de direção de defesa (UI mobile-first)

---

## 📝 VALIDAÇÃO

Execute para validar JSONs:

```bash
python tools/validate_json.py data/npcs/tekuro_nishiuchi.json
python tools/validate_lore_output.py data/items/cha_cravo_colonia.tres
```

Teste os sistemas no Godot:

```gdscript
# Debug commands no console
TransitionManager.execute_feint("level_change", "ruan_macacao")
NavigationManager.travel_to("arena_dique")
```

---

**Status**: ✅ Fase 1 Completa - Aguardando revisão para Fase 2 (UI/Game Feel)
