"""Streamlit Web Interface for the Empório da Música AI Agent."""

from __future__ import annotations

import uuid

import streamlit as st

from src.agent.graph import EmporioMusicaAssistant

SUGGESTED_PROMPTS: list[tuple[str, str]] = [
    ("🎸 Violões até R$ 1.000", "Quais opções de violões disponíveis custando até R$1000?"),
    ("📍 Endereço e Horários", "Qual o endereço da loja e os horários de funcionamento?"),
    ("💰 Preço do Takamine GD20", "Quanto custa o Takamine GD20? Posso parcelar ou pagar no PIX?"),
    ("🔄 Devolução por Arrependimento", "Me arrependi da minha compra, posso devolver meu pedido?"),
    ("🛡️ Caso Homônimo LGPD", "Quero consultar o pedido em nome de Bruno Martins."),
]


@st.cache_resource(show_spinner=False)
def _get_cached_assistant() -> EmporioMusicaAssistant:
    """Create and cache a single EmporioMusicaAssistant instance across reruns."""
    return EmporioMusicaAssistant()


def render_streamlit_app() -> None:
    """Render the Streamlit conversational workspace."""
    st.set_page_config(
        page_title="Empório da Música — Assistente Virtual",
        page_icon="🎸",
        layout="wide",
    )

    if "thread_id" not in st.session_state:
        st.session_state.thread_id = f"web-{uuid.uuid4().hex[:8]}"
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {
                "role": "assistant",
                "content": (
                    "Olá! Que bom ter você aqui no **Empório da Música**! 🎶\n\n"
                    "Sou o assistente virtual da loja e posso te ajudar a encontrar seu próximo "
                    "instrumento musical, simular descontos no PIX e parcelamentos sem juros, "
                    "calcular frete, tirar dúvidas sobre trocas/garantia ou consultar seus pedidos.\n\n"
                    "Como posso te ajudar hoje?"
                ),
                "tool_calls": [],
            }
        ]

    with st.sidebar:
        st.title("🎸 Empório da Música")
        st.caption("Rua 14 de Maio, 3200 — Centro, Campo Grande/MS")
        st.divider()

        st.subheader("Atalhos do Desafio")
        selected_prompt: str | None = None
        for label, prompt_text in SUGGESTED_PROMPTS:
            if st.button(label, use_container_width=True):
                selected_prompt = prompt_text

        st.divider()
        if st.button("🗑️ Nova Conversa", use_container_width=True):
            st.session_state.thread_id = f"web-{uuid.uuid4().hex[:8]}"
            st.session_state.chat_history = st.session_state.chat_history[:1]
            st.rerun()

        st.caption(f"Sessão ativa: `{st.session_state.thread_id}`")

    st.title("🎶 Atendimento Virtual — Empório da Música")
    st.caption(
        "Agente Conversacional Híbrido (LangGraph + Catálogo CSV em Tempo Real + Políticas da Loja)"
    )

    for entry in st.session_state.chat_history:
        with st.chat_message(entry["role"]):
            st.markdown(entry["content"])
            tool_calls = entry.get("tool_calls") or []
            if tool_calls:
                with st.expander(f"🔧 Ferramentas consultadas ({len(tool_calls)})"):
                    st.json(tool_calls)

    user_message = st.chat_input("Digite sua dúvida sobre instrumentos, preços, pedidos ou políticas...")
    active_prompt = selected_prompt or user_message

    if active_prompt:
        st.session_state.chat_history.append(
            {"role": "user", "content": active_prompt, "tool_calls": []}
        )
        with st.chat_message("user"):
            st.markdown(active_prompt)

        with (
            st.chat_message("assistant"),
            st.spinner("Consultando catálogo e políticas do Empório da Música..."),
        ):
            try:
                assistant = _get_cached_assistant()
                result = assistant.chat(
                    active_prompt,
                    thread_id=st.session_state.thread_id,
                )
                response_text = result.get("answer") or result.get("response") or ""
                tool_calls = result.get("tool_calls", [])
            except (RuntimeError, ValueError, OSError) as exc:
                response_text = (
                    f"⚠️ **Erro de configuração do provedor LLM:** `{exc}`\n\n"
                    "Certifique-se de configurar sua chave (`GEMINI_API_KEY`, `OPENAI_API_KEY` "
                    "ou `GROQ_API_KEY`) no arquivo `.env`."
                )
                tool_calls = []

            st.markdown(response_text)
            if tool_calls:
                with st.expander(f"🔧 Ferramentas consultadas ({len(tool_calls)})"):
                    st.json(tool_calls)

        st.session_state.chat_history.append(
            {
                "role": "assistant",
                "content": response_text,
                "tool_calls": tool_calls,
            }
        )
        if selected_prompt:
            st.rerun()


if __name__ == "__main__":  # pragma: no cover
    render_streamlit_app()
