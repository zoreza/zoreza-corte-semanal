"""
Script de migración para actualizar la base de datos existente.
Agrega nuevos campos y tablas sin perder datos.

Cambios:
1. Agrega campos opcionales a tabla clientes: domicilio, colonia, telefono, poblacion
2. Agrega campos a tabla maquinas: numero_permiso, fecha_permiso, asignada
3. Crea tabla cliente_ruta para asignaciones Cliente→Ruta
4. Migra datos de maquina_ruta a cliente_ruta
"""

import sqlite3
from pathlib import Path
from zoreza.db.core import db_path, now_iso

def migrate(silent: bool = False):
    """Ejecuta la migración de la base de datos.
    
    Args:
        silent: Si es True, no imprime mensajes (útil para Streamlit)
    """
    path = db_path()
    if not Path(path).exists():
        if not silent:
            print(f"❌ Base de datos no encontrada en: {path}")
        return False
    
    if not silent:
        print(f"🔄 Iniciando migración de: {path}")
    con = sqlite3.connect(path)
    con.row_factory = sqlite3.Row
    
    try:
        # Verificar si ya se ejecutó la migración
        cursor = con.execute("PRAGMA table_info(clientes)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'domicilio' in columns:
            if not silent:
                print("✅ La migración ya fue ejecutada anteriormente.")
            return True
        
        if not silent:
            print("📝 Aplicando cambios al esquema...")
        
        # 1. Agregar campos opcionales a clientes
        if not silent:
            print("  → Agregando campos a tabla 'clientes'...")
        con.execute("ALTER TABLE clientes ADD COLUMN domicilio TEXT")
        con.execute("ALTER TABLE clientes ADD COLUMN colonia TEXT")
        con.execute("ALTER TABLE clientes ADD COLUMN telefono TEXT")
        con.execute("ALTER TABLE clientes ADD COLUMN poblacion TEXT")
        
        # 2. Agregar campos a maquinas
        if not silent:
            print("  → Agregando campos a tabla 'maquinas'...")
        con.execute("ALTER TABLE maquinas ADD COLUMN numero_permiso TEXT")
        con.execute("ALTER TABLE maquinas ADD COLUMN fecha_permiso TEXT")
        con.execute("ALTER TABLE maquinas ADD COLUMN asignada INTEGER NOT NULL DEFAULT 1 CHECK (asignada IN (0,1))")
        
        # 3. Crear tabla cliente_ruta
        if not silent:
            print("  → Creando tabla 'cliente_ruta'...")
        con.execute("""
            CREATE TABLE IF NOT EXISTS cliente_ruta(
                cliente_id INTEGER NOT NULL,
                ruta_id INTEGER NOT NULL,
                activo INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0,1)),
                created_at TEXT NOT NULL,
                created_by INTEGER,
                PRIMARY KEY (cliente_id, ruta_id),
                FOREIGN KEY(cliente_id) REFERENCES clientes(id),
                FOREIGN KEY(ruta_id) REFERENCES rutas(id)
            )
        """)
        
        # 4. Migrar datos de maquina_ruta a cliente_ruta
        if not silent:
            print("  → Migrando asignaciones de Máquina→Ruta a Cliente→Ruta...")
        
        # Obtener todas las asignaciones actuales de maquina_ruta
        maquina_rutas = con.execute("""
            SELECT DISTINCT m.cliente_id, mr.ruta_id, mr.activo
            FROM maquina_ruta mr
            JOIN maquinas m ON m.id = mr.maquina_id
            WHERE mr.activo = 1
        """).fetchall()
        
        ts = now_iso()
        migrated = 0
        
        for row in maquina_rutas:
            # Insertar en cliente_ruta si no existe
            con.execute("""
                INSERT OR IGNORE INTO cliente_ruta(cliente_id, ruta_id, activo, created_at, created_by)
                VALUES (?, ?, ?, ?, NULL)
            """, (row[0], row[1], row[2], ts))
            migrated += 1
        
        if not silent:
            print(f"  ✓ Migradas {migrated} asignaciones únicas de Cliente→Ruta")
        
        # 5. Crear índices para mejor performance
        if not silent:
            print("  → Creando índices...")
        con.execute("CREATE INDEX IF NOT EXISTS idx_maquinas_asignada ON maquinas(asignada)")
        con.execute("CREATE INDEX IF NOT EXISTS idx_cliente_ruta ON cliente_ruta(cliente_id, ruta_id)")
        
        con.commit()
        if not silent:
            print("✅ Migración completada exitosamente!")
            print("\n📋 Resumen de cambios:")
            print("  • Clientes: +4 campos opcionales (domicilio, colonia, telefono, poblacion)")
            print("  • Máquinas: +3 campos (numero_permiso, fecha_permiso, asignada)")
            print("  • Nueva tabla: cliente_ruta")
            print(f"  • Asignaciones migradas: {migrated}")
            print("\n⚠️  IMPORTANTE:")
            print("  • La tabla 'maquina_ruta' se mantiene para compatibilidad")
            print("  • Ahora las asignaciones se hacen por Cliente→Ruta")
            print("  • Las máquinas heredan la ruta de su cliente")
            print("  • Puedes desasignar máquinas marcando 'asignada=0'")
        
        return True
        
    except Exception as e:
        con.rollback()
        if not silent:
            print(f"❌ Error durante la migración: {e}")
        return False
    finally:
        con.close()

if __name__ == "__main__":
    import sys
    success = migrate()
    sys.exit(0 if success else 1)

# Made with Bob
