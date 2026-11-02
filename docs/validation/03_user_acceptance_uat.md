# Sub-Atividade 5.3 — Teste de Aceite do Usuário (UAT) & Fidelidade Factual de IA

> **Projeto:** Empório da Música — Conversational AI Agent  
> **Fase SDLC:** 05 — Validation & Quality (`sdlc-05-validation`)  
> **Status:** 100% Homologado nas 3 Personas do Discovery

---

## 1. Roteiros de Homologação por Persona (Discovery ➔ UAT)

| Persona | Jornada Homologada | Critério de Sucesso | Status |
| :--- | :--- | :--- | :--- |
| **P1 — Iniciante / Estudante (Orçamento até R\$ 1.000)** | Consulta de violões até R\$ 1.000 + diferença entre nylon e aço + simulação de parcelamento no cartão. | Linguagem acolhedora ("amigo que entende de música"), exclusão de itens sem estoque (`ID 96`, `ID 113`) e cálculo exato de parcelas mínimas. | ✅ APROVADO |
| **P2 — Músico Intermediário / Profissional** | Consulta do *Takamine GD20* (`ID 95`), verificação de promoção expirada (*Semana do Violão 12%*) vs. violões com promoção ativa (`Crafter HT-100` 18% OFF) e frete de grande porte. | Fidelidade factual 100% aos CSVs, aplicação correta da não-cumulatividade PIX (Seção 6.2) e transparência sobre divergências cadastrais (`IDs 135–144`). | ✅ APROVADO |
| **P3 — Cliente Pós-Venda (Pedidos, Trocas e LGPD)** | Consulta de Direito de Arrependimento (7 dias), rastreio do Pedido #8, garantia do Pedido #1 e proteção de homônimos (*Bruno Martins*). | Contagem exata de dias corridos a partir do recebimento/compra e bloqueio LGPD até confirmação do telefone. | ✅ APROVADO |

---

## 2. Auditoria de Fidelidade Factual (Faithfulness & Tool Grounding)

- **Zero Alucinação de Preços ou Estoque:** 100% dos valores monetários e quantidades em estoque citados nos 5 exemplos (`examples/01..05.md`) provêm diretamente do retorno JSON das 6 ferramentas determinísticas.
- **Acessibilidade e Ergonomia (CLI Rich & Streamlit Web UI):** Interface CLI formatada com painéis de alto contraste e tabelas legíveis; interface Web Streamlit com botões de atalho semântico e inspetor expansível de `tool_calls`.
