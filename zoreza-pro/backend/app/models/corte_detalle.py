"""CorteDetalle model — per-machine data for a weekly settlement."""

from __future__ import annotations

import uuid

from sqlalchemy import (
    CheckConstraint,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from app.db.base import UUIDType
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class CorteDetalle(Base):
    __tablename__ = "corte_detalle"
    __table_args__ = (
        UniqueConstraint("corte_id", "maquina_id", name="uq_detalle_corte_maquina"),
        CheckConstraint(
            "estado_maquina IN ('CAPTURADA','OMITIDA')", name="ck_detalle_estado_maquina"
        ),
    )

    corte_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType(), ForeignKey("cortes.uuid", ondelete="CASCADE"), nullable=False
    )
    maquina_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType(), ForeignKey("maquinas.uuid"), nullable=False
    )
    estado_maquina: Mapped[str] = mapped_column(String(20), default="CAPTURADA")

    # ── Money fields (CAPTURADA) ─────────────────────────────────────
    score_tarjeta: Mapped[float | None] = mapped_column(Float, nullable=True)
    efectivo_total: Mapped[float | None] = mapped_column(Float, nullable=True)
    fondo: Mapped[float | None] = mapped_column(Float, nullable=True)
    recaudable: Mapped[float | None] = mapped_column(Float, nullable=True)
    diferencia_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    # ── Counter fields (CAPTURADA) ───────────────────────────────────
    contador_entrada_actual: Mapped[int | None] = mapped_column(Integer, nullable=True)
    contador_salida_actual: Mapped[int | None] = mapped_column(Integer, nullable=True)
    contador_entrada_prev: Mapped[int | None] = mapped_column(Integer, nullable=True)
    contador_salida_prev: Mapped[int | None] = mapped_column(Integer, nullable=True)
    delta_entrada: Mapped[int | None] = mapped_column(Integer, nullable=True)
    delta_salida: Mapped[int | None] = mapped_column(Integer, nullable=True)
    monto_estimado_contadores: Mapped[float | None] = mapped_column(Float, nullable=True)

    # ── Irregularity (CAPTURADA) ─────────────────────────────────────
    causa_irregularidad_id: Mapped[uuid.UUID | None] = mapped_column(
        UUIDType(), ForeignKey("cat_irregularidad.uuid"), nullable=True
    )
    nota_irregularidad: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ── Counter event (CAPTURADA) ────────────────────────────────────
    evento_contador_id: Mapped[uuid.UUID | None] = mapped_column(
        UUIDType(), ForeignKey("cat_evento_contador.uuid"), nullable=True
    )
    nota_evento_contador: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ── Omission (OMITIDA) ──────────────────────────────────────────
    motivo_omision_id: Mapped[uuid.UUID | None] = mapped_column(
        UUIDType(), ForeignKey("cat_omision.uuid"), nullable=True
    )
    nota_omision: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUIDType(), ForeignKey("usuarios.uuid"), nullable=True
    )

    # Relationships
    corte = relationship("Corte", back_populates="detalles")
    maquina = relationship("Maquina", lazy="selectin")
    causa_irregularidad = relationship("CatIrregularidad", lazy="selectin")
    evento_contador = relationship("CatEventoContador", lazy="selectin")
    motivo_omision = relationship("CatOmision", lazy="selectin")
