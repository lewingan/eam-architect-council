"""CLI interface for the EAM Architecture Council."""

from __future__ import annotations

import argparse
import asyncio
import io
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel

from eam_council.council.lead_agent import run_council

# Force UTF-8 stdout to avoid Windows cp1252 encoding errors
if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

console = Console(force_terminal=False)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="eam_council",
        description="EAM Architecture Council - multi-agent EAM advisor",
    )
    parser.add_argument("question", help="The EAM architecture question to answer")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Return deterministic stub output without calling the API",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Override the Claude model to use",
    )
    parser.add_argument(
        "--no-search",
        action="store_true",
        help="Disable web search for subagents (offline/cost-sensitive mode)",
    )
    parser.add_argument(
        "--minimal-context",
        action="store_true",
        help="Enable minimal context mode to reduce token usage",
    )
    parser.add_argument(
        "--search-budget",
        type=int,
        default=None,
        help="Override search tool budget for this run",
    )
    parser.add_argument(
        "--tokens-per-minute",
        type=int,
        default=None,
        help="Override EAM_TOKENS_PER_MINUTE throttling budget",
    )
    parser.add_argument(
        "--disable-tpm-throttle",
        action="store_true",
        help="Disable tokens-per-minute throttling for this run",
    )
    return parser.parse_args()


def main() -> None:
    load_dotenv()
    args = parse_args()

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    dry_run = args.dry_run or not api_key

    if not api_key and not args.dry_run:
        console.print(
            "[yellow]No ANTHROPIC_API_KEY found. Running in dry-run mode.[/yellow]"
        )

    model = args.model or os.environ.get("EAM_MODEL", "claude-sonnet-4-20250514")
    search_enabled = not args.no_search
    if args.minimal_context:
        os.environ["EAM_MINIMAL_MODE"] = "1"
    if args.search_budget is not None:
        os.environ["EAM_SEARCH_BUDGET"] = str(args.search_budget)
    if args.tokens_per_minute is not None:
        os.environ["EAM_TOKENS_PER_MINUTE"] = str(args.tokens_per_minute)
    if args.disable_tpm_throttle:
        os.environ["EAM_ENABLE_TPM_THROTTLE"] = "0"

    console.print(
        Panel(
            f"[bold]EAM Architecture Council[/bold]\n"
            f"Mode: {'DRY-RUN' if dry_run else 'LIVE'}\n"
            f"Model: {model}\n"
            f"Web Search: {'ON' if search_enabled else 'OFF'}",
            title="Council Session",
        )
    )
    console.print(f"\n[bold]Question:[/bold] {args.question}\n")

    result = asyncio.run(
        run_council(
            question=args.question,
            model=model,
            dry_run=dry_run,
            search_enabled=search_enabled,
        )
    )

    # Print to stdout
    console.print(Panel(result, title="Council Response", border_style="green"))

    # Write to file
    out_dir = Path("out")
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "latest.md"
    out_path.write_text(result, encoding="utf-8")
    console.print(f"\n[dim]Output written to {out_path}[/dim]")
