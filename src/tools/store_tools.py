"""Pydantic v2 typed tools exposed to the LangGraph conversational agent."""

from __future__ import annotations

import json
from typing import Literal

from langchain_core.tools import tool
from pydantic import BaseModel, Field

from src.data.policy_kb import PolicyKnowledgeBase
from src.data.repository import get_store_repository
from src.domain.rules import evaluate_shipping_rules

_POLICY_KB = PolicyKnowledgeBase()


# ---------------------------------------------------------------------------
# Tool 1: Catalog Search & Filtering
# ---------------------------------------------------------------------------
class SearchCatalogInput(BaseModel):
    """Input schema for searching musical instruments in the catalog."""

    category: str | None = Field(
        default=None,
        description=(
            "Categoria do instrumento (ex.: 'Violões', 'Guitarras', 'Baixos', 'Baterias', "
            "'Teclados', 'Ukuleles', 'Sopro', 'Cordas Orquestrais')."
        ),
    )
    search_query: str | None = Field(
        default=None,
        description="Termo livre de busca por marca, modelo, madeira ou estilo (ex.: 'Yamaha', 'Takamine', '7 cordas', 'dreadnought').",
    )
    max_price_brl: float | None = Field(
        default=None,
        description="Preço máximo em Reais (R$) desejado pelo cliente (ex.: 1000.0 para 'até R$ 1.000'). Avalia o preço efetivo já com promoção ativa.",
    )
    min_price_brl: float | None = Field(
        default=None,
        description="Preço mínimo em Reais (R$).",
    )
    strings_type: str | None = Field(
        default=None,
        description="Tipo de corda para violões/ukuleles: 'nylon', 'aco' (steel) ou '7 cordas'.",
    )
    has_electronics: bool | None = Field(
        default=None,
        description="Se True, filtra apenas instrumentos elétricos/eletroacústicos (com captação). Se False, apenas acústicos puros.",
    )
    only_promotions: bool = Field(
        default=False,
        description="Se True, retorna apenas instrumentos que possuem promoção ativa no momento (is_active == 1).",
    )
    include_unavailable: bool = Field(
        default=False,
        description="Se True, inclui também itens sem estoque, descontinuados ou em pré-lançamento para fins de diagnóstico.",
    )


@tool("search_products_catalog", args_schema=SearchCatalogInput)
def search_products_catalog(
    category: str | None = None,
    search_query: str | None = None,
    max_price_brl: float | None = None,
    min_price_brl: float | None = None,
    strings_type: str | None = None,
    has_electronics: bool | None = None,
    only_promotions: bool = False,
    include_unavailable: bool = False,
) -> str:
    """
    Busca e filtra instrumentos musicais no catálogo da Empório da Música por categoria,
    marca/modelo, orçamento máximo (R$), tipo de cordas, captação elétrica ou promoções ativas.
    Use SEMPRE esta ferramenta antes de responder sobre disponibilidade, opções de catálogo ou faixas de preço.
    """
    repo = get_store_repository()
    result = repo.search_catalog(
        category=category,
        search_query=search_query,
        max_price_brl=max_price_brl,
        min_price_brl=min_price_brl,
        strings_type=strings_type,
        has_electronics=has_electronics,
        only_promotions=only_promotions,
        include_unavailable=include_unavailable,
    )
    return json.dumps(result, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Tool 2: Product Specific Pricing, Promotions, PIX & Installments
# ---------------------------------------------------------------------------
class ProductPricingInput(BaseModel):
    """Input schema for detailed product price, promotions, PIX and installment calculation."""

    product_query: str = Field(
        ...,
        description="Nome, modelo ou ID numérico do instrumento (ex.: 'Takamine GD20', 'Yamaha C40', 'Ohana CK-20', '95').",
    )


@tool("get_product_pricing_and_payment", args_schema=ProductPricingInput)
def get_product_pricing_and_payment(product_query: str) -> str:
    """
    Consulta o preço exato, estoque, promoções (ativas vs. expiradas), valor à vista no PIX
    (aplicando a regra de não-cumulatividade da Seção 6.2) e tabela completa de parcelamento
    sem juros (respeitando as parcelas mínimas de R$ 50, R$ 80 e R$ 100) de um produto específico.
    Caso o produto esteja sem estoque, descontinuado ou em breve, retorna alternativas disponíveis.
    """
    repo = get_store_repository()
    result = repo.get_product_pricing_details(product_query=product_query)
    return json.dumps(result, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Tool 3: Shipping & Delivery Calculation
# ---------------------------------------------------------------------------
class ShippingCalculationInput(BaseModel):
    """Input schema for shipping cost and delivery estimation."""

    city: str = Field(
        ...,
        description="Cidade de destino informada pelo cliente (ex.: 'Campo Grande', 'Dourados', 'Três Lagoas', 'Corumbá', 'São Paulo').",
    )
    order_value_brl: float | None = Field(
        default=None,
        description="Valor total do pedido ou do instrumento em R$ (usado para verificar frete grátis acima de R$ 500 em Campo Grande).",
    )
    instrument_category_or_name: str | None = Field(
        default=None,
        description="Nome ou categoria do instrumento (para verificar alerta de frete especial em itens de grande porte: baterias, pianos, contrabaixos).",
    )


@tool("calculate_shipping_info", args_schema=ShippingCalculationInput)
def calculate_shipping_info(
    city: str,
    order_value_brl: float | None = None,
    instrument_category_or_name: str | None = None,
) -> str:
    """
    Calcula o valor do frete, prazo estimado e modalidades de entrega (Motoboy próprio para
    Campo Grande/Região Metropolitana; PAC, SEDEX e Jadlog com seguro e rastreamento para outras cidades),
    além de verificar alertas de instrumentos de grande porte (Seção 5 do Manual).
    """
    result = evaluate_shipping_rules(
        city=city,
        order_value_brl=order_value_brl,
        instrument_category_or_name=instrument_category_or_name,
    )
    return json.dumps(result, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Tool 4: Customer Order Status, LGPD Disambiguation & Return/Warranty Check
# ---------------------------------------------------------------------------
class InspectOrderInput(BaseModel):
    """Input schema for order lookup and return/exchange/warranty eligibility check."""

    order_id: int | None = Field(
        default=None,
        description="Número identificador do pedido (1 a 20), caso o cliente tenha informado.",
    )
    customer_name: str | None = Field(
        default=None,
        description="Nome do cliente (ex.: 'Lucas Mendes', 'Bruno Martins', 'Pedro Henrique Oliveira').",
    )
    verifier: str | None = Field(
        default=None,
        description="Segundo identificador para confirmação de segurança/desambiguação LGPD: telefone, e-mail ou cidade do cliente.",
    )
    reference_date: str | None = Field(
        default=None,
        description="Data de referência opcional no formato YYYY-MM-DD (se omitida, usa a data padrão da operação).",
    )


@tool("inspect_customer_order_and_return", args_schema=InspectOrderInput)
def inspect_customer_order_and_return(
    order_id: int | None = None,
    customer_name: str | None = None,
    verifier: str | None = None,
    reference_date: str | None = None,
) -> str:
    """
    Consulta pedidos de clientes (status, código de rastreio, itens comprados, previsão de entrega e notas)
    e calcula deterministicamente a elegibilidade para Direito de Arrependimento (7 dias corridos da entrega),
    Troca por Preferência (7 dias) e Troca por Defeito (30 dias na loja / 90 dias CDC).
    Aplica bloqueio de segurança LGPD caso haja homônimos sem segundo identificador.
    """
    repo = get_store_repository()
    result = repo.inspect_order_and_return(
        order_id=order_id,
        customer_name=customer_name,
        verifier=verifier,
        reference_date_str=reference_date,
    )
    return json.dumps(result, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Tool 5: Store Policy Manual Lookup
# ---------------------------------------------------------------------------
class LookupPolicyInput(BaseModel):
    """Input schema for querying the internal store policy manual."""

    topic: Literal[
        "geral_sobre_loja",
        "horario_funcionamento",
        "formas_pagamento_parcelamento",
        "trocas_devolucoes_arrependimento",
        "frete_entregas_rastreamento",
        "promocoes_descontos",
        "atendimento_whatsapp_escopo",
        "garantia",
        "privacidade_lgpd",
        "todas",
    ] = Field(
        ...,
        description="Tópico normativo do Manual de Políticas e Procedimentos v2.1 da Empório da Música.",
    )


@tool("lookup_store_policy", args_schema=LookupPolicyInput)
def lookup_store_policy(topic: str) -> str:
    """
    Consulta o Manual Interno de Políticas e Procedimentos v2.1 da Empório da Música (políticas_da_loja.pdf).
    Use para responder sobre endereço, CNPJ, telefones, horário de funcionamento, formas de pagamento,
    regras de parcelamento, trocas e devoluções (arrependimento 7 dias, defeito 30 dias, itens não elegíveis),
    política de frete, regras de promoções, escopo (sem acessórios), garantia (90 dias CDC) e LGPD.
    """
    result = _POLICY_KB.lookup(topic=topic)
    return json.dumps(result, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Tool 6: Register Complaint or Management Handover
# ---------------------------------------------------------------------------
class RegisterProtocolInput(BaseModel):
    """Input schema for registering a customer complaint or management escalation."""

    customer_identifier: str = Field(
        ...,
        description="Nome, telefone ou e-mail do cliente que está abrindo a solicitação.",
    )
    category: Literal[
        "reclamacao",
        "troca_devolucao",
        "duvida_gerencia",
        "lgpd_exclusao_dados",
        "encomenda_produto",
    ] = Field(
        ...,
        description="Categoria do registro para encaminhamento ao responsável.",
    )
    summary: str = Field(
        ...,
        description="Resumo claro e empático da demanda ou reclamação do cliente.",
    )
    order_id: int | None = Field(
        default=None,
        description="Número do pedido associado, se houver.",
    )


@tool("register_complaint_or_handover", args_schema=RegisterProtocolInput)
def register_complaint_or_handover(
    customer_identifier: str,
    category: str,
    summary: str,
    order_id: int | None = None,
) -> str:
    """
    Registra formalmente uma reclamação, pedido de intermediação de garantia/troca, solicitação
    de exclusão de dados LGPD, encomenda de instrumento sem estoque ou dúvida de política para a gerência.
    Retorna o número de protocolo e o prazo oficial de retorno de 24 horas úteis (Seção 7.3 e 10 do Manual).
    """
    repo = get_store_repository()
    result = repo.register_protocol(
        customer_identifier=customer_identifier,
        category=category,
        summary=summary,
        order_id=order_id,
    )
    return json.dumps(result, ensure_ascii=False)


ALL_STORE_TOOLS = [
    search_products_catalog,
    get_product_pricing_and_payment,
    calculate_shipping_info,
    inspect_customer_order_and_return,
    lookup_store_policy,
    register_complaint_or_handover,
]
