"""Cliente schemas."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field


class ClienteCreate(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=200)
    telefono: str = Field(..., min_length=1, max_length=30)
    email: str | None = Field(None, max_length=200)
    direccion_postal: str | None = Field(None, max_length=400)
    comision_pct: float = Field(0.40, ge=0.0, le=1.0)
    activo: bool = True


class ClienteUpdate(BaseModel):
    nombre: str | None = Field(None, min_length=2, max_length=200)
    telefono: str | None = Field(None, min_length=1, max_length=30)
    email: str | None = Field(None, max_length=200)
    direccion_postal: str | None = Field(None, max_length=400)
    comision_pct: float | None = Field(None, ge=0.0, le=1.0)
    activo: bool | None = None


class ClienteOut(BaseModel):
    uuid: UUID
    nombre: str
    telefono: str
    email: str | None = None
    direccion_postal: str | None = None
    comision_pct: float
    activo: bool

    model_config = {"from_attributes": True}
