import streamlit as st
from zoreza.ui.app_shell import run_app
from zoreza.db.migration_v2 import migrate
from zoreza.db.core import init_db
from pathlib import Path
from zoreza.db.core import db_path

st.set_page_config(page_title="Zoreza · Corte Semanal", page_icon="🧾", layout="wide")

# Inicializar BD si no existe
try:
    if not Path(db_path()).exists():
        print("🔧 Inicializando base de datos...")
        init_db(seed=True)
        print("✅ Base de datos inicializada correctamente")
except Exception as e:
    st.error(f"❌ Error al inicializar base de datos: {e}")
    st.stop()

# Ejecutar migración automáticamente (solo se aplica una vez)
# El parámetro silent=True evita que imprima mensajes en la consola
try:
    migrate(silent=True)
except Exception as e:
    # Si falla la migración, mostrar advertencia pero continuar
    st.warning(f"⚠️ Advertencia al ejecutar migración: {e}")

run_app()
