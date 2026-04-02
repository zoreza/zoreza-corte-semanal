"""Ruta model — service routes grouping operators and machines."""

from __future__ import annotations

from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Ruta(Base):
    __tablename__ = "rutas"

    nombre: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")

    usuarios = relationship("UsuarioRuta", back_populates="ruta", lazy="selectin")
    maquinas = relationship("MaquinaRuta", back_populates="ruta", lazy="selectin")
