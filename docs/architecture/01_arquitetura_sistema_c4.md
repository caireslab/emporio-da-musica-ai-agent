# 01 — Arquitetura de Sistemas, C4 Model e Topologia

> **Status:** Validado  
> **Data:** 2026-11-02  
> **Artefato:** `docs/architecture/01_arquitetura_sistema_c4.md`  

---

## 1. Visão Arquitetural e Estilo Adotado
O **Empório da Música AI Agent** adota o estilo **Monólito Modular Orientado a Agentes (Clean Architecture + LangGraph v0.3 StateGraph)** em **Python 3.12+**.

### Motivação de Engenharia (Zero-Friction Evaluation):
1. **Execução Imediata pelo Avaliador:** O avaliador da Artefact pode clonar o repositório, configurar a chave de API no `.env` e executar a CLI ou a Web UI (Streamlit) imediatamente com um único comando, sem depender de provisionamento de clusters externos.
2. **Desacoplamento Estrito de Camadas:** O núcleo de regras de negócio e higienização de dados (`src/domain` e `src/data`) é 100% independente do framework de LLM (`src/agent`) e das interfaces de apresentação (`src/ui` / `main.py`).
3. **Containerização Opcional (`Dockerfile` + `docker-compose.yml`):** Fornecida na raiz para reprodutibilidade determinística em qualquer SO (`python:3.12-slim`).

---

## 2. Diagramas C4 Model (Mermaid)

### 2.1 C4 Nível 1 — Diagrama de Contexto do Sistema
```mermaid
flowchart TD
    Cliente["👤 Cliente da Empório da Música\n(Músico Iniciante a Profissional / Pós-Venda)"]
    Avaliador["👤 Avaliador Artefact / Equipe Interna\n(Auditoria de Conversas & Tool Calls)"]
    
    subgraph Boundary["Sistema: Empório da Música AI Agent (Python 3.12+)"]
        AgentSystem["🤖 Assistente Virtual Empório da Música\n(Orquestrador LangGraph + Motor Comercial & Políticas)"]
    end

    LLMProvider["☁️ Provedor de Inferência LLM\n(Google Gemini / OpenAI / Groq via HTTPS)"]
    LocalData[("📂 Base Operacional & Normativa Local\n(data/*.csv + data/políticas_da_loja.pdf)")]

    Cliente -->|"Envia dúvidas de catálogo, preços, pedidos e políticas"| AgentSystem
    Avaliador -->|"Testa cenários via CLI / Streamlit UI e inspeciona Tool Calls"| AgentSystem
    AgentSystem -->|"Invoca Function Calling estruturado (Retry/Backoff)"| LLMProvider
    AgentSystem -->|"Leitura Read-Only & Higienização em Memória"| LocalData
```

### 2.2 C4 Nível 2 — Diagrama de Containers e Módulos Executáveis
```mermaid
flowchart TB
    User["👤 Usuário / Avaliador"]

    subgraph AppHost["Ambiente de Execução (Local Python venv / Container Docker python:3.12-slim)"]
        CLI["💻 Container: CLI Interativa\n(main.py / Rich Terminal)\nConversa multi-turn no terminal"]
        WebUI["🌐 Container: Web UI & Tool Inspector\n(Streamlit App - app.py)\nInterface de chat + visualização de Tool Calls"]
        
        subgraph CoreEngine["🧠 Container: Agentic Core & Application Layer (src/)"]
            LangGraphOrch["Orquestrador de Grafo de Estado\n(LangGraph v0.3 StateGraph + MemorySaver)"]
            ToolsLayer["Camada de Tools Tipadas (Pydantic v2)\n1. search_products_catalog\n2. get_product_pricing_and_payment\n3. calculate_shipping_info\n4. inspect_customer_order_and_return\n5. lookup_store_policy\n6. register_complaint_or_handover"]
            DomainServices["Motor de Regras de Negócio & Sanitização\n(Cálculo PIX/Promo, Parcelas, Prazos CDC 7d/30d/90d, Desambiguação LGPD)"]
        end

        subgraph DataStore["🗄️ Container: In-Memory Data Store & Knowledge Base"]
            RelationalStore[("Catálogo, Clientes, Pedidos & Promoções\n(Pydantic Models / SQLite In-Memory Read-Only)")]
            PolicyIndex[("Índice Estruturado de Políticas v2.1\n(Seções 1 a 10 extraídas de políticas_da_loja.pdf)")]
            ProtocolLog[("Log de Protocolos & Ouvidoria\n(Memória / JSONL de Sessão)")]
        end
    end

    ExternalLLM["☁️ API Externa de LLM\n(Gemini 2.5 Flash / GPT-4o-mini / Llama-3.3-70b)"]

    User -->|"Interage via Terminal"| CLI
    User -->|"Interage via Browser (Porta 8501)"| WebUI
    CLI -->|"Envia (mensagem, thread_id)"| LangGraphOrch
    WebUI -->|"Envia (mensagem, thread_id)"| LangGraphOrch
    LangGraphOrch <-->|"Tool Calling / Structured JSON"| ExternalLLM
    LangGraphOrch -->|"Executa Tools Validadas"| ToolsLayer
    ToolsLayer -->|"Aplica Regras RN-01 a RN-13"| DomainServices
    DomainServices -->|"Consulta Read-Only"| RelationalStore
    DomainServices -->|"Recupera Seções Normativas"| PolicyIndex
    DomainServices -->|"Registra Reclamação (SLA 24h)"| ProtocolLog
```

---

## 3. Topologia Física e Especificação de Containers

| Componente / Serviço | Runtime / Imagem Base | Porta Padrão | Persistência / Volumes | Responsabilidade Técnica |
| :--- | :--- | :--- | :--- | :--- |
| **`emporio-cli`** | `python:3.12-slim` (ou `venv` local) | N/A (STDIO) | `./data:/app/data:ro` (Read-Only) | Interface de linha de comando interativa e executor de cenários de demonstração. |
| **`emporio-web`** | `python:3.12-slim` (`streamlit run`) | `8501:8501` | `./data:/app/data:ro` (Read-Only) | Interface gráfica web com chat multi-turn, seletor de cenários de exemplo e inspetor de chamadas de ferramentas. |
| **`data-volume`** | Sistema de Arquivos Local | N/A | `data/*.csv` e `data/políticas_da_loja.pdf` | Montado estritamente como leitura (`ro`) para garantir a invariante de não-mutação dos dados originais. |
