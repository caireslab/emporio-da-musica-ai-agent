# Sub-Atividade 5.1 — Testes Funcionais, Aceite e Regressão

> **Projeto:** Empório da Música — Conversational AI Agent  
> **Fase SDLC:** 05 — Validation & Quality (`sdlc-05-validation`)  
> **Status:** 100% Aprovado (15/15 Testes Automatizados + 5 Cenários E2E do Desafio)

---

## 1. Matriz de Validação E2E dos Requisitos Funcionais (`RF-01` a `RF-10`) e Cenários BDD (`BDD-01` a `BDD-08`)

| Caso de Teste | Requisito / BDD | Cenário Validado | Resultado | Evidência Empírica |
| :--- | :--- | :--- | :--- | :--- |
| **TC-E2E-01** | `RF-01`, `RF-03` / `BDD-01` | *"Quais opções de violões disponíveis custando até R$1000?"* | ✅ APROVADO | Retornou exatamente os **12 violões ativos e com estoque > 0** até R\$ 1.000, excluindo `ID 96` (`stock = 0`) e `ID 113` (`discontinued`). |
| **TC-E2E-02** | `RF-04`, `RF-05` / `BDD-02` | *"Quanto custa o Takamine GD20?"* + Promoção expirada e PIX | ✅ APROVADO | Preço oficial R\$ 2.199,00, alerta de expiração da campanha de 12% (*Semana do Violão*), PIX 5% aplicado (R\$ 2.089,05) e não-cumulatividade verificada em itens promocionais (`ID 90`, `ID 94`). |
| **TC-E2E-03** | `RF-02`, `RF-07` / `BDD-06` | *"Qual o endereço da loja?"* + Horários + Frete | ✅ APROVADO | Endereço `Rua 14 de Maio, 3200 — Centro, Campo Grande - MS`, horários Seg-Sex 09h–18h / Sáb 09h–13h e frete grátis > R\$ 500 em Campo Grande. |
| **TC-E2E-04** | `RF-06` / `BDD-07` | *"Me arrependi da minha compra, posso devolver meu pedido?"* | ✅ APROVADO | Regras da Seção 4 (7 dias corridos do recebimento, sem uso, frete pela loja, reembolso em 10 dias úteis) + cálculo real nos Pedidos #1 e #8. |
| **TC-E2E-05** | `RF-08`, `RF-09`, `RF-10` / `BDD-03`, `BDD-04`, `BDD-05`, `BDD-08` | Guardrail de acessórios, categorias vazias (6–8), discrepâncias (135–144) e homônimos LGPD (`Bruno Martins`) | ✅ APROVADO | Bloqueio `OUT_OF_SCOPE_ACCESSORY`, `CATEGORY_TEMPORARILY_WITHOUT_STOCK` e `AMBIGUOUS_HOMONYM_DETECTED` validados. |
