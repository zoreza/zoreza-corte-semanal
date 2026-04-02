"""Dashboard endpoints."""

from datetime import date

from fastapi import APIRouter

from app.core.deps import AdminUser, DbSession
from app.schemas.dashboard import DashboardSummary
from app.services.dashboard_service import get_dashboard_summary

router = APIRouter()


@router.get("/summary", response_model=DashboardSummary)
async def dashboard_summary(
    db: DbSession,
    _admin: AdminUser,
    fecha_inicio: date | None = None,
    fecha_fin: date | None = None,
):
    return await get_dashboard_summary(db, fecha_inicio, fecha_fin)
