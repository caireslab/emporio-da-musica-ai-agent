# Sub-Atividade 6.4 — Evolução Contínua, Feedback & Dívida Técnica (Roadmap V-Next)

> **Projeto:** Empório da Música — Conversational AI Agent  
> **Fase SDLC:** 06 — Release & Evolution (`sdlc-06-evolution`)  
> **Status:** Inventário de Dívida Técnica e Backlog V-Next Consolidados

---

## 1. Registro Estruturado de Dívida Técnica e Limitações Conhecidas

| ID | Descrição Técnica | Impacto Atual | Solução Planejada (Release Alvo) |
| :--- | :--- | :--- | :--- |
| **DEBT-01** | Checkpointer em memória (`MemorySaver`) reinicia o histórico de sessões se o container reiniciar. | Médio (apenas em restart de container) | Migrar para `AsyncPostgresSaver` / Redis na **v1.1.0**. |
| **DEBT-02** | Base de dados estática em arquivos CSV Read-Only (`data/*.csv`). | Baixo (adequado ao escopo de 65 produtos do desafio) | Integrar com PostgreSQL + `pgvector` para busca híbrida BM25 + semântica na **v1.2.0**. |
| **DEBT-03** | Cotação de frete nacional baseada na tabela de prazos do Manual (sem tarifação dinâmica por CEP/cubagem). | Baixo | Integrar API REST dos Correios/Jadlog na **v1.2.0**. |
| **DEBT-04** | Desambiguação LGPD de homônimos realizada via confirmação conversacional de telefone/pedido. | Baixo | Adicionar verificação via token OTP no WhatsApp Business API na **v2.0.0**. |
