from dataclasses import dataclass
from typing import Optional, List
from .calculations import calc_machine

@dataclass
class ValidationError:
    field: str
    message: str

def validate_capturada(
    *,
    score_tarjeta: float | None,
    efectivo_total: float | None,
    fondo: float | None,
    contador_entrada_actual: int | None,
    contador_salida_actual: int | None,
    contador_entrada_prev: int | None,
    contador_salida_prev: int | None,
    tolerancia_pesos: float,
    causa_irregularidad_id: int | None,
    nota_irregularidad: str | None,
    irregularidad_requiere_nota: bool,
    evento_contador_id: int | None,
    nota_evento_contador: str | None,
) -> tuple[list[ValidationError], dict]:
    errs: List[ValidationError] = []
    required = {
        "score_tarjeta": score_tarjeta,
        "efectivo_total": efectivo_total,
        "fondo": fondo,
        "contador_entrada_actual": contador_entrada_actual,
        "contador_salida_actual": contador_salida_actual,
    }
    for k, v in required.items():
        if v is None:
            errs.append(ValidationError(k, "Campo obligatorio."))

    if errs:
        return errs, {}

    calc = calc_machine(
        score_tarjeta=float(score_tarjeta),
        efectivo_total=float(efectivo_total),
        fondo=float(fondo),
        contador_entrada_actual=int(contador_entrada_actual),
        contador_salida_actual=int(contador_salida_actual),
        contador_entrada_prev=contador_entrada_prev,
        contador_salida_prev=contador_salida_prev,
    )

    if calc.recaudable < 0:
        errs.append(ValidationError("fondo", "Recaudable < 0. Corrige efectivo_total o fondo."))

    if abs(calc.diferencia_score) > float(tolerancia_pesos):
        if causa_irregularidad_id is None:
            errs.append(ValidationError("causa_irregularidad_id", "Requerida por diferencia fuera de tolerancia."))
        if irregularidad_requiere_nota and not (nota_irregularidad or "").strip():
            errs.append(ValidationError("nota_irregularidad", "Nota obligatoria para esta causa."))

    # Contadores: si actual < previo => evento + nota obligatoria
    if contador_entrada_prev is not None and contador_salida_prev is not None:
        if int(contador_entrada_actual) < int(contador_entrada_prev) or int(contador_salida_actual) < int(contador_salida_prev):
            if evento_contador_id is None:
                errs.append(ValidationError("evento_contador_id", "Requerido: contador actual menor que previo."))
            if not (nota_evento_contador or "").strip():
                errs.append(ValidationError("nota_evento_contador", "Nota obligatoria: contador actual menor que previo."))

    return errs, {
        "recaudable": calc.recaudable,
        "diferencia_score": calc.diferencia_score,
        "delta_entrada": calc.delta_entrada,
        "delta_salida": calc.delta_salida,
        "monto_estimado_contadores": calc.monto_estimado_contadores,
    }

def validate_omitida(
    *,
    motivo_omision_id: int | None,
    nota_omision: str | None,
    requiere_nota: bool
) -> list[ValidationError]:
    errs: List[ValidationError] = []
    if motivo_omision_id is None:
        errs.append(ValidationError("motivo_omision_id", "Motivo de omisión obligatorio."))
    if requiere_nota and not (nota_omision or "").strip():
        errs.append(ValidationError("nota_omision", "Nota obligatoria para este motivo."))
    return errs

def can_close_corte(detalles: list[dict]) -> list[str]:
    if not detalles:
        return ["No hay máquinas en el corte."]
    capturadas = [d for d in detalles if d["estado_maquina"] == "CAPTURADA"]
    omitidas = [d for d in detalles if d["estado_maquina"] == "OMITIDA"]
    msgs: list[str] = []
    if len(capturadas) < 1:
        msgs.append("Debe existir al menos 1 máquina CAPTURADA para cerrar.")
    for d in capturadas:
        if d.get("recaudable") is None:
            msgs.append("Hay máquinas CAPTURADAS incompletas.")
            break
    for d in omitidas:
        if d.get("motivo_omision_id") is None:
            msgs.append("Hay máquinas OMITIDAS sin motivo.")
            break
    return msgs
