"""F4: model endpoint service — CRUD, encryption at rest, defaults, owner isolation."""
import pytest
from sqlmodel import Session, SQLModel, create_engine

import app.models  # noqa: F401  (register all tables)
from app.core import auth, crypto, model_service


def _db():
    eng = create_engine("sqlite://", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(eng)
    return Session(eng)


def _user(db, email="a@x.de"):
    return auth.signup(db, organization_name="Acme", email=email,
                       password="pw123456", display_name="A")


def test_crypto_roundtrip_and_empty():
    assert crypto.encrypt("") == ""
    assert crypto.decrypt("") == ""
    token = crypto.encrypt("sk-secret-123")
    assert token != "sk-secret-123"  # not plaintext
    assert crypto.decrypt(token) == "sk-secret-123"


def test_create_encrypts_key_at_rest():
    db = _db()
    u = _user(db)
    ep = model_service.create_endpoint(
        db, user_id=u.id, name="Cloud", provider="openai",
        base_url="https://api.openai.com/v1", model="gpt-5", api_key="sk-topsecret",
    )
    # stored ciphertext is not the plaintext, but decrypts back
    assert ep.api_key_encrypted and "sk-topsecret" not in ep.api_key_encrypted
    assert model_service.decrypt_key(ep) == "sk-topsecret"


def test_first_endpoint_becomes_default():
    db = _db()
    u = _user(db)
    a = model_service.create_endpoint(db, user_id=u.id, name="A", provider="openai",
                                      base_url="u", model="m")
    assert a.is_default is True
    b = model_service.create_endpoint(db, user_id=u.id, name="B", provider="openai",
                                      base_url="u", model="m")
    assert b.is_default is False


def test_set_default_clears_others():
    db = _db()
    u = _user(db)
    a = model_service.create_endpoint(db, user_id=u.id, name="A", provider="openai", base_url="u", model="m")
    b = model_service.create_endpoint(db, user_id=u.id, name="B", provider="openai", base_url="u", model="m")
    model_service.set_default(db, user_id=u.id, endpoint_id=b.id)
    eps = {e.id: e.is_default for e in model_service.list_endpoints(db, user_id=u.id)}
    assert eps[b.id] is True and eps[a.id] is False


def test_update_key_and_clear():
    db = _db()
    u = _user(db)
    ep = model_service.create_endpoint(db, user_id=u.id, name="A", provider="openai",
                                       base_url="u", model="m", api_key="sk-1")
    ep = model_service.update_endpoint(db, user_id=u.id, endpoint_id=ep.id, api_key="sk-2")
    assert model_service.decrypt_key(ep) == "sk-2"
    # None leaves it unchanged
    ep = model_service.update_endpoint(db, user_id=u.id, endpoint_id=ep.id, name="A2")
    assert model_service.decrypt_key(ep) == "sk-2" and ep.name == "A2"
    # "" clears it
    ep = model_service.update_endpoint(db, user_id=u.id, endpoint_id=ep.id, api_key="")
    assert ep.api_key_encrypted == ""


def test_delete_default_promotes_next():
    db = _db()
    u = _user(db)
    a = model_service.create_endpoint(db, user_id=u.id, name="A", provider="openai", base_url="u", model="m")
    b = model_service.create_endpoint(db, user_id=u.id, name="B", provider="openai", base_url="u", model="m")
    model_service.delete_endpoint(db, user_id=u.id, endpoint_id=a.id)  # a was default
    remaining = model_service.list_endpoints(db, user_id=u.id)
    assert len(remaining) == 1 and remaining[0].id == b.id and remaining[0].is_default is True


def test_invalid_provider_rejected():
    db = _db()
    u = _user(db)
    with pytest.raises(model_service.ModelError):
        model_service.create_endpoint(db, user_id=u.id, name="X", provider="gemini",
                                      base_url="u", model="m")


def test_endpoints_are_owner_isolated():
    db = _db()
    u1 = _user(db, email="one@x.de")
    u2 = _user(db, email="two@x.de")
    ep = model_service.create_endpoint(db, user_id=u1.id, name="A", provider="openai", base_url="u", model="m")
    # u2 cannot see or mutate u1's endpoint
    assert model_service.list_endpoints(db, user_id=u2.id) == []
    with pytest.raises(model_service.ModelError):
        model_service.update_endpoint(db, user_id=u2.id, endpoint_id=ep.id, name="hack")
    with pytest.raises(model_service.ModelError):
        model_service.delete_endpoint(db, user_id=u2.id, endpoint_id=ep.id)
