"""Passkey / WebAuthn endpoints — registration & authentication."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel, Field

from app.core.deps import CurrentUser, DbSession
from app.core.security import create_access_token, create_refresh_token
from app.schemas.auth import TokenResponse
from app.services.passkey_service import (
    delete_credential,
    generate_authentication_options,
    generate_registration_options,
    list_user_credentials,
    verify_authentication,
    verify_registration,
)

router = APIRouter()


# ── Schemas ──────────────────────────────────────────────────────────

class RegisterStartRequest(BaseModel):
    """No body needed — uses current authenticated user."""
    pass


class RegisterFinishRequest(BaseModel):
    credential: str = Field(..., description="JSON-stringified navigator.credentials.create() response")
    device_name: str = Field("", max_length=200)


class AuthStartRequest(BaseModel):
    username: str | None = Field(None, max_length=50, description="Leave empty for discoverable credentials")


class AuthFinishRequest(BaseModel):
    credential: str = Field(..., description="JSON-stringified navigator.credentials.get() response")
    username: str | None = Field(None, max_length=50)


class CredentialOut(BaseModel):
    uuid: str
    device_name: str
    backed_up: bool
    created_at: str
    sign_count: int


# ── Registration (requires auth) ────────────────────────────────────

@router.post("/register/start")
async def passkey_register_start(
    request: Request,
    user: CurrentUser,
    db: DbSession,
):
    """Generate registration options for the authenticated user."""
    origin = _get_origin(request)
    options_json = await generate_registration_options(db, user, origin)
    return {"options": options_json}


@router.post("/register/finish")
async def passkey_register_finish(
    body: RegisterFinishRequest,
    request: Request,
    user: CurrentUser,
    db: DbSession,
):
    """Verify registration and store the new passkey."""
    origin = _get_origin(request)
    try:
        cred = await verify_registration(
            db, user, body.credential, origin, body.device_name
        )
    except Exception as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))
    return {"ok": True, "credential_uuid": str(cred.uuid), "device_name": cred.device_name}


# ── Authentication (public) ──────────────────────────────────────────

@router.post("/authenticate/start")
async def passkey_auth_start(
    body: AuthStartRequest,
    request: Request,
    db: DbSession,
):
    """Generate authentication options for passkey login."""
    origin = _get_origin(request)
    options_json = await generate_authentication_options(db, body.username, origin)
    return {"options": options_json}


@router.post("/authenticate/finish", response_model=TokenResponse)
async def passkey_auth_finish(
    body: AuthFinishRequest,
    request: Request,
    db: DbSession,
):
    """Verify passkey authentication and return JWT tokens."""
    origin = _get_origin(request)
    try:
        user = await verify_authentication(
            db, body.credential, body.username, origin
        )
    except Exception as e:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, str(e))

    return TokenResponse(
        access_token=create_access_token({"sub": str(user.uuid)}),
        refresh_token=create_refresh_token({"sub": str(user.uuid)}),
    )


# ── Credential management (requires auth) ───────────────────────────

@router.get("/credentials")
async def passkey_list(user: CurrentUser, db: DbSession):
    """List all passkeys for the authenticated user."""
    creds = await list_user_credentials(db, str(user.uuid))
    return [
        CredentialOut(
            uuid=str(c.uuid),
            device_name=c.device_name,
            backed_up=c.backed_up,
            created_at=c.created_at.isoformat(),
            sign_count=c.sign_count,
        )
        for c in creds
    ]


@router.delete("/credentials/{credential_uuid}")
async def passkey_delete(
    credential_uuid: str,
    user: CurrentUser,
    db: DbSession,
):
    """Delete a specific passkey."""
    from uuid import UUID
    try:
        cred_uuid = UUID(credential_uuid)
    except ValueError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "UUID inválido")
    deleted = await delete_credential(db, str(user.uuid), cred_uuid)
    if not deleted:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Passkey no encontrada")
    return {"ok": True}


# ── Helpers ──────────────────────────────────────────────────────────

def _get_origin(request: Request) -> str:
    """Reconstruct origin from request headers."""
    origin = request.headers.get("origin")
    if origin:
        return origin
    # Fallback: reconstruct from Host header
    scheme = request.headers.get("x-forwarded-proto", request.url.scheme)
    host = request.headers.get("host", request.url.hostname or "localhost")
    return f"{scheme}://{host}"
