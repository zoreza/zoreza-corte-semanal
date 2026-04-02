"""Auth endpoints: login, refresh, me."""

from fastapi import APIRouter, HTTPException, status

from app.core.deps import CurrentUser, DbSession
from app.schemas.auth import LoginRequest, RefreshRequest, TokenResponse, UserInfo
from app.services.auth_service import authenticate, refresh_tokens

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: DbSession):
    tokens = await authenticate(db, body.username, body.password)
    if tokens is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Credenciales inválidas")
    return tokens


@router.post("/refresh", response_model=TokenResponse)
async def refresh(body: RefreshRequest, db: DbSession):
    tokens = await refresh_tokens(db, body.refresh_token)
    if tokens is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Refresh token inválido o expirado")
    return tokens


@router.get("/me", response_model=UserInfo)
async def me(user: CurrentUser):
    return user
