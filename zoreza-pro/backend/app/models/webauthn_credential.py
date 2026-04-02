"""WebAuthn credential model — stores passkeys for users (tenant DB)."""

from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, LargeBinary, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, UUIDType


class WebAuthnCredential(Base):
    __tablename__ = "webauthn_credentials"

    user_id: Mapped[str] = mapped_column(
        UUIDType(), ForeignKey("usuarios.uuid", ondelete="CASCADE"), nullable=False
    )
    credential_id: Mapped[bytes] = mapped_column(LargeBinary, nullable=False, unique=True)
    public_key: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    sign_count: Mapped[int] = mapped_column(default=0)
    device_name: Mapped[str] = mapped_column(String(200), default="")
    transports: Mapped[str | None] = mapped_column(Text, nullable=True)
    backed_up: Mapped[bool] = mapped_column(Boolean, default=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
