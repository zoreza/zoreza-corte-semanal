"""RBAC service — route / client / machine filtering by role."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cliente import Cliente
from app.models.maquina import Maquina
from app.models.maquina_ruta import MaquinaRuta
from app.models.ruta import Ruta
from app.models.usuario import Usuario
from app.models.usuario_ruta import UsuarioRuta


async def allowed_ruta_ids(db: AsyncSession, user: Usuario) -> list[UUID]:
    if user.is_supervisor():
        result = await db.execute(select(Ruta.uuid).where(Ruta.activo.is_(True)))
        return list(result.scalars().all())
    result = await db.execute(
        select(UsuarioRuta.ruta_id).where(
            UsuarioRuta.usuario_id == user.uuid,
            UsuarioRuta.activo.is_(True),
        )
    )
    return list(result.scalars().all())


async def allowed_clientes(db: AsyncSession, user: Usuario) -> list[Cliente]:
    if user.is_supervisor():
        result = await db.execute(
            select(Cliente).where(Cliente.activo.is_(True)).order_by(Cliente.nombre)
        )
        return list(result.scalars().all())

    ruta_ids = await allowed_ruta_ids(db, user)
    if not ruta_ids:
        return []
    # Clients that have at least one machine on an allowed route
    machine_ids = (
        select(MaquinaRuta.maquina_id)
        .where(MaquinaRuta.ruta_id.in_(ruta_ids), MaquinaRuta.activo.is_(True))
        .scalar_subquery()
    )
    cliente_ids = (
        select(Maquina.cliente_id)
        .where(Maquina.uuid.in_(machine_ids), Maquina.activo.is_(True))
        .distinct()
        .scalar_subquery()
    )
    result = await db.execute(
        select(Cliente)
        .where(Cliente.uuid.in_(cliente_ids), Cliente.activo.is_(True))
        .order_by(Cliente.nombre)
    )
    return list(result.scalars().all())


async def allowed_maquinas(
    db: AsyncSession, user: Usuario, cliente_id: UUID
) -> list[Maquina]:
    stmt = select(Maquina).where(
        Maquina.cliente_id == cliente_id, Maquina.activo.is_(True)
    )
    if not user.is_supervisor():
        ruta_ids = await allowed_ruta_ids(db, user)
        if not ruta_ids:
            return []
        machine_ids = (
            select(MaquinaRuta.maquina_id)
            .where(MaquinaRuta.ruta_id.in_(ruta_ids), MaquinaRuta.activo.is_(True))
            .scalar_subquery()
        )
        stmt = stmt.where(Maquina.uuid.in_(machine_ids))

    result = await db.execute(stmt.order_by(Maquina.codigo))
    return list(result.scalars().all())
