# 02 — Engenharia de Dados, Persistência e Fluxos

> **Status:** Validado  
> **Data:** 2026-11-02  
> **Artefato:** `docs/architecture/02_modelo_dados_persistencia.md`  

---

## 1. Estratégia de Persistência e Indexação (Zero-Config & Read-Only)
Para atender aos requisitos de **zero fricção na avaliação da Artefact**, **alta velocidade de resposta (`< 5s`)** e **proteção absoluta contra mutação dos CSVs originais (`W-01`)**, a camada de dados opera em dois motores complementares em memória:

1. **Dados Estruturados Operacionais (`data/*.csv`):**
   - Carregados na inicialização (Singleton Data Repository) a partir dos 6 arquivos CSV usando o módulo nativo `csv`/`sqlite3` (`:memory:`) e validados linha a linha por modelos **Pydantic v2**.
   - **Higienização e Enriquecimento em Tempo de Carga (`RN-03`, `RN-04`, `RN-05`):**
     - Cálculo prévio do campo virtual `effective_price_brl` (aplicando `discount_percent` apenas onde `promotions.is_active == 1`).
     - Geração automática da flag `has_catalog_discrepancy = True` e `discrepancy_note` para os produtos `IDs 135 a 144` (onde `name`, `description` e `specs` divergem na base bruta), garantindo que `name` e `price_brl` sejam usados como verdade comercial sem induzir o cliente a erro (CDC Art. 37).
     - Identificação explícita das categorias sem produtos (`category_id IN (6, 7, 8)`).
2. **Base de Conhecimento Normativa (`data/políticas_da_loja.pdf`):**
   - O Manual de Políticas v2.1 (8 páginas, 10 seções) é extraído via `pypdf` (com fallback determinístico estruturado em memória para as 10 seções oficiais) e indexado por tópicos semânticos e palavras-chave (`sobre_empresa`, `horario_funcionamento`, `formas_pagamento_parcelamento`, `trocas_devolucoes_arrependimento`, `frete_entregas_rastreamento`, `promocoes_descontos`, `atendimento_whatsapp_escopo`, `garantia`, `privacidade_lgpd`, `disposicoes_finais`).
3. **Memória de Conversa Multi-Turn:**
   - Gerenciada pelo `MemorySaver` nativo do **LangGraph v0.3**, isolando o estado de cada conversa por `thread_id`.

---

## 2. Diagrama Entidade-Relacionamento (Mermaid ER)

```mermaid
erDiagram
    CATEGORY ||--o{ PRODUCT : "classifica (6 ativas, 3 vazias)"
    PRODUCT ||--o{ PROMOTION : "possui (ativas=1 vs expiradas=0)"
    CUSTOMER ||--o{ ORDER : "realiza (homonimos detectados)"
    ORDER ||--|{ ORDER_ITEM : "contem"
    PRODUCT ||--o{ ORDER_ITEM : "referenciado_em"

    CATEGORY {
        int category_id PK "1 a 9 (6, 7, 8 sem produtos)"
        string name "Guitarras, Violoes, Ukuleles, etc."
        string description
    }

    PRODUCT {
        int product_id PK "81 a 145 (65 registros)"
        float price_brl "Preco de tabela oficial"
        string name "Nome comercial (Fonte da verdade)"
        int category_id FK
        string description "Texto descritivo (divergente em 135-144)"
        int stock_quantity "0 no ID 96"
        string status "active | discontinued | coming_soon"
        json specs "Atributos tecnicos em JSON"
        date created_at
        float effective_price_brl "Calculado: com desconto se promo ativa"
        boolean has_catalog_discrepancy "True para IDs 135 a 144"
    }

    PROMOTION {
        int promotion_id PK "1 a 25"
        int product_id FK "Apenas IDs 90, 94, 121, 127 ativos"
        int discount_percent "5% a 40%"
        string description "Campanha promocional"
        int is_active "1 (Vigente) | 0 (Expirada)"
    }

    CUSTOMER {
        int customer_id PK "1 a 50 (1-18 com pedidos)"
        string name "Atencao: Bruno Martins (11/43), Diego Castro (13/47)"
        string phone "(67) 9XXXX-XXXX"
        string email "Compartilhado em duplicatas 11/43 e 13/47"
        string city "Campo Grande, Dourados, Tres Lagoas, Corumba, Ponta Pora"
    }

    ORDER {
        int order_id PK "1 a 20"
        int customer_id FK
        date order_date "2025-10-15 a 2026-03-22"
        string status "delivered | shipped | confirmed | pending | cancelled"
        float total_brl "Valor fechado do pedido"
        string payment_method "pix | debit | boleto | credit_3x | credit_6x | credit_12x"
        string tracking_code "Formato BR + 9 alfanum + BR (vazio se nao enviado)"
        date estimated_delivery "Base para calculo de 7 dias de arrependimento"
        string notes "Motivo de cancelamento nos pedidos 17 a 20"
    }

    ORDER_ITEM {
        int order_id FK
        int product_id FK
        int quantity "1 ou 2 unidades"
    }
```

---

## 3. Dicionário de Dados & Regras de Integridade

| Entidade / Tabela | Chave Primária | Campos Indexados em Memória | Regra de Sanitização / Integridade Aplicada |
| :--- | :--- | :--- | :--- |
| `categories` | `category_id` (`int`) | `name` (normalizado sem acentos/lowercase) | Mapeia `IDs 6, 7, 8` como categorias institucionais válidas porém com `active_products_count = 0`. |
| `products` | `product_id` (`int`) | `category_id`, `status`, `name`, `effective_price_brl` | Parse seguro do campo JSON `specs`; marca `IDs 135–144` com nota de divergência técnica (`RN-03`). |
| `promotions` | `promotion_id` (`int`) | `product_id`, `is_active` | Separa promoções vigentes (`is_active == 1`) do histórico de promoções expiradas (`is_active == 0`). |
| `customers` | `customer_id` (`int`) | `name`, `phone`, `email`, `city` | Normaliza telefone (apenas dígitos) e nome para detectar homônimos/duplicatas (`RN-10`). |
| `orders` | `order_id` (`int`) | `customer_id`, `status`, `tracking_code` | Mantém `total_brl` como valor oficial contratado; converte `order_date` e `estimated_delivery` para objetos `datetime.date`. |

---

## 4. Políticas de Privacidade e Conformidade LGPD (Seção 9 do Manual)
- **Desambiguação Obrigatória de Homônimos (`RN-10`):** Quando um usuário buscar pedidos informando apenas um nome que possua múltiplos registros em `customers.csv` (ex.: `"Bruno Martins"` retorna `customer_id=11` e `customer_id=43`; `"Diego Castro"` retorna `customer_id=13` e `customer_id=47`), a camada de dados retorna `status = "AMBIGUOUS_CUSTOMER"` sem expor `orders`, exigindo confirmação de `order_id`, `phone` ou `full_name`.
- **Minimização de Dados:** A ferramenta de consulta de pedidos retorna apenas os dados estritamente necessários para o atendimento do titular verificado.
- **Imutabilidade dos Arquivos Fonte:** Nenhuma operação de escrita (`INSERT`/`UPDATE`/`DELETE`) é executada sobre os arquivos CSV em `data/`.
