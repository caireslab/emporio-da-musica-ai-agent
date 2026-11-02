# 03 — Integrações, Contratos de Ferramentas (Tools) e Resiliência

> **Status:** Validado  
> **Data:** 2026-11-02  
> **Artefato:** `docs/architecture/03_integracoes_apis_mensageria.md`  

---

## 1. Catálogo de Contratos de Ferramentas do Agente (Function Calling / Tool Schemas)
O agente utiliza **6 ferramentas (tools) determinísticas** com schemas de entrada validados via **Pydantic v2** (`@tool(args_schema=...)` do `langchain_core.tools`), retornando payloads JSON estruturados para eliminar ambiguidades.

| ID Tool | Nome da Ferramenta | Finalidade & Regras Atendidas | Schema de Entrada (Pydantic v2) | Retorno Estruturado (JSON) |
| :--- | :--- | :--- | :--- | :--- |
| **T-01** | `search_products_catalog` | Busca e filtra instrumentos por categoria, termo/marca/modelo, cordas (`nylon`/`steel`), eletrônica (`yes`/`no`) e teto de orçamento (`max_price_brl` avaliado sobre o preço efetivo com promoção ativa). Trata categorias vazias (`6, 7, 8`) e itens indisponíveis (`RN-01` a `RN-06`). | `category: Optional[str]`, `search_query: Optional[str]`, `max_price_brl: Optional[float]`, `min_price_brl: Optional[float]`, `strings_type: Optional[str]`, `has_electronics: Optional[bool]`, `include_unavailable: bool = False` | Lista de produtos disponíveis (`product_id`, `name`, `category_name`, `price_brl`, `effective_price_brl`, `active_promotion`, `pix_price_brl`, `stock_quantity`, `discrepancy_note`) + alternativas caso o filtro específico bata em item indisponível. |
| **T-02** | `get_product_pricing_and_payment` | Consulta detalhes profundos de um instrumento específico (por nome ou `product_id`), verifica promoções ativas (`is_active=1`) vs. expiradas (`is_active=0`), calcula o valor no PIX (5% OFF apenas se sem promoção ativa — `RN-07`) e gera a tabela exata de parcelamento sem juros (pisos R\$ 50 / R\$ 80 / R\$ 100 e combinação > R\$ 2.000 — `RN-08`). Se indisponível (`IDs 96, 113, 136, 130`), retorna substitutos (`RN-06`). | `product_query: str` (Nome, modelo ou ID do produto) | Objeto detalhado: `product`, `availability_status`, `active_promotion`, `expired_promotions`, `pricing_breakdown` (`table_price_brl`, `effective_price_brl`, `pix_price_brl`, `pix_discount_applied`, `max_installments`, `installment_options`, `allows_combined_payment`), `alternatives`. |
| **T-03** | `calculate_shipping_info` | Calcula custos, prazos e modalidades de frete para Campo Grande/Região Metropolitana (Grátis > R\$ 500; R\$ 35 <= R\$ 500; 1–3 dias úteis motoboy) ou outras cidades (PAC 5–12d, SEDEX 2–5d, Jadlog 3–8d, com seguro e rastreamento), emitindo alerta para instrumentos de grande porte (`RN-09`). | `city: str`, `order_value_brl: Optional[float] = None`, `instrument_category_or_name: Optional[str] = None` | `is_local_campo_grande`, `shipping_cost_brl`, `free_shipping_eligible`, `carrier_options` (lista com modalidade, prazo, seguro, rastreamento), `oversized_instrument_warning`. |
| **T-04** | `inspect_customer_order_and_return` | Consulta pedidos em `orders.csv` + `order_items.csv` + `customers.csv` com **bloqueio LGPD de homônimos (`RN-10`)** e calcula deterministicamente a elegibilidade para Direito de Arrependimento (7d corridos do recebimento), Troca por Preferência (7d) e Troca por Defeito (30d na loja / 90d CDC), verificando status do pedido (`delivered`, `shipped`, `confirmed`, `pending`, `cancelled`) e exceções (`RN-11`, `RN-12`). | `order_id: Optional[int] = None`, `customer_name: Optional[str] = None`, `verifier: Optional[str] = None` (telefone, e-mail ou cidade), `reference_date: Optional[str] = "2026-03-25"` | Se ambíguo: `status="AMBIGUOUS_HOMONYM_DETECTED"`, `message` pedindo 2º fator. Se unívoco: `customer`, `order_summary` (`status`, `total_brl`, `tracking_code`, `estimated_delivery`, `notes`, `items`), `return_eligibility` (`arrependimento_7d`, `preferencia_7d`, `defeito_30d_loja`, `garantia_legal_90d`, `ineligible_exceptions_note`). |
| **T-05** | `lookup_store_policy` | Consulta as seções normativas do Manual de Políticas e Procedimentos v2.1 (`data/políticas_da_loja.pdf`), retornando as regras oficiais sobre a loja, horários, pagamentos, trocas, frete, promoções, WhatsApp, garantia, LGPD e escopo de acessórios (`RN-01`, `RN-09`). | `topic: Literal["geral_sobre_loja", "horario_funcionamento", "formas_pagamento_parcelamento", "trocas_devolucoes_arrependimento", "frete_entregas_rastreamento", "promocoes_descontos", "atendimento_whatsapp_escopo", "garantia", "privacidade_lgpd", "todas"]` | `section_title`, `content`, `key_rules` e metadados de versão (`Versão 2.1 — Junho de 2025`). |
| **T-06** | `register_complaint_or_handover` | Registra formalmente uma reclamação, solicitação de exclusão de dados LGPD, encomenda de item sem estoque ou dúvida omissa para a gerência/atendente humano, gerando código de protocolo e informando o SLA oficial de **24 horas úteis** (`RN-13`). | `customer_identifier: str`, `category: Literal["reclamacao", "troca_devolucao", "duvida_gerencia", "lgpd_dados", "encomenda_produto"]`, `summary: str`, `order_id: Optional[int] = None` | `protocol_id` (ex.: `EMP-2026-XXXX`), `registered_at`, `sla_business_hours: 24`, `status: "FORWARDED_TO_MANAGEMENT"`, `instructions_to_agent`. |

---

## 2. Integração Externa com Provedores de LLM & Resiliência

### 2.1 Abstração Multi-Provider (`src/agent/llm_factory.py`)
Para garantir que qualquer avaliador da Artefact execute o projeto com a chave que tiver disponível, a fábrica de modelos suporta configuração via `.env`:
- **Provedor Padrão (`LLM_PROVIDER=gemini`):** `ChatGoogleGenerativeAI` (`gemini-2.5-flash` ou `gemini-2.0-flash`), com suporte nativo a Function Calling e baixa latência.
- **Provedor Alternativo 1 (`LLM_PROVIDER=openai`):** `ChatOpenAI` (`gpt-4o-mini` ou `gpt-4o`).
- **Provedor Alternativo 2 (`LLM_PROVIDER=groq`):** `ChatGroq` (`llama-3.3-70b-versatile`).

### 2.2 Políticas de Resiliência e Tolerância a Falhas (`RNF-04`)
| Parâmetro de Resiliência | Configuração Técnica | Comportamento em Caso de Falha |
| :--- | :--- | :--- |
| **Timeout de Requisição HTTP** | `timeout = 30.0s` | Cancela chamada travada e dispara tentativa de retry. |
| **Retry & Exponential Backoff** | `max_retries = 3` (Backoff `1s -> 2s -> 4s` com jitter) | Trata automaticamente erros transitórios `HTTP 429 (Rate Limit)` e `5xx`. |
| **Prevenção de Loop Infinito no Grafo** | `recursion_limit = 10` no `RunnableConfig` do LangGraph | Interrompe ciclos anômalos de chamadas repetidas de ferramentas. |
| **Fallback Gracioso ao Usuário** | Captura de exceções na borda do orquestrador | Retorna mensagem cordial pedindo para tentar novamente ou entrar em contato pelo WhatsApp `(67) 3321-4500` / `(67) 3341-4444`, sem expor *stack trace*. |
