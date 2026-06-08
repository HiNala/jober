from __future__ import annotations

import hashlib
import secrets


def generate_opaque_token() -> str:
    return secrets.token_urlsafe(32)


def hash_opaque_token(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()
