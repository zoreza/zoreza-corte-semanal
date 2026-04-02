"""Auth service — login / token refresh."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, create_refresh_token, decode_token, verify_password
from app.schemas.auth import TokenResponse
from app.services.usuario_service import get_usuario_by_username, get_usuario_by_uuid


async def authenticate(db: AsyncSession, username: str, password: str) -> TokenResponse | None:
    user = await get_usuario_by_username(db, username)
    if user is None or not user.activo:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return _create_tokens(str(user.uuid))


async def refresh_tokens(db: AsyncSession, refresh_token: str) -> TokenResponse | None:
    try:
        payload = decode_token(refresh_token)
    except Exception:
        return None
    if payload.get("type") != "refresh":
        return None
    user_uuid = payload.get("sub")
    if user_uuid is None:
        return None
    user = await get_usuario_by_uuid(db, user_uuid)
    if user is None or not user.activo:
        return None
    return _create_tokens(str(user.uuid))


def _create_tokens(user_uuid: str) -> TokenResponse:
    return TokenResponse(
        access_token=create_access_token({"sub": user_uuid}),
        refresh_token=create_refresh_token({"sub": user_uuid}),
    )
