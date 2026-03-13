import streamlit as st
from zoreza.ui.app_shell import run_app
from zoreza.db.migration_v2 import migrate

st.set_page_config(page_title="Zoreza · Corte Semanal", page_icon="🧾", layout="wide")

# Ejecutar migración automáticamente (solo se aplica una vez)
# El parámetro silent=True evita que imprima mensajes en la consola
try:
    migrate(silent=True)
except Exception as e:
    # Si falla la migración, mostrar advertencia pero continuar
    st.warning(f"⚠️ Advertencia al ejecutar migración: {e}")

run_app()
