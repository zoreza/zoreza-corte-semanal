"""
Página de emergencia para resetear contraseña de admin
Solo accesible mediante URL directa
"""
import streamlit as st
import hashlib
from zoreza.services.turso_service import create_turso_client, get_turso_config
import os

def hash_password(password: str) -> str:
    """Genera hash SHA-256 de la contraseña."""
    return hashlib.sha256(password.encode()).hexdigest()

def main():
    st.set_page_config(
        page_title="Reset Password Admin",
        page_icon="🔐",
        layout="centered"
    )
    
    st.title("🔐 Reset de Contraseña - Admin")
    st.warning("⚠️ Esta es una página de emergencia para resetear la contraseña del usuario admin")
    
    st.divider()
    
    # Verificar credenciales de Turso
    try:
        turso_url = st.secrets.get("TURSO_DATABASE_URL") or os.getenv("TURSO_DATABASE_URL")
        turso_token = st.secrets.get("TURSO_AUTH_TOKEN") or os.getenv("TURSO_AUTH_TOKEN")
        
        if not turso_url or not turso_token:
            st.error("❌ No se encontraron las credenciales de Turso")
            st.info("Verifica que TURSO_DATABASE_URL y TURSO_AUTH_TOKEN estén configurados en los secrets")
            return
            
        st.success("✅ Credenciales de Turso encontradas")
        st.code(f"URL: {turso_url[:50]}...", language="text")
        
    except Exception as e:
        st.error(f"❌ Error al obtener credenciales: {e}")
        return
    
    st.divider()
    
    # Formulario para resetear contraseña
    with st.form("reset_form"):
        st.subheader("Nueva Contraseña")
        
        new_password = st.text_input(
            "Contraseña para admin",
            value="admin123",
            type="password",
            help="Ingresa la nueva contraseña para el usuario admin"
        )
        
        confirm_password = st.text_input(
            "Confirmar contraseña",
            type="password",
            help="Confirma la nueva contraseña"
        )
        
        submitted = st.form_submit_button("🔄 Resetear Contraseña", type="primary", use_container_width=True)
        
        if submitted:
            if not new_password:
                st.error("❌ La contraseña no puede estar vacía")
                return
                
            if new_password != confirm_password:
                st.error("❌ Las contraseñas no coinciden")
                return
            
            # Resetear contraseña
            with st.spinner("Actualizando contraseña en Turso..."):
                try:
                    # Crear cliente Turso
                    client = create_turso_client(turso_url, turso_token)
                    
                    # Generar hash
                    password_hash = hash_password(new_password)
                    
                    # Ejecutar UPDATE
                    sql = "UPDATE usuarios SET password_hash = ? WHERE username = 'admin'"
                    cursor = client.cursor()
                    cursor.execute(sql, (password_hash,))
                    
                    # IMPORTANTE: Commit para persistir
                    client.commit()
                    
                    st.success("✅ Contraseña actualizada exitosamente")
                    
                    st.divider()
                    
                    st.info("📋 **Nuevas credenciales:**")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.code("Usuario: admin", language="text")
                    with col2:
                        st.code(f"Contraseña: {new_password}", language="text")
                    
                    st.divider()
                    
                    st.success("🎉 Ahora puedes cerrar esta página y hacer login con las nuevas credenciales")
                    
                    # Botón para ir al login
                    if st.button("🔙 Ir al Login", type="primary", use_container_width=True):
                        st.switch_page("app.py")
                    
                except Exception as e:
                    st.error(f"❌ Error al actualizar contraseña: {e}")
                    st.exception(e)
    
    st.divider()
    
    # Información adicional
    with st.expander("ℹ️ Información Técnica"):
        st.markdown("""
        ### ¿Cómo funciona?
        
        1. Esta página se conecta directamente a Turso usando las credenciales de los secrets
        2. Genera un hash SHA-256 de la nueva contraseña
        3. Ejecuta un UPDATE en la tabla `usuarios` para el usuario `admin`
        4. Hace commit para persistir los cambios
        
        ### ¿Cuándo usar esta página?
        
        - Cuando olvidaste la contraseña de admin
        - Cuando la contraseña se corrompió por algún problema de sincronización
        - Como herramienta de emergencia para recuperar acceso
        
        ### Seguridad
        
        - Esta página solo es accesible mediante URL directa
        - No aparece en el menú de navegación
        - Requiere acceso a los secrets de Streamlit Cloud
        """)

if __name__ == "__main__":
    main()

# Made with Bob
