from __future__ import annotations

import json
import uuid
from typing import Any

from cryptography.fernet import Fernet, InvalidToken

from jober_api.config import settings
from jober_api.storage.keys import run_storage_state_key
from jober_api.storage.minio_client import ObjectStorage


def _fernet() -> Fernet:
    key = settings.vault_encryption_key.strip()
    if not key:
        msg = "VAULT_ENCRYPTION_KEY required for encrypted browser storage state"
        raise ValueError(msg)
    return Fernet(key.encode() if isinstance(key, str) else key)


def encrypt_storage_state(state: dict[str, Any]) -> bytes:
    return _fernet().encrypt(json.dumps(state).encode())


def decrypt_storage_state(blob: bytes) -> dict[str, Any]:
    try:
        payload = _fernet().decrypt(blob)
    except InvalidToken as exc:
        msg = "Invalid encrypted storage state"
        raise ValueError(msg) from exc
    data: dict[str, Any] = json.loads(payload.decode())
    return data


async def save_run_storage_state(run_id: uuid.UUID, state: dict[str, Any]) -> str:
    """Persist Playwright storage state encrypted at rest (MinIO). Never commit to git."""
    storage = ObjectStorage()
    key = run_storage_state_key(run_id)
    await storage.put_object(
        key,
        encrypt_storage_state(state),
        content_type="application/octet-stream",
    )
    return key


async def load_run_storage_state(run_id: uuid.UUID) -> dict[str, Any] | None:
    storage = ObjectStorage()
    key = run_storage_state_key(run_id)
    try:
        blob = await storage.get_bytes(key)
    except Exception:  # noqa: BLE001
        return None
    return decrypt_storage_state(blob)


async def delete_run_storage_state(run_id: uuid.UUID) -> None:
    storage = ObjectStorage()
    key = run_storage_state_key(run_id)
    try:
        await storage.remove_object(key)
    except Exception:  # noqa: BLE001
        return
