# Sub-Atividade 4.3 — Code Review & Quality Gates

> **Projeto:** Empório da Música — Conversational AI Agent  
> **Fase SDLC:** 04 — Development & Integration (`sdlc-04-development`)  
> **Status:** Aprovado com Tolerância Zero (0 erros Ruff, 0 anti-patterns LangGraph, 0 segredos vazados)

---

## 1. Inspeção de Análise Estática e Linters (`ruff check`)

| Ferramenta | Escopo | Resultado |
| :--- | :--- | :--- |
| **Ruff (`ruff check`)** | `src/`, `tests/`, `main.py`, `app.py` | `All checks passed! (0 errors)` |
| **LangGraph Linter (`validate_graph.py`)** | `src/agent/graph.py` | `✅ Nenhum anti-pattern de LangGraph detectado!` |
| **Auditoria de Segredos** | Todo o repositório Git | `0 chaves hardcoded` (apenas `.env.example` versionado; `.env` protegido no `.gitignore`) |

---

## 2. Auditoria de Fronteiras Clean Architecture & Segurança OWASP LLM

1. **Desacoplamento de Camadas:**
   - `src/domain/models.py` e `src/domain/rules.py` são 100% puros (dependem apenas da biblioteca padrão e `pydantic`), sem qualquer importação de `langchain`, `langgraph` ou `streamlit`.
   - `src/data/repository.py` e `src/data/policy_kb.py` encapsulam toda a leitura Read-Only de `data/*.csv` e `data/políticas_da_loja.pdf`.
   - `src/tools/store_tools.py` atua como camada de adaptadores `@tool` com validação estrita de entrada via `args_schema` Pydantic v2.
   - `src/agent/graph.py` orquestra o `StateGraph` com `MemorySaver` e proteção de recursão (`iteration_count <= 8`, `recursion_limit = 15`).
2. **Conformidade OWASP Top 10 for LLM Applications (2025):**
   - **LLM01 (Prompt Injection):** Filtro heurístico em `agent_node` + isolamento do System Prompt e tools tipadas sem `eval`/`exec`/SQL dinâmico.
   - **LLM02 (Sensitive Information Disclosure / LGPD):** Bloqueio automático `AMBIGUOUS_HOMONYM_DETECTED` para clientes homônimos (`Bruno Martins` IDs 11/43 e `Diego Castro` IDs 13/47) até que o cliente informe um segundo verificador.
   - **LLM06 (Excessive Agency):** Repositório estritamente Read-Only sobre os CSVs originais; todas as regras financeiras são calculadas em Python determinístico.
