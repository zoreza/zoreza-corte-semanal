"""Maquina model — vending / arcade machines."""

from __future__ import annotations

import uuid

from sqlalchemy import Boolean, Float, ForeignKey, String
from app.db.base import UUIDType
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Maquina(Base):
    __tablename__ = "maquinas"

    codigo: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    fondo: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    cliente_id: Mapped[uuid.UUID | None] = mapped_column(
        UUIDType(), ForeignKey("clientes.uuid"), nullable=True, default=None
    )
    activo: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")

    cliente = relationship("Cliente", back_populates="maquinas", lazy="selectin")
    rutas = relationship("MaquinaRuta", back_populates="maquina", lazy="selectin")
