# Exemplo de Interação 03 — Endereço da Loja, Horários de Funcionamento e Política de Frete

> **Cenário Avaliado:** Pergunta #2 do Desafio Técnico (*"Qual o endereço da loja?"*) + Horários de funcionamento (**Seção 2**) + Simulação de frete local vs. outra cidade com instrumento de grande porte (**Seção 5**).  
> **Capacidades Demonstradas:**
> - Consulta direta ao Manual de Políticas (`lookup_store_policy`) retornando endereço exato (`Rua 14 de Maio, 3200 — Centro, Campo Grande - MS, CEP 79202-333`), CNPJ, telefones e horários.
> - Cálculo de frete (`calculate_shipping_info`) distinguindo Região Metropolitana de Campo Grande (grátis > R$ 500 ou taxa fixa R$ 35 via motoboy em 1–3 dias úteis) de outras cidades (PAC, SEDEX e Jadlog com seguro e rastreamento).
> - Alerta proativo sobre **instrumentos de grande porte** (baterias acústicas, pianos digitais, contrabaixos — **Seção 5.2**) e **divergências cadastrais** (`RN-03`).

---

## Turno 1 — Endereço e Horário de Funcionamento

**👤 Cliente:**
> Qual o endereço da loja? Posso passar aí no sábado à tarde ou no domingo pra testar uns instrumentos?

**🔧 Tools Acionadas pelo Agente (`LangGraph ToolNode`):**
```json
[
  {
    "tool_name": "lookup_store_policy",
    "args": {
      "topic": "geral_sobre_loja"
    }
  },
  {
    "tool_name": "lookup_store_policy",
    "args": {
      "topic": "horario_funcionamento"
    }
  }
]
```

**🎸 Agente Empório da Música:**
> Vai ser um prazer te receber aqui na loja pra testar os instrumentos! 🎶
>
> Nosso endereço e dados de contato são:
> - **📍 Endereço:** **Rua 14 de Maio, 3200 — Centro, Campo Grande - MS, CEP 79202-333**
> - **📞 Telefone Geral:** (67) 3341-4444 | **WhatsApp Atendimento:** (67) 3321-4500
> - **✉️ E-mail:** contato@emporiodamusica.com.br
>
> ### 🕒 Atenção ao Horário do Fim de Semana (Seção 2 do Manual)
> No **sábado à tarde** e no **domingo** nós estamos **fechados**! Nosso horário de funcionamento presencial (e também do WhatsApp) é:
> - **Segunda a Sexta-feira:** das **09:00 às 18:00**
> - **Sábado:** das **09:00 às 13:00** *(somente no período da manhã!)*
> - **Domingos e Feriados:** Fechado
>
> Se você conseguir dar um pulo aqui no **sábado entre 09h e 13h** ou durante a semana até as 18h, nossa equipe prepara os instrumentos pra você testar com calma. Qual instrumento você está querendo experimentar?

---

## Turno 2 — Frete para Dourados/MS e Alerta de Bateria Acústica (Grande Porte + Divergência Cadastral)

**👤 Cliente:**
> Entendi! Eu moro em Dourados/MS, então talvez peça pra entregar. Quanto tempo demora o frete de uma Bateria Acústica Yamaha Kit 1 Studio pra Dourados?

**🔧 Tools Acionadas pelo Agente (`LangGraph ToolNode`):**
```json
[
  {
    "tool_name": "get_product_pricing_and_payment",
    "args": {
      "product_query": "Bateria Acústica Yamaha Kit 1 Studio"
    }
  },
  {
    "tool_name": "calculate_shipping_info",
    "args": {
      "city": "Dourados",
      "order_value_brl": 4439.0,
      "instrument_category_or_name": "Bateria Acústica Yamaha Kit 1 Studio"
    }
  }
]
```

**🎸 Agente Empório da Música:**
> Para **Dourados/MS** (fora da Região Metropolitana de Campo Grande), nós enviamos com **seguro total contra extravios/danos e código de rastreamento** (no formato `BR...BR` enviado por WhatsApp e e-mail assim que despachamos) pelas seguintes modalidades (**Seção 5.2**):
>
> ### 🚚 Modalidades e Prazos para Dourados/MS
> - **SEDEX (Correios):** **2 a 5 dias úteis**
> - **Jadlog (.package):** **3 a 8 dias úteis**
> - **PAC (Correios):** **5 a 12 dias úteis**
> - **⚠️ Frete de Grande Porte (Seção 5.2):** Como se trata de uma **bateria acústica de 5 peças com ferragens**, ela se enquadra em **instrumento de grande porte** (assim como pianos digitais e contrabaixos) e pode exigir **cotação individual de frete especial** de acordo com o seu CEP em Dourados.
>
> ### 🔍 Aviso Importante de Transparência sobre a Bateria ID 139
> Antes de fecharmos qualquer cotação, faço questão de te avisar com total transparência: no nosso sistema, o item **`ID 139`** está registrado com o nome comercial **"Bateria Acústica Yamaha Kit 1 Studio"** por **R$ 4.439,00** (ou **R$ 4.217,05 no PIX** com 5% OFF | até **12x de R$ 369,92** sem juros, com **8 unidades em estoque**), porém a descrição interna do cadastro menciona *"Bateria acústica Pearl Export com cascos em Poplar"* e a ficha técnica marca cascos em *"Maple"*.
>
> Se você preferir um kit sem nenhuma divergência de cadastro, temos também a **Bateria Acústica Yamaha Kit 3 Studio (Yamaha Stage Custom)** (`ID 141`, **R$ 14.922,00**), ou posso registrar agora mesmo um protocolo para nossa gerência conferir a caixa física do `ID 139` no estoque e te passar a cotação exata do frete para o seu CEP em Dourados em até **24 horas úteis**. Como prefere seguir?
