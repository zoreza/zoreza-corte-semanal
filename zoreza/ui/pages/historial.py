import streamlit as st
from zoreza.services.rbac import allowed_clientes, is_supervisor
from zoreza.db import repo
from zoreza.ui.pages.operacion_corte import show_closed_corte

def page_historial(user: dict):
    st.header("Historial")

    clientes = allowed_clientes(user)
    cliente_filter = st.selectbox("Filtrar por cliente (opcional)", ["(todos)"] + [c["nombre"] for c in clientes])
    cliente_id = None
    if cliente_filter != "(todos)":
        cliente_id = next(c["id"] for c in clientes if c["nombre"] == cliente_filter)

    cortes = repo.list_cortes(cliente_id)
    if not cortes:
        st.info("Sin cortes.")
        return

    st.caption("Selecciona un corte para ver detalle / reimprimir ticket.")
    labels = [f"{c['cliente_nombre']} · {c['week_start'][:10]} · {c['estado']} · id={c['id']}" for c in cortes]
    idx = st.selectbox("Cortes", list(range(len(cortes))), format_func=lambda i: labels[i], index=0)
    corte = cortes[idx]

    if corte["estado"] != "CERRADO":
        st.warning("Este corte está en BORRADOR. Para cerrarlo ve a Operación.")
        st.write(corte)
        return

    show_closed_corte(corte["id"])
