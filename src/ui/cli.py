"""Rich-based Interactive CLI and Demo Scenario Runner for Empório da Música."""

from __future__ import annotations

import argparse
import sys
import uuid
from collections.abc import Sequence

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from src.agent.graph import EmporioMusicaAssistant
from src.agent.llm_factory import get_active_provider_info
from src.config import DATA_DIR

DEMO_SCENARIOS: list[tuple[str, list[str]]] = [
    (
        "Cenário 1 — Catálogo de Violões até R$ 1.000",
        ["Quais opções de violões disponíveis custando até R$1000?"],
    ),
    (
        "Cenário 2 — Preço do Takamine GD20 e Promoção Expirada",
        [
            "Quanto custa o Takamine GD20? Vi que tinha uma promoção de 12% nele, ainda consigo usar junto com o desconto do PIX?"
        ],
    ),
    (
        "Cenário 3 — Endereço da Loja, Horários e Frete",
        [
            "Qual o endereço e horário de funcionamento da loja? E quanto fica o frete de uma guitarra de R$ 2.500 para Campo Grande?"
        ],
    ),
    (
        "Cenário 4 — Arrependimento e Devolução de Pedido",
        [
            "Me arrependi da minha compra, posso devolver meu pedido? Meu pedido é o #8, está em trânsito."
        ],
    ),
    (
        "Cenário 5 — Multi-Turn: Escopo de Acessórios + Homônimos LGPD",
        [
            "Vocês têm encordoamento de aço 0.10 e correia pra violão? Aproveitando, quero ver o status do pedido em nome de Bruno Martins.",
            "O meu telefone é (67) 98543-2109, sou o Bruno Carvalho Martins.",
        ],
    ),
]


def _render_tool_calls(console: Console, tool_calls: Sequence[dict]) -> None:
    """Render a compact summary table of tools invoked during the turn."""
    if not tool_calls:
        return
    table = Table(
        title="Ferramentas Acionadas pelo Agente (LangGraph ToolNode)",
        show_header=True,
        header_style="bold cyan",
        border_style="dim",
    )
    table.add_column("#", style="dim", width=3)
    table.add_column("Tool Name", style="bold yellow")
    table.add_column("Arguments", style="green")

    for idx, call in enumerate(tool_calls, start=1):
        tool_name = call.get("tool_name") or call.get("name") or ""
        table.add_row(str(idx), str(tool_name), str(call.get("args", {})))

    console.print(table)


def run_demo_scenarios(assistant: EmporioMusicaAssistant, console: Console) -> None:
    """Execute the 5 showcase scenarios and print formatted responses."""
    console.print(
        Panel(
            "[bold green]Modo Demonstração — Executando 5 Cenários Reais do Desafio[/bold green]",
            border_style="green",
        )
    )
    for title, turns in DEMO_SCENARIOS:
        thread_id = f"demo-{uuid.uuid4().hex[:8]}"
        console.rule(f"[bold magenta]{title}[/bold magenta]")
        for user_msg in turns:
            console.print(f"\n[bold cyan]Cliente:[/bold cyan] {user_msg}")
            result = assistant.chat(user_msg, thread_id=thread_id)
            _render_tool_calls(console, result.get("tool_calls", []))
            answer_text = result.get("answer") or result.get("response") or ""
            console.print(
                Panel(
                    Markdown(answer_text),
                    title="[bold yellow]Empório da Música[/bold yellow]",
                    border_style="yellow",
                )
            )


def run_interactive_cli(argv: Sequence[str] | None = None) -> int:
    """Entrypoint for the terminal chat and CLI flags."""
    parser = argparse.ArgumentParser(
        description="Agente Conversacional de IA — Empório da Música (Campo Grande/MS)"
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Executa automaticamente os 5 cenários de demonstração do desafio.",
    )
    parser.add_argument(
        "--thread-id",
        default=f"cli-{uuid.uuid4().hex[:8]}",
        help="Identificador da sessão de conversa (thread_id do MemorySaver).",
    )
    parser.add_argument(
        "--query",
        type=str,
        default=None,
        help="Executa uma pergunta única e encerra.",
    )
    args = parser.parse_args(argv)

    console = Console()
    provider_info = get_active_provider_info()

    console.print(
        Panel.fit(
            "[bold yellow]🎸 Empório da Música — Assistente Virtual[/bold yellow]\n"
            "[dim]Rua 14 de Maio, 3200 — Centro, Campo Grande/MS[/dim]\n"
            f"[dim]Provider: {provider_info['provider']} ({provider_info['model']}) | Data Dir: {DATA_DIR.name}[/dim]",
            border_style="yellow",
        )
    )

    try:
        assistant = EmporioMusicaAssistant()
    except (RuntimeError, ValueError, OSError) as exc:  # pragma: no cover - defensive CLI message
        console.print(
            Panel(
                f"[bold red]Erro ao inicializar o agente:[/bold red] {exc}\n\n"
                "Verifique se o arquivo [bold].env[/bold] está configurado com sua chave de API "
                "(ex.: [bold]GEMINI_API_KEY[/bold], [bold]OPENAI_API_KEY[/bold] ou [bold]GROQ_API_KEY[/bold]).",
                border_style="red",
            )
        )
        return 1

    if args.demo:
        run_demo_scenarios(assistant, console)
        return 0

    if args.query:
        result = assistant.chat(args.query, thread_id=args.thread_id)
        _render_tool_calls(console, result.get("tool_calls", []))
        answer_text = result.get("answer") or result.get("response") or ""
        console.print(
            Panel(
                Markdown(answer_text),
                title="[bold yellow]Empório da Música[/bold yellow]",
                border_style="yellow",
            )
        )
        return 0

    thread_id = args.thread_id
    console.print(
        "[dim]Comandos rápidos: [bold]/novo[/bold] (nova conversa), "
        "[bold]/demo[/bold] (rodar cenários), [bold]/sair[/bold] (encerrar)[/dim]\n"
    )

    while True:
        try:
            user_input = console.input("[bold cyan]Você > [/bold cyan]").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[yellow]Até mais! Bons sons por aí! 🎶[/yellow]")
            break

        if not user_input:
            continue

        cmd = user_input.lower()
        if cmd in {"/sair", "sair", "exit", "quit"}:
            console.print("[yellow]Até mais! Bons sons por aí! 🎶[/yellow]")
            break
        if cmd in {"/novo", "/reset", "reset"}:
            thread_id = f"cli-{uuid.uuid4().hex[:8]}"
            console.print(
                f"[green]Nova conversa iniciada (thread_id={thread_id}).[/green]"
            )
            continue
        if cmd == "/demo":
            run_demo_scenarios(assistant, console)
            continue

        result = assistant.chat(user_input, thread_id=thread_id)
        _render_tool_calls(console, result.get("tool_calls", []))
        answer_text = result.get("answer") or result.get("response") or ""
        console.print(
            Panel(
                Markdown(answer_text),
                title="[bold yellow]Empório da Música[/bold yellow]",
                border_style="yellow",
            )
        )

    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(run_interactive_cli())
