# Sub-Atividade 5.4 — Gestão de Defeitos, Correção e Reteste

> **Projeto:** Empório da Música — Conversational AI Agent  
> **Fase SDLC:** 05 — Validation & Quality (`sdlc-05-validation`)  
> **Status:** 0 Defeitos Abertos (100% Corrigidos e Retestados)

---

## 1. Registro de Defeitos Detectados e Corrigidos Durante o Ciclo

| ID do Defeito | Descrição Técnica | Severidade | Correção Aplicada | Status de Reteste |
| :--- | :--- | :--- | :--- | :--- |
| **BUG-01** | `ModuleNotFoundError: No module named 'src'` ao invocar `pytest` sem `PYTHONPATH=.` configurado no Windows. | Média | Criado arquivo [`pytest.ini`](file:///c:/Users/Raul%20Caires/Documents/Desafio%20tecnico/Desafio%20Técnico%20AI%20Engineer/pytest.ini) na raiz com `pythonpath = .` e `fail_under = 80`. | ✅ CORRIGIDO & RETESTADO (`15 passed`) |
| **BUG-02** | `datetime.now()` sem timezone explícito em `StoreRepository.register_protocol` apontado pela regra `DTZ005` do linter `ruff`. | Baixa | Substituído por `datetime.now(tz=UTC).isoformat(timespec="seconds")` em [`src/data/repository.py`](file:///c:/Users/Raul%20Caires/Documents/Desafio%20tecnico/Desafio%20Técnico%20AI%20Engineer/src/data/repository.py#L696). | ✅ CORRIGIDO & RETESTADO (`All checks passed!`) |

---

## 2. Resumo por Severidade

| Severidade | Encontrados | Corrigidos | Retestados | Em Aberto |
| :--- | :--- | :--- | :--- | :--- |
| **Crítico (Blocker)** | 0 | 0 | 0 | **0** |
| **Alto** | 0 | 0 | 0 | **0** |
| **Médio** | 1 | 1 | 1 | **0** |
| **Baixo** | 1 | 1 | 1 | **0** |
| **Total** | **2** | **2** | **2** | **0** |
