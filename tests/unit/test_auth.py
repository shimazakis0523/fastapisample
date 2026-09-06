from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.core import auth as auth_module
from app.core.auth import require_permission, verify_token

AUDIENCE = "https://fastapisample-api"
ISSUER = "https://test-tenant.auth0.com/"


class _StubSigningKey:
    def __init__(self, key: Any) -> None:
        self.key = key


class _StubJWKSClient:
    def __init__(self, key: Any) -> None:
        self._key = key

    def get_signing_key_from_jwt(self, token: str) -> _StubSigningKey:
        return _StubSigningKey(self._key)


def _make_token(private_key: RSAPrivateKey, **claim_overrides: Any) -> str:
    now = datetime.now(UTC)
    claims = {
        "sub": "auth0|test-user",
        "aud": AUDIENCE,
        "iss": ISSUER,
        "iat": now,
        "exp": now + timedelta(minutes=5),
        **claim_overrides,
    }
    return jwt.encode(claims, private_key, algorithm="RS256")


def _credentials(token: str) -> HTTPAuthorizationCredentials:
    return HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)


@pytest.fixture
def rsa_keypair() -> tuple[RSAPrivateKey, Any]:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    return private_key, private_key.public_key()


@pytest.fixture(autouse=True)
def _configure_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(auth_module._settings, "auth0_audience", AUDIENCE)
    monkeypatch.setattr(auth_module._settings, "auth0_domain", "test-tenant.auth0.com")


async def test_valid_token_is_accepted(
    monkeypatch: pytest.MonkeyPatch, rsa_keypair: tuple[RSAPrivateKey, Any]
) -> None:
    private_key, public_key = rsa_keypair
    monkeypatch.setattr(auth_module, "_jwks_client", _StubJWKSClient(public_key))

    payload = await verify_token(_credentials(_make_token(private_key)))

    assert payload["sub"] == "auth0|test-user"


async def test_wrong_audience_is_rejected(
    monkeypatch: pytest.MonkeyPatch, rsa_keypair: tuple[RSAPrivateKey, Any]
) -> None:
    private_key, public_key = rsa_keypair
    monkeypatch.setattr(auth_module, "_jwks_client", _StubJWKSClient(public_key))
    token = _make_token(private_key, aud="https://someone-elses-api")

    with pytest.raises(HTTPException) as exc_info:
        await verify_token(_credentials(token))
    assert exc_info.value.status_code == 401


async def test_wrong_issuer_is_rejected(
    monkeypatch: pytest.MonkeyPatch, rsa_keypair: tuple[RSAPrivateKey, Any]
) -> None:
    private_key, public_key = rsa_keypair
    monkeypatch.setattr(auth_module, "_jwks_client", _StubJWKSClient(public_key))
    token = _make_token(private_key, iss="https://not-my-tenant.auth0.com/")

    with pytest.raises(HTTPException) as exc_info:
        await verify_token(_credentials(token))
    assert exc_info.value.status_code == 401


async def test_expired_token_is_rejected(
    monkeypatch: pytest.MonkeyPatch, rsa_keypair: tuple[RSAPrivateKey, Any]
) -> None:
    private_key, public_key = rsa_keypair
    monkeypatch.setattr(auth_module, "_jwks_client", _StubJWKSClient(public_key))
    expired = datetime.now(UTC) - timedelta(minutes=5)
    token = _make_token(private_key, iat=expired - timedelta(minutes=5), exp=expired)

    with pytest.raises(HTTPException) as exc_info:
        await verify_token(_credentials(token))
    assert exc_info.value.status_code == 401


async def test_signature_from_wrong_key_is_rejected(
    monkeypatch: pytest.MonkeyPatch, rsa_keypair: tuple[RSAPrivateKey, Any]
) -> None:
    private_key, _ = rsa_keypair
    other_public_key = rsa.generate_private_key(public_exponent=65537, key_size=2048).public_key()
    monkeypatch.setattr(auth_module, "_jwks_client", _StubJWKSClient(other_public_key))

    with pytest.raises(HTTPException) as exc_info:
        await verify_token(_credentials(_make_token(private_key)))
    assert exc_info.value.status_code == 401


async def test_malformed_token_is_rejected() -> None:
    with pytest.raises(HTTPException) as exc_info:
        await verify_token(_credentials("not-a-real-token"))
    assert exc_info.value.status_code == 401


async def test_require_permission_accepts_user_with_permission() -> None:
    check = require_permission("delete:items")

    await check({"sub": "test-user", "permissions": ["delete:items", "other:scope"]})


async def test_require_permission_rejects_user_without_permission() -> None:
    check = require_permission("delete:items")

    with pytest.raises(HTTPException) as exc_info:
        await check({"sub": "test-user", "permissions": ["other:scope"]})
    assert exc_info.value.status_code == 403


async def test_require_permission_rejects_token_without_permissions_claim() -> None:
    check = require_permission("delete:items")

    with pytest.raises(HTTPException) as exc_info:
        await check({"sub": "test-user"})
    assert exc_info.value.status_code == 403
