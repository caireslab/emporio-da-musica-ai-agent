# Exemplo de Interação 05 — Situações Especiais: Fora de Escopo (Acessórios), Categorias Sem Estoque e Proteção LGPD de Homônimos

> **Cenário Avaliado:** Fluxo complexo multi-turn combinando 3 guardrails críticos descobertos na auditoria dos dados:
> 1. **Fora de Escopo (Acessórios — Seções 1 e 7.1 / `RN-01`):** Cliente pede encordoamento, palhetas e amplificador.
> 2. **Categoria Cadastrada Sem Produtos Ativos (`categories.csv` IDs 6, 7 e 8 / `RN-06`):** Cliente pergunta por saxofone (Instrumentos de Sopro).
> 3. **Proteção de Dados Pessoais LGPD para Clientes Homônimos (`customers.csv` / `RN-10`):** Cliente pede status do pedido em nome de **"Bruno Martins"**, que possui 2 cadastros distintos (`customer_id = 11`: *Bruno Carvalho Martins* e `customer_id = 43`: *Bruno Martins*, ambos em Três Lagoas com o mesmo e-mail `bruno.martins@jmail.com`, diferenciados pelo telefone).

---

## Turno 1 — Pedido de Acessórios + Instrumento de Sopro + Consulta de Homônimo ("Bruno Martins")

**👤 Cliente:**
> Opa, beleza? Quero comprar um jogo de encordoamento 0.10, umas palhetas e um amplificador pequeno. Vocês também têm saxofone alto? Ah, e aproveita pra ver como está o meu pedido em nome de Bruno Martins!

**🔧 Tools Acionadas pelo Agente (`LangGraph ToolNode`):**
```json
[
  {
    "tool_name": "search_products_catalog",
    "args": {
      "search_query": "encordoamento palheta amplificador"
    }
  },
  {
    "tool_name": "search_products_catalog",
    "args": {
      "category": "Sopro",
      "search_query": "saxofone"
    }
  },
  {
    "tool_name": "inspect_customer_order_and_return",
    "args": {
      "customer_name": "Bruno Martins"
    }
  }
]
```

**📦 Retorno Estruturado das Tools:**
1. `search_products_catalog` (acessórios) ➔ `status: "OUT_OF_SCOPE_ACCESSORY"`, `detected_terms: ["encordoamento", "palheta", "amplificador"]`.
2. `search_products_catalog` (saxofone) ➔ `status: "CATEGORY_TEMPORARILY_WITHOUT_STOCK"`, `categories_matched: [{"category_id": 6, "name": "Instrumentos de Sopro (Madeiras)"}]`.
3. `inspect_customer_order_and_return` (`customer_name="Bruno Martins"`) ➔ `status: "AMBIGUOUS_HOMONYM_DETECTED"`, `lgpd_security_block: true`, `matched_count: 2`.

**🎸 Agente Empório da Música:**
> Opa, Bruno! Tudo ótimo por aqui! Vou te responder ponto a ponto pra não faltar nada:
>
> ### 1. 🎸 Sobre Encordoamento, Palhetas e Amplificador (Escopo da Loja — Seções 1 e 7.1)
> Aqui na **Empório da Música** nós trabalhamos **exclusivamente com instrumentos musicais**! Nós **não comercializamos acessórios** como cordas avulsas/encordoamentos, palhetas, cabos, cases, pedais ou amplificadores. Para esses itens, recomendo dar uma olhada nas lojas parceiras especializadas em acessórios musicais aqui da região!
>
> ### 2. 🎷 Sobre Saxofone Alto (Instrumentos de Sopro)
> A categoria de **Instrumentos de Sopro (Madeiras)** — que inclui saxofones, flautas e clarinetes (`Categoria #6`) — faz parte do nosso catálogo institucional, mas **no momento estamos sem nenhum modelo com saldo disponível no sistema online**. Se quiser, posso registrar uma consulta de encomenda com a nossa gerência (eles te retornam em até **24 horas úteis**)!
>
> ### 3. 🔒 Sobre o seu Pedido em nome de "Bruno Martins" (Proteção de Dados LGPD)
> Localizei **2 cadastros diferentes** compatíveis com o nome **Bruno Martins** no nosso sistema. Para proteger a sua privacidade conforme a **LGPD (Seção 9 do Manual)**, você poderia me confirmar **o número do seu telefone com DDD** (ou o **número do pedido** / **nome completo com o nome do meio**)? Assim já libero o status exato pra você na hora!

---

## Turno 2 — Desambiguação LGPD com Telefone + Alerta de Divergência Cadastral no Pedido #10

**👤 Cliente:**
> Claro! Meu nome completo é Bruno Carvalho Martins e meu telefone é (67) 98543-2109.

**🔧 Tool Acionada pelo Agente (`LangGraph ToolNode`):**
```json
{
  "tool_name": "inspect_customer_order_and_return",
  "args": {
    "customer_name": "Bruno Carvalho Martins",
    "verifier": "(67) 98543-2109"
  }
}
```

**📦 Retorno Estruturado da Tool:**
- `status`: `"OK"` | `customer`: `{"customer_id": 11, "name": "Bruno Carvalho Martins", "phone": "(67) 98543-2109", "city": "Três Lagoas"}`.
- `orders`: `[{"order_id": 10, "order_date": "2026-02-25", "status": "confirmed", "total_brl": 8732.0, "payment_method": "pix", "items": [{"product_id": 135, "product_name": "Music Man Bass 1X Electric Bass", "quantity": 1}]}]`.

**🎸 Agente Empório da Música:**
> Perfeito, **Bruno Carvalho Martins**! Identidade confirmada com segurança (`Cadastro #11` — Três Lagoas/MS). Aqui estão os detalhes do seu pedido:
>
> ### 📋 Status do Pedido #10
> - **Data do Pedido:** `25/02/2026`
> - **Status Atual:** **Confirmado (`confirmed`)** — pagamento aprovado, aguardando despacho/geração do código de rastreamento.
> - **Item Comprado:** 1x **Music Man Bass 1X Electric Bass** (`ID 135`)
> - **Valor Total:** **R$ 8.732,00** (Forma de pagamento: **PIX**).
> - **Prazo de Cancelamento/Arrependimento:** Como o pedido está confirmado e ainda será despachado para **Três Lagoas/MS**, assim que o código de rastreio (`BR...BR`) for gerado você o receberá automaticamente no WhatsApp e e-mail. E lembrando que seus **7 dias corridos de Direito de Arrependimento** só começam a contar depois que o contrabaixo for entregue!
>
> *(💡 **Nota de Transparência sobre o Item #135:** No nosso catálogo, o `ID 135` está registrado com o nome **Music Man Bass 1X Electric Bass**, mas o campo descritivo interno cita "Fender Jazz Bass". Caso queira que nossa gerência confirme o número de série e o modelo físico exato separado na expedição antes do envio, posso abrir um protocolo prioritário com retorno em até 24h úteis!)*
>
> Posso te ajudar com mais alguma informação sobre o seu pedido ou abrir a consulta do saxofone?
