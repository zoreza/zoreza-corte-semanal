"""Bridge: Maquina ↔ Ruta."""

from __future__ import annotations

import uuid

from sqlalchemy import Boolean, ForeignKey, UniqueConstraint
from app.db.base import UUIDType
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class MaquinaRuta(Base):
    __tablename__ = "maquina_ruta"
    __table_args__ = (
        UniqueConstraint("maquina_id", "ruta_id", name="uq_maquina_ruta"),
    )

    maquina_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType(), ForeignKey("maquinas.uuid"), nullable=False
    )
    ruta_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType(), ForeignKey("rutas.uuid"), nullable=False
    )
    activo: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")

    maquina = relationship("Maquina", back_populates="rutas", lazy="selectin")
    ruta = relationship("Ruta", back_populates="maquinas", lazy="selectin")
