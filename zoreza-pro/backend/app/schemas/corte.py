"""Corte & CorteDetalle schemas."""

from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field


# ── Corte (header) ──────────────────────────────────────────────────
class CorteCreate(BaseModel):
    cliente_id: UUID
    fecha_corte: date


class CorteOut(BaseModel):
    uuid: UUID
    cliente_id: UUID
    cliente_nombre: str | None = None
    week_start: date
    week_end: date
    fecha_corte: date | None
    comision_pct_usada: float
    neto_cliente: float
    pago_cliente: float
    ganancia_dueno: float
    estado: str
    created_by: UUID | None
    operador_nombre: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class CorteSummary(BaseModel):
    """Lightweight listing item."""

    uuid: UUID
    cliente_nombre: str | None = None
    week_start: date
    week_end: date
    estado: str
    neto_cliente: float
    pago_cliente: float
    ganancia_dueno: float

    model_config = {"from_attributes": True}


# ── CorteDetalle ────────────────────────────────────────────────────
class DetalleCapturadaPayload(BaseModel):
    maquina_id: UUID
    score_tarjeta: float = Field(..., ge=0)
    efectivo_total: float = Field(..., ge=0)
    fondo: float = Field(..., ge=0)

    contador_entrada_actual: int | None = None
    contador_salida_actual: int | None = None

    causa_irregularidad_id: UUID | None = None
    nota_irregularidad: str | None = None

    evento_contador_id: UUID | None = None
    nota_evento_contador: str | None = None


class DetalleOmitidaPayload(BaseModel):
    maquina_id: UUID
    motivo_omision_id: UUID
    nota_omision: str | None = None


class DetalleOut(BaseModel):
    uuid: UUID
    corte_id: UUID
    maquina_id: UUID
    maquina_codigo: str | None = None
    estado_maquina: str

    score_tarjeta: float | None = None
    efectivo_total: float | None = None
    fondo: float | None = None
    recaudable: float | None = None
    diferencia_score: float | None = None

    contador_entrada_actual: int | None = None
    contador_salida_actual: int | None = None
    contador_entrada_prev: int | None = None
    contador_salida_prev: int | None = None
    delta_entrada: int | None = None
    delta_salida: int | None = None
    monto_estimado_contadores: float | None = None

    causa_irregularidad_id: UUID | None = None
    causa_irregularidad_nombre: str | None = None
    nota_irregularidad: str | None = None

    evento_contador_id: UUID | None = None
    evento_contador_nombre: str | None = None
    nota_evento_contador: str | None = None

    motivo_omision_id: UUID | None = None
    motivo_omision_nombre: str | None = None
    nota_omision: str | None = None

    model_config = {"from_attributes": True}


class CorteCloseRequest(BaseModel):
    """Sent when the operator wants to close a corte."""

    pass  # Body can be empty; corte_id comes from path


class CorteEditRequest(BaseModel):
    """Supervisor/Admin editing a closed corte."""

    reason: str = Field(..., min_length=10, max_length=500)
