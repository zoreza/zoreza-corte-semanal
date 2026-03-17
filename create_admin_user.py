#!/usr/bin/env python3
"""
Script para crear el usuario admin en Turso si no existe
"""
import os
import sys
import requests
import hashlib

def hash_password(password: str) -> str:
    """Genera hash SHA-256 de la contraseña."""
    return hashlib.sha256(password.encode()).hexdigest()

def convert_url(url: str) -> str:
    """Convierte URL de libsql:// a https://"""
    if url.startswith("libsql://"):
        return url.replace("libsql://", "https://")
    elif url.startswith("http://") or url.startswith("https://"):
        return url
    else:
        return f"https://{url}"

def execute_query(http_url: str, token: str, sql: str, params: list = None):
    """Ejecuta una query en Turso."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Preparar argumentos
    args = []
    if params:
        for param in params:
            if isinstance(param, str):
                args.append({"type": "text", "value": param})
            elif isinstance(param, int):
                args.append({"type": "integer", "value": str(param)})
            else:
                args.append({"type": "text", "value": str(param)})
    
    request_data = {
        "requests": [
            {
                "type": "execute",
                "stmt": {
                    "sql": sql,
                    "args": args
                }
            },
            {"type": "close"}
        ]
    }
    
    response = requests.post(
        f"{http_url}/v2/pipeline",
        headers=headers,
        json=request_data,
        timeout=10
    )
    
    return response

def main():
    # Obtener credenciales
    turso_url = os.getenv("TURSO_DATABASE_URL")
    turso_token = os.getenv("TURSO_AUTH_TOKEN")
    
    if not turso_url or not turso_token:
        print("❌ Error: Variables de entorno no encontradas")
        return False
    
    http_url = convert_url(turso_url)
    
    print("=" * 60)
    print("🔐 CREAR USUARIO ADMIN EN TURSO")
    print("=" * 60)
    print()
    print(f"🔧 Conectando a: {http_url[:50]}...")
    print()
    
    # 1. Listar usuarios existentes
    print("📋 Listando usuarios existentes...")
    try:
        response = execute_query(http_url, turso_token, "SELECT username, rol, activo FROM usuarios")
        
        if response.status_code == 200:
            result = response.json()
            if "results" in result and len(result["results"]) > 0:
                first_result = result["results"][0]
                if first_result.get("type") == "ok":
                    response_data = first_result.get("response", {})
                    result_data = response_data.get("result", {})
                    rows = result_data.get("rows", [])
                    columns = result_data.get("columns", [])
                    
                    if rows:
                        print(f"✅ Encontrados {len(rows)} usuarios:")
                        for row in rows:
                            print(f"   - {row[0]} (rol: {row[1]}, activo: {row[2]})")
                    else:
                        print("⚠️  No hay usuarios en la base de datos")
                else:
                    print(f"❌ Error: {first_result.get('error', {}).get('message', 'Error desconocido')}")
        else:
            print(f"❌ Error HTTP {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error al listar usuarios: {e}")
    
    print()
    print("-" * 60)
    print()
    
    # 2. Crear usuario admin
    print("➕ Creando usuario admin...")
    password = "admin123"
    password_hash = hash_password(password)
    
    # Obtener timestamp actual
    from datetime import datetime
    now = datetime.now().isoformat()
    
    sql = """
    INSERT INTO usuarios (username, password_hash, nombre, rol, activo, created_at, updated_at)
    VALUES (?, ?, ?, 'ADMIN', 1, ?, ?)
    """
    
    try:
        response = execute_query(
            http_url,
            turso_token,
            sql,
            ["admin", password_hash, "Administrador", now, now]
        )
        
        if response.status_code == 200:
            result = response.json()
            if "results" in result and len(result["results"]) > 0:
                first_result = result["results"][0]
                
                if first_result.get("type") == "ok":
                    print("✅ Usuario admin creado exitosamente")
                    print()
                    print("📋 Credenciales:")
                    print(f"   Usuario: admin")
                    print(f"   Contraseña: {password}")
                    print()
                    return True
                else:
                    error_msg = first_result.get("error", {}).get("message", "Error desconocido")
                    if "UNIQUE constraint failed" in error_msg:
                        print("⚠️  El usuario 'admin' ya existe")
                        print()
                        print("🔄 Intentando actualizar contraseña...")
                        
                        # Intentar UPDATE
                        update_sql = "UPDATE usuarios SET password_hash = ? WHERE username = 'admin'"
                        update_response = execute_query(
                            http_url,
                            turso_token,
                            update_sql,
                            [password_hash]
                        )
                        
                        if update_response.status_code == 200:
                            print("✅ Contraseña actualizada exitosamente")
                            print()
                            print("📋 Credenciales:")
                            print(f"   Usuario: admin")
                            print(f"   Contraseña: {password}")
                            print()
                            return True
                        else:
                            print(f"❌ Error al actualizar: {update_response.text}")
                            return False
                    else:
                        print(f"❌ Error: {error_msg}")
                        return False
        else:
            print(f"❌ Error HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print()
    success = main()
    print("=" * 60)
    
    if success:
        print("✅ Proceso completado exitosamente")
        print()
        print("Ahora puedes entrar con:")
        print("  Usuario: admin")
        print("  Contraseña: admin123")
        sys.exit(0)
    else:
        print("❌ El proceso falló")
        sys.exit(1)

# Made with Bob
