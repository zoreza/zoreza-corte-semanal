"""Tenant provisioning service — create/manage tenant databases."""

from __future__ import annotations

import re

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.db.tenant_session import create_tenant_tables, get_tenant_session_factory
from app.models.tenant import Tenant
from app.models.usuario import Usuario
from app.models.catalogs import CatIrregularidad, CatOmision, CatEventoContador
from app.models.config import Config

_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9\-]{1,48}[a-z0-9]$")
_RESERVED_SLUGS = {"zoreza-admin", "api", "health", "docs", "redoc", "static", "assets"}


async def create_tenant(
    db: AsyncSession,
    *,
    slug: str,
    nombre: str,
    contacto_nombre: str | None = None,
    contacto_email: str | None = None,
    contacto_telefono: str | None = None,
    plan: str = "basico",
    admin_password: str = "admin123",
) -> Tenant:
    """Create a new tenant: register in master DB + provision tenant DB."""
    slug = slug.lower().strip()
    if not _SLUG_RE.match(slug):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Slug inválido. Use letras minúsculas, números y guiones (3-50 caracteres).",
        )
    if slug in _RESERVED_SLUGS:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Slug '{slug}' es reservado.")

    # Check uniqueness
    existing = await db.execute(select(Tenant).where(Tenant.slug == slug))
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, f"Tenant '{slug}' ya existe.")

    # 1) Register in master DB
    tenant = Tenant(
        slug=slug,
        nombre=nombre,
        contacto_nombre=contacto_nombre,
        contacto_email=contacto_email,
        contacto_telefono=contacto_telefono,
        plan=plan,
    )
    db.add(tenant)
    await db.commit()
    await db.refresh(tenant)

    # 2) Create tenant database & tables
    await create_tenant_tables(slug)

    # 3) Seed tenant database
    await _seed_tenant_db(slug, nombre, admin_password)

    return tenant


async def _seed_tenant_db(slug: str, nombre_comercio: str, admin_password: str) -> None:
    """Seed a new tenant DB with admin user, catalogs, and config."""
    factory = await get_tenant_session_factory(slug)
    async with factory() as db:
        # Admin user
        db.add(Usuario(
            username="admin",
            password_hash=hash_password(admin_password),
            nombre=f"Administrador",
            rol="ADMIN",
        ))

        # Catalogs
        db.add_all([
            CatIrregularidad(nombre="Manipulación declarada", requiere_nota=False),
            CatIrregularidad(nombre="Manipulación no declarada", requiere_nota=True),
            CatIrregularidad(nombre="Falla Técnica del equipo", requiere_nota=False),
            CatIrregularidad(nombre="Desconocido, posible manipulación por terceros", requiere_nota=True),
        ])
        db.add_all([
            CatOmision(nombre="No accesible", requiere_nota=False),
            CatOmision(nombre="Fuera de servicio", requiere_nota=False),
            CatOmision(nombre="Cliente no autorizó", requiere_nota=False),
            CatOmision(nombre="Falta de llave / acceso", requiere_nota=False),
            CatOmision(nombre="Otro", requiere_nota=True),
            CatOmision(nombre="Desconocido", requiere_nota=True),
        ])
        db.add_all([
            CatEventoContador(nombre="Reset contador", requiere_nota=True),
            CatEventoContador(nombre="Falla", requiere_nota=True),
            CatEventoContador(nombre="Cambio de tablero", requiere_nota=True),
            CatEventoContador(nombre="Mantenimiento", requiere_nota=True),
            CatEventoContador(nombre="Otro", requiere_nota=True),
        ])

        # Default config
        defaults = {
            "nombre_comercio": nombre_comercio,
            "tolerancia_pesos": "30",
            "fondo_sugerido": "500",
            "semana_inicia": "LUNES",
            "ticket_negocio_nombre": nombre_comercio,
            "ticket_footer": "Gracias por su preferencia.",
            "categorias_gasto": "REFACCIONES,FONDOS_ROBOS,PERMISOS,EMPLEADOS,SERVICIOS,TRANSPORTE,OTRO",
        }
        db.add_all([Config(key=k, value=v) for k, v in defaults.items()])

        await db.commit()
