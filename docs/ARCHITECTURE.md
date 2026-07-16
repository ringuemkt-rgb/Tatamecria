# Arquitetura do NeuroJitsu Analytics

## Princípios

1. **Core determinístico:** coleta, qualidade, cálculos, armazenamento e relatórios não dependem de LLM.
2. **Privacidade antes da análise:** qualquer visualização ou inferência posterior recebe o frame redigido.
3. **Qualidade como dado:** toda métrica carrega confiança, validade e motivo de invalidação.
4. **Comparação longitudinal:** o participante é comparado principalmente com sua própria linha de base.
5. **Extensões isoladas:** MMPose, LLM e WiFi-CSI podem falhar sem interromper a sessão central.
6. **Decisão humana:** recomendações nunca substituem o profissional.

## Camadas

```text
┌───────────────────────────────────────────────────────────────┐
│ Interface: Streamlit / FastAPI / CLI                          │
├───────────────────────────────────────────────────────────────┤
│ Relatório: Template determinístico + revisão profissional     │
├───────────────────────────────────────────────────────────────┤
│ Agentes: qualidade | movimento | participação | protocolo     │
├───────────────────────────────────────────────────────────────┤
│ Análise: fases | cinemática | participação | HRV              │
├───────────────────────────────────────────────────────────────┤
│ Contratos: Pydantic | estado | eventos | timestamps           │
├───────────────────────────────────────────────────────────────┤
│ Ingestão: câmera | PPG | observação | RuView experimental     │
├───────────────────────────────────────────────────────────────┤
│ Governança: consentimento | SQLCipher | auditoria | retenção   │
└───────────────────────────────────────────────────────────────┘
```

## Modos

### `synthetic`

Padrão. Executa todo o pipeline sem dados pessoais, câmera ou GPU.

### `single_participant_camera`

Uma pessoa, uma câmera, face redigida, pose e métricas. Indicado para validação com adultos.

### `multi_person_research`

Duas câmeras, detector multi-pessoa, tracker, confirmação humana de identidade e backend MMPose. Não deve ser ativado antes de validação técnica.

### `wifi_csi_experimental`

RuView isolado em serviço separado. Dados entram somente após verificação de qualidade e calibração da sala.

## Fluxo dos agentes

```text
Structured SessionWindow[]
       ├── QualityAgent
       ├── MotorAgent
       ├── ParticipationAgent
       └── ProtocolAgent (futuro)
                 ↓
          ReportOrchestrator
                 ↓
         ReportPayload validado
                 ↓
       HTML/JSON + revisão humana
```

O LLM do Hugging Face é opcional e recebe somente `ReportPayload`. Ele não recebe frames nem inventa métricas.

## Evolução sem reescrita

- `PoseBackend` permite trocar MediaPipe por MMPose.
- `FrameSource` permite webcam, arquivo ou stream RTSP.
- `EventBus` local pode ser substituído por NATS quando houver múltiplos processos.
- `Database` pode trocar SQLite sintético por SQLCipher sem alterar os agentes.
- `WifiSensingWindow` mantém RuView desacoplado da análise visual.
