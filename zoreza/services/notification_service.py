"""
Servicio de notificaciones para irregularidades y eventos importantes.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Literal
from zoreza.db import repo


NotificationType = Literal["irregularidad", "omision", "evento_contador", "corte_cerrado", "edicion_corte"]
NotificationPriority = Literal["baja", "media", "alta", "critica"]


@dataclass
class Notification:
    """Representa una notificación del sistema."""
    id: int | None
    type: NotificationType
    priority: NotificationPriority
    title: str
    message: str
    corte_id: int | None
    maquina_id: int | None
    user_id: int | None
    read: bool
    created_at: str


def create_irregularidad_notification(
    corte_id: int,
    maquina_id: int,
    causa: str,
    diferencia: float,
    user_id: int
) -> None:
    """
    Crea notificación por irregularidad detectada.
    
    Args:
        corte_id: ID del corte
        maquina_id: ID de la máquina
        causa: Causa de la irregularidad
        diferencia: Diferencia en pesos
        user_id: Usuario que detectó
    """
    priority: NotificationPriority = "alta" if abs(diferencia) > 1000 else "media"
    
    title = f"Irregularidad detectada: {causa}"
    message = f"Diferencia de ${abs(diferencia):.2f} en máquina ID {maquina_id}"
    
    _save_notification("irregularidad", priority, title, message, corte_id, maquina_id, user_id)


def create_omision_notification(
    corte_id: int,
    maquina_id: int,
    motivo: str,
    user_id: int
) -> None:
    """
    Crea notificación por máquina omitida.
    
    Args:
        corte_id: ID del corte
        maquina_id: ID de la máquina
        motivo: Motivo de omisión
        user_id: Usuario que omitió
    """
    title = f"Máquina omitida: {motivo}"
    message = f"Máquina ID {maquina_id} no fue capturada"
    
    _save_notification("omision", "baja", title, message, corte_id, maquina_id, user_id)


def create_evento_contador_notification(
    corte_id: int,
    maquina_id: int,
    evento: str,
    user_id: int
) -> None:
    """
    Crea notificación por evento en contador.
    
    Args:
        corte_id: ID del corte
        maquina_id: ID de la máquina
        evento: Tipo de evento
        user_id: Usuario que reportó
    """
    priority: NotificationPriority = "alta" if "reset" in evento.lower() else "media"
    
    title = f"Evento en contador: {evento}"
    message = f"Evento detectado en máquina ID {maquina_id}"
    
    _save_notification("evento_contador", priority, title, message, corte_id, maquina_id, user_id)


def create_corte_cerrado_notification(
    corte_id: int,
    cliente_nombre: str,
    neto_cliente: float,
    user_id: int
) -> None:
    """
    Crea notificación cuando se cierra un corte.
    
    Args:
        corte_id: ID del corte
        cliente_nombre: Nombre del cliente
        neto_cliente: Neto del cliente
        user_id: Usuario que cerró
    """
    title = f"Corte cerrado: {cliente_nombre}"
    message = f"Neto cliente: ${neto_cliente:,.2f}"
    
    _save_notification("corte_cerrado", "media", title, message, corte_id, None, user_id)


def create_edicion_corte_notification(
    corte_id: int,
    reason: str,
    user_id: int
) -> None:
    """
    Crea notificación cuando se edita un corte cerrado.
    
    Args:
        corte_id: ID del corte
        reason: Razón de la edición
        user_id: Usuario que editó
    """
    title = "Corte cerrado editado"
    message = f"Corte ID {corte_id} fue editado. Razón: {reason}"
    
    _save_notification("edicion_corte", "alta", title, message, corte_id, None, user_id)


def get_unread_notifications(user_id: int | None = None, limit: int = 50) -> list[Notification]:
    """
    Obtiene notificaciones no leídas.
    
    Args:
        user_id: Filtrar por usuario (None = todas)
        limit: Límite de resultados
        
    Returns:
        Lista de notificaciones
    """
    notifications = repo.get_notifications(user_id, read=False, limit=limit)
    return [_dict_to_notification(n) for n in notifications]


def get_all_notifications(user_id: int | None = None, limit: int = 100) -> list[Notification]:
    """
    Obtiene todas las notificaciones.
    
    Args:
        user_id: Filtrar por usuario (None = todas)
        limit: Límite de resultados
        
    Returns:
        Lista de notificaciones
    """
    notifications = repo.get_notifications(user_id, read=None, limit=limit)
    return [_dict_to_notification(n) for n in notifications]


def mark_as_read(notification_id: int) -> None:
    """Marca una notificación como leída."""
    repo.mark_notification_read(notification_id)


def mark_all_as_read(user_id: int | None = None) -> None:
    """Marca todas las notificaciones como leídas."""
    repo.mark_all_notifications_read(user_id)


def get_notification_count(user_id: int | None = None, unread_only: bool = True) -> int:
    """
    Obtiene el conteo de notificaciones.
    
    Args:
        user_id: Filtrar por usuario
        unread_only: Solo contar no leídas
        
    Returns:
        Número de notificaciones
    """
    return repo.count_notifications(user_id, unread_only)


def delete_old_notifications(days: int = 30) -> int:
    """
    Elimina notificaciones antiguas.
    
    Args:
        days: Días de antigüedad
        
    Returns:
        Número de notificaciones eliminadas
    """
    return repo.delete_old_notifications(days)


def _save_notification(
    type: NotificationType,
    priority: NotificationPriority,
    title: str,
    message: str,
    corte_id: int | None,
    maquina_id: int | None,
    user_id: int | None
) -> None:
    """Guarda una notificación en la base de datos."""
    repo.create_notification(type, priority, title, message, corte_id, maquina_id, user_id)


def _dict_to_notification(data: dict) -> Notification:
    """Convierte un diccionario a objeto Notification."""
    return Notification(
        id=data["id"],
        type=data["type"],
        priority=data["priority"],
        title=data["title"],
        message=data["message"],
        corte_id=data.get("corte_id"),
        maquina_id=data.get("maquina_id"),
        user_id=data.get("user_id"),
        read=bool(data["read"]),
        created_at=data["created_at"]
    )

# Made with Bob
