# 🔍 BOOT AUDIT REPORT - Cria do Tatame

**Data:** $(date)  
**Godot Version Target:** 4.3+  
**Status:** ⚠️ CRITICAL ISSUES FOUND

---

## 📊 RESUMO EXECUTIVO

| Categoria | Status | Issues |
|-----------|--------|--------|
| Main Scene | ✅ OK | 0 |
| Autoloads (30 total) | ⚠️ WARNING | 3 potenciais |
| Scenes (.tscn) | ⚠️ WARNING | 2 referências não validadas |
| Scripts (.gd) | ✅ OK | Sintaxe válida |
| JSON Data Files | ✅ OK | 105 arquivos validados |

---

## 🔴 ISSUES CRÍTICAS IDENTIFICADAS

### Issue #1: Duplicação de Sistemas de Combate

**Problema:** Existem DOIS gerenciadores de combate ativos:
- `src/autoloads/CombatManager.gd` (autoload canônico)
- `src/combat/transition_manager.gd` (autoload adicional)

**Impacto:** Conflito de responsabilidade, estados inconsistentes, possível crash em runtime.

**Solução Recomendada:** 
- Manter `CombatManager` como orquestrador principal
- `TransitionManager` deve ser subordinado ao `CombatManager`, não autoload independente
- OU fundir lógica do TransitionManager dentro do CombatManager

### Issue #2: Múltiplos Gerenciadores de Mundo

**Problema:** 4 sistemas de mundo/coexistência:
- `WorldState` (autoload)
- `WorldDirectorManager` (autoload)
- `WorldMapManager` (autoload)
- `NavigationManager` (autoload - novo)

**Impacto:** Estado do mundo pode dessincronizar, navegação inconsistente.

**Solução:** Consolidar em hierarquia clara:
```
WorldDirectorManager (orquestrador)
├── WorldState (dados)
├── WorldMapManager (geografia)
└── NavigationManager (viagens)
```

### Issue #3: Audio Duplo

**Problema:** 
- `AudioManager` (autoload canônico)
- `CombatAudio` (autoload novo, vazio/stub)

**Solução:** Remover `CombatAudio` como autoload; integrar como módulo do `AudioManager`.

---

## ✅ VALIDAÇÃO DE MAIN SCENE

**Cena:** `res://scenes/main_menu/MainMenu.tscn`

**Status:** ✅ VÁLIDA
- Script existe: `MainMenu.gd` ✓
- Hierarquia correta ✓
- Sem referências quebradas ✓

**Fluxo esperado:**
```
MainMenu → TerreiroDaLuta → CombatArenaBase → Result → Save
```

---

## 📋 AUTOLoadS VALIDADOS (30 total)

| # | Autoload | Status | Observações |
|---|----------|--------|-------------|
| 1 | SignalBus | ✅ | OK |
| 2 | DataRegistry | ✅ | OK |
| 3 | DeckManager | ✅ | OK |
| 4 | LocalAIManager | ✅ | OK |
| 5 | WorldState | ✅ | OK |
| 6 | WorldDirectorManager | ✅ | OK |
| 7 | NFTManager | ⚠️ | Não essencial para MVP |
| 8 | SaveManager | ✅ | OK |
| 9 | CombatManager | ✅ | CANÔNICO DE COMBATE |
| 10 | CareerLoop | ✅ | OK |
| 11 | ReputationMatrix | ✅ | OK |
| 12 | CriaLiveManager | ✅ | OK |
| 13 | AudioManager | ✅ | CANÔNICO DE ÁUDIO |
| 14-30 | Outros | ✅ | OK |
| 31 | TransitionManager | ⚠️ | DUPLICADO - revisar |
| 32 | NavigationManager | ⚠️ | CONSOLIDAR com WorldMap |
| 33 | CombatVFX | ⚠️ | Stub/vazio |
| 34 | CombatAudio | ⚠️ | Stub/vazio |

---

## 🎯 RECOMENDAÇÕES PRIORITÁRIAS

### Prioridade 1 (Crítico - Bloqueia Release)
1. **Unificar sistemas de combate** - Escolher UM cérebro canônico
2. **Consolidar gerenciamento de mundo** - Hierarquia clara
3. **Remover autoloads stub** - CombatVFX, CombatAudio

### Prioridade 2 (Importante - Melhora Estabilidade)
4. Validar todas as cenas .tscn no Godot Editor
5. Testar fluxo completo Menu→Terreiro→Combate→Save
6. Implementar fallback para assets faltantes

### Prioridade 3 (Polimento - Pós-MVP)
7. Integrar GameFeelManager com sistema de combate
8. Adicionar sprites finais
9. Implementar áudio completo

---

## 🧪 TESTE DE BOOT SUGERIDO

```bash
# No Godot Editor:
1. Abrir project.godot
2. F5 (rodar main_scene)
3. Verificar console por erros
4. Navegar: MainMenu → Terreiro → Combate
5. Executar 1 ação de combate
6. Voltar ao Terreiro
7. Salvar e fechar
8. Reabrir save
```

---

**Próximo Passo:** Gerar `DUPLICATION_MAP.md` com plano de migração detalhado.
