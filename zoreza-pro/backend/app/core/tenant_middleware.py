"""Tenant resolution middleware.

Extracts the tenant slug from the URL path and attaches it to request.state.
Routes: /{slug}/api/v1/...  → tenant API
        /zoreza-admin/...    → super-admin panel
        /health              → no tenant needed
"""

from __future__ import annotations

import re

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from sqlalchemy import select
from app.db.master_session import master_session_factory
from app.models.tenant import Tenant

# Paths that don't require tenant resolution
_SKIP_PATTERNS = re.compile(
    r"^/(health|docs|redoc|openapi\.json|zoreza-admin)"
)

# Valid slug: lowercase alphanumeric + hyphens, 2-50 chars
_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9\-]{1,48}[a-z0-9]$")


class TenantMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Skip paths that don't need tenant
        if _SKIP_PATTERNS.match(path):
            request.state.tenant_slug = None
            return await call_next(request)

        # Extract slug from first path segment: /{slug}/api/v1/...
        parts = path.strip("/").split("/", 1)
        slug = parts[0] if parts else ""

        if not slug or not _SLUG_RE.match(slug):
            return JSONResponse(
                status_code=404,
                content={"detail": "Tenant no encontrado"},
            )

        # Validate tenant exists and is active
        async with master_session_factory() as db:
            result = await db.execute(
                select(Tenant).where(Tenant.slug == slug, Tenant.activo == True)
            )
            tenant = result.scalar_one_or_none()

        if tenant is None:
            return JSONResponse(
                status_code=404,
                content={"detail": f"Tenant '{slug}' no encontrado o inactivo"},
            )

        request.state.tenant_slug = slug
        request.state.tenant_uuid = str(tenant.uuid)
        request.state.tenant_nombre = tenant.nombre
        return await call_next(request)
