"""Catalog tables: irregularidad, omision, evento_contador."""

from __future__ import annotations

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class CatIrregularidad(Base):
    __tablename__ = "cat_irregularidad"

    nombre: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    requiere_nota: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    activo: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")


class CatOmision(Base):
    __tablename__ = "cat_omision"

    nombre: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    requiere_nota: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    activo: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")


class CatEventoContador(Base):
    __tablename__ = "cat_evento_contador"

    nombre: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    requiere_nota: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    activo: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
