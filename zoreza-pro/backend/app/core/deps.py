"""FastAPI dependencies: DB session, current user, role checks."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_token
from app.db.tenant_session import get_tenant_session_factory
from app.db.master_session import master_session_factory
from app.models.usuario import Usuario
from app.models.tenant import SuperAdmin

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/{tenant}/api/v1/auth/login", auto_error=False)


async def get_db(request: Request) -> AsyncSession:  # type: ignore[misc]
    """Yield a DB session for the current tenant."""
    slug = getattr(request.state, "tenant_slug", None)
    if not slug:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Tenant no especificado")
    factory = await get_tenant_session_factory(slug)
    async with factory() as session:
        yield session


async def get_master_db() -> AsyncSession:  # type: ignore[misc]
    """Yield a session on the master (platform) database."""
    async with master_session_factory() as session:
        yield session


async def get_current_user(
    request: Request,
    token: Annotated[str | None, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Usuario:
    if not token:
        # Try extracting token manually (since tokenUrl is a template)
        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            token = auth[7:]
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido o expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_exc
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            raise credentials_exc
        user_uuid: str | None = payload.get("sub")
        if user_uuid is None:
            raise credentials_exc
    except JWTError:
        raise credentials_exc

    from app.services.usuario_service import get_usuario_by_uuid

    user = await get_usuario_by_uuid(db, user_uuid)
    if user is None or not user.activo:
        raise credentials_exc
    return user


async def get_current_superadmin(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_master_db)],
) -> SuperAdmin:
    """Authenticate super-admin via Bearer token on the master DB."""
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token requerido")
    token = auth[7:]
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido o expirado",
    )
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            raise credentials_exc
        user_uuid: str | None = payload.get("sub")
        if user_uuid is None:
            raise credentials_exc
    except JWTError:
        raise credentials_exc

    admin = await db.get(SuperAdmin, user_uuid)
    if admin is None or not admin.activo:
        raise credentials_exc
    return admin


def require_roles(*roles: str):
    """Dependency factory: require the current user to have one of the given roles."""

    async def _check(user: Annotated[Usuario, Depends(get_current_user)]) -> Usuario:
        if user.rol not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Rol requerido: {', '.join(roles)}",
            )
        return user

    return _check


# Handy aliases
CurrentUser = Annotated[Usuario, Depends(get_current_user)]
AdminUser = Annotated[Usuario, Depends(require_roles("ADMIN"))]
SupervisorUser = Annotated[Usuario, Depends(require_roles("ADMIN", "SUPERVISOR"))]
DbSession = Annotated[AsyncSession, Depends(get_db)]
MasterDbSession = Annotated[AsyncSession, Depends(get_master_db)]
SuperAdminUser = Annotated[SuperAdmin, Depends(get_current_superadmin)]
