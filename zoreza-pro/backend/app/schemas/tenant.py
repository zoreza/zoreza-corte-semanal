"""Tenant schemas — for super-admin API."""

from __future__ import annotations

from pydantic import BaseModel, Field


class TenantCreate(BaseModel):
    slug: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-z0-9][a-z0-9\-]{1,48}[a-z0-9]$")
    nombre: str = Field(..., min_length=1, max_length=200)
    contacto_nombre: str | None = None
    contacto_email: str | None = None
    contacto_telefono: str | None = None
    plan: str = "basico"
    admin_password: str = Field(default="admin123", min_length=6)


class TenantOut(BaseModel):
    uuid: str
    slug: str
    nombre: str
    contacto_nombre: str | None
    contacto_email: str | None
    contacto_telefono: str | None
    plan: str
    activo: bool
    notas: str | None
    created_at: str

    model_config = {"from_attributes": True}


class TenantUpdate(BaseModel):
    nombre: str | None = None
    contacto_nombre: str | None = None
    contacto_email: str | None = None
    contacto_telefono: str | None = None
    plan: str | None = None
    activo: bool | None = None
    notas: str | None = None


class SuperAdminLogin(BaseModel):
    username: str
    password: str
