"""Security primitives: password hashing (argon2) and API-token hashing.

Kept dependency-light and side-effect-free so it's trivially testable. Higher-level
auth flows (sessions, 2FA, login) build on these in T0.4's later increments.
"""
import hashlib
import secrets

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHashError

# argon2id with library defaults (sane, modern). Tunable later if needed.
_ph = PasswordHasher()

# API-token display prefix and byte strength.
TOKEN_PREFIX = "lokyy_"
_TOKEN_BYTES = 32


def hash_password(password: str) -> str:
    """Return an argon2id hash for a plaintext password."""
    if not password:
        raise ValueError("password must not be empty")
    return _ph.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    """Constant-time-ish verification. Returns False on any mismatch/format error."""
    try:
        return _ph.verify(hashed, password)
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False


def needs_rehash(hashed: str) -> bool:
    """True if the stored hash uses outdated parameters and should be upgraded."""
    try:
        return _ph.check_needs_rehash(hashed)
    except (InvalidHashError, Exception):
        return False


def generate_api_token() -> tuple[str, str, str]:
    """Create a new API token.

    Returns (raw_token, token_hash, token_prefix). Only the raw token is ever
    shown to the user (once); we persist the hash + a short display prefix.
    """
    raw = TOKEN_PREFIX + secrets.token_urlsafe(_TOKEN_BYTES)
    return raw, hash_token(raw), raw[: len(TOKEN_PREFIX) + 8]


def hash_token(raw_token: str) -> str:
    """SHA-256 of an API token. Tokens are high-entropy, so a fast hash is fine."""
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def verify_token(raw_token: str, token_hash: str) -> bool:
    return secrets.compare_digest(hash_token(raw_token), token_hash)
