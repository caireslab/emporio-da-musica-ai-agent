# 03 — Priorização do Backlog e Fatiamento de MVP

> **Status:** Validado  
> **Data:** 2026-11-02  
> **Artefato:** `docs/requirements/03_priorizacao_backlog.md`  

---

## 1. Matriz de Priorização MoSCoW

> **Auditoria de Equilíbrio do Backlog:** De um total de **13 itens funcionais e técnicos** mapeados para o ciclo completo do produto, **7 itens (53,8%)** estão classificados como **Must Have** (respeitando estritamente o teto de `< 60%` para blindagem contra *scope creep*), **3 itens (23,1%)** como **Should Have**, **1 item (7,7%)** como **Could Have** e **2 blocos (15,4%)** como **Won't Have**.

### 1.1 Must Have (Crítico para viabilidade do MVP — 53,8% do Backlog)
*Funcionalidades inegociáveis exigidas pelo enunciado do Desafio Técnico Artefact:*
- [x] **M-01 (`RF-01` / `US-06`):** Persona conversacional da Empório da Música (*"amigo que entende de música"*) e guardrails estritos de escopo (recusa educada de acessórios como cordas, cabos, palhetas, cases, pedais e amplificadores, além de assuntos externos).
- [x] **M-02 (`RF-02` / `US-03`):** Pipeline de ingestão e higienização de `data/*.csv` (tratamento da anomalia cadastral `name` vs. `description`/`specs` nos `IDs 135–144`, categorias vazias `IDs 6–8`, promoções ativas `is_active=1` vs. expiradas `is_active=0` e status `active`/`discontinued`/`coming_soon`).
- [x] **M-03 (`RF-03`, `RF-04`, `RF-05` / `US-01`, `US-02`, `US-03`):** Ferramentas determinísticas de busca de catálogo (por categoria/preço efetivo/termo), sugestão de alternativas para itens indisponíveis e cálculo exato de promoções, PIX (5% não cumulativo) e parcelamento escalonado (pisos de R\$ 50, R\$ 80 e R\$ 100).
- [x] **M-04 (`RF-06`, `RF-09` / `US-06`):** Ferramenta de consulta estruturada ao Manual de Políticas (`políticas_da_loja.pdf`) e cálculo de frete/prazos (Campo Grande vs. outras cidades via PAC/SEDEX/Jadlog e alerta de grande porte).
- [x] **M-05 (`RF-07`, `RF-08` / `US-04`, `US-05`):** Ferramenta de consulta de pedidos e clientes com **desambiguação obrigatória de homônimos (LGPD)** e avaliação determinística de elegibilidade de troca/devolução/arrependimento (7 dias recebimento / 30 dias defeito / 90 dias CDC).
- [x] **M-06 (`RF-10`):** Persistência de histórico de conversa multi-turn por sessão + Interface CLI interativa funcional.
- [x] **M-07 (Entregáveis Obrigatórios Artefact):** `README.md` arquitetural completo + 3 a 5 exemplos de interação real documentados em `examples/` + Repositório Git público com commits incrementais.

### 1.2 Should Have (Importante e de alto valor diferencial — 23,1% do Backlog)
*Funcionalidades que elevam o padrão sênior da entrega sem bloquear o núcleo conversacional:*
- [x] **S-01 (`RF-09` / `US-07`):** Ferramenta dedicada `register_complaint_or_handover` para registro estruturado de reclamações e encaminhamento à gerência com protocolo e SLA de 24h úteis, mantendo a sessão ativa.
- [x] **S-02 (`RF-10`):** Interface Web simples e intuitiva (ex.: Streamlit) para permitir testar o agente visualmente no navegador além da CLI.
- [x] **S-03 (`RNF-01`, `RNF-05`):** Suíte automatizada de testes (`pytest`) cobrindo 100% das regras de negócio determinísticas, anomalias de dados e roteamento de ferramentas.

### 1.3 Could Have (Desejável / Melhoria de experiência — 7,7% do Backlog)
*Item de conveniência visual se houver margem na janela de implementação:*
- [x] **C-01:** Painel/Inspetor de Telemetria de Tool Calls (exibindo na UI/CLI quais ferramentas foram acionadas pelo agente em cada turno e os argumentos passados, facilitando a auditoria pela banca da Artefact).

### 1.4 Won't Have (Fora de Escopo nesta Release — 15,4% do Backlog)
*Funcionalidades expressamente descartadas para proteger o foco e a integridade dos dados:*
- ❌ **W-01:** Mutação ou sobrescrita destrutiva nos arquivos `data/*.csv` originais (sistema opera em modo estritamente Read-Only sobre as tabelas de origem).
- ❌ **W-02:** Integração externa com API oficial da Meta (WhatsApp Cloud API), geração de cobrança bancária real (PIX/Cartão) ou consulta externa aos webservices dos Correios/Jadlog.

---

## 2. Estratégia de Fatiamento de Releases (Release Slices)

| Release | Foco Estratégico | Itens Incluídos | Critério de Go-Live |
| :--- | :--- | :--- | :--- |
| **MVP Core (v1.0-core)** | Cumprimento integral de 100% dos requisitos do Desafio Artefact | Todos os itens **Must Have (`M-01` a `M-07`)** + **`S-01`** e **`S-03`** | Agente respondendo com 0% de alucinação na CLI, testes passando e 5 exemplos documentados |
| **Release Sênior (v1.0-full)** | Experiência Visual & Observabilidade para Avaliadores | Adição de **`S-02` (Web UI)** e **`C-01` (Inspetor de Tool Calls)** | Interface Web operacional integrada ao mesmo motor agêntico da CLI |
| **v2.0 (Roadmap Futuro)** | Evolução Pós-Desafio (Documentado no `README.md`) | Itens **Won't Have** (Integração WhatsApp Business API, Banco Relacional PostgreSQL, Painel Humano de Handoff) | Aprovação de entrada em produção real na Empório da Música |
