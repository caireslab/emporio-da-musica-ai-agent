# Sub-Atividade 4.4 — Integração Contínua, Exemplos, README & Containers

> **Projeto:** Empório da Música — Conversational AI Agent  
> **Fase SDLC:** 04 — Development & Integration (`sdlc-04-development`)  
> **Status:** Concluído e Integrado

---

## 1. Entregáveis de Integração e Documentação Final

| Artefato | Caminho | Descrição |
| :--- | :--- | :--- |
| **README Principal** | [`README.md`](file:///c:/Users/Raul%20Caires/Documents/Desafio%20tecnico/Desafio%20Técnico%20AI%20Engineer/README.md) | Documentação completa do repositório cobrindo instalação, modos de execução, justificativa das decisões técnicas, tratamento de anomalias nos dados, limitações, roadmap e transparência de IA. |
| **Exemplos de Interação (1 a 5)** | [`examples/01_catalogo_violoes_ate_1000.md`](file:///c:/Users/Raul%20Caires/Documents/Desafio%20tecnico/Desafio%20Técnico%20AI%20Engineer/examples/01_catalogo_violoes_ate_1000.md) a [`examples/05_casos_especiais_homonimos_lgpd_e_escopo.md`](file:///c:/Users/Raul%20Caires/Documents/Desafio%20tecnico/Desafio%20Técnico%20AI%20Engineer/examples/05_casos_especiais_homonimos_lgpd_e_escopo.md) | 5 diálogos multi-turn demonstrando roteamento híbrido entre CSVs e Manual PDF, tool calls JSON e guardrails. |
| **Containers Docker** | [`Dockerfile`](file:///c:/Users/Raul%20Caires/Documents/Desafio%20tecnico/Desafio%20Técnico%20AI%20Engineer/Dockerfile), [`docker-compose.yml`](file:///c:/Users/Raul%20Caires/Documents/Desafio%20tecnico/Desafio%20Técnico%20AI%20Engineer/docker-compose.yml) | Serviços `emporio-cli` (Rich terminal) e `emporio-web` (Streamlit na porta `8501`). |
| **Configuração de Testes** | [`pytest.ini`](file:///c:/Users/Raul%20Caires/Documents/Desafio%20tecnico/Desafio%20Técnico%20AI%20Engineer/pytest.ini) | Configuração de `pythonpath = .` e gate de cobertura `fail_under = 80`. |

---

## 2. Verificação de Execução do Modo Demo via CLI (`python main.py --demo`)

Os 5 cenários do desafio foram validados via `run_interactive_cli(["--demo"])` e `run_interactive_cli(["--query", ...])` com código de saída `0`.
