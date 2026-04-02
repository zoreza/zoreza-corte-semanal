"""SQLAlchemy declarative Base with common columns."""

from __future__ import annotations

import uuid as _uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, String, TypeDecorator, CHAR
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class UUIDType(TypeDecorator):
    """Platform-independent UUID type.

    Uses CHAR(32) on SQLite and native UUID on PostgreSQL.
    """

    impl = CHAR(32)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            if isinstance(value, _uuid.UUID):
                return value.hex
            return _uuid.UUID(value).hex
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            return _uuid.UUID(value) if not isinstance(value, _uuid.UUID) else value
        return value


class Base(DeclarativeBase):
    """Base class for all ORM models.

    Every table gets:
      - uuid (PK)
      - sync fields (sync_status, sync_version, device_id)
      - timestamps (created_at, updated_at)
    """

    __abstract__ = True

    uuid: Mapped[_uuid.UUID] = mapped_column(
        UUIDType(),
        primary_key=True,
        default=_uuid.uuid4,
    )

    sync_status: Mapped[str] = mapped_column(
        String(20), default="synced"
    )
    sync_version: Mapped[int] = mapped_column(default=0)
    device_id: Mapped[str | None] = mapped_column(String(100), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
