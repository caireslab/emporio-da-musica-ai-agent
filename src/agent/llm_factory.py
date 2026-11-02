"""Multi-provider LLM factory supporting Google Gemini, OpenAI, and Groq with retry resilience."""

from __future__ import annotations

import os
from typing import Any

from langchain_core.language_models.chat_models import BaseChatModel

from src.config import DEFAULT_MODELS, LLM_MODEL, LLM_PROVIDER, LLM_TEMPERATURE


class LLMConfigurationError(RuntimeError):
    """Raised when no valid API key or LLM provider is configured."""


def create_chat_model(
    provider: str | None = None,
    model_name: str | None = None,
    temperature: float | None = None,
) -> BaseChatModel:
    """
    Instantiate a LangChain v0.3+ BaseChatModel with built-in retry/backoff resilience.

    Supports:
    - 'gemini' (Default: gemini-2.5-flash via langchain-google-genai)
    - 'openai' (Default: gpt-4o-mini via langchain-openai)
    - 'groq'   (Default: llama-3.3-70b-versatile via langchain-groq)
    """
    selected_provider = (provider or LLM_PROVIDER or "gemini").strip().lower()
    temp = LLM_TEMPERATURE if temperature is None else temperature
    resolved_model = (
        model_name
        or LLM_MODEL
        or DEFAULT_MODELS.get(selected_provider, "gemini-2.5-flash")
    )

    if selected_provider == "gemini":
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key or api_key.startswith("sua_chave"):
            raise LLMConfigurationError(
                "Chave GEMINI_API_KEY (ou GOOGLE_API_KEY) não configurada no arquivo .env. "
                "Copie .env.example para .env e insira sua chave."
            )
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(
            model=resolved_model,
            google_api_key=api_key,
            temperature=temp,
            max_retries=3,
            timeout=30.0,
        )

    if selected_provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or api_key.startswith("sua_chave"):
            raise LLMConfigurationError(
                "Chave OPENAI_API_KEY não configurada no arquivo .env."
            )
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=resolved_model,
            api_key=api_key,
            temperature=temp,
            max_retries=3,
            timeout=30.0,
        )

    if selected_provider == "groq":
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key or api_key.startswith("sua_chave"):
            raise LLMConfigurationError(
                "Chave GROQ_API_KEY não configurada no arquivo .env."
            )
        from langchain_groq import ChatGroq

        return ChatGroq(
            model=resolved_model,
            api_key=api_key,
            temperature=temp,
            max_retries=3,
            timeout=30.0,
        )

    raise LLMConfigurationError(
        f"Provedor LLM '{selected_provider}' não suportado. Escolha entre: 'gemini', 'openai' ou 'groq'."
    )


def get_active_provider_info() -> dict[str, Any]:
    """Return metadata about the configured LLM provider and key readiness."""
    prov = (os.getenv("LLM_PROVIDER") or LLM_PROVIDER or "gemini").strip().lower()
    model = (os.getenv("LLM_MODEL") or LLM_MODEL or DEFAULT_MODELS.get(prov, "gemini-2.5-flash")).strip()
    key_map = {
        "gemini": os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"),
        "openai": os.getenv("OPENAI_API_KEY"),
        "groq": os.getenv("GROQ_API_KEY"),
    }
    raw_key = key_map.get(prov, "")
    has_valid_key = bool(raw_key and not raw_key.startswith("sua_chave"))
    return {
        "provider": prov,
        "model": model,
        "has_valid_api_key": has_valid_key,
    }
