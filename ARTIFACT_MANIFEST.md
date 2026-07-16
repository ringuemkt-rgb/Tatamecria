# Manifesto da entrega

## Estado validado

- 39 módulos Python em `src/neurojitsu`;
- 22 testes automatizados aprovados;
- Ruff sem violações;
- mypy estrito sem erros;
- fluxo sintético end-to-end executado;
- API validada em `/health`, `/sessions` e `/reports/{session_id}`;
- relatório demonstrativo JSON/HTML gerado.

## Perfis

- **Executável agora:** sintético, agentes estruturados, banco, relatório e API.
- **Executável após instalar extra:** dashboard, câmera, MediaPipe, Supervision, NeuroKit2.
- **Exige hardware e validação:** multi-pessoa e RuView/WiFi-CSI.
- **Exige governança institucional:** qualquer dado de criança ou uso clínico.

## Garantias técnicas reais

- frames originais não são persistidos pelo pipeline fornecido;
- participantes reais são bloqueados em banco SQLite não criptografado;
- métricas inválidas carregam motivo explícito;
- relatórios exigem revisão profissional;
- LLM e RuView não fazem parte do caminho obrigatório.

## O que não é garantido pelo código

- aprovação ética ou regulatória;
- validade clínica das métricas;
- conformidade PIPL/LGPD apenas pela instalação;
- precisão em BJJ multi-pessoa sem estudo de validação;
- previsão de crise, emoção ou diagnóstico de TEA.
