"""Database seeder — creates initial data (admin user, catalogs, config)."""

from __future__ import annotations

import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.db.session import async_session_factory, engine
from app.db.base import Base
from app.models import (  # noqa: F401 — ensure all models are imported for metadata
    AuditLog,
    CatEventoContador,
    CatIrregularidad,
    CatOmision,
    Cliente,
    Config,
    Corte,
    CorteDetalle,
    Gasto,
    Maquina,
    MaquinaRuta,
    Notification,
    Ruta,
    Usuario,
    UsuarioRuta,
)


async def seed_database() -> None:
    """Create tables and seed initial data if empty."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_factory() as db:
        await _seed_usuarios(db)
        await _seed_catalogs(db)
        await _seed_config(db)


async def _seed_usuarios(db: AsyncSession) -> None:
    result = await db.execute(select(Usuario).limit(1))
    if result.scalar_one_or_none() is not None:
        return

    users = [
        Usuario(
            username="admin",
            password_hash=hash_password("admin123"),
            nombre="Administrador Zoreza",
            rol="ADMIN",
        ),
        Usuario(
            username="operador",
            password_hash=hash_password("operador123"),
            nombre="Operador Demo",
            rol="OPERADOR",
        ),
    ]
    db.add_all(users)
    await db.commit()


async def _seed_catalogs(db: AsyncSession) -> None:
    # Irregularidades
    result = await db.execute(select(CatIrregularidad).limit(1))
    if result.scalar_one_or_none() is None:
        db.add_all([
            CatIrregularidad(nombre="Manipulación declarada", requiere_nota=False),
            CatIrregularidad(nombre="Manipulación no declarada", requiere_nota=True),
            CatIrregularidad(nombre="Falla Técnica del equipo", requiere_nota=False),
            CatIrregularidad(
                nombre="Desconocido, posible manipulación por terceros", requiere_nota=True
            ),
        ])

    # Omisiones
    result = await db.execute(select(CatOmision).limit(1))
    if result.scalar_one_or_none() is None:
        db.add_all([
            CatOmision(nombre="No accesible", requiere_nota=False),
            CatOmision(nombre="Fuera de servicio", requiere_nota=False),
            CatOmision(nombre="Cliente no autorizó", requiere_nota=False),
            CatOmision(nombre="Falta de llave / acceso", requiere_nota=False),
            CatOmision(nombre="Otro", requiere_nota=True),
            CatOmision(nombre="Desconocido", requiere_nota=True),
        ])

    # Eventos contador
    result = await db.execute(select(CatEventoContador).limit(1))
    if result.scalar_one_or_none() is None:
        db.add_all([
            CatEventoContador(nombre="Reset contador", requiere_nota=True),
            CatEventoContador(nombre="Falla", requiere_nota=True),
            CatEventoContador(nombre="Cambio de tablero", requiere_nota=True),
            CatEventoContador(nombre="Mantenimiento", requiere_nota=True),
            CatEventoContador(nombre="Otro", requiere_nota=True),
        ])

    await db.commit()


async def _seed_config(db: AsyncSession) -> None:
    result = await db.execute(select(Config).limit(1))
    if result.scalar_one_or_none() is not None:
        return

    defaults = {
        "tolerancia_pesos": "30",
        "fondo_sugerido": "500",
        "semana_inicia": "LUNES",
        "ticket_negocio_nombre": "Zoreza",
        "ticket_footer": "Gracias por su preferencia.",
    }
    db.add_all([Config(key=k, value=v) for k, v in defaults.items()])
    await db.commit()


if __name__ == "__main__":
    asyncio.run(seed_database())
