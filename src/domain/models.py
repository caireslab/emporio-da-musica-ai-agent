"""Pydantic v2 domain models representing Empório da Música operational entities."""

from __future__ import annotations

from datetime import date
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class Category(BaseModel):
    """Instrument category model from categories.csv."""

    model_config = ConfigDict(frozen=True)

    category_id: int
    name: str
    description: str


class Promotion(BaseModel):
    """Promotion campaign record from promotions.csv."""

    model_config = ConfigDict(frozen=True)

    promotion_id: int
    product_id: int
    discount_percent: int
    description: str
    is_active: bool


class Product(BaseModel):
    """Sanitized musical instrument product model from products.csv."""

    model_config = ConfigDict(frozen=True)

    product_id: int
    price_brl: float
    name: str
    category_id: int
    category_name: str
    description: str
    stock_quantity: int
    status: Literal["active", "discontinued", "coming_soon"]
    specs: dict[str, Any] = Field(default_factory=dict)
    created_at: date

    # Enriched deterministic attributes (RN-03, RN-04, RN-05)
    active_promotion: Promotion | None = None
    expired_promotions: list[Promotion] = Field(default_factory=list)
    effective_price_brl: float
    has_catalog_discrepancy: bool = False
    discrepancy_note: str | None = None

    @property
    def is_available_for_sale(self) -> bool:
        """Return True only if product is active and has physical stock > 0 (RN-06)."""
        return self.status == "active" and self.stock_quantity > 0


class Customer(BaseModel):
    """Customer record from customers.csv."""

    model_config = ConfigDict(frozen=True)

    customer_id: int
    name: str
    phone: str
    email: str
    city: str


class OrderItemDetail(BaseModel):
    """Enriched order item combining order_items.csv and products.csv."""

    model_config = ConfigDict(frozen=True)

    order_id: int
    product_id: int
    product_name: str
    category_name: str
    quantity: int
    current_unit_price_brl: float


class Order(BaseModel):
    """Customer order record from orders.csv."""

    model_config = ConfigDict(frozen=True)

    order_id: int
    customer_id: int
    order_date: date
    status: Literal["delivered", "shipped", "confirmed", "pending", "cancelled"]
    total_brl: float
    payment_method: str
    tracking_code: str | None = None
    estimated_delivery: date | None = None
    notes: str | None = None
    items: list[OrderItemDetail] = Field(default_factory=list)


class InstallmentOption(BaseModel):
    """Single credit card installment option."""

    model_config = ConfigDict(frozen=True)

    installments: int
    installment_value_brl: float
    total_brl: float
    min_installment_rule_brl: float


class PricingBreakdown(BaseModel):
    """Complete deterministic financial calculation for a product (RN-04, RN-07, RN-08)."""

    model_config = ConfigDict(frozen=True)

    table_price_brl: float
    has_active_promotion: bool
    active_promotion_description: str | None = None
    discount_percent: int = 0
    effective_price_brl: float
    pix_price_brl: float
    pix_discount_applied: bool
    pix_rule_explanation: str
    debit_price_brl: float
    boleto_price_brl: float
    max_installments: int
    installment_options: list[InstallmentOption] = Field(default_factory=list)
    allows_combined_payment: bool
    combined_payment_rule: str


class PolicySection(BaseModel):
    """Normalized section of the store policy manual (políticas_da_loja.pdf)."""

    model_config = ConfigDict(frozen=True)

    topic_key: str
    section_number: str
    title: str
    content: str
    key_rules: list[str]
