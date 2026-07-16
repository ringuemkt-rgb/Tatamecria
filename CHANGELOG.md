# Changelog

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
