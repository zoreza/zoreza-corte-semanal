"""
Servicio de dashboard con métricas y estadísticas del negocio.
"""
from datetime import datetime, date, timedelta
from typing import Any
from zoreza.db.queries import fetchall, fetchone


def get_dashboard_summary(
    fecha_inicio: date | None = None,
    fecha_fin: date | None = None
) -> dict[str, Any]:
    """
    Obtiene resumen general para el dashboard.
    
    Args:
        fecha_inicio: Fecha inicio del período (default: último mes)
        fecha_fin: Fecha fin del período (default: hoy)
        
    Returns:
        Diccionario con métricas principales
    """
    if not fecha_fin:
        fecha_fin = date.today()
    
    if not fecha_inicio:
        fecha_inicio = fecha_fin - timedelta(days=30)
    
    # Totales del período
    totales = fetchone("""
        SELECT 
            COUNT(*) as total_cortes,
            SUM(CASE WHEN estado = 'CERRADO' THEN 1 ELSE 0 END) as cortes_cerrados,
            SUM(neto_cliente) as total_neto,
            SUM(pago_cliente) as total_pago_cliente,
            SUM(ganancia_dueno) as total_ganancia_dueno,
            AVG(neto_cliente) as promedio_neto
        FROM cortes
        WHERE fecha_corte BETWEEN ? AND ?
    """, (fecha_inicio.isoformat(), fecha_fin.isoformat()))
    
    # Top clientes
    top_clientes = fetchall("""
        SELECT 
            cl.nombre,
            COUNT(c.id) as num_cortes,
            SUM(c.neto_cliente) as total_neto,
            AVG(c.neto_cliente) as promedio_neto
        FROM cortes c
        JOIN clientes cl ON cl.id = c.cliente_id
        WHERE c.fecha_corte BETWEEN ? AND ? AND c.estado = 'CERRADO'
        GROUP BY cl.id, cl.nombre
        ORDER BY total_neto DESC
        LIMIT 5
    """, (fecha_inicio.isoformat(), fecha_fin.isoformat()))
    
    # Irregularidades
    irregularidades = fetchone("""
        SELECT 
            COUNT(*) as total_irregularidades,
            COUNT(DISTINCT cd.corte_id) as cortes_con_irregularidades
        FROM corte_detalle cd
        JOIN cortes c ON c.id = cd.corte_id
        WHERE cd.causa_irregularidad_id IS NOT NULL
        AND c.fecha_corte BETWEEN ? AND ?
    """, (fecha_inicio.isoformat(), fecha_fin.isoformat()))
    
    # Máquinas omitidas
    omisiones = fetchone("""
        SELECT 
            COUNT(*) as total_omisiones,
            COUNT(DISTINCT cd.maquina_id) as maquinas_omitidas
        FROM corte_detalle cd
        JOIN cortes c ON c.id = cd.corte_id
        WHERE cd.estado_maquina = 'OMITIDA'
        AND c.fecha_corte BETWEEN ? AND ?
    """, (fecha_inicio.isoformat(), fecha_fin.isoformat()))
    
    return {
        "periodo": {
            "inicio": fecha_inicio.isoformat(),
            "fin": fecha_fin.isoformat()
        },
        "totales": totales or {},
        "top_clientes": top_clientes,
        "irregularidades": irregularidades or {},
        "omisiones": omisiones or {}
    }


def get_revenue_trend(days: int = 30) -> list[dict]:
    """
    Obtiene tendencia de ingresos por día.
    
    Args:
        days: Número de días hacia atrás
        
    Returns:
        Lista de datos por día
    """
    fecha_fin = date.today()
    fecha_inicio = fecha_fin - timedelta(days=days)
    
    return fetchall("""
        SELECT 
            fecha_corte,
            COUNT(*) as num_cortes,
            SUM(neto_cliente) as total_neto,
            SUM(ganancia_dueno) as total_ganancia
        FROM cortes
        WHERE fecha_corte BETWEEN ? AND ?
        AND estado = 'CERRADO'
        GROUP BY fecha_corte
        ORDER BY fecha_corte
    """, (fecha_inicio.isoformat(), fecha_fin.isoformat()))


def get_client_performance(cliente_id: int, months: int = 6) -> dict:
    """
    Obtiene rendimiento histórico de un cliente.
    
    Args:
        cliente_id: ID del cliente
        months: Meses hacia atrás
        
    Returns:
        Diccionario con métricas del cliente
    """
    fecha_fin = date.today()
    fecha_inicio = fecha_fin - timedelta(days=months * 30)
    
    # Resumen general
    resumen = fetchone("""
        SELECT 
            COUNT(*) as total_cortes,
            SUM(neto_cliente) as total_neto,
            AVG(neto_cliente) as promedio_neto,
            MAX(neto_cliente) as max_neto,
            MIN(neto_cliente) as min_neto
        FROM cortes
        WHERE cliente_id = ?
        AND fecha_corte BETWEEN ? AND ?
        AND estado = 'CERRADO'
    """, (cliente_id, fecha_inicio.isoformat(), fecha_fin.isoformat()))
    
    # Tendencia mensual
    tendencia = fetchall("""
        SELECT 
            strftime('%Y-%m', fecha_corte) as mes,
            COUNT(*) as num_cortes,
            SUM(neto_cliente) as total_neto,
            AVG(neto_cliente) as promedio_neto
        FROM cortes
        WHERE cliente_id = ?
        AND fecha_corte BETWEEN ? AND ?
        AND estado = 'CERRADO'
        GROUP BY mes
        ORDER BY mes
    """, (cliente_id, fecha_inicio.isoformat(), fecha_fin.isoformat()))
    
    # Máquinas del cliente
    maquinas = fetchone("""
        SELECT 
            COUNT(*) as total_maquinas,
            SUM(CASE WHEN activo = 1 THEN 1 ELSE 0 END) as maquinas_activas
        FROM maquinas
        WHERE cliente_id = ?
    """, (cliente_id,))
    
    return {
        "resumen": resumen or {},
        "tendencia_mensual": tendencia,
        "maquinas": maquinas or {}
    }


def get_machine_performance(maquina_id: int, limit: int = 10) -> dict:
    """
    Obtiene rendimiento de una máquina específica.
    
    Args:
        maquina_id: ID de la máquina
        limit: Número de cortes recientes a analizar
        
    Returns:
        Diccionario con métricas de la máquina
    """
    # Últimos cortes
    ultimos_cortes = fetchall("""
        SELECT 
            c.fecha_corte,
            c.week_start,
            cd.estado_maquina,
            cd.recaudable,
            cd.diferencia_score,
            cd.causa_irregularidad_id,
            ci.nombre as causa_nombre
        FROM corte_detalle cd
        JOIN cortes c ON c.id = cd.corte_id
        LEFT JOIN cat_irregularidad ci ON ci.id = cd.causa_irregularidad_id
        WHERE cd.maquina_id = ?
        AND c.estado = 'CERRADO'
        ORDER BY c.week_start DESC
        LIMIT ?
    """, (maquina_id, limit))
    
    # Estadísticas generales
    stats = fetchone("""
        SELECT 
            COUNT(*) as total_cortes,
            SUM(CASE WHEN cd.estado_maquina = 'CAPTURADA' THEN 1 ELSE 0 END) as veces_capturada,
            SUM(CASE WHEN cd.estado_maquina = 'OMITIDA' THEN 1 ELSE 0 END) as veces_omitida,
            AVG(cd.recaudable) as promedio_recaudable,
            SUM(cd.recaudable) as total_recaudable,
            COUNT(cd.causa_irregularidad_id) as num_irregularidades
        FROM corte_detalle cd
        JOIN cortes c ON c.id = cd.corte_id
        WHERE cd.maquina_id = ?
        AND c.estado = 'CERRADO'
    """, (maquina_id,))
    
    return {
        "ultimos_cortes": ultimos_cortes,
        "estadisticas": stats or {}
    }


def get_irregularities_report(
    fecha_inicio: date | None = None,
    fecha_fin: date | None = None
) -> dict:
    """
    Genera reporte de irregularidades.
    
    Args:
        fecha_inicio: Fecha inicio
        fecha_fin: Fecha fin
        
    Returns:
        Diccionario con análisis de irregularidades
    """
    if not fecha_fin:
        fecha_fin = date.today()
    
    if not fecha_inicio:
        fecha_inicio = fecha_fin - timedelta(days=30)
    
    # Por tipo de causa
    por_causa = fetchall("""
        SELECT 
            ci.nombre as causa,
            COUNT(*) as cantidad,
            AVG(ABS(cd.diferencia_score)) as promedio_diferencia,
            SUM(ABS(cd.diferencia_score)) as total_diferencia
        FROM corte_detalle cd
        JOIN cortes c ON c.id = cd.corte_id
        JOIN cat_irregularidad ci ON ci.id = cd.causa_irregularidad_id
        WHERE c.fecha_corte BETWEEN ? AND ?
        AND cd.causa_irregularidad_id IS NOT NULL
        GROUP BY ci.id, ci.nombre
        ORDER BY cantidad DESC
    """, (fecha_inicio.isoformat(), fecha_fin.isoformat()))
    
    # Máquinas con más irregularidades
    maquinas_problematicas = fetchall("""
        SELECT 
            m.codigo,
            cl.nombre as cliente,
            COUNT(*) as num_irregularidades,
            AVG(ABS(cd.diferencia_score)) as promedio_diferencia
        FROM corte_detalle cd
        JOIN cortes c ON c.id = cd.corte_id
        JOIN maquinas m ON m.id = cd.maquina_id
        JOIN clientes cl ON cl.id = m.cliente_id
        WHERE c.fecha_corte BETWEEN ? AND ?
        AND cd.causa_irregularidad_id IS NOT NULL
        GROUP BY m.id, m.codigo, cl.nombre
        HAVING num_irregularidades > 1
        ORDER BY num_irregularidades DESC
        LIMIT 10
    """, (fecha_inicio.isoformat(), fecha_fin.isoformat()))
    
    return {
        "periodo": {
            "inicio": fecha_inicio.isoformat(),
            "fin": fecha_fin.isoformat()
        },
        "por_causa": por_causa,
        "maquinas_problematicas": maquinas_problematicas
    }


def get_operator_performance(
    fecha_inicio: date | None = None,
    fecha_fin: date | None = None
) -> list[dict]:
    """
    Obtiene rendimiento de operadores.
    
    Args:
        fecha_inicio: Fecha inicio
        fecha_fin: Fecha fin
        
    Returns:
        Lista de métricas por operador
    """
    if not fecha_fin:
        fecha_fin = date.today()
    
    if not fecha_inicio:
        fecha_inicio = fecha_fin - timedelta(days=30)
    
    return fetchall("""
        SELECT 
            u.nombre as operador,
            COUNT(DISTINCT c.id) as num_cortes,
            COUNT(DISTINCT c.cliente_id) as num_clientes,
            SUM(c.neto_cliente) as total_procesado,
            AVG(c.neto_cliente) as promedio_por_corte
        FROM cortes c
        JOIN usuarios u ON u.id = c.created_by
        WHERE c.fecha_corte BETWEEN ? AND ?
        AND c.estado = 'CERRADO'
        GROUP BY u.id, u.nombre
        ORDER BY total_procesado DESC
    """, (fecha_inicio.isoformat(), fecha_fin.isoformat()))

# Made with Bob
