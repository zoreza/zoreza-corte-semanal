"""Cortes endpoints — the core business workflow."""

from datetime import date
from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.core.deps import CurrentUser, DbSession, SupervisorUser
from app.schemas.corte import (
    CorteCreate,
    CorteEditRequest,
    CorteOut,
    CorteSummary,
    DetalleCapturadaPayload,
    DetalleOmitidaPayload,
    DetalleOut,
)
from app.services.corte_service import (
    close_corte,
    get_audit_log,
    get_corte,
    get_corte_detalles,
    get_or_create_corte,
    list_cortes,
    reopen_corte,
    save_detalle_capturada,
    save_detalle_omitida,
)

router = APIRouter()


# ── List / get ──────────────────────────────────────────────────────
@router.get("", response_model=list[CorteSummary])
async def list_settlements(
    db: DbSession,
    user: CurrentUser,
    cliente_id: UUID | None = None,
    estado: str | None = None,
    limit: int = 100,
    offset: int = 0,
):
    cortes = await list_cortes(db, cliente_id=cliente_id, estado=estado, limit=limit, offset=offset)
    return [
        CorteSummary(
            uuid=c.uuid,
            cliente_nombre=c.cliente.nombre if c.cliente else None,
            week_start=c.week_start,
            week_end=c.week_end,
            estado=c.estado,
            neto_cliente=c.neto_cliente,
            pago_cliente=c.pago_cliente,
            ganancia_dueno=c.ganancia_dueno,
        )
        for c in cortes
    ]


@router.get("/{corte_id}", response_model=CorteOut)
async def get_settlement(corte_id: UUID, db: DbSession, user: CurrentUser):
    c = await get_corte(db, corte_id)
    if c is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Corte no encontrado")
    return CorteOut(
        uuid=c.uuid,
        cliente_id=c.cliente_id,
        cliente_nombre=c.cliente.nombre if c.cliente else None,
        week_start=c.week_start,
        week_end=c.week_end,
        fecha_corte=c.fecha_corte,
        comision_pct_usada=c.comision_pct_usada,
        neto_cliente=c.neto_cliente,
        pago_cliente=c.pago_cliente,
        ganancia_dueno=c.ganancia_dueno,
        estado=c.estado,
        created_by=c.created_by,
        operador_nombre=c.operador.nombre if c.operador else None,
        created_at=c.created_at,
    )


@router.get("/{corte_id}/detalles", response_model=list[DetalleOut])
async def get_settlement_details(corte_id: UUID, db: DbSession, user: CurrentUser):
    detalles = await get_corte_detalles(db, corte_id)
    return [
        DetalleOut(
            uuid=d.uuid,
            corte_id=d.corte_id,
            maquina_id=d.maquina_id,
            maquina_codigo=d.maquina.codigo if d.maquina else None,
            estado_maquina=d.estado_maquina,
            score_tarjeta=d.score_tarjeta,
            efectivo_total=d.efectivo_total,
            fondo=d.fondo,
            recaudable=d.recaudable,
            diferencia_score=d.diferencia_score,
            contador_entrada_actual=d.contador_entrada_actual,
            contador_salida_actual=d.contador_salida_actual,
            contador_entrada_prev=d.contador_entrada_prev,
            contador_salida_prev=d.contador_salida_prev,
            delta_entrada=d.delta_entrada,
            delta_salida=d.delta_salida,
            monto_estimado_contadores=d.monto_estimado_contadores,
            causa_irregularidad_id=d.causa_irregularidad_id,
            causa_irregularidad_nombre=(
                d.causa_irregularidad.nombre if d.causa_irregularidad else None
            ),
            nota_irregularidad=d.nota_irregularidad,
            evento_contador_id=d.evento_contador_id,
            evento_contador_nombre=(
                d.evento_contador.nombre if d.evento_contador else None
            ),
            nota_evento_contador=d.nota_evento_contador,
            motivo_omision_id=d.motivo_omision_id,
            motivo_omision_nombre=d.motivo_omision.nombre if d.motivo_omision else None,
            nota_omision=d.nota_omision,
        )
        for d in detalles
    ]


# ── Create / mutate ────────────────────────────────────────────────
@router.post("", response_model=CorteOut, status_code=201)
async def create_settlement(body: CorteCreate, db: DbSession, user: CurrentUser):
    c = await get_or_create_corte(db, body.cliente_id, body.fecha_corte, user)
    return CorteOut(
        uuid=c.uuid,
        cliente_id=c.cliente_id,
        cliente_nombre=c.cliente.nombre if c.cliente else None,
        week_start=c.week_start,
        week_end=c.week_end,
        fecha_corte=c.fecha_corte,
        comision_pct_usada=c.comision_pct_usada,
        neto_cliente=c.neto_cliente,
        pago_cliente=c.pago_cliente,
        ganancia_dueno=c.ganancia_dueno,
        estado=c.estado,
        created_by=c.created_by,
        operador_nombre=c.operador.nombre if c.operador else None,
        created_at=c.created_at,
    )


@router.post("/{corte_id}/detalle/capturada", response_model=DetalleOut)
async def save_captured(
    corte_id: UUID, body: DetalleCapturadaPayload, db: DbSession, user: CurrentUser
):
    d = await save_detalle_capturada(db, corte_id, body, user)
    return DetalleOut(
        uuid=d.uuid,
        corte_id=d.corte_id,
        maquina_id=d.maquina_id,
        maquina_codigo=d.maquina.codigo if d.maquina else None,
        estado_maquina=d.estado_maquina,
        score_tarjeta=d.score_tarjeta,
        efectivo_total=d.efectivo_total,
        fondo=d.fondo,
        recaudable=d.recaudable,
        diferencia_score=d.diferencia_score,
        contador_entrada_actual=d.contador_entrada_actual,
        contador_salida_actual=d.contador_salida_actual,
        contador_entrada_prev=d.contador_entrada_prev,
        contador_salida_prev=d.contador_salida_prev,
        delta_entrada=d.delta_entrada,
        delta_salida=d.delta_salida,
        monto_estimado_contadores=d.monto_estimado_contadores,
        causa_irregularidad_id=d.causa_irregularidad_id,
        nota_irregularidad=d.nota_irregularidad,
        evento_contador_id=d.evento_contador_id,
        nota_evento_contador=d.nota_evento_contador,
    )


@router.post("/{corte_id}/detalle/omitida", response_model=DetalleOut)
async def save_omitted(
    corte_id: UUID, body: DetalleOmitidaPayload, db: DbSession, user: CurrentUser
):
    d = await save_detalle_omitida(db, corte_id, body, user)
    return DetalleOut(
        uuid=d.uuid,
        corte_id=d.corte_id,
        maquina_id=d.maquina_id,
        estado_maquina=d.estado_maquina,
        motivo_omision_id=d.motivo_omision_id,
        nota_omision=d.nota_omision,
    )


@router.post("/{corte_id}/close", response_model=CorteOut)
async def close_settlement(corte_id: UUID, db: DbSession, user: CurrentUser):
    c = await close_corte(db, corte_id, user)
    return CorteOut(
        uuid=c.uuid,
        cliente_id=c.cliente_id,
        cliente_nombre=c.cliente.nombre if c.cliente else None,
        week_start=c.week_start,
        week_end=c.week_end,
        fecha_corte=c.fecha_corte,
        comision_pct_usada=c.comision_pct_usada,
        neto_cliente=c.neto_cliente,
        pago_cliente=c.pago_cliente,
        ganancia_dueno=c.ganancia_dueno,
        estado=c.estado,
        created_by=c.created_by,
        operador_nombre=c.operador.nombre if c.operador else None,
        created_at=c.created_at,
    )


@router.post("/{corte_id}/reopen", response_model=CorteOut)
async def reopen_settlement(
    corte_id: UUID, body: CorteEditRequest, db: DbSession, supervisor: SupervisorUser
):
    c = await reopen_corte(db, corte_id, supervisor, body.reason)
    return CorteOut(
        uuid=c.uuid,
        cliente_id=c.cliente_id,
        cliente_nombre=c.cliente.nombre if c.cliente else None,
        week_start=c.week_start,
        week_end=c.week_end,
        fecha_corte=c.fecha_corte,
        comision_pct_usada=c.comision_pct_usada,
        neto_cliente=c.neto_cliente,
        pago_cliente=c.pago_cliente,
        ganancia_dueno=c.ganancia_dueno,
        estado=c.estado,
        created_by=c.created_by,
        operador_nombre=c.operador.nombre if c.operador else None,
        created_at=c.created_at,
    )


@router.get("/{corte_id}/audit-log")
async def get_settlement_audit(corte_id: UUID, db: DbSession, supervisor: SupervisorUser):
    logs = await get_audit_log(db, corte_id)
    return [
        {
            "uuid": log.uuid,
            "action": log.action,
            "reason": log.reason,
            "changes": log.changes,
            "user_nombre": log.user.nombre if log.user else None,
            "created_at": log.created_at,
        }
        for log in logs
    ]
