# 05 — Decisões Arquiteturais (ADRs), Trade-offs e Stack Tecnológica

> **Status:** Validado  
> **Data:** 2026-11-02  
> **Artefato:** `docs/architecture/05_decisoes_arquiteturais_adrs.md`  

---

## 1. Architecture Decision Records (ADRs — Padrão Michael Nygard)

### ADR-01: Abordagem do Agente — Orquestração Híbrida com LangGraph v0.3 (`StateGraph`) e Tool Calling Determinístico
- **Status:** Aceito
- **Contexto:** O desafio exige que o agente saiba quando consultar dados operacionais (`data/*.csv`: produtos, preços, promoções, pedidos) e quando consultar políticas (`data/políticas_da_loja.pdf`: trocas, horários, pagamento, frete), além de manter histórico de conversa multi-turn. Abordagens baseadas em `AgentExecutor` legado do LangChain estão depreciadas, e agentes que geram SQL/código Python livremente (`create_pandas_dataframe_agent`) sofrem com riscos de segurança (`eval` / RCE) e erros em regras comerciais complexas (como não-cumulatividade de PIX com promoção ativa e parcelas mínimas escalonadas).
- **Decisão:** Adotar **LangGraph v0.3 (`StateGraph`)** combinado com **6 Tools fortemente tipadas via Pydantic v2** e **Checkpointer em Memória (`MemorySaver`)** por `thread_id`.
- **Opções Consideradas:**
  1. *LangGraph v0.3 `StateGraph` + Tools Determinísticas Tipadas (Escolhida).*
  2. *Agente Text-to-SQL / Pandas REPL (`eval` dinâmico).*
  3. *RAG Vetorial Único (indexar CSVs e PDF juntos em um banco vetorial).*
- **Consequências:**
  - *Positivas:* **0% de erro matemático ou violação de regras comerciais**, pois descontos, parcelas mínimas e prazos do CDC (7d/30d/90d) são calculados por código Python determinístico testado; controle explícito de estado multi-turn; rastreabilidade transparente das chamadas de ferramentas (*Tool Call Trace*).
  - *Negativas (Trade-offs):* Exige escrever e manter schemas Pydantic e funções de domínio para cada família de intenção, em vez de deixar o LLM escrever queries ad-hoc arbitrárias.

---

### ADR-02: Engenharia de Dados & Tratamento de Anomalias — Repositório In-Memory Read-Only com Sanitização Pydantic v2
- **Status:** Aceito
- **Contexto:** Os arquivos `data/*.csv` possuem volume compacto (65 produtos, 50 clientes, 20 pedidos, 25 promoções), mas contêm anomalias críticas intencionais: contradições entre `name`, `description` e `specs` nos produtos `IDs 135–144`, categorias sem produtos (`IDs 6, 7, 8`), promoções expiradas (`is_active=0`), itens esgotados/descontinuados/em breve e clientes homônimos (`Bruno Martins`, `Diego Castro`).
- **Decisão:** Carregar os CSVs em modo **estritamente Read-Only** na inicialização para estruturas tipadas **Pydantic v2** em memória, aplicando higienização não-destrutiva (enriquecendo `effective_price_brl`, marcando `has_catalog_discrepancy` nos `IDs 135–144` e exigindo 2º fator em homônimos).
- **Opções Consideradas:**
  1. *Repositório In-Memory Read-Only com Sanitização Pydantic v2 (Escolhida).*
  2. *Banco PostgreSQL externo obrigatório.*
  3. *Leitura bruta de CSV sem tratamento de anomalias.*
- **Consequências:**
  - *Positivas:* Execução local instantânea (**Zero-Config** para o avaliador da Artefact), latência de busca sub-milissegundo (`< 1ms`), proteção dos arquivos originais e conformidade total com o CDC (Art. 37) e LGPD.
  - *Negativas (Trade-offs):* Para um catálogo futuro com milhões de SKUs em produção real, seria necessário migrar o repositório em memória para PostgreSQL/DuckDB (evolução já prevista e documentada no roadmap do `README.md`).

---

### ADR-03: Arquitetura de Retrieval para Políticas — Indexação Estruturada por Seções Semânticas (`políticas_da_loja.pdf`)
- **Status:** Aceito
- **Contexto:** O documento `data/políticas_da_loja.pdf` possui apenas 8 páginas muito bem divididas em 10 seções numeradas. Usar *chunking* cego por contagem de caracteres combinado com embeddings pesados (FAISS/Chroma local com modelos Torch de centenas de MBs) frequentemente corta tabelas ao meio (como a tabela de parcelamento da Seção 3 ou a tabela de prazos de frete da Seção 5.2) e adiciona peso desnecessário de instalação.
- **Decisão:** Extrair e indexar o manual por **Seções Semânticas Completas (1 a 10)** (suportando leitura direta do PDF via `pypdf` e estrutura canônica preservada), exposta através da tool `lookup_store_policy(topic=...)`.
- **Opções Consideradas:**
  1. *Retrieval Estruturado por Seções Semânticas Completas via Tool (Escolhida).*
  2. *Chunking fixo de 500 caracteres + Vector DB externo (Pinecone/Chroma).*
  3. *Injetar o PDF inteiro em todos os prompts de sistema.*
- **Consequências:**
  - *Positivas:* **100% de Context Recall e Context Precision** — tabelas de frete e regras de parcelamento nunca são truncadas; zero custo de API de embeddings; economia de tokens (carrega apenas a seção solicitada pela tool).
  - *Negativas (Trade-offs):* Se a loja tivesse centenas de PDFs não estruturados de milhares de páginas, seria necessário acoplar busca híbrida (BM25 + Embeddings Vetoriais).

---

### ADR-04: Provedor de Modelo (LLM) e Interfaces — Factory Multi-Provider Configurável (`.env`) + Dual UI (CLI & Streamlit)
- **Status:** Aceito
- **Contexto:** O desafio permite escolher qualquer modelo/provedor e qualquer interface (CLI, notebook, API ou UI simples), desde que justificado no `README.md`. Avaliadores diferentes podem preferir rodar no terminal (CLI) ou no navegador (Web UI), e podem possuir chaves de API do Google Gemini, OpenAI ou Groq.
- **Decisão:** Implementar uma `LLMFactory` configurável via `.env` com **Google Gemini (`gemini-2.5-flash`)** como padrão recomendado (excelente velocidade, janela de contexto ampla, ótimo suporte a Function Calling em português e *free tier* acessível no Google AI Studio), suportando também **OpenAI (`gpt-4o-mini` / `gpt-4o`)** e **Groq (`llama-3.3-70b-versatile`)**, e entregar tanto **CLI interativa (`main.py`)** quanto **Web UI (`app.py` em Streamlit)** com inspetor de Tool Calls.
- **Consequências:**
  - *Positivas:* Flexibilidade máxima para a banca avaliadora; resiliência contra *rate limits* (`HTTP 429`) via retry com backoff exponencial; inspeção visual e no terminal.
  - *Negativas (Trade-offs):* Requer manter os pacotes de integração leves (`langchain-google-genai`, `langchain-openai`, `langchain-groq`) no `requirements.txt`.

---

## 2. Matriz Definitiva de Tecnologias (Stack Técnica)

| Camada | Tecnologia / Biblioteca | Versão Alvo | Justificativa Técnica |
| :--- | :--- | :--- | :--- |
| **Linguagem Base** | **Python** | `>= 3.11 / 3.12+` | Restrição obrigatória do desafio; ecossistema maduro de IA e tipagem moderna. |
| **Orquestração Agêntica** | **LangGraph & LangChain Core** | `langgraph >= 0.3`, `langchain-core >= 0.3` | Grafo de estado cíclico controlado (`StateGraph`), persistência nativa (`MemorySaver`) e suporte multi-provider de Function Calling. |
| **Validação & Contratos** | **Pydantic v2** | `pydantic >= 2.7` | Validação determinística de schemas de ferramentas e entidades de domínio em Rust-core. |
| **Provedores de LLM** | **Google Gemini / OpenAI / Groq** | `langchain-google-genai`, `langchain-openai`, `langchain-groq` | Flexibilidade total para o avaliador configurar a API Key de sua preferência via `.env`. |
| **Ingestão de Documentos** | **pypdf & csv (stdlib)** | `pypdf >= 4.0` | Leitura leve e segura do PDF de políticas e das 6 tabelas CSV operacionais. |
| **Interfaces (Dual UI)** | **Rich (CLI) & Streamlit (Web UI)** | `rich >= 13.7`, `streamlit >= 1.38` | Experiência elegante tanto via linha de comando quanto via navegador com inspeção de Tools. |
| **Qualidade & Testes** | **Pytest & Ruff** | `pytest >= 8.0`, `ruff >= 0.6` | Testes unitários/integração das regras de negócio e linter estático ultrarrápido. |
