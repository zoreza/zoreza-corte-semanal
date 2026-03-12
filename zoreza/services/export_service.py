"""
Servicio de exportación de datos a diferentes formatos (CSV, Excel).
"""
import csv
import io
from datetime import datetime
from typing import Any
from zoreza.services.exceptions import ExportError
from zoreza.db import repo


def export_cortes_to_csv(
    cliente_id: int | None = None,
    fecha_inicio: str | None = None,
    fecha_fin: str | None = None
) -> tuple[str, str]:
    """
    Exporta cortes a formato CSV.
    
    Args:
        cliente_id: Filtrar por cliente (opcional)
        fecha_inicio: Fecha inicio en formato ISO (opcional)
        fecha_fin: Fecha fin en formato ISO (opcional)
        
    Returns:
        Tupla (contenido_csv, nombre_archivo)
        
    Raises:
        ExportError: Si hay error en la exportación
    """
    try:
        # Obtener datos
        cortes = repo.list_cortes_for_export(cliente_id, fecha_inicio, fecha_fin)
        
        if not cortes:
            raise ExportError("No hay datos para exportar con los filtros especificados")
        
        # Crear CSV en memoria
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Encabezados
        headers = [
            "ID Corte",
            "Cliente",
            "Semana Inicio",
            "Semana Fin",
            "Fecha Corte",
            "Estado",
            "Comisión %",
            "Neto Cliente",
            "Pago Cliente",
            "Ganancia Dueño",
            "Creado Por",
            "Fecha Creación"
        ]
        writer.writerow(headers)
        
        # Datos
        for corte in cortes:
            row = [
                corte["id"],
                corte.get("cliente_nombre", ""),
                corte["week_start"],
                corte["week_end"],
                corte["fecha_corte"],
                corte["estado"],
                f"{corte['comision_pct_usada'] * 100:.1f}",
                f"{corte['neto_cliente']:.2f}",
                f"{corte['pago_cliente']:.2f}",
                f"{corte['ganancia_dueno']:.2f}",
                corte.get("creador_nombre", ""),
                corte["created_at"]
            ]
            writer.writerow(row)
        
        # Generar nombre de archivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"cortes_export_{timestamp}.csv"
        
        return output.getvalue(), filename
        
    except Exception as e:
        raise ExportError(f"Error al exportar cortes: {str(e)}")


def export_corte_detalle_to_csv(corte_id: int) -> tuple[str, str]:
    """
    Exporta el detalle de un corte específico a CSV.
    
    Args:
        corte_id: ID del corte
        
    Returns:
        Tupla (contenido_csv, nombre_archivo)
        
    Raises:
        ExportError: Si hay error en la exportación
    """
    try:
        # Obtener corte
        corte = repo.get_corte_by_id(corte_id)
        if not corte:
            raise ExportError(f"Corte {corte_id} no encontrado")
        
        # Obtener detalle
        detalles = repo.list_detalle(corte_id)
        
        if not detalles:
            raise ExportError(f"No hay detalles para el corte {corte_id}")
        
        # Crear CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Encabezados
        headers = [
            "Máquina",
            "Estado",
            "Score Tarjeta",
            "Efectivo Total",
            "Fondo",
            "Recaudable",
            "Diferencia Score",
            "Contador Entrada Actual",
            "Contador Salida Actual",
            "Contador Entrada Previo",
            "Contador Salida Previo",
            "Delta Entrada",
            "Delta Salida",
            "Monto Estimado Contadores",
            "Causa Irregularidad",
            "Nota Irregularidad",
            "Evento Contador",
            "Nota Evento",
            "Motivo Omisión",
            "Nota Omisión"
        ]
        writer.writerow(headers)
        
        # Datos
        for det in detalles:
            row = [
                det.get("maquina_codigo", ""),
                det["estado_maquina"],
                det.get("score_tarjeta", ""),
                det.get("efectivo_total", ""),
                det.get("fondo", ""),
                det.get("recaudable", ""),
                det.get("diferencia_score", ""),
                det.get("contador_entrada_actual", ""),
                det.get("contador_salida_actual", ""),
                det.get("contador_entrada_prev", ""),
                det.get("contador_salida_prev", ""),
                det.get("delta_entrada", ""),
                det.get("delta_salida", ""),
                det.get("monto_estimado_contadores", ""),
                det.get("causa_irregularidad_nombre", ""),
                det.get("nota_irregularidad", ""),
                det.get("evento_contador_nombre", ""),
                det.get("nota_evento_contador", ""),
                det.get("motivo_omision_nombre", ""),
                det.get("nota_omision", "")
            ]
            writer.writerow(row)
        
        # Nombre de archivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"corte_{corte_id}_detalle_{timestamp}.csv"
        
        return output.getvalue(), filename
        
    except Exception as e:
        raise ExportError(f"Error al exportar detalle del corte: {str(e)}")


def export_maquinas_to_csv() -> tuple[str, str]:
    """
    Exporta todas las máquinas a CSV.
    
    Returns:
        Tupla (contenido_csv, nombre_archivo)
    """
    try:
        maquinas = repo.list_maquinas()
        
        if not maquinas:
            raise ExportError("No hay máquinas para exportar")
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        headers = ["ID", "Código", "Cliente", "Activo", "Fecha Creación"]
        writer.writerow(headers)
        
        for maq in maquinas:
            row = [
                maq["id"],
                maq["codigo"],
                maq.get("cliente_nombre", ""),
                "Sí" if maq["activo"] else "No",
                maq["created_at"]
            ]
            writer.writerow(row)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"maquinas_export_{timestamp}.csv"
        
        return output.getvalue(), filename
        
    except Exception as e:
        raise ExportError(f"Error al exportar máquinas: {str(e)}")


def export_clientes_to_csv() -> tuple[str, str]:
    """
    Exporta todos los clientes a CSV.
    
    Returns:
        Tupla (contenido_csv, nombre_archivo)
    """
    try:
        clientes = repo.list_clientes()
        
        if not clientes:
            raise ExportError("No hay clientes para exportar")
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        headers = ["ID", "Nombre", "Comisión %", "Activo", "Fecha Creación"]
        writer.writerow(headers)
        
        for cli in clientes:
            row = [
                cli["id"],
                cli["nombre"],
                f"{cli['comision_pct'] * 100:.1f}",
                "Sí" if cli["activo"] else "No",
                cli["created_at"]
            ]
            writer.writerow(row)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"clientes_export_{timestamp}.csv"
        
        return output.getvalue(), filename
        
    except Exception as e:
        raise ExportError(f"Error al exportar clientes: {str(e)}")

# Made with Bob
