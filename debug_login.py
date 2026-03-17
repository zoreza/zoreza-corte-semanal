#!/usr/bin/env python3
"""
Script para debuggear exactamente qué está pasando con el login
"""
import os
import sys

# Configurar credenciales
os.environ["TURSO_DATABASE_URL"] = "libsql://zoreza-corte-zoreza.aws-us-east-1.turso.io"
os.environ["TURSO_AUTH_TOKEN"] = "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicnciLCJpYXQiOjE3NzM0NjI3MTYsImlkIjoiMDE5Y2U5YjEtMzEwMS03ZDk2LTkwMWYtZTY2Mzk2NTk1ZTZjIiwicmlkIjoiOTk2ODZhYjItMTc0ZS00OThkLTliNzEtMGU5NjY4ZTg4NDQ0In0.IwiFkSEa5_KI7zqTt2w2tf2itZF2d2WQScZDgDtj-E09M-TvO7mVIxTol-gutzeGVHBPshsRp6l2mymfCs5lCg"

print("=" * 70)
print("🔍 DEBUG DE LOGIN")
print("=" * 70)
print()

# 1. Verificar que Turso está configurado
print("1️⃣ Verificando configuración de Turso...")
from zoreza.services.turso_service import is_turso_configured, get_turso_config

if is_turso_configured():
    print("   ✅ Turso está configurado")
    url, token = get_turso_config()
    print(f"   URL: {url[:50]}...")
    print(f"   Token: {token[:20]}...")
else:
    print("   ❌ Turso NO está configurado")
    sys.exit(1)

print()

# 2. Probar conexión directa
print("2️⃣ Probando conexión con connect()...")
from zoreza.db.core import connect

try:
    conn = connect()
    print(f"   ✅ Conexión obtenida: {type(conn)}")
    print(f"   Tipo: {conn.__class__.__name__}")
except Exception as e:
    print(f"   ❌ Error al conectar: {e}")
    sys.exit(1)

print()

# 3. Ejecutar query directa
print("3️⃣ Ejecutando SELECT directo en usuarios...")
try:
    cursor = conn.execute("SELECT username, nombre, rol, activo FROM usuarios")
    rows = cursor.fetchall()
    
    print(f"   ✅ Query ejecutada, {len(rows)} resultados")
    
    if rows:
        print()
        print("   Usuarios encontrados:")
        for row in rows:
            print(f"   - Username: {row[0]}")
            print(f"     Nombre: {row[1]}")
            print(f"     Rol: {row[2]}")
            print(f"     Activo: {row[3]}")
            print()
    else:
        print("   ⚠️  No se encontraron usuarios")
        
except Exception as e:
    print(f"   ❌ Error en query: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# 4. Probar fetchone (como lo usa authenticate)
print("4️⃣ Probando fetchone() como en authenticate()...")
from zoreza.db.queries import fetchone

try:
    user = fetchone("SELECT * FROM usuarios WHERE username=? AND activo=1", ("admin",))
    
    if user:
        print("   ✅ Usuario encontrado con fetchone()")
        print(f"   Username: {user.get('username')}")
        print(f"   Nombre: {user.get('nombre')}")
        print(f"   Rol: {user.get('rol')}")
        print(f"   Activo: {user.get('activo')}")
        print(f"   Password hash: {user.get('password_hash', '')[:20]}...")
    else:
        print("   ❌ Usuario NO encontrado con fetchone()")
        print()
        print("   🔍 Intentando sin filtro de activo...")
        user2 = fetchone("SELECT * FROM usuarios WHERE username=?", ("admin",))
        if user2:
            print(f"   ⚠️  Usuario existe pero activo={user2.get('activo')}")
        else:
            print("   ❌ Usuario 'admin' no existe en absoluto")
        
except Exception as e:
    print(f"   ❌ Error en fetchone: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# 5. Probar authenticate completo
print("5️⃣ Probando authenticate() completo...")
from zoreza.services.auth import authenticate

try:
    user, error_code = authenticate("admin", "admin123")
    
    if user:
        print("   ✅ Authenticate exitoso")
        print(f"   Usuario: {user.get('username')}")
        print(f"   Rol: {user.get('rol')}")
    else:
        print(f"   ❌ Authenticate falló")
        print(f"   Código de error: {error_code}")
        
        if error_code == "USER_NOT_FOUND":
            print("   → El usuario no existe o está inactivo")
        elif error_code == "INVALID_PASSWORD":
            print("   → La contraseña es incorrecta")
        elif error_code == "DB_ERROR":
            print("   → Error de conexión con la BD")
        
except Exception as e:
    print(f"   ❌ Error en authenticate: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()
print("=" * 70)
print("✅ Debug completado")
print("=" * 70)

# Made with Bob
