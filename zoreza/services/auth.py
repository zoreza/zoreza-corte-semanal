from zoreza.db.queries import fetchone
from zoreza.services.passwords import verify_password
from typing import Tuple, Optional

def authenticate(username: str, password: str) -> Tuple[Optional[dict], str]:
    """
    Autentica un usuario.
    
    Returns:
        Tuple[Optional[dict], str]: (usuario_dict o None, mensaje_error)
        
    Mensajes de error posibles:
        - "" (string vacío): Login exitoso
        - "DB_ERROR": Error de conexión con la base de datos
        - "USER_NOT_FOUND": Usuario no existe o está inactivo
        - "INVALID_PASSWORD": Contraseña incorrecta
    """
    try:
        # Intentar buscar el usuario
        user = fetchone("SELECT * FROM usuarios WHERE username=? AND activo=1", (username,))
        
        if not user:
            return None, "USER_NOT_FOUND"
        
        # Verificar contraseña
        if not verify_password(password, user["password_hash"]):
            return None, "INVALID_PASSWORD"
        
        # Login exitoso
        return user, ""
        
    except Exception as e:
        # Error de conexión con la BD
        print(f"❌ Error en authenticate(): {e}")
        return None, "DB_ERROR"
