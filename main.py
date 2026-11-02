"""CLI Entrypoint for the Empório da Música Conversational AI Agent."""

from __future__ import annotations

import sys

from src.ui.cli import run_interactive_cli

if __name__ == "__main__":
    sys.exit(run_interactive_cli())
