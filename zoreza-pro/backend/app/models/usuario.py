"""Usuario model — users of the system."""

from __future__ import annotations

from sqlalchemy import Boolean, String, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Usuario(Base):
    __tablename__ = "usuarios"
    __table_args__ = (
        CheckConstraint("rol IN ('ADMIN','SUPERVISOR','OPERADOR')", name="ck_usuarios_rol"),
    )

    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    telefono: Mapped[str] = mapped_column(String(30), nullable=False, default="")
    email: Mapped[str] = mapped_column(String(200), nullable=False, default="")
    rol: Mapped[str] = mapped_column(String(20), nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")

    # Relationships
    rutas = relationship("UsuarioRuta", back_populates="usuario", lazy="selectin")

    def is_supervisor(self) -> bool:
        return self.rol in ("ADMIN", "SUPERVISOR")
