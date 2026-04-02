"""Usuario schemas."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field


class UsuarioCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=128)
    nombre: str = Field(..., min_length=2, max_length=150)
    telefono: str = Field(..., min_length=1, max_length=30)
    email: str = Field(..., min_length=1, max_length=200)
    rol: str = Field(..., pattern="^(ADMIN|SUPERVISOR|OPERADOR)$")
    activo: bool = True


class UsuarioUpdate(BaseModel):
    nombre: str | None = Field(None, min_length=2, max_length=150)
    telefono: str | None = Field(None, min_length=1, max_length=30)
    email: str | None = Field(None, min_length=1, max_length=200)
    rol: str | None = Field(None, pattern="^(ADMIN|SUPERVISOR|OPERADOR)$")
    activo: bool | None = None
    password: str | None = Field(None, min_length=6, max_length=128)


class UsuarioOut(BaseModel):
    uuid: UUID
    username: str
    nombre: str
    telefono: str
    email: str
    rol: str
    activo: bool

    model_config = {"from_attributes": True}
