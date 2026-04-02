"""Master DB engine & session — tenant registry database."""

from __future__ import annotations

from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

_MASTER_DB_PATH = Path("data/master.db")
_MASTER_DB_PATH.parent.mkdir(parents=True, exist_ok=True)

_MASTER_URL = f"sqlite+aiosqlite:///{_MASTER_DB_PATH}"

master_engine = create_async_engine(
    _MASTER_URL,
    echo=False,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

master_session_factory = async_sessionmaker(
    master_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
