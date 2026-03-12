import streamlit as st
from datetime import datetime, timedelta
from zoreza.db.repo import (
    list_cortes_for_export,
    get_gastos_summary,
    list_gastos
)
import pandas as pd

def page_dashboard(user):
    """Dashboard principal para ADMIN con métricas y gráficas"""
    
    st.title("🏠 Dashboard")
    st.caption(f"Bienvenido, {user['nombre']}")
    
    # Obtener fecha actual y rangos
    today = datetime.now()
    current_month_start = today.replace(day=1)
    last_month_start = (current_month_start - timedelta(days=1)).replace(day=1)
    last_month_end = current_month_start - timedelta(days=1)
    
    # Métricas del mes actual
    st.markdown("### 📊 Resumen del Mes Actual")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Obtener cortes del mes actual
    cortes_mes = list_cortes_for_export(
        fecha_inicio=current_month_start.strftime("%Y-%m-%d"),
        fecha_fin=today.strftime("%Y-%m-%d")
    )
    
    # Calcular totales
    total_ingresos = sum(c.get("total_capturado", 0) for c in cortes_mes if c.get("estado") == "CERRADO")
    total_comision = sum(c.get("comision_casa", 0) for c in cortes_mes if c.get("estado") == "CERRADO")
    total_pago_cliente = sum(c.get("pago_cliente", 0) for c in cortes_mes if c.get("estado") == "CERRADO")
    cortes_cerrados = len([c for c in cortes_mes if c.get("estado") == "CERRADO"])
    
    # Obtener gastos del mes
    gastos_mes = get_gastos_summary(
        fecha_inicio=current_month_start.strftime("%Y-%m-%d"),
        fecha_fin=today.strftime("%Y-%m-%d")
    )
    total_gastos = gastos_mes.get("total", 0)
    
    # Ganancia neta
    ganancia_neta = total_comision - total_gastos
    
    with col1:
        st.metric(
            label="💰 Ingresos Totales",
            value=f"${total_ingresos:,.2f}",
            delta=f"{cortes_cerrados} cortes"
        )
    
    with col2:
        st.metric(
            label="🏦 Comisión Casa",
            value=f"${total_comision:,.2f}",
            delta=f"{(total_comision/total_ingresos*100) if total_ingresos > 0 else 0:.1f}%"
        )
    
    with col3:
        st.metric(
            label="💸 Gastos",
            value=f"${total_gastos:,.2f}",
            delta=f"{gastos_mes.get('count', 0)} registros"
        )
    
    with col4:
        delta_color = "normal" if ganancia_neta >= 0 else "inverse"
        st.metric(
            label="📈 Ganancia Neta",
            value=f"${ganancia_neta:,.2f}",
            delta=f"{'Positivo' if ganancia_neta >= 0 else 'Negativo'}",
            delta_color=delta_color
        )
    
    st.markdown("---")
    
    # Comparación con mes anterior
    st.markdown("### 📉 Comparación Mensual")
    
    cortes_mes_anterior = list_cortes_for_export(
        fecha_inicio=last_month_start.strftime("%Y-%m-%d"),
        fecha_fin=last_month_end.strftime("%Y-%m-%d")
    )
    
    if cortes_mes_anterior:
        total_ingresos_anterior = sum(c.get("total_capturado", 0) for c in cortes_mes_anterior if c.get("estado") == "CERRADO")
        total_comision_anterior = sum(c.get("comision_casa", 0) for c in cortes_mes_anterior if c.get("estado") == "CERRADO")
        
        gastos_mes_anterior = get_gastos_summary(
            fecha_inicio=last_month_start.strftime("%Y-%m-%d"),
            fecha_fin=last_month_end.strftime("%Y-%m-%d")
        )
        total_gastos_anterior = gastos_mes_anterior.get("total", 0)
        ganancia_neta_anterior = total_comision_anterior - total_gastos_anterior
        
        # Crear DataFrame para gráfica de comparación
        df_comparacion = pd.DataFrame({
            'Categoría': ['Ingresos', 'Comisión', 'Gastos', 'Ganancia Neta'],
            'Mes Anterior': [total_ingresos_anterior, total_comision_anterior, total_gastos_anterior, ganancia_neta_anterior],
            'Mes Actual': [total_ingresos, total_comision, total_gastos, ganancia_neta]
        })
        
        st.bar_chart(df_comparacion.set_index('Categoría'))
        
        # Calcular cambios porcentuales
        col1, col2, col3 = st.columns(3)
        
        with col1:
            cambio_ingresos = ((total_ingresos - total_ingresos_anterior) / total_ingresos_anterior * 100) if total_ingresos_anterior > 0 else 0
            st.metric(
                "Cambio en Ingresos",
                f"{cambio_ingresos:+.1f}%",
                delta=f"${total_ingresos - total_ingresos_anterior:,.2f}"
            )
        
        with col2:
            cambio_gastos = ((total_gastos - total_gastos_anterior) / total_gastos_anterior * 100) if total_gastos_anterior > 0 else 0
            st.metric(
                "Cambio en Gastos",
                f"{cambio_gastos:+.1f}%",
                delta=f"${total_gastos - total_gastos_anterior:,.2f}",
                delta_color="inverse"
            )
        
        with col3:
            cambio_ganancia = ((ganancia_neta - ganancia_neta_anterior) / abs(ganancia_neta_anterior) * 100) if ganancia_neta_anterior != 0 else 0
            st.metric(
                "Cambio en Ganancia",
                f"{cambio_ganancia:+.1f}%",
                delta=f"${ganancia_neta - ganancia_neta_anterior:,.2f}"
            )
    else:
        st.info("No hay datos del mes anterior para comparar.")
    
    st.markdown("---")
    
    # Distribución de gastos por categoría
    st.markdown("### 💸 Distribución de Gastos por Categoría")
    
    gastos_detalle = list_gastos(
        fecha_inicio=current_month_start.strftime("%Y-%m-%d"),
        fecha_fin=today.strftime("%Y-%m-%d")
    )
    
    if gastos_detalle:
        # Agrupar por categoría
        gastos_por_categoria = {}
        for gasto in gastos_detalle:
            cat = gasto.get("categoria", "OTRO")
            gastos_por_categoria[cat] = gastos_por_categoria.get(cat, 0) + gasto.get("monto", 0)
        
        # Crear DataFrame para gráfica
        df_gastos = pd.DataFrame({
            'Categoría': list(gastos_por_categoria.keys()),
            'Monto': list(gastos_por_categoria.values())
        })
        
        st.bar_chart(df_gastos.set_index('Categoría'))
        
        # Mostrar tabla de resumen
        st.dataframe(
            df_gastos.style.format({'Monto': '${:,.2f}'}),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No hay gastos registrados en el mes actual.")
    
    st.markdown("---")
    
    # Accesos rápidos
    st.markdown("### ⚡ Accesos Rápidos")
    
    col1, col2, col3, col4 = st.columns(4)
    
    quick_button_style = """
        <style>
        div[data-testid="column"] > div > div > div > div > button {
            width: 100% !important;
            height: 100px !important;
            font-size: 18px !important;
            font-weight: 600 !important;
            background: linear-gradient(135deg, #FF8C42 0%, #FFA500 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 12px !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 6px rgba(255, 140, 66, 0.2) !important;
        }
        div[data-testid="column"] > div > div > div > div > button:hover {
            transform: translateY(-5px) !important;
            box-shadow: 0 12px 24px rgba(255, 140, 66, 0.4) !important;
            background: linear-gradient(135deg, #FFA500 0%, #FF8C42 100%) !important;
        }
        </style>
    """
    st.markdown(quick_button_style, unsafe_allow_html=True)
    
    with col1:
        if st.button("📊 Nuevo Corte", use_container_width=True, key="quick_corte"):
            st.session_state.current_page = "Operación · Corte semanal"
            st.rerun()
    
    with col2:
        if st.button("💰 Registrar Gasto", use_container_width=True, key="quick_gasto"):
            st.session_state.current_page = "Gastos"
            st.rerun()
    
    with col3:
        if st.button("📜 Ver Historial", use_container_width=True, key="quick_historial"):
            st.session_state.current_page = "Historial"
            st.rerun()
    
    with col4:
        if st.button("⚙️ Administración", use_container_width=True, key="quick_admin"):
            st.session_state.current_page = "Admin"
            st.rerun()

# Made with Bob
