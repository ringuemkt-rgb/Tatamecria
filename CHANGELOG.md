# Changelog

## 0.2.0 — 2026-07-16

### Motion Intelligence

- contratos whole-body para corpo, mãos, pés e pontos faciais;
- métricas transparentes de ângulo, amplitude, trajetória, jerk, diferença bilateral e inclinação do tronco;
- controle de qualidade por região corporal, oclusão, frames perdidos e confiança de atribuição;
- ontologia temporal `setup`, `entry`, `control`, `transition`, `completion` e `recovery`;
- estabilização de fase por threshold e confirmações consecutivas;
- configuração em camadas para RTMW/RTMO, Pose2Sim, OpenSim, MMAction2 e MotionBERT;
- matriz de adoção de repositórios e separação explícita entre núcleo, referência e laboratório experimental;
- testes unitários para biomecânica, fases técnicas e quality gates.

### Governança

- ferramentas de identificação facial não entram no caminho operacional;
- localização da região facial permanece restrita à redação visual e estudos separados;
- modelos pesados e licenças restritivas continuam desacoplados do pacote principal.

## 0.1.0 — 2026-07-16

### Adicionado

- núcleo determinístico com contratos Pydantic;
- máquina de estados da sessão;
- segmentação por fases e métricas cinemáticas;
- processamento HRV temporal com bloqueio por qualidade;
- banco transacional com integridade SHA-256;
- modo SQLCipher e cofre de identidade separado;
- agentes de movimento, participação e qualidade;
- relatório individual JSON/HTML;
- API FastAPI e dashboard Streamlit;
- adaptadores MediaPipe, Supervision e RuView;
- dados sintéticos, Docker, CI, Dependabot e suíte de testes.

### Segurança

- frames originais não são persistidos pelo pipeline fornecido;
- participantes reais são bloqueados sem SQLCipher;
- LLM e WiFi-CSI permanecem fora do caminho crítico;
- revisão profissional obrigatória em todos os relatórios.
