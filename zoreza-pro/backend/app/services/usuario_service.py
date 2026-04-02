"""Usuario service — CRUD + lookup."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate


async def get_usuario_by_uuid(db: AsyncSession, user_uuid: str | UUID) -> Usuario | None:
    result = await db.execute(select(Usuario).where(Usuario.uuid == user_uuid))
    return result.scalar_one_or_none()


async def get_usuario_by_username(db: AsyncSession, username: str) -> Usuario | None:
    result = await db.execute(select(Usuario).where(Usuario.username == username))
    return result.scalar_one_or_none()


async def list_usuarios(db: AsyncSession, activo: bool | None = None) -> list[Usuario]:
    stmt = select(Usuario).order_by(Usuario.nombre)
    if activo is not None:
        stmt = stmt.where(Usuario.activo == activo)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def create_usuario(db: AsyncSession, payload: UsuarioCreate) -> Usuario:
    user = Usuario(
        username=payload.username,
        password_hash=hash_password(payload.password),
        nombre=payload.nombre,
        telefono=payload.telefono,
        email=payload.email,
        rol=payload.rol,
        activo=payload.activo,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def update_usuario(
    db: AsyncSession, user_uuid: UUID, payload: UsuarioUpdate
) -> Usuario | None:
    user = await get_usuario_by_uuid(db, user_uuid)
    if user is None:
        return None
    update_data = payload.model_dump(exclude_unset=True)
    if "password" in update_data:
        update_data["password_hash"] = hash_password(update_data.pop("password"))
    for key, value in update_data.items():
        setattr(user, key, value)
    await db.commit()
    await db.refresh(user)
    return user
