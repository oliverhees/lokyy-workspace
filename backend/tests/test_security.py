"""T0.4 increment 1: password & token primitives."""
import pytest

from app.core.security import (
    generate_api_token,
    hash_password,
    hash_token,
    verify_password,
    verify_token,
)


def test_password_hash_roundtrip():
    h = hash_password("correct horse battery staple")
    assert h != "correct horse battery staple"  # never store plaintext
    assert verify_password("correct horse battery staple", h) is True
    assert verify_password("wrong", h) is False


def test_password_hash_is_salted():
    assert hash_password("same") != hash_password("same")  # random salt


def test_empty_password_rejected():
    with pytest.raises(ValueError):
        hash_password("")


def test_api_token_generation_and_verify():
    raw, token_hash, prefix = generate_api_token()
    assert raw.startswith("lokyy_")
    assert prefix.startswith("lokyy_") and len(prefix) == len("lokyy_") + 8
    assert raw != token_hash  # store only the hash
    assert token_hash == hash_token(raw)
    assert verify_token(raw, token_hash) is True
    assert verify_token("lokyy_tampered", token_hash) is False


def test_tokens_are_unique():
    assert generate_api_token()[0] != generate_api_token()[0]
