import os
import sqlite3
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from zoreza.services.passwords import hash_password

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

def db_path() -> str:
    return os.getenv("ZOREZA_DB_PATH", "./data/zoreza.db")

def connect():
    path = db_path()
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path, check_same_thread=False)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON;")
    return con

def now_iso() -> str:
    """Retorna timestamp actual en zona horaria configurada."""
    tz = ZoneInfo(os.getenv("APP_TZ", "America/Mexico_City"))
    return datetime.now(tz).isoformat(timespec="seconds")

def init_db(seed: bool = True):
    con = connect()
    try:
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

        # cats
        for table, rows in DEFAULT_CATS.items():
            for nombre, req in rows:
                con.execute(
                    f"INSERT OR IGNORE INTO {table}(nombre,requiere_nota,activo) VALUES (?,?,1)",
                    (nombre, req),
                )
        con.commit()

        # users if empty
        n_users = con.execute("SELECT COUNT(*) AS n FROM usuarios").fetchone()["n"]
        if n_users == 0:
            con.execute(
                "INSERT INTO usuarios(username,password_hash,nombre,rol,activo,created_at,updated_at,created_by,updated_by) VALUES (?,?,?,?,1,?,?,NULL,NULL)",
                ("admin", hash_password("admin123"), "Admin Zoreza", "ADMIN", now_iso(), now_iso()),
            )
            con.execute(
                "INSERT INTO usuarios(username,password_hash,nombre,rol,activo,created_at,updated_at,created_by,updated_by) VALUES (?,?,?,?,1,?,?,NULL,NULL)",
                ("operador", hash_password("operador123"), "Operador Zoreza", "OPERADOR", now_iso(), now_iso()),
            )
            con.commit()

        # seed minimal entities if empty
        n_clientes = con.execute("SELECT COUNT(*) AS n FROM clientes").fetchone()["n"]
        if n_clientes == 0:
            admin_id = con.execute("SELECT id FROM usuarios WHERE username='admin'").fetchone()["id"]
            con.execute(
                "INSERT INTO clientes(nombre,comision_pct,activo,created_at,updated_at,created_by,updated_by) VALUES (?,?,1,?,?,?,?)",
                ("Cliente Demo", 0.40, now_iso(), now_iso(), admin_id, admin_id),
            )
            cliente_id = con.execute("SELECT id FROM clientes WHERE nombre='Cliente Demo'").fetchone()["id"]
            con.execute(
                "INSERT INTO maquinas(codigo,cliente_id,activo,created_at,updated_at,created_by,updated_by) VALUES (?,?,1,?,?,?,?)",
                ("M-001", cliente_id, now_iso(), now_iso(), admin_id, admin_id),
            )
            con.execute(
                "INSERT INTO maquinas(codigo,cliente_id,activo,created_at,updated_at,created_by,updated_by) VALUES (?,?,1,?,?,?,?)",
                ("M-002", cliente_id, now_iso(), now_iso(), admin_id, admin_id),
            )
            con.execute(
                "INSERT INTO rutas(nombre,descripcion,activo,created_at,updated_at,created_by,updated_by) VALUES (?,?,1,?,?,?,?)",
                ("Ruta Demo", "Ruta inicial", now_iso(), now_iso(), admin_id, admin_id),
            )
            ruta_id = con.execute("SELECT id FROM rutas WHERE nombre='Ruta Demo'").fetchone()["id"]
            op_id = con.execute("SELECT id FROM usuarios WHERE username='operador'").fetchone()["id"]

            con.execute("INSERT INTO usuario_ruta(usuario_id,ruta_id,activo) VALUES (?,?,1)", (op_id, ruta_id))
            for row in con.execute("SELECT id FROM maquinas").fetchall():
                con.execute("INSERT INTO maquina_ruta(maquina_id,ruta_id,activo) VALUES (?,?,1)", (row["id"], ruta_id))
            con.commit()

    finally:
        con.close()
