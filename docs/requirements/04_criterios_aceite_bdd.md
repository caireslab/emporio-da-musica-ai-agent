# 04 — Critérios de Aceite, Cenários BDD e Exceções

> **Status:** Validado  
> **Data:** 2026-11-02  
> **Artefato:** `docs/requirements/04_criterios_aceite_bdd.md`  

---

## 1. Cenários de Sucesso (Happy Path — Gherkin / BDD)

### Cenário BDD-01: Busca de catálogo por categoria e teto de orçamento (`US-01` / `RF-03` / `RN-05`)
```gherkin
Funcionalidade: Busca Consultiva de Instrumentos no Catálogo
  Cenário: Filtrar violões disponíveis custando até R$ 1.000,00
    Dado que a base "products.csv" e "promotions.csv" estão carregadas e higienizadas em memória
    Quando o cliente pergunta "Quais opções de violões disponíveis custando até R$1000?"
    Então o agente deve acionar a ferramenta de busca de produtos filtrando pela categoria "Violões" (category_id = 5) e preço efetivo máximo de 1000.00
    E a ferramenta deve retornar apenas violões com status "active" e "stock_quantity" > 0 (ex.: Yamaha C40 R$ 599,90, Yamaha C70 R$ 849,00, Tagima Memphis AC-39 R$ 429,90, Giannini GN-15 R$ 689,00, Rozini RC-104 R$ 459,90, Tagima Dallas R$ 749,00, Yamaha F310 R$ 699,90, Giannini GF-1R R$ 579,90, Shelby SN-100 R$ 549,00, Tagima Woodstock R$ 899,00, Shelby SGD-195E R$ 799,00, Tagima TW-7 R$ 999,00)
    E NÃO deve listar como disponível o "Giannini GF-3D Dreadnought Sunburst" (ID 96, stock_quantity = 0) nem o "Shelby SN-7C 7 Cordas" (ID 113, status = discontinued)
    E a resposta deve manter o tom acolhedor e musical da Empório da Música
```

### Cenário BDD-02: Consulta de preço de produto específico e promoção expirada (`US-02` / `RF-05` / `RN-04`, `RN-07`, `RN-08`)
```gherkin
Funcionalidade: Consulta de Preço, Promoções e Condições de Pagamento
  Cenário: Consultar o preço e condições do Takamine GD20 (Promoção Expirada)
    Dado que o produto "Takamine GD20 Dreadnought Natural" (ID 95) possui price_brl = 2199.00, stock_quantity = 5 e uma promoção histórica em "promotions.csv" (ID 4, 12% OFF) com is_active = 0
    Quando o cliente pergunta "Quanto custa o Takamine GD20? Ele está em promoção e como fica o pagamento?"
    Então o agente deve consultar a ferramenta de produto/preço para "Takamine GD20"
    E deve informar com transparência que a promoção anterior de 12% já está expirada e o preço vigente é R$ 2.199,00
    E deve informar o valor à vista no PIX com 5% de desconto (R$ 2.089,05), pois não há promoção ativa
    E deve informar o parcelamento em até 12x sem juros de R$ 183,25 no cartão de crédito (pois a parcela supera o mínimo de R$ 100,00 para a faixa de 7x a 12x) e que aceita pagamento combinado (PIX + cartão) por ser acima de R$ 2.000,00
```

### Cenário BDD-03: Produto com promoção ativa e regra de não-cumulatividade do PIX (`US-02` / `RF-05` / `RN-04`, `RN-07`)
```gherkin
Funcionalidade: Não-Cumulatividade de Promoção Ativa com Desconto PIX
  Cenário: Consultar instrumento com promoção ativa (ex.: Crafter HT-100 ou Ohana CK-20)
    Dado que o produto "Ohana CK-20 Concert Natural" (ID 121) tem preço original R$ 549,00 e promoção ativa (is_active = 1) de 20% OFF ("Desconto Exclusivo")
    Quando o cliente pergunta o preço do Ohana CK-20 e se tem mais 5% de desconto no PIX
    Então o agente deve apresentar o preço original (R$ 549,00), o percentual de desconto (20% OFF) e o preço promocional final (R$ 439,20)
    E deve explicar que, conforme a política da loja (Seção 6.2), promoções não são cumulativas e o desconto de 5% do PIX não se aplica sobre preços já promocionais
    E deve informar que o parcelamento sem juros no cartão vai até 5x de R$ 87,84 (pois em 6x a parcela cairia para R$ 73,20, abaixo do mínimo de R$ 80,00 exigido para a faixa de 4x a 6x)
```

### Cenário BDD-04: Consulta de informações institucionais e frete no Manual de Políticas (`US-06` / `RF-06`, `RF-09`)
```gherkin
Funcionalidade: Consulta ao Manual de Políticas e Procedimentos
  Cenário: Consultar endereço, horário de funcionamento e regras de frete
    Dado que o Manual de Políticas v2.1 está indexado na ferramenta de políticas
    Quando o cliente pergunta "Qual o endereço da loja, o horário de funcionamento e como funciona o frete?"
    Então o agente deve informar o endereço "Rua 14 de Maio, 3200 — Centro, Campo Grande - MS, CEP 79202-333"
    E os horários de Segunda a Sexta (09:00 às 18:00), Sábado (09:00 às 13:00) e Domingo/Feriados (Fechado)
    E as regras de frete para a Região Metropolitana de Campo Grande (Grátis acima de R$ 500,00; taxa fixa de R$ 35,00 abaixo de R$ 500,00; prazo de 1 a 3 dias úteis via motoboy próprio) e para outras cidades (PAC 5–12 dias úteis, SEDEX 2–5 dias úteis, Jadlog 3–8 dias úteis, todos com seguro e rastreamento)
```

---

## 2. Cenários de Exceção e Borda (Edge Cases & Failure Modes)

### Cenário BDD-05: Devolução por arrependimento combinando regra do CDC e checagem de pedido real (`US-05` / `RF-08` / `RN-11`)
```gherkin
Funcionalidade: Avaliação de Direito de Arrependimento e Status de Pedido
  Cenário: Cliente solicita devolução por arrependimento de pedido entregue vs. pedido ainda não entregue ou fora do prazo
    Dado que a política de Direito de Arrependimento (Seção 4.1) prevê até 7 dias corridos após o recebimento para compras online, sem sinais de uso, na embalagem original, com frete por conta da loja e reembolso em até 10 dias úteis
    Quando o cliente pergunta "Me arrependi da minha compra, posso devolver meu pedido?"
    Então o agente deve explicar imediatamente os requisitos da Seção 4.1 e solicitar o número do pedido (ou nome + telefone/e-mail) para verificar o caso específico
    E se o pedido informado estiver com status "pending" ou "confirmed" (ainda não entregue, ex.: Pedido #13 de Fernanda Ribeiro), deve informar que o pedido ainda não foi entregue e orientar sobre o cancelamento imediato antes do envio
    E se o pedido estiver com status "cancelled" (ex.: Pedido #17 a #20), deve informar que o pedido já consta como cancelado e detalhar o motivo registrado em "notes"
    E se o pedido estiver "delivered" há mais de 7 dias corridos na data de referência (ex.: Pedido #1 entregue em 2025-10-25), deve informar com empatia que o prazo legal de 7 dias corridos do recebimento já se encerrou
```

### Cenário BDD-06: Bloqueio de privacidade LGPD para clientes homônimos (`US-04` / `RF-07` / `RN-10`)
```gherkin
Funcionalidade: Proteção de Dados Pessoais e Desambiguação de Homônimos (LGPD)
  Cenário: Cliente homônimo ("Bruno Martins" ou "Diego Castro") solicita status de pedido apenas pelo nome
    Dado que existem múltiplos registros para "Bruno Martins" (ID 11 Bruno Carvalho Martins e ID 43 Bruno Martins) e "Diego Castro" (ID 13 Diego Fernandes Castro e ID 47 Diego Castro) em "customers.csv"
    Quando o cliente diz "Oi, sou o Bruno Martins, quero saber o status do meu pedido" sem informar order_id ou telefone
    Então a ferramenta de pedidos deve detectar a ambiguidade de homônimos e bloquear a exposição imediata dos dados sensíveis do pedido #10
    E o agente deve solicitar educadamente um segundo identificador (número do pedido, telefone cadastrado ou nome completo) antes de exibir o valor (R$ 8.732,00) e os itens do pedido
```

### Cenário BDD-07: Tratamento de produto fora de estoque, descontinuado, em breve ou com divergência cadastral (`US-03` / `RF-02`, `RF-04` / `RN-03`, `RN-06`)
```gherkin
Funcionalidade: Transparência de Estoque e Higienização Cadastral
  Cenário: Cliente busca produto sem estoque (ID 96), descontinuado (ID 113/136), em breve (ID 130) ou com divergência (IDs 135-144)
    Dado que o cliente consulta o "Giannini GF-3D" (ID 96, stock=0), o "Shelby SN-7C 7 Cordas" (ID 113, discontinued), o "Kala KA-ABP-CTG Barítono" (ID 130, coming_soon) ou o "Music Man Bass 1X" (ID 135, divergência entre nome e descrição)
    Quando a ferramenta de catálogo é executada
    Então para os IDs 96, 113, 136 e 130, o agente nunca deve confirmar disponibilidade imediata e deve sugerir alternativas ativas da mesma categoria (ex.: outros violões dreadnought/7 cordas ou ukuleles barítono com estoque > 0)
    E para os IDs 135 a 144, deve utilizar o nome e preço oficial da tabela, sinalizando com transparência a observação cadastral da ficha técnica para nunca induzir o cliente a erro (CDC Art. 37)
```

### Cenário BDD-08: Guardrail de escopo para acessórios, categorias sem estoque (Sopros/Orquestrais) e reclamações (`US-06`, `US-07` / `RF-01`, `RF-09` / `RN-01`, `RN-13`)
```gherkin
Funcionalidade: Guardrails de Escopo e Registro de Reclamações
  Cenário: Cliente pede acessórios (cordas/amplificador), pergunta por saxofone/violino ou registra reclamação
    Dado que a loja comercializa exclusivamente instrumentos musicais e as categorias 6, 7 e 8 não possuem itens ativos em "products.csv"
    Quando o cliente pede "encordoamento de aço, palhetas e um amplificador"
    Então o agente deve informar educadamente que a Empório da Música trabalha exclusivamente com instrumentos musicais (não vendendo acessórios como cordas, palhetas, cabos, cases, pedais ou amplificadores) e sugerir procurar lojas parceiras
    E quando o cliente perguntar por "Saxofone" ou "Violino" (Categorias 6, 7 ou 8), deve informar que a categoria faz parte do escopo da loja mas está temporariamente sem modelos em estoque no sistema, oferecendo registrar encomenda/consulta à gerência
    E quando o cliente registrar uma reclamação, deve acionar a tool de protocolo e informar o prazo de retorno de 24 horas úteis mantendo a sessão aberta
```

---

## 3. Checklist de Validação e Rastreabilidade por História

| História | Requisitos & Regras | Critério de Aceite BDD | Tipo de Teste | Status |
| :--- | :--- | :--- | :--- | :--- |
| **US-01** | `RF-03`, `RN-05` | `BDD-01` (Filtro de orçamento por preço efetivo e estoque > 0) | Unitário + E2E Conversacional | [x] Especificado |
| **US-02** | `RF-05`, `RN-04`, `RN-07`, `RN-08` | `BDD-02`, `BDD-03` (Promoção ativa vs. expirada, PIX não cumulativo, parcelas mínimas) | Unitário + E2E Conversacional | [x] Especificado |
| **US-03** | `RF-02`, `RF-04`, `RN-03`, `RN-06` | `BDD-07` (Substitutos para esgotados/descontinuados e transparência em IDs 135–144) | Unitário + Integração | [x] Especificado |
| **US-04** | `RF-07`, `RN-10` | `BDD-06` (Desambiguação obrigatória de homônimos LGPD) | Unitário + Segurança | [x] Especificado |
| **US-05** | `RF-08`, `RN-11`, `RN-12` | `BDD-05` (Cálculo determinístico de 7d/30d/90d e status do pedido) | Unitário + E2E Conversacional | [x] Especificado |
| **US-06** | `RF-01`, `RF-06`, `RF-09`, `RN-01`, `RN-09` | `BDD-04`, `BDD-08` (Endereço, horários, frete CG vs. Brasil e recusa de acessórios) | Unitário + E2E Conversacional | [x] Especificado |
| **US-07** | `RF-09`, `RF-10`, `RN-13` | `BDD-08` (Protocolo de reclamação com SLA 24h úteis e sessão multi-turn ativa) | Integração | [x] Especificado |
