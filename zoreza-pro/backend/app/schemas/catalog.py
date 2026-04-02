"""Catalog schemas (irregularidad, omision, evento_contador)."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field


class CatalogItemCreate(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=150)
    requiere_nota: bool = False
    activo: bool = True


class CatalogItemUpdate(BaseModel):
    nombre: str | None = Field(None, min_length=2, max_length=150)
    requiere_nota: bool | None = None
    activo: bool | None = None


class CatalogItemOut(BaseModel):
    uuid: UUID
    nombre: str
    requiere_nota: bool
    activo: bool

    model_config = {"from_attributes": True}
