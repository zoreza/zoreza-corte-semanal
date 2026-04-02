"""Usuarios endpoints."""

from uuid import UUID

from fastapi import APIRouter

from app.core.deps import AdminUser, DbSession
from app.schemas.usuario import UsuarioCreate, UsuarioOut, UsuarioUpdate
from app.services.usuario_service import create_usuario, list_usuarios, update_usuario

router = APIRouter()


@router.get("", response_model=list[UsuarioOut])
async def list_users(db: DbSession, _admin: AdminUser, activo: bool | None = None):
    return await list_usuarios(db, activo=activo)


@router.post("", response_model=UsuarioOut, status_code=201)
async def create_user(body: UsuarioCreate, db: DbSession, _admin: AdminUser):
    return await create_usuario(db, body)


@router.patch("/{user_id}", response_model=UsuarioOut)
async def update_user(user_id: UUID, body: UsuarioUpdate, db: DbSession, _admin: AdminUser):
    user = await update_usuario(db, user_id, body)
    if user is None:
        from fastapi import HTTPException, status
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Usuario no encontrado")
    return user
