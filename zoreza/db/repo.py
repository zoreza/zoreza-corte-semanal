from __future__ import annotations
from zoreza.db.queries import fetchall, fetchone, execute, execute_returning_id
from zoreza.db.core import now_iso, connect

def list_usuarios() -> list[dict]:
    return fetchall("SELECT id,username,nombre,rol,activo,created_at,updated_at FROM usuarios ORDER BY id")

def create_usuario(username: str, password_hash: str, nombre: str, rol: str, activo: int, actor_id: int | None) -> int:
    ts = now_iso()
    return execute_returning_id(
        "INSERT INTO usuarios(username,password_hash,nombre,rol,activo,created_at,updated_at,created_by,updated_by) VALUES (?,?,?,?,?,?,?,?,?)",
        (username, password_hash, nombre, rol, int(activo), ts, ts, actor_id, actor_id),
    )

def update_usuario(user_id: int, nombre: str, rol: str, activo: int, actor_id: int | None, password_hash: str | None = None) -> None:
    ts = now_iso()
    if password_hash:
        execute(
            "UPDATE usuarios SET password_hash=?, nombre=?, rol=?, activo=?, updated_at=?, updated_by=? WHERE id=?",
            (password_hash, nombre, rol, int(activo), ts, actor_id, user_id),
        )
    else:
        execute(
            "UPDATE usuarios SET nombre=?, rol=?, activo=?, updated_at=?, updated_by=? WHERE id=?",
            (nombre, rol, int(activo), ts, actor_id, user_id),
        )

def list_clientes() -> list[dict]:
    return fetchall("SELECT * FROM clientes ORDER BY nombre")

def create_cliente(nombre: str, comision_pct: float, activo: int, actor_id: int | None,
                   domicilio: str | None = None, colonia: str | None = None,
                   telefono: str | None = None, poblacion: str | None = None):
    ts = now_iso()
    return execute_returning_id(
        "INSERT INTO clientes(nombre,comision_pct,domicilio,colonia,telefono,poblacion,activo,created_at,updated_at,created_by,updated_by) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
        (nombre, float(comision_pct), domicilio, colonia, telefono, poblacion, int(activo), ts, ts, actor_id, actor_id),
    )

def update_cliente(cliente_id: int, nombre: str, comision_pct: float, activo: int, actor_id: int | None,
                   domicilio: str | None = None, colonia: str | None = None,
                   telefono: str | None = None, poblacion: str | None = None):
    ts = now_iso()
    execute(
        "UPDATE clientes SET nombre=?, comision_pct=?, domicilio=?, colonia=?, telefono=?, poblacion=?, activo=?, updated_at=?, updated_by=? WHERE id=?",
        (nombre, float(comision_pct), domicilio, colonia, telefono, poblacion, int(activo), ts, actor_id, cliente_id),
    )

def list_maquinas() -> list[dict]:
    return fetchall(
        """
        SELECT m.*, c.nombre AS cliente_nombre
        FROM maquinas m JOIN clientes c ON c.id=m.cliente_id
        ORDER BY c.nombre, m.codigo
        """
    )

def create_maquina(codigo: str, cliente_id: int, activo: int, actor_id: int | None,
                   numero_permiso: str | None = None, fecha_permiso: str | None = None, asignada: int = 1):
    ts = now_iso()
    return execute_returning_id(
        "INSERT INTO maquinas(codigo,cliente_id,numero_permiso,fecha_permiso,asignada,activo,created_at,updated_at,created_by,updated_by) VALUES (?,?,?,?,?,?,?,?,?,?)",
        (codigo, int(cliente_id), numero_permiso, fecha_permiso, int(asignada), int(activo), ts, ts, actor_id, actor_id),
    )

def update_maquina(maquina_id: int, codigo: str, cliente_id: int, activo: int, actor_id: int | None,
                   numero_permiso: str | None = None, fecha_permiso: str | None = None, asignada: int = 1):
    ts = now_iso()
    execute(
        "UPDATE maquinas SET codigo=?, cliente_id=?, numero_permiso=?, fecha_permiso=?, asignada=?, activo=?, updated_at=?, updated_by=? WHERE id=?",
        (codigo, int(cliente_id), numero_permiso, fecha_permiso, int(asignada), int(activo), ts, actor_id, maquina_id),
    )

def list_rutas() -> list[dict]:
    return fetchall("SELECT * FROM rutas ORDER BY nombre")

def create_ruta(nombre: str, descripcion: str, activo: int, actor_id: int | None) -> int:
    ts = now_iso()
    return execute_returning_id(
        "INSERT INTO rutas(nombre,descripcion,activo,created_at,updated_at,created_by,updated_by) VALUES (?,?,?,?,?,?,?)",
        (nombre, descripcion, int(activo), ts, ts, actor_id, actor_id),
    )

def update_ruta(ruta_id: int, nombre: str, descripcion: str, activo: int, actor_id: int | None):
    ts = now_iso()
    execute(
        "UPDATE rutas SET nombre=?, descripcion=?, activo=?, updated_at=?, updated_by=? WHERE id=?",
        (nombre, descripcion, int(activo), ts, actor_id, ruta_id),
    )

def list_usuario_ruta():
    return fetchall(
        """
        SELECT ur.usuario_id, u.username, u.nombre AS usuario_nombre, ur.ruta_id, r.nombre AS ruta_nombre, ur.activo
        FROM usuario_ruta ur
        JOIN usuarios u ON u.id=ur.usuario_id
        JOIN rutas r ON r.id=ur.ruta_id
        ORDER BY u.username, r.nombre
        """
    )

def set_usuario_ruta(usuario_id: int, ruta_id: int, activo: int):
    execute(
        "INSERT INTO usuario_ruta(usuario_id,ruta_id,activo) VALUES (?,?,?) "
        "ON CONFLICT(usuario_id,ruta_id) DO UPDATE SET activo=excluded.activo",
        (int(usuario_id), int(ruta_id), int(activo)),
    )

def list_maquina_ruta():
    return fetchall(
        """
        SELECT mr.maquina_id, m.codigo AS maquina_codigo, mr.ruta_id, r.nombre AS ruta_nombre, mr.activo
        FROM maquina_ruta mr
        JOIN maquinas m ON m.id=mr.maquina_id
        JOIN rutas r ON r.id=mr.ruta_id
        ORDER BY m.codigo, r.nombre
        """
    )

def set_maquina_ruta(maquina_id: int, ruta_id: int, activo: int):
    execute(
        "INSERT INTO maquina_ruta(maquina_id,ruta_id,activo) VALUES (?,?,?) "
        "ON CONFLICT(maquina_id,ruta_id) DO UPDATE SET activo=excluded.activo",
        (int(maquina_id), int(ruta_id), int(activo)),
    )

def list_cliente_ruta():
    return fetchall(
        """
        SELECT cr.cliente_id, c.nombre AS cliente_nombre, cr.ruta_id, r.nombre AS ruta_nombre, cr.activo
        FROM cliente_ruta cr
        JOIN clientes c ON c.id=cr.cliente_id
        JOIN rutas r ON r.id=cr.ruta_id
        ORDER BY c.nombre, r.nombre
        """
    )

def set_cliente_ruta(cliente_id: int, ruta_id: int, activo: int, actor_id: int | None):
    ts = now_iso()
    execute(
        "INSERT INTO cliente_ruta(cliente_id,ruta_id,activo,created_at,created_by) VALUES (?,?,?,?,?) "
        "ON CONFLICT(cliente_id,ruta_id) DO UPDATE SET activo=excluded.activo",
        (int(cliente_id), int(ruta_id), int(activo), ts, actor_id),
    )

def get_cliente_ruta(cliente_id: int) -> dict | None:
    """Obtiene la ruta asignada a un cliente."""
    return fetchone(
        "SELECT ruta_id FROM cliente_ruta WHERE cliente_id=? AND activo=1",
        (int(cliente_id),)
    )

def list_maquinas_sin_asignar():
    """Lista máquinas que no están asignadas (pool de máquinas disponibles)."""
    return fetchall(
        """
        SELECT m.*, c.nombre AS cliente_nombre
        FROM maquinas m
        JOIN clientes c ON c.id=m.cliente_id
        WHERE m.asignada=0 AND m.activo=1
        ORDER BY c.nombre, m.codigo
        """
    )

def list_cats(table: str):
    assert table in ("cat_irregularidad","cat_omision","cat_evento_contador")
    return fetchall(f"SELECT * FROM {table} ORDER BY nombre")

def upsert_cat(table: str, cat_id: int | None, nombre: str, requiere_nota: int, activo: int):
    assert table in ("cat_irregularidad","cat_omision","cat_evento_contador")
    if cat_id is None:
        execute(f"INSERT INTO {table}(nombre,requiere_nota,activo) VALUES (?,?,?)", (nombre, int(requiere_nota), int(activo)))
    else:
        execute(f"UPDATE {table} SET nombre=?, requiere_nota=?, activo=? WHERE id=?", (nombre, int(requiere_nota), int(activo), int(cat_id)))

# --- Corte workflow ---
def get_corte(cliente_id: int, week_start_iso: str) -> dict | None:
    return fetchone("SELECT * FROM cortes WHERE cliente_id=? AND week_start=?", (int(cliente_id), week_start_iso))

def create_or_get_borrador(cliente_id: int, week_start_iso: str, week_end_iso: str, fecha_corte_iso: str, comision_pct: float, actor_id: int):
    existing = get_corte(cliente_id, week_start_iso)
    if existing:
        return existing
    ts = now_iso()
    try:
        corte_id = execute_returning_id(
            "INSERT INTO cortes(cliente_id,week_start,week_end,fecha_corte,comision_pct_usada,estado,created_at,created_by) "
            "VALUES (?,?,?,?,?,'BORRADOR',?,?)",
            (int(cliente_id), week_start_iso, week_end_iso, fecha_corte_iso, float(comision_pct), ts, int(actor_id)),
        )
        return fetchone("SELECT * FROM cortes WHERE id=?", (corte_id,))
    except Exception:
        return get_corte(cliente_id, week_start_iso)

def list_detalle(corte_id: int):
    return fetchall(
        """
        SELECT d.*, m.codigo AS maquina_codigo,
               ci.nombre AS causa_nombre, ci.requiere_nota AS causa_requiere_nota,
               co.nombre AS omision_nombre, co.requiere_nota AS omision_requiere_nota,
               ce.nombre AS evento_nombre, ce.requiere_nota AS evento_requiere_nota
        FROM corte_detalle d
        JOIN maquinas m ON m.id=d.maquina_id
        LEFT JOIN cat_irregularidad ci ON ci.id=d.causa_irregularidad_id
        LEFT JOIN cat_omision co ON co.id=d.motivo_omision_id
        LEFT JOIN cat_evento_contador ce ON ce.id=d.evento_contador_id
        WHERE d.corte_id=?
        ORDER BY m.codigo
        """,
        (int(corte_id),),
    )

def upsert_detalle_base(corte_id: int, maquina_id: int, actor_id: int):
    ts = now_iso()
    con = connect()
    try:
        con.execute(
            "INSERT OR IGNORE INTO corte_detalle(corte_id,maquina_id,estado_maquina,created_at,created_by) VALUES (?,?, 'OMITIDA', ?, ?)",
            (int(corte_id), int(maquina_id), ts, int(actor_id)),
        )
        con.commit()
    finally:
        con.close()

def last_capturada_counters(maquina_id: int) -> dict | None:
    return fetchone(
        """
        SELECT d.contador_entrada_actual AS in_act, d.contador_salida_actual AS out_act
        FROM corte_detalle d
        JOIN cortes c ON c.id=d.corte_id
        WHERE d.maquina_id=? AND d.estado_maquina='CAPTURADA' AND c.estado='CERRADO'
        ORDER BY c.week_start DESC, d.id DESC
        LIMIT 1
        """,
        (int(maquina_id),),
    )

def save_detalle_capturada(corte_id: int, maquina_id: int, actor_id: int, payload: dict):
    ts = now_iso()
    execute(
        """UPDATE corte_detalle SET
            estado_maquina='CAPTURADA',
            score_tarjeta=?, efectivo_total=?, fondo=?, recaudable=?, diferencia_score=?,
            causa_irregularidad_id=?, nota_irregularidad=?,
            contador_entrada_actual=?, contador_salida_actual=?,
            contador_entrada_prev=?, contador_salida_prev=?,
            delta_entrada=?, delta_salida=?, monto_estimado_contadores=?,
            evento_contador_id=?, nota_evento_contador=?,
            motivo_omision_id=NULL, nota_omision=NULL,
            created_at=?, created_by=?
        WHERE corte_id=? AND maquina_id=?""",
        (
            payload.get("score_tarjeta"),
            payload.get("efectivo_total"),
            payload.get("fondo"),
            payload.get("recaudable"),
            payload.get("diferencia_score"),
            payload.get("causa_irregularidad_id"),
            payload.get("nota_irregularidad"),
            payload.get("contador_entrada_actual"),
            payload.get("contador_salida_actual"),
            payload.get("contador_entrada_prev"),
            payload.get("contador_salida_prev"),
            payload.get("delta_entrada"),
            payload.get("delta_salida"),
            payload.get("monto_estimado_contadores"),
            payload.get("evento_contador_id"),
            payload.get("nota_evento_contador"),
            ts,
            int(actor_id),
            int(corte_id),
            int(maquina_id),
        ),
    )

def save_detalle_omitida(corte_id: int, maquina_id: int, actor_id: int, motivo_omision_id: int | None, nota_omision: str | None):
    ts = now_iso()
    execute(
        """UPDATE corte_detalle SET
            estado_maquina='OMITIDA',
            motivo_omision_id=?, nota_omision=?,
            score_tarjeta=NULL, efectivo_total=NULL, fondo=NULL, recaudable=NULL, diferencia_score=NULL,
            causa_irregularidad_id=NULL, nota_irregularidad=NULL,
            contador_entrada_actual=NULL, contador_salida_actual=NULL,
            contador_entrada_prev=NULL, contador_salida_prev=NULL,
            delta_entrada=NULL, delta_salida=NULL, monto_estimado_contadores=NULL,
            evento_contador_id=NULL, nota_evento_contador=NULL,
            created_at=?, created_by=?
        WHERE corte_id=? AND maquina_id=?""",
        (motivo_omision_id, nota_omision, ts, int(actor_id), int(corte_id), int(maquina_id)),
    )

def close_corte(corte_id: int, neto_cliente: float, pago_cliente: float, ganancia_dueno: float):
    execute(
        "UPDATE cortes SET estado='CERRADO', neto_cliente=?, pago_cliente=?, ganancia_dueno=? WHERE id=?",
        (float(neto_cliente), float(pago_cliente), float(ganancia_dueno), int(corte_id)),
    )

def list_cortes(filter_cliente_id: int | None = None):
    if filter_cliente_id:
        return fetchall(
            """
            SELECT c.id, c.week_start, c.week_end, c.fecha_corte, c.estado, c.neto_cliente, c.pago_cliente, c.ganancia_dueno,
                   cl.nombre AS cliente_nombre, u.nombre AS operador_nombre
            FROM cortes c
            JOIN clientes cl ON cl.id=c.cliente_id
            JOIN usuarios u ON u.id=c.created_by
            WHERE c.cliente_id=?
            ORDER BY c.week_start DESC
            """,
            (int(filter_cliente_id),),
        )
    return fetchall(
        """
        SELECT c.id, c.week_start, c.week_end, c.fecha_corte, c.estado, c.neto_cliente, c.pago_cliente, c.ganancia_dueno,
               cl.nombre AS cliente_nombre, u.nombre AS operador_nombre
        FROM cortes c
        JOIN clientes cl ON cl.id=c.cliente_id
        JOIN usuarios u ON u.id=c.created_by
        ORDER BY c.week_start DESC
        """
    )

def list_cortes_for_export(cliente_id: int | None = None, fecha_inicio: str | None = None, fecha_fin: str | None = None):
    """Lista cortes con filtros para exportación."""
    conditions = []
    params = []
    
    if cliente_id:
        conditions.append("c.cliente_id = ?")
        params.append(int(cliente_id))
    
    if fecha_inicio:
        conditions.append("c.fecha_corte >= ?")
        params.append(fecha_inicio)
    
    if fecha_fin:
        conditions.append("c.fecha_corte <= ?")
        params.append(fecha_fin)
    
    where_clause = " AND ".join(conditions) if conditions else "1=1"
    
    sql = f"""
        SELECT c.*, cl.nombre AS cliente_nombre, u.nombre AS creador_nombre
        FROM cortes c
        JOIN clientes cl ON cl.id=c.cliente_id
        JOIN usuarios u ON u.id=c.created_by
        WHERE {where_clause}
        ORDER BY c.week_start DESC
    """
    
    return fetchall(sql, tuple(params))

def get_corte_by_id(corte_id: int) -> dict | None:
    """Obtiene un corte por su ID."""
    return fetchone("SELECT * FROM cortes WHERE id=?", (int(corte_id),))
def reopen_corte(corte_id: int, user_id: int, reason: str):
    """Reabre un corte cerrado para edición."""
    ts = now_iso()
    execute(
        "UPDATE cortes SET estado='BORRADOR' WHERE id=?",
        (int(corte_id),)
    )
    # Registrar en log
    log_corte_edit(corte_id, None, user_id, f"REAPERTURA: {reason}", {})

def update_corte_totals(corte_id: int, neto_cliente: float, pago_cliente: float, ganancia_dueno: float):
    """Actualiza los totales de un corte."""
    execute(
        "UPDATE cortes SET neto_cliente=?, pago_cliente=?, ganancia_dueno=? WHERE id=?",
        (float(neto_cliente), float(pago_cliente), float(ganancia_dueno), int(corte_id))
    )

def log_corte_edit(corte_id: int, maquina_id: int | None, user_id: int, reason: str, changes: dict):
    """Registra una edición en el log de auditoría."""
    ts = now_iso()
    # Crear tabla de log si no existe
    con = connect()
    try:
        con.execute("""
            CREATE TABLE IF NOT EXISTS corte_edit_log(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                corte_id INTEGER NOT NULL,
                maquina_id INTEGER,
                user_id INTEGER NOT NULL,
                reason TEXT NOT NULL,
                changes TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY(corte_id) REFERENCES cortes(id),
                FOREIGN KEY(maquina_id) REFERENCES maquinas(id),
                FOREIGN KEY(user_id) REFERENCES usuarios(id)
            )
        """)
        con.execute(
            "INSERT INTO corte_edit_log(corte_id, maquina_id, user_id, reason, changes, created_at) VALUES (?,?,?,?,?,?)",
            (int(corte_id), maquina_id, int(user_id), reason, str(changes), ts)
        )
        con.commit()
    finally:
        con.close()

def get_corte_edit_log(corte_id: int) -> list[dict]:
    """Obtiene el historial de ediciones de un corte."""
    return fetchall(
        """
        SELECT l.*, u.nombre AS user_nombre
        FROM corte_edit_log l
        JOIN usuarios u ON u.id=l.user_id
        WHERE l.corte_id=?
        ORDER BY l.created_at DESC
        """,
        (int(corte_id),)
    )
# --- Notificaciones ---
def create_notification(
    type: str,
    priority: str,
    title: str,
    message: str,
    corte_id: int | None,
    maquina_id: int | None,
    user_id: int | None
):
    """Crea una notificación."""
    ts = now_iso()
    con = connect()
    try:
        # Crear tabla si no existe
        con.execute("""
            CREATE TABLE IF NOT EXISTS notifications(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                priority TEXT NOT NULL,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                corte_id INTEGER,
                maquina_id INTEGER,
                user_id INTEGER,
                read INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                FOREIGN KEY(corte_id) REFERENCES cortes(id),
                FOREIGN KEY(maquina_id) REFERENCES maquinas(id),
                FOREIGN KEY(user_id) REFERENCES usuarios(id)
            )
        """)
        con.execute(
            "INSERT INTO notifications(type,priority,title,message,corte_id,maquina_id,user_id,read,created_at) VALUES (?,?,?,?,?,?,?,0,?)",
            (type, priority, title, message, corte_id, maquina_id, user_id, ts)
        )
        con.commit()
    finally:
        con.close()

def get_notifications(user_id: int | None = None, read: bool | None = None, limit: int = 100):
    """Obtiene notificaciones con filtros opcionales."""
    conditions = []
    params = []
    
    if user_id is not None:
        conditions.append("user_id = ?")
        params.append(int(user_id))
    
    if read is not None:
        conditions.append("read = ?")
        params.append(1 if read else 0)
    
    where_clause = " AND ".join(conditions) if conditions else "1=1"
    
    sql = f"""
        SELECT * FROM notifications
        WHERE {where_clause}
        ORDER BY created_at DESC
        LIMIT ?
    """
    params.append(limit)
    
    return fetchall(sql, tuple(params))

def mark_notification_read(notification_id: int):
    """Marca una notificación como leída."""
    execute("UPDATE notifications SET read=1 WHERE id=?", (int(notification_id),))

def mark_all_notifications_read(user_id: int | None = None):
    """Marca todas las notificaciones como leídas."""
    if user_id:
        execute("UPDATE notifications SET read=1 WHERE user_id=?", (int(user_id),))
    else:
        execute("UPDATE notifications SET read=1")

def count_notifications(user_id: int | None = None, unread_only: bool = True) -> int:
    """Cuenta notificaciones."""
    conditions = []
    params = []
    
    if user_id is not None:
        conditions.append("user_id = ?")
        params.append(int(user_id))
    
    if unread_only:
        conditions.append("read = 0")
    
    where_clause = " AND ".join(conditions) if conditions else "1=1"
    
    result = fetchone(f"SELECT COUNT(*) as count FROM notifications WHERE {where_clause}", tuple(params))
    return result["count"] if result else 0

def delete_old_notifications(days: int = 30) -> int:
    """Elimina notificaciones antiguas."""
    con = connect()
    try:
        # Calcular fecha límite
        from datetime import datetime, timedelta
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        
        cursor = con.execute("DELETE FROM notifications WHERE created_at < ?", (cutoff,))
        deleted = cursor.rowcount
        con.commit()
        return deleted
    finally:
        con.close()

# --- Gastos (solo ADMIN) ---
def create_gasto(fecha: str, categoria: str, descripcion: str, monto: float, notas: str | None, actor_id: int):
    """Crea un nuevo gasto."""
    ts = now_iso()
    return execute_returning_id(
        "INSERT INTO gastos(fecha,categoria,descripcion,monto,notas,created_at,created_by) VALUES (?,?,?,?,?,?,?)",
        (fecha, categoria, descripcion, float(monto), notas, ts, int(actor_id))
    )

def list_gastos(fecha_inicio: str | None = None, fecha_fin: str | None = None, categoria: str | None = None):
    """Lista gastos con filtros opcionales."""
    conditions = []
    params = []
    
    if fecha_inicio:
        conditions.append("fecha >= ?")
        params.append(fecha_inicio)
    
    if fecha_fin:
        conditions.append("fecha <= ?")
        params.append(fecha_fin)
    
    if categoria:
        conditions.append("categoria = ?")
        params.append(categoria)
    
    where_clause = " AND ".join(conditions) if conditions else "1=1"
    
    sql = f"""
        SELECT g.*, u.nombre AS creador_nombre
        FROM gastos g
        JOIN usuarios u ON u.id = g.created_by
        WHERE {where_clause}
        ORDER BY g.fecha DESC, g.created_at DESC
    """
    
    return fetchall(sql, tuple(params))

def get_gasto_by_id(gasto_id: int) -> dict | None:
    """Obtiene un gasto por ID."""
    return fetchone("SELECT * FROM gastos WHERE id=?", (int(gasto_id),))

def update_gasto(gasto_id: int, fecha: str, categoria: str, descripcion: str, monto: float, notas: str | None):
    """Actualiza un gasto existente."""
    execute(
        "UPDATE gastos SET fecha=?, categoria=?, descripcion=?, monto=?, notas=? WHERE id=?",
        (fecha, categoria, descripcion, float(monto), notas, int(gasto_id))
    )

def delete_gasto(gasto_id: int):
    """Elimina un gasto."""
    execute("DELETE FROM gastos WHERE id=?", (int(gasto_id),))

def get_gastos_summary(fecha_inicio: str | None = None, fecha_fin: str | None = None) -> dict:
    """Obtiene resumen de gastos por categoría."""
    conditions = []
    params = []
    
    if fecha_inicio:
        conditions.append("fecha >= ?")
        params.append(fecha_inicio)
    
    if fecha_fin:
        conditions.append("fecha <= ?")
        params.append(fecha_fin)
    
    where_clause = " AND ".join(conditions) if conditions else "1=1"
    
    # Total por categoría
    sql_cat = f"""
        SELECT 
            categoria,
            COUNT(*) as cantidad,
            SUM(monto) as total
        FROM gastos
        WHERE {where_clause}
        GROUP BY categoria
        ORDER BY total DESC
    """
    
    por_categoria = fetchall(sql_cat, tuple(params))
    
    # Total general
    sql_total = f"""
        SELECT 
            COUNT(*) as total_gastos,
            SUM(monto) as total_monto
        FROM gastos
        WHERE {where_clause}
    """
    
    totales = fetchone(sql_total, tuple(params))
    
    return {
        "por_categoria": por_categoria,
        "totales": totales or {}
    }



def corte_with_cliente_user(corte_id: int):
    return fetchone(
        """
        SELECT c.*, cl.nombre AS cliente_nombre, cl.comision_pct AS cliente_comision_pct,
               u.nombre AS operador_nombre
        FROM cortes c
        JOIN clientes cl ON cl.id=c.cliente_id
        JOIN usuarios u ON u.id=c.created_by
        WHERE c.id=?
        """,
        (int(corte_id),),
    )

def get_cliente(cliente_id: int):
    return fetchone("SELECT * FROM clientes WHERE id=?", (int(cliente_id),))
