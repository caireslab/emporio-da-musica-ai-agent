# GEMINI.md — Contrato Operacional & Governança Local (Emporio da Musica AI Agent)

> **Herança:** Este repositório herda o fluxo SDLC, Stage Gates e postura `/grill-me` do `GEMINI.md` Global (`~/.gemini/config/GEMINI.md`). Este documento define as invariantes verificáveis e o protocolo de execução local.

---

## 1. Contexto do Produto & Roteamento de Ciclo (SDLC)
* **Sistema:** Emporio da Musica AI Agent — Agente conversacional de atendimento ao cliente para a loja de instrumentos musicais Emporio da Musica (Desafio Tecnico AI Engineer - Artefact)
* **Estágio Atual do SDLC:** <!-- SDLC_PHASE_STATUS_START -->`Fase 05 — Validation & Quality`<!-- SDLC_PHASE_STATUS_END -->
* **Matriz de Classificação & Roteamento de Demandas (Auto-Routing):**

| Tipo (Intent) | Palavras-Chave / Gatilho | Target SDLC Skill / Workflow | Comportamento Esperado neste Repositório |
| :--- | :--- | :--- | :--- |
| **NEW_PROJECT / PIVOT** | "do zero", "novo módulo", "pivotagem" | ➔ `sdlc-01-discovery` | Seguir sequência estrita Gates `01 ➔ 02 ➔ 02.5 ➔ 03 ➔ 04 ➔ 05 ➔ 06`. |
| **NEW_FEATURE** | "nova implementação", "feature completa", "evolução" | ➔ `sdlc-02-requirements` | Iniciar em Requisitos (`SRS`) e avançar por `02.5 ➔ 03` antes de codificar em `04`. |
| **DESIGN_UI** | "desenhe", "UI", "UX", "tela", "dashboard", "tokens" | ➔ `sdlc-02.5-solution-design` (+ `frontend-design`) | Atualizar User Flows, tokens W3C DTCG/OKLCH, wireframes e auditoria WCAG 2.2 AA (`UXD`). |
| **COMPLEX_CODE** | "crie a lógica", "refatore o sistema", "implemente backend" | ➔ `graphify-update` ➔ `sdlc-03-architecture` ➔ `sdlc-04-development` | Mapear blast radius, validar `SAD`, implementar em `04` e validar em `05`. |
| **AI_AGENT** | "crie um agente", "chatbot", "LangGraph", "RAG", "evals" | ➔ Gate Ativo + `langgraph-dev` + `deepeval` / `deepeval-tracing` | Combinar a fase SDLC ativa com grafos de estado (`langgraph-dev`) e suíte `deepeval`. |
| **SIMPLE_CODE** | "corrija o bug pontual", "ajuste o botão", "refatore arquivo X" | **Edição Direta (Tier 1 — Fast-Track)** | *Bypass do FSM documental (pós-Gate 03/04).* Edição cirúrgica + execução obrigatória da Seção 4. |
| **SURVEY** | "analise", "liste arquivos", "varredura", "diagnóstico" | **Explorer (Tier 0 — Read-Only)** | *Bypass do FSM.* Leitura e diagnóstico de contexto local apenas. Zero edições. |
| **QUESTION** | "o que é", "como funciona", "explique" | **Conceitual (Tier 0 — Direct Answer)** | *Bypass do FSM.* Resposta puramente textual e informativa. |

---

## 2. Mapa de Artefatos Mestres (Leitura Sob Demanda)
Carregue via `read_file` **apenas** o artefato exigido pela tarefa ativa (nunca leia todos simultaneamente):
<!-- SDLC_ARTIFACTS_TABLE_START -->
| Fase / Gate | Artefato Mestre | Status |
| :--- | :--- | :--- |
| **Gate 01 (Discovery)** | `docs/discovery/PRODUCT_DISCOVERY_VISION.md` | ✅ Consolidado |
| **Gate 02 (Requirements)** | `docs/requirements/SRS_SOFTWARE_REQUIREMENTS_SPECIFICATION.md` | ✅ Consolidado |
| **Gate 02.5 (UI/UX & Tokens)** | `docs/design/UXD_USER_EXPERIENCE_DESIGN_SPECIFICATION.md` | ✅ Consolidado |
| **Gate 03 (Architecture)** | `docs/architecture/SAD_SOLUTION_ARCHITECTURE_DOCUMENT.md` | ✅ Consolidado |
| **Gate 04 (Development)** | `docs/development/WSI_WORKING_SOFTWARE_INCREMENT.md` | ✅ Consolidado |
| **Gate 05 (Validation)** | `docs/validation/QVR_QUALITY_VALIDATION_REPORT.md` | 🔄 Em Andamento |
| **Gate 06 (Release)** | `docs/release/PRER_PRODUCTION_RELEASE_EVOLUTION_REPORT.md` | ⏳ Pendente |
<!-- SDLC_ARTIFACTS_TABLE_END -->

---

## 3. Contratos Arquiteturais & Regras de Fronteira
Qualquer edição de código deve respeitar a matriz de diretórios e dependências abaixo:

<!-- SDLC_ARCH_CONTRACTS_START -->
| Camada / Diretório | Responsabilidade | Restrição Estrita (Proibido) |
| :--- | :--- | :--- |
| `docs/` | Artefatos formais das 7 fases do SDLC. | Proibido criar documentos soltos fora das subpastas de fase. |
| ` Workspace Root` | Configuração e governança (`GEMINI.md`). | **TRAVA DE PRÉ-ARQUITETURA:** Proibido criar código-fonte (`.js`, `.ts`, `.py`, `.go`) antes da aprovação formal do **Gate 03 (`SAD`)**. |
<!-- SDLC_ARCH_CONTRACTS_END -->

---

## 4. Protocolo de Verificação & Prevenção de Regressões (Obrigatório)
O agente **NÃO PODE** declarar uma entrega técnica ou documental concluída sem executar a bateria de verificação abaixo no PowerShell e comprovar `Exit Code 0`:

<!-- SDLC_VERIFICATION_START -->
### 4.1 Auditoria Determinística de Pré-Arquitetura (Fases 01 a 03)
```powershell
# Verifica ausência de implementação prematura antes da aprovação do Gate 03 (SAD)
if (-not (Test-Path "docs/architecture/SAD_SOLUTION_ARCHITECTURE_DOCUMENT.md")) {
    $prematureCode = Get-ChildItem -Path . -Include *.js,*.ts,*.tsx,*.py,*.go,*.rs,*.java -Recurse -File -ErrorAction SilentlyContinue |
        Where-Object { $_.FullName -notmatch "\\(\.gemini|\.git|node_modules|venv|\.venv|tests)\\" }
    if ($prematureCode) {
        throw "VIOLACAO_ZERO_PREMATURE_CODE: Codigo de aplicacao detectado antes do Gate 03!"
    }
}
Write-Output "GUARDRAIL_PRE_ARCH_OK"
```
<!-- SDLC_VERIFICATION_END -->

---

## 5. Definição de Pronto (DoD) para o Agente
Ao finalizar qualquer tarefa técnica ou documental neste repositório, o agente deve apresentar no resumo final:
1. **Arquivos criados/modificados** com links clicáveis e camada arquitetural afetada.
2. **Evidência de execução** dos checks da Seção 4 (`Exit Code 0`).
3. **Sincronização documental:** Se um contrato de API, schema de banco, token visual ou Gate mudou, atualizar o respectivo artefato em `docs/` e sincronizar este contrato (`python "C:\Users\Raul Caires\.gemini\config\scripts\sdlc_workspace_bootstrap.py" --workspace . --sync`).
