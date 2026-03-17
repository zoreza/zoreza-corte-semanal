#!/usr/bin/env python3
"""
Script de administración directa de Turso.
Permite ver y modificar usuarios directamente en la base de datos.
"""

import os
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

from zoreza.services.turso_service import get_turso_config, create_turso_client, test_turso_connection
from zoreza.services.passwords import hash_password, verify_password


def print_header(title):
    """Imprime un encabezado formateado."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60 + "\n")


def list_users(client):
    """Lista todos los usuarios en la BD."""
    print_header("USUARIOS EN LA BASE DE DATOS")
    
    try:
        cursor = client.execute("SELECT id, username, nombre, rol, activo FROM usuarios ORDER BY id")
        users = cursor.fetchall()
        
        if not users:
            print("❌ No hay usuarios en la base de datos")
            return
        
        print(f"{'ID':<5} {'Username':<15} {'Nombre':<20} {'Rol':<12} {'Activo':<8}")
        print("-" * 60)
        
        for user in users:
            user_id = user[0]
            username = user[1]
            nombre = user[2]
            rol = user[3]
            activo = "✅ Sí" if user[4] == 1 else "❌ No"
            
            print(f"{user_id:<5} {username:<15} {nombre:<20} {rol:<12} {activo:<8}")
        
        print(f"\nTotal: {len(users)} usuarios")
        
    except Exception as e:
        print(f"❌ Error al listar usuarios: {e}")


def reset_admin_password(client, new_password="admin123"):
    """Resetea la contraseña del usuario admin."""
    print_header("RESETEAR CONTRASEÑA DE ADMIN")
    
    try:
        # Generar nuevo hash
        password_hash = hash_password(new_password)
        
        # Actualizar en BD
        client.execute(
            "UPDATE usuarios SET password_hash = ? WHERE username = 'admin'",
            (password_hash,)
        )
        client.commit()
        
        print(f"✅ Contraseña de 'admin' reseteada a: {new_password}")
        print(f"🔐 Hash generado: {password_hash[:30]}...")
        
        # Verificar
        cursor = client.execute("SELECT password_hash FROM usuarios WHERE username = 'admin'")
        result = cursor.fetchone()
        
        if result:
            stored_hash = result[0]
            if verify_password(new_password, stored_hash):
                print("✅ Verificación exitosa: La contraseña funciona correctamente")
            else:
                print("⚠️ Advertencia: La verificación falló")
        
    except Exception as e:
        print(f"❌ Error al resetear contraseña: {e}")


def create_admin_user(client):
    """Crea un usuario admin si no existe."""
    print_header("CREAR USUARIO ADMIN")
    
    try:
        # Verificar si ya existe
        cursor = client.execute("SELECT id FROM usuarios WHERE username = 'admin'")
        existing = cursor.fetchone()
        
        if existing:
            print("⚠️ El usuario 'admin' ya existe")
            print("   Usa la opción 2 para resetear su contraseña")
            return
        
        # Crear usuario
        password_hash = hash_password("admin123")
        from datetime import datetime
        now = datetime.now().isoformat()
        
        client.execute(
            """INSERT INTO usuarios 
               (username, password_hash, nombre, rol, activo, created_at, updated_at, created_by, updated_by)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            ("admin", password_hash, "Administrador", "ADMIN", 1, now, now, None, None)
        )
        client.commit()
        
        print("✅ Usuario 'admin' creado exitosamente")
        print("   Username: admin")
        print("   Password: admin123")
        
    except Exception as e:
        print(f"❌ Error al crear usuario: {e}")


def view_user_details(client, username):
    """Muestra detalles completos de un usuario."""
    print_header(f"DETALLES DEL USUARIO: {username}")
    
    try:
        cursor = client.execute(
            "SELECT * FROM usuarios WHERE username = ?",
            (username,)
        )
        user = cursor.fetchone()
        
        if not user:
            print(f"❌ Usuario '{username}' no encontrado")
            return
        
        # Obtener nombres de columnas
        columns = cursor._columns if hasattr(cursor, '_columns') else [
            'id', 'username', 'password_hash', 'nombre', 'rol', 'activo',
            'created_at', 'updated_at', 'created_by', 'updated_by'
        ]
        
        for i, col in enumerate(columns):
            value = user[i]
            if col == 'password_hash':
                value = f"{value[:30]}..." if value else "None"
            print(f"{col:<15}: {value}")
        
    except Exception as e:
        print(f"❌ Error al ver detalles: {e}")


def execute_custom_query(client):
    """Permite ejecutar una query SQL personalizada."""
    print_header("EJECUTAR QUERY PERSONALIZADA")
    
    print("Ingresa tu query SQL (o 'cancel' para cancelar):")
    print("Ejemplo: SELECT * FROM usuarios WHERE rol = 'ADMIN'")
    print()
    
    query = input("SQL> ").strip()
    
    if query.lower() == 'cancel':
        print("Cancelado")
        return
    
    try:
        cursor = client.execute(query)
        
        # Si es SELECT, mostrar resultados
        if query.upper().startswith('SELECT'):
            results = cursor.fetchall()
            
            if not results:
                print("✅ Query ejecutada. Sin resultados.")
                return
            
            print(f"\n✅ {len(results)} resultados:")
            print("-" * 60)
            
            for row in results:
                print(row)
        else:
            # Para INSERT, UPDATE, DELETE
            client.commit()
            print("✅ Query ejecutada exitosamente")
        
    except Exception as e:
        print(f"❌ Error al ejecutar query: {e}")


def main():
    """Función principal del script."""
    print_header("TURSO ADMIN - Herramienta de Administración")
    
    # Verificar configuración
    print("🔍 Verificando configuración de Turso...")
    url, token = get_turso_config()
    
    if not url or not token:
        print("❌ Error: No se encontró configuración de Turso")
        print("\nAsegúrate de tener configurado:")
        print("  - TURSO_DATABASE_URL en variables de entorno o .streamlit/secrets.toml")
        print("  - TURSO_AUTH_TOKEN en variables de entorno o .streamlit/secrets.toml")
        return
    
    print(f"✅ URL: {url}")
    print(f"✅ Token: {token[:20]}...")
    
    # Probar conexión
    print("\n🔌 Probando conexión...")
    success, message = test_turso_connection(url, token)
    print(message)
    
    if not success:
        print("\n❌ No se pudo conectar a Turso. Verifica tu configuración.")
        return
    
    # Crear cliente
    print("\n📡 Conectando a Turso...")
    try:
        client = create_turso_client(url, token)
        print("✅ Conectado exitosamente")
    except Exception as e:
        print(f"❌ Error al crear cliente: {e}")
        return
    
    # Menú principal
    while True:
        print("\n" + "=" * 60)
        print("MENÚ PRINCIPAL")
        print("=" * 60)
        print("1. Listar todos los usuarios")
        print("2. Resetear contraseña de admin (a 'admin123')")
        print("3. Crear usuario admin (si no existe)")
        print("4. Ver detalles de un usuario")
        print("5. Ejecutar query SQL personalizada")
        print("0. Salir")
        print()
        
        choice = input("Selecciona una opción: ").strip()
        
        if choice == "1":
            list_users(client)
        
        elif choice == "2":
            reset_admin_password(client)
        
        elif choice == "3":
            create_admin_user(client)
        
        elif choice == "4":
            username = input("Ingresa el username: ").strip()
            if username:
                view_user_details(client, username)
        
        elif choice == "5":
            execute_custom_query(client)
        
        elif choice == "0":
            print("\n👋 ¡Hasta luego!")
            break
        
        else:
            print("❌ Opción inválida")
    
    # Cerrar conexión
    try:
        client.close()
    except:
        pass


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interrumpido por el usuario. ¡Hasta luego!")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()

# Made with Bob
