from __future__ import annotations
import json
from typing import Any
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import print as rprint

console = Console()


def print_banner(title: str) -> None:
    console.print(Panel(f"[bold cyan]{title}[/]", style="cyan"))


def print_step(agent: str, message: str) -> None:
    console.print(f"[bold cyan]\\[{agent}][/] [yellow]⟳[/] {message}")


def print_done(agent: str, summary: str) -> None:
    console.print(f"[bold cyan]\\[{agent}][/] [green]✓[/] {summary}")


def print_json_block(title: str, payload: Any) -> None:
    console.print(f"\n[bold]{title}[/]")
    console.print_json(json.dumps(payload, ensure_ascii=False))


def print_hypothesis_card(persona: str, data: dict) -> None:
    conf = data.get('confidence', 0)
    bar_len = 10
    filled = round(conf * bar_len)
    bar = "█" * filled + "░" * (bar_len - filled)
    color = "green" if conf >= 0.7 else "yellow" if conf >= 0.4 else "red"
    console.print(Panel(
        f"[bold]{data.get('root_cause', '')}[/]\n"
        f"Confidence: [{color}][{bar}] {conf:.0%}[/]\n"
        f"Fix: {data.get('likely_fix', '')}",
        title=f"[bold magenta]{persona}[/]",
        border_style="magenta"
    ))


def print_final_diagnosis(judge: dict) -> None:
    console.print(Panel(
        f"[bold yellow]Root Cause:[/] {judge.get('final_diagnosis', '')}\n\n"
        f"[bold green]Fix:[/] {judge.get('fix_suggestion', '')}\n\n"
        f"[bold cyan]Validation:[/]\n" + "\n".join(f"  • {v}" for v in judge.get('validation_strategy', [])),
        title="[bold green]🎯 Final Diagnosis[/]",
        border_style="green"
    ))
