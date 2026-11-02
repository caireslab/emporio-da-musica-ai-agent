# Sub-Atividade 6.1 — Planejamento de Release & Deployment (`v1.0.0`)

> **Projeto:** Empório da Música — Conversational AI Agent  
> **Fase SDLC:** 06 — Release & Evolution (`sdlc-06-evolution`)  
> **Status:** Release `v1.0.0` Publicada e Validada por Smoke Test

---

## 1. Versionamento Semântico (SemVer) e Estratégia de Rollback

- **Versão Oficial:** `v1.0.0` (General Availability — Entrega Completa do Desafio Técnico AI Engineer).
- **Repositório Público:** `https://github.com/caireslab/emporio-da-musica-ai-agent`
- **Procedimento de Rollback Automatizado (RTO < 2 min):**
  - Em caso de falha do provedor primário de LLM (ex.: indisponibilidade regional da API Google Gemini), basta alternar `LLM_PROVIDER=openai` ou `LLM_PROVIDER=groq` no `.env` e reiniciar o container (`docker compose restart emporio-web`), sem qualquer alteração de código.
  - Em caso de regressão de código, reversão imediata via `git checkout v1.0.0 && docker compose up -d --build`.

---

## 2. Evidência Empírica do Smoke Test Pós-Deploy

```json
{"status": "healthy", "version": "1.0.0", "products_loaded": 65, "categories_loaded": 9, "orders_loaded": 20, "customers_loaded": 50, "policy_sections": 9}
```
