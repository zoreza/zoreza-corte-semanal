import streamlit as st
from zoreza.db import repo
from zoreza.services.passwords import hash_password
from zoreza.services.config_service import get_config, set_config
from zoreza.db.queries import fetchall

def page_admin(user: dict):
    if user["rol"] != "ADMIN":
        st.error("Acceso denegado.")
        return

    st.header("Admin")

    tab = st.tabs(["Usuarios","Clientes","Máquinas","Rutas","Asignaciones","Config & Catálogos"])

    with tab[0]:
        st.subheader("Usuarios")
        users = repo.list_usuarios()
        st.dataframe(users, use_container_width=True, hide_index=True)

        with st.expander("Crear usuario"):
            with st.form("create_user"):
                username = st.text_input("username")
                nombre = st.text_input("nombre")
                rol = st.selectbox("rol", ["ADMIN","SUPERVISOR","OPERADOR"])
                activo = st.checkbox("activo", value=True)
                password = st.text_input("password", type="password")
                ok = st.form_submit_button("Crear")
            if ok:
                repo.create_usuario(username.strip(), hash_password(password), nombre.strip(), rol, 1 if activo else 0, user["id"])
                st.success("Creado.")
                st.rerun()

        with st.expander("Editar usuario"):
            if users:
                pick = st.selectbox("Usuario", users, format_func=lambda r: f"{r['username']} ({r['rol']})", key="pick_user")
                with st.form("edit_user"):
                    nombre2 = st.text_input("nombre", value=pick["nombre"])
                    rol2 = st.selectbox("rol", ["ADMIN","SUPERVISOR","OPERADOR"], index=["ADMIN","SUPERVISOR","OPERADOR"].index(pick["rol"]))
                    activo2 = st.checkbox("activo", value=bool(pick["activo"]))
                    newpass = st.text_input("nuevo password (opcional)", type="password")
                    ok2 = st.form_submit_button("Guardar cambios")
                if ok2:
                    ph = hash_password(newpass) if newpass.strip() else None
                    repo.update_usuario(pick["id"], nombre2.strip(), rol2, 1 if activo2 else 0, user["id"], ph)
                    st.success("Actualizado.")
                    st.rerun()

    with tab[1]:
        st.subheader("Clientes")
        clientes = repo.list_clientes()
        st.dataframe(clientes, use_container_width=True, hide_index=True)

        with st.expander("Crear cliente"):
            with st.form("create_cliente"):
                nombre = st.text_input("Nombre cliente")
                com = st.number_input("Comisión % (0-100)", min_value=0.0, max_value=100.0, value=40.0, step=1.0)
                activo = st.checkbox("activo", value=True, key="c_act")
                ok = st.form_submit_button("Crear")
            if ok:
                repo.create_cliente(nombre.strip(), com/100.0, 1 if activo else 0, user["id"])
                st.success("Creado.")
                st.rerun()

        with st.expander("Editar cliente"):
            if clientes:
                pick = st.selectbox("Cliente", clientes, format_func=lambda r: r["nombre"], key="pick_cliente")
                with st.form("edit_cliente"):
                    nombre2 = st.text_input("Nombre", value=pick["nombre"])
                    com2 = st.number_input("Comisión %", min_value=0.0, max_value=100.0, value=float(pick["comision_pct"])*100.0, step=1.0)
                    activo2 = st.checkbox("activo", value=bool(pick["activo"]), key="c_act2")
                    ok2 = st.form_submit_button("Guardar")
                if ok2:
                    repo.update_cliente(pick["id"], nombre2.strip(), com2/100.0, 1 if activo2 else 0, user["id"])
                    st.success("Actualizado.")
                    st.rerun()

    with tab[2]:
        st.subheader("Máquinas")
        maquinas = repo.list_maquinas()
        st.dataframe(maquinas, use_container_width=True, hide_index=True)

        clientes = repo.list_clientes()
        cliente_map = {c["nombre"]: c["id"] for c in clientes}

        with st.expander("Crear máquina"):
            with st.form("create_maquina"):
                codigo = st.text_input("Código (único)")
                cliente_name = st.selectbox("Cliente", list(cliente_map.keys()))
                activo = st.checkbox("activo", value=True, key="m_act")
                ok = st.form_submit_button("Crear")
            if ok:
                repo.create_maquina(codigo.strip(), cliente_map[cliente_name], 1 if activo else 0, user["id"])
                st.success("Creada.")
                st.rerun()

        with st.expander("Editar máquina"):
            if maquinas:
                pick = st.selectbox("Máquina", maquinas, format_func=lambda r: f"{r['codigo']} · {r['cliente_nombre']}", key="pick_maquina")
                with st.form("edit_maquina"):
                    codigo2 = st.text_input("Código", value=pick["codigo"])
                    cliente_name2 = st.selectbox("Cliente", list(cliente_map.keys()), index=list(cliente_map.keys()).index(pick["cliente_nombre"]))
                    activo2 = st.checkbox("activo", value=bool(pick["activo"]), key="m_act2")
                    ok2 = st.form_submit_button("Guardar")
                if ok2:
                    repo.update_maquina(pick["id"], codigo2.strip(), cliente_map[cliente_name2], 1 if activo2 else 0, user["id"])
                    st.success("Actualizada.")
                    st.rerun()

    with tab[3]:
        st.subheader("Rutas")
        rutas = repo.list_rutas()
        st.dataframe(rutas, use_container_width=True, hide_index=True)

        with st.expander("Crear ruta"):
            with st.form("create_ruta"):
                nombre = st.text_input("Nombre (único)")
                desc = st.text_area("Descripción")
                activo = st.checkbox("activo", value=True, key="r_act")
                ok = st.form_submit_button("Crear")
            if ok:
                repo.create_ruta(nombre.strip(), desc.strip(), 1 if activo else 0, user["id"])
                st.success("Creada.")
                st.rerun()

        with st.expander("Editar ruta"):
            if rutas:
                pick = st.selectbox("Ruta", rutas, format_func=lambda r: r["nombre"], key="pick_ruta")
                with st.form("edit_ruta"):
                    nombre2 = st.text_input("Nombre", value=pick["nombre"])
                    desc2 = st.text_area("Descripción", value=pick["descripcion"] or "")
                    activo2 = st.checkbox("activo", value=bool(pick["activo"]), key="r_act2")
                    ok2 = st.form_submit_button("Guardar")
                if ok2:
                    repo.update_ruta(pick["id"], nombre2.strip(), desc2.strip(), 1 if activo2 else 0, user["id"])
                    st.success("Actualizada.")
                    st.rerun()

    with tab[4]:
        st.subheader("Asignaciones")
        st.caption("Usuario ↔ Ruta y Máquina ↔ Ruta")

        rutas = repo.list_rutas()
        usuarios = repo.list_usuarios()
        maquinas = repo.list_maquinas()

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### Usuario ↔ Ruta")
            ur = repo.list_usuario_ruta()
            st.dataframe(ur, use_container_width=True, hide_index=True)
            with st.form("set_ur"):
                u = st.selectbox("Usuario", usuarios, format_func=lambda r: r["username"], key="ur_u")
                r = st.selectbox("Ruta", rutas, format_func=lambda rr: rr["nombre"], key="ur_r")
                activo = st.checkbox("activo", value=True, key="ur_act")
                ok = st.form_submit_button("Guardar")
            if ok:
                repo.set_usuario_ruta(u["id"], r["id"], 1 if activo else 0)
                st.success("Asignación guardada.")
                st.rerun()

        with col2:
            st.markdown("#### Máquina ↔ Ruta")
            mr = repo.list_maquina_ruta()
            st.dataframe(mr, use_container_width=True, hide_index=True)
            with st.form("set_mr"):
                m = st.selectbox("Máquina", maquinas, format_func=lambda r: r["codigo"], key="mr_m")
                r2 = st.selectbox("Ruta", rutas, format_func=lambda rr: rr["nombre"], key="mr_r")
                activo2 = st.checkbox("activo", value=True, key="mr_act")
                ok2 = st.form_submit_button("Guardar")
            if ok2:
                repo.set_maquina_ruta(m["id"], r2["id"], 1 if activo2 else 0)
                st.success("Asignación guardada.")
                st.rerun()

    with tab[5]:
        st.subheader("Config global")
        cfg = get_config()
        keys = ["tolerancia_pesos","fondo_sugerido","semana_inicia","ticket_negocio_nombre","ticket_footer"]
        for k in keys:
            val = cfg.get(k,"")
            new = st.text_input(k, value=val, key=f"cfg_{k}")
            if new != val:
                if st.button(f"Guardar {k}", key=f"savecfg_{k}"):
                    set_config(k, new, user["id"])
                    st.success("Guardado.")
                    st.rerun()

        st.divider()
        st.subheader("Catálogos")

        for table, title in [
            ("cat_irregularidad","Causas de irregularidad"),
            ("cat_omision","Motivos de omisión"),
            ("cat_evento_contador","Motivos evento contador"),
        ]:
            st.markdown(f"### {title}")
            cats = repo.list_cats(table)
            st.dataframe(cats, use_container_width=True, hide_index=True)
            with st.expander(f"Agregar/Editar en {title}"):
                cat_id = st.selectbox("Editar (opcional)", [None] + [c["id"] for c in cats], format_func=lambda x: "(nuevo)" if x is None else f"id={x}", key=f"cat_pick_{table}")
                current = next((c for c in cats if c["id"] == cat_id), None)
                nombre = st.text_input("nombre", value=(current["nombre"] if current else ""), key=f"cat_name_{table}")
                req = st.checkbox("requiere_nota", value=bool(current["requiere_nota"]) if current else False, key=f"cat_req_{table}")
                act = st.checkbox("activo", value=bool(current["activo"]) if current else True, key=f"cat_act_{table}")
                if st.button("Guardar catálogo", key=f"cat_save_{table}"):
                    repo.upsert_cat(table, cat_id, nombre.strip(), 1 if req else 0, 1 if act else 0)
                    st.success("Guardado.")
                    st.rerun()
