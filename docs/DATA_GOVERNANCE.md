# Governança de dados

## Classificação

| Dado | Classe | Padrão |
|---|---|---|
| Nome e chave de reidentificação | Crítico | Banco separado; não implementado no MVP público |
| Vídeo original | Crítico | Nunca persistir |
| Vídeo redigido | Alto | Desativado por padrão |
| Landmarks e fisiologia | Alto | SQLCipher |
| Métricas agregadas pseudônimas | Médio | SQLCipher |
| Dataset sintético | Baixo | SQLite permitido |

## Regras operacionais

- Consentimento e assentimento são verificados antes da captura.
- Nenhum reconhecimento facial.
- Nenhuma inferência emocional pela face.
- A chave do banco vem de variável de ambiente ou cofre.
- Toda leitura de janelas e relatórios gera audit trail.
- Frames não aparecem em logs, exceptions ou payloads de API.
- A política de retenção deve ser aprovada institucionalmente antes da coleta real.

## PIPL/LGPD

A arquitetura é **privacy-by-design**, mas conformidade jurídica depende de protocolo, finalidade, consentimento, contratos, localização dos dados, revisão institucional e operação real. O código não pode garantir aprovação regulatória.
