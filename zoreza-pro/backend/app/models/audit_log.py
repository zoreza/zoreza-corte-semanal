"""AuditLog model — tracks all edits to closed cortes."""

from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, String, Text
from app.db.base import UUIDType
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class AuditLog(Base):
    __tablename__ = "audit_log"

    corte_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType(), ForeignKey("cortes.uuid"), nullable=False
    )
    maquina_id: Mapped[uuid.UUID | None] = mapped_column(
        UUIDType(), ForeignKey("maquinas.uuid"), nullable=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType(), ForeignKey("usuarios.uuid"), nullable=False
    )
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    changes: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON

    user = relationship("Usuario", lazy="selectin")
