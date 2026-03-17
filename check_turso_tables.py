#!/usr/bin/env python3
"""
Script para verificar qué tablas existen en Turso y su contenido
"""
import os
import sys
import requests

def convert_url(url: str) -> str:
    """Convierte URL de libsql:// a https://"""
    if url.startswith("libsql://"):
        return url.replace("libsql://", "https://")
    elif url.startswith("http://") or url.startswith("https://"):
        return url
    else:
        return f"https://{url}"

def execute_query(http_url: str, token: str, sql: str):
    """Ejecuta una query en Turso."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    request_data = {
        "requests": [
            {
                "type": "execute",
                "stmt": {"sql": sql}
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
    
    print("=" * 70)
    print("🔍 VERIFICACIÓN DE TABLAS EN TURSO")
    print("=" * 70)
    print()
    print(f"🔧 Conectando a: {http_url[:50]}...")
    print()
    
    # 1. Listar todas las tablas
    print("📋 Listando tablas en la base de datos...")
    print("-" * 70)
    
    try:
        response = execute_query(
            http_url,
            turso_token,
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        
        if response.status_code == 200:
            result = response.json()
            if "results" in result and len(result["results"]) > 0:
                first_result = result["results"][0]
                if first_result.get("type") == "ok":
                    response_data = first_result.get("response", {})
                    result_data = response_data.get("result", {})
                    rows = result_data.get("rows", [])
                    
                    if rows:
                        print(f"✅ Encontradas {len(rows)} tablas:")
                        for row in rows:
                            table_name = row[0].get('value', 'unknown')
                            print(f"   - {table_name}")
                    else:
                        print("⚠️  No hay tablas en la base de datos")
                        print()
                        print("❌ LA BASE DE DATOS ESTÁ VACÍA")
                        print()
                        print("Esto explica por qué no encuentra el usuario admin.")
                        print("Necesitas inicializar la base de datos con el schema.")
                        return False
                else:
                    print(f"❌ Error: {first_result.get('error', {}).get('message', 'Error desconocido')}")
                    return False
        else:
            print(f"❌ Error HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error al listar tablas: {e}")
        return False
    
    print()
    print("-" * 70)
    print()
    
    # 2. Si existe la tabla usuarios, contar registros
    print("👥 Verificando tabla 'usuarios'...")
    
    try:
        response = execute_query(
            http_url,
            turso_token,
            "SELECT COUNT(*) as total FROM usuarios"
        )
        
        if response.status_code == 200:
            result = response.json()
            if "results" in result and len(result["results"]) > 0:
                first_result = result["results"][0]
                if first_result.get("type") == "ok":
                    response_data = first_result.get("response", {})
                    result_data = response_data.get("result", {})
                    rows = result_data.get("rows", [])
                    
                    if rows:
                        total = rows[0][0].get('value', '0')
                        print(f"✅ Total de usuarios: {total}")
                        
                        if int(total) == 0:
                            print()
                            print("⚠️  La tabla 'usuarios' existe pero está VACÍA")
                            print("   Necesitas crear el usuario admin")
                    else:
                        print("⚠️  No se pudo contar usuarios")
                else:
                    error_msg = first_result.get('error', {}).get('message', 'Error desconocido')
                    if "no such table" in error_msg:
                        print("❌ La tabla 'usuarios' NO EXISTE")
                        print()
                        print("Necesitas inicializar el schema de la base de datos")
                    else:
                        print(f"❌ Error: {error_msg}")
                    return False
    except Exception as e:
        print(f"❌ Error al verificar usuarios: {e}")
        return False
    
    print()
    print("=" * 70)
    return True

if __name__ == "__main__":
    success = main()
    
    if not success:
        print()
        print("💡 SOLUCIÓN:")
        print()
        print("1. Inicializar el schema en Turso:")
        print("   python -c \"from zoreza.db.core import init_db; init_db(seed=True)\"")
        print()
        print("2. O ejecutar el script de inicialización:")
        print("   python zoreza/init_db.py")
        print()
        sys.exit(1)
    else:
        print("✅ Base de datos verificada correctamente")
        sys.exit(0)

# Made with Bob
