from __future__ import annotations

import pytest
from cryptography.fernet import Fernet

from jober_worker.browser.storage_state import decrypt_storage_state, encrypt_storage_state


def test_storage_state_round_trip() -> None:
    key = Fernet.generate_key().decode()
    state = {"cookies": [{"name": "session", "value": "abc", "domain": "example.com"}]}
    blob = encrypt_storage_state(state, key)
    restored = decrypt_storage_state(blob, key)
    assert restored == state


def test_storage_state_rejects_invalid_key() -> None:
    key = Fernet.generate_key().decode()
    blob = encrypt_storage_state({"cookies": []}, key)
    with pytest.raises(ValueError, match="Invalid encrypted"):
        decrypt_storage_state(blob, Fernet.generate_key().decode())
