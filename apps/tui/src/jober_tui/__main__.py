from __future__ import annotations

from rich.console import Console

from jober_tui.app import main_menu


def main() -> None:
    console = Console(highlight=False, soft_wrap=True)
    main_menu(console)


if __name__ == "__main__":
    main()
