"""Dashboard / reporting service."""

from __future__ import annotations

from datetime import date

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.corte import Corte
from app.models.corte_detalle import CorteDetalle
from app.models.gasto import Gasto
from app.schemas.dashboard import DashboardSummary


async def get_dashboard_summary(
    db: AsyncSession,
    fecha_inicio: date | None = None,
    fecha_fin: date | None = None,
) -> DashboardSummary:
    # Cortes
    stmt = select(
        func.count(Corte.uuid).label("total"),
        func.count(Corte.uuid).filter(Corte.estado == "CERRADO").label("cerrados"),
        func.coalesce(func.sum(Corte.neto_cliente).filter(Corte.estado == "CERRADO"), 0).label(
            "neto"
        ),
        func.coalesce(func.sum(Corte.pago_cliente).filter(Corte.estado == "CERRADO"), 0).label(
            "pago"
        ),
        func.coalesce(
            func.sum(Corte.ganancia_dueno).filter(Corte.estado == "CERRADO"), 0
        ).label("ganancia"),
    )
    if fecha_inicio:
        stmt = stmt.where(Corte.week_start >= fecha_inicio)
    if fecha_fin:
        stmt = stmt.where(Corte.week_end <= fecha_fin)
    row = (await db.execute(stmt)).one()

    # Gastos
    g_stmt = select(func.coalesce(func.sum(Gasto.monto), 0))
    if fecha_inicio:
        g_stmt = g_stmt.where(Gasto.fecha >= fecha_inicio)
    if fecha_fin:
        g_stmt = g_stmt.where(Gasto.fecha <= fecha_fin)
    total_gastos = float((await db.execute(g_stmt)).scalar() or 0)

    neto = float(row.neto)
    ganancia = float(row.ganancia)
    cerrados = int(row.cerrados)

    return DashboardSummary(
        total_cortes=int(row.total),
        cortes_cerrados=cerrados,
        total_neto=neto,
        total_pago_cliente=float(row.pago),
        total_ganancia_dueno=ganancia,
        total_gastos=total_gastos,
        ganancia_neta=ganancia - total_gastos,
        promedio_neto=round(neto / cerrados, 2) if cerrados else 0,
    )
