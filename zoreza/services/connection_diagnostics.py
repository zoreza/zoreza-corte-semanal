"""
Diagnóstico de conexión a base de datos.
Verifica si Turso está configurado y funcionando correctamente.
"""
import os
from typing import Tuple

def diagnose_connection() -> Tuple[bool, str, dict]:
    """
    Diagnostica el estado de la conexión a la base de datos.
    
    Returns:
        Tuple[bool, str, dict]: (turso_ok, mensaje, detalles)
    """
    detalles = {
        "turso_url_found": False,
        "turso_token_found": False,
        "turso_url_preview": "",
        "streamlit_secrets_available": False,
        "connection_test": "not_tested",
        "using_fallback": False
    }
    
    # 1. Verificar si Streamlit está disponible
    try:
        import streamlit as st
        detalles["streamlit_secrets_available"] = True
        
        # Intentar leer desde secrets
        try:
            url = st.secrets.get("TURSO_DATABASE_URL")
            token = st.secrets.get("TURSO_AUTH_TOKEN")
            
            if url:
                detalles["turso_url_found"] = True
                detalles["turso_url_preview"] = url[:50] + "..." if len(url) > 50 else url
            
            if token:
                detalles["turso_token_found"] = True
                
        except Exception as e:
            # Secrets no disponibles, intentar variables de entorno
            pass
    except ImportError:
        detalles["streamlit_secrets_available"] = False
    
    # 2. Si no se encontró en secrets, buscar en variables de entorno
    if not detalles["turso_url_found"]:
        url = os.getenv("TURSO_DATABASE_URL")
        if url:
            detalles["turso_url_found"] = True
            detalles["turso_url_preview"] = url[:50] + "..." if len(url) > 50 else url
    
    if not detalles["turso_token_found"]:
        token = os.getenv("TURSO_AUTH_TOKEN")
        if token:
            detalles["turso_token_found"] = True
    
    # 3. Verificar si hay credenciales completas
    if not detalles["turso_url_found"] or not detalles["turso_token_found"]:
        mensaje = "❌ Credenciales de Turso incompletas"
        return False, mensaje, detalles
    
    # 4. Probar conexión a Turso
    try:
        from zoreza.services.turso_service import test_turso_connection, get_turso_config
        
        url, token = get_turso_config()
        success, test_msg = test_turso_connection(url, token)
        
        detalles["connection_test"] = "success" if success else "failed"
        
        if success:
            mensaje = "✅ Turso configurado y funcionando"
            return True, mensaje, detalles
        else:
            mensaje = f"❌ Turso configurado pero falla conexión: {test_msg}"
            return False, mensaje, detalles
            
    except Exception as e:
        detalles["connection_test"] = f"error: {str(e)}"
        mensaje = f"❌ Error al probar conexión: {str(e)}"
        return False, mensaje, detalles
    
    # 5. Verificar si está usando fallback
    try:
        from zoreza.services.sync_service import is_using_fallback
        if is_using_fallback():
            detalles["using_fallback"] = True
            mensaje = "⚠️ Usando SQLite local (fallback activo)"
            return False, mensaje, detalles
    except:
        pass
    
    return True, "✅ Conexión OK", detalles


def show_diagnostics_ui():
    """Muestra diagnóstico en la UI de Streamlit."""
    try:
        import streamlit as st
        
        turso_ok, mensaje, detalles = diagnose_connection()
        
        if not turso_ok:
            st.error(mensaje)
            
            with st.expander("🔍 Detalles del diagnóstico"):
                st.json(detalles)
                
                if not detalles["turso_url_found"]:
                    st.warning("⚠️ TURSO_DATABASE_URL no encontrada")
                    st.info("Verifica que esté configurada en Streamlit Cloud → Settings → Secrets")
                
                if not detalles["turso_token_found"]:
                    st.warning("⚠️ TURSO_AUTH_TOKEN no encontrado")
                    st.info("Verifica que esté configurado en Streamlit Cloud → Settings → Secrets")
                
                if detalles["connection_test"] == "failed":
                    st.error("❌ La conexión a Turso falló")
                    st.info("Verifica que las credenciales sean correctas y que Turso esté activo")
        else:
            st.success(mensaje)
            
    except ImportError:
        print("⚠️ Streamlit no disponible para mostrar diagnóstico")

# Made with Bob
