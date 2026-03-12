"""
Servicio de búsqueda y filtros avanzados para historial.
"""
from datetime import datetime, date
from typing import Any
from zoreza.db.queries import fetchall


def search_cortes(
    cliente_id: int | None = None,
    estado: str | None = None,
    fecha_inicio: date | None = None,
    fecha_fin: date | None = None,
    min_neto: float | None = None,
    max_neto: float | None = None,
    operador_id: int | None = None,
    search_text: str | None = None,
    order_by: str = "week_start",
    order_dir: str = "DESC",
    limit: int = 100,
    offset: int = 0
) -> list[dict]:
    """
    Búsqueda avanzada de cortes con múltiples filtros.
    
    Args:
        cliente_id: Filtrar por cliente
        estado: Filtrar por estado (BORRADOR/CERRADO)
        fecha_inicio: Fecha inicio del rango
        fecha_fin: Fecha fin del rango
        min_neto: Neto mínimo
        max_neto: Neto máximo
        operador_id: Filtrar por operador que creó
        search_text: Búsqueda de texto en nombre de cliente
        order_by: Campo para ordenar
        order_dir: Dirección (ASC/DESC)
        limit: Límite de resultados
        offset: Offset para paginación
        
    Returns:
        Lista de cortes que cumplen los criterios
    """
    conditions = []
    params: list[Any] = []
    
    # Filtros
    if cliente_id:
        conditions.append("c.cliente_id = ?")
        params.append(int(cliente_id))
    
    if estado:
        conditions.append("c.estado = ?")
        params.append(estado.upper())
    
    if fecha_inicio:
        conditions.append("c.fecha_corte >= ?")
        params.append(fecha_inicio.isoformat())
    
    if fecha_fin:
        conditions.append("c.fecha_corte <= ?")
        params.append(fecha_fin.isoformat())
    
    if min_neto is not None:
        conditions.append("c.neto_cliente >= ?")
        params.append(float(min_neto))
    
    if max_neto is not None:
        conditions.append("c.neto_cliente <= ?")
        params.append(float(max_neto))
    
    if operador_id:
        conditions.append("c.created_by = ?")
        params.append(int(operador_id))
    
    if search_text:
        conditions.append("cl.nombre LIKE ?")
        params.append(f"%{search_text}%")
    
    where_clause = " AND ".join(conditions) if conditions else "1=1"
    
    # Validar order_by para prevenir SQL injection
    valid_order_fields = ["week_start", "fecha_corte", "neto_cliente", "estado", "cliente_nombre"]
    if order_by not in valid_order_fields:
        order_by = "week_start"
    
    if order_dir.upper() not in ["ASC", "DESC"]:
        order_dir = "DESC"
    
    sql = f"""
        SELECT 
            c.id,
            c.cliente_id,
            c.week_start,
            c.week_end,
            c.fecha_corte,
            c.estado,
            c.comision_pct_usada,
            c.neto_cliente,
            c.pago_cliente,
            c.ganancia_dueno,
            c.created_at,
            cl.nombre AS cliente_nombre,
            u.nombre AS operador_nombre,
            u.id AS operador_id
        FROM cortes c
        JOIN clientes cl ON cl.id = c.cliente_id
        JOIN usuarios u ON u.id = c.created_by
        WHERE {where_clause}
        ORDER BY c.{order_by} {order_dir}
        LIMIT ? OFFSET ?
    """
    
    params.extend([limit, offset])
    
    return fetchall(sql, tuple(params))


def count_cortes(
    cliente_id: int | None = None,
    estado: str | None = None,
    fecha_inicio: date | None = None,
    fecha_fin: date | None = None,
    min_neto: float | None = None,
    max_neto: float | None = None,
    operador_id: int | None = None,
    search_text: str | None = None
) -> int:
    """
    Cuenta cortes que cumplen los criterios de búsqueda.
    
    Args:
        Mismos parámetros que search_cortes (sin paginación)
        
    Returns:
        Número de cortes
    """
    conditions = []
    params: list[Any] = []
    
    if cliente_id:
        conditions.append("c.cliente_id = ?")
        params.append(int(cliente_id))
    
    if estado:
        conditions.append("c.estado = ?")
        params.append(estado.upper())
    
    if fecha_inicio:
        conditions.append("c.fecha_corte >= ?")
        params.append(fecha_inicio.isoformat())
    
    if fecha_fin:
        conditions.append("c.fecha_corte <= ?")
        params.append(fecha_fin.isoformat())
    
    if min_neto is not None:
        conditions.append("c.neto_cliente >= ?")
        params.append(float(min_neto))
    
    if max_neto is not None:
        conditions.append("c.neto_cliente <= ?")
        params.append(float(max_neto))
    
    if operador_id:
        conditions.append("c.created_by = ?")
        params.append(int(operador_id))
    
    if search_text:
        conditions.append("cl.nombre LIKE ?")
        params.append(f"%{search_text}%")
    
    where_clause = " AND ".join(conditions) if conditions else "1=1"
    
    sql = f"""
        SELECT COUNT(*) as count
        FROM cortes c
        JOIN clientes cl ON cl.id = c.cliente_id
        WHERE {where_clause}
    """
    
    result = fetchall(sql, tuple(params))
    return result[0]["count"] if result else 0


def search_maquinas(
    cliente_id: int | None = None,
    codigo: str | None = None,
    activo: bool | None = None,
    ruta_id: int | None = None
) -> list[dict]:
    """
    Búsqueda de máquinas con filtros.
    
    Args:
        cliente_id: Filtrar por cliente
        codigo: Búsqueda parcial en código
        activo: Filtrar por estado activo
        ruta_id: Filtrar por ruta
        
    Returns:
        Lista de máquinas
    """
    conditions = []
    params: list[Any] = []
    
    if cliente_id:
        conditions.append("m.cliente_id = ?")
        params.append(int(cliente_id))
    
    if codigo:
        conditions.append("m.codigo LIKE ?")
        params.append(f"%{codigo}%")
    
    if activo is not None:
        conditions.append("m.activo = ?")
        params.append(1 if activo else 0)
    
    if ruta_id:
        conditions.append("EXISTS (SELECT 1 FROM maquina_ruta mr WHERE mr.maquina_id = m.id AND mr.ruta_id = ? AND mr.activo = 1)")
        params.append(int(ruta_id))
    
    where_clause = " AND ".join(conditions) if conditions else "1=1"
    
    sql = f"""
        SELECT 
            m.*,
            c.nombre AS cliente_nombre
        FROM maquinas m
        JOIN clientes c ON c.id = m.cliente_id
        WHERE {where_clause}
        ORDER BY c.nombre, m.codigo
    """
    
    return fetchall(sql, tuple(params))


def get_corte_statistics(
    cliente_id: int | None = None,
    fecha_inicio: date | None = None,
    fecha_fin: date | None = None
) -> dict:
    """
    Obtiene estadísticas de cortes.
    
    Args:
        cliente_id: Filtrar por cliente
        fecha_inicio: Fecha inicio
        fecha_fin: Fecha fin
        
    Returns:
        Diccionario con estadísticas
    """
    conditions = []
    params: list[Any] = []
    
    if cliente_id:
        conditions.append("cliente_id = ?")
        params.append(int(cliente_id))
    
    if fecha_inicio:
        conditions.append("fecha_corte >= ?")
        params.append(fecha_inicio.isoformat())
    
    if fecha_fin:
        conditions.append("fecha_corte <= ?")
        params.append(fecha_fin.isoformat())
    
    where_clause = " AND ".join(conditions) if conditions else "1=1"
    
    sql = f"""
        SELECT 
            COUNT(*) as total_cortes,
            SUM(CASE WHEN estado = 'CERRADO' THEN 1 ELSE 0 END) as cortes_cerrados,
            SUM(CASE WHEN estado = 'BORRADOR' THEN 1 ELSE 0 END) as cortes_borrador,
            SUM(neto_cliente) as total_neto,
            AVG(neto_cliente) as promedio_neto,
            MAX(neto_cliente) as max_neto,
            MIN(neto_cliente) as min_neto,
            SUM(pago_cliente) as total_pago_cliente,
            SUM(ganancia_dueno) as total_ganancia_dueno
        FROM cortes
        WHERE {where_clause}
    """
    
    result = fetchall(sql, tuple(params))
    return result[0] if result else {}

# Made with Bob
