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

### Supervision Vision Bus

- conversão validada para `sv.Detections` com caixas, confiança, classes, tracks e códigos pseudônimos;
- conversão whole-body para `sv.KeyPoints`;
- zonas poligonais para tatame, drills, pausa e exclusão;
- máquina de estados determinística para eventos `enter`, `dwell` e `exit`;
- cálculo auditável do tempo de permanência por track temporário;
- documentação de separação entre tracking visual e identidade pseudônima;
- testes unitários independentes da instalação opcional do Supervision.

### Governança

- ferramentas de identificação facial não entram no caminho operacional;
- localização da região facial permanece restrita à redação visual e estudos separados;
- modelos pesados e licenças restritivas continuam desacoplados do pacote principal;
- metadados do Supervision não podem conter nomes, embeddings ou identificadores diretos.

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
