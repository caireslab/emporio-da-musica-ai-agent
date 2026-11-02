"""Automated tests for Domain Models, Business Rules, Policy KB, and CSV Repository."""

from __future__ import annotations

from datetime import date

import pytest

from src.config import DATA_DIR, get_reference_date
from src.data.policy_kb import PolicyKnowledgeBase
from src.data.repository import StoreRepository, get_store_repository
from src.domain.rules import (
    CATALOG_DISCREPANCY_NOTES,
    OUT_OF_SCOPE_ACCESSORIES,
    calculate_pricing_breakdown,
    evaluate_shipping_rules,
    normalize_text,
)


@pytest.fixture(scope="module")
def repo() -> StoreRepository:
    """Shared read-only repository loaded from real data/*.csv files."""
    return get_store_repository()


@pytest.fixture(scope="module")
def policy_kb() -> PolicyKnowledgeBase:
    """Shared store policy knowledge base."""
    return PolicyKnowledgeBase()


def test_config_and_reference_date() -> None:
    assert DATA_DIR.exists()
    assert get_reference_date("2025-11-18") == date(2025, 11, 18)
    assert get_reference_date("invalid-date") == date(2026, 3, 25)
    assert normalize_text("Violões Clássicos!") == "violoes classicos!"


def test_bdd01_violoes_available_up_to_1000(repo: StoreRepository) -> None:
    """BDD-01: Search acoustic guitars up to R$ 1,000 excluding out-of-stock/discontinued."""
    res = repo.search_catalog(
        category="Violões",
        max_price_brl=1000.0,
        include_unavailable=False,
    )
    assert res["status"] == "OK"
    assert res["total_available_found"] == 12

    returned_ids = {item["product_id"] for item in res["available_products"]}
    # ID 96 (stock=0) and ID 113 (discontinued) must NOT be in available_products
    assert 96 not in returned_ids
    assert 113 not in returned_ids

    for item in res["available_products"]:
        assert item["effective_price_brl"] <= 1000.0
        assert item["is_available_for_sale"] is True


def test_bdd01_active_promotions_on_violoes(repo: StoreRepository) -> None:
    """Active promotions on IDs 90 (18% OFF) and 94 (8% OFF) must be applied."""
    sim_90 = repo.get_product_pricing_details("90")
    assert sim_90["status"] == "OK"
    p90 = sim_90["pricing_breakdown"]
    assert p90["has_active_promotion"] is True
    assert p90["discount_percent"] == 18
    assert p90["effective_price_brl"] == pytest.approx(1967.18, abs=0.05)
    assert p90["pix_discount_applied"] is False
    assert p90["pix_price_brl"] == p90["effective_price_brl"]

    sim_94 = repo.get_product_pricing_details("94")
    assert sim_94["status"] == "OK"
    p94 = sim_94["pricing_breakdown"]
    assert p94["discount_percent"] == 8
    assert p94["effective_price_brl"] == pytest.approx(5519.08, abs=0.05)


def test_bdd02_takamine_gd20_expired_promotion_and_non_cumulative_pix(
    repo: StoreRepository,
) -> None:
    """BDD-02: Takamine GD20 (ID 95) has an expired 12% promo; PIX 5% applies on R$ 2,199.00."""
    sim = repo.get_product_pricing_details("Takamine GD20")
    assert sim["status"] == "OK"
    p = sim["pricing_breakdown"]
    assert sim["product"]["product_id"] == 95
    assert p["table_price_brl"] == 2199.00
    assert p["has_active_promotion"] is False
    assert len(sim["expired_promotions"]) == 1
    assert sim["expired_promotions"][0]["discount_percent"] == 12
    assert p["pix_discount_applied"] is True
    assert p["pix_price_brl"] == pytest.approx(2089.05, abs=0.01)
    assert p["allows_combined_payment"] is True
    assert p["max_installments"] == 12


def test_bdd03_catalog_discrepancies_flagged_ids_135_to_144(
    repo: StoreRepository,
) -> None:
    """BDD-03: Products 135..144 have sanitized discrepancy warnings attached."""
    for pid in range(135, 145):
        assert pid in CATALOG_DISCREPANCY_NOTES
        product = repo.products.get(pid)
        assert product is not None
        assert product.discrepancy_note is not None
    for pid in (135, 136, 137, 139, 140, 142, 144):
        assert repo.products[pid].has_catalog_discrepancy is True


def test_bdd04_unavailable_items_and_empty_categories(repo: StoreRepository) -> None:
    """BDD-04: Unavailable products (96, 113, 136, 130) and empty categories (6, 7, 8)."""
    for pid, expected_status in [
        (96, "active"),
        (113, "discontinued"),
        (136, "discontinued"),
        (130, "coming_soon"),
    ]:
        prod = repo.products.get(pid)
        assert prod is not None
        assert prod.status == expected_status
        assert prod.is_available_for_sale is False
        details = repo.get_product_pricing_details(str(pid))
        assert len(details["suggested_alternatives"]) >= 1

    # Searching unavailable item with include_unavailable=True returns alternatives
    res_unavail = repo.search_catalog(
        search_query="Shelby SN-7C",
        include_unavailable=True,
    )
    assert res_unavail["status"] == "OK"
    assert len(res_unavail["unavailable_or_discontinued_matches"]) >= 1

    # Searching empty categories (Saxofone / Trompete / Violino)
    for wind_or_bow_query in ["saxofone", "trompete", "violino"]:
        empty_res = repo.search_catalog(search_query=wind_or_bow_query)
        assert empty_res["status"] == "CATEGORY_TEMPORARILY_WITHOUT_STOCK"


def test_bdd05_accessory_out_of_scope_guardrail(repo: StoreRepository) -> None:
    """BDD-05: Store sells exclusively musical instruments; accessories trigger guardrail."""
    assert len(OUT_OF_SCOPE_ACCESSORIES) >= 10
    cat_res = repo.search_catalog(search_query="encordoamento e palheta")
    assert cat_res["status"] == "OUT_OF_SCOPE_ACCESSORY"


def test_bdd06_store_policy_address_and_shipping(
    policy_kb: PolicyKnowledgeBase,
) -> None:
    """BDD-06: Store address, opening hours, and shipping simulations."""
    sec_geral = policy_kb.lookup("geral_sobre_loja")
    assert len(sec_geral["sections"]) == 1
    assert "Rua 14 de Maio, 3200" in sec_geral["sections"][0]["content"]

    sec_all = policy_kb.lookup("todas")
    assert len(sec_all["sections"]) == 9

    sec_keyword = policy_kb.lookup("arrependimento")
    assert len(sec_keyword["sections"]) >= 1

    # Free shipping over R$ 500 in Campo Grande
    ship_local_free = evaluate_shipping_rules(
        city="Campo Grande",
        order_value_brl=650.0,
        instrument_category_or_name="Violão",
    )
    assert ship_local_free["is_campo_grande_metro"] is True
    assert ship_local_free["calculated_shipping_cost_brl"] == 0.0
    assert ship_local_free["free_shipping_eligible"] is True

    # Fixed R$ 35 shipping up to R$ 500 in Campo Grande
    ship_local_paid = evaluate_shipping_rules(
        city="Campo Grande",
        order_value_brl=300.0,
    )
    assert ship_local_paid["calculated_shipping_cost_brl"] == 35.0

    # National shipping outside Campo Grande with oversized instrument warning
    ship_national = evaluate_shipping_rules(
        city="São Paulo - SP",
        order_value_brl=4500.0,
        instrument_category_or_name="Bateria Acústica",
    )
    assert ship_national["is_campo_grande_metro"] is False
    assert len(ship_national["carrier_options"]) == 3
    assert "grande porte" in ship_national["oversized_instrument_warning"]


def test_bdd07_order_return_eligibility_all_statuses(repo: StoreRepository) -> None:
    """BDD-07: Inspect orders across delivered, shipped, pending, confirmed, and cancelled statuses."""
    # Order #1 (order_date 2025-10-15, delivered on 2025-10-25): with ref_date 2025-10-29 (4 days after delivery) -> eligible for 7d regret
    res_eligible = repo.inspect_order_and_return(
        order_id=1,
        reference_date_str="2025-10-29",
    )
    assert res_eligible["status"] == "OK"
    elig_1 = res_eligible["orders"][0]["return_and_warranty_eligibility"]
    assert elig_1["arrependimento_7d_eligible"] is True
    assert elig_1["troca_defeito_30d_loja_eligible"] is True

    # Same Order #1 with ref_date 2026-03-25 (> 90 days) -> expired
    res_expired = repo.inspect_order_and_return(
        order_id=1,
        reference_date_str="2026-03-25",
    )
    elig_exp = res_expired["orders"][0]["return_and_warranty_eligibility"]
    assert elig_exp["arrependimento_7d_eligible"] is False
    assert elig_exp["troca_defeito_30d_loja_eligible"] is False

    # Shipped (#8), confirmed (#10), pending (#13), and cancelled (#17) orders
    for oid in (8, 10, 13, 17):
        res_oid = repo.inspect_order_and_return(order_id=oid)
        assert res_oid["status"] == "OK"

    # Non-existent order
    not_found = repo.inspect_order_and_return(order_id=999)
    assert not_found["status"] == "ORDER_NOT_FOUND"


def test_bdd08_lgpd_homonym_disambiguation(repo: StoreRepository) -> None:
    """BDD-08: Querying 'Bruno Martins' or 'Diego Castro' without verifier blocks disclosure."""
    ambiguous_bruno = repo.inspect_order_and_return(customer_name="Bruno Martins")
    assert ambiguous_bruno["status"] == "AMBIGUOUS_HOMONYM_DETECTED"
    assert ambiguous_bruno["lgpd_security_block"] is True

    # Disambiguating with phone verifier resolves to exact customer (ID 11)
    resolved_bruno = repo.inspect_order_and_return(
        customer_name="Bruno Martins",
        verifier="98543-2109",
    )
    assert resolved_bruno["status"] == "OK"
    assert resolved_bruno["customer"]["customer_id"] == 11

    ambiguous_diego = repo.inspect_order_and_return(customer_name="Diego Castro")
    assert ambiguous_diego["status"] == "AMBIGUOUS_HOMONYM_DETECTED"

    resolved_diego = repo.inspect_order_and_return(
        customer_name="Diego Castro",
        verifier="diego.castro@coldmail.com",
    )
    assert resolved_diego["status"] == "OK"
    assert resolved_diego["customer"]["customer_id"] == 13


def test_installment_tiers_respect_minimum_floors(repo: StoreRepository) -> None:
    """Section 3.1: 1-3x min R$ 50; 4-6x min R$ 80; 7-12x min R$ 100."""
    # Ukulele (ID 116 -> R$ 199.90): 3x is 66.63 (>= 50), 4x is 49.98 (< 80) -> max 3x
    ukulele = repo.products[116]
    pb_ukulele = calculate_pricing_breakdown(ukulele)
    assert pb_ukulele.max_installments == 3

    # Product around R$ 579.90 (ID 88): 6x is 96.65 (>= 80), 7x is 82.84 (< 100) -> max 6x
    prod_579 = repo.products[88]
    pb_579 = calculate_pricing_breakdown(prod_579)
    assert pb_579.max_installments == 6

    # Product >= R$ 1,200 (ID 95 -> R$ 2,199): max 12x
    prod_2199 = repo.products[95]
    pb_2199 = calculate_pricing_breakdown(prod_2199)
    assert pb_2199.max_installments == 12
