"""Corte model — weekly settlement header."""

from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import CheckConstraint, Date, DateTime, Float, ForeignKey, String, UniqueConstraint
from app.db.base import UUIDType
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Corte(Base):
    __tablename__ = "cortes"
    __table_args__ = (
        UniqueConstraint("cliente_id", "week_start", name="uq_corte_cliente_week"),
        CheckConstraint("estado IN ('BORRADOR','CERRADO')", name="ck_cortes_estado"),
    )

    cliente_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType(), ForeignKey("clientes.uuid"), nullable=False
    )
    week_start: Mapped[date] = mapped_column(Date, nullable=False)
    week_end: Mapped[date] = mapped_column(Date, nullable=False)
    fecha_corte: Mapped[date | None] = mapped_column(Date, nullable=True)

    comision_pct_usada: Mapped[float] = mapped_column(Float, default=0.0)
    neto_cliente: Mapped[float] = mapped_column(Float, default=0.0)
    pago_cliente: Mapped[float] = mapped_column(Float, default=0.0)
    ganancia_dueno: Mapped[float] = mapped_column(Float, default=0.0)

    estado: Mapped[str] = mapped_column(String(20), default="BORRADOR", server_default="BORRADOR")
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUIDType(), ForeignKey("usuarios.uuid"), nullable=True
    )

    # Relationships
    cliente = relationship("Cliente", lazy="selectin")
    operador = relationship("Usuario", foreign_keys=[created_by], lazy="selectin")
    detalles = relationship(
        "CorteDetalle", back_populates="corte", lazy="selectin", cascade="all, delete-orphan"
    )
