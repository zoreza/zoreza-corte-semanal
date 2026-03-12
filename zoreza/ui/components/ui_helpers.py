"""
Componentes y helpers para mejorar la UI con feedback visual y confirmaciones.
"""
import streamlit as st
from typing import Callable, Any


def show_success_message(message: str, icon: str = "✅"):
    """Muestra mensaje de éxito con estilo consistente."""
    st.success(f"{icon} {message}")


def show_error_message(message: str, icon: str = "❌"):
    """Muestra mensaje de error con estilo consistente."""
    st.error(f"{icon} {message}")


def show_warning_message(message: str, icon: str = "⚠️"):
    """Muestra mensaje de advertencia con estilo consistente."""
    st.warning(f"{icon} {message}")


def show_info_message(message: str, icon: str = "ℹ️"):
    """Muestra mensaje informativo con estilo consistente."""
    st.info(f"{icon} {message}")


def confirm_action(
    message: str,
    confirm_text: str = "Confirmar",
    cancel_text: str = "Cancelar",
    key: str | None = None
) -> bool:
    """
    Muestra diálogo de confirmación para acciones importantes.
    
    Args:
        message: Mensaje de confirmación
        confirm_text: Texto del botón de confirmar
        cancel_text: Texto del botón de cancelar
        key: Key única para el componente
        
    Returns:
        True si el usuario confirmó, False si canceló
    """
    st.warning(f"⚠️ {message}")
    
    col1, col2, col3 = st.columns([1, 1, 3])
    
    with col1:
        if st.button(confirm_text, key=f"{key}_confirm" if key else None, type="primary"):
            return True
    
    with col2:
        if st.button(cancel_text, key=f"{key}_cancel" if key else None):
            return False
    
    return False


def show_loading(message: str = "Procesando..."):
    """Muestra indicador de carga."""
    return st.spinner(message)


def create_metric_card(label: str, value: str | float, delta: str | None = None, help_text: str | None = None):
    """
    Crea una tarjeta de métrica con estilo consistente.
    
    Args:
        label: Etiqueta de la métrica
        value: Valor a mostrar
        delta: Cambio o diferencia (opcional)
        help_text: Texto de ayuda (opcional)
    """
    st.metric(label=label, value=value, delta=delta, help=help_text)


def create_status_badge(status: str, color_map: dict[str, str] | None = None) -> str:
    """
    Crea un badge de estado con color.
    
    Args:
        status: Estado a mostrar
        color_map: Mapeo de estados a colores (opcional)
        
    Returns:
        HTML del badge
    """
    default_colors = {
        "CERRADO": "green",
        "BORRADOR": "orange",
        "ACTIVO": "green",
        "INACTIVO": "red",
        "CAPTURADA": "blue",
        "OMITIDA": "gray"
    }
    
    colors = color_map or default_colors
    color = colors.get(status, "gray")
    
    return f'<span style="background-color: {color}; color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px;">{status}</span>'


def show_progress_bar(current: int, total: int, label: str = "Progreso"):
    """
    Muestra barra de progreso.
    
    Args:
        current: Valor actual
        total: Valor total
        label: Etiqueta
    """
    if total > 0:
        progress = current / total
        st.progress(progress, text=f"{label}: {current}/{total} ({progress*100:.0f}%)")
    else:
        st.progress(0, text=f"{label}: 0/0")


def create_data_table(data: list[dict], columns: list[str] | None = None):
    """
    Crea tabla de datos con estilo mejorado.
    
    Args:
        data: Lista de diccionarios con datos
        columns: Columnas a mostrar (None = todas)
    """
    if not data:
        st.info("No hay datos para mostrar")
        return
    
    import pandas as pd
    df = pd.DataFrame(data)
    
    if columns:
        df = df[columns]
    
    st.dataframe(df, use_container_width=True, hide_index=True)


def create_download_button(
    data: str | bytes,
    filename: str,
    label: str = "Descargar",
    mime: str = "text/csv",
    key: str | None = None
):
    """
    Crea botón de descarga con estilo consistente.
    
    Args:
        data: Datos a descargar
        filename: Nombre del archivo
        label: Texto del botón
        mime: Tipo MIME
        key: Key única
    """
    st.download_button(
        label=f"📥 {label}",
        data=data,
        file_name=filename,
        mime=mime,
        key=key
    )


def show_notification_badge(count: int):
    """
    Muestra badge de notificaciones no leídas.
    
    Args:
        count: Número de notificaciones
    """
    if count > 0:
        st.markdown(
            f'<span style="background-color: red; color: white; padding: 2px 6px; '
            f'border-radius: 10px; font-size: 11px; font-weight: bold;">{count}</span>',
            unsafe_allow_html=True
        )


def create_collapsible_section(title: str, content_func: Callable, expanded: bool = False):
    """
    Crea sección colapsable.
    
    Args:
        title: Título de la sección
        content_func: Función que renderiza el contenido
        expanded: Si debe estar expandida por defecto
    """
    with st.expander(title, expanded=expanded):
        content_func()


def show_empty_state(message: str, icon: str = "📭"):
    """
    Muestra estado vacío cuando no hay datos.
    
    Args:
        message: Mensaje a mostrar
        icon: Icono
    """
    st.markdown(
        f"""
        <div style="text-align: center; padding: 40px; color: #666;">
            <div style="font-size: 48px; margin-bottom: 16px;">{icon}</div>
            <div style="font-size: 16px;">{message}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def create_action_buttons(actions: list[tuple[str, Callable, str]], key_prefix: str = ""):
    """
    Crea grupo de botones de acción.
    
    Args:
        actions: Lista de tuplas (label, callback, type)
        key_prefix: Prefijo para las keys
    """
    from typing import Literal
    cols = st.columns(len(actions))
    
    for idx, (label, callback, btn_type) in enumerate(actions):
        with cols[idx]:
            # Validar tipo de botón
            valid_type: Literal["primary", "secondary", "tertiary"] = "secondary"
            if btn_type in ("primary", "secondary", "tertiary"):
                valid_type = btn_type  # type: ignore
            
            if st.button(label, key=f"{key_prefix}_btn_{idx}", type=valid_type):
                callback()


def show_validation_errors(errors: list[tuple[str, str]]):
    """
    Muestra errores de validación de forma clara.
    
    Args:
        errors: Lista de tuplas (campo, mensaje)
    """
    if not errors:
        return
    
    st.error("❌ Se encontraron los siguientes errores:")
    for field, message in errors:
        st.markdown(f"- **{field}**: {message}")


def create_filter_panel(filters: dict[str, Any]) -> dict[str, Any]:
    """
    Crea panel de filtros reutilizable.
    
    Args:
        filters: Diccionario con configuración de filtros
        
    Returns:
        Diccionario con valores seleccionados
    """
    st.subheader("🔍 Filtros")
    
    selected = {}
    
    for key, config in filters.items():
        filter_type = config.get("type", "text")
        label = config.get("label", key)
        
        if filter_type == "text":
            selected[key] = st.text_input(label, value=config.get("default", ""))
        elif filter_type == "select":
            options = config.get("options", [])
            selected[key] = st.selectbox(label, options)
        elif filter_type == "date":
            selected[key] = st.date_input(label, value=config.get("default"))
        elif filter_type == "number":
            selected[key] = st.number_input(
                label,
                min_value=config.get("min", 0),
                max_value=config.get("max", 1000000),
                value=config.get("default", 0)
            )
    
    return selected


def show_confirmation_dialog(
    title: str,
    message: str,
    on_confirm: Callable,
    on_cancel: Callable | None = None,
    confirm_text: str = "Confirmar",
    cancel_text: str = "Cancelar"
):
    """
    Muestra diálogo modal de confirmación.
    
    Args:
        title: Título del diálogo
        message: Mensaje de confirmación
        on_confirm: Callback al confirmar
        on_cancel: Callback al cancelar (opcional)
        confirm_text: Texto del botón confirmar
        cancel_text: Texto del botón cancelar
    """
    with st.container():
        st.markdown(f"### {title}")
        st.warning(message)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button(confirm_text, type="primary", use_container_width=True):
                on_confirm()
        
        with col2:
            if st.button(cancel_text, use_container_width=True):
                if on_cancel:
                    on_cancel()

# Made with Bob
