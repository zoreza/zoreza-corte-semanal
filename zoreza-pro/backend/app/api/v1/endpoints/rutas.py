"""Rutas endpoints."""

from uuid import UUID

from fastapi import APIRouter

from app.core.deps import AdminUser, DbSession
from app.schemas.ruta import RutaCreate, RutaOut, RutaUpdate
from app.services.crud_service import create_ruta, list_rutas, update_ruta, set_maquina_ruta

router = APIRouter()


@router.get("", response_model=list[RutaOut])
async def list_routes(db: DbSession, _admin: AdminUser, activo: bool | None = None):
    return await list_rutas(db, activo=activo)


@router.post("", response_model=RutaOut, status_code=201)
async def create_route(body: RutaCreate, db: DbSession, _admin: AdminUser):
    return await create_ruta(db, body.model_dump())


@router.patch("/{ruta_id}", response_model=RutaOut)
async def update_route(ruta_id: UUID, body: RutaUpdate, db: DbSession, _admin: AdminUser):
    return await update_ruta(db, ruta_id, body.model_dump(exclude_unset=True))


@router.get("/{ruta_id}/maquinas", status_code=200)
async def list_ruta_machines(ruta_id: UUID, db: DbSession, _admin: AdminUser):
    from sqlalchemy import select
    from app.models import MaquinaRuta
    result = await db.execute(
        select(MaquinaRuta).where(MaquinaRuta.ruta_id == ruta_id, MaquinaRuta.activo == True)  # noqa: E712
    )
    items = result.scalars().all()
    return [
        {
            "maquina_id": str(mr.maquina_id),
            "codigo": mr.maquina.codigo if mr.maquina else None,
            "cliente_nombre": mr.maquina.cliente.nombre if mr.maquina and mr.maquina.cliente else None,
        }
        for mr in items
    ]


@router.post("/{ruta_id}/maquinas/{maquina_id}", status_code=200)
async def assign_machine(ruta_id: UUID, maquina_id: UUID, db: DbSession, _admin: AdminUser):
    obj = await set_maquina_ruta(db, maquina_id, ruta_id)
    return {"maquina_id": str(obj.maquina_id), "ruta_id": str(obj.ruta_id), "activo": obj.activo}


@router.delete("/{ruta_id}/maquinas/{maquina_id}", status_code=200)
async def unassign_machine(ruta_id: UUID, maquina_id: UUID, db: DbSession, _admin: AdminUser):
    obj = await set_maquina_ruta(db, maquina_id, ruta_id, activo=False)
    return {"maquina_id": str(obj.maquina_id), "ruta_id": str(obj.ruta_id), "activo": obj.activo}
