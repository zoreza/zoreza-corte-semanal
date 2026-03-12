"""
Servicio para edición de cortes cerrados con control de permisos.
"""
from zoreza.services.exceptions import (
    AuthorizationError,
    CorteAlreadyClosedError,
    ValidationError,
    BusinessRuleError
)
from zoreza.db import repo
from zoreza.services.rbac import is_supervisor


def can_edit_closed_corte(user: dict, corte: dict) -> tuple[bool, str]:
    """
    Verifica si un usuario puede editar un corte cerrado.
    
    Args:
        user: Usuario que intenta editar
        corte: Corte a editar
        
    Returns:
        Tupla (puede_editar, razón)
    """
    # Solo ADMIN y SUPERVISOR pueden editar cortes cerrados
    if not is_supervisor(user):
        return False, "Solo administradores y supervisores pueden editar cortes cerrados"
    
    # Verificar que el corte esté cerrado
    if corte["estado"] != "CERRADO":
        return False, "El corte no está cerrado"
    
    return True, ""


def reopen_corte(corte_id: int, user: dict, reason: str) -> None:
    """
    Reabre un corte cerrado para edición.
    
    Args:
        corte_id: ID del corte
        user: Usuario que reabre
        reason: Razón para reabrir
        
    Raises:
        AuthorizationError: Si el usuario no tiene permisos
        ValidationError: Si los datos son inválidos
    """
    # Obtener corte
    corte = repo.get_corte_by_id(corte_id)
    if not corte:
        raise ValidationError(f"Corte {corte_id} no encontrado")
    
    # Verificar permisos
    can_edit, msg = can_edit_closed_corte(user, corte)
    if not can_edit:
        raise AuthorizationError(msg)
    
    # Validar razón
    if not reason or len(reason.strip()) < 10:
        raise ValidationError("Debe proporcionar una razón detallada (mínimo 10 caracteres)")
    
    # Reabrir corte
    repo.reopen_corte(corte_id, user["id"], reason)


def edit_closed_corte_detalle(
    corte_id: int,
    maquina_id: int,
    user: dict,
    reason: str,
    payload: dict
) -> None:
    """
    Edita el detalle de una máquina en un corte cerrado.
    
    Args:
        corte_id: ID del corte
        maquina_id: ID de la máquina
        user: Usuario que edita
        reason: Razón de la edición
        payload: Datos actualizados
        
    Raises:
        AuthorizationError: Si el usuario no tiene permisos
        ValidationError: Si los datos son inválidos
    """
    # Obtener corte
    corte = repo.get_corte_by_id(corte_id)
    if not corte:
        raise ValidationError(f"Corte {corte_id} no encontrado")
    
    # Verificar permisos
    can_edit, msg = can_edit_closed_corte(user, corte)
    if not can_edit:
        raise AuthorizationError(msg)
    
    # Validar razón
    if not reason or len(reason.strip()) < 10:
        raise ValidationError("Debe proporcionar una razón detallada (mínimo 10 caracteres)")
    
    # Registrar edición en log de auditoría
    repo.log_corte_edit(corte_id, maquina_id, user["id"], reason, payload)
    
    # Actualizar detalle
    if payload.get("estado_maquina") == "CAPTURADA":
        repo.save_detalle_capturada(corte_id, maquina_id, user["id"], payload)
    else:
        repo.save_detalle_omitida(
            corte_id,
            maquina_id,
            user["id"],
            payload.get("motivo_omision_id"),
            payload.get("nota_omision")
        )


def recalculate_corte_totals(corte_id: int, user: dict) -> dict:
    """
    Recalcula los totales de un corte después de ediciones.
    
    Args:
        corte_id: ID del corte
        user: Usuario que recalcula
        
    Returns:
        Diccionario con nuevos totales
        
    Raises:
        ValidationError: Si hay error en el cálculo
    """
    # Obtener corte
    corte = repo.get_corte_by_id(corte_id)
    if not corte:
        raise ValidationError(f"Corte {corte_id} no encontrado")
    
    # Verificar permisos
    can_edit, msg = can_edit_closed_corte(user, corte)
    if not can_edit:
        raise AuthorizationError(msg)
    
    # Obtener detalles
    detalles = repo.list_detalle(corte_id)
    
    # Calcular totales
    neto_cliente = 0.0
    for det in detalles:
        if det["estado_maquina"] == "CAPTURADA" and det.get("recaudable"):
            neto_cliente += float(det["recaudable"])
    
    # Calcular reparto
    comision_pct = float(corte["comision_pct_usada"])
    pago_cliente = neto_cliente * comision_pct
    ganancia_dueno = neto_cliente - pago_cliente
    
    # Actualizar corte
    repo.update_corte_totals(corte_id, neto_cliente, pago_cliente, ganancia_dueno)
    
    return {
        "neto_cliente": neto_cliente,
        "pago_cliente": pago_cliente,
        "ganancia_dueno": ganancia_dueno
    }


def get_corte_edit_history(corte_id: int) -> list[dict]:
    """
    Obtiene el historial de ediciones de un corte.
    
    Args:
        corte_id: ID del corte
        
    Returns:
        Lista de ediciones
    """
    return repo.get_corte_edit_log(corte_id)


def validate_corte_edit_permission(user: dict, corte_id: int) -> None:
    """
    Valida que el usuario tenga permisos para editar el corte.
    
    Args:
        user: Usuario
        corte_id: ID del corte
        
    Raises:
        AuthorizationError: Si no tiene permisos
        ValidationError: Si el corte no existe
    """
    corte = repo.get_corte_by_id(corte_id)
    if not corte:
        raise ValidationError(f"Corte {corte_id} no encontrado")
    
    can_edit, msg = can_edit_closed_corte(user, corte)
    if not can_edit:
        raise AuthorizationError(msg)

# Made with Bob
