"""Symmetric encryption for secrets at rest (F4).

Provider API keys must never be stored in plaintext. We derive a Fernet key from
the app SECRET_KEY (SHA-256 → 32 bytes → urlsafe-b64) and encrypt/decrypt with it.
Rotating SECRET_KEY invalidates stored ciphertexts by design — re-enter keys after
a rotation. (A dedicated key-management story can replace this later.)
"""
import base64
import hashlib

from cryptography.fernet import Fernet, InvalidToken

from app.core.config import get_settings


def _fernet() -> Fernet:
    secret = get_settings().secret_key.encode("utf-8")
    key = base64.urlsafe_b64encode(hashlib.sha256(secret).digest())
    return Fernet(key)


def encrypt(plaintext: str) -> str:
    """Encrypt a secret. Empty input stays empty (no key configured)."""
    if not plaintext:
        return ""
    return _fernet().encrypt(plaintext.encode("utf-8")).decode("utf-8")


def decrypt(token: str) -> str:
    """Decrypt a secret. Returns "" for empty input; raises on tampering/rotation."""
    if not token:
        return ""
    return _fernet().decrypt(token.encode("utf-8")).decode("utf-8")


def try_decrypt(token: str) -> str | None:
    """Best-effort decrypt: returns None instead of raising (e.g. after key rotation)."""
    try:
        return decrypt(token)
    except (InvalidToken, ValueError):
        return None
