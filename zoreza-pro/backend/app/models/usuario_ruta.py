"""Bridge: Usuario ↔ Ruta."""

from __future__ import annotations

import uuid

from sqlalchemy import Boolean, ForeignKey, UniqueConstraint
from app.db.base import UUIDType
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class UsuarioRuta(Base):
    __tablename__ = "usuario_ruta"
    __table_args__ = (
        UniqueConstraint("usuario_id", "ruta_id", name="uq_usuario_ruta"),
    )

    usuario_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType(), ForeignKey("usuarios.uuid"), nullable=False
    )
    ruta_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType(), ForeignKey("rutas.uuid"), nullable=False
    )
    activo: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")

    usuario = relationship("Usuario", back_populates="rutas", lazy="selectin")
    ruta = relationship("Ruta", back_populates="usuarios", lazy="selectin")
