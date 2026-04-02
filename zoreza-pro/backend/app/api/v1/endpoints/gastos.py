"""Gastos endpoints."""

from datetime import date
from uuid import UUID

from fastapi import APIRouter

from app.core.deps import AdminUser, DbSession
from app.schemas.gasto import GastoCreate, GastoOut, GastosSummary
from app.services.crud_service import create_gasto, delete_gasto, get_gastos_summary, list_gastos

router = APIRouter()


@router.get("", response_model=list[GastoOut])
async def list_expenses(
    db: DbSession,
    _admin: AdminUser,
    fecha_inicio: date | None = None,
    fecha_fin: date | None = None,
    categoria: str | None = None,
):
    return await list_gastos(db, fecha_inicio, fecha_fin, categoria)


@router.post("", response_model=GastoOut, status_code=201)
async def create_expense(body: GastoCreate, db: DbSession, admin: AdminUser):
    return await create_gasto(db, body.model_dump(), admin.uuid)


@router.delete("/{gasto_id}", status_code=204)
async def delete_expense(gasto_id: UUID, db: DbSession, _admin: AdminUser):
    await delete_gasto(db, gasto_id)


@router.get("/summary", response_model=GastosSummary)
async def expense_summary(
    db: DbSession,
    _admin: AdminUser,
    fecha_inicio: date | None = None,
    fecha_fin: date | None = None,
):
    data = await get_gastos_summary(db, fecha_inicio, fecha_fin)
    return GastosSummary(**data, por_categoria={})
