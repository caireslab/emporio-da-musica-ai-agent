# Artefato 1.2 — Discovery de Usuários, Jornadas & Hipóteses

> **Iniciativa / Projeto:** Empório da Música AI Agent (Desafio Técnico AI Engineer — Artefact)  
> **Data:** 2026-11-02  
> **Facilitador:** Antigravity (SDLC Master Orchestrator)  

---

## 1. Mapeamento de Personas e Perfis de Usuário

### Persona Primária (Core): Lucas Mendes — O Cliente Músico (Consultivo & Pré-Venda)
- **Perfil:** Músico (estudante/iniciante a profissional) residente em Campo Grande/MS ou cidades do interior (Dourados, Três Lagoas, Corumbá, Ponta Porã).
- **Objetivo Principal:** Encontrar o instrumento musical ideal dentro do seu orçamento (ex.: *"violões até R\$ 1.000"*), confirmar disponibilidade real em estoque, comparar especificações técnicas (madeira do tampo, captação ativa, cordas de aço vs. nylon) e calcular condições de pagamento (desconto no PIX vs. parcelamento sem juros) e frete.
- **Nível de Familiaridade Técnica:** Variável (desde iniciantes que buscam recomendação de primeiro violão/ukulele até profissionais que perguntam especificamente pelo *Takamine GD20* ou *Martin D-28*).
- **Principais Dores (Pains):**
  - **Dor 1 — Demora e Robôs Engessados:** Ficar preso em menus numéricos de WhatsApp que não entendem buscas combinadas (*"violão de nylon elétrico até R\$ 1.500"*) ou esperar mais de 30 minutos por um atendente humano.
  - **Dor 2 — Incerteza de Estoque e Preço ("Venda Fantasma"):** Receber informações desatualizadas sobre um instrumento fora de estoque (`stock_quantity = 0`), descontinuado (`discontinued`) ou com promoção já expirada (`is_active = 0`).
  - **Dor 3 — Frustração com Escopo Oculto:** Tentar comprar cordas avulsas, cabos, pedais ou amplificadores sem saber que a loja trabalha exclusivamente com instrumentos musicais.
- **Ganhos Desejados (Gains):**
  - **Ganho 1:** Ser atendido em segundos por um assistente com tom de *"amigo que entende de música"*, que já traz preços reais, descontos ativos e alternativas em estoque caso o modelo desejado esteja esgotado.
  - **Ganho 2:** Transparência imediata sobre quanto pagará no PIX (5% OFF apenas em itens fora de promoção) ou em quantas vezes sem juros pode parcelar respeitando a parcela mínima.

### Persona Secundária 1: Fernanda / Pedro — O Cliente de Pós-Venda (Pedidos, Entregas & Trocas)
- **Perfil:** Cliente que já realizou uma compra (consta em `customers.csv` e `orders.csv`) e aciona o WhatsApp para saber o status do pedido, código de rastreio, motivo de cancelamento ou para solicitar troca/devolução (arrependimento em 7 dias ou defeito em 30 dias).
- **Principais Dores (Pains):**
  - **Dor 1 — Ansiedade Logística:** Instrumentos são caros e frágeis; o cliente quer saber imediatamente se o pedido está `pending`, `confirmed`, `shipped` ou `delivered`, qual o código de rastreamento (`BR...BR`) e a previsão de entrega.
  - **Dor 2 — Burocracia em Trocas/Devoluções:** Dúvida sobre quem paga o frete de devolução no arrependimento (7 dias corridos) ou como proceder quando um item apresenta defeito após 30 dias ou foi comprado com personalização/liquidação.
  - **Dor 3 — Risco de Homônimos / Privacidade (LGPD):** Clientes com nomes ou e-mails semelhantes na base (ex.: `Bruno Carvalho Martins` ID 11 vs. `Bruno Martins` ID 43; `Diego Fernandes Castro` ID 13 vs. `Diego Castro` ID 47) precisam de desambiguação segura (por `order_id`, telefone ou combinação de dados) para que dados de terceiros nunca sejam expostos.

### Persona Secundária 2: Mariana — Especialista de Atendimento Humano (Equipe Interna)
- **Papel na Organização:** Consultora de vendas e suporte da Empório da Música no WhatsApp `(67) 3321-4500` / `(67) 3341-4444`.
- **Principais Dores (Pains):**
  - **Dor 1 — Sobrecarga Operacional:** Gastar 80% do expediente respondendo perguntas repetitivas (*"Qual o horário de sábado?"*, *"Qual o endereço?"*, *"Quanto custa o Yamaha C40?"*).
  - **Dor 2 — Consultas Cruzadas Manuais:** Ter que abrir múltiplas planilhas (`products.csv`, `promotions.csv`, `orders.csv`) e checar o PDF de políticas para calcular se um item aceita 10x sem juros ou se a promoção ainda vale.
- **Ganhos Desejados (Gains):**
  - Receber apenas os casos de alto valor consultivo, dúvidas omissas na política ou **reclamações formais** já triadas e registradas pelo agente (com prazo de retorno de 24 horas úteis comunicado ao cliente).

---

## 2. Evidências Externas de Dores & Fricções (Web Research)
*Queixas comuns, relatos de comunidade e dados de mercado obtidos via `search_web`:*
- **Padrões de Frustração na Indústria (Sinch / Gartner / E-Commerce Brasil):**
  - **81% dos consumidores** sentem forte frustração quando precisam repetir todo o seu problema ao serem transferidos de um bot para um atendente humano.
  - **60% dos usuários** rejeitam chatbots que fingem saber o que não sabem ou que escondem as regras de negócio em textos robóticos intermináveis.
- **Fricções Específicas no E-commerce de Instrumentos Musicais (Música & Mercado / Reclame Aqui):**
  - **Ruptura de Estoque ("Vender o que não tem"):** Principal causa de reclamação no setor musical brasileiro — lojas que confirmam disponibilidade sem checar o saldo real (`stock_quantity`) ou status (`discontinued` / `coming_soon`).
  - **Falta de Conhecimento Técnico / Contradição de Catálogo:** Clientes músicos abandonam a compra quando o atendimento contradiz especificações básicas (ex.: anunciar um baixo de 5 cordas como 4 cordas, ou confundir marcas no título vs. descrição — exatamente a anomalia presente nos `IDs 135–144` de `products.csv`).
  - **Insegurança no Frete e Avarias:** Alta sensibilidade quanto a seguro de transporte, prazos para cidades fora da capital (Dourados, Corumbá, Três Lagoas, Ponta Porã via PAC/SEDEX/Jadlog) e cotação especial para instrumentos de grande porte (baterias acústicas, pianos digitais, contrabaixos).
- **Fontes / Referências Consultadas:**
  - *Música & Mercado / E-Commerce Brasil (2025/2026)*: Dores de consumidores na compra online de instrumentos musicais (estoque, logística e atendimento técnico).
  - *Estudos de UX Conversacional (Octadesk / Coletiva.net / UX Collective)*: Impacto da transparência, concisão em balões de texto e preservação de contexto no transbordo humano.

---

## 3. Jornada do Usuário Atual (Fluxo As-Is vs. Pontos de Quebra)

```text
[ Cliente envia mensagem no WhatsApp ] ──► [ Fila de Espera Humana ] ──► [ Consulta Manual em Planilhas/PDF ] ──► [ Resposta Tardia ou Inconsistente ]
```

| Etapa | Ação do Usuário | Ferramentas Usadas Hoje (As-Is) | Ponto de Fricção / Dor Crítica | Emoção / Sentimento |
| :--- | :--- | :--- | :--- | :--- |
| **1. Contato Inicial** | Pergunta sobre produto, horário ou pedido no WhatsApp | WhatsApp `(67) 3321-4500` | Espera acima do SLA de 5 min em horários de pico ou falta de retorno claro fora do expediente (`Seg-Sex 09h-18h`, `Sáb 09h-13h`). | Impaciência |
| **2. Busca de Catálogo / Preço** | Pergunta *"Quais violões até R\$ 1.000?"* ou *"Quanto tá o Takamine GD20?"* | Planilhas CSV avulsas (`products.csv`, `promotions.csv`) | Risco de informar item sem estoque (`ID 96`), descontinuado (`ID 113`/`136`), com promoção vencida (`is_active=0`) ou com descrição contraditória (`IDs 135-144`). | Desconfiança / Confusão |
| **3. Simulação de Pagamento e Frete** | Pergunta se tem desconto no PIX ou em quantas vezes divide | Leitura manual do PDF (`políticas_da_loja.pdf`) | Erro ao acumular 5% do PIX em item já promocional (proibido pela Seção 6.2) ou errar a parcela mínima (R\$ 50 até 3x, R\$ 80 de 4x-6x, R\$ 100 de 7x-12x). | Frustração |
| **4. Rastreamento e Pós-Venda** | Pede status do pedido ou quer devolver por arrependimento | `customers.csv` + `orders.csv` + `order_items.csv` | Homônimos na base (`Bruno Martins`, `Diego Castro`) gerando risco de expor pedido errado (violação LGPD); dúvida sobre prazos do CDC (7 dias arrependimento vs. 30 dias defeito). | Ansiedade / Irritação |

---

## 4. Necessidades Fundamentais (Jobs to be Done - JTBD)
1. **JTBD 01 (Descoberta & Recomendação de Catálogo):** *"Quando estou procurando um instrumento musical por categoria, faixa de preço ou característica (ex.: violão até R\$ 1.000, ukulele soprano, guitarra), eu quero ver apenas opções reais disponíveis em estoque — ou ser avisado com transparência se o modelo que busco esgotou/foi descontinuado, recebendo alternativas equivalentes — para tomar uma decisão de compra rápida e segura."*
2. **JTBD 02 (Transparência Comercial & Simulação de Compra):** *"Quando me interesso por um instrumento específico, eu quero saber o preço exato, se há promoção ativa (mostrando o preço original e o % de desconto), quanto fica à vista no PIX (respeitando a não-cumulatividade) e o parcelamento válido no cartão, além do frete para minha cidade, para planejar meu pagamento sem surpresas no checkout."*
3. **JTBD 03 (Acompanhamento de Pedido com Privacidade):** *"Quando já comprei na Empório da Música, eu quero consultar o status, itens, código de rastreio e previsão de entrega do meu pedido de forma rápida e protegida contra homônimos, para acompanhar a chegada do meu instrumento com tranquilidade."*
4. **JTBD 04 (Suporte a Políticas, Trocas e Fora de Escopo):** *"Quando tenho dúvidas sobre trocas, devolução por arrependimento, garantia, horário da loja ou procuro acessórios não vendidos pela loja (cordas, cabos, pedais, amplificadores), eu quero uma resposta empática, exata segundo o manual interno e que registre minha reclamação para retorno em 24h úteis quando necessário."*

---

## 5. Hipóteses de Valor Estruturadas

### Hipótese H01 (Roteamento Híbrido: Tool Calling + Políticas):
* **Acreditamos que:** Os clientes músicos e a equipe da Empório da Música sofrem com lentidão e risco de erro quando perguntas exigem cruzar catálogo/promoções (`data/*.csv`) com regras de negócio (`políticas_da_loja.pdf`).
* **Se viabilizarmos:** Um agente conversacional em Python capaz de decidir autonomamente quando invocar ferramentas de consulta de dados estruturados (produtos, promoções, pedidos) e quando consultar o manual de políticas, aplicando higienização prévia nas anomalias do CSV.
* **Resultará em:** 100% de precisão factual sobre preços, estoques, promoções vigentes e regras de parcelamento/troca, eliminando riscos de propaganda enganosa (CDC Art. 30/37).
* **Saberemos que tivemos sucesso quando medirmos:** Aprovação integral nos cenários de teste (incluindo os 3 a 5 diálogos demonstrativos exigidos no desafio e casos de borda não triviais) com zero alucinação de preço, estoque ou regra normativa.

### Hipótese H02 (Desambiguação Segura & Guardrails de Escopo):
* **Acreditamos que:** Consultas de pedidos por clientes com nomes comuns/homônimos e pedidos de itens fora de escopo (acessórios ou assuntos aleatórios) geram vulnerabilidade de LGPD e desvio da persona da loja.
* **Se viabilizarmos:** Validação de identidade em duas etapas para pedidos (ex.: confirmação de `order_id`, telefone ou e-mail/cidade) e guardrails estritos de escopo com tom acolhedor (*"amigo que entende de música"*).
* **Resultará em:** Proteção total dos dados pessoais dos clientes (LGPD) e redirecionamento elegante de demandas de acessórios ou reclamações críticas.
* **Saberemos que tivemos sucesso quando medirmos:** Zero vazamento de dados de pedidos entre homônimos nos testes de segurança e 100% de aderência às diretrizes da Seção 7 do Manual de Políticas.
