# NeuroJitsu Analytics

Plataforma local, modular e orientada à pesquisa para analisar sessões de Jiu-Jitsu Brasileiro adaptado por meio de métricas motoras, participação observável, fisiologia e qualidade dos dados.

> **Estado:** MVP de pesquisa executável. O software não é instrumento diagnóstico, não prevê crises, não substitui o profissional e não deve armazenar dados reais sem criptografia, consentimento e aprovação institucional.

## O que já funciona

- geração de sessões sintéticas reproduzíveis;
- contratos Pydantic para todas as trocas entre módulos;
- máquina de estados previsível;
- segmentação por fases da sessão;
- métricas transparentes de movimento, participação e HRV temporal;
- agente de qualidade que bloqueia resultados de baixa confiança;
- banco transacional com integridade SHA-256;
- modo SQLCipher opcional e obrigatório para participantes reais;
- agentes especializados de movimento, participação, qualidade e relatório;
- relatório individual JSON + HTML com limitações explícitas;
- API FastAPI local;
- dashboard Streamlit em modo escuro com botão de pausa sensorial;
- adaptador opcional para MediaPipe Tasks;
- barramento Roboflow Supervision para `Detections`, `KeyPoints`, zonas e metadados;
- eventos determinísticos de entrada, permanência e saída nas zonas;
- adaptador experimental RuView/WiFi-CSI;
- contratos whole-body para corpo, mãos, pés e pontos faciais;
- métricas de ângulo, amplitude, trajetória, suavidade, simetria e tronco;
- qualidade separada para corpo, mãos, pés, oclusão e frames perdidos;
- ontologia temporal de técnica com estabilização por histerese.

## Motion Intelligence v2

A camada avançada organiza a análise em três níveis:

```text
Tempo real: detector/pose → Supervision → Trackers → trajetórias 2D → qualidade → painel
Referência: câmeras sincronizadas → Pose2Sim → OpenSim → cinemática 3D
Temporal: sequências de esqueleto → MMAction2/MotionBERT → fases técnicas
```

As fases técnicas canônicas são:

```text
setup → entry → control → transition → completion → recovery
```

Backends pesados ficam em serviços opcionais. O núcleo continua executável sem GPU e sem depender de um único modelo externo.

## Instalação rápida

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -e ".[dev,api,dashboard]"
```

## Executar o fluxo seguro de demonstração

```bash
neurojitsu verify
neurojitsu demo --output outputs/demo
```

Arquivos gerados:

```text
outputs/demo/NJ-DEMO-001.json
outputs/demo/NJ-DEMO-001.html
outputs/demo/NJ-DEMO-001-agents.json
```

## API e dashboard

```bash
uvicorn neurojitsu.api.main:app --reload
streamlit run src/neurojitsu/dashboard/app.py
```

Ou:

```bash
docker compose up --build
```

- API: `http://localhost:8000`
- Dashboard: `http://localhost:8501`

## Instalação por capacidade

```bash
pip install -e ".[vision]"       # OpenCV, MediaPipe, Supervision
pip install -e ".[tracking]"     # trackers/ByteTrackTracker
pip install -e ".[physiology]"   # NeuroKit2
pip install -e ".[agents]"       # smolagents + Transformers
pip install -e ".[wifi]"         # RuView WebSocket/MQTT adapter
```

## Regra de segurança do banco

Sem `NEUROJITSU_DB_KEY`, o sistema aceita apenas participantes marcados como sintéticos. Ao tentar registrar uma pessoa real em SQLite comum, a aplicação encerra a operação com `PermissionError`.

```bash
export NEUROJITSU_DB_KEY="uma-chave-robusta-fornecida-pelo-cofre"
pip install -e ".[sqlcipher]"
```

A chave nunca deve ser salva no repositório.

## Pipeline de câmera

```text
Frame volátil
   ↓
localização facial para redação visual
   ↓
frame redigido
   ↓
detecção + pose whole-body
   ↓
Supervision Detections/KeyPoints + Trackers + zonas
   ↓
landmarks + eventos + qualidade + oclusão
   ↓
nenhum frame original persistido
```

O backend MediaPipe exige um modelo `.task` externo, controlado por `NEUROJITSU_POSE_MODEL_PATH`. O modelo deve ser baixado de fonte oficial, versionado e validado por checksum no ambiente de pesquisa.

## Arquitetura

Consulte:

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
- [`docs/MOTION_ANALYSIS_STACK.md`](docs/MOTION_ANALYSIS_STACK.md)
- [`docs/SUPERVISION_INTEGRATION.md`](docs/SUPERVISION_INTEGRATION.md)
- [`docs/MOTION_REPOSITORY_REVIEW.md`](docs/MOTION_REPOSITORY_REVIEW.md)
- [`docs/REPOSITORY_REVIEW.md`](docs/REPOSITORY_REVIEW.md)
- [`docs/DATA_GOVERNANCE.md`](docs/DATA_GOVERNANCE.md)
- [`docs/VALIDATION_PLAN.md`](docs/VALIDATION_PLAN.md)
- [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md)

## Testes

```bash
pytest
ruff check src tests
mypy src/neurojitsu
```

## Licença

MIT para o código próprio. Pesos de modelos, datasets e dependências conservam suas próprias licenças. Modelos experimentais ou pesos com restrições não devem ser redistribuídos automaticamente com o NeuroJitsu.
