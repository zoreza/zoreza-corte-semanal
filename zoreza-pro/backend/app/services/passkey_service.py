"""Passkey / WebAuthn service — registration & authentication ceremonies."""

from __future__ import annotations

import json
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import webauthn
from webauthn.helpers.structs import (
    AuthenticatorSelectionCriteria,
    PublicKeyCredentialDescriptor,
    ResidentKeyRequirement,
    UserVerificationRequirement,
)

from app.models.webauthn_credential import WebAuthnCredential
from app.models.usuario import Usuario

# ── In-memory challenge store (swap for Redis in production) ─────────
_challenges: dict[str, bytes] = {}


def _rp_id(origin: str) -> str:
    """Extract RP ID from origin (e.g., 'zoreza.com' from 'https://zoreza.com')."""
    from urllib.parse import urlparse
    parsed = urlparse(origin)
    return parsed.hostname or "localhost"


# ── Registration ─────────────────────────────────────────────────────

async def generate_registration_options(
    db: AsyncSession,
    user: Usuario,
    origin: str,
) -> dict:
    """Create WebAuthn registration options for a user."""
    rp_id = _rp_id(origin)

    # Existing credentials (to exclude re-registration)
    existing = await _get_user_credentials(db, str(user.uuid))
    exclude_credentials = [
        PublicKeyCredentialDescriptor(
            id=c.credential_id,
            transports=json.loads(c.transports) if c.transports else [],
        )
        for c in existing
    ]

    options = webauthn.generate_registration_options(
        rp_id=rp_id,
        rp_name="Zoreza Pro",
        user_id=str(user.uuid).encode(),
        user_name=user.username,
        user_display_name=user.nombre,
        authenticator_selection=AuthenticatorSelectionCriteria(
            resident_key=ResidentKeyRequirement.PREFERRED,
            user_verification=UserVerificationRequirement.PREFERRED,
        ),
        exclude_credentials=exclude_credentials,
    )

    # Store challenge
    _challenges[str(user.uuid)] = options.challenge

    return webauthn.options_to_json(options)


async def verify_registration(
    db: AsyncSession,
    user: Usuario,
    credential_json: str,
    origin: str,
    device_name: str = "",
) -> WebAuthnCredential:
    """Verify registration response and store the new credential."""
    rp_id = _rp_id(origin)
    expected_challenge = _challenges.pop(str(user.uuid), None)
    if expected_challenge is None:
        raise ValueError("No hay challenge pendiente. Inicia el registro nuevamente.")

    verification = webauthn.verify_registration_response(
        credential=credential_json,
        expected_challenge=expected_challenge,
        expected_rp_id=rp_id,
        expected_origin=origin,
    )

    # Store credential
    cred = WebAuthnCredential(
        user_id=user.uuid,
        credential_id=verification.credential_id,
        public_key=verification.credential_public_key,
        sign_count=verification.sign_count,
        device_name=device_name,
        transports=json.dumps(
            [t.value for t in verification.credential_device_type.transports]
            if hasattr(verification, "credential_device_type")
            and hasattr(verification.credential_device_type, "transports")
            else []
        ),
        backed_up=verification.credential_backed_up,
    )
    db.add(cred)
    await db.commit()
    await db.refresh(cred)
    return cred


# ── Authentication ───────────────────────────────────────────────────

async def generate_authentication_options(
    db: AsyncSession,
    username: str | None,
    origin: str,
) -> dict:
    """Create WebAuthn authentication options.

    If username is provided, only that user's credentials are allowed.
    If None, it's a discoverable (usernameless) flow.
    """
    rp_id = _rp_id(origin)
    allow_credentials = []

    if username:
        user = await _get_user_by_username(db, username)
        if user:
            creds = await _get_user_credentials(db, str(user.uuid))
            allow_credentials = [
                PublicKeyCredentialDescriptor(
                    id=c.credential_id,
                    transports=json.loads(c.transports) if c.transports else [],
                )
                for c in creds
            ]

    options = webauthn.generate_authentication_options(
        rp_id=rp_id,
        allow_credentials=allow_credentials or None,
        user_verification=UserVerificationRequirement.PREFERRED,
    )

    # Store challenge keyed by a stable identifier
    challenge_key = username or "__discoverable__"
    _challenges[challenge_key] = options.challenge

    return webauthn.options_to_json(options)


async def verify_authentication(
    db: AsyncSession,
    credential_json: str,
    username: str | None,
    origin: str,
) -> Usuario:
    """Verify authentication response and return the authenticated user."""
    rp_id = _rp_id(origin)
    challenge_key = username or "__discoverable__"
    expected_challenge = _challenges.pop(challenge_key, None)
    if expected_challenge is None:
        raise ValueError("No hay challenge pendiente. Inicia el login nuevamente.")

    # Parse credential to get credential_id for lookup
    import json as _json
    cred_data = _json.loads(credential_json) if isinstance(credential_json, str) else credential_json
    raw_id_b64 = cred_data.get("rawId") or cred_data.get("id", "")
    import base64
    try:
        credential_id_bytes = base64.urlsafe_b64decode(raw_id_b64 + "==")
    except Exception:
        raise ValueError("Credential ID inválido")

    # Lookup stored credential
    stored = await _get_credential_by_id(db, credential_id_bytes)
    if stored is None or not stored.activo:
        raise ValueError("Passkey no reconocida o desactivada")

    verification = webauthn.verify_authentication_response(
        credential=credential_json,
        expected_challenge=expected_challenge,
        expected_rp_id=rp_id,
        expected_origin=origin,
        credential_public_key=stored.public_key,
        credential_current_sign_count=stored.sign_count,
    )

    # Update sign count
    stored.sign_count = verification.new_sign_count
    await db.commit()

    # Get and return user
    user = await _get_user_by_uuid(db, stored.user_id)
    if user is None or not user.activo:
        raise ValueError("Usuario no encontrado o desactivado")

    return user


# ── Credential management ────────────────────────────────────────────

async def list_user_credentials(
    db: AsyncSession, user_uuid: str
) -> list[WebAuthnCredential]:
    return await _get_user_credentials(db, user_uuid)


async def delete_credential(
    db: AsyncSession, user_uuid: str, credential_uuid: UUID
) -> bool:
    result = await db.execute(
        select(WebAuthnCredential).where(
            WebAuthnCredential.uuid == credential_uuid,
            WebAuthnCredential.user_id == user_uuid,
        )
    )
    cred = result.scalar_one_or_none()
    if cred is None:
        return False
    await db.delete(cred)
    await db.commit()
    return True


# ── Helpers ──────────────────────────────────────────────────────────

async def _get_user_credentials(
    db: AsyncSession, user_uuid: str
) -> list[WebAuthnCredential]:
    result = await db.execute(
        select(WebAuthnCredential).where(
            WebAuthnCredential.user_id == user_uuid,
            WebAuthnCredential.activo == True,  # noqa: E712
        )
    )
    return list(result.scalars().all())


async def _get_credential_by_id(
    db: AsyncSession, credential_id: bytes
) -> WebAuthnCredential | None:
    result = await db.execute(
        select(WebAuthnCredential).where(
            WebAuthnCredential.credential_id == credential_id
        )
    )
    return result.scalar_one_or_none()


async def _get_user_by_username(db: AsyncSession, username: str) -> Usuario | None:
    result = await db.execute(
        select(Usuario).where(Usuario.username == username)
    )
    return result.scalar_one_or_none()


async def _get_user_by_uuid(db: AsyncSession, user_uuid) -> Usuario | None:
    result = await db.execute(
        select(Usuario).where(Usuario.uuid == user_uuid)
    )
    return result.scalar_one_or_none()
