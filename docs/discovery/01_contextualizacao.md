# Artefato 1.1 — Contextualização do Negócio & Stakeholders

> **Iniciativa / Projeto:** Empório da Música AI Agent (Desafio Técnico AI Engineer — Artefact)  
> **Data:** 2026-11-02  
> **Facilitador:** Antigravity (SDLC Master Orchestrator)  

---

## 1. Contexto do Negócio e Organizacional
- **Visão Geral da Empresa / Área:** A **Empório da Música** (`Empório da Música Instrumentos Musicais Ltda.`, CNPJ `12.345.678/0001-90`) é uma loja especializada exclusivamente na comercialização de instrumentos musicais, fundada em 2008 em Campo Grande/MS (Rua 14 de Maio, 3200 — Centro). Com mais de 15 anos de atuação na região Centro-Oeste, atende músicos iniciantes, intermediários e profissionais tanto presencialmente quanto via comércio eletrônico e atendimento remoto pelo WhatsApp.
- **Motivação da Iniciativa:** A equipe humana de atendimento encontra-se severamente sobrecarregada por um alto volume de consultas repetitivas e transacionais no WhatsApp — incluindo horários de funcionamento, endereço, status e rastreamento de pedidos, preços, disponibilidade de estoque, regras de parcelamento, frete e políticas de troca/devolução. Além disso, a operação requer rigor absoluto no cruzamento entre dados operacionais em tempo real (`data/*.csv`) e regras normativas (`data/políticas_da_loja.pdf`), evitando erros humanos ou alucinações que possam configurar propaganda enganosa.
- **Alinhamento Estratégico:**
  - **Meta/OKR 1 — Eficiência Operacional e Deflexão Qualificada:** Absorver autonomamente entre 70% e 80% das dúvidas recorrentes e consultas transacionais (catálogo, estoque, promoções, pedidos e políticas) com tempo de resposta inferior a 5 segundos (superando o SLA interno de 5 minutos), liberando os especialistas humanos para negociações complexas, reclamações críticas e pós-venda consultivo.
  - **Meta/OKR 2 — Conformidade Legal e Precisão Comercial (Zero Alucinação):** Garantir 100% de aderência às regras do Código de Defesa do Consumidor (CDC — Lei nº 8.078/90, Arts. 30, 37 e 49) e à LGPD (Lei nº 13.709/2018), assegurando que nenhum preço, desconto de PIX/promoção, disponibilidade de estoque ou regra de troca seja informado sem verificação determinística nas bases da loja e com higienização das anomalias cadastrais (`IDs 135–144`).

---

## 2. Enriquecimento de Mercado & Benchmarks Externos (Web Research)
*Fontes, dados estatísticos e tendências coletadas via `search_web`:*
- **Panorama do Setor / Tendências (2025/2026):** O mercado brasileiro de e-commerce ultrapassou R\$ 258 bilhões, e o nicho de instrumentos musicais consolidou o **comércio unificado (omnichannel)** e o **atendimento consultivo via agentes de IA no WhatsApp**. O consumidor musical moderno exige especificações precisas, transparência sobre disponibilidade e orientação adequada ao seu nível técnico (iniciante a profissional), rejeitando árvores de decisão engessadas.
- **Práticas e Soluções no Mercado:** Operações maduras de varejo solucionam a sobrecarga no WhatsApp combinando **RAG (Retrieval-Augmented Generation)** sobre manuais normativos/políticas com **Function Calling / Tool Use determinístico** conectado a bancos operacionais (catálogo, estoque, promoções e ERP de pedidos). Os benchmarks da indústria apontam uma **Taxa de Deflexão (Deflection Rate)** de **70% a 85%** para dúvidas de FAQ e status de pedido, reduzindo o Custo por Resolução (CPA) de R\$ 15–R\$ 25 (humano) para centavos por interação, mantendo o CSAT elevado por meio de transbordo inteligente (*handoff*) em casos de reclamação ou exceção.
- **Marco Regulatório Vigente (CDC & LGPD):**
  - **Art. 30 e 37 do CDC (Vinculação da Oferta e Proibição de Propaganda Enganosa):** Toda informação sobre preço, desconto, estoque ou especificação técnica veiculada no atendimento vincula o fornecedor. Informar estoque inexistente, prometer promoção expirada (`is_active = 0`), aplicar desconto cumulativo indevido ou repassar descrições técnicas contraditórias (como as detectadas nos produtos `IDs 135–144` do CSV bruto) induz o consumidor a erro e gera passivo jurídico.
  - **Art. 49 do CDC e Decreto nº 7.962/2013 (Direito de Arrependimento):** Compras online possuem prazo legal de 7 dias corridos após o recebimento para devolução imotivada, com frete reverso custeado pela loja e reembolso integral.
  - **LGPD (Lei nº 13.709/2018):** Dados pessoais de clientes (`customers.csv` e `orders.csv`) devem ser utilizados estritamente para execução contratual (consulta de status/rastreamento mediante identificação segura), evitando exposição indevida de dados de terceiros ou homônimos.
- **Fontes e Referências Auditáveis:**
  - *E-Commerce Brasil / UOL Economia (2025/2026)*: Panorama do Comércio Unificado e Agentes Conversacionais no Varejo Especializado Brasileiro.
  - *Benchmarks de Atendimento IA no Varejo (Cloud Humans / SleekFlow / Zenvia)*: Arquiteturas híbridas RAG + Function Calling atingindo 70%–85% de deflexão e SLA < 5s.
  - *Código de Defesa do Consumidor (Lei nº 8.078/1990 — Portal Consumidor.gov.br / Procon)*: Art. 30 (Força vinculante da oferta), Art. 37 (Publicidade enganosa por comissão ou omissão), Art. 26 (Garantia legal de 90 dias para bens duráveis) e Art. 49 (Direito de arrependimento em 7 dias).

---

## 3. Declaração do Problema ou Oportunidade (Framework SCQ)
- **Situação Atual:** A Empório da Música é referência regional em Campo Grande/MS na venda de instrumentos musicais (catálogo ativo com dezenas de modelos entre violões, ukuleles, guitarras, baixos, baterias e teclados), operando atendimento presencial e remoto via WhatsApp de segunda a sexta (`09:00–18:00`) e aos sábados (`09:00–13:00`).
- **Complicação / Fator Crítico:** O canal de WhatsApp sofre com fila de espera e sobrecarga da equipe humana devido ao volume massivo de perguntas operacionais repetitivas (preços, estoque, status de pedidos, cálculo de parcelamento, frete e regras de troca). Adicionalmente, a base de dados operacional (`data/*.csv`) contém armadilhas críticas de negócio: promoções expiradas (`is_active = 0`), produtos sem estoque (`stock_quantity = 0`), itens descontinuados (`discontinued`) ou ainda não lançados (`coming_soon`), clientes homônimos/duplicados e divergências cadastrais severas entre `name`, `description` e `specs` nos produtos `IDs 135 a 144`.
- **Impacto no Negócio:**
  - **Perda de Vendas (Abandono de Atendimento):** Clientes aguardando mais de 5 minutos por informações simples de preço ou estoque migram para concorrentes online.
  - **Risco Jurídico e Reputacional (CDC Art. 30/37):** Consultas manuais apressadas ou um LLM mal arquitetado (sem tools determinísticas e sem tratamento de dados) podem prometer descontos expirados, aplicar 5% de PIX sobre item já promocional (violando a não-cumulatividade da Seção 6.2), confirmar estoque de item zerado/descontinuado ou informar especificações contraditórias.
- **Custo de Inação (Cost of Delay):** Se não resolvido imediatamente, a sobrecarga da equipe impedirá o crescimento das vendas digitais na região Centro-Oeste, aumentará o Custo por Atendimento (CPA), deteriorará o CSAT e exporá a loja a reclamações formais no Procon por falha de informação ou atraso no suporte pós-venda.

---

## 4. Matriz de Stakeholders (Poder x Interesse & RACI)

| Nome / Papel | Departamento | Influência | Interesse | Papel RACI | Expectativa Principal |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Gerência da Empório da Música** | Diretoria / Operações | Alto | Alto | **Accountable (A)** | Redução da sobrecarga da equipe, conformidade estrita com o Manual de Políticas v2.1, zero passivo de propaganda enganosa e proteção de margem (não-cumulatividade de descontos). |
| **Banca Avaliadora Artefact** | Engenharia de IA (Avaliação Técnica) | Alto | Alto | **Accountable (A)** | Clareza arquitetural, decisões técnicas bem justificadas no `README.md`, tratamento inteligente dos dados sujos dos CSVs, código Python limpo e histórico Git incremental. |
| **AI Engineer (Autor do Projeto)** | Engenharia de Software & IA | Alto | Alto | **Responsible (R)** | Projetar, implementar, higienizar os dados, testar e documentar o agente conversacional cumprindo 100% dos requisitos funcionais e não-funcionais do desafio. |
| **Equipe de Atendimento Humano** | Suporte & Vendas (WhatsApp) | Médio | Alto | **Consulted (C)** | Que o agente absorva a triagem e consultas repetitivas com precisão e encaminhe reclamações (`Prazo: 24h úteis`) ou dúvidas fora da política com contexto claro. |
| **Clientes (Músicos Iniciantes a Profissionais)** | Consumidor Final | Baixo | Alto | **Informed (I)** | Atendimento ágil, acolhedor ("amigo que entende de música"), transparente quanto a preços/estoque/prazos e alinhado aos direitos do consumidor. |
