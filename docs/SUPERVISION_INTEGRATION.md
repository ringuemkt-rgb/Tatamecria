# Roboflow Supervision no NeuroJitsu

## Decisão arquitetural

O `roboflow/supervision` é a camada model-agnostic de engenharia de visão do NeuroJitsu. Ele padroniza resultados de detectores e estimadores, conecta tracking e zonas e compõe previews redigidos. Ele não é um modelo de IA e não produz interpretação clínica.

```text
Detector de pessoas / segmentação
              ↓
        sv.Detections
              ↓
trackers.ByteTrackTracker
              ↓
IDs visuais temporários
              ↓
sv.PolygonZone + ZoneEventEngine
              ↓
pose whole-body / qualidade / eventos
              ↓
analytics e relatório revisado
```

## Responsabilidades do Supervision

- transportar caixas, máscaras, confiança, classes e `tracker_id`;
- transportar metadados de câmera e dados pseudônimos permitidos;
- converter keypoints para visualização padronizada;
- testar presença em zonas do tatame;
- fornecer anotadores para previews já redigidos;
- apoiar leitura, transformação e exportação de vídeos autorizados;
- desacoplar o NeuroJitsu de YOLO, RT-DETR, RF-DETR, Transformers ou MMDetection.

## Responsabilidades que permanecem no NeuroJitsu

- consentimento e governança;
- redação facial antes de preview ou persistência;
- associação entre `tracker_id` e participante pseudônimo;
- quality gates de corpo, mãos, pés, oclusão e frames perdidos;
- cálculo biomecânico;
- fases técnicas;
- interpretação profissional;
- criptografia, auditoria e retenção.

## Módulos implementados

### `supervision_runtime.py`

Fornece:

- `DetectionRecord`;
- `ZoneDefinition`;
- conversão para `sv.Detections`;
- conversão whole-body para `sv.KeyPoints`;
- criação de `sv.PolygonZone`;
- cálculo de IDs temporários presentes em cada zona;
- avaliação simultânea de múltiplas zonas.

### `zone_events.py`

Máquina de estados determinística e independente de OpenCV que transforma presença por frame em:

- `enter`;
- `dwell`;
- `exit`;
- duração total da permanência.

A separação permite testes sintéticos e evita que a semântica temporal dependa da biblioteca visual.

## Zonas recomendadas

```text
tatame_active       área principal de atividade
technical_drill     área de execução orientada
sensory_pause       área de pausa voluntária
instructor          área reservada ao profissional
equipment_exclusion área de câmera, parede ou equipamentos
```

A âncora padrão deve ser o ponto inferior central da caixa corporal. Isso aproxima a decisão da posição da pessoa no chão e evita usar o centro do tronco como localização espacial.

## Tracking

Não utilizar `sv.ByteTrack` em código novo. A classe está em descontinuação e deve ser substituída por `ByteTrackTracker` do pacote `trackers`.

```text
tracker_id = identidade visual temporária
participant_id = código pseudônimo confirmado
```

Os dois identificadores nunca devem ser tratados como equivalentes sem confirmação operacional.

## Privacidade

Supervision só pode receber frames depois da etapa de redação quando a finalidade for preview, anotação ou armazenamento. Frames originais podem existir temporariamente apenas no estágio de localização facial e devem ser liberados depois.

Não armazenar nos campos `data` ou `metadata`:

- nomes reais;
- imagens faciais;
- embeddings biométricos;
- documentos;
- contatos;
- referências capazes de reidentificar diretamente a criança.

## Política de versão

O projeto mantém Supervision como dependência opcional. A faixa atual aceita versões `>=0.27,<0.31`; antes de adotar 0.31, deve-se executar uma revisão de compatibilidade porque o `sv.ByteTrack` legado será removido.

Backends de detecção e pose continuam em serviços opcionais. Uma atualização do Supervision não deve impedir o fluxo sintético, o banco, os agentes ou os relatórios determinísticos.

## Critérios de aceite

- nenhum frame não redigido é persistido pelo pipeline;
- toda zona usa deteções rastreadas;
- eventos possuem timestamp e track temporário;
- eventos individuais só entram no relatório após associação pseudônima confiável;
- oclusão e identidade incerta bloqueiam interpretações finas;
- a falha do Supervision não interrompe módulos sem visão;
- a suíte principal executa sem instalar o extra `vision`.
