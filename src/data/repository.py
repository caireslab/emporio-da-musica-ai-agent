"""Read-Only In-Memory Store Repository with data sanitization and LGPD homonym protection."""

from __future__ import annotations

import csv
import json
import re
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

from src.config import CSV_FILES, get_reference_date
from src.domain.models import (
    Category,
    Customer,
    Order,
    OrderItemDetail,
    Product,
    Promotion,
)
from src.domain.rules import (
    CATALOG_DISCREPANCY_NOTES,
    OUT_OF_SCOPE_ACCESSORIES,
    calculate_pricing_breakdown,
    evaluate_order_return_and_warranty,
    normalize_text,
)


def _digits_only(val: str) -> str:
    """Extract only numeric digits from a string."""
    return re.sub(r"\D", "", val or "")


class StoreRepository:
    """
    Read-Only Repository loading and sanitizing all 6 CSV tables of Empório da Música.

    Implements:
    - RN-01: Out-of-scope accessory detection.
    - RN-03: Catalog discrepancy detection and transparency notes (IDs 135-144).
    - RN-04 / RN-05: Active vs expired promotions and effective price computation.
    - RN-06: Stock and status handling (`active`, `discontinued`, `coming_soon`) + substitutes.
    - RN-10: LGPD homonym disambiguation for customer orders (`Bruno Martins`, `Diego Castro`).
    """

    def __init__(self, csv_paths: dict[str, Path] | None = None) -> None:
        self.csv_paths = csv_paths or CSV_FILES
        self.categories: dict[int, Category] = {}
        self.promotions_by_product: dict[int, list[Promotion]] = {}
        self.products: dict[int, Product] = {}
        self.customers: dict[int, Customer] = {}
        self.orders: dict[int, Order] = {}
        self.registered_protocols: list[dict[str, Any]] = []

        self._load_all()

    def _load_all(self) -> None:
        """Load and sanitize all CSV datasets in strict Read-Only mode."""
        # 1. Categories
        with open(self.csv_paths["categories"], mode="r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                cat = Category(
                    category_id=int(row["category_id"]),
                    name=row["name"].strip(),
                    description=row["description"].strip(),
                )
                self.categories[cat.category_id] = cat

        # 2. Promotions
        with open(self.csv_paths["promotions"], mode="r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                promo = Promotion(
                    promotion_id=int(row["promotion_id"]),
                    product_id=int(row["product_id"]),
                    discount_percent=int(row["discount_percent"]),
                    description=row["description"].strip(),
                    is_active=bool(int(row["is_active"])),
                )
                self.promotions_by_product.setdefault(promo.product_id, []).append(promo)

        # 3. Products (with sanitization for IDs 135-144 and effective_price_brl)
        with open(self.csv_paths["products"], mode="r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                pid = int(row["product_id"])
                price = float(row["price_brl"])
                cat_id = int(row["category_id"])
                cat_name = self.categories[cat_id].name if cat_id in self.categories else "Outros"

                raw_specs = row.get("specs", "{}")
                try:
                    specs_dict = json.loads(raw_specs) if raw_specs else {}
                except json.JSONDecodeError:
                    specs_dict = {}

                prod_promos = self.promotions_by_product.get(pid, [])
                active_promos = [p for p in prod_promos if p.is_active]
                expired_promos = [p for p in prod_promos if not p.is_active]
                active_promo = active_promos[0] if active_promos else None

                effective_price = (
                    round(price * (1.0 - active_promo.discount_percent / 100.0), 2)
                    if active_promo
                    else round(price, 2)
                )

                discrepancy_note = CATALOG_DISCREPANCY_NOTES.get(pid)
                has_discrepancy = pid in (135, 136, 137, 139, 140, 142, 144)

                prod = Product(
                    product_id=pid,
                    price_brl=price,
                    name=row["name"].strip(),
                    category_id=cat_id,
                    category_name=cat_name,
                    description=row["description"].strip(),
                    stock_quantity=int(row["stock_quantity"]),
                    status=row["status"].strip(),  # type: ignore[arg-type]
                    specs=specs_dict,
                    created_at=date.fromisoformat(row["created_at"].strip()),
                    active_promotion=active_promo,
                    expired_promotions=expired_promos,
                    effective_price_brl=effective_price,
                    has_catalog_discrepancy=has_discrepancy,
                    discrepancy_note=discrepancy_note,
                )
                self.products[pid] = prod

        # 4. Customers
        with open(self.csv_paths["customers"], mode="r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                cust = Customer(
                    customer_id=int(row["customer_id"]),
                    name=row["name"].strip(),
                    phone=row["phone"].strip(),
                    email=row["email"].strip(),
                    city=row["city"].strip(),
                )
                self.customers[cust.customer_id] = cust

        # 5. Order Items grouped by order_id
        items_by_order: dict[int, list[OrderItemDetail]] = {}
        with open(self.csv_paths["order_items"], mode="r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                oid = int(row["order_id"])
                pid = int(row["product_id"])
                qty = int(row["quantity"])
                prod_obj = self.products.get(pid)
                item_detail = OrderItemDetail(
                    order_id=oid,
                    product_id=pid,
                    product_name=prod_obj.name if prod_obj else f"Produto #{pid}",
                    category_name=prod_obj.category_name if prod_obj else "Desconhecida",
                    quantity=qty,
                    current_unit_price_brl=prod_obj.price_brl if prod_obj else 0.0,
                )
                items_by_order.setdefault(oid, []).append(item_detail)

        # 6. Orders
        with open(self.csv_paths["orders"], mode="r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                oid = int(row["order_id"])
                est_del_str = (row.get("estimated_delivery") or "").strip()
                est_del = date.fromisoformat(est_del_str) if est_del_str else None
                tracking = (row.get("tracking_code") or "").strip() or None
                notes = (row.get("notes") or "").strip() or None

                order = Order(
                    order_id=oid,
                    customer_id=int(row["customer_id"]),
                    order_date=date.fromisoformat(row["order_date"].strip()),
                    status=row["status"].strip(),  # type: ignore[arg-type]
                    total_brl=float(row["total_brl"]),
                    payment_method=row["payment_method"].strip(),
                    tracking_code=tracking,
                    estimated_delivery=est_del,
                    notes=notes,
                    items=items_by_order.get(oid, []),
                )
                self.orders[oid] = order

    # -------------------------------------------------------------------------
    # Catalog & Pricing Queries
    # -------------------------------------------------------------------------
    def _serialize_product_summary(self, prod: Product) -> dict[str, Any]:
        """Serialize a product with its pricing and promotion summary."""
        pricing = calculate_pricing_breakdown(prod)
        return {
            "product_id": prod.product_id,
            "name": prod.name,
            "category_id": prod.category_id,
            "category_name": prod.category_name,
            "status": prod.status,
            "stock_quantity": prod.stock_quantity,
            "is_available_for_sale": prod.is_available_for_sale,
            "table_price_brl": prod.price_brl,
            "effective_price_brl": prod.effective_price_brl,
            "pix_price_brl": pricing.pix_price_brl,
            "pix_discount_applied": pricing.pix_discount_applied,
            "max_installments": pricing.max_installments,
            "active_promotion": (
                {
                    "discount_percent": prod.active_promotion.discount_percent,
                    "description": prod.active_promotion.description,
                }
                if prod.active_promotion
                else None
            ),
            "expired_promotions_count": len(prod.expired_promotions),
            "specs": prod.specs,
            "description": prod.description,
            "has_catalog_discrepancy": prod.has_catalog_discrepancy,
            "discrepancy_note": prod.discrepancy_note,
        }

    def get_available_alternatives(
        self,
        category_id: int,
        exclude_product_id: int | None = None,
        target_price_brl: float | None = None,
        limit: int = 3,
    ) -> list[dict[str, Any]]:
        """Find available substitute instruments in the same category (Section 7.3 / RN-06)."""
        candidates = [
            p
            for p in self.products.values()
            if p.category_id == category_id
            and p.is_available_for_sale
            and p.product_id != exclude_product_id
        ]
        if target_price_brl is not None:
            candidates.sort(key=lambda p: abs(p.effective_price_brl - target_price_brl))
        else:
            candidates.sort(key=lambda p: p.effective_price_brl)
        return [self._serialize_product_summary(p) for p in candidates[:limit]]

    def resolve_category_ids(self, category_query: str) -> list[int]:
        """Match a natural language category or instrument family to category_ids."""
        norm = normalize_text(category_query)
        if not norm:
            return []

        synonyms: dict[int, tuple[str, ...]] = {
            1: ("guitarra", "guitarras", "stratocaster", "les paul", "telecaster", "rg550", "prs"),
            2: ("baixo", "baixos", "contrabaixo", "jazz bass", "precision", "stingray"),
            3: ("bateria", "baterias", "percussao"),
            4: ("teclado", "teclados", "piano", "pianos", "sintetizador", "synth", "arranjador", "midi"),
            5: ("violao", "violoes", "dreadnought", "folk", "classico", "7 cordas", "eletroacustico"),
            6: ("sopro", "madeira", "madeiras", "flauta", "clarinete", "saxofone", "sax", "oboe", "boquilha"),
            7: ("metal", "metais", "trompete", "trombone", "tuba", "trompa"),
            8: ("orquestral", "orquestrais", "violino", "viola de arco", "violoncelo", "cello"),
            9: ("ukulele", "ukuleles", "soprano", "concert", "tenor", "baritono"),
        }

        matched_ids: list[int] = []
        for cid, cat in self.categories.items():
            if norm in normalize_text(cat.name) or norm in normalize_text(cat.description):
                matched_ids.append(cid)
                continue
            if any(syn in norm for syn in synonyms.get(cid, ())):
                matched_ids.append(cid)
        return sorted(set(matched_ids))

    def search_catalog(
        self,
        category: str | None = None,
        search_query: str | None = None,
        max_price_brl: float | None = None,
        min_price_brl: float | None = None,
        strings_type: str | None = None,
        has_electronics: bool | None = None,
        only_promotions: bool = False,
        include_unavailable: bool = False,
    ) -> dict[str, Any]:
        """
        Search and filter the musical instrument catalog deterministically (RN-01 to RN-06).
        """
        combined_query = normalize_text(f"{category or ''} {search_query or ''}")

        # Check if user is explicitly asking for out-of-scope accessories (RN-01)
        matched_accessories = [acc for acc in OUT_OF_SCOPE_ACCESSORIES if acc in combined_query]
        # Avoid false positive if user asked for "violao cordas de nylon" or "violao 7 cordas"
        if matched_accessories and not any(
            inst in combined_query
            for inst in ("violao", "violoes", "ukulele", "guitarra", "baixo", "bateria", "teclado")
        ):
            return {
                "status": "OUT_OF_SCOPE_ACCESSORY",
                "detected_terms": matched_accessories,
                "policy_rule": (
                    "A Empório da Música trabalha EXCLUSIVAMENTE com instrumentos musicais. "
                    "Não comercializamos acessórios como cordas avulsas, palhetas, cabos, cases, "
                    "pedais ou amplificadores (Seções 1 e 7.1 do Manual). Redirecione o cliente "
                    "educadamente e sugira procurar lojas parceiras de acessórios."
                ),
                "available_products": [],
            }

        target_cat_ids = self.resolve_category_ids(category or search_query or "")

        # Check if query maps exclusively to empty categories 6, 7, or 8
        if target_cat_ids and all(cid in (6, 7, 8) for cid in target_cat_ids):
            empty_cats = [self.categories[cid].model_dump() for cid in target_cat_ids]
            return {
                "status": "CATEGORY_TEMPORARILY_WITHOUT_STOCK",
                "categories_matched": empty_cats,
                "explanation": (
                    "As categorias de Instrumentos de Sopro (Madeiras e Metais) e Cordas Orquestrais "
                    "fazem parte do catálogo institucional da Empório da Música, porém no momento não "
                    "há modelos com saldo cadastrado no sistema online. Ofereça registrar uma consulta "
                    "de encomenda junto à gerência (prazo de 24h úteis) ou apresente nossas categorias "
                    "com pronta entrega (Violões, Ukuleles, Guitarras, Baixos, Baterias e Teclados)."
                ),
                "available_products": [],
            }

        results: list[Product] = list(self.products.values())

        if category:
            cat_ids = self.resolve_category_ids(category)
            if cat_ids:
                results = [p for p in results if p.category_id in cat_ids]

        if search_query:
            norm_q = normalize_text(search_query)
            # Ignore generic words that are already covered by category
            tokens = [
                t
                for t in re.split(r"\s+", norm_q)
                if t
                and t
                not in {
                    "violao",
                    "violoes",
                    "guitarra",
                    "guitarras",
                    "baixo",
                    "baixos",
                    "bateria",
                    "baterias",
                    "teclado",
                    "teclados",
                    "ukulele",
                    "ukuleles",
                    "instrumento",
                    "instrumentos",
                    "de",
                    "com",
                    "para",
                    "ate",
                }
            ]
            if tokens:
                filtered_by_tokens = [
                    p
                    for p in results
                    if all(
                        tok in normalize_text(p.name)
                        or tok in normalize_text(p.description)
                        or tok in normalize_text(json.dumps(p.specs, ensure_ascii=False))
                        or tok in normalize_text(p.category_name)
                        for tok in tokens
                    )
                ]
                if filtered_by_tokens or not target_cat_ids:
                    results = filtered_by_tokens

        if strings_type:
            norm_str = normalize_text(strings_type)
            if "nylon" in norm_str:
                results = [p for p in results if normalize_text(str(p.specs.get("strings", ""))) == "nylon"]
            elif "aco" in norm_str or "steel" in norm_str:
                results = [p for p in results if normalize_text(str(p.specs.get("strings", ""))) == "steel"]
            elif "7" in norm_str:
                results = [p for p in results if "7 cordas" in normalize_text(p.name)]

        if has_electronics is not None:
            expected = "yes" if has_electronics else "no"
            results = [p for p in results if normalize_text(str(p.specs.get("electronics", ""))) == expected]

        if only_promotions:
            results = [p for p in results if p.active_promotion is not None]

        # RN-05: Filter budget against effective_price_brl (which includes active promotions)
        if max_price_brl is not None:
            results = [p for p in results if p.effective_price_brl <= max_price_brl]

        if min_price_brl is not None:
            results = [p for p in results if p.effective_price_brl >= min_price_brl]

        available = [p for p in results if p.is_available_for_sale]
        unavailable = [p for p in results if not p.is_available_for_sale]

        available.sort(key=lambda p: p.effective_price_brl)

        response: dict[str, Any] = {
            "status": "OK",
            "total_available_found": len(available),
            "available_products": [self._serialize_product_summary(p) for p in available],
        }

        if include_unavailable or (not available and unavailable):
            response["unavailable_or_discontinued_matches"] = [
                {
                    **self._serialize_product_summary(u),
                    "suggested_alternatives": self.get_available_alternatives(
                        u.category_id, exclude_product_id=u.product_id, target_price_brl=u.effective_price_brl
                    ),
                }
                for u in unavailable
            ]
        elif unavailable:
            response["excluded_unavailable_items_note"] = [
                {
                    "product_id": u.product_id,
                    "name": u.name,
                    "status": u.status,
                    "stock_quantity": u.stock_quantity,
                    "reason_excluded": (
                        "Fora de estoque (stock_quantity = 0)"
                        if u.status == "active"
                        else f"Status '{u.status}' (não disponível para pronta entrega)"
                    ),
                }
                for u in unavailable
            ]

        return response

    def get_product_pricing_details(self, product_query: str) -> dict[str, Any]:
        """
        Retrieve complete pricing, promotion, PIX, and installment breakdown for a specific product.
        """
        q = product_query.strip()
        matched_product: Product | None = None

        if q.isdigit() and int(q) in self.products:
            matched_product = self.products[int(q)]
        else:
            norm_q = normalize_text(q)
            # 1. Exact or substring match in product name
            name_matches = [
                p for p in self.products.values() if norm_q in normalize_text(p.name)
            ]
            if len(name_matches) == 1:
                matched_product = name_matches[0]
            elif len(name_matches) > 1:
                # Pick closest length match
                name_matches.sort(key=lambda p: len(p.name))
                matched_product = name_matches[0]
            else:
                # Token match
                tokens = [t for t in re.split(r"\s+", norm_q) if len(t) >= 2]
                token_matches = [
                    p
                    for p in self.products.values()
                    if tokens and all(tok in normalize_text(f"{p.name} {p.description}") for tok in tokens)
                ]
                if token_matches:
                    matched_product = token_matches[0]

        if not matched_product:
            return {
                "status": "PRODUCT_NOT_FOUND",
                "query": product_query,
                "message": (
                    f"Nenhum instrumento encontrado para '{product_query}'. "
                    "Use search_products_catalog para listar opções por categoria ou faixa de preço."
                ),
            }

        pricing = calculate_pricing_breakdown(matched_product)
        availability_reason = "Disponível em estoque para pronta entrega."
        if matched_product.status == "discontinued":
            availability_reason = (
                "PRODUTO DESCONTINUADO: Não faz mais parte do catálogo ativo da loja (Seção 7.3). "
                "Apresente os modelos equivalentes disponíveis abaixo."
            )
        elif matched_product.status == "coming_soon":
            availability_reason = (
                "PRODUTO EM PRÉ-LANÇAMENTO ('coming_soon'): Ainda não disponível para pronta entrega imediata. "
                "Apresente as alternativas disponíveis abaixo."
            )
        elif matched_product.stock_quantity <= 0:
            availability_reason = (
                "PRODUTO FORA DE ESTOQUE (stock_quantity = 0): Temporariamente indisponível (Seção 7.3). "
                "Nunca confirme disponibilidade sem estoque; sugira as alternativas abaixo."
            )

        alternatives = (
            self.get_available_alternatives(
                matched_product.category_id,
                exclude_product_id=matched_product.product_id,
                target_price_brl=matched_product.effective_price_brl,
            )
            if not matched_product.is_available_for_sale
            else []
        )

        return {
            "status": "OK",
            "product": self._serialize_product_summary(matched_product),
            "availability_verdict": availability_reason,
            "active_promotion": (
                matched_product.active_promotion.model_dump()
                if matched_product.active_promotion
                else None
            ),
            "expired_promotions": [
                {
                    **ep.model_dump(),
                    "policy_warning": (
                        f"A promoção '{ep.description}' ({ep.discount_percent}% OFF) está EXPIRADA "
                        "(is_active = 0). Informe com transparência que venceu e apresente o preço atual."
                    ),
                }
                for ep in matched_product.expired_promotions
            ],
            "pricing_breakdown": pricing.model_dump(),
            "suggested_alternatives": alternatives,
        }

    # -------------------------------------------------------------------------
    # Customer Orders, LGPD Homonym Disambiguation & Return Eligibility
    # -------------------------------------------------------------------------
    def inspect_order_and_return(
        self,
        order_id: int | None = None,
        customer_name: str | None = None,
        verifier: str | None = None,
        reference_date_str: str | None = None,
    ) -> dict[str, Any]:
        """
        Inspect order status, tracking, and return/warranty eligibility with strict LGPD homonym protection (RN-10).
        """
        ref_date = get_reference_date(reference_date_str)

        # Case 1: Lookup by explicit order_id
        if order_id is not None:
            order = self.orders.get(order_id)
            if not order:
                return {
                    "status": "ORDER_NOT_FOUND",
                    "order_id": order_id,
                    "message": f"Pedido #{order_id} não encontrado na base de pedidos da Empório da Música (IDs válidos: 1 a 20).",
                }
            customer = self.customers.get(order.customer_id)
            # Check if customer is one of the homonym pairs and a conflicting name was passed
            if customer_name and customer:
                norm_cname = normalize_text(customer_name)
                if norm_cname not in normalize_text(customer.name) and not any(
                    part in normalize_text(customer.name) for part in norm_cname.split()
                ):
                    return {
                        "status": "VERIFICATION_MISMATCH",
                        "message": (
                            f"Por segurança e proteção de dados (LGPD), o nome informado ('{customer_name}') "
                            f"não corresponde ao titular registrado no Pedido #{order_id}. Solicite confirmação "
                            "do telefone ou e-mail do titular."
                        ),
                    }
            return self._build_order_report(customer, [order], ref_date)

        # Case 2: Lookup by customer_name and/or verifier (phone, email, city)
        if not customer_name and not verifier:
            return {
                "status": "MISSING_IDENTIFIER",
                "message": (
                    "Para consultar um pedido ou verificar o prazo exato de devolução/garantia, "
                    "solicite ao cliente o número do pedido (order_id) ou o nome completo acompanhado "
                    "do telefone ou e-mail cadastrado."
                ),
            }

        candidates = list(self.customers.values())
        if customer_name:
            norm_name = normalize_text(customer_name)
            name_tokens = [t for t in norm_name.split() if len(t) >= 2]
            exact_matches = [c for c in candidates if normalize_text(c.name) == norm_name]
            token_matches = [
                c
                for c in candidates
                if all(tok in normalize_text(c.name) for tok in name_tokens)
            ]
            # If exact match is still ambiguous with partial homonyms (e.g. "Bruno Martins" matches ID 43 exact and ID 11 token)
            if len(token_matches) > 1:
                candidates = token_matches
            elif exact_matches:
                candidates = exact_matches
            else:
                candidates = token_matches

        if verifier:
            norm_ver = normalize_text(verifier)
            ver_digits = _digits_only(verifier)
            filtered_by_ver = [
                c
                for c in candidates
                if (ver_digits and len(ver_digits) >= 4 and ver_digits in _digits_only(c.phone))
                or (norm_ver in normalize_text(c.email))
                or (norm_ver in normalize_text(c.city))
                or (norm_ver in normalize_text(c.name))
            ]
            if filtered_by_ver:
                candidates = filtered_by_ver
            else:
                return {
                    "status": "VERIFIER_NOT_MATCHED",
                    "message": (
                        f"Não foi possível confirmar o cadastro para '{customer_name or ''}' com o "
                        f"identificador adicional '{verifier}'. Solicite o número do pedido ou o telefone exato."
                    ),
                }

        if not candidates:
            return {
                "status": "CUSTOMER_NOT_FOUND",
                "message": f"Nenhum cliente encontrado com os dados informados ('{customer_name or verifier}').",
            }

        # LGPD Homonym Guardrail (RN-10): e.g., Bruno Martins (IDs 11 and 43) or Diego Castro (IDs 13 and 47)
        if len(candidates) > 1:
            return {
                "status": "AMBIGUOUS_HOMONYM_DETECTED",
                "lgpd_security_block": True,
                "matched_count": len(candidates),
                "message": (
                    f"PROTEÇÃO LGPD (Homônimos Detectados): Encontramos {len(candidates)} cadastros "
                    f"compatíveis com o nome '{customer_name}'. Para proteger a privacidade dos dados "
                    "pessoais (Seção 9 do Manual - LGPD), NÃO exiba dados de pedidos ainda. "
                    "Peça gentilmente ao cliente para confirmar o número do pedido, o telefone com DDD "
                    "ou o nome completo com o nome do meio."
                ),
            }

        matched_customer = candidates[0]
        customer_orders = [
            o for o in self.orders.values() if o.customer_id == matched_customer.customer_id
        ]
        customer_orders.sort(key=lambda o: o.order_date, reverse=True)

        return self._build_order_report(matched_customer, customer_orders, ref_date)

    def _build_order_report(
        self, customer: Customer | None, orders: list[Order], ref_date: date
    ) -> dict[str, Any]:
        """Build a detailed order status and return/warranty eligibility report."""
        orders_payload = []
        for o in orders:
            eligibility = evaluate_order_return_and_warranty(o, ref_date)
            orders_payload.append(
                {
                    "order_id": o.order_id,
                    "order_date": o.order_date.isoformat(),
                    "status": o.status,
                    "total_brl": o.total_brl,
                    "payment_method": o.payment_method,
                    "tracking_code": o.tracking_code,
                    "estimated_delivery": (
                        o.estimated_delivery.isoformat() if o.estimated_delivery else None
                    ),
                    "notes": o.notes,
                    "items": [item.model_dump() for item in o.items],
                    "return_and_warranty_eligibility": eligibility,
                }
            )

        return {
            "status": "OK",
            "reference_date_used": ref_date.isoformat(),
            "customer": customer.model_dump() if customer else None,
            "total_orders_found": len(orders_payload),
            "orders": orders_payload,
            "message": (
                "Cliente localizado, porém não há pedidos registrados para este cadastro."
                if not orders_payload
                else f"Encontrados {len(orders_payload)} pedido(s) para o cliente."
            ),
        }

    # -------------------------------------------------------------------------
    # Complaint & Management Handover Protocol (Section 7.3 & 10 / RN-13)
    # -------------------------------------------------------------------------
    def register_protocol(
        self,
        customer_identifier: str,
        category: str,
        summary: str,
        order_id: int | None = None,
    ) -> dict[str, Any]:
        """Register a structured complaint or management escalation with a 24-business-hour SLA."""
        seq = len(self.registered_protocols) + 1
        protocol_id = f"EMP-2026-{seq:04d}"
        record = {
            "protocol_id": protocol_id,
            "registered_at": datetime.now(tz=UTC).isoformat(timespec="seconds"),
            "customer_identifier": customer_identifier,
            "category": category,
            "order_id": order_id,
            "summary": summary,
            "sla_return_deadline": "24 horas úteis",
            "status": "ENCAMINHADO_AO_RESPONSAVEL",
        }
        self.registered_protocols.append(record)
        return {
            "status": "PROTOCOL_REGISTERED",
            "protocol": record,
            "instructions_to_agent": (
                f"Protocolo {protocol_id} registrado com sucesso e encaminhado à gerência/responsável. "
                "Informe o número do protocolo ao cliente com empatia e confirme que o retorno ocorrerá "
                "em até 24 horas úteis (conforme Seção 7.3 do Manual de Políticas)."
            ),
        }


# Global Singleton Repository Instance
_STORE_REPO_INSTANCE: StoreRepository | None = None


def get_store_repository() -> StoreRepository:
    """Return the singleton StoreRepository instance."""
    global _STORE_REPO_INSTANCE
    if _STORE_REPO_INSTANCE is None:
        _STORE_REPO_INSTANCE = StoreRepository()
    return _STORE_REPO_INSTANCE
