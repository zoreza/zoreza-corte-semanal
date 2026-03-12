from zoreza.db.queries import fetchall

def is_supervisor(user: dict) -> bool:
    return user["rol"] in ("ADMIN", "SUPERVISOR")

def allowed_ruta_ids(user: dict) -> list[int]:
    if is_supervisor(user):
        rows = fetchall("SELECT id FROM rutas WHERE activo=1")
        return [r["id"] for r in rows]
    rows = fetchall("SELECT ruta_id FROM usuario_ruta WHERE usuario_id=? AND activo=1", (user["id"],))
    return [r["ruta_id"] for r in rows]

def allowed_clientes(user: dict) -> list[dict]:
    if is_supervisor(user):
        return fetchall("SELECT * FROM clientes WHERE activo=1 ORDER BY nombre")
    ruta_ids = allowed_ruta_ids(user)
    if not ruta_ids:
        return []
    placeholders = ",".join(["?"]*len(ruta_ids))
    sql = f"""
    SELECT DISTINCT c.*
    FROM clientes c
    JOIN maquinas m ON m.cliente_id=c.id AND m.activo=1
    JOIN maquina_ruta mr ON mr.maquina_id=m.id AND mr.activo=1
    WHERE c.activo=1 AND mr.ruta_id IN ({placeholders})
    ORDER BY c.nombre
    """
    return fetchall(sql, tuple(ruta_ids))

def allowed_maquinas_for_cliente(user: dict, cliente_id: int) -> list[dict]:
    if is_supervisor(user):
        return fetchall("SELECT * FROM maquinas WHERE activo=1 AND cliente_id=? ORDER BY codigo", (cliente_id,))
    ruta_ids = allowed_ruta_ids(user)
    if not ruta_ids:
        return []
    placeholders = ",".join(["?"]*len(ruta_ids))
    sql = f"""
    SELECT DISTINCT m.*
    FROM maquinas m
    JOIN maquina_ruta mr ON mr.maquina_id=m.id AND mr.activo=1
    WHERE m.activo=1 AND m.cliente_id=? AND mr.ruta_id IN ({placeholders})
    ORDER BY m.codigo
    """
    return fetchall(sql, (cliente_id, *ruta_ids))
