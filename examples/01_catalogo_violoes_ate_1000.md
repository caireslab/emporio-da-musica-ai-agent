# Exemplo de Interação 01 — Catálogo de Violões até R$ 1.000,00 (Multi-Turn)

> **Cenário Avaliado:** Pergunta #1 do Desafio Técnico (*"Quais opções de violões disponíveis custando até R$1000?"*) + Refinamento Multi-Turn com escolha de violão com captação elétrica e simulação de parcelamento.  
> **Capacidades Demonstradas:**
> - Filtragem determinística de catálogo por categoria (`Violões` — `category_id = 5`) e teto de orçamento (`max_price_brl = 1000.0`).
> - Exclusão automática de itens indisponíveis: `ID 96` (*Giannini GF-3D*, `stock_quantity = 0`) e `ID 113` (*Shelby SN-7C 7 Cordas*, `status = discontinued`).
> - Cálculo de desconto no PIX (5% à vista) e respeito às faixas de parcela mínima da **Seção 3.1** do Manual.
> - Persistência de contexto conversacional via `MemorySaver` (`thread_id = "sessao-violoes-01"`).

---

## Turno 1 — Consulta de Violões até R$ 1.000

**👤 Cliente:**
> Quais opções de violões disponíveis custando até R$1000?

**🔧 Tool Acionada pelo Agente (`LangGraph ToolNode`):**
```json
{
  "tool_name": "search_products_catalog",
  "args": {
    "category": "Violões",
    "max_price_brl": 1000.0,
    "include_unavailable": false
  }
}
```

**📦 Retorno Estruturado da Tool (Resumo Real dos CSVs):**
- `total_available_found`: **12 violões disponíveis** (em estoque e `status = "active"`).
- `excluded_unavailable_items_note`:
  - `ID 96` — *Giannini GF-3D Dreadnought Sunburst* (`R$ 799,90`, excluído pois `stock_quantity = 0`).
  - `ID 113` — *Shelby SN-7C 7 Cordas Nylon Natural* (`R$ 749,00`, excluído pois `status = "discontinued"`).

**🎸 Agente Empório da Música:**
> Opa, tudo bem? Que massa que você está procurando um violão novo! Aqui na **Empório da Música** temos **12 opções de violões em estoque** custando até **R$ 1.000,00** (já separei por estilo de corda pra facilitar sua escolha e deixei de fora os modelos que estão sem estoque no momento):
>
> ### 🎶 Violões Clássicos (Cordas de Nylon — mais macias, ótimas para estudo, MPB e dedilhado)
> 1. **Tagima Memphis AC-39 Nylon Natural** (`ID 83`) — **R$ 429,90** (ou **R$ 408,40 no PIX** com 5% OFF | até **5x de R$ 85,98** sem juros) — *15 un. em estoque*.
> 2. **Rozini RC-104 Nylon Estudante** (`ID 85`) — **R$ 459,90** (ou **R$ 436,90 no PIX** | até **5x de R$ 91,98** sem juros) — *10 un. em estoque*.
> 3. **Yamaha C40 Nylon Natural** (`ID 81`) — **R$ 599,90** (ou **R$ 569,90 no PIX** | até **7x de R$ 85,70**? Não, pela nossa regra de parcela mínima, fazemos em até **6x de R$ 99,98** sem juros!) — *12 un. em estoque*.
> 4. **Giannini GN-15 Nylon Cedro Natural** (`ID 84`) — **R$ 689,00** (ou **R$ 654,55 no PIX** | até **6x de R$ 114,83** sem juros) — *6 un. em estoque*.
> 5. **Yamaha C70 Nylon Natural (Tampo Sólido)** (`ID 82`) — **R$ 849,00** (ou **R$ 806,55 no PIX** | até **8x de R$ 106,12** sem juros) — *8 un. em estoque*.
>
> ### 🎸 Violões Folk / Dreadnought (Cordas de Aço — som brilhante e encorpado para pop, rock e sertanejo)
> 6. **Shelby SN-100 Folk Aço Preto** (`ID 89`) — **R$ 549,00** (ou **R$ 521,55 no PIX** | até **6x de R$ 91,50** sem juros) — *5 un. em estoque*.
> 7. **Giannini GF-1R Aço Folk Sunburst** (`ID 88`) — **R$ 579,90** (ou **R$ 550,90 no PIX** | até **6x de R$ 96,65** sem juros) — *7 un. em estoque*.
> 8. **Yamaha F310 Aço Natural** (`ID 87`) — **R$ 699,90** (ou **R$ 664,90 no PIX** | até **6x de R$ 116,65** sem juros) — *14 un. em estoque*.
> 9. **Tagima Dallas Tuner Aço Natural (com afinador)** (`ID 86`) — **R$ 749,00** (ou **R$ 711,55 no PIX** | até **7x de R$ 107,00** sem juros) — *9 un. em estoque*.
> 10. **Shelby SGD-195E Elétrico Aço Sunburst (Eletroacústico)** (`ID 107`) — **R$ 799,00** (ou **R$ 759,05 no PIX** | até **7x de R$ 114,14** sem juros) — *6 un. em estoque*.
> 11. **Tagima Woodstock Dreadnought Natural** (`ID 91`) — **R$ 899,00** (ou **R$ 854,05 no PIX** | até **8x de R$ 112,38** sem juros) — *11 un. em estoque*.
>
> ### 🎼 Violão de 7 Cordas (Aço)
> 12. **Tagima TW-7 7 Cordas Aço Natural** (`ID 112`) — **R$ 999,00** (ou **R$ 949,05 no PIX** | até **9x de R$ 111,00** sem juros) — *6 un. em estoque*.
>
> *(Obs.: O **Giannini GF-3D** de R$ 799,90 está temporariamente sem estoque e o **Shelby SN-7C** foi descontinuado, por isso já te mostrei apenas os que temos a pronta entrega!)*
>
> Você prefere cordas de **nylon** (mais macias) ou de **aço** (som mais aberto)?

---

## Turno 2 — Refinamento Multi-Turn (Eletroacústico + Parcelamento e Frete)

**👤 Cliente:**
> Gostei desse Shelby elétrico de aço de R$ 799! Como ficam todas as opções de parcelamento dele no cartão e quanto sai o frete aqui pra Campo Grande?

**🔧 Tools Acionadas pelo Agente (`LangGraph ToolNode`):**
```json
[
  {
    "tool_name": "get_product_pricing_and_payment",
    "args": {
      "product_query": "Shelby SGD-195E"
    }
  },
  {
    "tool_name": "calculate_shipping_info",
    "args": {
      "city": "Campo Grande",
      "order_value_brl": 799.0,
      "instrument_category_or_name": "Violão Shelby SGD-195E"
    }
  }
]
```

**🎸 Agente Empório da Música:**
> Boa escolha! O **Shelby SGD-195E Elétrico Aço Sunburst** (`ID 107`) já vem com captação elétrica e afinador embutido, excelente custo-benefício pra plugar em caixa ou tocar acústico! Temos **6 unidades** a pronta entrega.
>
> Confira todas as condições de pagamento e entrega para **Campo Grande/MS**:
>
> ### 💳 Preço e Formas de Pagamento (Seção 3 do Manual)
> - **Preço de Tabela (Débito ou Boleto à vista):** R$ 799,00
> - **À vista no PIX (5% de desconto):** **R$ 759,05** *(economia de R$ 39,95!)*
> - **Cartão de Crédito (em até 7x sem juros):**
>   - **1x** de R$ 799,00
>   - **2x** de R$ 399,50 *(faixa 1x–3x: parcela mínima R$ 50,00)*
>   - **3x** de R$ 266,33
>   - **4x** de R$ 199,75 *(faixa 4x–6x: parcela mínima R$ 80,00)*
>   - **5x** de R$ 159,80
>   - **6x** de R$ 133,17
>   - **7x** de R$ 114,14 *(faixa 7x–12x: parcela mínima R$ 100,00 — a partir de 8x a parcela ficaria R$ 99,88, abaixo do piso de R$ 100,00)*
>
> ### 🚚 Frete para Campo Grande/MS (Seção 5.1 do Manual)
> - **Valor do Frete:** **GRÁTIS!** *(Pedidos acima de R$ 500,00 têm frete grátis para toda Campo Grande e Região Metropolitana).*
> - **Prazo e Modalidade:** **1 a 3 dias úteis**, entregue pelo nosso **motoboy próprio** (nossa equipe te liga antes de sair para a entrega).
>
> Quer que eu separe um pra você ou prefere comparar com algum modelo eletroacústico de nylon?
