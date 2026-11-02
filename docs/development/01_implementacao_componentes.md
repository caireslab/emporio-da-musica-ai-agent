# Sub-Atividade 4.1 — Implementação de Código & Componentes

> **Projeto:** Empório da Música — Conversational AI Agent  
> **Fase SDLC:** 04 — Development & Integration (`sdlc-04-development`)  
> **Status:** Concluído (Zero Placeholders, Validado por `validate_graph.py`)

---

## 1. Inventário de Módulos Implementados (Clean Architecture)

| Camada | Arquivo | Responsabilidade Técnica |
| :--- | :--- | :--- |
| **Configuração** | [`src/config.py`](file:///c:/Users/Raul%20Caires/Documents/Desafio%20tecnico/Desafio%20Técnico%20AI%20Engineer/src/config.py) | Carregamento seguro de variáveis `.env` (`LLM_PROVIDER`, `GOOGLE_API_KEY`, `OPENAI_API_KEY`, `GROQ_API_KEY`, `REFERENCE_DATE`, `DATA_DIR`). |
| **Domínio (Entidades)** | [`src/domain/models.py`](file:///c:/Users/Raul%20Caires/Documents/Desafio%20tecnico/Desafio%20Técnico%20AI%20Engineer/src/domain/models.py) | Modelos imutáveis Pydantic v2 (`Category`, `Product`, `Promotion`, `Customer`, `OrderItem`, `Order`, `PricingSimulation`, `InstallmentOption`, `ShippingSimulation`, `ReturnEligibilityReport`). |
| **Domínio (Regras Puras)** | [`src/domain/rules.py`](file:///c:/Users/Raul%20Caires/Documents/Desafio%20tecnico/Desafio%20Técnico%20AI%20Engineer/src/domain/rules.py) | Cálculo determinístico da não-cumulatividade PIX vs. Promoção (Seção 6.2), escada de parcelas mínimas R\$ 50/80/100 (Seção 3.1), frete regional e frete grátis > R\$ 1.000 (Seção 5), elegibilidade de devolução 7 dias e troca 30 dias (Seção 4) e registro de discrepâncias cadastrais (IDs `135`–`144`). |
| **Dados & Sanitização** | [`src/data/repository.py`](file:///c:/Users/Raul%20Caires/Documents/Desafio%20tecnico/Desafio%20Técnico%20AI%20Engineer/src/data/repository.py) | Repositório Read-Only em memória para os 6 CSVs de `data/`, busca semântica/léxica normalizada sem acentos, detecção de categorias vazias (IDs 6, 7, 8), recomendação de substitutos disponíveis e desambiguação LGPD de homônimos (`Bruno Martins`, `Diego Castro`). |
| **Base de Políticas (RAG)** | [`src/data/policy_kb.py`](file:///c:/Users/Raul%20Caires/Documents/Desafio%20tecnico/Desafio%20Técnico%20AI%20Engineer/src/data/policy_kb.py) | Extração de `data/políticas_da_loja.pdf` via `pypdf` combinada às 10 seções canônicas indexadas por tópicos e palavras-chave. |
| **Ferramentas (`@tool`)** | [`src/tools/store_tools.py`](file:///c:/Users/Raul%20Caires/Documents/Desafio%20tecnico/Desafio%20Técnico%20AI%20Engineer/src/tools/store_tools.py) | 6 ferramentas estruturadas com schemas Pydantic v2 (`search_products_catalog`, `get_product_pricing_and_payment`, `calculate_shipping_info`, `inspect_customer_order_and_return`, `lookup_store_policy`, `register_complaint_or_handover`). |
| **Agente LangGraph** | [`src/agent/graph.py`](file:///c:/Users/Raul%20Caires/Documents/Desafio%20tecnico/Desafio%20Técnico%20AI%20Engineer/src/agent/graph.py), [`src/agent/prompts.py`](file:///c:/Users/Raul%20Caires/Documents/Desafio%20tecnico/Desafio%20Técnico%20AI%20Engineer/src/agent/prompts.py), [`src/agent/llm_factory.py`](file:///c:/Users/Raul%20Caires/Documents/Desafio%20tecnico/Desafio%20Técnico%20AI%20Engineer/src/agent/llm_factory.py) | Grafo de estado `StateGraph(MessagesState)` com `ToolNode`, `tools_condition`, `MemorySaver` por `thread_id`, System Prompt com persona acolhedora (Seção 7.1) e fábrica multi-provider (Gemini / OpenAI / Groq). |
| **Interfaces & Containers** | [`src/ui/cli.py`](file:///c:/Users/Raul%20Caires/Documents/Desafio%20tecnico/Desafio%20Técnico%20AI%20Engineer/src/ui/cli.py), [`src/ui/streamlit_app.py`](file:///c:/Users/Raul%20Caires/Documents/Desafio%20tecnico/Desafio%20Técnico%20AI%20Engineer/src/ui/streamlit_app.py), [`main.py`](file:///c:/Users/Raul%20Caires/Documents/Desafio%20tecnico/Desafio%20Técnico%20AI%20Engineer/main.py), [`app.py`](file:///c:/Users/Raul%20Caires/Documents/Desafio%20tecnico/Desafio%20Técnico%20AI%20Engineer/app.py), [`Dockerfile`](file:///c:/Users/Raul%20Caires/Documents/Desafio%20tecnico/Desafio%20Técnico%20AI%20Engineer/Dockerfile), [`docker-compose.yml`](file:///c:/Users/Raul%20Caires/Documents/Desafio%20tecnico/Desafio%20Técnico%20AI%20Engineer/docker-compose.yml) | CLI interativa Rich (com modo `--demo` e `--query`), interface Web Streamlit com inspetor de tool calls e empacotamento Docker multi-serviço. |

---

## 2. Evidência do Linter Estático de LangGraph

```text
🔍 [LangGraph Linter] Analisados 1 arquivos em 'src\agent\graph.py'.
✅ Nenhum anti-pattern de LangGraph detectado! Código em conformidade moderna.
```
