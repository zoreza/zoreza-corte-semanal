import os
import sqlite3
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from zoreza.services.passwords import hash_password

# Intentar importar soporte para Turso y sincronización
try:
    from zoreza.services import turso_service
    from zoreza.services import sync_service
    TURSO_SUPPORT = True
except ImportError:
    TURSO_SUPPORT = False
    turso_service = None
    sync_service = None

SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS usuarios(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT NOT NULL UNIQUE,
  password_hash TEXT NOT NULL,
  nombre TEXT NOT NULL,
  rol TEXT NOT NULL CHECK (rol IN ('ADMIN','SUPERVISOR','OPERADOR')),
  activo INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0,1)),
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  created_by INTEGER,
  updated_by INTEGER
);

CREATE TABLE IF NOT EXISTS clientes(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  nombre TEXT NOT NULL,
  comision_pct REAL NOT NULL DEFAULT 0.40,
  domicilio TEXT,
  colonia TEXT,
  telefono TEXT,
  poblacion TEXT,
  activo INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0,1)),
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  created_by INTEGER,
  updated_by INTEGER
);

CREATE TABLE IF NOT EXISTS rutas(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  nombre TEXT NOT NULL UNIQUE,
  descripcion TEXT,
  activo INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0,1)),
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  created_by INTEGER,
  updated_by INTEGER
);

CREATE TABLE IF NOT EXISTS maquinas(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  codigo TEXT NOT NULL UNIQUE,
  cliente_id INTEGER NOT NULL,
  numero_permiso TEXT,
  fecha_permiso TEXT,
  asignada INTEGER NOT NULL DEFAULT 1 CHECK (asignada IN (0,1)),
  activo INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0,1)),
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  created_by INTEGER,
  updated_by INTEGER,
  FOREIGN KEY(cliente_id) REFERENCES clientes(id)
);

CREATE TABLE IF NOT EXISTS usuario_ruta(
  usuario_id INTEGER NOT NULL,
  ruta_id INTEGER NOT NULL,
  activo INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0,1)),
  PRIMARY KEY (usuario_id, ruta_id),
  FOREIGN KEY(usuario_id) REFERENCES usuarios(id),
  FOREIGN KEY(ruta_id) REFERENCES rutas(id)
);

CREATE TABLE IF NOT EXISTS cliente_ruta(
  cliente_id INTEGER NOT NULL,
  ruta_id INTEGER NOT NULL,
  activo INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0,1)),
  created_at TEXT NOT NULL,
  created_by INTEGER,
  PRIMARY KEY (cliente_id, ruta_id),
  FOREIGN KEY(cliente_id) REFERENCES clientes(id),
  FOREIGN KEY(ruta_id) REFERENCES rutas(id)
);

CREATE TABLE IF NOT EXISTS maquina_ruta(
  maquina_id INTEGER NOT NULL,
  ruta_id INTEGER NOT NULL,
  activo INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0,1)),
  PRIMARY KEY (maquina_id, ruta_id),
  FOREIGN KEY(maquina_id) REFERENCES maquinas(id),
  FOREIGN KEY(ruta_id) REFERENCES rutas(id)
);

CREATE TABLE IF NOT EXISTS config(
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  updated_by INTEGER
);

CREATE TABLE IF NOT EXISTS cat_irregularidad(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  nombre TEXT NOT NULL UNIQUE,
  requiere_nota INTEGER NOT NULL DEFAULT 0 CHECK (requiere_nota IN (0,1)),
  activo INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0,1))
);

CREATE TABLE IF NOT EXISTS cat_omision(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  nombre TEXT NOT NULL UNIQUE,
  requiere_nota INTEGER NOT NULL DEFAULT 0 CHECK (requiere_nota IN (0,1)),
  activo INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0,1))
);

CREATE TABLE IF NOT EXISTS cat_evento_contador(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  nombre TEXT NOT NULL UNIQUE,
  requiere_nota INTEGER NOT NULL DEFAULT 0 CHECK (requiere_nota IN (0,1)),
  activo INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0,1))
);

CREATE TABLE IF NOT EXISTS cortes(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  cliente_id INTEGER NOT NULL,
  week_start TEXT NOT NULL,
  week_end TEXT NOT NULL,
  fecha_corte TEXT NOT NULL,
  comision_pct_usada REAL NOT NULL,
  neto_cliente REAL NOT NULL DEFAULT 0,
  pago_cliente REAL NOT NULL DEFAULT 0,
  ganancia_dueno REAL NOT NULL DEFAULT 0,
  estado TEXT NOT NULL CHECK (estado IN ('BORRADOR','CERRADO')),
  created_at TEXT NOT NULL,
  created_by INTEGER NOT NULL,
  UNIQUE(cliente_id, week_start),
  FOREIGN KEY(cliente_id) REFERENCES clientes(id)
);

CREATE TABLE IF NOT EXISTS corte_detalle(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  corte_id INTEGER NOT NULL,
  maquina_id INTEGER NOT NULL,
  estado_maquina TEXT NOT NULL CHECK (estado_maquina IN ('CAPTURADA','OMITIDA')),

  score_tarjeta REAL,
  efectivo_total REAL,
  fondo REAL,
  recaudable REAL,
  diferencia_score REAL,
  causa_irregularidad_id INTEGER,
  nota_irregularidad TEXT,

  contador_entrada_actual INTEGER,
  contador_salida_actual INTEGER,
  contador_entrada_prev INTEGER,
  contador_salida_prev INTEGER,
  delta_entrada INTEGER,
  delta_salida INTEGER,
  monto_estimado_contadores REAL,
  evento_contador_id INTEGER,
  nota_evento_contador TEXT,

  motivo_omision_id INTEGER,
  nota_omision TEXT,

  created_at TEXT NOT NULL,
  created_by INTEGER NOT NULL,

  UNIQUE(corte_id, maquina_id),

  FOREIGN KEY(corte_id) REFERENCES cortes(id),
  FOREIGN KEY(maquina_id) REFERENCES maquinas(id),
  FOREIGN KEY(causa_irregularidad_id) REFERENCES cat_irregularidad(id),
  FOREIGN KEY(evento_contador_id) REFERENCES cat_evento_contador(id),
  FOREIGN KEY(motivo_omision_id) REFERENCES cat_omision(id)
);

CREATE INDEX IF NOT EXISTS idx_maquinas_cliente ON maquinas(cliente_id);
CREATE INDEX IF NOT EXISTS idx_maquinas_asignada ON maquinas(asignada);
CREATE INDEX IF NOT EXISTS idx_cliente_ruta ON cliente_ruta(cliente_id, ruta_id);
CREATE INDEX IF NOT EXISTS idx_cortes_cliente_week ON cortes(cliente_id, week_start);
CREATE INDEX IF NOT EXISTS idx_detalle_corte ON corte_detalle(corte_id);

CREATE TABLE IF NOT EXISTS gastos(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  fecha TEXT NOT NULL,
  categoria TEXT NOT NULL CHECK (categoria IN ('REFACCIONES','FONDOS_ROBOS','PERMISOS','EMPLEADOS','SERVICIOS','TRANSPORTE','OTRO')),
  descripcion TEXT NOT NULL,
  monto REAL NOT NULL,
  notas TEXT,
  created_at TEXT NOT NULL,
  created_by INTEGER NOT NULL,
  FOREIGN KEY(created_by) REFERENCES usuarios(id)
);

CREATE INDEX IF NOT EXISTS idx_gastos_fecha ON gastos(fecha);
CREATE INDEX IF NOT EXISTS idx_gastos_categoria ON gastos(categoria);
"""

DEFAULT_CONFIG = {
    "tolerancia_pesos": "30",
    "fondo_sugerido": "500",
    "semana_inicia": "LUNES",
    "ticket_negocio_nombre": "Zoreza",
    "ticket_footer": "Gracias por su preferencia.",
}

DEFAULT_CATS = {
    "cat_irregularidad": [
        ("Manipulación declarada", 0),
        ("Manipulación no declarada", 1),
        ("Falla Técnica del equipo", 0),
        ("Desconocido, posible manipulación por terceros", 1),
    ],
    "cat_omision": [
        ("No accesible", 0),
        ("Fuera de servicio", 0),
        ("Cliente no autorizó", 0),
        ("Falta de llave / acceso", 0),
        ("Otro", 1),
        ("Desconocido", 1),
    ],
    "cat_evento_contador": [
        ("Reset contador", 1),
        ("Falla", 1),
        ("Cambio de tablero", 1),
        ("Mantenimiento", 1),
        ("Otro", 1),
    ],
}


class FallbackConnection:
    """
    Wrapper de conexión que maneja fallback automático entre Turso y SQLite local.
    Si Turso falla, guarda operaciones en cola y usa SQLite local.
    """
    def __init__(self, primary_conn, fallback_conn=None):
        self.primary_conn = primary_conn
        self.fallback_conn = fallback_conn
        self.using_fallback = False
        self._row_factory = None
    
    @property
    def row_factory(self):
        return self._row_factory
    
    @row_factory.setter
    def row_factory(self, value):
        self._row_factory = value
        if self.primary_conn:
            self.primary_conn.row_factory = value
        if self.fallback_conn:
            self.fallback_conn.row_factory = value
    
    def execute(self, sql: str, params: tuple = ()):
        """Ejecuta query con fallback automático."""
        # Intentar con conexión primaria (Turso)
        if not self.using_fallback and self.primary_conn:
            try:
                result = self.primary_conn.execute(sql, params)
                return result
            except Exception as e:
                print(f"⚠️ Error en Turso: {e}")
                print("🔄 Activando fallback a SQLite local...")
                
                # Marcar que Turso falló
                if sync_service:
                    sync_service.mark_turso_failed(str(e))
                
                self.using_fallback = True
                
                # Crear conexión fallback si no existe
                if not self.fallback_conn:
                    self.fallback_conn = self._create_fallback_connection()
        
        # Usar fallback (SQLite local)
        if self.fallback_conn:
            result = self.fallback_conn.execute(sql, params)
            
            # Guardar operación en cola si es escritura
            if sync_service and self._is_write_operation(sql):
                sync_service.add_pending_operation("execute", sql, params)
            
            return result
        
        raise Exception("No hay conexión disponible (ni Turso ni fallback)")
    
    def commit(self):
        """Commit con fallback."""
        if self.using_fallback and self.fallback_conn:
            self.fallback_conn.commit()
        elif self.primary_conn:
            try:
                self.primary_conn.commit()
            except Exception as e:
                print(f"⚠️ Error en commit de Turso: {e}")
                if sync_service:
                    sync_service.mark_turso_failed(str(e))
                self.using_fallback = True
                if self.fallback_conn:
                    self.fallback_conn.commit()
    
    def executescript(self, script: str):
        """Ejecuta script SQL con fallback."""
        if self.using_fallback and self.fallback_conn:
            return self.fallback_conn.executescript(script)
        elif self.primary_conn:
            try:
                return self.primary_conn.executescript(script)
            except Exception as e:
                print(f"⚠️ Error en executescript de Turso: {e}")
                if sync_service:
                    sync_service.mark_turso_failed(str(e))
                self.using_fallback = True
                if not self.fallback_conn:
                    self.fallback_conn = self._create_fallback_connection()
                return self.fallback_conn.executescript(script)
        
        raise Exception("No hay conexión disponible")
    
    def close(self):
        """Cierra ambas conexiones."""
        if self.primary_conn:
            try:
                self.primary_conn.close()
            except:
                pass
        if self.fallback_conn:
            try:
                self.fallback_conn.close()
            except:
                pass
    
    def _create_fallback_connection(self):
        """Crea conexión SQLite local para fallback."""
        path = db_path()
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        con = sqlite3.connect(path, check_same_thread=False)
        con.row_factory = self._row_factory or sqlite3.Row
        con.execute("PRAGMA foreign_keys = ON;")
        return con
    
    def _is_write_operation(self, sql: str) -> bool:
        """Detecta si una operación SQL es de escritura."""
        sql_upper = sql.strip().upper()
        write_keywords = ['INSERT', 'UPDATE', 'DELETE', 'CREATE', 'ALTER', 'DROP']
        return any(sql_upper.startswith(keyword) for keyword in write_keywords)

def db_path() -> str:
    return os.getenv("ZOREZA_DB_PATH", "./data/zoreza.db")

def connect():
    """
    Crea una conexión a la base de datos.
    Usa Turso (SQLite en la nube) si está configurado, con fallback a SQLite local solo en caso de error.
    """
    # Verificar si Turso está configurado
    if TURSO_SUPPORT and turso_service:
        from zoreza.services.turso_service import is_turso_configured, create_turso_client, get_turso_config
        
        if is_turso_configured():
            try:
                url, token = get_turso_config()
                primary_conn = create_turso_client(url, token)
                
                # Probar la conexión con una query simple
                try:
                    primary_conn.execute("SELECT 1").fetchone()
                    # Si llegamos aquí, Turso funciona correctamente
                    primary_conn.row_factory = sqlite3.Row
                    return primary_conn
                except Exception as test_error:
                    print(f"⚠️ Error al probar conexión Turso: {test_error}")
                    # Continuar al fallback
                
            except Exception as e:
                print(f"⚠️ Error al crear cliente Turso: {e}")
                print("📁 Cayendo a SQLite local")
    
    # Usar SQLite local (comportamiento por defecto)
    path = db_path()
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path, check_same_thread=False)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON;")
    return con

def get_db_type() -> str:
    """Retorna el tipo de base de datos en uso: 'turso' o 'local'."""
    from zoreza.services.turso_service import is_turso_configured
    return "turso" if is_turso_configured() else "local"

def now_iso() -> str:
    """Retorna timestamp actual en zona horaria configurada."""
    tz = ZoneInfo(os.getenv("APP_TZ", "America/Mexico_City"))
    return datetime.now(tz).isoformat(timespec="seconds")

def init_db(seed: bool = True):
    """
    Inicializa la base de datos.
    Si falla con Turso, automáticamente usa SQLite local.
    """
    try:
        con = connect()
        con.executescript(SCHEMA_SQL)
        con.commit()

        if not seed:
            return

        # config
        for k, v in DEFAULT_CONFIG.items():
            con.execute(
                "INSERT OR IGNORE INTO config(key,value,updated_at,updated_by) VALUES (?,?,?,NULL)",
                (k, v, now_iso()),
            )
        con.commit()
    except Exception as e:
        # Si falla (probablemente Turso), forzar SQLite local y reintentar
        print(f"⚠️ Error inicializando BD con Turso: {e}")
        print("🔄 Reintentando con SQLite local...")
        
        # Forzar uso de SQLite local
        if TURSO_SUPPORT:
            from zoreza.services import turso_service
            turso_service.force_local_db()
        
        # Reintentar con SQLite local
        con = connect()
        con.executescript(SCHEMA_SQL)
        con.commit()

        if not seed:
            return

        # config
        for k, v in DEFAULT_CONFIG.items():
            con.execute(
                "INSERT OR IGNORE INTO config(key,value,updated_at,updated_by) VALUES (?,?,?,NULL)",
                (k, v, now_iso()),
            )
        con.commit()
    
    # IMPORTANTE: Este código debe ejecutarse SIEMPRE, no solo en el except
    if not seed:
        return
    
    # cats
    for table, rows in DEFAULT_CATS.items():
        for nombre, req in rows:
            con.execute(
                f"INSERT OR IGNORE INTO {table}(nombre,requiere_nota,activo) VALUES (?,?,1)",
                (nombre, req),
            )
    con.commit()

    # users if empty - SOLO CREAR ADMIN
    print("🔍 Verificando usuarios existentes...")
    result = con.execute("SELECT COUNT(*) AS n FROM usuarios").fetchone()
    n_users = result["n"] if result else 0
    print(f"📊 Usuarios encontrados: {n_users}")
    
    if n_users == 0:
        print("📝 Creando usuario admin...")
        password_hash = hash_password("admin123")
        print(f"🔐 Hash generado: {password_hash[:20]}...")
        
        con.execute(
            "INSERT INTO usuarios(username,password_hash,nombre,rol,activo,created_at,updated_at,created_by,updated_by) VALUES (?,?,?,?,1,?,?,NULL,NULL)",
            ("admin", password_hash, "Admin Zoreza", "ADMIN", now_iso(), now_iso()),
        )
        con.commit()
        print("✅ Usuario admin insertado")
        
        # Verificar que se creó
        verify = con.execute("SELECT username, rol, activo FROM usuarios WHERE username='admin'").fetchone()
        if verify:
            print(f"✅ Usuario admin verificado: {dict(verify)}")
        else:
            print("❌ ERROR: Usuario admin NO se creó correctamente")
    else:
        print(f"ℹ️ Ya existen {n_users} usuarios, no se creará admin")
    
    # NO CREAR DATOS DEMO - El usuario los llenará manualmente
    
    # Cerrar conexión
    con.close()
