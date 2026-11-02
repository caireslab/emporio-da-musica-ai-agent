# Product Discovery & Project Vision — Empório da Música AI Agent

> **Status:** Aguardando Aprovação Final no Gate 01  
> **Data de Atualização:** 2026-11-02  
> **Autores / Facilitadores:** Antigravity (SDLC Master Orchestrator) & AI Engineer  
> **Patrocinador / Sponsor:** Gerência da Empório da Música & Banca Avaliadora Artefact  

---

## 1. Contexto do Negócio e Organizacional

### 1.1 Cenário Atual
A **Empório da Música** (`Empório da Música Instrumentos Musicais Ltda.`, CNPJ `12.345.678/0001-90`) é uma loja especializada exclusivamente na venda de instrumentos musicais, fundada em 2008 em Campo Grande/MS (Rua 14 de Maio, 3200 — Centro, CEP `79202-333`). Com mais de 15 anos de história, atende músicos iniciantes, intermediários e profissionais na região Centro-Oeste e em todo o Brasil via vendas presenciais e online.

Atualmente, o atendimento remoto via WhatsApp é realizado de forma manual pela equipe interna, que se encontra sobrecarregada por um alto volume de dúvidas recorrentes: horários de funcionamento, endereço, preços e especificações de instrumentos, disponibilidade em estoque, promoções, cálculo de parcelamento/PIX, frete e status/rastreamento de pedidos, além de dúvidas sobre trocas e devoluções.

### 1.2 Objetivos Estratégicos Alinhados
- **Objetivo 1 — Deflexão Operacional com Atendimento Consultivo (< 5s):** Absorver autonomamente de 70% a 80% das demandas repetitivas e transacionais no canal de texto, mantendo a persona acolhedora da loja (*"um amigo que entende de música"*), reduzindo drasticamente o tempo de espera (hoje limitado a um SLA manual de 5 minutos que sofre em horários de pico).
- **Objetivo 2 — Precisão Comercial e Conformidade Regulatória (Zero Alucinação):** Garantir que 100% das respostas sobre preços, estoques, promoções, pedidos e políticas sejam baseadas em consultas determinísticas aos dados operacionais (`data/*.csv`) e ao manual normativo (`data/políticas_da_loja.pdf`), eliminando riscos de propaganda enganosa (CDC Arts. 30 e 37) e vazamento de dados pessoais entre homônimos (LGPD).

### 1.3 Inteligência de Mercado & Benchmarks Externos (Web Research)
- **Panorama do Setor / Tendências (2025/2026):** O e-commerce brasileiro ultrapassou R\$ 258 bilhões, e o setor de instrumentos musicais migrou para o comércio conversacional no WhatsApp. Músicos exigem atendimento consultivo capaz de diferenciar especificações reais (madeiras, captação, afinação) e confirmar estoque imediato.
- **Benchmarks Concorrentes / Referências:** Operações de varejo líderes utilizam arquiteturas híbridas combinando **Function Calling / Tool Use** (para consulta transacional em tempo real a estoques, preços e pedidos) e **RAG / Knowledge Retrieval** (para políticas de troca, frete e garantia). Os benchmarks globais apontam **AI Containment Rate de 50% a 75%**, **First Response Time < 3–5 segundos** e **Hallucination Rate < 3%**.
- **Fontes e Links Consultados:**
  - *E-Commerce Brasil / Música & Mercado (2025/2026)*: Tendências de comércio unificado, agentes de IA no WhatsApp e principais reclamações de músicos (ruptura de estoque, contradição de ficha técnica e avarias no frete).
  - *Helply / Kim.cc / Confident AI (DeepEval)*: Benchmarks de escopo de MVP para agentes de suporte e-commerce e métricas de engenharia de LLMs (*Tool Correctness*, *Faithfulness*, *Answer Relevancy*).
  - *Legislação Brasileira (CDC Lei nº 8.078/1990, Decreto nº 7.962/2013 e LGPD Lei nº 13.709/2018)*: Vinculação da oferta (Art. 30), proibição de publicidade enganosa (Art. 37), garantia legal de 90 dias (Art. 26) e direito de arrependimento em 7 dias (Art. 49).

---

## 2. Declaração do Problema ou Oportunidade

> **Situação:** A Empório da Música possui um catálogo diversificado de instrumentos musicais e uma operação ativa de vendas presenciais e online em Campo Grande/MS, apoiada por dados operacionais em tabelas (`data/*.csv`) e um Manual de Políticas e Procedimentos (`data/políticas_da_loja.pdf`).  
> **Complicação / Dor Central:** O atendimento manual está saturado por perguntas repetitivas que exigem cruzamento constante entre catálogo, promoções, pedidos e regras do manual. Além disso, a base de dados operacional possui anomalias críticas (contradições entre `name`, `description` e `specs` nos produtos `IDs 135–144`, categorias vazias `IDs 6–8`, promoções expiradas `is_active=0`, produtos esgotados/descontinuados/em breve e clientes homônimos).  
> **Impacto no Negócio:** Demora no atendimento gera perda de conversão; por outro lado, automatizar sem rigor técnico e sem tratamento de dados expõe a loja a passivos de propaganda enganosa (CDC), perda financeira (aplicar desconto de PIX sobre promoção ativa ou violar parcelas mínimas) e incidente de privacidade (expor pedidos de homônimos sob a LGPD).  

### 2.1 Por que resolver agora?
A construção de um protótipo funcional, seguro e auditável em Python permitirá validar imediatamente a automação do atendimento da Empório da Música, protegendo a margem e a reputação jurídica da loja enquanto libera a equipe humana para casos complexos e reclamações (SLA de 24h úteis).

---

## 3. Mapeamento de Stakeholders

| Stakeholder / Papel | Área / Organização | Nível de Interesse | Nível de Influência | Papel no Projeto (RACI) |
| :--- | :--- | :--- | :--- | :--- |
| **Gerência da Empório da Música** | Diretoria / Operações | Alto | Alto | **Accountable (A)** — Exige aderência ao Manual v2.1 e proteção de margem/compliance. |
| **Banca Avaliadora Artefact** | Engenharia de IA | Alto | Alto | **Accountable (A)** — Avalia lógica, clareza arquitetural, tratamento de dados e justificativas no `README.md`. |
| **AI Engineer (Autor)** | Engenharia de Software & IA | Alto | Alto | **Responsible (R)** — Projeta, implementa, testa e documenta a solução completa em Python. |
| **Equipe de Atendimento Humano** | Suporte & Vendas (WhatsApp) | Alto | Médio | **Consulted (C)** — Recebe transbordos e reclamações registradas pelo agente. |
| **Clientes Músicos** | Consumidor Final | Alto | Baixo | **Informed (I)** — Consomem o atendimento conversacional de pré e pós-venda. |

---

## 4. Usuários e Personas

### Persona Primária (Core): Lucas Mendes — O Cliente Músico (Consultivo & Pré-Venda)
- **Perfil:** Músico iniciante, intermediário ou profissional buscando instrumentos musicais por categoria, orçamento ou especificação técnica.
- **Evidências Externas de Dores (Web Research):** Frustração com bots de menu rígido, demora de horas no WhatsApp, "venda fantasma" (comprar item sem estoque) e fichas técnicas contraditórias.
- **Principais Dores Locais (Pains):**
  - Dificuldade em filtrar rapidamente opções disponíveis dentro de um teto de preço (ex.: *"violões até R\$ 1.000"*).
  - Incerteza sobre se um desconto ainda vale, se o PIX de 5% acumula com promoção ou qual o parcelamento máximo sem juros.
  - Desconhecimento de que a loja **não vende acessórios** (cordas, cabos, palhetas, cases, pedais, amplificadores).
- **Ganhos Desejados (Gains):**
  - Resposta instantânea, cordial e precisa com preços reais, cálculo automático de PIX/parcelas, sugestões de produtos substitutos em estoque e regras claras de frete.
- **Jornada Atual (As-Is):**
  - Envia mensagem no WhatsApp ➔ Aguarda na fila humana ➔ **[Gargalo: Atendente cruza CSVs e PDF manualmente]** ➔ Recebe resposta tardia.

### Personas Secundárias:
1. **Cliente Pós-Venda (Fernanda / Pedro):** Busca status de pedido, código de rastreio (`BR...BR`), motivo de cancelamento ou elegibilidade de troca/devolução (arrependimento 7 dias vs. defeito 30 dias), exigindo proteção de privacidade contra homônimos (`Bruno Martins`, `Diego Castro`).
2. **Especialista de Atendimento Humano (Mariana):** Deseja que o agente filtre 80% das perguntas rotineiras e encaminhe reclamações formais já registradas (prazo de retorno de 24h úteis).

---

## 5. Necessidades e Hipóteses de Valor

### 5.1 Necessidades Fundamentais (Jobs to be Done)
- **JTBD 01 (Descoberta de Catálogo):** Quando procuro um instrumento por categoria ou faixa de preço, preciso ver apenas opções com estoque real (ou receber alternativas caso o item desejado esteja esgotado/descontinuado), para decidir minha compra com confiança.
- **JTBD 02 (Simulação Comercial Determinística):** Quando pergunto o preço de um instrumento, preciso saber o preço de tabela, eventuais promoções ativas (com preço original e % de desconto), valor no PIX (sem acumular com promoção) e opções válidas de parcelamento e frete.
- **JTBD 03 (Pós-Venda Seguro):** Quando consulto meu pedido ou solicito devolução/troca, preciso que minha identidade seja validada sem expor dados de homônimos e que as regras do CDC/Manual sejam aplicadas corretamente.

### 5.2 Hipóteses Formuladas
1. **Hipótese H01 (Roteamento Híbrido + Dados Higienizados):** Acreditamos que clientes e atendentes sofrem com lentidão e risco de erro comercial ao cruzar tabelas operacionais e regras do manual. Se viabilizarmos um agente com **Tools determinísticas em Python** sobre os CSVs higienizados e consulta estruturada ao PDF de políticas, alcançaremos **100% de precisão factual** (zero alucinação de preço/estoque/regras), comprovado por suíte de testes automatizados e pelos diálogos demonstrativos.
2. **Hipótese H02 (Desambiguação LGPD & Guardrails de Escopo):** Acreditamos que homônimos na base de clientes e perguntas sobre acessórios/temas externos geram risco de privacidade e desvio de escopo. Se implementarmos **verificação de 2º identificador em pedidos** e **guardrails explícitos de persona/escopo**, eliminaremos 100% dos vazamentos de dados entre homônimos e manteremos 100% de alinhamento às diretrizes da loja.

---

## 6. Visão do Produto e Escopo

### 6.1 Declaração de Visão (Elevator Pitch)
> **Para** clientes músicos e a equipe de atendimento da Empório da Música,  
> **Que** precisam de respostas rápidas, acolhedoras e 100% precisas sobre instrumentos musicais, preços, promoções, pedidos e políticas da loja,  
> **O** **Empório da Música AI Agent**  
> **É um** assistente virtual conversacional em Python baseado em LLMs e integração determinística com ferramentas (Tool Calling + Políticas),  
> **Que** resolve dúvidas de catálogo, simula pagamentos/fretes, rastreia pedidos com segurança LGPD e aplica as políticas de troca e garantia em segundos.  
> **Diferente de** chatbots engessados ou LLMs sem guardrails que alucinam preços e ignoram anomalias nos dados,  
> **Nosso produto** higieniza inconsistências cadastrais, executa cálculos financeiros exatos em código e preserva a identidade de *"um amigo que entende de música"*.  

### 6.2 Escopo Inicial (In-Scope — MVP)
- [x] **Capacidade 1:** Persona alinhada à Empório da Música (informal, acolhedora e profissional) e guardrails de escopo (recusa educada de acessórios como cordas, cabos, palhetas, pedais, amplificadores e cases, além de temas fora do contexto da loja).
- [x] **Capacidade 2:** Pipeline de tratamento e higienização de `data/*.csv` (tratamento da divergência `name` vs. `description`/`specs` nos `IDs 135–144`, mapeamento de categorias vazias `6, 7, 8`, filtro de promoções ativas `is_active=1` vs. expiradas `is_active=0` e status `active`/`discontinued`/`coming_soon`).
- [x] **Capacidade 3:** Ferramentas determinísticas de consulta de catálogo, cálculo de preços/descontos (não-cumulatividade do PIX 5% com promoção ativa), simulação de parcelamento (parcelas mínimas de R\$ 50, R\$ 80 e R\$ 100) e sugestão de substitutos para itens sem estoque.
- [x] **Capacidade 4:** Consulta segura de pedidos e clientes (`orders.csv`, `order_items.csv`, `customers.csv`) com desambiguação contra homônimos e avaliação de elegibilidade de troca/devolução/garantia.
- [x] **Capacidade 5:** Consulta estruturada ao Manual de Políticas (`data/políticas_da_loja.pdf`) e ferramenta de registro de reclamações/encaminhamento humano (SLA de 24h úteis).
- [x] **Capacidade 6:** Persistência de histórico de conversa multi-turn por sessão + Interface CLI e Web UI enxuta.
- [x] **Capacidade 7:** Documentação completa no `README.md`, 5 exemplos de interação real documentados e suíte de testes automatizados (`pytest`).

### 6.3 Expressamente Fora de Escopo (Out-of-Scope / Anti-Escopo)
- ❌ **Mutação Destrutiva nos CSVs:** O agente é estritamente Read-Only sobre os arquivos `data/*.csv` originais.
- ❌ **Integrações Externas Pagas/Complexas:** Sem integração real com WhatsApp Business Cloud API da Meta, gateways bancários de PIX/Cartão ou API externa dos Correios/Jadlog.
- ❌ **Fine-Tuning de Pesos de LLM:** Uso de engenharia de contexto, System Prompts estruturados, RAG/Tools e Function Calling.

---

## 7. Critérios de Sucesso e Métricas de Impacto

| Métrica / Indicador (KPI / OKR) | Linha de Base (Atual) | Meta Almejada | Benchmark de Mercado (Web Research) | Janela de Aferição |
| :--- | :--- | :--- | :--- | :--- |
| **Precisão Factual / Faithfulness** | Variável (erro manual em planilhas) | **100%** (Zero alucinação de preço/estoque/regras) | > 97% (< 3% Hallucination) | Suíte de testes e validação no Gate 05 |
| **Tool Correctness (Roteamento Dados vs. Políticas)** | N/A | **100%** nos cenários de teste | > 95% (BFCL / DeepEval) | Validação automatizada em `tests/` |
| **Tempo de Resposta (FRT)** | Até 5 min (ou fila em pico) | **< 5 segundos** | < 3–5 segundos | Execução local do agente |
| **Proteção LGPD (Homônimos) & Guardrails de Escopo** | Vulnerável a confusão manual | **100%** de desambiguação e recusa de acessórios | 100% Compliance | Casos de teste de segurança e borda |

---

## 8. Restrições e Dependências Críticas

### 8.1 Auditoria Regulatória & Compliance (Web Research)
- **Marco Regulatório:** CDC (Lei nº 8.078/90 — Arts. 26, 30, 37 e 49), Decreto do E-commerce (nº 7.962/2013) e LGPD (Lei nº 13.709/2018).
- **Auditoria de Fornecedores / APIs e OWASP LLM:** Prevenção contra *OWASP LLM01 (Prompt Injection)* e *RCE* proibindo `eval()`/código dinâmico; resiliência contra *Rate Limits (`429`)* via retry com backoff exponencial e suporte multi-provider configurável por `.env`.

### 8.2 Restrições Não Negociáveis
- **Tecnológicas:** Uso obrigatório de **Python** como linguagem principal.
- **Governança Git:** Repositório Git público com commits incrementais reais (proibido *force-push* de commit único).
- **Segurança:** Preservação absoluta de segredos (`.env` nunca versionado) e operação Read-Only sobre os dados de origem.

### 8.3 Dependências Externas
- **Provedor de LLM via API:** Configurável via variáveis de ambiente (Google Gemini / OpenAI / Groq).
- **Arquivos Locais de Dados:** `data/*.csv` (6 tabelas) e `data/políticas_da_loja.pdf`.

---

## 9. Análise Inicial de Riscos e Mitigações

| ID | Categoria | Risco Identificado | Impacto (A/M/B) | Probabilidade (A/M/B) | Ação de Mitigação Inicial |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **R01** | Negócio / CDC | Contradição entre `name`, `description` e `specs` nos produtos `IDs 135–144` ou promessa de promoção inativa (`is_active=0`). | Alto | Alta | Higienizar e sinalizar divergências na camada de dados (adotando `name` e `price_brl` como verdade comercial) e filtrar `is_active == 1`. |
| **R02** | Financeiro | Erro de cálculo do LLM em descontos de PIX (5%), cumulatividade indevida ou parcelas mínimas (R\$ 50 / R\$ 80 / R\$ 100). | Alto | Média | Executar cálculos matemáticos dentro de Tools Python determinísticas, nunca delegando aritmética financeira ao LLM puro. |
| **R03** | Legal / LGPD | Exposição de pedidos de homônimos (`Bruno Martins` IDs 11 e 43; `Diego Castro` IDs 13 e 47). | Alto | Média | Exigir segundo identificador (`order_id`, telefone, e-mail ou cidade) na tool de consulta de pedidos quando houver ambiguidade. |
| **R04** | Segurança | RCE / Prompt Injection via agentes Pandas baseados em `eval()`. | Alto | Baixa | Proibir `eval()`/`exec()`; utilizar exclusivamente Tools tipadas (Pydantic) Read-Only. |
| **R05** | Operacional | Rate limit (`429`) da API de LLM durante avaliação. | Médio | Média | Implementar retry com backoff exponencial e suportar configuração flexível de provedor/modelo no `.env`. |

---

## 10. Gate de Aprovação da Etapa 01 (Quality Gate)

### Pergunta Central de Aprovação:
> **"Temos clareza suficiente sobre o problema que estamos tentando resolver?"**

### Checklist de Avaliação do Gate:
- [x] O problema e suas dores centrais estão comprovados com dados e fatos reais (incluindo inspeção completa dos CSVs e PDF)?
- [x] O contexto e as regulações aplicáveis (CDC, LGPD, benchmarks de e-commerce e OWASP LLM) foram validados com pesquisas externas (`search_web`)?
- [x] Os stakeholders chave e os usuários impactados (Cliente Músico, Cliente Pós-Venda e Atendente Humano) estão identificados e alinhados?
- [x] As fronteiras de escopo (In-Scope MVP vs. Out-of-Scope Read-Only) estão explícitas e aceitas?
- [x] Os critérios de sucesso e metas foram calibrados com benchmarks reais de mercado?
- [x] Os riscos e restrições iniciais (anomalias `IDs 135–144`, homônimos, não-cumulatividade de promoções, segurança de tools) foram mapeados com plano de mitigação preliminar?
- [x] Nenhuma implementação prematura de código de aplicação foi realizada antes da validação do problema?

### Parecer do Gate 01:
* **Decisão:** `[ (X) APROVADO — Pronto para Fase 02 (Requirements & Specification) | ( ) REPROVADO / REVISÃO NECESSÁRIA ]`
* **Data da Decisão:** 2026-11-02
* **Aprovadores / Assinaturas:** Usuário (Sponsor / AI Engineer) & Antigravity (SDLC Orchestrator)
* **Observações e Condicionantes:** Todas as anomalias de qualidade de dados descobertas na base `data/*.csv` devem ser convertidas em Requisitos Funcionais e Regras de Negócio explícitas na Fase 02 (`SRS`).
