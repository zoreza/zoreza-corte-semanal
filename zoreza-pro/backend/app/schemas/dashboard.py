"""Dashboard / reporting schemas."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel


class DashboardSummary(BaseModel):
    total_cortes: int
    cortes_cerrados: int
    total_neto: float
    total_pago_cliente: float
    total_ganancia_dueno: float
    total_gastos: float
    ganancia_neta: float
    promedio_neto: float


class RevenueTrend(BaseModel):
    fecha: date
    num_cortes: int
    total_neto: float
    total_ganancia: float


class ClientPerformance(BaseModel):
    cliente_nombre: str
    total_cortes: int
    total_neto: float
    promedio: float


class IrregularityReport(BaseModel):
    causa: str
    count: int
    maquinas_afectadas: int
