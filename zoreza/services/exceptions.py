"""
Excepciones personalizadas para el sistema Zoreza.
Permite manejo de errores más específico y mensajes claros.
"""

class ZorezaException(Exception):
    """Excepción base para todas las excepciones del sistema."""
    def __init__(self, message: str, details: dict | None = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class DatabaseError(ZorezaException):
    """Error relacionado con operaciones de base de datos."""
    pass


class ValidationError(ZorezaException):
    """Error de validación de datos de entrada."""
    pass


class AuthenticationError(ZorezaException):
    """Error de autenticación de usuario."""
    pass


class AuthorizationError(ZorezaException):
    """Error de autorización/permisos."""
    pass


class BusinessRuleError(ZorezaException):
    """Error de regla de negocio."""
    pass


class CorteAlreadyClosedError(BusinessRuleError):
    """El corte ya está cerrado y no puede modificarse."""
    pass


class DuplicateCorteError(BusinessRuleError):
    """Ya existe un corte para este cliente en esta semana."""
    pass


class InvalidStateTransitionError(BusinessRuleError):
    """Transición de estado inválida."""
    pass


class DataNotFoundError(ZorezaException):
    """Datos solicitados no encontrados."""
    pass


class ExportError(ZorezaException):
    """Error al exportar datos."""
    pass


class BackupError(ZorezaException):
    """Error al realizar backup."""
    pass

# Made with Bob
