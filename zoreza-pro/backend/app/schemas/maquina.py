"""Maquina schemas."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field


class MaquinaCreate(BaseModel):
    codigo: str = Field(..., min_length=1, max_length=50)
    fondo: float = Field(0.0, ge=0)
    cliente_id: UUID | None = None
    activo: bool = True


class MaquinaUpdate(BaseModel):
    codigo: str | None = Field(None, min_length=1, max_length=50)
    fondo: float | None = Field(None, ge=0)
    cliente_id: UUID | None = None
    activo: bool | None = None


class MaquinaOut(BaseModel):
    uuid: UUID
    codigo: str
    fondo: float
    cliente_id: UUID | None = None
    activo: bool
    cliente_nombre: str | None = None

    model_config = {"from_attributes": True}
