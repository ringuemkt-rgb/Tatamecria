# NeuroJitsu Motion Intelligence v2

## Objetivo

Construir uma avaliação motora profissional de sessões de Jiu-Jitsu adaptado sem prometer precisão clínica antes da validação. O sistema separa mensuração, reconstrução, reconhecimento temporal, biomecânica e redação do relatório.

## Arquitetura em camadas

```text
Câmeras sincronizadas
        ↓
Detecção de pessoas + tracking temporário
        ↓
RTMW/RTMO: corpo, mãos, face e pés
        ↓
Controle de oclusão, frames perdidos e identidade operacional
        ↓
Trajetórias 2D por participante
        ├── análise em tempo real
        └── triangulação multicâmera
                    ↓
              Pose2Sim 3D
                    ↓
                OpenSim
                    ↓
ângulos, amplitudes, velocidades, estabilidade e métricas bilaterais
        ↓
MMAction2 / modelo temporal NeuroJitsu
        ↓
setup → entry → control → transition → completion → recovery
        ↓
relatório estruturado com confiança e limitações
```

## Núcleo recomendado

### RTMW e RTMO por MMPose

Uso principal para localizar corpo inteiro, mãos, pés e pontos faciais. O adaptador deve rodar como processo ou serviço isolado e retornar o contrato `PersonWholeBodyPose`. A imagem original não atravessa a fronteira de armazenamento.

### Pose2Sim + OpenSim

Fluxo offline de referência para sessões controladas com três ou quatro câmeras. Responsável por calibração, sincronização, associação entre câmeras, triangulação, filtragem 3D e cinemática musculoesquelética.

### FreeMoCap

Sistema de referência para gravação e comparação de reconstruções 3D. Deve ser executado como ferramenta de laboratório separada devido à licença AGPL e ao peso operacional.

### MMAction2

Framework de treinamento para classificar sequências de esqueleto e localizar eventos no tempo. O modelo final precisa ser treinado com dataset próprio de Jiu-Jitsu, pois checkpoints gerais não conhecem posições e transições de grappling.

### MotionBERT-Lite

Encoder temporal opcional para sequências corporais de 17 articulações. Pode ajudar em representação temporal e 3D, mas não substitui RTMW para dedos, mãos, pés ou contato entre dois praticantes.

## Camada experimental

WHAM, HMR2/4DHumans, OpenCap Monocular e MonoMSK são úteis como benchmarks de pesquisa. Modelos baseados em SMPL ou estimativas monoculares podem produzir corpos visualmente plausíveis sem precisão articular suficiente para uma afirmação biomecânica. Nenhum deles entra no relatório principal sem validação contra o fluxo multicâmera.

## Métricas implementadas

- ângulo articular 2D/3D;
- amplitude de movimento;
- comprimento da trajetória;
- jerk normalizado como proxy transparente de suavidade;
- diferença bilateral normalizada;
- inclinação do tronco;
- qualidade por região corporal;
- bloqueio de análise fina das mãos sob oclusão;
- histerese para evitar troca instável de fase técnica.

## Métricas futuras após validação

- velocidade e aceleração angular;
- estabilidade da base de suporte;
- deslocamento do centro corporal;
- tempo de transição entre posições;
- distância entre quadris, troncos, mãos e pontos de controle;
- contato provável entre segmentos;
- consistência entre câmeras;
- erro de reprojeção 3D;
- entropia e confiança calibrada da fase técnica.

## Ontologia de técnicas

Cada técnica deve ser rotulada em etapas, não como um único nome:

```text
setup
entry
control
transition
completion
recovery
unclassified
```

A primeira biblioteca deve incluir tarefas cooperativas e movimentos mensuráveis:

- technical stand-up;
- hip escape;
- bridge;
- guard recovery;
- positional transition;
- controlled grip and release;
- posture maintenance;
- return after voluntary pause.

Finalizações e situações de alta compressão devem entrar somente depois de protocolos adultos controlados.

## Qualidade obrigatória

Uma métrica só entra no relatório quando todas as condições específicas forem satisfeitas. Exemplos:

- corpo: landmarks válidos ≥ 70%;
- mãos: landmarks válidos ≥ 75%;
- atribuição individual ≥ 80%;
- oclusão ≤ 35% para cinemática corporal;
- oclusão ≤ 20% para análise fina das mãos;
- frames perdidos ≤ 10%;
- calibração e sincronização válidas para 3D.

Os limites são configuração inicial de engenharia e precisam ser ajustados por estudo de validação.

## Dataset NeuroJitsu-BJJ

Cada amostra deve conter:

- código pseudônimo;
- sessão e câmera;
- timestamps sincronizados;
- caixas e keypoints 2D;
- keypoints 3D quando disponíveis;
- identidade operacional confirmada/incerta;
- fase técnica;
- técnica ou tarefa;
- assistência do professor;
- oclusão;
- qualidade de vídeo;
- confiança do avaliador;
- divergência entre avaliadores.

A separação de treino, validação e teste deve ocorrer por participante e sessão, nunca por frames adjacentes.

## Validação

1. objetos e movimentos sintéticos;
2. adultos, uma pessoa, tarefas simples;
3. adultos, múltiplas câmeras;
4. dois adultos em contato cooperativo;
5. comparação com avaliadores humanos;
6. comparação com referência 3D;
7. estudo silencioso aprovado com crianças;
8. relatório revisado sem alertas automáticos;
9. apenas depois, suporte em tempo real.
