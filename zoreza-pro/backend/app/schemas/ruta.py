"""Ruta schemas."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field


class RutaCreate(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100)
    descripcion: str | None = None
    activo: bool = True


class RutaUpdate(BaseModel):
    nombre: str | None = Field(None, min_length=2, max_length=100)
    descripcion: str | None = None
    activo: bool | None = None


class RutaOut(BaseModel):
    uuid: UUID
    nombre: str
    descripcion: str | None
    activo: bool

    model_config = {"from_attributes": True}
