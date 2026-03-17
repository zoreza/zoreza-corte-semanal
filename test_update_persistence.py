#!/usr/bin/env python3
"""
Script para probar si los UPDATEs persisten en Turso
"""
import os
import requests
import hashlib
import time

# Credenciales
turso_url = "libsql://zoreza-corte-zoreza.aws-us-east-1.turso.io"
turso_token = "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicnciLCJpYXQiOjE3NzM0NjI3MTYsImlkIjoiMDE5Y2U5YjEtMzEwMS03ZDk2LTkwMWYtZTY2Mzk2NTk1ZTZjIiwicmlkIjoiOTk2ODZhYjItMTc0ZS00OThkLTliNzEtMGU5NjY4ZTg4NDQ0In0.IwiFkSEa5_KI7zqTt2w2tf2itZF2d2WQScZDgDtj-E09M-TvO7mVIxTol-gutzeGVHBPshsRp6l2mymfCs5lCg"

http_url = turso_url.replace("libsql://", "https://")

def execute_query(sql, params=None):
    """Ejecuta una query en Turso."""
    headers = {
        "Authorization": f"Bearer {turso_token}",
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

print("=" * 70)
print("🧪 TEST DE PERSISTENCIA DE UPDATES EN TURSO")
print("=" * 70)
print()

# 1. Leer password_hash actual
print("1️⃣ Leyendo password_hash actual...")
response = execute_query("SELECT password_hash FROM usuarios WHERE username = 'admin'")

if response.status_code == 200:
    result = response.json()
    if "results" in result and len(result["results"]) > 0:
        rows = result["results"][0]["response"]["result"]["rows"]
        if rows:
            old_hash = rows[0][0]["value"]
            print(f"   Hash actual: {old_hash[:30]}...")
        else:
            print("   ❌ No se encontró el usuario")
            exit(1)
else:
    print(f"   ❌ Error: {response.text}")
    exit(1)

print()

# 2. Generar nuevo hash
print("2️⃣ Generando nuevo hash para 'admin123'...")
new_password = "admin123"
new_hash = hashlib.sha256(new_password.encode()).hexdigest()
print(f"   Nuevo hash: {new_hash[:30]}...")

print()

# 3. Ejecutar UPDATE
print("3️⃣ Ejecutando UPDATE...")
update_response = execute_query(
    "UPDATE usuarios SET password_hash = ? WHERE username = 'admin'",
    [new_hash]
)

if update_response.status_code == 200:
    result = update_response.json()
    print(f"   ✅ UPDATE ejecutado")
    print(f"   Response: {result}")
    
    # Verificar affected_row_count
    if "results" in result and len(result["results"]) > 0:
        affected = result["results"][0]["response"]["result"].get("affected_row_count", 0)
        print(f"   Filas afectadas: {affected}")
else:
    print(f"   ❌ Error: {update_response.text}")
    exit(1)

print()

# 4. Esperar un momento
print("4️⃣ Esperando 2 segundos...")
time.sleep(2)

print()

# 5. Leer password_hash de nuevo
print("5️⃣ Leyendo password_hash después del UPDATE...")
response2 = execute_query("SELECT password_hash FROM usuarios WHERE username = 'admin'")

if response2.status_code == 200:
    result2 = response2.json()
    if "results" in result2 and len(result2["results"]) > 0:
        rows2 = result2["results"][0]["response"]["result"]["rows"]
        if rows2:
            current_hash = rows2[0][0]["value"]
            print(f"   Hash después: {current_hash[:30]}...")
            
            print()
            print("=" * 70)
            
            if current_hash == new_hash:
                print("✅ ¡ÉXITO! El UPDATE persistió correctamente")
                print()
                print("El hash cambió de:")
                print(f"  {old_hash[:30]}...")
                print("a:")
                print(f"  {new_hash[:30]}...")
            else:
                print("❌ FALLO: El UPDATE NO persistió")
                print()
                print("El hash sigue siendo:")
                print(f"  {current_hash[:30]}...")
                print()
                print("Debería ser:")
                print(f"  {new_hash[:30]}...")
                
                if current_hash == old_hash:
                    print()
                    print("⚠️  El hash no cambió en absoluto")
                    print("   Esto confirma que los UPDATEs no persisten")
        else:
            print("   ❌ No se encontró el usuario")
else:
    print(f"   ❌ Error: {response2.text}")

print()
print("=" * 70)

# Made with Bob
