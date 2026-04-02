"""Cliente model — business entities that own machines."""

from __future__ import annotations

from sqlalchemy import Boolean, Float, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Cliente(Base):
    __tablename__ = "clientes"

    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    telefono: Mapped[str] = mapped_column(String(30), nullable=False, default="")
    email: Mapped[str | None] = mapped_column(String(200), nullable=True)
    direccion_postal: Mapped[str | None] = mapped_column(String(400), nullable=True)
    comision_pct: Mapped[float] = mapped_column(Float, default=0.40)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")

    maquinas = relationship("Maquina", back_populates="cliente", lazy="selectin")
