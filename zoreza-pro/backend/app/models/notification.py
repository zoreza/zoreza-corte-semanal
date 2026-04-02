"""Notification model."""

from __future__ import annotations

import uuid

from sqlalchemy import Boolean, ForeignKey, String, Text
from app.db.base import UUIDType
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Notification(Base):
    __tablename__ = "notifications"

    type: Mapped[str] = mapped_column(String(50), nullable=False)
    priority: Mapped[str] = mapped_column(String(20), default="media")
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)

    corte_id: Mapped[uuid.UUID | None] = mapped_column(
        UUIDType(), ForeignKey("cortes.uuid"), nullable=True
    )
    maquina_id: Mapped[uuid.UUID | None] = mapped_column(
        UUIDType(), ForeignKey("maquinas.uuid"), nullable=True
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUIDType(), ForeignKey("usuarios.uuid"), nullable=True
    )
    read: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
