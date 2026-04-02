"""Clientes endpoints."""

from uuid import UUID

from fastapi import APIRouter

from app.core.deps import AdminUser, CurrentUser, DbSession
from app.schemas.cliente import ClienteCreate, ClienteOut, ClienteUpdate
from app.services.crud_service import create_cliente, list_clientes, update_cliente
from app.services.rbac_service import allowed_clientes

router = APIRouter()


@router.get("", response_model=list[ClienteOut])
async def list_clients(db: DbSession, user: CurrentUser, activo: bool | None = None):
    if user.is_supervisor():
        return await list_clientes(db, activo=activo)
    return await allowed_clientes(db, user)


@router.post("", response_model=ClienteOut, status_code=201)
async def create_client(body: ClienteCreate, db: DbSession, _admin: AdminUser):
    return await create_cliente(db, body.model_dump())


@router.patch("/{cliente_id}", response_model=ClienteOut)
async def update_client(
    cliente_id: UUID, body: ClienteUpdate, db: DbSession, _admin: AdminUser
):
    return await update_cliente(db, cliente_id, body.model_dump(exclude_unset=True))
