"""Config model — key/value global settings."""

from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, String, Text
from app.db.base import UUIDType
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Config(Base):
    __tablename__ = "config"

    key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    updated_by: Mapped[uuid.UUID | None] = mapped_column(
        UUIDType(), ForeignKey("usuarios.uuid"), nullable=True
    )
