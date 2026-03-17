from dataclasses import dataclass
from typing import Optional

@dataclass
class MachineCalc:
    recaudable: float
    diferencia_score: float
    delta_entrada: Optional[int]
    delta_salida: Optional[int]
    monto_estimado_contadores: Optional[float]

def calc_machine(
    score_tarjeta: float,
    efectivo_total: float,
    fondo: float,
    contador_entrada_actual: int,
    contador_salida_actual: int,
    contador_entrada_prev: int | None,
    contador_salida_prev: int | None,
) -> MachineCalc:
    recaudable = efectivo_total - fondo
    diferencia_score = recaudable - score_tarjeta

    delta_entrada = None
    delta_salida = None
    monto_estimado = None
    if contador_entrada_prev is not None and contador_salida_prev is not None:
        delta_entrada = contador_entrada_actual - contador_entrada_prev
        delta_salida = contador_salida_actual - contador_salida_prev
        monto_estimado = float(delta_entrada - delta_salida)  # $1 por pulso

    return MachineCalc(
        recaudable=recaudable,
        diferencia_score=diferencia_score,
        delta_entrada=delta_entrada,
        delta_salida=delta_salida,
        monto_estimado_contadores=monto_estimado,
    )

def reparto(neto_cliente: float, comision_pct: float) -> tuple[float, float]:
    pago_cliente = neto_cliente * comision_pct
    ganancia_dueno = neto_cliente - pago_cliente
    return pago_cliente, ganancia_dueno
