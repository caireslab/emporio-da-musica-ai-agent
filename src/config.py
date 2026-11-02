"""Configuration loader and constants for Empório da Música AI Agent."""

from __future__ import annotations

import os
from datetime import date
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent
DATA_DIR: Path = PROJECT_ROOT / "data"

CSV_FILES: dict[str, Path] = {
    "categories": DATA_DIR / "desafio_tecnico_ai_eng - categories.csv",
    "customers": DATA_DIR / "desafio_tecnico_ai_eng - customers.csv",
    "orders": DATA_DIR / "desafio_tecnico_ai_eng - orders.csv",
    "order_items": DATA_DIR / "desafio_tecnico_ai_eng - order_items.csv",
    "products": DATA_DIR / "desafio_tecnico_ai_eng - products.csv",
    "promotions": DATA_DIR / "desafio_tecnico_ai_eng - promotions.csv",
}

POLICY_PDF_PATH: Path = DATA_DIR / "políticas_da_loja.pdf"

# Store Operational Settings
DEFAULT_REFERENCE_DATE_STR: str = os.getenv("STORE_REFERENCE_DATE", "2026-03-25")

# LLM Provider Settings
LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "gemini").strip().lower()
LLM_MODEL: str = os.getenv("LLM_MODEL", "").strip()
LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.1"))

DEFAULT_MODELS: dict[str, str] = {
    "gemini": "gemini-2.5-flash",
    "openai": "gpt-4o-mini",
    "groq": "llama-3.3-70b-versatile",
}


def get_reference_date(override_date_str: str | None = None) -> date:
    """Parse and return the reference date used for return/warranty calculations."""
    target = (override_date_str or DEFAULT_REFERENCE_DATE_STR).strip()
    try:
        return date.fromisoformat(target)
    except ValueError:
        return date(2026, 3, 25)
