"""AppRelease model — lives in master DB for platform-wide APK distribution."""

from __future__ import annotations

from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.master_base import MasterBase


class AppRelease(MasterBase):
    __tablename__ = "app_releases"

    version_name: Mapped[str] = mapped_column(String(30), nullable=False)  # e.g. "1.2.0"
    version_code: Mapped[int] = mapped_column(Integer, nullable=False)  # e.g. 3
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, default=0)  # bytes
    release_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_mandatory: Mapped[bool] = mapped_column(Boolean, default=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
