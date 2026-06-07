from __future__ import annotations

import json
import time
from typing import Any

from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.table import Table

from jober_tui.api_client import JoberApiClient


def _format_event_line(payload: dict[str, Any]) -> str:
    ts = payload.get("ts", "")
    clock = ts[11:19] if isinstance(ts, str) and len(ts) >= 19 else "??:??:??"
    event_type = payload.get("event_type", "event")
    message = payload.get("message", "")
    if event_type == "field.filled":
        field = (payload.get("payload") or {}).get("field_key", message)
        return f"[{clock}] filled field=\"{field}\" status=ok"
    if event_type == "human.required":
        return f"[{clock}] HUMAN CHECKPOINT: {message}"
    return f"[{clock}] {event_type} {message}"


def watch_run(console: Console, client: JoberApiClient, run_id: str) -> None:
    snapshot = client.console_snapshot(run_id)
    company = snapshot.get("company", "")
    role = snapshot.get("role", "")
    console.print(f'Watching run {run_id} — job="{company} / {role}"', style="bold")
    lines: list[str] = []
    last_seq = int(snapshot.get("last_event_seq", 0))
    for event in snapshot.get("events", []):
        lines.append(_format_event_line(event))
        last_seq = max(last_seq, int(event.get("seq", 0)))

    checkpoint = snapshot.get("open_checkpoint")

    def render() -> Panel:
        table = Table.grid(padding=(0, 1))
        table.add_column(justify="left")
        for line in lines[-40:]:
            table.add_row(line)
        if checkpoint:
            table.add_row("")
            table.add_row(f"[bold yellow]CHECKPOINT[/]: {checkpoint.get('prompt')}")
        return Panel(table, title="Live run log", border_style="cyan")

    with Live(render(), console=console, refresh_per_second=4, transient=False) as live:
        while True:
            try:
                for raw in client.stream_events(run_id, after_seq=last_seq):
                    data = raw.get("data")
                    if not data:
                        continue
                    payload = json.loads(data)
                    lines.append(_format_event_line(payload))
                    last_seq = max(last_seq, int(payload.get("seq", last_seq)))
                    live.update(render())
                    if payload.get("event_type") == "human.required":
                        from jober_tui.checkpoint_prompt import prompt_checkpoint

                        snap = client.console_snapshot(run_id)
                        open_cp = snap.get("open_checkpoint")
                        if open_cp:
                            prompt_checkpoint(console, client, run_id, open_cp)
                            checkpoint = None
                            live.update(render())
                time.sleep(0.5)
            except KeyboardInterrupt:
                console.print("Stopped watching.", style="dim")
                return
