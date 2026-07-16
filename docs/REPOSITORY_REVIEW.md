# Revisão de repositórios relevantes

## Decisão executiva

| Repositório | Papel | Decisão |
|---|---|---|
| `google-ai-edge/mediapipe` | Pose local no MVP | **Núcleo opcional de visão** |
| `roboflow/supervision` | Contratos visuais, zonas, anotação e utilitários | **Adicionar por adaptador** |
| `roboflow/trackers` | Tracking multiobjeto | **Adicionar na fase multi-pessoa** |
| `open-mmlab/mmpose` | Pose multi-pessoa e modelos RTMPose/RTMO | **Backend avançado de validação** |
| `neuropsychology/NeuroKit` | Processamento PPG/HRV | **Extensão fisiológica oficial** |
| `sqlcipher/sqlcipher` | Banco local criptografado | **Obrigatório para dados reais** |
| `fastapi/fastapi` | API local tipada | **Núcleo de serviço** |
| `pydantic/pydantic` | Contratos e validação | **Núcleo obrigatório** |
| `huggingface/smolagents` | Coordenação pós-sessão | **Opcional; não usar em tempo real** |
| `Qwen/Qwen3.5-4B` | Síntese local do relatório | **Opcional e sempre revisado** |
| `ruvnet/RuView` | WiFi-CSI | **Laboratório experimental isolado** |

## 1. MediaPipe

**Uso:** pose em uma pessoa, execução local, baixo custo computacional.

**Pontos fortes:** APIs on-device, implantação multiplataforma e modelo de Tasks adequado para protótipo.

**Riscos:** telemetria de uso deve ser considerada na governança; sobreposição corporal do BJJ reduz a confiabilidade; o modelo precisa ser externo e versionado.

**Implementação:** `vision/mediapipe_pose.py` atrás da interface `PoseBackend`.

## 2. Roboflow Supervision

**Uso:** converter resultados de modelos, desenhar keypoints, definir zonas, organizar vídeo e métricas.

**Pontos fortes:** model-agnostic, `Detections`, `KeyPoints`, `PolygonZone`, anotadores e sinks.

**Riscos:** não é detector, não criptografa dados e não resolve identidade clínica. A classe `sv.ByteTrack` está em processo de remoção; usar o repositório `roboflow/trackers`.

**Implementação:** dependência versionada e adaptadores; não copiar código-fonte para o monorepo.

## 3. Roboflow Trackers

**Uso:** tracking temporário de pessoas em cenas multiobjeto.

**Riscos:** IDs podem trocar em oclusões; `tracker_id` nunca deve ser tratado como identidade do participante.

**Implementação:** mapear `tracker_id` para um código pseudônimo confirmado pelo operador.

## 4. MMPose

**Uso:** comparação com MediaPipe, pose multi-pessoa, RTMPose/RTMO e experimentos 3D.

**Pontos fortes:** amplo model zoo, modelos em tempo real, datasets e ferramentas de avaliação.

**Riscos:** stack PyTorch/MMEngine mais pesada; versão e compatibilidade precisam ser congeladas em imagem Docker própria.

**Implementação:** serviço GPU separado, nunca requisito para iniciar uma sessão.

## 5. NeuroKit2

**Uso:** limpeza de PPG, detecção de picos e HRV em janelas controladas.

**Riscos:** PPG durante grappling contém artefato intenso. HRV durante luta é exploratória; o painel principal usa apenas métricas com qualidade suficiente.

**Implementação:** `physiology/hrv.py`, com falha explícita quando a qualidade é insuficiente.

## 6. SQLCipher

**Uso:** criptografia do banco local.

**Regra:** SQLite comum é permitido somente para dados sintéticos. O código bloqueia participantes reais sem driver SQLCipher e chave externa.

## 7. FastAPI e Pydantic

**Uso:** contratos, validação, endpoints locais e documentação da API.

**Decisão:** entram no core porque reduzem ambiguidades entre processos e facilitam testes.

## 8. smolagents e Qwen

**Uso:** análise pós-sessão e redação opcional.

**Proibição:** nenhum LLM controla câmera, decide interrupção, calcula ângulos ou cria números.

**Entrada permitida:** JSON validado, pseudonimizado e agregado.

## 9. RuView

**Uso:** presença e movimento por WiFi-CSI como sensor redundante durante oclusões.

**Riscos principais:** dependência do ambiente, necessidade de calibração local, possível assinatura biométrica, maturidade clínica insuficiente e dificuldade multi-pessoa.

**Decisão:** serviço experimental separado. Falha do RuView nunca invalida nem interrompe o núcleo NeuroJitsu.
