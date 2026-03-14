"""
Servicio para gestionar conexión a Turso (SQLite en la nube).
Permite usar BD local o remota según configuración.
"""

import os
from typing import Any, Optional
from pathlib import Path

# Intentar importar libsql, pero no fallar si no está disponible
try:
    import libsql_experimental as libsql
    TURSO_AVAILABLE = True
except ImportError:
    TURSO_AVAILABLE = False
    libsql = None


def is_turso_configured() -> bool:
    """Verifica si Turso está configurado."""
    url = os.getenv("TURSO_DATABASE_URL")
    token = os.getenv("TURSO_AUTH_TOKEN")
    return bool(url and token and TURSO_AVAILABLE)


def get_turso_config() -> dict[str, str]:
    """Obtiene la configuración de Turso desde variables de entorno."""
    return {
        "url": os.getenv("TURSO_DATABASE_URL", ""),
        "auth_token": os.getenv("TURSO_AUTH_TOKEN", "")
    }


def set_turso_config(url: str, auth_token: str) -> None:
    """Establece la configuración de Turso en variables de entorno."""
    os.environ["TURSO_DATABASE_URL"] = url
    os.environ["TURSO_AUTH_TOKEN"] = auth_token


def test_turso_connection(url: str, auth_token: str) -> tuple[bool, str]:
    """
    Prueba la conexión a Turso.
    
    Returns:
        tuple[bool, str]: (éxito, mensaje)
    """
    if not TURSO_AVAILABLE:
        return False, "La librería libsql-experimental-python no está instalada. Ejecuta: pip install libsql-experimental-python"
    
    if not url or not auth_token:
        return False, "URL y Auth Token son requeridos"
    
    try:
        # Conectar usando libsql-experimental (más estable para Streamlit)
        conn = libsql.connect(
            database=url,
            auth_token=auth_token
        )
        
        # Intentar una consulta simple
        cursor = conn.cursor()
        cursor.execute("SELECT 1 as test")
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return True, "✅ Conexión exitosa a Turso"
        else:
            return False, "❌ No se pudo ejecutar consulta de prueba"
            
    except Exception as e:
        return False, f"❌ Error de conexión: {str(e)}"


def create_turso_client():
    """Crea una conexión a Turso con la configuración actual."""
    if not TURSO_AVAILABLE:
        raise ImportError("libsql-experimental-python no está instalado")
    
    config = get_turso_config()
    if not config["url"] or not config["auth_token"]:
        raise ValueError("Turso no está configurado")
    
    # Conectar usando libsql-experimental
    return libsql.connect(
        database=config["url"],
        auth_token=config["auth_token"]
    )


def get_db_status() -> dict[str, Any]:
    """
    Obtiene el estado actual de la base de datos.
    
    Returns:
        dict con: type (local/turso), configured (bool), available (bool), message (str)
    """
    if is_turso_configured():
        return {
            "type": "turso",
            "configured": True,
            "available": TURSO_AVAILABLE,
            "message": "🌐 Usando Turso (Base de datos en la nube)"
        }
    else:
        local_db = os.getenv("ZOREZA_DB_PATH", "./data/zoreza.db")
        exists = Path(local_db).exists()
        return {
            "type": "local",
            "configured": False,
            "available": True,
            "message": f"💾 Usando SQLite local: {local_db}" + (" (existe)" if exists else " (se creará)")
        }


def migrate_local_to_turso(local_db_path: str) -> tuple[bool, str]:
    """
    Migra una base de datos SQLite local a Turso.
    
    Args:
        local_db_path: Ruta al archivo SQLite local
        
    Returns:
        tuple[bool, str]: (éxito, mensaje)
    """
    if not TURSO_AVAILABLE:
        return False, "libsql-client no está instalado"
    
    if not is_turso_configured():
        return False, "Turso no está configurado"
    
    if not Path(local_db_path).exists():
        return False, f"Archivo local no existe: {local_db_path}"
    
    try:
        import sqlite3
        
        # Leer BD local
        local_conn = sqlite3.connect(local_db_path)
        local_conn.row_factory = sqlite3.Row
        
        # Conectar a Turso
        turso_conn = create_turso_client()
        turso_cursor = turso_conn.cursor()
        
        # Obtener todas las tablas
        tables = local_conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        ).fetchall()
        
        migrated_tables = 0
        migrated_rows = 0
        
        for table_row in tables:
            table_name = table_row[0]
            
            # Obtener estructura de la tabla
            create_stmt = local_conn.execute(
                f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}'"
            ).fetchone()[0]
            
            # Crear tabla en Turso
            try:
                turso_cursor.execute(create_stmt)
                turso_conn.commit()
            except:
                pass  # La tabla puede ya existir
            
            # Copiar datos
            rows = local_conn.execute(f"SELECT * FROM {table_name}").fetchall()
            
            for row in rows:
                columns = list(row.keys())
                values = [row[col] for col in columns]
                placeholders = ",".join(["?" for _ in columns])
                
                insert_sql = f"INSERT OR REPLACE INTO {table_name} ({','.join(columns)}) VALUES ({placeholders})"
                turso_cursor.execute(insert_sql, values)
                migrated_rows += 1
            
            turso_conn.commit()
            migrated_tables += 1
        
        turso_conn.close()
        
        local_conn.close()
        
        return True, f"✅ Migración exitosa: {migrated_tables} tablas, {migrated_rows} registros"
        
    except Exception as e:
        return False, f"❌ Error durante migración: {str(e)}"

# Made with Bob
