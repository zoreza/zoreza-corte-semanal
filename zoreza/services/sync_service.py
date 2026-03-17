"""
Servicio de sincronización entre SQLite local y Turso.
Maneja fallback automático y cola de operaciones pendientes.
"""

import os
import sqlite3
import json
from pathlib import Path
from typing import Any, Optional
from datetime import datetime

try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False
    st = None


# Estado global de sincronización
_sync_state = {
    "using_fallback": False,
    "pending_operations": [],
    "last_error": None,
    "last_error_time": None
}


def get_sync_state() -> dict:
    """Retorna el estado actual de sincronización."""
    return _sync_state.copy()


def is_using_fallback() -> bool:
    """Verifica si estamos usando fallback local."""
    return _sync_state["using_fallback"]


def has_pending_operations() -> bool:
    """Verifica si hay operaciones pendientes de sincronizar."""
    return len(_sync_state["pending_operations"]) > 0


def get_pending_count() -> int:
    """Retorna el número de operaciones pendientes."""
    return len(_sync_state["pending_operations"])


def mark_turso_failed(error: str) -> None:
    """Marca que Turso falló y activa el modo fallback."""
    _sync_state["using_fallback"] = True
    _sync_state["last_error"] = str(error)
    _sync_state["last_error_time"] = datetime.now().isoformat()
    
    # Guardar estado en archivo para persistencia
    _save_sync_state()


def mark_turso_recovered() -> None:
    """Marca que Turso se recuperó."""
    _sync_state["using_fallback"] = False
    _sync_state["last_error"] = None
    _sync_state["last_error_time"] = None
    
    # Guardar estado
    _save_sync_state()


def add_pending_operation(operation_type: str, sql: str, params: tuple, timestamp: str | None = None) -> None:
    """Agrega una operación a la cola de pendientes."""
    if timestamp is None:
        timestamp = datetime.now().isoformat()
    
    operation = {
        "type": operation_type,
        "sql": sql,
        "params": list(params),  # Convertir tupla a lista para JSON
        "timestamp": timestamp
    }
    
    _sync_state["pending_operations"].append(operation)
    
    # Guardar estado
    _save_sync_state()


def clear_pending_operations() -> None:
    """Limpia todas las operaciones pendientes."""
    _sync_state["pending_operations"] = []
    _save_sync_state()


def _get_sync_state_path() -> str:
    """Retorna la ruta del archivo de estado de sincronización."""
    return os.path.join("data", "sync_state.json")


def _save_sync_state() -> None:
    """Guarda el estado de sincronización en archivo."""
    try:
        path = _get_sync_state_path()
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w') as f:
            json.dump(_sync_state, f, indent=2)
    except Exception as e:
        print(f"⚠️ Error al guardar estado de sincronización: {e}")


def _load_sync_state() -> None:
    """Carga el estado de sincronización desde archivo."""
    try:
        path = _get_sync_state_path()
        if Path(path).exists():
            with open(path, 'r') as f:
                loaded_state = json.load(f)
                _sync_state.update(loaded_state)
    except Exception as e:
        print(f"⚠️ Error al cargar estado de sincronización: {e}")


def sync_pending_operations() -> tuple[bool, str, int]:
    """
    Intenta sincronizar todas las operaciones pendientes con Turso.
    
    Returns:
        tuple[bool, str, int]: (éxito, mensaje, operaciones_sincronizadas)
    """
    if not has_pending_operations():
        return True, "No hay operaciones pendientes", 0
    
    try:
        from zoreza.services.turso_service import create_turso_client, get_turso_config, is_turso_configured
        
        if not is_turso_configured():
            return False, "Turso no está configurado", 0
        
        url, token = get_turso_config()
        turso_client = create_turso_client(url, token)
        
        synced_count = 0
        failed_operations = []
        
        for operation in _sync_state["pending_operations"]:
            try:
                sql = operation["sql"]
                params = tuple(operation["params"])
                
                # Ejecutar operación en Turso
                turso_client.execute(sql, params)
                turso_client.commit()
                synced_count += 1
                
            except Exception as e:
                print(f"⚠️ Error al sincronizar operación: {e}")
                failed_operations.append(operation)
        
        # Actualizar lista de pendientes (solo mantener las que fallaron)
        _sync_state["pending_operations"] = failed_operations
        
        if synced_count > 0:
            mark_turso_recovered()
            _save_sync_state()
            return True, f"✅ {synced_count} operaciones sincronizadas", synced_count
        else:
            return False, "❌ No se pudo sincronizar ninguna operación", 0
            
    except Exception as e:
        return False, f"❌ Error al sincronizar: {str(e)}", 0


# Cargar estado al importar el módulo
_load_sync_state()

# Made with Bob
