"""Super-admin endpoints — tenant management + platform auth + APK releases.

All routes here are mounted under /zoreza-admin/api/...
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import select

from app.core.deps import MasterDbSession, SuperAdminUser
from app.core.security import create_access_token, create_refresh_token, hash_password, verify_password
from app.models.tenant import SuperAdmin, Tenant
from app.models.app_release import AppRelease
from app.schemas.tenant import SuperAdminLogin, TenantCreate, TenantOut, TenantUpdate
from app.schemas.release import ReleaseCreate, ReleaseLatest, ReleaseOut
from app.services.tenant_service import create_tenant

RELEASES_DIR = Path("data/releases")

router = APIRouter()


# ── Super-admin auth ─────────────────────────────────────────────────

@router.post("/auth/login")
async def superadmin_login(body: SuperAdminLogin, db: MasterDbSession):
    result = await db.execute(
        select(SuperAdmin).where(SuperAdmin.username == body.username)
    )
    admin = result.scalar_one_or_none()
    if admin is None or not verify_password(body.password, admin.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Credenciales inválidas")
    if not admin.activo:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Cuenta desactivada")

    access = create_access_token({"sub": str(admin.uuid)})
    refresh = create_refresh_token({"sub": str(admin.uuid)})
    return {
        "access_token": access,
        "refresh_token": refresh,
        "nombre": admin.nombre,
        "rol": "SUPERADMIN",
    }


@router.get("/auth/me")
async def superadmin_me(admin: SuperAdminUser):
    return {
        "uuid": str(admin.uuid),
        "username": admin.username,
        "nombre": admin.nombre,
        "rol": "SUPERADMIN",
    }


# ── Tenant CRUD ──────────────────────────────────────────────────────

@router.get("/tenants", response_model=list[TenantOut])
async def list_tenants(db: MasterDbSession, _admin: SuperAdminUser):
    result = await db.execute(select(Tenant).order_by(Tenant.created_at.desc()))
    tenants = result.scalars().all()
    return [_to_out(t) for t in tenants]


@router.post("/tenants", response_model=TenantOut, status_code=201)
async def create_tenant_endpoint(body: TenantCreate, db: MasterDbSession, _admin: SuperAdminUser):
    tenant = await create_tenant(
        db,
        slug=body.slug,
        nombre=body.nombre,
        contacto_nombre=body.contacto_nombre,
        contacto_email=body.contacto_email,
        contacto_telefono=body.contacto_telefono,
        plan=body.plan,
        admin_password=body.admin_password,
    )
    return _to_out(tenant)


@router.get("/tenants/{slug}", response_model=TenantOut)
async def get_tenant(slug: str, db: MasterDbSession, _admin: SuperAdminUser):
    result = await db.execute(select(Tenant).where(Tenant.slug == slug))
    tenant = result.scalar_one_or_none()
    if tenant is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Tenant no encontrado")
    return _to_out(tenant)


@router.put("/tenants/{slug}", response_model=TenantOut)
async def update_tenant(slug: str, body: TenantUpdate, db: MasterDbSession, _admin: SuperAdminUser):
    result = await db.execute(select(Tenant).where(Tenant.slug == slug))
    tenant = result.scalar_one_or_none()
    if tenant is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Tenant no encontrado")

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(tenant, field, value)
    await db.commit()
    await db.refresh(tenant)
    return _to_out(tenant)


@router.post("/tenants/{slug}/reset-password")
async def reset_tenant_admin_password(
    slug: str,
    body: dict,
    db: MasterDbSession,
    _admin: SuperAdminUser,
):
    """Reset the admin user's password for a specific tenant."""
    new_password = body.get("password", "").strip()
    if len(new_password) < 6:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "La contraseña debe tener al menos 6 caracteres")

    # Verify tenant exists
    result = await db.execute(select(Tenant).where(Tenant.slug == slug))
    tenant = result.scalar_one_or_none()
    if tenant is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Tenant no encontrado")

    # Update admin password in tenant DB
    from app.db.tenant_session import get_tenant_session_factory
    from app.models.usuario import Usuario

    factory = await get_tenant_session_factory(slug)
    async with factory() as tenant_db:
        res = await tenant_db.execute(
            select(Usuario).where(Usuario.username == "admin")
        )
        admin_user = res.scalar_one_or_none()
        if admin_user is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Usuario admin no encontrado en el tenant")
        admin_user.password_hash = hash_password(new_password)
        await tenant_db.commit()

    return {"ok": True, "message": f"Contraseña del admin de '{slug}' actualizada"}


def _to_out(t: Tenant) -> TenantOut:
    return TenantOut(
        uuid=str(t.uuid),
        slug=t.slug,
        nombre=t.nombre,
        contacto_nombre=t.contacto_nombre,
        contacto_email=t.contacto_email,
        contacto_telefono=t.contacto_telefono,
        plan=t.plan,
        activo=t.activo,
        notas=t.notas,
        created_at=t.created_at.isoformat() if t.created_at else "",
    )


# ── App Releases (APK management) ───────────────────────────────────


def _release_download_url(r: AppRelease) -> str:
    return f"/zoreza-admin/api/releases/{r.uuid}/download"


def _release_to_out(r: AppRelease) -> ReleaseOut:
    return ReleaseOut(
        uuid=str(r.uuid),
        version_name=r.version_name,
        version_code=r.version_code,
        filename=r.filename,
        file_size=r.file_size,
        release_notes=r.release_notes,
        is_mandatory=r.is_mandatory,
        activo=r.activo,
        download_url=_release_download_url(r),
        created_at=r.created_at.isoformat() if r.created_at else "",
    )


@router.get("/releases", response_model=list[ReleaseOut])
async def list_releases(db: MasterDbSession, _admin: SuperAdminUser):
    result = await db.execute(
        select(AppRelease).order_by(AppRelease.version_code.desc())
    )
    releases = result.scalars().all()
    return [_release_to_out(r) for r in releases]


@router.post("/releases", response_model=ReleaseOut, status_code=201)
async def upload_release(
    db: MasterDbSession,
    _admin: SuperAdminUser,
    file: UploadFile = File(...),
    version_name: str = Form(...),
    version_code: int = Form(...),
    release_notes: str = Form(default=""),
    is_mandatory: bool = Form(default=False),
):
    if not file.filename or not file.filename.endswith(".apk"):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Solo se aceptan archivos .apk")

    # Ensure unique version_code
    existing = await db.execute(
        select(AppRelease).where(AppRelease.version_code == version_code)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status.HTTP_409_CONFLICT, f"Ya existe una release con version_code={version_code}")

    RELEASES_DIR.mkdir(parents=True, exist_ok=True)
    safe_name = f"zoreza-pro-v{version_name}-{version_code}.apk"
    dest = RELEASES_DIR / safe_name

    # Stream file to disk
    total = 0
    with open(dest, "wb") as f:
        while chunk := await file.read(1024 * 256):
            f.write(chunk)
            total += len(chunk)

    release = AppRelease(
        version_name=version_name,
        version_code=version_code,
        filename=safe_name,
        file_size=total,
        release_notes=release_notes or None,
        is_mandatory=is_mandatory,
    )
    db.add(release)
    await db.commit()
    await db.refresh(release)
    return _release_to_out(release)


@router.get("/releases/latest", response_model=ReleaseLatest)
async def get_latest_release(db: MasterDbSession):
    """Public endpoint — returns latest active release info for auto-update."""
    result = await db.execute(
        select(AppRelease)
        .where(AppRelease.activo.is_(True))
        .order_by(AppRelease.version_code.desc())
        .limit(1)
    )
    release = result.scalar_one_or_none()
    if not release:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No hay releases disponibles")
    return ReleaseLatest(
        version_name=release.version_name,
        version_code=release.version_code,
        release_notes=release.release_notes,
        is_mandatory=release.is_mandatory,
        download_url=_release_download_url(release),
    )


@router.delete("/releases/{release_uuid}")
async def delete_release(release_uuid: str, db: MasterDbSession, _admin: SuperAdminUser):
    release = await db.get(AppRelease, release_uuid)
    if not release:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Release no encontrada")
    # Delete file from disk
    fpath = RELEASES_DIR / release.filename
    if fpath.exists():
        fpath.unlink()
    await db.delete(release)
    await db.commit()
    return {"ok": True}


@router.get("/releases/{release_uuid}/download")
async def download_release(release_uuid: str, db: MasterDbSession):
    """Public download — no auth required for APK download."""
    release = await db.get(AppRelease, release_uuid)
    if not release or not release.activo:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Release no encontrada")
    fpath = RELEASES_DIR / release.filename
    if not fpath.exists():
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Archivo no encontrado")
    return FileResponse(
        path=str(fpath),
        filename=release.filename,
        media_type="application/vnd.android.package-archive",
    )
