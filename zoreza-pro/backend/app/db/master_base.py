"""SQLAlchemy Base for the master (platform) database."""

from __future__ import annotations

import uuid as _uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.db.base import UUIDType


class MasterBase(DeclarativeBase):
    """Base class for master-DB models (tenants, super-admins)."""

    __abstract__ = True

    uuid: Mapped[_uuid.UUID] = mapped_column(
        UUIDType(), primary_key=True, default=_uuid.uuid4
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
