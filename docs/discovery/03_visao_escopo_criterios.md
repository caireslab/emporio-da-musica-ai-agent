# Artefato 1.3 — Visão de Produto, Escopo & Critérios de Sucesso

> **Iniciativa / Projeto:** Empório da Música AI Agent (Desafio Técnico AI Engineer — Artefact)  
> **Data:** 2026-11-02  
> **Facilitador:** Antigravity (SDLC Master Orchestrator)  

---

## 1. Declaração de Visão do Produto (Elevator Pitch)

> **Para** clientes músicos (iniciantes a profissionais) e a equipe de atendimento da Empório da Música em Campo Grande/MS,  
> **Que** enfrentam filas de espera no WhatsApp e riscos de inconsistência comercial ao consultar preços, estoques, status de pedidos e regras de políticas manualmente,  
> **O** **Empório da Música AI Agent**  
> **É um** assistente virtual conversacional inteligente em Python com arquitetura híbrida (Tool Calling determinístico + Recuperação de Políticas),  
> **Que** responde em segundos com o acolhimento de *"um amigo que entende de música"*, cruzando em tempo real o catálogo higienizado, promoções vigentes e pedidos (`data/*.csv`) com o Manual de Políticas e Procedimentos (`data/políticas_da_loja.pdf`).  
> **Diferente de** chatbots de árvore rígida ou LLMs puros sujeitos a alucinações de preços e regras do CDC,  
> **Nosso produto** garante 100% de precisão factual (zero propaganda enganosa), aplica regras financeiras determinísticas (não-cumulatividade de PIX 5% com promoções, parcelas mínimas escalonadas e cálculo de frete), protege a privacidade contra homônimos (LGPD) e redireciona demandas fora de escopo com elegância.

---

## 2. Benchmarks de Mercado para o Escopo Inicial (Web Research)
*Achados de mercado obtidos via `search_web` sobre MVPs de Agentes de Suporte E-commerce e métricas de engenharia de IA:*
- **Padrões de Escopo Inicial no Setor (AI Customer Support MVP):**
  - Os MVPs de maior sucesso no varejo combinam **Transactional Data Lookup (Tool Use Read-Only)** para busca de produtos, cálculo de condições comerciais e rastreamento de pedidos com **Knowledge Base Retrieval (RAG / Contexto Estruturado)** para políticas de troca, frete e garantia, além de **Memória de Conversa Multi-Turn** e **Transbordo Humano (Handoff)** estruturado.
- **Funcionalidades Tipicamente Postergadas (Anti-Bloat):**
  - Execução autônoma de estornos financeiros, geração direta de etiquetas postais nos Correios/Jadlog, mutação destrutiva no banco de dados de produção (baixa de estoque ou cancelamento irreversível via chat), integrações de voz/telefonia e fine-tuning de pesos de modelos.
- **Métricas Técnicas de Engenharia de Agentes (DeepEval / RAGAS / BFCL):**
  - Avaliação objetiva baseada em **Tool Correctness** (seleção exata da ferramenta e argumentos), **Faithfulness / Groundedness** (> 95% de aderência estrita aos dados retornados pelas tools sem inventar fatos) e **Answer Relevancy**.
- **Fontes / Análises de Mercado Consultadas:**
  - *Helply / Kim.cc / Aissist.io (2025/2026)*: E-commerce AI Support MVP Scope & Containment Benchmarks (50%–75% containment, < 3s First Response Time, < 3% Hallucination Rate).
  - *Confident AI (DeepEval) & Berkeley Function Calling Leaderboard (BFCL)*: Métricas padrão de avaliação de agentes com chamada de ferramentas e fidelidade ao contexto.

---

## 3. Escopo Inicial (In-Scope — MVP)
*Capacidades indispensáveis para cumprir e superar todos os critérios do Desafio Técnico Artefact:*
- [x] **Capacidade 1 — Persona & Guardrails Conversacionais:** Assumir o tom informal, acolhedor e técnico-musical da Empório da Música (Seção 7.1 do Manual), cumprindo o fluxo de 5 etapas (Saudação, Entendimento, Consulta, Resposta, Fechamento), informando horários de expediente e redirecionando educadamente buscas por acessórios não comercializados (cordas avulsas, palhetas, cabos, cases, pedais, amplificadores) ou temas fora do domínio.
- [x] **Capacidade 2 — Pipeline de Tratamento e Higienização de Dados (`data/*.csv`):** Camada de ingestão em Python que carrega e higieniza as 6 tabelas CSV, tratando explicitamente as anomalias detectadas:
  - Sinalização/tratamento da divergência entre `name`, `description` e `specs` nos produtos `IDs 135–144` (priorizando `name` e `price_brl` como referência comercial e alertando sobre especificações para evitar erro do consumidor).
  - Mapeamento das categorias sem produtos (`IDs 6, 7, 8` — Sopros e Cordas Orquestrais).
  - Distinção estrita entre promoções ativas (`is_active == 1`, apenas 4 produtos) e expiradas (`is_active == 0`, 21 registros).
  - Tratamento de status de produtos (`active` com `stock_quantity > 0`, `active` sem estoque `ID 96`, `discontinued` `IDs 113/136` e `coming_soon` `ID 130`).
- [x] **Capacidade 3 — Ferramentas Determinísticas de Catálogo, Preços e Condições Comerciais (Tool Calling):**
  - Busca e filtragem de instrumentos por categoria, faixa de preço (ex.: *"violões disponíveis até R\$ 1.000"*), marca, modelo ou especificações.
  - Cálculo exato de preços promocionais (exibindo preço original + % de desconto + preço final), aplicação da regra de **não-cumulatividade do PIX (5% OFF apenas em produtos sem promoção ativa)** e simulação de parcelamento sem juros (respeitando parcela mínima de R\$ 50 até 3x, R\$ 80 de 4x–6x e R\$ 100 de 7x–12x, além de pagamento combinado acima de R\$ 2.000).
  - Sugestão automática de alternativas em estoque quando o item consultado estiver indisponível, descontinuado ou em breve.
- [x] **Capacidade 4 — Consulta Segura de Pedidos, Rastreamento e Elegibilidade de Troca/Devolução:**
  - Busca de pedidos (`orders.csv` + `order_items.csv` + `customers.csv`) com **desambiguação obrigatória de identidade** (exigindo segundo identificador como `order_id`, telefone, e-mail ou cidade) para impedir vazamento de dados entre homônimos (`Bruno Martins`, `Diego Castro`).
  - Avaliação de elegibilidade para Direito de Arrependimento (7 dias corridos do recebimento, frete pela loja), Troca por Preferência (7 dias) e Troca por Defeito (30 dias na loja / 90 dias garantia legal CDC), respeitando as exceções (itens personalizados, venda final, boquilhas).
- [x] **Capacidade 5 — Consulta Estruturada ao Manual de Políticas (`políticas_da_loja.pdf`) e Registro de Reclamações:**
  - Recuperação exata de informações institucionais (endereço, CNPJ, horários, frete para Campo Grande vs. outras cidades via PAC/SEDEX/Jadlog, garantia e LGPD).
  - Registro estruturado (em memória/log seguro) de reclamações ou solicitações de transbordo humano, informando o prazo oficial de retorno de **24 horas úteis**.
- [x] **Capacidade 6 — Persistência de Histórico de Conversa (Multi-Turn Memory) & Interfaces de Uso:**
  - Manutenção do estado da conversa por sessão (`thread_id` / `session_id`) para permitir perguntas de acompanhamento naturais (ex.: *"E quanto fica ele no PIX?"*, *"Pode parcelar em 10x?"*).
  - Disponibilização via **CLI interativa** e **Interface Web enxuta** (para facilitar a avaliação e inspeção de chamadas de ferramentas).
- [x] **Capacidade 7 — Entregáveis de Engenharia (Documentação, Exemplos e Testes):**
  - `README.md` completo com instruções de execução, arquitetura, justificativa das decisões técnicas, tratamento das anomalias dos dados, limitações/roadmap e relato de uso de IA no workflow.
  - **5 exemplos de conversas completas** em `examples/` cobrindo cenários triviais e não-triviais (incluindo os 4 cenários sugeridos no PDF do desafio + 1 cenário complexo de pedido/homônimo/promoção expirada).
  - Suíte automatizada de testes (`pytest`) validando regras de negócio e ferramentas.

---

## 4. Expressamente Fora de Escopo (Out-of-Scope / Anti-Escopo)
*O que NÃO será desenvolvido nesta fase para manter foco cirúrgico nos objetivos do desafio:*
- ❌ **Anti-escopo 1 — Mutação Destrutiva nos CSVs Originais:** O agente operará em modo **Read-Only** sobre `data/*.csv`. Ele não sobrescreverá `orders.csv` ou `products.csv` para cancelar pedidos ou dar baixa em estoque; solicitações de troca/cancelamento/reclamação geram protocolo de encaminhamento para a equipe humana (24h úteis).
- ❌ **Anti-escopo 2 — Integração com API Oficial da Meta (WhatsApp Cloud API) ou Gateways de Pagamento Reais:** A interação ocorrerá via CLI/UI local em Python; não haverá geração real de QR Code PIX bancário nem webhook externo com a Meta.
- ❌ **Anti-escopo 3 — Cotação Dinâmica Externa nos Correios/Jadlog:** Para entregas fora da Região Metropolitana de Campo Grande, o agente informará as modalidades e prazos oficiais da tabela do Manual (PAC 5–12 dias úteis, SEDEX 2–5 dias úteis, Jadlog 3–8 dias úteis, com seguro incluso) e orientará sobre cotação por CEP/frete especial para itens de grande porte, sem chamar APIs externas dos Correios.
- ❌ **Anti-escopo 4 — Fine-Tuning de Modelos ou Infraestrutura Cloud Pesada:** Não será feito treinamento de pesos de LLM nem exigência de clusters Kubernetes/bancos externos pagos que dificultem a execução local imediata pelo avaliador da Artefact.

---

## 5. Critérios de Sucesso e Métricas de Impacto

| Indicador de Sucesso (KPI / OKR) | Linha de Base (Hoje - Manual) | Meta Esperada (To-Be) | Benchmark de Mercado | Critério de Medição no Projeto |
| :--- | :--- | :--- | :--- | :--- |
| **Precisão Factual / Faithfulness (Zero Alucinação)** | Sujeito a erro humano ao cruzar CSVs e PDF | **100%** de fidelidade aos dados higienizados e regras do PDF | > 97% (Hallucination < 3%) | Suíte de testes automatizados (`pytest`) + auditoria dos 5 diálogos de exemplo |
| **Correção de Roteamento (Tool Correctness)** | N/A (Consulta manual) | **100%** de acerto na escolha entre Tools de Dados (CSV) vs. Políticas (PDF) | > 95% em agentes de produção | Validação determinística de chamadas de ferramentas nos cenários de teste |
| **Tempo de Primeira Resposta (FRT)** | Até 5 min (ou horas em pico) | **< 5 segundos** por turno conversacional | < 3 a 5 segundos | Medição de latência nas interações de teste |
| **Proteção de Dados e Escopo (Guardrails LGPD & Acessórios)** | Risco de confusão entre homônimos | **100%** de bloqueio de vazamento sem 2º identificador e 100% de recusa educada de acessórios | 100% em auditorias de segurança | Testes de casos de borda (homônimos `Bruno Martins`/`Diego Castro` e pedido de cordas/amplificador) |
| **Completude dos Entregáveis Artefact** | Repositório apenas com `data/` | **100%** dos itens entregues (Código Python, `README.md`, 5 exemplos de interação, histórico Git limpo) | Padrão Sênior de Avaliação Técnica | Checklist final de verificação antes da entrega |
