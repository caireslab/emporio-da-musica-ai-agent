# Artefato 1.4 — Análise Inicial de Riscos, Restrições & Dependências

> **Iniciativa / Projeto:** Empório da Música AI Agent (Desafio Técnico AI Engineer — Artefact)  
> **Data:** 2026-11-02  
> **Facilitador:** Antigravity (SDLC Master Orchestrator)  

---

## 1. Auditoria Regulatória & Limitações de Dependências Externas (Web Research)
*Achados obtidos via `search_web` sobre normas ativas, leis recentes e status de parceiros terceiros:*
- **Marco Legal / Diretrizes de Compliance Vigentes:**
  - **Código de Defesa do Consumidor (Lei nº 8.078/1990):**
    - *Art. 30 e Art. 37 (Vinculação da Oferta e Publicidade Enganosa):* Proíbe induzir o consumidor a erro quanto à marca, características, preço, desconto ou estoque. Exige tratamento ativo das inconsistências nos produtos `IDs 135–144` e verificação estrita de `is_active == 1` em promoções.
    - *Art. 49 e Decreto nº 7.962/2013 (Direito de Arrependimento no E-commerce):* 7 dias corridos após o recebimento sem justificativa, reembolso integral (até 10 dias úteis na política da loja) e frete reverso por conta da loja.
    - *Art. 26 (Garantia Legal):* 90 dias contra defeitos de fabricação (alinhado à Seção 8.1 do Manual, sendo os primeiros 30 dias com troca direta na loja conforme Seção 4.2).
  - **Lei Geral de Proteção de Dados (LGPD — Lei nº 13.709/2018):**
    - Proteção contra vazamento de dados pessoais (`name`, `phone`, `email`, `city`, histórico de compras em `customers.csv` e `orders.csv`). Exige desambiguação de identidade quando houver homônimos ou múltiplos registros.
- **Auditoria de Fornecedores / APIs Terceiras e Segurança de Agentes (OWASP Top 10 for LLM):**
  - **Limites de Taxa de Provedores LLM (RPM / TPM / Free Tier `429 Too Many Requests`):** APIs gratuitas ou de desenvolvedor (Google Gemini Developer API, Groq Free Tier, OpenAI Tier 1) aplicam limites estritos de requisições por minuto (RPM) e tokens por minuto (TPM). É mandatório implementar *Exponential Backoff com Jitter* e configuração flexível de provedor/modelo via variáveis de ambiente (`.env`).
  - **Vulnerabilidades OWASP LLM01 (Prompt Injection) & Execução Insegura em CSV/Pandas:** Agentes que utilizam `eval()`, `exec()`, `create_pandas_dataframe_agent(..., allow_dangerous_code=True)` ou SQL dinâmico sem parametrização sofrem risco crítico de Execução Remota de Código (RCE) e exfiltração de toda a base de clientes. A mitigação padrão da indústria é o uso exclusivo de **Structured Tool Calling (Pydantic Schemas) Read-Only** sobre funções determinísticas em Python.
- **Fontes Oficiais & Documentações Consultadas:**
  - *OWASP Top 10 for Large Language Model Applications (LLM01: Prompt Injection, LLM07: Insecure Plugin/Tool Design)*.
  - *Práticas de Resiliência de APIs LLM (LiteLLM / MLflow / Cloud Architecture 2025/2026)*: Exponential Backoff, Token Budgeting e Multi-Provider Configuration.
  - *Legislação Brasileira (Planalto.gov.br — Lei nº 8.078/90 CDC e Lei nº 13.709/18 LGPD)*.

---

## 2. Restrições Não Negociáveis do Projeto
- **Restrições Tecnológicas Obrigatórias (Enunciado Artefact):**
  - **Python** como linguagem principal obrigatória.
  - Consumo exclusivo dos materiais fornecidos em `data/*.csv` e `data/políticas_da_loja.pdf`.
- **Restrições de Entrega e Repositório:**
  - Repositório Git público com **histórico de commits real e incremental** (proibido `git push --force` de commit único).
  - Presença obrigatória do `README.md` justificando todas as decisões técnicas e de **3 a 5 exemplos de interação** cobrindo casos triviais e não-triviais.
- **Restrições Regulatórias e de Segurança Operacional:**
  - Proibição de execução de código arbitrário gerado por LLM (`eval`/`exec`) sobre os CSVs.
  - Proibição de exposição de chaves de API (`GEMINI_API_KEY`, `OPENAI_API_KEY`, etc.) no histórico Git (uso obrigatório de `.env` + `.env.example` + `.gitignore`).

---

## 3. Mapeamento de Dependências Críticas

| Dependência | Tipo (Interna / Externa) | Responsável / Fornecedor | Impacto no Projeto | Status Atual / Ação Necessária |
| :--- | :--- | :--- | :--- | :--- |
| **API de Provedor LLM (Gemini / OpenAI / Groq)** | Externa | Google / OpenAI / Groq | Bloqueante para raciocínio e geração de linguagem natural do agente | Mitigado via suporte configurável por `.env` + retries com backoff exponencial |
| **Base de Dados Operacional (`data/*.csv`)** | Interna (Local) | Empório da Música / Artefact | Crítico para consulta de produtos, promoções, clientes e pedidos | Arquivos presentes; exige camada de sanitização e indexação em memória na inicialização |
| **Manual de Políticas (`data/políticas_da_loja.pdf`)** | Interna (Local) | Empório da Música / Artefact | Crítico para regras normativas (horários, pagamentos, trocas, frete, garantia) | Arquivo presente (8 páginas); texto extraído e estruturado semanticamente por seções |

---

## 4. Matriz de Análise Inicial de Riscos

| ID | Categoria | Descrição do Risco | Prob. (A/M/B) | Imp. (A/M/B) | Severidade | Ação Preventiva / Mitigação Inicial | Plano de Contingência |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **R01** | **Negócio / Legal (CDC Art. 37)** | O agente informar marcas ou especificações contraditórias dos produtos `IDs 135–144` (ex.: nome `Music Man` e descrição `Fender Jazz Bass`) ou prometer promoção expirada (`is_active=0`). | Alta | Alto | **Crítica** | Higienizar e enriquecer os registros `135–144` na camada de dados (priorizando `name` e sinalizando a divergência de cadastro) e filtrar promoções por `is_active == 1` com aviso explícito quando expiradas. | Documentar a anomalia dos dados brutos em seção de destaque no `README.md`. |
| **R02** | **Negócio / Financeiro** | O LLM errar contas de cabeça ao calcular desconto de PIX (5%), acumular PIX com promoção ativa (proibido na Seção 6.2) ou violar a parcela mínima escalonada (R\$ 50 / R\$ 80 / R\$ 100). | Média | Alto | **Alta** | Implementar o cálculo financeiro de PIX, desconto promocional e tabela de parcelas válidas **dentro de uma Tool Python determinística**, entregando os valores já calculados ao LLM. | Testes unitários (`pytest`) cobrindo todas as faixas de parcelamento e não-cumulatividade. |
| **R03** | **Legal / Privacidade (LGPD)** | Vazamento de dados de pedidos entre homônimos (`Bruno Martins` IDs 11 e 43; `Diego Castro` IDs 13 e 47) ao buscar apenas pelo primeiro nome. | Média | Alto | **Alta** | A tool de consulta de pedidos exigirá confirmação de um segundo fator (`order_id`, telefone, e-mail ou cidade) quando houver ambiguidade ou busca por nome. | Retornar solicitação amigável de confirmação antes de exibir `tracking_code` ou `total_brl`. |
| **R04** | **Segurança (OWASP LLM01)** | Uso de interpretador Python/Pandas dinâmico (`eval`) permitir execução remota de código ou Prompt Injection. | Baixa | Alto | **Alta** | Proibir `eval`/`exec` e usar exclusivamente **Tools tipadas com Pydantic** e operações seguras Read-Only em memória. | Validação estrita de argumentos de entrada nas tools. |
| **R05** | **Técnico / Operacional** | O avaliador da Artefact enfrentar erro de cota (`429 Rate Limit`) ou não possuir chave de um provedor específico ao testar o repositório. | Média | Médio | **Média** | Suportar múltiplos provedores via `.env` (ex.: Google Gemini como padrão gratuito/acessível + suporte a OpenAI/Groq) e incluir script de verificação e exemplos pré-gerados. | Retries automáticos e mensagens de erro claras de configuração de `.env`. |

---

## 5. Recomendações para as Próximas Fases (Requisitos & Arquitetura)
- [x] **Formalizar Regras de Negócio Determinísticas na Fase 02 (`SRS`):** Especificar todas as fórmulas de cálculo (PIX, promoções, parcelamento, frete por cidade e prazos de troca) e critérios BDD/Gherkin.
- [x] **Projetar Tools Tipadas Read-Only e Grafo do Agente na Fase 03 (`SAD`):** Desenhar o fluxo de decisão híbrido (LangGraph / Function Calling) separando claramente dados estruturados (`data/*.csv`) e conhecimento normativo (`políticas_da_loja.pdf`).
