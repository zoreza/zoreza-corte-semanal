"""Máquinas endpoints."""

from uuid import UUID

from fastapi import APIRouter

from app.core.deps import AdminUser, CurrentUser, DbSession
from app.schemas.maquina import MaquinaCreate, MaquinaOut, MaquinaUpdate
from app.services.crud_service import create_maquina, list_maquinas, update_maquina

router = APIRouter()


@router.get("", response_model=list[MaquinaOut])
async def list_machines(
    db: DbSession, user: CurrentUser, cliente_id: UUID | None = None, activo: bool | None = None
):
    machines = await list_maquinas(db, cliente_id=cliente_id, activo=activo)
    return [
        MaquinaOut(
            uuid=m.uuid,
            codigo=m.codigo,
            fondo=m.fondo,
            cliente_id=m.cliente_id,
            activo=m.activo,
            cliente_nombre=m.cliente.nombre if m.cliente else None,
        )
        for m in machines
    ]


@router.post("", response_model=MaquinaOut, status_code=201)
async def create_machine(body: MaquinaCreate, db: DbSession, _admin: AdminUser):
    m = await create_maquina(db, body.model_dump())
    return MaquinaOut(
        uuid=m.uuid, codigo=m.codigo, fondo=m.fondo, cliente_id=m.cliente_id, activo=m.activo,
        cliente_nombre=m.cliente.nombre if m.cliente else None,
    )


@router.patch("/{maquina_id}", response_model=MaquinaOut)
async def update_machine(
    maquina_id: UUID, body: MaquinaUpdate, db: DbSession, _admin: AdminUser
):
    m = await update_maquina(db, maquina_id, body.model_dump(exclude_unset=True))
    return MaquinaOut(
        uuid=m.uuid, codigo=m.codigo, fondo=m.fondo, cliente_id=m.cliente_id, activo=m.activo,
        cliente_nombre=m.cliente.nombre if m.cliente else None,
    )
