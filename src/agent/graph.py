"""LangGraph v0.3+ stateful conversational orchestrator for Empório da Música."""

from __future__ import annotations

from typing import Annotated, Any, TypedDict

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from src.agent.llm_factory import create_chat_model
from src.agent.prompts import build_system_prompt
from src.tools.store_tools import ALL_STORE_TOOLS

# Prompt injection heuristic patterns (OWASP LLM01 Defense-in-Depth)
_INJECTION_PATTERNS: tuple[str, ...] = (
    "ignore previous instructions",
    "ignore all previous instructions",
    "ignore as instrucoes anteriores",
    "ignore todas as instrucoes",
    "esqueça suas regras",
    "esqueca suas regras",
    "system prompt",
    "voce agora e dan",
    "jailbreak",
)


class AgentState(TypedDict):
    """Canonical LangGraph state using immutable add_messages reducer."""

    messages: Annotated[list[BaseMessage], add_messages]
    iteration_count: int


def _extract_text_content(content: Any) -> str:
    """Safely extract string text from AIMessage content (handles string or list of content blocks)."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict) and "text" in item:
                parts.append(str(item["text"]))
        return "\n".join(parts)
    return str(content or "")


def build_agent_graph(
    chat_model: BaseChatModel | None = None,
    checkpointer: MemorySaver | None = None,
    reference_date_str: str | None = None,
):
    """
    Construct and compile the Empório da Música LangGraph StateGraph.

    Follows strict langgraph-dev guardrails:
    - Uses StateGraph + Annotated[list[BaseMessage], add_messages]
    - Uses ToolNode + tools_condition
    - Enforces iteration_count guard to prevent infinite tool loops
    - Attaches MemorySaver checkpointer for multi-turn session state
    """
    llm = chat_model or create_chat_model()
    llm_with_tools = llm.bind_tools(ALL_STORE_TOOLS)
    system_prompt_text = build_system_prompt(reference_date_str=reference_date_str)

    def agent_node(state: AgentState) -> dict[str, Any]:
        """Primary reasoning node that invokes the tool-bound LLM."""
        current_iter = state.get("iteration_count", 0) + 1
        messages = state.get("messages", [])

        # Check last human message for direct prompt injection attempts (OWASP LLM01)
        if messages and isinstance(messages[-1], HumanMessage):
            user_text_lower = _extract_text_content(messages[-1].content).lower()
            if any(pat in user_text_lower for pat in _INJECTION_PATTERNS):
                safe_refusal = AIMessage(
                    content=(
                        "Opa, tudo bem? Eu sou o assistente virtual da **Empório da Música** e sigo "
                        "as diretrizes oficiais da nossa loja aqui em Campo Grande/MS! 🎸\n\n"
                        "Posso te ajudar a encontrar instrumentos musicais no nosso catálogo, consultar "
                        "preços, promoções, formas de pagamento, frete, status de pedidos ou nossas "
                        "políticas de troca e garantia. Como posso te ajudar com sua música hoje?"
                    )
                )
                return {"messages": [safe_refusal], "iteration_count": current_iter}

        # Ensure SystemMessage is prepended without mutating state in-place
        if not messages or not isinstance(messages[0], SystemMessage):
            full_messages: list[BaseMessage] = [
                SystemMessage(content=system_prompt_text),
                *messages,
            ]
        else:
            full_messages = list(messages)

        response = llm_with_tools.invoke(full_messages)
        return {"messages": [response], "iteration_count": current_iter}

    def route_after_agent(state: AgentState) -> str:
        """Route to 'tools' if tool_calls exist and iteration limit is respected, else END."""
        if state.get("iteration_count", 0) >= 8:
            return END
        return tools_condition(state)

    workflow = StateGraph(AgentState)
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", ToolNode(ALL_STORE_TOOLS))

    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges(
        "agent",
        route_after_agent,
        {"tools": "tools", END: END},
    )
    workflow.add_edge("tools", "agent")

    memory = checkpointer or MemorySaver()
    return workflow.compile(checkpointer=memory)


class EmporioMusicaAssistant:
    """High-level facade for interacting with the compiled LangGraph agent across sessions."""

    def __init__(
        self,
        chat_model: BaseChatModel | None = None,
        reference_date_str: str | None = None,
    ) -> None:
        self.memory = MemorySaver()
        self.reference_date_str = reference_date_str
        self.graph = build_agent_graph(
            chat_model=chat_model,
            checkpointer=self.memory,
            reference_date_str=reference_date_str,
        )

    def chat(self, user_message: str, thread_id: str = "default_session") -> dict[str, Any]:
        """
        Send a message to the agent within a thread_id session and return the response + tool trace.
        """
        config = {
            "configurable": {"thread_id": thread_id},
            "recursion_limit": 15,
        }

        prior_state = self.graph.get_state(config)
        prior_msg_count = len(prior_state.values.get("messages", [])) if prior_state and prior_state.values else 0

        result_state = self.graph.invoke(
            {
                "messages": [HumanMessage(content=user_message)],
                "iteration_count": 0,
            },
            config=config,
        )

        all_messages: list[BaseMessage] = result_state.get("messages", [])
        new_messages = all_messages[prior_msg_count:]

        tool_calls_trace: list[dict[str, Any]] = []
        for msg in new_messages:
            if isinstance(msg, AIMessage) and getattr(msg, "tool_calls", None):
                for tc in msg.tool_calls:
                    tool_calls_trace.append(
                        {
                            "tool_name": tc.get("name"),
                            "args": tc.get("args"),
                            "id": tc.get("id"),
                        }
                    )
            elif isinstance(msg, ToolMessage):
                # Attach preview of tool output to matching tool call
                for traced in tool_calls_trace:
                    if traced.get("id") == getattr(msg, "tool_call_id", None):
                        traced["output_preview"] = _extract_text_content(msg.content)[:500]

        final_ai_msg = next(
            (m for m in reversed(new_messages) if isinstance(m, AIMessage)),
            all_messages[-1] if all_messages else AIMessage(content=""),
        )
        answer_text = _extract_text_content(final_ai_msg.content)

        return {
            "thread_id": thread_id,
            "user_message": user_message,
            "answer": answer_text,
            "tool_calls": tool_calls_trace,
        }
