import streamlit as st
from datetime import datetime, timedelta
from zoreza.db.repo import (
    create_gasto,
    list_gastos,
    update_gasto,
    delete_gasto,
    get_gastos_summary
)

CATEGORIAS_GASTOS = [
    "REFACCIONES",
    "FONDOS_ROBOS",
    "PERMISOS",
    "EMPLEADOS",
    "SERVICIOS",
    "TRANSPORTE",
    "OTRO"
]

CATEGORIAS_LABELS = {
    "REFACCIONES": "🔧 Refacciones",
    "FONDOS_ROBOS": "🚨 Fondos (Robos)",
    "PERMISOS": "📋 Permisos",
    "EMPLEADOS": "👥 Empleados",
    "SERVICIOS": "⚙️ Servicios",
    "TRANSPORTE": "🚗 Transporte",
    "OTRO": "📦 Otro"
}

def page_gastos(user):
    """Página de gestión de gastos - Solo ADMIN"""
    
    # Verificar permisos
    if user["rol"] != "ADMIN":
        st.error("⛔ Acceso denegado. Solo administradores pueden acceder a esta sección.")
        return
    
    st.title("💰 Gestión de Gastos")
    st.caption("Registro y seguimiento de gastos del negocio")
    
    # Tabs para organizar la interfaz
    tab1, tab2, tab3 = st.tabs(["📝 Nuevo Gasto", "📊 Resumen", "📜 Historial"])
    
    # Tab 1: Nuevo Gasto
    with tab1:
        st.markdown("### Registrar Nuevo Gasto")
        
        with st.form("form_nuevo_gasto", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                fecha = st.date_input(
                    "Fecha del gasto",
                    value=datetime.now(),
                    max_value=datetime.now()
                )
                
                categoria = st.selectbox(
                    "Categoría",
                    options=CATEGORIAS_GASTOS,
                    format_func=lambda x: CATEGORIAS_LABELS.get(x, x)
                )
            
            with col2:
                monto = st.number_input(
                    "Monto ($)",
                    min_value=0.01,
                    step=0.01,
                    format="%.2f"
                )
                
                descripcion = st.text_input(
                    "Descripción",
                    max_chars=200,
                    placeholder="Ej: Reparación de máquina M-005"
                )
            
            notas = st.text_area(
                "Notas adicionales (opcional)",
                max_chars=500,
                placeholder="Detalles adicionales sobre el gasto..."
            )
            
            submitted = st.form_submit_button("💾 Guardar Gasto", use_container_width=True)
            
            if submitted:
                if not descripcion.strip():
                    st.error("La descripción es obligatoria")
                elif monto <= 0:
                    st.error("El monto debe ser mayor a 0")
                else:
                    try:
                        gasto_id = create_gasto(
                            fecha=fecha.strftime("%Y-%m-%d"),
                            categoria=categoria,
                            descripcion=descripcion.strip(),
                            monto=monto,
                            notas=notas.strip() if notas else None,
                            actor_id=user["id"]
                        )
                        st.success(f"✅ Gasto registrado exitosamente (ID: {gasto_id})")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error al registrar gasto: {str(e)}")
    
    # Tab 2: Resumen
    with tab2:
        st.markdown("### 📊 Resumen de Gastos")
        
        # Filtros de fecha
        col1, col2 = st.columns(2)
        
        with col1:
            fecha_inicio = st.date_input(
                "Desde",
                value=datetime.now().replace(day=1),
                key="resumen_fecha_inicio"
            )
        
        with col2:
            fecha_fin = st.date_input(
                "Hasta",
                value=datetime.now(),
                key="resumen_fecha_fin"
            )
        
        # Obtener resumen
        resumen = get_gastos_summary(
            fecha_inicio=fecha_inicio.strftime("%Y-%m-%d"),
            fecha_fin=fecha_fin.strftime("%Y-%m-%d")
        )
        
        # Mostrar métricas
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "💸 Total Gastado",
                f"${resumen.get('total', 0):,.2f}"
            )
        
        with col2:
            st.metric(
                "📝 Número de Gastos",
                resumen.get('count', 0)
            )
        
        with col3:
            promedio = resumen.get('total', 0) / resumen.get('count', 1) if resumen.get('count', 0) > 0 else 0
            st.metric(
                "📊 Promedio por Gasto",
                f"${promedio:,.2f}"
            )
        
        st.markdown("---")
        
        # Obtener gastos detallados
        gastos = list_gastos(
            fecha_inicio=fecha_inicio.strftime("%Y-%m-%d"),
            fecha_fin=fecha_fin.strftime("%Y-%m-%d")
        )
        
        if gastos:
            # Agrupar por categoría
            gastos_por_categoria = {}
            for gasto in gastos:
                cat = gasto.get("categoria", "OTRO")
                if cat not in gastos_por_categoria:
                    gastos_por_categoria[cat] = {
                        "total": 0,
                        "count": 0
                    }
                gastos_por_categoria[cat]["total"] += gasto.get("monto", 0)
                gastos_por_categoria[cat]["count"] += 1
            
            # Mostrar por categoría
            st.markdown("#### Desglose por Categoría")
            
            for cat in CATEGORIAS_GASTOS:
                if cat in gastos_por_categoria:
                    data = gastos_por_categoria[cat]
                    with st.expander(f"{CATEGORIAS_LABELS[cat]} - ${data['total']:,.2f} ({data['count']} gastos)"):
                        gastos_cat = [g for g in gastos if g.get("categoria") == cat]
                        for gasto in gastos_cat:
                            col1, col2, col3 = st.columns([2, 1, 1])
                            with col1:
                                st.write(f"**{gasto.get('descripcion')}**")
                                if gasto.get('notas'):
                                    st.caption(gasto.get('notas'))
                            with col2:
                                st.write(f"${gasto.get('monto', 0):,.2f}")
                            with col3:
                                st.caption(gasto.get('fecha'))
        else:
            st.info("No hay gastos registrados en el período seleccionado.")
    
    # Tab 3: Historial
    with tab3:
        st.markdown("### 📜 Historial de Gastos")
        
        # Filtros
        col1, col2, col3 = st.columns(3)
        
        with col1:
            fecha_inicio_hist = st.date_input(
                "Desde",
                value=datetime.now() - timedelta(days=30),
                key="hist_fecha_inicio"
            )
        
        with col2:
            fecha_fin_hist = st.date_input(
                "Hasta",
                value=datetime.now(),
                key="hist_fecha_fin"
            )
        
        with col3:
            categoria_filtro = st.selectbox(
                "Categoría",
                options=["TODAS"] + CATEGORIAS_GASTOS,
                format_func=lambda x: "Todas las categorías" if x == "TODAS" else CATEGORIAS_LABELS.get(x, x),
                key="hist_categoria"
            )
        
        # Obtener gastos
        gastos_hist = list_gastos(
            fecha_inicio=fecha_inicio_hist.strftime("%Y-%m-%d"),
            fecha_fin=fecha_fin_hist.strftime("%Y-%m-%d"),
            categoria=None if categoria_filtro == "TODAS" else categoria_filtro
        )
        
        if gastos_hist:
            st.info(f"📊 Mostrando {len(gastos_hist)} gastos")
            
            # Mostrar tabla
            for gasto in gastos_hist:
                with st.container():
                    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                    
                    with col1:
                        st.markdown(f"**{CATEGORIAS_LABELS.get(gasto.get('categoria'), gasto.get('categoria'))}**")
                        st.write(gasto.get('descripcion'))
                        if gasto.get('notas'):
                            st.caption(f"📝 {gasto.get('notas')}")
                    
                    with col2:
                        st.metric("Monto", f"${gasto.get('monto', 0):,.2f}")
                    
                    with col3:
                        st.caption("Fecha")
                        st.write(gasto.get('fecha'))
                    
                    with col4:
                        # Botones de acción
                        if st.button("🗑️", key=f"delete_{gasto.get('id')}", help="Eliminar gasto"):
                            try:
                                delete_gasto(gasto.get('id'))
                                st.success("Gasto eliminado")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {str(e)}")
                    
                    st.markdown("---")
        else:
            st.info("No hay gastos registrados en el período seleccionado.")

# Made with Bob
