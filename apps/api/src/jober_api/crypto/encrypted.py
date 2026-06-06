from typing import Any

from cryptography.fernet import Fernet, InvalidToken
from sqlalchemy.types import LargeBinary, TypeDecorator


class EncryptedText(TypeDecorator[str | None]):
    """Transparent Fernet encryption at the ORM layer; ciphertext stored as bytes."""

    impl = LargeBinary
    cache_ok = True

    def __init__(self, key_provider: Any) -> None:
        super().__init__()
        self._key_provider = key_provider

    def _fernet(self) -> Fernet:
        raw_key = self._key_provider()
        if not raw_key:
            msg = "VAULT_ENCRYPTION_KEY is required for encrypted fields"
            raise ValueError(msg)
        key_bytes = raw_key.encode("utf-8") if isinstance(raw_key, str) else raw_key
        return Fernet(key_bytes)

    def process_bind_param(self, value: str | None, dialect: Any) -> bytes | None:
        if value is None:
            return None
        return self._fernet().encrypt(value.encode("utf-8"))

    def process_result_value(self, value: bytes | None, dialect: Any) -> str | None:
        if value is None:
            return None
        try:
            return self._fernet().decrypt(value).decode("utf-8")
        except InvalidToken as exc:
            msg = "Failed to decrypt vault field — check VAULT_ENCRYPTION_KEY"
            raise ValueError(msg) from exc
