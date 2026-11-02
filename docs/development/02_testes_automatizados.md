# Sub-Atividade 4.2 — Testes Automatizados & Cobertura

> **Projeto:** Empório da Música — Conversational AI Agent  
> **Fase SDLC:** 04 — Development & Integration (`sdlc-04-development`)  
> **Status:** 15/15 Testes Aprovados (100% PASS) | Cobertura Total: **88.39%** (Piso: 80.0%)

---

## 1. Matriz de Rastreabilidade BDD ➔ Testes Automatizados

| ID BDD | Cenário Especificado no SRS | Teste Automatizado | Resultado |
| :--- | :--- | :--- | :--- |
| **BDD-01** | Busca de violões disponíveis até R\$ 1.000,00 e promoções ativas | [`test_bdd01_violoes_available_up_to_1000`](file:///c:/Users/Raul%20Caires/Documents/Desafio%20tecnico/Desafio%20Técnico%20AI%20Engineer/tests/test_domain_and_data.py#L41-L59), [`test_bdd01_active_promotions_on_violoes`](file:///c:/Users/Raul%20Caires/Documents/Desafio%20tecnico/Desafio%20Técnico%20AI%20Engineer/tests/test_domain_and_data.py#L62-L77) | ✅ PASS |
| **BDD-02** | Consulta do Takamine GD20 (promoção expirada + não-cumulatividade PIX + parcelas mínimas) | [`test_bdd02_takamine_gd20_expired_promotion_and_non_cumulative_pix`](file:///c:/Users/Raul%20Caires/Documents/Desafio%20tecnico/Desafio%20Técnico%20AI%20Engineer/tests/test_domain_and_data.py#L80-L96), [`test_installment_tiers_respect_minimum_floors`](file:///c:/Users/Raul%20Caires/Documents/Desafio%20tecnico/Desafio%20Técnico%20AI%20Engineer/tests/test_domain_and_data.py#L238-L253) | ✅ PASS |
| **BDD-03** | Alerta de discrepâncias cadastrais nos produtos IDs `135` a `144` | [`test_bdd03_catalog_discrepancies_flagged_ids_135_to_144`](file:///c:/Users/Raul%20Caires/Documents/Desafio%20tecnico/Desafio%20Técnico%20AI%20Engineer/tests/test_domain_and_data.py#L99-L109) | ✅ PASS |
| **BDD-04** | Produtos sem estoque (`96`), descontinuados (`113`, `136`), em breve (`130`) e categorias vazias (`6`, `7`, `8`) | [`test_bdd04_unavailable_items_and_empty_categories`](file:///c:/Users/Raul%20Caires/Documents/Desafio%20tecnico/Desafio%20Técnico%20AI%20Engineer/tests/test_domain_and_data.py#L112-L139) | ✅ PASS |
| **BDD-05** | Guardrail de fora de escopo (acessórios musicais não comercializados) | [`test_bdd05_accessory_out_of_scope_guardrail`](file:///c:/Users/Raul%20Caires/Documents/Desafio%20tecnico/Desafio%20Técnico%20AI%20Engineer/tests/test_domain_and_data.py#L142-L147) | ✅ PASS |
| **BDD-06** | Endereço físico, horários de funcionamento e cálculo de frete regional/nacional | [`test_bdd06_store_policy_address_and_shipping`](file:///c:/Users/Raul%20Caires/Documents/Desafio%20tecnico/Desafio%20Técnico%20AI%20Engineer/tests/test_domain_and_data.py#L150-L185) | ✅ PASS |
| **BDD-07** | Elegibilidade de arrependimento (7 dias corridos) e defeito (30 dias na loja / 90 dias CDC) | [`test_bdd07_order_return_eligibility_all_statuses`](file:///c:/Users/Raul%20Caires/Documents/Desafio%20tecnico/Desafio%20Técnico%20AI%20Engineer/tests/test_domain_and_data.py#L188-L214) | ✅ PASS |
| **BDD-08** | Proteção LGPD contra vazamento em clientes homônimos (`Bruno Martins`, `Diego Castro`) + Grafo Multi-Turn | [`test_bdd08_lgpd_homonym_disambiguation`](file:///c:/Users/Raul%20Caires/Documents/Desafio%20tecnico/Desafio%20Técnico%20AI%20Engineer/tests/test_domain_and_data.py#L217-L235), [`test_langgraph_state_graph_multi_turn_and_injection_guard`](file:///c:/Users/Raul%20Caires/Documents/Desafio%20tecnico/Desafio%20Técnico%20AI%20Engineer/tests/test_tools_and_agent.py#L171-L200) | ✅ PASS |

---

## 2. Evidência Empírica de Execução (`pytest --cov=src`)

```text
Name                       Stmts   Miss  Cover   Missing
--------------------------------------------------------
src\__init__.py                0      0   100%
src\agent\__init__.py          0      0   100%
src\agent\graph.py            80     11    86%   43-51, 99, 107
src\agent\llm_factory.py      36      6    83%   45-47, 61-63, 77-79
src\agent\prompts.py           5      0   100%
src\config.py                 21      0   100%
src\data\__init__.py           0      0   100%
src\data\policy_kb.py         32      3    91%   243, 247-248
src\data\repository.py       227     33    85%   93-94, 234, 241, 261, 369-375, 378-379, 382, 389, 447-460, 463, 550-554, 566, 588-591, 607, 616
src\domain\__init__.py         0      0   100%
src\domain\models.py          92      0   100%
src\domain\rules.py           76      3    96%   230-232
src\tools\__init__.py          0      0   100%
src\tools\store_tools.py      65      0   100%
src\ui\__init__.py             0      0   100%
src\ui\cli.py                 81     27    67%   56, 164-205
--------------------------------------------------------
TOTAL                        715     83    88%
Required test coverage of 80.0% reached. Total coverage: 88.39%
============================= 15 passed in 2.68s ==============================
```
