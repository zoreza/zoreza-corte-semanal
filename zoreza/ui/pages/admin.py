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

    tab = st.tabs(["Usuarios","Clientes","Máquinas","Rutas","Asignaciones","Config & Catálogos","Base de Datos"])

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
                nombre = st.text_input("Nombre cliente*")
                com = st.number_input("Comisión % (0-100)*", min_value=0.0, max_value=100.0, value=40.0, step=1.0)
                st.caption("Campos opcionales:")
                col1, col2 = st.columns(2)
                with col1:
                    domicilio = st.text_input("Domicilio")
                    telefono = st.text_input("Teléfono")
                with col2:
                    colonia = st.text_input("Colonia")
                    poblacion = st.text_input("Población")
                activo = st.checkbox("activo", value=True, key="c_act")
                ok = st.form_submit_button("Crear")
            if ok:
                repo.create_cliente(
                    nombre.strip(), com/100.0, 1 if activo else 0, user["id"],
                    domicilio.strip() or None, colonia.strip() or None,
                    telefono.strip() or None, poblacion.strip() or None
                )
                st.success("Creado.")
                st.rerun()

        with st.expander("Editar cliente"):
            if clientes:
                pick = st.selectbox("Cliente", clientes, format_func=lambda r: r["nombre"], key="pick_cliente")
                with st.form("edit_cliente"):
                    nombre2 = st.text_input("Nombre*", value=pick["nombre"])
                    com2 = st.number_input("Comisión %*", min_value=0.0, max_value=100.0, value=float(pick["comision_pct"])*100.0, step=1.0)
                    st.caption("Campos opcionales:")
                    col1, col2 = st.columns(2)
                    with col1:
                        domicilio2 = st.text_input("Domicilio", value=pick.get("domicilio") or "")
                        telefono2 = st.text_input("Teléfono", value=pick.get("telefono") or "")
                    with col2:
                        colonia2 = st.text_input("Colonia", value=pick.get("colonia") or "")
                        poblacion2 = st.text_input("Población", value=pick.get("poblacion") or "")
                    activo2 = st.checkbox("activo", value=bool(pick["activo"]), key="c_act2")
                    ok2 = st.form_submit_button("Guardar")
                if ok2:
                    repo.update_cliente(
                        pick["id"], nombre2.strip(), com2/100.0, 1 if activo2 else 0, user["id"],
                        domicilio2.strip() or None, colonia2.strip() or None,
                        telefono2.strip() or None, poblacion2.strip() or None
                    )
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
                codigo = st.text_input("Código (único)*")
                cliente_name = st.selectbox("Cliente*", list(cliente_map.keys()))
                st.caption("Campos opcionales:")
                col1, col2 = st.columns(2)
                with col1:
                    numero_permiso = st.text_input("Número de Permiso")
                with col2:
                    fecha_permiso = st.date_input("Fecha de Permiso", value=None)
                asignada = st.checkbox("Asignada (en uso)", value=True, help="Desmarcar para dejar en pool de máquinas disponibles")
                activo = st.checkbox("activo", value=True, key="m_act")
                ok = st.form_submit_button("Crear")
            if ok:
                fecha_str = fecha_permiso.isoformat() if fecha_permiso else None
                repo.create_maquina(
                    codigo.strip(), cliente_map[cliente_name], 1 if activo else 0, user["id"],
                    numero_permiso.strip() or None, fecha_str, 1 if asignada else 0
                )
                st.success("Creada.")
                st.rerun()

        with st.expander("Editar máquina"):
            if maquinas:
                pick = st.selectbox("Máquina", maquinas, format_func=lambda r: f"{r['codigo']} · {r['cliente_nombre']}", key="pick_maquina")
                with st.form("edit_maquina"):
                    codigo2 = st.text_input("Código*", value=pick["codigo"])
                    cliente_name2 = st.selectbox("Cliente*", list(cliente_map.keys()), index=list(cliente_map.keys()).index(pick["cliente_nombre"]))
                    st.caption("Campos opcionales:")
                    col1, col2 = st.columns(2)
                    with col1:
                        numero_permiso2 = st.text_input("Número de Permiso", value=pick.get("numero_permiso") or "")
                    with col2:
                        from datetime import date
                        fecha_val = None
                        if pick.get("fecha_permiso"):
                            try:
                                fecha_val = date.fromisoformat(pick["fecha_permiso"])
                            except:
                                pass
                        fecha_permiso2 = st.date_input("Fecha de Permiso", value=fecha_val)
                    asignada2 = st.checkbox("Asignada (en uso)", value=bool(pick.get("asignada", 1)), help="Desmarcar para dejar en pool de máquinas disponibles")
                    activo2 = st.checkbox("activo", value=bool(pick["activo"]), key="m_act2")
                    ok2 = st.form_submit_button("Guardar")
                if ok2:
                    fecha_str2 = fecha_permiso2.isoformat() if fecha_permiso2 else None
                    repo.update_maquina(
                        pick["id"], codigo2.strip(), cliente_map[cliente_name2], 1 if activo2 else 0, user["id"],
                        numero_permiso2.strip() or None, fecha_str2, 1 if asignada2 else 0
                    )
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
        st.info("ℹ️ **Nuevo sistema:** Ahora las asignaciones son Cliente→Ruta. Todas las máquinas del cliente heredan automáticamente la ruta asignada.")

        rutas = repo.list_rutas()
        usuarios = repo.list_usuarios()
        clientes = repo.list_clientes()

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
            st.markdown("#### Cliente ↔ Ruta")
            cr = repo.list_cliente_ruta()
            st.dataframe(cr, use_container_width=True, hide_index=True)
            with st.form("set_cr"):
                c = st.selectbox("Cliente", clientes, format_func=lambda r: r["nombre"], key="cr_c")
                r2 = st.selectbox("Ruta", rutas, format_func=lambda rr: rr["nombre"], key="cr_r")
                activo2 = st.checkbox("activo", value=True, key="cr_act")
                ok2 = st.form_submit_button("Guardar")
            if ok2:
                repo.set_cliente_ruta(c["id"], r2["id"], 1 if activo2 else 0, user["id"])
                st.success("Asignación guardada. Todas las máquinas del cliente heredan esta ruta.")
                st.rerun()
        
        st.divider()
        st.markdown("#### 📦 Pool de Máquinas Sin Asignar")
        st.caption("Máquinas marcadas como 'no asignadas' que están disponibles para uso futuro")
        sin_asignar = repo.list_maquinas_sin_asignar()
        if sin_asignar:
            st.dataframe(sin_asignar, use_container_width=True, hide_index=True)
        else:
            st.info("No hay máquinas sin asignar. Todas las máquinas están en uso.")

    with tab[5]:
        st.subheader("Configuración Global")
        cfg = get_config()
        
        # Usar un formulario para guardar todos los cambios a la vez
        with st.form("config_form"):
            st.caption("Modifica los valores y presiona 'Guardar Configuración' al final")
            
            config_values = {}
            config_values["tolerancia_pesos"] = st.text_input(
                "Tolerancia de Pesos",
                value=cfg.get("tolerancia_pesos", ""),
                help="Tolerancia permitida en diferencias de peso"
            )
            config_values["fondo_sugerido"] = st.text_input(
                "Fondo Sugerido",
                value=cfg.get("fondo_sugerido", ""),
                help="Monto sugerido para fondo de caja"
            )
            config_values["semana_inicia"] = st.text_input(
                "Semana Inicia",
                value=cfg.get("semana_inicia", ""),
                help="Día en que inicia la semana (ej: Lunes)"
            )
            config_values["ticket_negocio_nombre"] = st.text_input(
                "Nombre del Negocio (Ticket)",
                value=cfg.get("ticket_negocio_nombre", ""),
                help="Nombre que aparece en los tickets"
            )
            config_values["ticket_footer"] = st.text_area(
                "Pie de Página (Ticket)",
                value=cfg.get("ticket_footer", ""),
                help="Texto que aparece al final de los tickets"
            )
            
            submitted = st.form_submit_button("💾 Guardar Configuración", type="primary", use_container_width=True)
        
        if submitted:
            # Guardar todos los cambios
            changes_made = False
            for key, new_value in config_values.items():
                old_value = cfg.get(key, "")
                if new_value != old_value:
                    set_config(key, new_value, user["id"])
                    changes_made = True
            
            if changes_made:
                st.success("✅ Configuración guardada exitosamente")
                st.rerun()
            else:
                st.info("ℹ️ No hay cambios que guardar")

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
                with st.form(f"cat_form_{table}"):
                    cat_id = st.selectbox("Editar (opcional)", [None] + [c["id"] for c in cats], format_func=lambda x: "(nuevo)" if x is None else f"id={x}", key=f"cat_pick_{table}")
                    current = next((c for c in cats if c["id"] == cat_id), None)
                    nombre = st.text_input("nombre", value=(current["nombre"] if current else ""), key=f"cat_name_{table}")
                    req = st.checkbox("requiere_nota", value=bool(current["requiere_nota"]) if current else False, key=f"cat_req_{table}")
                    act = st.checkbox("activo", value=bool(current["activo"]) if current else True, key=f"cat_act_{table}")
                    submitted = st.form_submit_button("💾 Guardar catálogo", use_container_width=True)
                
                if submitted:
                    repo.upsert_cat(table, cat_id, nombre.strip(), 1 if req else 0, 1 if act else 0)
                    st.success("✅ Guardado.")
                    st.rerun()

    
    with tab[6]:
        st.subheader("Base de Datos")
        
        # Importar servicios necesarios
        try:
            from zoreza.services import turso_service
            from zoreza.db.core import get_db_type, db_path
            
            # Mostrar estado actual
            status = turso_service.get_db_status()
            
            if status["type"] == "turso":
                st.success(f"✅ Usando **{status['details']['provider']}**")
                st.caption(f"📍 URL: `{status['url']}`")
                st.caption(f"🔌 Conexión: {status['details']['connection']}")
            else:
                st.info(f"📁 Usando **{status['details']['provider']}**")
                st.caption(f"📍 Ruta: `{status['url']}`")
                if "warning" in status["details"]:
                    st.warning(f"⚠️ {status['details']['warning']}")
            
            st.divider()
            
            # Sección de configuración de Turso
            st.markdown("### 🌐 Configurar Turso (Base de Datos en la Nube)")
            st.caption("Turso es SQLite en la nube, 100% gratis. Perfecto para Streamlit Cloud.")
            
            with st.expander("ℹ️ ¿Cómo obtener las credenciales de Turso?", expanded=False):
                st.markdown("""
                **Paso 1:** Crea una cuenta gratis en [turso.tech](https://turso.tech)
                
                **Paso 2:** Instala Turso CLI:
                ```bash
                curl -sSfL https://get.tur.so/install.sh | bash
                ```
                
                **Paso 3:** Inicia sesión:
                ```bash
                turso auth login
                ```
                
                **Paso 4:** Crea una base de datos:
                ```bash
                turso db create zoreza-corte
                ```
                
                **Paso 5:** Obtén la URL:
                ```bash
                turso db show zoreza-corte --url
                ```
                
                **Paso 6:** Crea un token:
                ```bash
                turso db tokens create zoreza-corte
                ```
                
                **Paso 7:** Copia la URL y el Token aquí abajo 👇
                """)
            
            # Formulario de configuración
            current_url, current_token = turso_service.get_turso_config()
            
            with st.form("turso_config"):
                turso_url = st.text_input(
                    "Turso Database URL",
                    value=current_url,
                    placeholder="libsql://your-database.turso.io",
                    help="URL de tu base de datos en Turso"
                )
                
                turso_token = st.text_input(
                    "Turso Auth Token",
                    value=current_token,
                    type="password",
                    placeholder="eyJhbGciOiJFZERTQS...",
                    help="Token de autenticación de Turso"
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    test_btn = st.form_submit_button("🔍 Probar Conexión", use_container_width=True)
                with col2:
                    save_btn = st.form_submit_button("💾 Guardar Configuración", use_container_width=True, type="primary")
            
            # Probar conexión
            if test_btn:
                if not turso_url or not turso_token:
                    st.error("❌ Por favor ingresa URL y Token")
                else:
                    with st.spinner("Probando conexión..."):
                        success, message = turso_service.test_turso_connection(turso_url, turso_token)
                        if success:
                            st.success(message)
                        else:
                            st.error(message)
            
            # Guardar configuración
            if save_btn:
                if not turso_url or not turso_token:
                    st.error("❌ Por favor ingresa URL y Token")
                else:
                    # Primero probar la conexión
                    with st.spinner("Verificando conexión..."):
                        success, message = turso_service.test_turso_connection(turso_url, turso_token)
                    
                    if success:
                        turso_service.set_turso_config(turso_url, turso_token)
                        st.success("✅ Configuración guardada. La app usará Turso al reiniciar.")
                        st.info("⚠️ **Importante:** Necesitas reiniciar la aplicación para que los cambios surtan efecto.")
                        
                        # Botón para reiniciar (solo funciona en Streamlit Cloud)
                        if st.button("🔄 Reiniciar Aplicación"):
                            st.rerun()
                    else:
                        st.error(f"❌ No se pudo conectar: {message}")
            
            st.divider()
            
            # Sección de migración
            if status["type"] == "local":
                st.markdown("### 📤 Migrar Datos a Turso")
                st.caption("Si ya tienes datos en SQLite local, puedes migrarlos a Turso.")
                
                # Usar has_turso_credentials() en lugar de is_turso_configured()
                # para permitir migración incluso cuando el fallback está activo
                if turso_service.has_turso_credentials():
                    local_path = db_path()
                    config_url, config_token = turso_service.get_turso_config()
                    
                    if st.button("🚀 Migrar Datos Locales a Turso", type="primary"):
                        with st.spinner("Migrando datos..."):
                            success, message, stats = turso_service.migrate_local_to_turso(
                                local_path,
                                config_url,
                                config_token
                            )
                        
                        if success:
                            st.success(message)
                            st.info("💡 Reinicia la aplicación para empezar a usar Turso")
                            if stats.get("errors"):
                                with st.expander("⚠️ Ver errores"):
                                    for error in stats["errors"]:
                                        st.warning(error)
                        else:
                            st.error(message)
                else:
                    st.warning("⚠️ Primero configura Turso arriba para poder migrar datos")
            
            st.divider()
            
            # Información adicional
            st.markdown("### 📚 Información")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Tipo de BD", status["type"].upper())
            with col2:
                st.metric("Estado", "✅ Configurado" if status["configured"] else "⚠️ Local")
            
            with st.expander("🔧 Detalles Técnicos"):
                st.json({
                    "type": status["type"],
                    "configured": status["configured"],
                    "url": status["url"],
                    "details": status["details"],
                    "local_path": db_path() if status["type"] == "local" else "N/A"
                })
            
        except ImportError as e:
            st.error(f"❌ Error al cargar módulo de Turso: {e}")
            st.info("Asegúrate de que `libsql-client` esté instalado: `pip install libsql-client`")
