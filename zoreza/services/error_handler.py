"""
Manejador centralizado de errores para el sistema Zoreza.
Proporciona funciones para capturar, registrar y mostrar errores de forma consistente.
"""
import logging
import traceback
from typing import Callable, Any
from functools import wraps
import streamlit as st
from zoreza.services.exceptions import (
    ZorezaException,
    DatabaseError,
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    BusinessRuleError,
)

# Configurar logger
logger = logging.getLogger("zoreza")
logger.setLevel(logging.INFO)

# Handler para archivo
file_handler = logging.FileHandler("data/zoreza.log")
file_handler.setLevel(logging.INFO)
file_formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def handle_error(error: Exception, context: str = "") -> None:
    """
    Maneja un error de forma centralizada.
    
    Args:
        error: La excepción capturada
        context: Contexto adicional sobre dónde ocurrió el error
    """
    error_msg = str(error)
    
    if isinstance(error, ZorezaException):
        # Errores conocidos del sistema
        logger.warning(f"{context}: {error_msg}", extra={"details": error.details})
        
        if isinstance(error, ValidationError):
            st.error(f"❌ Error de validación: {error_msg}")
        elif isinstance(error, AuthenticationError):
            st.error(f"🔒 Error de autenticación: {error_msg}")
        elif isinstance(error, AuthorizationError):
            st.error(f"⛔ No tienes permisos: {error_msg}")
        elif isinstance(error, BusinessRuleError):
            st.warning(f"⚠️ Regla de negocio: {error_msg}")
        elif isinstance(error, DatabaseError):
            st.error(f"💾 Error de base de datos: {error_msg}")
            logger.error(f"Database error in {context}", exc_info=True)
        else:
            st.error(f"❌ Error: {error_msg}")
    else:
        # Errores inesperados
        logger.error(f"Unexpected error in {context}: {error_msg}", exc_info=True)
        st.error(f"❌ Error inesperado: {error_msg}")
        
        # En desarrollo, mostrar traceback
        if st.session_state.get("debug_mode", False):
            st.code(traceback.format_exc())


def safe_execute(func: Callable, context: str = "", *args, **kwargs) -> Any:
    """
    Ejecuta una función de forma segura, capturando y manejando errores.
    
    Args:
        func: Función a ejecutar
        context: Contexto para logging
        *args, **kwargs: Argumentos para la función
        
    Returns:
        El resultado de la función o None si hay error
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        handle_error(e, context or func.__name__)
        return None


def with_error_handling(context: str = ""):
    """
    Decorador para agregar manejo de errores a funciones.
    
    Args:
        context: Contexto descriptivo de la operación
        
    Example:
        @with_error_handling("crear usuario")
        def create_user(username, password):
            # código que puede fallar
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                handle_error(e, context or func.__name__)
                return None
        return wrapper
    return decorator


def log_operation(operation: str, user_id: int | None = None, details: dict | None = None):
    """
    Registra una operación importante en el log.
    
    Args:
        operation: Descripción de la operación
        user_id: ID del usuario que realizó la operación
        details: Detalles adicionales
    """
    log_data: dict[str, Any] = {"operation": operation}
    if user_id:
        log_data["user_id"] = user_id
    if details:
        log_data.update(details)
    
    logger.info(f"Operation: {operation}", extra=log_data)


def show_success(message: str):
    """Muestra un mensaje de éxito consistente."""
    st.success(f"✅ {message}")
    logger.info(f"Success: {message}")


def show_warning(message: str):
    """Muestra una advertencia consistente."""
    st.warning(f"⚠️ {message}")
    logger.warning(f"Warning: {message}")


def show_info(message: str):
    """Muestra un mensaje informativo consistente."""
    st.info(f"ℹ️ {message}")

# Made with Bob
