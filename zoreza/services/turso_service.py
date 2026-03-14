"""
Servicio para gestionar conexión a Turso (SQLite en la nube).
Permite usar BD local o remota según configuración.
Usa API HTTP directa para evitar problemas con WebSocket.
"""

import os
import json
import sqlite3
from typing import Any, Optional
from pathlib import Path

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    requests = None


def is_turso_configured() -> bool:
    """Verifica si Turso está configurado."""
    url = os.getenv("TURSO_DATABASE_URL")
    token = os.getenv("TURSO_AUTH_TOKEN")
    return bool(url and token and REQUESTS_AVAILABLE)


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


def _convert_turso_url_to_http(url: str) -> str:
    """
    Convierte URL de Turso a formato HTTP para API.
    libsql://xxx.turso.io -> https://xxx.turso.io
    """
    if url.startswith("libsql://"):
        return url.replace("libsql://", "https://")
    elif url.startswith("http://") or url.startswith("https://"):
        return url
    else:
        return f"https://{url}"


def test_turso_connection(url: str, auth_token: str) -> tuple[bool, str]:
    """
    Prueba la conexión a Turso usando API HTTP.
    
    Returns:
        tuple[bool, str]: (éxito, mensaje)
    """
    if not REQUESTS_AVAILABLE:
        return False, "La librería requests no está instalada. Ejecuta: pip install requests"
    
    if not url or not auth_token:
        return False, "URL y token son requeridos"
    
    try:
        # Convertir URL a formato HTTP
        http_url = _convert_turso_url_to_http(url)
        
        # Probar con una query simple
        response = requests.post(
            f"{http_url}/v2/pipeline",
            headers={
                "Authorization": f"Bearer {auth_token}",
                "Content-Type": "application/json"
            },
            json={
                "requests": [
                    {"type": "execute", "stmt": {"sql": "SELECT 1"}}
                ]
            },
            timeout=10
        )
        
        if response.status_code == 200:
            return True, "✅ Conexión exitosa a Turso"
        else:
            error_msg = f"Error {response.status_code}"
            try:
                error_data = response.json()
                if "error" in error_data:
                    error_msg = f"{error_msg}: {error_data['error']}"
            except:
                pass
            return False, f"❌ {error_msg}"
            
    except requests.exceptions.Timeout:
        return False, "❌ Timeout: La conexión tardó demasiado"
    except requests.exceptions.ConnectionError:
        return False, "❌ Error de conexión: Verifica la URL"
    except Exception as e:
        return False, f"❌ Error: {str(e)}"


def create_turso_client(url: str, auth_token: str) -> Any:
    """
    Crea un cliente HTTP para Turso.
    Retorna un objeto con método execute() para queries.
    """
    if not REQUESTS_AVAILABLE:
        raise ImportError("requests no está instalado")
    
    http_url = _convert_turso_url_to_http(url)
    
    class TursoHTTPClient:
        def __init__(self, base_url: str, token: str):
            self.base_url = base_url
            self.token = token
            self.headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
        
        def execute(self, sql: str, params: tuple = ()) -> Any:
            """Ejecuta una query SQL."""
            response = requests.post(
                f"{self.base_url}/v2/pipeline",
                headers=self.headers,
                json={
                    "requests": [
                        {
                            "type": "execute",
                            "stmt": {
                                "sql": sql,
                                "args": list(params) if params else []
                            }
                        }
                    ]
                },
                timeout=30
            )
            
            if response.status_code != 200:
                raise Exception(f"Turso error {response.status_code}: {response.text}")
            
            return response.json()
        
        def fetchall(self, sql: str, params: tuple = ()) -> list:
            """Ejecuta query y retorna todas las filas."""
            result = self.execute(sql, params)
            
            # Extraer resultados del formato de respuesta de Turso
            if "results" in result and len(result["results"]) > 0:
                query_result = result["results"][0]["response"]["result"]
                if "rows" in query_result:
                    return query_result["rows"]
            
            return []
        
        def fetchone(self, sql: str, params: tuple = ()) -> Optional[tuple]:
            """Ejecuta query y retorna una fila."""
            rows = self.fetchall(sql, params)
            return rows[0] if rows else None
        
        def commit(self):
            """No-op para compatibilidad con sqlite3."""
            pass
        
        def close(self):
            """No-op para compatibilidad con sqlite3."""
            pass
    
    return TursoHTTPClient(http_url, auth_token)


def get_db_status() -> dict[str, Any]:
    """
    Retorna el estado actual de la base de datos.
    
    Returns:
        dict con: type (local/turso), configured (bool), url (str), details (dict)
    """
    if is_turso_configured():
        config = get_turso_config()
        return {
            "type": "turso",
            "configured": True,
            "url": config["url"],
            "details": {
                "provider": "Turso (SQLite en la nube)",
                "connection": "HTTP API",
                "persistent": True
            }
        }
    else:
        return {
            "type": "local",
            "configured": False,
            "url": "data/zoreza.db",
            "details": {
                "provider": "SQLite Local",
                "connection": "Archivo local",
                "persistent": False,
                "warning": "Los datos se perderán al hacer reboot en Streamlit Cloud"
            }
        }


def migrate_local_to_turso(local_db_path: str, turso_url: str, turso_token: str) -> tuple[bool, str, dict]:
    """
    Migra datos de SQLite local a Turso.
    
    Returns:
        tuple[bool, str, dict]: (éxito, mensaje, estadísticas)
    """
    stats = {
        "tables": 0,
        "rows": 0,
        "errors": []
    }
    
    try:
        # Verificar que existe la BD local
        if not Path(local_db_path).exists():
            return False, f"❌ No se encontró la base de datos local: {local_db_path}", stats
        
        # Conectar a BD local
        local_conn = sqlite3.connect(local_db_path)
        local_cursor = local_conn.cursor()
        
        # Crear cliente Turso
        turso_client = create_turso_client(turso_url, turso_token)
        
        # Obtener lista de tablas
        local_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        tables = [row[0] for row in local_cursor.fetchall()]
        
        stats["tables"] = len(tables)
        
        # Migrar cada tabla
        for table in tables:
            try:
                # Obtener estructura de la tabla
                local_cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table}'")
                create_sql = local_cursor.fetchone()[0]
                
                # Crear tabla en Turso (ignorar si ya existe)
                try:
                    turso_client.execute(create_sql)
                except:
                    pass  # Tabla ya existe
                
                # Copiar datos
                local_cursor.execute(f"SELECT * FROM {table}")
                rows = local_cursor.fetchall()
                
                if rows:
                    # Obtener nombres de columnas
                    local_cursor.execute(f"PRAGMA table_info({table})")
                    columns = [col[1] for col in local_cursor.fetchall()]
                    placeholders = ",".join(["?" for _ in columns])
                    
                    # Insertar filas
                    for row in rows:
                        try:
                            insert_sql = f"INSERT OR REPLACE INTO {table} VALUES ({placeholders})"
                            turso_client.execute(insert_sql, row)
                            stats["rows"] += 1
                        except Exception as e:
                            stats["errors"].append(f"Error en {table}: {str(e)}")
                
            except Exception as e:
                stats["errors"].append(f"Error migrando tabla {table}: {str(e)}")
        
        local_conn.close()
        
        if stats["errors"]:
            return True, f"⚠️ Migración completada con {len(stats['errors'])} errores", stats
        else:
            return True, f"✅ Migración exitosa: {stats['tables']} tablas, {stats['rows']} filas", stats
            
    except Exception as e:
        stats["errors"].append(str(e))
        return False, f"❌ Error en migración: {str(e)}", stats

# Made with Bob
