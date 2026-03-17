#!/usr/bin/env python3
"""
Script de pruebas de persistencia en Turso.
Verifica que los datos se guarden correctamente en la base de datos.
"""

import sys
from pathlib import Path
from datetime import datetime
import time

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

from zoreza.services.turso_service import (
    get_turso_config, 
    create_turso_client, 
    test_turso_connection,
    is_turso_configured
)
from zoreza.services.passwords import hash_password
from zoreza.db.core import connect, get_db_type


class TestResult:
    """Clase para almacenar resultados de pruebas."""
    def __init__(self, name):
        self.name = name
        self.passed = False
        self.message = ""
        self.details = []
    
    def success(self, message=""):
        self.passed = True
        self.message = message
    
    def fail(self, message=""):
        self.passed = False
        self.message = message
    
    def add_detail(self, detail):
        self.details.append(detail)
    
    def print_result(self):
        status = "✅ PASS" if self.passed else "❌ FAIL"
        print(f"\n{status}: {self.name}")
        if self.message:
            print(f"   {self.message}")
        for detail in self.details:
            print(f"   • {detail}")


def print_header(title):
    """Imprime un encabezado formateado."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def test_turso_connection_basic():
    """Prueba 1: Verificar conexión básica a Turso."""
    result = TestResult("Conexión Básica a Turso")
    
    try:
        url, token = get_turso_config()
        
        if not url or not token:
            result.fail("No se encontró configuración de Turso")
            return result
        
        result.add_detail(f"URL: {url}")
        result.add_detail(f"Token: {token[:20]}...")
        
        success, message = test_turso_connection(url, token)
        
        if success:
            result.success("Conexión exitosa")
        else:
            result.fail(f"Conexión falló: {message}")
        
    except Exception as e:
        result.fail(f"Error: {str(e)}")
    
    return result


def test_turso_client_creation():
    """Prueba 2: Verificar creación de cliente Turso."""
    result = TestResult("Creación de Cliente Turso")
    
    try:
        url, token = get_turso_config()
        client = create_turso_client(url, token)
        
        result.add_detail(f"Cliente creado: {type(client).__name__}")
        result.add_detail(f"Tiene método execute: {hasattr(client, 'execute')}")
        result.add_detail(f"Tiene método commit: {hasattr(client, 'commit')}")
        
        result.success("Cliente creado correctamente")
        
    except Exception as e:
        result.fail(f"Error: {str(e)}")
    
    return result


def test_simple_select():
    """Prueba 3: Verificar SELECT simple."""
    result = TestResult("SELECT Simple")
    
    try:
        url, token = get_turso_config()
        client = create_turso_client(url, token)
        
        cursor = client.execute("SELECT 1 as test")
        row = cursor.fetchone()
        
        if row and row[0] == 1:
            result.success("SELECT funciona correctamente")
            result.add_detail(f"Resultado: {row[0]}")
        else:
            result.fail("SELECT no retornó el valor esperado")
        
    except Exception as e:
        result.fail(f"Error: {str(e)}")
    
    return result


def test_select_usuarios():
    """Prueba 4: Verificar SELECT de usuarios."""
    result = TestResult("SELECT Usuarios")
    
    try:
        url, token = get_turso_config()
        client = create_turso_client(url, token)
        
        cursor = client.execute("SELECT COUNT(*) as count FROM usuarios")
        row = cursor.fetchone()
        
        count = row[0] if row else 0
        result.add_detail(f"Usuarios en BD: {count}")
        
        if count > 0:
            cursor2 = client.execute("SELECT username, nombre, rol FROM usuarios LIMIT 3")
            users = cursor2.fetchall()
            for user in users:
                result.add_detail(f"  - {user[0]} ({user[1]}) - {user[2]}")
        
        result.success(f"Encontrados {count} usuarios")
        
    except Exception as e:
        result.fail(f"Error: {str(e)}")
    
    return result


def test_insert_and_verify():
    """Prueba 5: Verificar INSERT y persistencia."""
    result = TestResult("INSERT y Verificación de Persistencia")
    
    test_username = f"test_user_{int(time.time())}"
    
    try:
        url, token = get_turso_config()
        client = create_turso_client(url, token)
        
        # 1. Insertar usuario de prueba
        password_hash = hash_password("test123")
        now = datetime.now().isoformat()
        
        result.add_detail(f"Insertando usuario: {test_username}")
        
        client.execute(
            """INSERT INTO usuarios 
               (username, password_hash, nombre, rol, activo, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (test_username, password_hash, "Usuario de Prueba", "OPERADOR", 1, now, now)
        )
        
        result.add_detail("INSERT ejecutado")
        
        # 2. Commit explícito
        client.commit()
        result.add_detail("COMMIT ejecutado")
        
        # 3. Esperar un momento
        time.sleep(1)
        
        # 4. Crear NUEVO cliente para verificar persistencia
        client2 = create_turso_client(url, token)
        result.add_detail("Nuevo cliente creado para verificación")
        
        # 5. Buscar el usuario insertado
        cursor = client2.execute(
            "SELECT username, nombre, rol FROM usuarios WHERE username = ?",
            (test_username,)
        )
        found_user = cursor.fetchone()
        
        if found_user:
            result.success("✅ Usuario insertado y verificado correctamente")
            result.add_detail(f"Usuario encontrado: {found_user[0]} - {found_user[1]}")
            
            # Limpiar: eliminar usuario de prueba
            client2.execute("DELETE FROM usuarios WHERE username = ?", (test_username,))
            client2.commit()
            result.add_detail("Usuario de prueba eliminado")
        else:
            result.fail("❌ Usuario NO se encontró después del INSERT")
            result.add_detail("El INSERT no persistió en la base de datos")
        
    except Exception as e:
        result.fail(f"Error: {str(e)}")
        import traceback
        result.add_detail(traceback.format_exc())
    
    return result


def test_update_and_verify():
    """Prueba 6: Verificar UPDATE y persistencia."""
    result = TestResult("UPDATE y Verificación de Persistencia")
    
    try:
        url, token = get_turso_config()
        client = create_turso_client(url, token)
        
        # 1. Obtener usuario admin
        cursor = client.execute("SELECT id, nombre FROM usuarios WHERE username = 'admin'")
        admin = cursor.fetchone()
        
        if not admin:
            result.fail("Usuario admin no encontrado")
            return result
        
        admin_id = admin[0]
        original_name = admin[1]
        result.add_detail(f"Usuario admin ID: {admin_id}")
        result.add_detail(f"Nombre original: {original_name}")
        
        # 2. Actualizar nombre
        new_name = f"Admin Test {int(time.time())}"
        result.add_detail(f"Actualizando a: {new_name}")
        
        client.execute(
            "UPDATE usuarios SET nombre = ? WHERE id = ?",
            (new_name, admin_id)
        )
        
        result.add_detail("UPDATE ejecutado")
        
        # 3. Commit explícito
        client.commit()
        result.add_detail("COMMIT ejecutado")
        
        # 4. Esperar un momento
        time.sleep(1)
        
        # 5. Crear NUEVO cliente para verificar
        client2 = create_turso_client(url, token)
        result.add_detail("Nuevo cliente creado para verificación")
        
        # 6. Verificar el cambio
        cursor2 = client2.execute("SELECT nombre FROM usuarios WHERE id = ?", (admin_id,))
        updated_user = cursor2.fetchone()
        
        if updated_user and updated_user[0] == new_name:
            result.success("✅ UPDATE persistió correctamente")
            result.add_detail(f"Nombre actualizado: {updated_user[0]}")
            
            # Restaurar nombre original
            client2.execute(
                "UPDATE usuarios SET nombre = ? WHERE id = ?",
                (original_name, admin_id)
            )
            client2.commit()
            result.add_detail(f"Nombre restaurado a: {original_name}")
        else:
            result.fail("❌ UPDATE NO persistió")
            actual_name = updated_user[0] if updated_user else "NULL"
            result.add_detail(f"Nombre esperado: {new_name}")
            result.add_detail(f"Nombre actual: {actual_name}")
        
    except Exception as e:
        result.fail(f"Error: {str(e)}")
        import traceback
        result.add_detail(traceback.format_exc())
    
    return result


def test_connect_function():
    """Prueba 7: Verificar función connect() del sistema."""
    result = TestResult("Función connect() del Sistema")
    
    try:
        # Verificar tipo de BD
        db_type = get_db_type()
        result.add_detail(f"Tipo de BD detectado: {db_type}")
        
        # Crear conexión
        conn = connect()
        result.add_detail(f"Conexión creada: {type(conn).__name__}")
        
        # Verificar métodos
        has_execute = hasattr(conn, 'execute')
        has_commit = hasattr(conn, 'commit')
        has_close = hasattr(conn, 'close')
        
        result.add_detail(f"Tiene execute: {has_execute}")
        result.add_detail(f"Tiene commit: {has_commit}")
        result.add_detail(f"Tiene close: {has_close}")
        
        if has_execute and has_commit and has_close:
            result.success("Conexión tiene todos los métodos necesarios")
        else:
            result.fail("Conexión no tiene todos los métodos necesarios")
        
        conn.close()
        
    except Exception as e:
        result.fail(f"Error: {str(e)}")
    
    return result


def test_commit_behavior():
    """Prueba 8: Verificar comportamiento de commit()."""
    result = TestResult("Comportamiento de commit()")
    
    test_username = f"commit_test_{int(time.time())}"
    
    try:
        url, token = get_turso_config()
        client = create_turso_client(url, token)
        
        # Insertar sin commit
        password_hash = hash_password("test123")
        now = datetime.now().isoformat()
        
        result.add_detail("Insertando SIN commit...")
        client.execute(
            """INSERT INTO usuarios 
               (username, password_hash, nombre, rol, activo, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (test_username, password_hash, "Test Sin Commit", "OPERADOR", 1, now, now)
        )
        
        # Verificar inmediatamente (mismo cliente)
        cursor = client.execute("SELECT username FROM usuarios WHERE username = ?", (test_username,))
        found_before_commit = cursor.fetchone()
        
        result.add_detail(f"Encontrado antes de commit: {found_before_commit is not None}")
        
        # Ahora hacer commit
        result.add_detail("Ejecutando commit()...")
        client.commit()
        
        # Verificar con nuevo cliente
        time.sleep(1)
        client2 = create_turso_client(url, token)
        cursor2 = client2.execute("SELECT username FROM usuarios WHERE username = ?", (test_username,))
        found_after_commit = cursor2.fetchone()
        
        result.add_detail(f"Encontrado después de commit: {found_after_commit is not None}")
        
        if found_after_commit:
            result.success("commit() funciona correctamente")
            # Limpiar
            client2.execute("DELETE FROM usuarios WHERE username = ?", (test_username,))
            client2.commit()
        else:
            result.fail("commit() NO está persistiendo los datos")
        
    except Exception as e:
        result.fail(f"Error: {str(e)}")
        import traceback
        result.add_detail(traceback.format_exc())
    
    return result


def run_all_tests():
    """Ejecuta todas las pruebas."""
    print_header("SUITE DE PRUEBAS DE PERSISTENCIA EN TURSO")
    
    print("\n🔍 Verificando configuración...")
    if not is_turso_configured():
        print("❌ Turso no está configurado")
        print("\nAsegúrate de tener:")
        print("  - TURSO_DATABASE_URL en .streamlit/secrets.toml o variables de entorno")
        print("  - TURSO_AUTH_TOKEN en .streamlit/secrets.toml o variables de entorno")
        return
    
    print("✅ Turso está configurado")
    
    # Lista de pruebas
    tests = [
        test_turso_connection_basic,
        test_turso_client_creation,
        test_simple_select,
        test_select_usuarios,
        test_insert_and_verify,
        test_update_and_verify,
        test_connect_function,
        test_commit_behavior,
    ]
    
    results = []
    
    # Ejecutar pruebas
    for i, test_func in enumerate(tests, 1):
        print(f"\n{'─' * 70}")
        doc = test_func.__doc__ or "Sin descripción"
        test_name = doc.split(':')[1].strip() if ':' in doc else doc
        print(f"Ejecutando prueba {i}/{len(tests)}: {test_name}")
        print(f"{'─' * 70}")
        
        result = test_func()
        results.append(result)
        result.print_result()
        
        time.sleep(0.5)  # Pequeña pausa entre pruebas
    
    # Resumen
    print_header("RESUMEN DE PRUEBAS")
    
    passed = sum(1 for r in results if r.passed)
    failed = len(results) - passed
    
    print(f"\n✅ Pruebas exitosas: {passed}/{len(results)}")
    print(f"❌ Pruebas fallidas: {failed}/{len(results)}")
    
    if failed > 0:
        print("\n⚠️  PRUEBAS FALLIDAS:")
        for result in results:
            if not result.passed:
                print(f"  • {result.name}")
                print(f"    {result.message}")
    
    print("\n" + "=" * 70)
    
    if failed == 0:
        print("🎉 ¡TODAS LAS PRUEBAS PASARON!")
        print("✅ El sistema de persistencia funciona correctamente")
    else:
        print("⚠️  HAY PROBLEMAS DE PERSISTENCIA")
        print("❌ Revisa los detalles de las pruebas fallidas arriba")
    
    print("=" * 70 + "\n")
    
    return failed == 0


if __name__ == "__main__":
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n👋 Pruebas interrumpidas por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

# Made with Bob
