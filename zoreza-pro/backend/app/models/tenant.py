"""Tenant model — lives in master DB."""

from __future__ import annotations

from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.master_base import MasterBase


class Tenant(MasterBase):
    __tablename__ = "tenants"

    slug: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    contacto_nombre: Mapped[str | None] = mapped_column(String(200), nullable=True)
    contacto_email: Mapped[str | None] = mapped_column(String(200), nullable=True)
    contacto_telefono: Mapped[str | None] = mapped_column(String(30), nullable=True)
    plan: Mapped[str] = mapped_column(String(30), default="basico")
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    notas: Mapped[str | None] = mapped_column(Text, nullable=True)


class SuperAdmin(MasterBase):
    """Platform-level super-admin (Zoreza Labs staff). Not tenant-scoped."""
    __tablename__ = "super_admins"

    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
