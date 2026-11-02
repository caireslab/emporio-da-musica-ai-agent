# Exemplo de Interação 02 — Preço do Takamine GD20, Promoção Expirada e Não-Cumulatividade PIX

> **Cenário Avaliado:** Pergunta #3 do Desafio Técnico (*"Quanto custa o Takamine GD20?"*) + Cruzamento com tabela `promotions.csv` (`is_active == 0` vs `is_active == 1`) e regra de **Não-Cumulatividade de Promoções com PIX** (**Seção 6.2** do Manual).  
> **Capacidades Demonstradas:**
> - Identificação precisa do **Takamine GD20 Dreadnought Natural** (`ID 95`, `price_brl = R$ 2.199,00`, `stock_quantity = 5`).
> - Transparência sobre promoção expirada (`promotion_id = 5`, *Semana do Violão*, `12% OFF`, `is_active = 0` — **Seção 7.3**).
> - Aplicação correta do desconto de 5% no PIX (`R$ 2.089,05`) por não haver promoção ativa no GD20, contrastando no Turno 2 com o **Crafter HT-100** (`ID 90`), que possui **promoção ativa de 18% OFF** (`is_active = 1`) e portanto **não acumula** os 5% adicionais do PIX (**Seção 6.2**).
> - Regra de pagamento combinado (`PIX + Cartão`) para compras acima de **R$ 2.000,00** (**Seção 3.1**).

---

## Turno 1 — Consulta do Takamine GD20 e Promoção Vencida

**👤 Cliente:**
> Quanto custa o Takamine GD20? Um amigo me falou que viu uma promoção de 12% da Semana do Violão nele, ainda está valendo?

**🔧 Tool Acionada pelo Agente (`LangGraph ToolNode`):**
```json
{
  "tool_name": "get_product_pricing_and_payment",
  "args": {
    "product_query": "Takamine GD20"
  }
}
```

**📦 Retorno Estruturado da Tool (Dados Reais):**
- `product_id`: `95` | `name`: `"Takamine GD20 Dreadnought Natural"` | `stock_quantity`: `5` (`active`).
- `table_price_brl`: `2199.00` | `active_promotion`: `null`.
- `expired_promotions`: `[{"promotion_id": 5, "discount_percent": 12, "description": "Semana do Violão - 12% em Takamine GD20", "is_active": false}]`.
- `pix_price_brl`: `2089.05` (`pix_discount_applied = true`).
- `max_installments`: `12` (`12x de R$ 183,25 sem juros`).
- `allows_combined_payment`: `true` (`> R$ 2.000,00`).

**🎸 Agente Empório da Música:**
> O **Takamine GD20 Dreadnought Natural** (`ID 95`) é um baita instrumento — tampo sólido em Cedro e fundo/laterais em Sapele, com um timbre super quente e definido pra fingerstyle! Temos **5 unidades em estoque** agora.
>
> Sobre a campanha que seu amigo comentou: a promoção **"Semana do Violão (12% OFF no Takamine GD20)"** infelizmente **já expirou** no nosso sistema (`is_active = 0`). Seguindo nossa política de transparência, ela não está mais ativa, mas você ainda consegue ótimas condições nele hoje:
>
> ### 💰 Valores e Formas de Pagamento do Takamine GD20
> - **Preço Atual de Tabela (Cartão, Débito ou Boleto):** **R$ 2.199,00**
> - **À vista no PIX (5% de desconto ativo):** **R$ 2.089,05** *(você economiza R$ 109,95 à vista!)*
> - **Parcelamento sem juros no Cartão de Crédito:** em até **12x de R$ 183,25 sem juros** (como todas as parcelas ficam acima de R$ 100,00, você pode escolher qualquer faixa de **1x a 12x**).
> - **💡 Pagamento Combinado (PIX + Cartão):** Como o valor do GD20 passa de **R$ 2.000,00** (**Seção 3.1**), você também pode dar uma entrada no PIX e parcelar o restante no cartão!
> - **🚚 Frete:** Se você estiver em **Campo Grande ou Região Metropolitana**, o **frete é GRÁTIS** (1 a 3 dias úteis via motoboy próprio).
>
> Quer aproveitar o desconto do PIX nele ou quer ver também quais violões estão com **promoção ativa** hoje na loja?

---

## Turno 2 — Comparação com Violão em Promoção Ativa (Regra de Não-Cumulatividade PIX)

**👤 Cliente:**
> Quais violões têm promoção ativa hoje? E se eu pegar um desses em promoção e pagar no PIX, ganho mais 5% em cima?

**🔧 Tool Acionada pelo Agente (`LangGraph ToolNode`):**
```json
{
  "tool_name": "search_products_catalog",
  "args": {
    "category": "Violões",
    "only_promotions": true
  }
}
```

**📦 Retorno Estruturado da Tool (Dados Reais):**
- `ID 90` — **Crafter HT-100 Folk Aço Natural**: Preço Original `R$ 2.399,00` | Promoção Ativa: `18% OFF` (*Promoção de Inverno*) ➔ **Preço Promocional: R$ 1.967,18** | `pix_discount_applied`: `false` (`pix_price_brl = R$ 1.967,18`).
- `ID 94` — **Taylor 110e Dreadnought Natural**: Preço Original `R$ 5.999,00` | Promoção Ativa: `8% OFF` (*Desconto Especial Taylor 110e*) ➔ **Preço Promocional: R$ 5.519,08** | `pix_discount_applied`: `false` (`pix_price_brl = R$ 5.519,08`).

**🎸 Agente Empório da Música:**
> Hoje temos **2 violões com promoção ativa** no catálogo (e ambos têm tampo sólido, na mesma faixa ou acima do Takamine GD20!):
>
> 1. **Crafter HT-100 Folk Aço Natural (Tampo Sólido em Spruce Engelmann)** (`ID 90` — *3 un. em estoque*)
>    - **Preço Original:** ~~R$ 2.399,00~~
>    - **Desconto Ativo:** **18% OFF** *(Promoção de Inverno)*
>    - **Preço Promocional:** **R$ 1.967,18** (em até **12x de R$ 163,93 sem juros** ou à vista no PIX por **R$ 1.967,18**).
>
> 2. **Taylor 110e Dreadnought Elétrico Natural (Tampo Sólido Sitka Spruce + Captação ES2)** (`ID 94` — *4 un. em estoque*)
>    - **Preço Original:** ~~R$ 5.999,00~~
>    - **Desconto Ativo:** **8% OFF** *(Desconto Especial Taylor 110e)*
>    - **Preço Promocional:** **R$ 5.519,08** (em até **12x de R$ 459,92 sem juros** ou à vista no PIX por **R$ 5.519,08**).
>
> ### ⚠️ Sobre somar o desconto da Promoção + 5% do PIX (Seção 6.2 do Manual)
> Pela nossa política oficial (**Seção 6.2 — Regras de Promoções**), **as promoções não são cumulativas**: o desconto de **5% do PIX não se aplica sobre preços que já estão em promoção ativa**.
>
> Ou seja: no **Crafter HT-100**, você já leva direto os **18% de desconto (R$ 1.967,18)** tanto no PIX quanto parcelado em até **12x sem juros** — o que acaba deixando ele mais barato que o próprio Takamine GD20! Entre o timbre de **Cedro do Takamine GD20** e o **Spruce Engelmann do Crafter HT-100**, qual sonoridade te agrada mais?
