# Sub-Atividade 6.3 — Operação & Gestão de Incidentes (SLAs & Runbooks)

> **Projeto:** Empório da Música — Conversational AI Agent  
> **Fase SDLC:** 06 — Release & Evolution (`sdlc-06-evolution`)  
> **Status:** Matriz SEV e Runbooks Operacionais Ativos

---

## 1. Matriz de Severidade Operacional e SLAs

| Severidade | Definição no Contexto do Empório da Música | Tempo de Resposta (SLA) | Ação de Contenção (Runbook) |
| :--- | :--- | :--- | :--- |
| **SEV-1 (Crítico)** | Indisponibilidade total do provedor LLM primário ou falha de leitura dos CSVs. | `< 5 minutos` | Failover imediato no `.env` (`LLM_PROVIDER=openai` ou `groq`) e reinício do serviço. |
| **SEV-2 (Alto)** | Divergência cadastral detectada em produto (`IDs 135–144`) ou reclamação formal de pós-venda. | `Até 24 horas úteis` (Seção 7.3 do Manual) | Acionamento automático da tool `register_complaint_or_handover` gerando protocolo `EMP-2026-XXXX` para a gerência. |
| **SEV-3 (Médio)** | Solicitação de encomenda para categorias temporariamente sem estoque (`IDs 6, 7, 8`). | `Até 24 horas úteis` | Registro de protocolo `encomenda_produto` junto à equipe comercial. |
| **SEV-4 (Baixo)** | Dúvida fora de escopo (acessórios musicais). | Imediato (no próprio turno) | Redirecionamento educado sugerindo lojas parceiras de acessórios (Seção 7.1). |
