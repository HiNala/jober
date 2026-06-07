from __future__ import annotations

import json
from typing import Any

from cryptography.fernet import Fernet, InvalidToken


def _fernet(key: str) -> Fernet:
    if not key:
        msg = "VAULT_ENCRYPTION_KEY required for encrypted browser storage state"
        raise ValueError(msg)
    return Fernet(key.encode("utf-8") if isinstance(key, str) else key)


def encrypt_storage_state(state: dict[str, Any], key: str) -> bytes:
    return _fernet(key).encrypt(json.dumps(state).encode("utf-8"))


def decrypt_storage_state(blob: bytes, key: str) -> dict[str, Any]:
    try:
        raw = _fernet(key).decrypt(blob)
    except InvalidToken as exc:
        msg = "Invalid encrypted storage state"
        raise ValueError(msg) from exc
    data = json.loads(raw.decode("utf-8"))
    if not isinstance(data, dict):
        msg = "Storage state must be a JSON object"
        raise TypeError(msg)
    return data
