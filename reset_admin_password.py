#!/usr/bin/env python3
"""
Script para resetear la contraseña del usuario admin en Turso
Usa las credenciales de Streamlit Cloud (secrets)
"""
import os
import sys
import requests
import hashlib

def hash_password(password: str) -> str:
    """Genera hash SHA-256 de la contraseña."""
    return hashlib.sha256(password.encode()).hexdigest()

def reset_admin_password():
    """Resetea la contraseña del admin a 'admin123'."""
    
    # Obtener credenciales de variables de entorno (Streamlit Cloud)
    turso_url = os.getenv("TURSO_DATABASE_URL")
    turso_token = os.getenv("TURSO_AUTH_TOKEN")
    
    if not turso_url or not turso_token:
        print("❌ Error: Variables de entorno TURSO_DATABASE_URL y TURSO_AUTH_TOKEN no encontradas")
        print("\nEn Streamlit Cloud, estas variables están en los secrets.")
        print("Para ejecutar localmente, necesitas exportarlas:")
        print('  export TURSO_DATABASE_URL="libsql://..."')
        print('  export TURSO_AUTH_TOKEN="eyJ..."')
        return False
    
    # Preparar nueva contraseña
    new_password = "admin123"
    password_hash = hash_password(new_password)
    
    print(f"🔧 Conectando a Turso...")
    print(f"   URL: {turso_url[:50]}...")
    
    # Preparar query SQL
    sql = "UPDATE usuarios SET password_hash = ? WHERE username = 'admin'"
    
    # Preparar request para Turso API
    headers = {
        "Authorization": f"Bearer {turso_token}",
        "Content-Type": "application/json"
    }
    
    request_data = {
        "requests": [
            {
                "type": "execute",
                "stmt": {
                    "sql": sql,
                    "args": [{"type": "text", "value": password_hash}]
                }
            },
            {"type": "close"}  # IMPORTANTE: Persistir cambios
        ]
    }
    
    try:
        # Ejecutar UPDATE
        print(f"🔄 Actualizando contraseña de 'admin' a '{new_password}'...")
        response = requests.post(
            f"{turso_url}/v2/pipeline",
            headers=headers,
            json=request_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Verificar si hubo error
            if "results" in result and len(result["results"]) > 0:
                first_result = result["results"][0]
                
                if first_result.get("type") == "ok":
                    rows_affected = first_result.get("response", {}).get("result", {}).get("rows_affected", 0)
                    
                    if rows_affected > 0:
                        print(f"✅ Contraseña actualizada exitosamente")
                        print(f"\n📋 Credenciales:")
                        print(f"   Usuario: admin")
                        print(f"   Contraseña: {new_password}")
                        print(f"\n🔐 Hash generado: {password_hash[:20]}...")
                        return True
                    else:
                        print(f"⚠️  No se encontró el usuario 'admin' en la base de datos")
                        return False
                else:
                    error_msg = first_result.get("error", {}).get("message", "Error desconocido")
                    print(f"❌ Error en la query: {error_msg}")
                    return False
            else:
                print(f"❌ Respuesta inesperada de Turso")
                print(f"   Response: {result}")
                return False
        else:
            print(f"❌ Error HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error al conectar con Turso: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🔐 RESET DE CONTRASEÑA - USUARIO ADMIN")
    print("=" * 60)
    print()
    
    success = reset_admin_password()
    
    print()
    print("=" * 60)
    
    if success:
        print("✅ Proceso completado exitosamente")
        print("\nAhora puedes entrar con:")
        print("  Usuario: admin")
        print("  Contraseña: admin123")
        sys.exit(0)
    else:
        print("❌ El proceso falló")
        print("\nRevisa los errores arriba para más detalles")
        sys.exit(1)

# Made with Bob
