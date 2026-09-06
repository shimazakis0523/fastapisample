from collections.abc import Awaitable, Callable
from typing import Annotated, Any

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import get_settings

_settings = get_settings()
_bearer_scheme = HTTPBearer()
_jwks_client = jwt.PyJWKClient(f"https://{_settings.auth0_domain}/.well-known/jwks.json")


async def verify_token(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(_bearer_scheme)],
) -> dict[str, Any]:
    try:
        signing_key = _jwks_client.get_signing_key_from_jwt(credentials.credentials)
        return jwt.decode(
            credentials.credentials,
            signing_key.key,
            algorithms=["RS256"],
            audience=_settings.auth0_audience,
            issuer=f"https://{_settings.auth0_domain}/",
        )
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


CurrentUser = Annotated[dict[str, Any], Depends(verify_token)]


def require_permission(permission: str) -> Callable[[CurrentUser], Awaitable[None]]:
    """Auth0 RBAC: the access token's `permissions` claim must include `permission`."""

    async def _check(user: CurrentUser) -> None:
        if permission not in user.get("permissions", []):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required permission: {permission}",
            )

    return _check
