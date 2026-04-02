"""FastAPI application factory — multi-tenant."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import router as v1_router
from app.api.v1.endpoints.superadmin import router as superadmin_router
from app.core.config import get_settings
from app.core.tenant_middleware import TenantMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown hooks."""
    # Create master DB tables on startup
    from app.db.master_session import master_engine
    from app.db.master_base import MasterBase
    from app.models.tenant import Tenant, SuperAdmin  # noqa: F401 — register models
    from app.models.app_release import AppRelease  # noqa: F401

    async with master_engine.begin() as conn:
        await conn.run_sync(MasterBase.metadata.create_all)

    # Seed default super-admin if none exists
    from app.db.master_session import master_session_factory
    from app.core.security import hash_password
    from sqlalchemy import select

    async with master_session_factory() as db:
        result = await db.execute(select(SuperAdmin).limit(1))
        if result.scalar_one_or_none() is None:
            db.add(SuperAdmin(
                username="zoreza",
                password_hash=hash_password("ZorezaLabs2026!"),
                nombre="Zoreza Labs Admin",
            ))
            await db.commit()

    # Migrate existing single-tenant DB as the first tenant if needed
    await _migrate_existing_db()

    yield

    # On shutdown: dispose engines
    from app.db.tenant_session import dispose_all_tenant_engines
    from app.db.master_session import master_engine as me

    await dispose_all_tenant_engines()
    await me.dispose()


async def _migrate_existing_db() -> None:
    """If data/zoreza_pro.db exists and no tenants in master, import it as 'demo'."""
    from pathlib import Path
    import shutil
    from sqlalchemy import select
    from app.db.master_session import master_session_factory
    from app.models.tenant import Tenant

    old_db = Path("data/zoreza_pro.db")
    if not old_db.exists():
        return

    async with master_session_factory() as db:
        result = await db.execute(select(Tenant).limit(1))
        if result.scalar_one_or_none() is not None:
            return  # Already have tenants, skip migration

    # Copy existing DB as first tenant
    tenants_dir = Path("data/tenants")
    tenants_dir.mkdir(parents=True, exist_ok=True)
    dest = tenants_dir / "demo.db"
    if not dest.exists():
        shutil.copy2(old_db, dest)

    # Register in master
    async with master_session_factory() as db:
        db.add(Tenant(
            slug="demo",
            nombre="Demo (migrado)",
            notas="Migrado automáticamente desde la instalación single-tenant.",
        ))
        await db.commit()


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # CORS — allow frontend origins
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Tenant resolution middleware (must be added after CORS)
    app.add_middleware(TenantMiddleware)

    # Tenant API: /{slug}/api/v1/...
    app.include_router(v1_router, prefix="/{tenant}/api/v1")

    # Super-admin API: /zoreza-admin/api/...
    app.include_router(superadmin_router, prefix="/zoreza-admin/api", tags=["Super Admin"])

    @app.get("/health")
    async def health():
        return {"status": "ok", "app": settings.app_name}

    return app


app = create_app()
