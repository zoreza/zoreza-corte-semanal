"""Corte service — create, record details, close, edit closed."""

from __future__ import annotations

import json
from datetime import date, timedelta
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.corte import Corte
from app.models.corte_detalle import CorteDetalle
from app.models.audit_log import AuditLog
from app.models.cliente import Cliente
from app.models.usuario import Usuario
from app.schemas.corte import (
    DetalleCapturadaPayload,
    DetalleOmitidaPayload,
)


# ── Week bounds ─────────────────────────────────────────────────────
def compute_week_bounds(fecha_corte: date) -> tuple[date, date]:
    """Return (Monday, Sunday) of the ISO week containing fecha_corte."""
    week_start = fecha_corte - timedelta(days=fecha_corte.weekday())  # Monday
    week_end = week_start + timedelta(days=6)  # Sunday
    return week_start, week_end


# ── Create / get draft ──────────────────────────────────────────────
async def get_or_create_corte(
    db: AsyncSession, cliente_id: UUID, fecha_corte: date, actor: Usuario
) -> Corte:
    week_start, week_end = compute_week_bounds(fecha_corte)

    result = await db.execute(
        select(Corte).where(
            Corte.cliente_id == cliente_id,
            Corte.week_start == week_start,
        )
    )
    corte = result.scalar_one_or_none()
    if corte is not None:
        return corte

    # Snapshot client commission
    cliente = await db.get(Cliente, cliente_id)
    if cliente is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Cliente no encontrado")

    corte = Corte(
        cliente_id=cliente_id,
        week_start=week_start,
        week_end=week_end,
        fecha_corte=fecha_corte,
        comision_pct_usada=cliente.comision_pct,
        estado="BORRADOR",
        created_by=actor.uuid,
    )
    db.add(corte)
    await db.commit()
    await db.refresh(corte)
    return corte


# ── Save captured machine detail ────────────────────────────────────
async def save_detalle_capturada(
    db: AsyncSession,
    corte_id: UUID,
    payload: DetalleCapturadaPayload,
    actor: Usuario,
    tolerancia: float = 30.0,
    fondo_sugerido: float = 500.0,
) -> CorteDetalle:
    corte = await _get_corte_or_fail(db, corte_id)
    _assert_borrador(corte)

    # Look up previous counters from last CERRADO corte for this machine
    prev = await _get_prev_counters(db, payload.maquina_id, corte.cliente_id)

    recaudable = payload.efectivo_total - payload.fondo
    diferencia = recaudable - payload.score_tarjeta

    delta_entrada = None
    delta_salida = None
    monto_estimado = None
    if payload.contador_entrada_actual is not None and prev.get("entrada") is not None:
        delta_entrada = payload.contador_entrada_actual - prev["entrada"]
    if payload.contador_salida_actual is not None and prev.get("salida") is not None:
        delta_salida = payload.contador_salida_actual - prev["salida"]
    if delta_entrada is not None and delta_salida is not None:
        monto_estimado = float(delta_entrada - delta_salida)

    # Validation
    if recaudable < 0:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Recaudable no puede ser negativo")
    if abs(diferencia) > tolerancia and payload.causa_irregularidad_id is None:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            f"Diferencia de ${diferencia:.2f} excede tolerancia (${tolerancia:.2f}). Seleccione causa de irregularidad.",
        )

    # Upsert
    result = await db.execute(
        select(CorteDetalle).where(
            CorteDetalle.corte_id == corte_id,
            CorteDetalle.maquina_id == payload.maquina_id,
        )
    )
    detalle = result.scalar_one_or_none()
    if detalle is None:
        detalle = CorteDetalle(corte_id=corte_id, maquina_id=payload.maquina_id)
        db.add(detalle)

    detalle.estado_maquina = "CAPTURADA"
    detalle.score_tarjeta = payload.score_tarjeta
    detalle.efectivo_total = payload.efectivo_total
    detalle.fondo = payload.fondo
    detalle.recaudable = recaudable
    detalle.diferencia_score = diferencia
    detalle.contador_entrada_actual = payload.contador_entrada_actual
    detalle.contador_salida_actual = payload.contador_salida_actual
    detalle.contador_entrada_prev = prev.get("entrada")
    detalle.contador_salida_prev = prev.get("salida")
    detalle.delta_entrada = delta_entrada
    detalle.delta_salida = delta_salida
    detalle.monto_estimado_contadores = monto_estimado
    detalle.causa_irregularidad_id = payload.causa_irregularidad_id
    detalle.nota_irregularidad = payload.nota_irregularidad
    detalle.evento_contador_id = payload.evento_contador_id
    detalle.nota_evento_contador = payload.nota_evento_contador
    # Clear omission fields
    detalle.motivo_omision_id = None
    detalle.nota_omision = None
    detalle.created_by = actor.uuid

    await db.commit()
    await db.refresh(detalle)
    return detalle


# ── Save omitted machine detail ─────────────────────────────────────
async def save_detalle_omitida(
    db: AsyncSession,
    corte_id: UUID,
    payload: DetalleOmitidaPayload,
    actor: Usuario,
) -> CorteDetalle:
    corte = await _get_corte_or_fail(db, corte_id)
    _assert_borrador(corte)

    result = await db.execute(
        select(CorteDetalle).where(
            CorteDetalle.corte_id == corte_id,
            CorteDetalle.maquina_id == payload.maquina_id,
        )
    )
    detalle = result.scalar_one_or_none()
    if detalle is None:
        detalle = CorteDetalle(corte_id=corte_id, maquina_id=payload.maquina_id)
        db.add(detalle)

    detalle.estado_maquina = "OMITIDA"
    detalle.motivo_omision_id = payload.motivo_omision_id
    detalle.nota_omision = payload.nota_omision
    # Clear capture fields
    for field in (
        "score_tarjeta", "efectivo_total", "fondo", "recaudable", "diferencia_score",
        "contador_entrada_actual", "contador_salida_actual", "contador_entrada_prev",
        "contador_salida_prev", "delta_entrada", "delta_salida", "monto_estimado_contadores",
        "causa_irregularidad_id", "nota_irregularidad", "evento_contador_id", "nota_evento_contador",
    ):
        setattr(detalle, field, None)
    detalle.created_by = actor.uuid

    await db.commit()
    await db.refresh(detalle)
    return detalle


# ── Close corte ─────────────────────────────────────────────────────
async def close_corte(db: AsyncSession, corte_id: UUID, actor: Usuario) -> Corte:
    corte = await _get_corte_or_fail(db, corte_id)
    _assert_borrador(corte)

    result = await db.execute(
        select(CorteDetalle).where(CorteDetalle.corte_id == corte_id)
    )
    detalles = list(result.scalars().all())

    # Validation: at least one CAPTURADA
    capturadas = [d for d in detalles if d.estado_maquina == "CAPTURADA"]
    if not capturadas:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "Debe haber al menos una máquina capturada para cerrar el corte.",
        )

    # Calculate totals
    neto_cliente = sum(d.recaudable or 0 for d in capturadas)
    pago_cliente = round(neto_cliente * corte.comision_pct_usada, 2)
    ganancia_dueno = round(neto_cliente - pago_cliente, 2)

    corte.neto_cliente = round(neto_cliente, 2)
    corte.pago_cliente = pago_cliente
    corte.ganancia_dueno = ganancia_dueno
    corte.estado = "CERRADO"

    await db.commit()
    await db.refresh(corte)
    return corte


# ── Reopen corte (SUPERVISOR/ADMIN) ─────────────────────────────────
async def reopen_corte(
    db: AsyncSession, corte_id: UUID, actor: Usuario, reason: str
) -> Corte:
    if not actor.is_supervisor():
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Solo supervisores pueden reabrir cortes")
    corte = await _get_corte_or_fail(db, corte_id)
    if corte.estado != "CERRADO":
        raise HTTPException(status.HTTP_409_CONFLICT, "El corte no está cerrado")

    corte.estado = "BORRADOR"
    db.add(AuditLog(
        corte_id=corte_id,
        user_id=actor.uuid,
        action="reopen",
        reason=reason,
        changes=json.dumps({"estado": "BORRADOR"}),
    ))
    await db.commit()
    await db.refresh(corte)
    return corte


# ── List / get ──────────────────────────────────────────────────────
async def list_cortes(
    db: AsyncSession,
    cliente_id: UUID | None = None,
    estado: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[Corte]:
    stmt = select(Corte).order_by(Corte.week_start.desc())
    if cliente_id:
        stmt = stmt.where(Corte.cliente_id == cliente_id)
    if estado:
        stmt = stmt.where(Corte.estado == estado)
    stmt = stmt.limit(limit).offset(offset)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_corte(db: AsyncSession, corte_id: UUID) -> Corte | None:
    return await db.get(Corte, corte_id)


async def get_corte_detalles(db: AsyncSession, corte_id: UUID) -> list[CorteDetalle]:
    result = await db.execute(
        select(CorteDetalle).where(CorteDetalle.corte_id == corte_id)
    )
    return list(result.scalars().all())


async def get_audit_log(db: AsyncSession, corte_id: UUID) -> list[AuditLog]:
    result = await db.execute(
        select(AuditLog).where(AuditLog.corte_id == corte_id).order_by(AuditLog.created_at.desc())
    )
    return list(result.scalars().all())


# ── Internal helpers ────────────────────────────────────────────────
async def _get_corte_or_fail(db: AsyncSession, corte_id: UUID) -> Corte:
    corte = await db.get(Corte, corte_id)
    if corte is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Corte no encontrado")
    return corte


def _assert_borrador(corte: Corte) -> None:
    if corte.estado != "BORRADOR":
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "El corte está cerrado. Reabra primero.",
        )


async def _get_prev_counters(
    db: AsyncSession, maquina_id: UUID, cliente_id: UUID
) -> dict:
    """Get last CERRADO counters for a machine."""
    stmt = (
        select(CorteDetalle)
        .join(Corte, CorteDetalle.corte_id == Corte.uuid)
        .where(
            CorteDetalle.maquina_id == maquina_id,
            CorteDetalle.estado_maquina == "CAPTURADA",
            Corte.estado == "CERRADO",
            Corte.cliente_id == cliente_id,
        )
        .order_by(Corte.week_start.desc())
        .limit(1)
    )
    result = await db.execute(stmt)
    prev_det = result.scalar_one_or_none()
    if prev_det is None:
        return {}
    return {
        "entrada": prev_det.contador_entrada_actual,
        "salida": prev_det.contador_salida_actual,
    }
