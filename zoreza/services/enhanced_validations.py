"""
Validaciones mejoradas con rangos, tipos y reglas de negocio más estrictas.
"""
from typing import Any
from zoreza.services.exceptions import ValidationError


def validate_positive_number(value: Any, field_name: str, allow_zero: bool = False) -> float:
    """
    Valida que un valor sea un número positivo.
    
    Args:
        value: Valor a validar
        field_name: Nombre del campo para mensajes de error
        allow_zero: Si se permite el valor 0
        
    Returns:
        El valor como float
        
    Raises:
        ValidationError: Si la validación falla
    """
    try:
        num = float(value)
    except (TypeError, ValueError):
        raise ValidationError(f"{field_name} debe ser un número válido")
    
    if allow_zero:
        if num < 0:
            raise ValidationError(f"{field_name} no puede ser negativo")
    else:
        if num <= 0:
            raise ValidationError(f"{field_name} debe ser mayor que 0")
    
    return num


def validate_positive_integer(value: Any, field_name: str, allow_zero: bool = False) -> int:
    """
    Valida que un valor sea un entero positivo.
    
    Args:
        value: Valor a validar
        field_name: Nombre del campo para mensajes de error
        allow_zero: Si se permite el valor 0
        
    Returns:
        El valor como int
        
    Raises:
        ValidationError: Si la validación falla
    """
    try:
        num = int(value)
    except (TypeError, ValueError):
        raise ValidationError(f"{field_name} debe ser un número entero válido")
    
    if allow_zero:
        if num < 0:
            raise ValidationError(f"{field_name} no puede ser negativo")
    else:
        if num <= 0:
            raise ValidationError(f"{field_name} debe ser mayor que 0")
    
    return num


def validate_percentage(value: Any, field_name: str) -> float:
    """
    Valida que un valor sea un porcentaje válido (0-1).
    
    Args:
        value: Valor a validar
        field_name: Nombre del campo
        
    Returns:
        El valor como float
        
    Raises:
        ValidationError: Si la validación falla
    """
    try:
        num = float(value)
    except (TypeError, ValueError):
        raise ValidationError(f"{field_name} debe ser un número válido")
    
    if not 0 <= num <= 1:
        raise ValidationError(f"{field_name} debe estar entre 0 y 1 (0% - 100%)")
    
    return num


def validate_string_not_empty(value: Any, field_name: str, min_length: int = 1, max_length: int | None = None) -> str:
    """
    Valida que una cadena no esté vacía y cumpla con longitud mínima/máxima.
    
    Args:
        value: Valor a validar
        field_name: Nombre del campo
        min_length: Longitud mínima
        max_length: Longitud máxima (opcional)
        
    Returns:
        La cadena limpia
        
    Raises:
        ValidationError: Si la validación falla
    """
    if not isinstance(value, str):
        raise ValidationError(f"{field_name} debe ser texto")
    
    cleaned = value.strip()
    
    if len(cleaned) < min_length:
        raise ValidationError(f"{field_name} debe tener al menos {min_length} caracteres")
    
    if max_length and len(cleaned) > max_length:
        raise ValidationError(f"{field_name} no puede exceder {max_length} caracteres")
    
    return cleaned


def validate_username(username: str) -> str:
    """
    Valida un nombre de usuario.
    
    Args:
        username: Nombre de usuario a validar
        
    Returns:
        Username limpio
        
    Raises:
        ValidationError: Si la validación falla
    """
    cleaned = validate_string_not_empty(username, "Usuario", min_length=3, max_length=50)
    
    # Solo alfanuméricos y guiones bajos
    if not all(c.isalnum() or c == '_' for c in cleaned):
        raise ValidationError("Usuario solo puede contener letras, números y guiones bajos")
    
    return cleaned


def validate_password(password: str, min_length: int = 6) -> str:
    """
    Valida una contraseña.
    
    Args:
        password: Contraseña a validar
        min_length: Longitud mínima
        
    Returns:
        Password validado
        
    Raises:
        ValidationError: Si la validación falla
    """
    if not isinstance(password, str):
        raise ValidationError("Contraseña debe ser texto")
    
    if len(password) < min_length:
        raise ValidationError(f"Contraseña debe tener al menos {min_length} caracteres")
    
    return password


def validate_contador_values(
    entrada_actual: int,
    salida_actual: int,
    entrada_prev: int | None,
    salida_prev: int | None
) -> tuple[bool, str]:
    """
    Valida valores de contadores y detecta si hay evento anormal.
    
    Args:
        entrada_actual: Contador de entrada actual
        salida_actual: Contador de salida actual
        entrada_prev: Contador de entrada previo (puede ser None)
        salida_prev: Contador de salida previo (puede ser None)
        
    Returns:
        Tupla (requiere_evento, mensaje)
    """
    # Validar que entrada >= salida (lógica de negocio)
    if entrada_actual < salida_actual:
        return True, "Contador de entrada no puede ser menor que salida"
    
    # Si hay valores previos, validar
    if entrada_prev is not None and salida_prev is not None:
        # Detectar reset o decremento
        if entrada_actual < entrada_prev:
            return True, "Contador de entrada decrementó (posible reset)"
        
        if salida_actual < salida_prev:
            return True, "Contador de salida decrementó (posible reset)"
        
        # Validar que los deltas sean razonables (opcional)
        delta_entrada = entrada_actual - entrada_prev
        delta_salida = salida_actual - salida_prev
        
        # Si el delta es muy grande, podría ser sospechoso
        if delta_entrada > 100000 or delta_salida > 100000:
            return True, "Delta de contadores excesivamente grande (verificar)"
    
    return False, ""


def validate_money_values(
    score_tarjeta: float,
    efectivo_total: float,
    fondo: float,
    tolerancia: float
) -> tuple[bool, str, float]:
    """
    Valida valores monetarios y calcula diferencias.
    
    Args:
        score_tarjeta: Score de tarjeta
        efectivo_total: Efectivo total
        fondo: Fondo
        tolerancia: Tolerancia en pesos
        
    Returns:
        Tupla (requiere_irregularidad, mensaje, diferencia)
    """
    recaudable = efectivo_total - fondo
    
    if recaudable < 0:
        raise ValidationError(
            f"Recaudable negativo (${recaudable:.2f}). "
            f"Efectivo total (${efectivo_total:.2f}) debe ser mayor que fondo (${fondo:.2f})"
        )
    
    diferencia = recaudable - score_tarjeta
    
    if abs(diferencia) > tolerancia:
        msg = f"Diferencia de ${abs(diferencia):.2f} excede tolerancia de ${tolerancia:.2f}"
        return True, msg, diferencia
    
    return False, "", diferencia


def validate_comision_percentage(comision: float) -> float:
    """
    Valida que el porcentaje de comisión sea razonable.
    
    Args:
        comision: Porcentaje de comisión (0-1)
        
    Returns:
        Comisión validada
        
    Raises:
        ValidationError: Si está fuera de rango razonable
    """
    comision = validate_percentage(comision, "Comisión")
    
    # Validar rango razonable (10% - 90%)
    if comision < 0.10 or comision > 0.90:
        raise ValidationError(
            f"Comisión de {comision*100:.0f}% está fuera del rango razonable (10% - 90%)"
        )
    
    return comision

# Made with Bob
