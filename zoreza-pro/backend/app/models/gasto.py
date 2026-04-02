"""Gasto model — business expenses."""

from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import CheckConstraint, Date, Float, ForeignKey, String, Text
from app.db.base import UUIDType
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

GASTO_CATEGORIAS = (
    "REFACCIONES",
    "FONDOS_ROBOS",
    "PERMISOS",
    "EMPLEADOS",
    "SERVICIOS",
    "TRANSPORTE",
    "OTRO",
)


class Gasto(Base):
    __tablename__ = "gastos"

    fecha: Mapped[date] = mapped_column(Date, nullable=False)
    categoria: Mapped[str] = mapped_column(String(30), nullable=False)
    descripcion: Mapped[str] = mapped_column(String(200), nullable=False)
    monto: Mapped[float] = mapped_column(Float, nullable=False)
    notas: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUIDType(), ForeignKey("usuarios.uuid"), nullable=True
    )

    operador = relationship("Usuario", lazy="selectin")
