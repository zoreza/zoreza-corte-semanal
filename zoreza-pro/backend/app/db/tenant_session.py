"""Dynamic per-tenant DB session management.

Each tenant gets its own SQLite file at data/tenants/{slug}.db.
Engine instances are cached and reused across requests.
"""

from __future__ import annotations

import asyncio
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.db.base import Base

_TENANTS_DIR = Path("data/tenants")
_TENANTS_DIR.mkdir(parents=True, exist_ok=True)

# Cache: slug → (engine, session_factory)
_tenant_engines: dict[str, tuple] = {}
_lock = asyncio.Lock()


def _get_tenant_db_url(slug: str) -> str:
    return f"sqlite+aiosqlite:///{_TENANTS_DIR / slug}.db"


async def get_tenant_session_factory(slug: str) -> async_sessionmaker[AsyncSession]:
    """Return (or create) session factory for a tenant."""
    if slug in _tenant_engines:
        return _tenant_engines[slug][1]

    async with _lock:
        # Double-check after acquiring lock
        if slug in _tenant_engines:
            return _tenant_engines[slug][1]

        url = _get_tenant_db_url(slug)
        engine = create_async_engine(
            url,
            echo=False,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        _tenant_engines[slug] = (engine, factory)
        return factory


async def create_tenant_tables(slug: str) -> None:
    """Create all tenant tables in a new tenant DB."""
    factory = await get_tenant_session_factory(slug)
    engine = _tenant_engines[slug][0]
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def dispose_tenant_engine(slug: str) -> None:
    """Dispose engine when tenant is deactivated."""
    entry = _tenant_engines.pop(slug, None)
    if entry:
        await entry[0].dispose()


async def dispose_all_tenant_engines() -> None:
    """Cleanup on shutdown."""
    for slug in list(_tenant_engines.keys()):
        await dispose_tenant_engine(slug)
