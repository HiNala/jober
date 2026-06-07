from __future__ import annotations

from rich.console import Console
from rich.prompt import IntPrompt, Prompt

from jober_tui.api_client import JoberApiClient
from jober_tui.live_watch import watch_run

FIXTURE = """<!DOCTYPE html><html><body>
<label for="email">Email address</label><input id="email" name="email" type="email" />
<label for="name">Full name</label><input id="name" name="name" type="text" />
</body></html>"""


def main_menu(console: Console) -> None:
    client = JoberApiClient()
    while True:
        console.print("\n[bold]Jober[/] — interactive console", justify="center")
        console.print(
            "1 Import workbook\n"
            "2 Set up profile\n"
            "3 Pick a batch\n"
            "4 Start run\n"
            "5 Watch live\n"
            "6 Review pending checkpoints\n"
            "7 Reports\n"
            "8 Settings\n"
            "0 Exit",
            justify="left",
        )
        choice = Prompt.ask("Choose", choices=[str(i) for i in range(9)], default="5")
        if choice == "0":
            return
        if choice == "4":
            _start_fixture_run(console, client)
        elif choice == "5":
            run_id = Prompt.ask("Run id to watch")
            watch_run(console, client, run_id.strip())
        elif choice == "6":
            _review_checkpoints(console, client)
        else:
            console.print("Coming soon in a future mission.", style="dim")


def _start_fixture_run(console: Console, client: JoberApiClient) -> None:
    jobs = client.list_jobs()
    if not jobs:
        console.print("No jobs in queue — import a workbook first.", style="yellow")
        return
    table = "\n".join(
        f"{idx + 1}. {job.get('company')} / {job.get('role')} ({job.get('id')})"
        for idx, job in enumerate(jobs[:20])
    )
    console.print(table)
    pick = IntPrompt.ask("Job number", default=1)
    job = jobs[pick - 1]
    console.print(f"Starting fixture fill for {job.get('company')}…")
    result = client.fill_fixture(str(job["id"]), FIXTURE)
    run_id = str(result.get("run_id"))
    console.print(f"Run started: {run_id}", style="green")
    if Prompt.ask("Watch live now?", choices=["y", "n"], default="y") == "y":
        watch_run(console, client, run_id)


def _review_checkpoints(console: Console, client: JoberApiClient) -> None:
    run_id = Prompt.ask("Run id with open checkpoint")
    snap = client.console_snapshot(run_id.strip())
    checkpoint = snap.get("open_checkpoint")
    if not checkpoint:
        console.print("No open checkpoint on that run.", style="yellow")
        return
    from jober_tui.checkpoint_prompt import prompt_checkpoint

    prompt_checkpoint(console, client, run_id.strip(), checkpoint)
