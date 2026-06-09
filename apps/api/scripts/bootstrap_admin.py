#!/usr/bin/env python3
"""One-time first-admin bootstrap. Requires ADMIN_BOOTSTRAP_SECRET — not a public API."""

from __future__ import annotations

import argparse
import asyncio
import getpass
import sys

from jober_api.db.session import async_session_factory
from jober_api.services.admin.bootstrap import BootstrapError, bootstrap_first_admin


async def _run(email: str, secret: str) -> None:
    async with async_session_factory() as session:
        try:
            user = await bootstrap_first_admin(session, email=email, secret=secret)
        except BootstrapError as exc:
            print(f"Bootstrap failed: {exc}", file=sys.stderr)
            raise SystemExit(1) from exc
    print(f"Admin bootstrap complete for {user.email} ({user.id})")


def main() -> None:
    parser = argparse.ArgumentParser(description="Bootstrap the first Jober admin user")
    parser.add_argument("--email", required=True, help="Email of the user to promote")
    parser.add_argument(
        "--secret",
        help="ADMIN_BOOTSTRAP_SECRET value (prompted if omitted)",
    )
    args = parser.parse_args()
    secret = args.secret or getpass.getpass("ADMIN_BOOTSTRAP_SECRET: ")
    asyncio.run(_run(args.email, secret))


if __name__ == "__main__":
    main()
