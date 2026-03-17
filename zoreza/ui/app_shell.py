import streamlit as st
from zoreza.db.core import init_db
from zoreza.services.auth import authenticate

from zoreza.ui.pages.operacion_corte import page_corte
from zoreza.ui.pages.historial import page_historial
from zoreza.ui.pages.admin import page_admin

def run_app():
    init_db(seed=True)

    if "user" not in st.session_state:
        st.session_state.user = None
    
    if "current_page" not in st.session_state:
        # Inicializar current_page solo si el usuario ya está autenticado
        if st.session_state.user and st.session_state.user.get("rol") == "ADMIN":
            st.session_state.current_page = "Dashboard"
        else:
            st.session_state.current_page = "Operación · Corte semanal"

    if not st.session_state.user:
        login_screen()
        return

    user = st.session_state.user
    
    # Banner de alerta si hay problemas de sincronización
    try:
        from zoreza.services import sync_service
        if sync_service and sync_service.has_pending_operations():
            pending_count = sync_service.get_pending_count()
            sync_state = sync_service.get_sync_state()
            
            st.markdown(f"""
                <div style="
                    background-color: #DC3545;
                    color: white;
                    padding: 1rem;
                    border-radius: 0.5rem;
                    margin-bottom: 1rem;
                    border-left: 5px solid #A71D2A;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
                ">
                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                        <span style="font-size: 1.5rem;">⚠️</span>
                        <div>
                            <strong style="font-size: 1.1rem;">MODO FALLBACK ACTIVO</strong>
                            <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem;">
                                La conexión con la base de datos en la nube falló.
                                Los cambios se están guardando localmente.
                            </p>
                            <p style="margin: 0.3rem 0 0 0; font-size: 0.85rem; opacity: 0.9;">
                                📝 <strong>{pending_count}</strong> operaciones pendientes de sincronizar
                            </p>
                            {f'<p style="margin: 0.3rem 0 0 0; font-size: 0.8rem; opacity: 0.8;">Último error: {sync_state.get("last_error", "Desconocido")}</p>' if sync_state.get("last_error") else ''}
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Botón para intentar sincronizar (solo para ADMIN)
            if user["rol"] == "ADMIN":
                col1, col2, col3 = st.columns([2, 1, 1])
                with col2:
                    if st.button("🔄 Intentar Sincronizar", key="sync_now", type="primary"):
                        with st.spinner("Sincronizando..."):
                            success, message, count = sync_service.sync_pending_operations()
                            if success:
                                st.success(message)
                                st.rerun()
                            else:
                                st.error(message)
                with col3:
                    if st.button("ℹ️ Ver Detalles", key="sync_details"):
                        st.session_state.show_sync_details = not st.session_state.get("show_sync_details", False)
                
                # Mostrar detalles si se solicitó
                if st.session_state.get("show_sync_details", False):
                    with st.expander("📋 Detalles de Sincronización", expanded=True):
                        st.json(sync_state)
    except Exception as e:
        # Silenciar errores del banner para no interrumpir la app
        pass
    
    # Header del sidebar
    st.sidebar.markdown("### Zoreza")
    st.sidebar.write(f"**{user['nombre']}**")
    st.sidebar.caption(f"Rol: {user['rol']}")
    st.sidebar.markdown("---")
    
    # Navegación con botones estilizados
    st.sidebar.markdown("#### Navegación")
    
    # Definir páginas según rol
    if user["rol"] == "ADMIN":
        pages = [
            ("🏠", "Dashboard"),
            ("📊", "Operación · Corte semanal"),
            ("📜", "Historial"),
            ("💰", "Gastos"),
            ("⚙️", "Admin")
        ]
    else:
        pages = [
            ("📊", "Operación · Corte semanal"),
            ("📜", "Historial")
        ]
    
    # Crear botones de navegación con estilo personalizado
    for icon, page_name in pages:
        is_selected = st.session_state.current_page == page_name
        bg_color = "#FF8C42" if is_selected else "transparent"
        text_color = "white" if is_selected else "#FAFAFA"
        font_weight = "600" if is_selected else "400"
        
        button_style = f"""
            <style>
            div.stButton > button {{
                width: 100%;
                text-align: left;
                padding: 0.75rem 1rem;
                border-radius: 0.5rem;
                border: none;
                background-color: {bg_color};
                color: {text_color};
                font-weight: {font_weight};
                transition: all 0.3s ease;
                margin-bottom: 0.5rem;
            }}
            div.stButton > button:hover {{
                background-color: #FF8C42;
                color: white;
                transform: translateX(5px);
            }}
            </style>
        """
        
        st.sidebar.markdown(button_style, unsafe_allow_html=True)
        if st.sidebar.button(f"{icon} {page_name}", key=f"nav_{page_name}"):
            st.session_state.current_page = page_name
            st.rerun()
    
    # Espaciador para empujar el botón de cerrar sesión al final
    st.sidebar.markdown("<br>" * 10, unsafe_allow_html=True)
    st.sidebar.markdown("---")
    
    # Botón de cerrar sesión al final
    logout_style = """
        <style>
        div.stButton > button[kind="secondary"] {
            width: 100%;
            background-color: #DC3545;
            color: white;
            border: none;
            padding: 0.75rem 1rem;
            border-radius: 0.5rem;
            font-weight: 500;
        }
        div.stButton > button[kind="secondary"]:hover {
            background-color: #C82333;
        }
        </style>
    """
    st.sidebar.markdown(logout_style, unsafe_allow_html=True)
    if st.sidebar.button("🚪 Cerrar sesión", type="secondary", key="logout"):
        st.session_state.user = None
        st.session_state.current_page = None
        st.rerun()
    
    # Renderizar página seleccionada
    current = st.session_state.current_page
    if current == "Dashboard":
        from zoreza.ui.pages.dashboard import page_dashboard
        page_dashboard(user)
    elif current and current.startswith("Operación"):
        page_corte(user)
    elif current == "Historial":
        page_historial(user)
    elif current == "Gastos":
        from zoreza.ui.pages.gastos import page_gastos
        page_gastos(user)
    elif current == "Admin":
        page_admin(user)
    else:
        # Fallback: si current es None o no coincide, mostrar página por defecto
        page_corte(user)

def login_screen():
    st.title("🧾 Zoreza · Corte Semanal")
    st.caption("Login requerido")
    with st.form("login"):
        username = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        submitted = st.form_submit_button("Entrar")
    
    if submitted:
        user, error_code = authenticate(username.strip(), password)
        
        if error_code == "DB_ERROR":
            st.error("❌ **Error de conexión con la base de datos**")
            st.warning("⚠️ No se pudo conectar a la base de datos. Posibles causas:")
            st.markdown("""
            - Problema de conexión con Turso
            - Credenciales de Turso incorrectas o expiradas
            - Base de datos no inicializada
            
            **Solución:** Contacta al administrador del sistema.
            """)
            
            # Mostrar información técnica en expander
            with st.expander("ℹ️ Información técnica"):
                from zoreza.services.turso_service import has_turso_credentials, get_turso_config
                
                if has_turso_credentials():
                    url, _ = get_turso_config()
                    st.code(f"Turso URL: {url[:50]}...", language="text")
                    st.info("✅ Credenciales de Turso encontradas")
                else:
                    st.error("❌ No se encontraron credenciales de Turso")
            return
        
        elif error_code == "USER_NOT_FOUND":
            st.error("❌ **Usuario no encontrado o inactivo**")
            st.info(f"El usuario '{username}' no existe en el sistema o está desactivado.")
            return
        
        elif error_code == "INVALID_PASSWORD":
            st.error("❌ **Contraseña incorrecta**")
            st.info("La contraseña ingresada no es correcta. Verifica e intenta nuevamente.")
            return
        
        elif user:
            # Login exitoso
            st.session_state.user = user
            st.rerun()
        else:
            # Error desconocido
            st.error("❌ Error desconocido durante el login")
            return
