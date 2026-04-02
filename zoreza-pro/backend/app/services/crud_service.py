"""CRUD services for catalogs, clientes, maquinas, rutas, gastos."""

from __future__ import annotations

from datetime import date
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.catalogs import CatEventoContador, CatIrregularidad, CatOmision
from app.models.cliente import Cliente
from app.models.gasto import Gasto
from app.models.maquina import Maquina
from app.models.maquina_ruta import MaquinaRuta
from app.models.ruta import Ruta
from app.models.usuario import Usuario
from app.models.usuario_ruta import UsuarioRuta


# ── Generic catalog CRUD ────────────────────────────────────────────
_CATALOG_MAP = {
    "irregularidad": CatIrregularidad,
    "omision": CatOmision,
    "evento_contador": CatEventoContador,
}


async def list_catalog(db: AsyncSession, catalog: str, activo: bool | None = None):
    model = _CATALOG_MAP.get(catalog)
    if model is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Catálogo desconocido: {catalog}")
    stmt = select(model).order_by(model.nombre)
    if activo is not None:
        stmt = stmt.where(model.activo == activo)
    return list((await db.execute(stmt)).scalars().all())


async def upsert_catalog(db: AsyncSession, catalog: str, item_uuid: UUID | None, data: dict):
    model = _CATALOG_MAP.get(catalog)
    if model is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Catálogo desconocido: {catalog}")
    if item_uuid:
        obj = await db.get(model, item_uuid)
        if obj is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Registro no encontrado")
        for k, v in data.items():
            if v is not None:
                setattr(obj, k, v)
    else:
        obj = model(**data)
        db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


# ── Cliente CRUD ────────────────────────────────────────────────────
async def list_clientes(db: AsyncSession, activo: bool | None = None) -> list[Cliente]:
    stmt = select(Cliente).order_by(Cliente.nombre)
    if activo is not None:
        stmt = stmt.where(Cliente.activo == activo)
    return list((await db.execute(stmt)).scalars().all())


async def create_cliente(db: AsyncSession, data: dict) -> Cliente:
    obj = Cliente(**data)
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


async def update_cliente(db: AsyncSession, uuid: UUID, data: dict) -> Cliente:
    obj = await db.get(Cliente, uuid)
    if obj is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Cliente no encontrado")
    for k, v in data.items():
        if v is not None:
            setattr(obj, k, v)
    await db.commit()
    await db.refresh(obj)
    return obj


# ── Maquina CRUD ────────────────────────────────────────────────────
async def list_maquinas(
    db: AsyncSession, cliente_id: UUID | None = None, activo: bool | None = None
) -> list[Maquina]:
    stmt = select(Maquina).order_by(Maquina.codigo)
    if cliente_id:
        stmt = stmt.where(Maquina.cliente_id == cliente_id)
    if activo is not None:
        stmt = stmt.where(Maquina.activo == activo)
    return list((await db.execute(stmt)).scalars().all())


async def create_maquina(db: AsyncSession, data: dict) -> Maquina:
    obj = Maquina(**data)
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


async def update_maquina(db: AsyncSession, uuid: UUID, data: dict) -> Maquina:
    obj = await db.get(Maquina, uuid)
    if obj is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Máquina no encontrada")
    for k, v in data.items():
        if v is not None:
            setattr(obj, k, v)
    await db.commit()
    await db.refresh(obj)
    return obj


# ── Ruta CRUD ───────────────────────────────────────────────────────
async def list_rutas(db: AsyncSession, activo: bool | None = None) -> list[Ruta]:
    stmt = select(Ruta).order_by(Ruta.nombre)
    if activo is not None:
        stmt = stmt.where(Ruta.activo == activo)
    return list((await db.execute(stmt)).scalars().all())


async def create_ruta(db: AsyncSession, data: dict) -> Ruta:
    obj = Ruta(**data)
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


async def update_ruta(db: AsyncSession, uuid: UUID, data: dict) -> Ruta:
    obj = await db.get(Ruta, uuid)
    if obj is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Ruta no encontrada")
    for k, v in data.items():
        if v is not None:
            setattr(obj, k, v)
    await db.commit()
    await db.refresh(obj)
    return obj


# ── Assignments ─────────────────────────────────────────────────────
async def set_usuario_ruta(
    db: AsyncSession, usuario_id: UUID, ruta_id: UUID, activo: bool = True
) -> UsuarioRuta:
    result = await db.execute(
        select(UsuarioRuta).where(
            UsuarioRuta.usuario_id == usuario_id, UsuarioRuta.ruta_id == ruta_id
        )
    )
    obj = result.scalar_one_or_none()
    if obj is None:
        obj = UsuarioRuta(usuario_id=usuario_id, ruta_id=ruta_id, activo=activo)
        db.add(obj)
    else:
        obj.activo = activo
    await db.commit()
    await db.refresh(obj)
    return obj


async def set_maquina_ruta(
    db: AsyncSession, maquina_id: UUID, ruta_id: UUID, activo: bool = True
) -> MaquinaRuta:
    result = await db.execute(
        select(MaquinaRuta).where(
            MaquinaRuta.maquina_id == maquina_id, MaquinaRuta.ruta_id == ruta_id
        )
    )
    obj = result.scalar_one_or_none()
    if obj is None:
        obj = MaquinaRuta(maquina_id=maquina_id, ruta_id=ruta_id, activo=activo)
        db.add(obj)
    else:
        obj.activo = activo
    await db.commit()
    await db.refresh(obj)
    return obj


# ── Gastos CRUD ─────────────────────────────────────────────────────
async def list_gastos(
    db: AsyncSession,
    fecha_inicio: date | None = None,
    fecha_fin: date | None = None,
    categoria: str | None = None,
    limit: int = 200,
    offset: int = 0,
) -> list[Gasto]:
    stmt = select(Gasto).order_by(Gasto.fecha.desc())
    if fecha_inicio:
        stmt = stmt.where(Gasto.fecha >= fecha_inicio)
    if fecha_fin:
        stmt = stmt.where(Gasto.fecha <= fecha_fin)
    if categoria:
        stmt = stmt.where(Gasto.categoria == categoria)
    return list((await db.execute(stmt.limit(limit).offset(offset))).scalars().all())


async def create_gasto(db: AsyncSession, data: dict, actor_id: UUID) -> Gasto:
    obj = Gasto(**data, created_by=actor_id)
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


async def delete_gasto(db: AsyncSession, gasto_id: UUID) -> None:
    obj = await db.get(Gasto, gasto_id)
    if obj is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Gasto no encontrado")
    await db.delete(obj)
    await db.commit()


async def get_gastos_summary(
    db: AsyncSession,
    fecha_inicio: date | None = None,
    fecha_fin: date | None = None,
) -> dict:
    stmt = select(
        func.coalesce(func.sum(Gasto.monto), 0).label("total"),
        func.count(Gasto.uuid).label("count"),
    )
    if fecha_inicio:
        stmt = stmt.where(Gasto.fecha >= fecha_inicio)
    if fecha_fin:
        stmt = stmt.where(Gasto.fecha <= fecha_fin)
    row = (await db.execute(stmt)).one()
    total = float(row.total)
    count = int(row.count)
    return {
        "total": total,
        "count": count,
        "promedio": round(total / count, 2) if count else 0,
    }
