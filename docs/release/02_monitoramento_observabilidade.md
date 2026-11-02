# Sub-Atividade 6.2 — Produção, Monitoramento & Observabilidade GenAI

> **Projeto:** Empório da Música — Conversational AI Agent  
> **Fase SDLC:** 06 — Release & Evolution (`sdlc-06-evolution`)  
> **Status:** Telemetria de Tool Calls Ativa e Padrão OpenTelemetry GenAI Mapeado

---

## 1. Rastreabilidade Estruturada de Tool Calls (`tool_calls_trace`)

Cada chamada a `EmporioMusicaAssistant.chat(user_message, thread_id)` retorna nativamente o dicionário auditável:
- `thread_id`: identificador da sessão no `MemorySaver`.
- `tool_calls`: lista ordenada contendo `tool_name`, `args`, `id` e `output_preview` de cada ferramenta executada pelo `ToolNode`.

---

## 2. Golden Signals & Regras de Alerta (Zero Alert Fatigue)

| Sinal Dourado | Métrica Monitorada | Limiar P1 (Crítico) | Limiar P2 (Warning) |
| :--- | :--- | :--- | :--- |
| **Latência (Latency)** | Tempo total do turno (`agent ➔ tools ➔ agent`) | `> 8.0s` por 5 min | `> 4.0s` por 10 min |
| **Erros (Errors)** | Exceções de provedor LLM após 3 retries (`max_retries=3`) | `> 5%` das requisições | `> 1%` das requisições |
| **Saturação de Loop** | `iteration_count` atingindo o limite de segurança (`>= 8`) | Qualquer ocorrência | `>= 5` iterações no mesmo turno |
| **Segurança LGPD** | Disparo de `AMBIGUOUS_HOMONYM_DETECTED` | Log de auditoria obrigatório | — |
