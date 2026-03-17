"""
Connection pooling para Turso.
Mantiene conexiones abiertas para reducir latencia.
"""
from typing import Optional
import threading
from contextlib import contextmanager

# Pool global de conexiones
_connection_pool = threading.local()


def get_pooled_connection():
    """
    Obtiene una conexión del pool (o crea una nueva si no existe).
    La conexión se mantiene abierta durante toda la sesión de Streamlit.
    """
    if not hasattr(_connection_pool, 'connection') or _connection_pool.connection is None:
        from zoreza.db.core import connect
        _connection_pool.connection = connect()
    
    return _connection_pool.connection


def close_pooled_connection():
    """Cierra la conexión del pool si existe."""
    if hasattr(_connection_pool, 'connection') and _connection_pool.connection is not None:
        try:
            _connection_pool.connection.close()
        except:
            pass
        _connection_pool.connection = None


@contextmanager
def get_connection():
    """
    Context manager para obtener una conexión del pool.
    La conexión NO se cierra al salir del contexto (se reutiliza).
    """
    conn = get_pooled_connection()
    try:
        yield conn
    except Exception as e:
        # Si hay error, cerrar la conexión para forzar reconexión
        close_pooled_connection()
        raise e


def reset_pool():
    """Resetea el pool de conexiones (útil para testing)."""
    close_pooled_connection()

# Made with Bob
