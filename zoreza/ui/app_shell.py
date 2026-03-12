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
        user = authenticate(username.strip(), password)
        if not user:
            st.error("Credenciales inválidas o usuario inactivo.")
            return
        st.session_state.user = user
        st.rerun()
