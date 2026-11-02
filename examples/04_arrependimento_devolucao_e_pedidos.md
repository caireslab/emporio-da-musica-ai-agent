# Exemplo de Interação 04 — Direito de Arrependimento, Trocas, Garantia e Consulta Real de Pedidos

> **Cenário Avaliado:** Pergunta #4 do Desafio Técnico (*"Me arrependi da minha compra, posso devolver meu pedido?"*) + Cruzamento em tempo real com `orders.csv`, `order_items.csv` e `customers.csv` para verificar prazos legais (7 dias corridos de arrependimento, 30 dias de troca por defeito na loja e 90 dias de garantia legal CDC).  
> **Capacidades Demonstradas:**
> - Explicação completa das regras da **Seção 4** do Manual (Direito de Arrependimento em 7 dias corridos após o recebimento, embalagem original sem uso, frete de devolução por conta da loja, reembolso em até 10 dias úteis e exceções da Seção 4.4).
> - Verificação real de um pedido **em trânsito (`shipped`)** — **Pedido #8** (Cliente: *Ana Carolina Ferreira*, Ukulele *Kala KA-C Concert Mogno* `ID 120`, código de rastreio `BRJL5544332BR`) — orientando que o prazo de 7 dias começa a contar a partir do recebimento.
> - Verificação real de um pedido **entregue há mais de 30 dias (`delivered`)** — **Pedido #1** (Cliente: *Pedro Henrique Oliveira*, Violão *Martin D-28* `ID 93`, entregue em `2025-10-25`) — demonstrando o bloqueio determinístico do arrependimento de 7 dias e da troca direta de 30 dias na loja, e acionando a intermediação com a garantia do fabricante (**Seção 4.2 e 8.2**) via `register_complaint_or_handover`.

---

## Turno 1 — Dúvida Geral sobre Direito de Arrependimento

**👤 Cliente:**
> Me arrependi da minha compra, posso devolver meu pedido?

**🔧 Tool Acionada pelo Agente (`LangGraph ToolNode`):**
```json
{
  "tool_name": "lookup_store_policy",
  "args": {
    "topic": "trocas_devolucoes_arrependimento"
  }
}
```

**🎸 Agente Empório da Música:**
> Pode sim, desde que esteja dentro das condições da nossa **Política de Trocas e Devoluções (Seção 4 do Manual / Código de Defesa do Consumidor)**:
>
> ### 🔄 Regras para Devolução por Arrependimento (Compras Online — Seção 4.1)
> - **Prazo:** Até **7 (sete) dias corridos após o recebimento** do instrumento (sem necessidade de justificativa).
> - **Condição do Produto:** Deve estar na **embalagem original, sem sinais de uso**, acompanhado de todos os manuais e itens originais.
> - **Frete de Devolução:** Fica **100% por conta da Empório da Música**!
> - **Reembolso:** Realizado na **mesma forma de pagamento original em até 10 dias úteis**.
> - *(Obs. — Seção 4.3: Se você preferir apenas **trocar por outro modelo, cor ou tamanho**, o prazo também é de **7 dias corridos** a partir do recebimento).*
>
> ### ⚠️ Itens Não Elegíveis para Troca/Devolução (Seção 4.4)
> Não conseguimos aceitar troca/devolução por arrependimento/preferência nos seguintes casos:
> 1. Instrumentos com **personalização ou ajustes sob encomenda** (setup, regulagem especial).
> 2. Produtos comprados em promoções de liquidação com aviso explícito de **"venda final"**.
> 3. **Boquilhas de instrumentos de sopro**, por questões de higiene.
>
> Se você me informar o **número do seu pedido** (ou seu **nome completo e telefone**), eu já consulto o status da entrega agora mesmo e verifico o prazo certinho pra você!

---

## Turno 2 — Verificação Real de Pedido em Trânsito (`Pedido #8`) e Pedido Antigo (`Pedido #1`)

**👤 Cliente:**
> Na verdade são dois pedidos aqui de casa: o Pedido #8 da minha esposa Ana Carolina Ferreira (que me arrependi e quero devolver) e o Pedido #1 no meu nome, Pedro Henrique Oliveira, que comprei em outubro do ano passado e agora começou a apresentar um defeito na colagem do cavalete.

**🔧 Tools Acionadas pelo Agente (`LangGraph ToolNode`):**
```json
[
  {
    "tool_name": "inspect_customer_order_and_return",
    "args": {
      "order_id": 8,
      "customer_name": "Ana Carolina Ferreira"
    }
  },
  {
    "tool_name": "inspect_customer_order_and_return",
    "args": {
      "order_id": 1,
      "customer_name": "Pedro Henrique Oliveira"
    }
  }
]
```

**📦 Retorno Estruturado das Tools (Dados Reais de `orders.csv` e `order_items.csv`):**
- **Pedido #8 (`Ana Carolina Ferreira`):** `status = "shipped"`, data da compra `2026-02-15`, item: `1x Kala KA-C Concert Mogno (ID 120)`, total `R$ 349,90` (`debit`), rastreio `BRJL5544332BR`. Elegibilidade: em trânsito (pode recusar no ato da entrega ou exercer os 7 dias corridos após o recebimento).
- **Pedido #1 (`Pedro Henrique Oliveira`):** `status = "delivered"`, data da compra `2025-10-15`, entrega em `2025-10-25`, item: `1x Martin D-28 Dreadnought Natural (ID 93)`, total `R$ 11.499,00` (`pix`). Elegibilidade (na data de referência `2026-03-25`): `151 dias corridos desde a entrega` ➔ **Prazos de 7 dias (arrependimento), 30 dias (troca direta na loja) e 90 dias (garantia legal CDC) encerrados**, cabendo acionamento da **Garantia do Fabricante (6 meses a 2 anos — Seção 8.2)** com intermediação da loja (**Seção 4.2**).

**🎸 Agente Empório da Música:**
> Consultei os dois pedidos aqui no sistema, Pedro! A situação de cada um é bem diferente — olha só os detalhes:
>
> ---
> ### 📦 1. Pedido #8 — Titular: Ana Carolina Ferreira (*Elegível para Devolução!*)
> - **Instrumento:** 1x **Ukulele Kala KA-C Concert Mogno** (`ID 120`) — Valor: **R$ 349,90** (pago no Débito).
> - **Status Atual:** **Em trânsito (`shipped`)** — Código de rastreio: **`BRJL5544332BR`**.
> - **Como proceder com o Arrependimento (Seção 4.1):**
>   Como o pedido ainda está em transporte, o prazo legal de **7 dias corridos** só começa a contar a partir do recebimento físico! Vocês podem:
>   1. **Recusar a entrega no ato** quando o entregador chegar (assim ele já volta direto pra loja), **OU**
>   2. Receber, manter na **embalagem original sem uso** e nos avisar em até **7 dias corridos** para gerarmos a logística reversa gratuita (frete por nossa conta) e fazermos o reembolso de **R$ 349,90** em até **10 dias úteis**.
>
> ---
> ### 🛠️ 2. Pedido #1 — Titular: Pedro Henrique Oliveira (*Acionamento de Garantia do Fabricante*)
> - **Instrumento:** 1x **Violão Martin D-28 Dreadnought Natural** (`ID 93`) — Valor: **R$ 11.499,00** (pago no PIX).
> - **Datas Registradas:** Compra em `15/10/2025` | Entregue em `25/10/2025` (rastreio `BRAB1234567BR`).
> - **Análise dos Prazos de Troca e Garantia (Seções 4.2 e 8):**
>   - **Direito de Arrependimento (7 dias)** e **Troca Direta na Loja por Defeito (30 dias):** Encerrados (já se passaram mais de 30 dias desde outubro de 2025).
>   - **Garantia Legal CDC (90 dias):** Também superada.
>   - **✅ Solução — Garantia do Fabricante (Seção 4.2 e 8.2):** Como a **Martin** oferece garantia de fábrica (que varia de 6 meses a 2 anos contra defeitos estruturais de fabricação, como descolamento de cavalete que não seja causado por mau uso ou exposição climática extrema), pela **Seção 4.2** **a Empório da Música pode intermediar o acionamento da garantia junto ao fabricante** mediante sua solicitação!
>
> Quer que eu já registre o protocolo de **devolução do Pedido #8** e o protocolo de **intermediação de garantia de fábrica do seu Martin D-28 (Pedido #1)** com nossa equipe responsável?
