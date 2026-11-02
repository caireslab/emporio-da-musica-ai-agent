"""Pure deterministic business rules for Empório da Música (RN-01 to RN-13)."""

from __future__ import annotations

import unicodedata
from datetime import date
from typing import Any

from src.domain.models import InstallmentOption, Order, PricingBreakdown, Product

# Categories or keywords that require special oversized shipping quotation (Section 5.2 / RN-09)
OVERSIZED_KEYWORDS: tuple[str, ...] = (
    "bateria",
    "piano",
    "contrabaixo",
    "baixo",
)

# Out-of-scope accessories explicitly not sold by the store (Section 1 & 7.1 / RN-01)
OUT_OF_SCOPE_ACCESSORIES: tuple[str, ...] = (
    "corda avulsa",
    "encordoamento",
    "jogos de corda",
    "palheta",
    "cabo",
    "case",
    "capa",
    "bag",
    "pedal",
    "pedaleira",
    "amplificador",
    "amp",
    "cubo",
    "fonte",
    "correia",
    "suporte",
    "estante",
    "capotraste",
    "afinador avulso",
    "baqueta",
)

# Known catalog discrepancies in products.csv (IDs 135 to 144 - RN-03)
CATALOG_DISCREPANCY_NOTES: dict[int, str] = {
    135: (
        "Atenção (Divergência Cadastral no Sistema): O produto está registrado com o nome comercial "
        "'Music Man Bass 1X Electric Bass' (R$ 8.732,00), porém o campo de descrição menciona "
        "'Contrabaixo elétrico Fender Jazz Bass com corpo em Alder'. Recomenda-se confirmar o modelo "
        "físico no estoque com a gerência antes do fechamento."
    ),
    136: (
        "Atenção (Divergência Cadastral e Item Descontinuado): Registrado como 'Ibanez Bass 2X Electric Bass' "
        "(status: discontinued), mas a descrição cita 'Contrabaixo Precision de 4 cordas'."
    ),
    137: (
        "Atenção (Divergência Cadastral no Sistema): Registrado como 'Yamaha Bass 3X Electric Bass' "
        "(R$ 11.445,00), porém a descrição menciona 'Contrabaixo ativo de 5 cordas Ibanez' e o JSON de "
        "specs indica '4 cordas' ('strings': '4'). Informe essa divergência com transparência ao cliente."
    ),
    138: (
        "Nota Técnica: Registrado como 'Music Man Bass 4X Electric Bass' (R$ 7.157,00), correspondente à "
        "linha Music Man StingRay com captador humbucker na ponte."
    ),
    139: (
        "Atenção (Divergência Cadastral no Sistema): O nome comercial é 'Bateria Acústica Yamaha Kit 1 Studio' "
        "(R$ 4.439,00), mas o texto descritivo cita 'Bateria acústica Pearl Export com cascos em Poplar' e "
        "as specs indicam cascos em 'Maple'. Alerte o cliente sobre essa divergência de cadastro."
    ),
    140: (
        "Atenção (Divergência Cadastral no Sistema): O nome comercial é 'Bateria Acústica Pearl Kit 2 Studio' "
        "(R$ 13.285,00), mas a descrição cita 'Bateria acústica Tama com cascos 100% Birch' e as specs "
        "indicam 'Maple'. Alerte o cliente sobre essa divergência de cadastro."
    ),
    141: (
        "Nota Técnica: Registrado como 'Bateria Acústica Yamaha Kit 3 Studio' (R$ 14.922,00), linha Yamaha "
        "Stage Custom com ferragens inclusas."
    ),
    142: (
        "Atenção (Divergência Cadastral no Sistema): O nome comercial é 'Teclado Sintetizador Korg Synth 1 Pro' "
        "(R$ 1.127,00), porém a descrição menciona 'Sintetizador workstation Roland com 88 teclas pesadas' e "
        "as specs indicam '61 teclas'. Informe essa divergência com transparência ao cliente."
    ),
    143: (
        "Nota Técnica: Registrado como 'Teclado Sintetizador Nord Synth 2 Pro' (R$ 19.567,00), linha Nord Stage "
        "com 61 teclas."
    ),
    144: (
        "Atenção (Divergência Cadastral no Sistema): O nome comercial é 'Teclado Sintetizador Roland Synth 3 Pro' "
        "(R$ 9.351,00), mas a descrição menciona 'Teclado arranjador Yamaha com 61 teclas sensitivas'. "
        "Informe essa divergência com transparência ao cliente."
    ),
}


def normalize_text(text: str) -> str:
    """Normalize text by stripping accents and converting to lowercase."""
    if not text:
        return ""
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if not unicodedata.combining(c)).lower().strip()


def calculate_pricing_breakdown(product: Product) -> PricingBreakdown:
    """
    Calculate deterministic pricing, promotions, PIX and installment rules (Section 3 & 6 / RN-04, RN-07, RN-08).

    Rules:
    - Active promotion (is_active == 1): effective_price = round(price_brl * (1 - discount/100), 2).
    - Non-cumulativity (Section 6.2): PIX 5% discount applies ONLY if there is NO active promotion.
    - Credit card installments (Section 3.1): up to 12x interest-free:
      * 1x to 3x: min installment >= R$ 50.00 (except 1x if total < R$ 50.00)
      * 4x to 6x: min installment >= R$ 80.00
      * 7x to 12x: min installment >= R$ 100.00
    - Combined payment (PIX + Card): allowed for purchases > R$ 2,000.00.
    """
    table_price = round(product.price_brl, 2)
    has_promo = product.active_promotion is not None
    discount_pct = product.active_promotion.discount_percent if product.active_promotion else 0
    promo_desc = product.active_promotion.description if product.active_promotion else None

    effective_price = round(product.effective_price_brl, 2)

    if has_promo:
        pix_price = effective_price
        pix_discount_applied = False
        pix_explanation = (
            f"Produto já está em promoção ativa ({discount_pct}% OFF - {promo_desc}). "
            "Conforme a Seção 6.2 do Manual de Políticas, promoções não são cumulativas e o "
            "desconto de 5% do PIX não se aplica sobre preços já promocionais."
        )
    else:
        pix_price = round(table_price * 0.95, 2)
        pix_discount_applied = True
        pix_explanation = "5% de desconto à vista no PIX aplicado sobre o preço de tabela (Seção 3)."

    installment_options: list[InstallmentOption] = []
    for n in range(1, 13):
        val = round(effective_price / n, 2)
        if n <= 3:
            min_rule = 50.0
            if n == 1 or val >= min_rule:
                installment_options.append(
                    InstallmentOption(
                        installments=n,
                        installment_value_brl=val,
                        total_brl=effective_price,
                        min_installment_rule_brl=min_rule,
                    )
                )
        elif 4 <= n <= 6:
            min_rule = 80.0
            if val >= min_rule:
                installment_options.append(
                    InstallmentOption(
                        installments=n,
                        installment_value_brl=val,
                        total_brl=effective_price,
                        min_installment_rule_brl=min_rule,
                    )
                )
        else:  # 7 <= n <= 12
            min_rule = 100.0
            if val >= min_rule:
                installment_options.append(
                    InstallmentOption(
                        installments=n,
                        installment_value_brl=val,
                        total_brl=effective_price,
                        min_installment_rule_brl=min_rule,
                    )
                )

    max_inst = installment_options[-1].installments if installment_options else 1
    allows_combined = effective_price > 2000.0
    combined_rule = (
        "Permitida combinação de formas de pagamento (ex.: PIX + cartão) pois o valor supera R$ 2.000,00."
        if allows_combined
        else "Combinação de formas de pagamento (ex.: PIX + cartão) disponível apenas para compras acima de R$ 2.000,00."
    )

    return PricingBreakdown(
        table_price_brl=table_price,
        has_active_promotion=has_promo,
        active_promotion_description=promo_desc,
        discount_percent=discount_pct,
        effective_price_brl=effective_price,
        pix_price_brl=pix_price,
        pix_discount_applied=pix_discount_applied,
        pix_rule_explanation=pix_explanation,
        debit_price_brl=effective_price,
        boleto_price_brl=effective_price,
        max_installments=max_inst,
        installment_options=installment_options,
        allows_combined_payment=allows_combined,
        combined_payment_rule=combined_rule,
    )


def evaluate_shipping_rules(
    city: str,
    order_value_brl: float | None = None,
    instrument_category_or_name: str | None = None,
) -> dict[str, Any]:
    """
    Evaluate shipping cost, delivery time, and carrier options based on Section 5 of the Policy Manual (RN-09).
    """
    norm_city = normalize_text(city)
    local_cities = {"campo grande", "cg", "regiao metropolitana de campo grande", "terenos", "jaraguari", "sidrolandia"}
    is_local = any(loc in norm_city for loc in local_cities) if norm_city else False

    norm_inst = normalize_text(instrument_category_or_name or "")
    is_oversized = any(kw in norm_inst for kw in OVERSIZED_KEYWORDS)
    oversized_warning = (
        "Atenção (Seção 5.2): Instrumentos de grande porte (baterias acústicas, pianos digitais, contrabaixos) "
        "podem exigir frete especial com cotação individual."
        if is_oversized
        else None
    )

    if is_local:
        if order_value_brl is not None:
            free_eligible = order_value_brl > 500.0
            cost = 0.0 if free_eligible else 35.0
            cost_Rule = (
                f"Frete GRÁTIS aplicado (pedido de R$ {order_value_brl:.2f} acima de R$ 500,00)."
                if free_eligible
                else f"Taxa fixa de R$ 35,00 (pedido de R$ {order_value_brl:.2f} até R$ 500,00; grátis acima de R$ 500,00)."
            )
        else:
            free_eligible = None
            cost = None
            cost_Rule = "Frete GRÁTIS para pedidos acima de R$ 500,00; taxa fixa de R$ 35,00 para pedidos abaixo de R$ 500,00."

        return {
            "destination_city": city,
            "is_campo_grande_metro": True,
            "free_shipping_threshold_brl": 500.0,
            "fixed_fee_below_threshold_brl": 35.0,
            "calculated_shipping_cost_brl": cost,
            "free_shipping_eligible": free_eligible,
            "cost_explanation": cost_Rule,
            "delivery_time": "1 a 3 dias úteis",
            "delivery_method": "Motoboy próprio da Empório da Música (cliente é contactado por telefone antes da entrega).",
            "insurance_and_damage_policy": "Todos os envios possuem seguro. Em caso de avaria, recusar o recebimento e contatar a loja imediatamente.",
            "oversized_instrument_warning": oversized_warning,
        }

    return {
        "destination_city": city or "Outras Cidades (Fora da Região Metropolitana de Campo Grande)",
        "is_campo_grande_metro": False,
        "cost_explanation": "O valor do frete é calculado automaticamente com base no CEP de destino, peso e dimensões do produto.",
        "carrier_options": [
            {
                "modality": "SEDEX (Correios)",
                "estimated_delivery": "2 a 5 dias úteis",
                "tracking_included": True,
                "insurance_included": True,
            },
            {
                "modality": "Jadlog (.package)",
                "estimated_delivery": "3 a 8 dias úteis",
                "tracking_included": True,
                "insurance_included": True,
            },
            {
                "modality": "PAC (Correios)",
                "estimated_delivery": "5 a 12 dias úteis",
                "tracking_included": True,
                "insurance_included": True,
            },
        ],
        "tracking_code_format": "BR seguido de 9 caracteres alfanuméricos e BR (ex.: BR4K7M2X9P1BR), enviado por e-mail e WhatsApp após o despacho.",
        "insurance_and_damage_policy": "Todos os envios incluem seguro contra extravios e danos. Em caso de avaria no transporte, o cliente deve recusar o recebimento e entrar em contato imediatamente com a loja.",
        "oversized_instrument_warning": oversized_warning
        or "Nota: Instrumentos de grande porte (baterias acústicas, pianos digitais, contrabaixos) podem exigir frete especial com cotação individual.",
    }


def evaluate_order_return_and_warranty(order: Order, reference_date: date) -> dict[str, Any]:
    """
    Evaluate return, exchange, and warranty eligibility for an order based on Sections 4 & 8 (RN-11, RN-12).

    Rules:
    - Direito de Arrependimento (Section 4.1 / CDC Art. 49): up to 7 calendar days after delivery (`estimated_delivery`).
    - Troca por Preferência (Section 4.3): up to 7 calendar days after delivery/receipt.
    - Troca por Defeito na Loja (Section 4.2): up to 30 calendar days after purchase (`order_date`).
    - Garantia Legal CDC (Section 8.1): up to 90 calendar days after receipt (`estimated_delivery` or `order_date`).
    """
    days_since_order = (reference_date - order.order_date).days
    days_since_delivery = (
        (reference_date - order.estimated_delivery).days if order.estimated_delivery else None
    )

    ineligible_exceptions = [
        "Instrumentos com personalização ou ajustes sob encomenda (setup, regulagem especial).",
        "Produtos adquiridos em promoções de liquidação com aviso explícito de 'venda final'.",
        "Boquilhas de instrumentos de sopro, por questões de higiene.",
    ]

    if order.status == "cancelled":
        return {
            "reference_date": reference_date.isoformat(),
            "order_status": order.status,
            "can_return_or_exchange": False,
            "summary_verdict": (
                f"Este pedido (#{order.order_id}) já consta como CANCELADO no sistema "
                f"(Motivo registrado: '{order.notes or 'Não informado'}'). Não cabe devolução física de item cancelado."
            ),
            "days_since_order": days_since_order,
            "days_since_delivery": None,
            "ineligible_exceptions": ineligible_exceptions,
        }

    if order.status in ("pending", "confirmed"):
        return {
            "reference_date": reference_date.isoformat(),
            "order_status": order.status,
            "can_return_or_exchange": True,
            "summary_verdict": (
                f"O pedido (#{order.order_id}) está com status '{order.status}' e ainda NÃO foi despachado/entregue. "
                "Como ainda não houve recebimento físico, o cliente pode solicitar o cancelamento imediato ou "
                "exercer o Direito de Arrependimento em até 7 dias corridos após receber o produto."
            ),
            "days_since_order": days_since_order,
            "days_since_delivery": None,
            "arrependimento_7d_rule": "Até 7 dias corridos após o recebimento, sem sinais de uso e na embalagem original. Frete por conta da loja e reembolso em até 10 dias úteis.",
            "ineligible_exceptions": ineligible_exceptions,
        }

    if order.status == "shipped":
        return {
            "reference_date": reference_date.isoformat(),
            "order_status": order.status,
            "can_return_or_exchange": True,
            "summary_verdict": (
                f"O pedido (#{order.order_id}) está em trânsito ('shipped', código de rastreio {order.tracking_code}, "
                f"entrega estimada para {order.estimated_delivery}). O prazo de 7 dias corridos para Direito de "
                "Arrependimento ou Troca por Preferência começa a contar a partir da data do recebimento físico."
            ),
            "days_since_order": days_since_order,
            "days_since_delivery": days_since_delivery,
            "arrependimento_7d_rule": "Até 7 dias corridos após o recebimento, embalagem original, sem uso, frete de devolução pago pela loja e reembolso em até 10 dias úteis.",
            "ineligible_exceptions": ineligible_exceptions,
        }

    # Status == "delivered"
    arrependimento_ok = days_since_delivery is not None and 0 <= days_since_delivery <= 7
    preferencia_ok = days_since_delivery is not None and 0 <= days_since_delivery <= 7
    defeito_loja_30d_ok = 0 <= days_since_order <= 30
    garantia_cdc_90d_ok = (
        (days_since_delivery is not None and 0 <= days_since_delivery <= 90)
        or (0 <= days_since_order <= 90)
    )

    return {
        "reference_date": reference_date.isoformat(),
        "order_status": order.status,
        "days_since_order": days_since_order,
        "days_since_delivery": days_since_delivery,
        "arrependimento_7d_eligible": arrependimento_ok,
        "arrependimento_7d_explanation": (
            f"ELEGÍVEL ({days_since_delivery} dias corridos desde a entrega em {order.estimated_delivery}, dentro do limite de 7 dias). "
            "Requer embalagem original sem sinais de uso; frete de devolução por conta da loja e reembolso em até 10 dias úteis."
            if arrependimento_ok
            else f"PRAZO ENCERRADO para Direito de Arrependimento ({days_since_delivery} dias corridos desde a entrega em {order.estimated_delivery}; o limite legal da Seção 4.1 / CDC Art. 49 é de até 7 dias corridos após o recebimento)."
        ),
        "troca_preferencia_7d_eligible": preferencia_ok,
        "troca_defeito_30d_loja_eligible": defeito_loja_30d_ok,
        "troca_defeito_30d_explanation": (
            f"ELEGÍVEL para troca direta na loja por defeito de fabricação ({days_since_order} dias desde a compra em {order.order_date}, limite de 30 dias da Seção 4.2)."
            if defeito_loja_30d_ok
            else f"Prazo de 30 dias para troca direta na loja encerrado ({days_since_order} dias desde a compra em {order.order_date}). "
            "Após 30 dias, deve-se acionar a garantia do fabricante (a Empório da Música pode intermediar mediante solicitação)."
        ),
        "garantia_legal_cdc_90d_eligible": garantia_cdc_90d_ok,
        "garantia_fabricante_note": "A maioria dos fabricantes oferece garantia própria de 6 meses a 2 anos (Seção 8.2).",
        "ineligible_exceptions": ineligible_exceptions,
    }
