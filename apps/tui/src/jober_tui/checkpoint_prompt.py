from __future__ import annotations

from typing import Any

from rich.console import Console
from rich.prompt import Prompt

from jober_tui.api_client import JoberApiClient


def prompt_checkpoint(
    console: Console,
    client: JoberApiClient,
    run_id: str,
    checkpoint: dict[str, Any],
) -> None:
    cp_type = str(checkpoint.get("checkpoint_type", "checkpoint"))
    console.print(f"\n[bold yellow]{cp_type}[/]: {checkpoint.get('prompt')}")
    if cp_type == "review_submit":
        choice = Prompt.ask(
            "Resolve checkpoint",
            choices=["a", "e", "s", "d"],
            default="a",
            show_choices=True,
        )
        action = {"a": "approve", "e": "edit", "s": "skip", "d": "deny"}[choice]
    else:
        choice = Prompt.ask("Continue?", choices=["y", "n"], default="y")
        action = "approve" if choice == "y" else "skip"
    result = client.resolve_checkpoint(run_id, str(checkpoint["id"]), action)
    console.print(f"Checkpoint {result.get('action')} → run {result.get('run_status')}", style="green")
