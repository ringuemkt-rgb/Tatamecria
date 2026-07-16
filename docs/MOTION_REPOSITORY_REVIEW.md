# Revisão de repositórios para análise motora

## Decisão executiva

O NeuroJitsu adota uma arquitetura modular. Nenhuma biblioteca externa controla sozinha a avaliação. Modelos de percepção geram pontos e probabilidades; módulos próprios calculam métricas transparentes; o agente de qualidade decide o que pode entrar no relatório.

## Matriz de adoção

| Repositório | Uso coerente | Decisão |
|---|---|---|
| `open-mmlab/mmpose` | RTMW/RTMO, corpo inteiro, mãos, pés, múltiplas pessoas | núcleo avançado, serviço isolado |
| `open-mmlab/mmaction2` | reconhecimento e localização temporal de ações por vídeo ou esqueleto | treinamento do modelo NeuroJitsu-BJJ |
| `perfanalytics/pose2sim` | calibração, sincronização, triangulação e cinemática 3D | referência offline preferida |
| `opensim-org/opensim-core` | modelos musculoesqueléticos, cinemática e simulação | núcleo biomecânico offline |
| `freemocap/freemocap` | captura 3D de referência com múltiplas câmeras | ferramenta laboratorial separada |
| `Walter0807/MotionBERT` | representação temporal, pose 3D e ações por esqueleto | encoder opcional |
| `shubham-goel/4D-Humans` | reconstrução e tracking de malha humana | benchmark experimental |
| `yohanshin/WHAM` | movimento humano 3D monocular em coordenadas globais | benchmark experimental |
| `TadasBaltrusaitis/OpenFace` | orientação da cabeça e direção geral do olhar | pesquisa opcional e separada |
| `deepinsight/insightface` | localização facial para redação visual, após licença dos pesos | não usar módulos de identificação |
| `ageitgey/face_recognition` | interface dlib simples | não adicionar ao produto |
| `cvat-ai/cvat` | anotação de caixas, keypoints, tracks e fases | ferramenta recomendada para dataset |

## Motivos para não usar identificação facial

O participante já possui código pseudônimo, confirmação humana e rastreamento temporário. Uma galeria facial não melhora ângulos, velocidade, postura, contato ou reconhecimento técnico. Ela adiciona dados biométricos, risco de reidentificação, dependência de thresholds e problemas com oclusão, iluminação e mudança de aparência.

Para anonimização, basta localizar a região facial e aplicar redação antes do restante do pipeline. Nenhum crop facial ou vetor biométrico deve ser persistido.

## Backends de pose

### Tempo real

- RTMW para corpo inteiro e detalhes de mãos e pés;
- RTMO para múltiplas pessoas;
- MediaPipe como fallback leve;
- Supervision/Trackers para eventos, zonas e IDs temporários.

### Referência 3D

- três ou quatro câmeras sincronizadas;
- Pose2Sim para triangulação e filtragem;
- OpenSim para cinemática e modelos musculoesqueléticos;
- FreeMoCap para comparação de captura e fluxo laboratorial.

### Temporal

- MMAction2 com PoseC3D, ST-GCN++ ou CTR-GCN;
- MotionBERT-Lite como encoder secundário;
- dataset próprio de grappling com divisão por participante e sessão.

## Sistemas experimentais

OpenCap Monocular, MonoMSK, WHAM e HMR2/4DHumans podem ser comparados em estudos adultos. Não são fonte principal de métricas até demonstrarem concordância com o sistema multicâmera nas tarefas NeuroJitsu.

## Regra de integração

Cada backend deve ser substituível e expor somente contratos versionados. O processo principal continua funcionando sem GPU, sem modelo de linguagem, sem WiFi-CSI e sem qualquer módulo biométrico.
