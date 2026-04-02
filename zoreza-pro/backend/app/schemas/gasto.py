"""Gasto schemas."""

from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field

_CATS = ("REFACCIONES", "FONDOS_ROBOS", "PERMISOS", "EMPLEADOS", "SERVICIOS", "TRANSPORTE", "OTRO")


class GastoCreate(BaseModel):
    fecha: date
    categoria: str = Field(..., min_length=1, max_length=30)
    descripcion: str = Field(..., min_length=1, max_length=200)
    monto: float = Field(..., gt=0)
    notas: str | None = Field(None, max_length=500)


class GastoOut(BaseModel):
    uuid: UUID
    fecha: date
    categoria: str
    descripcion: str
    monto: float
    notas: str | None
    created_by: UUID | None
    created_at: datetime

    model_config = {"from_attributes": True}


class GastosSummary(BaseModel):
    total: float
    count: int
    promedio: float
    por_categoria: dict[str, float]
