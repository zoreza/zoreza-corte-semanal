import streamlit as st
from datetime import date
from zoreza.services.time_utils import compute_week_bounds
from zoreza.services.rbac import allowed_clientes, allowed_maquinas_for_cliente, is_supervisor
from zoreza.services.config_service import get_float, get_config
from zoreza.services.validations import validate_capturada, validate_omitida, can_close_corte
from zoreza.services.calculations import reparto
from zoreza.db import repo
from zoreza.ticket.render import render_ticket

def page_corte(user: dict):
    st.header("Operación · Corte semanal")

    clientes = allowed_clientes(user)
    if not clientes:
        st.info("No tienes clientes disponibles por tus rutas asignadas.")
        return

    cliente_map = {c["nombre"]: c for c in clientes}
    cliente_name = st.selectbox("Cliente", list(cliente_map.keys()))
    cliente = cliente_map[cliente_name]

    fecha_corte = st.date_input("Fecha de corte", value=date.today())
    ws_dt, we_dt = compute_week_bounds(fecha_corte)
    week_start_iso = ws_dt.isoformat()
    week_end_iso = we_dt.isoformat()
    st.caption(f"Semana: {ws_dt.date()} — {we_dt.date()} (week_start={week_start_iso})")

    corte = repo.get_corte(cliente["id"], week_start_iso)
    if corte and corte["estado"] == "CERRADO":
        st.success("Este cliente ya tiene un corte CERRADO para esta semana. Solo se permite reimprimir.")
        show_closed_corte(corte["id"])
        return

    # BORRADOR: crear o cargar
    corte = repo.create_or_get_borrador(
        cliente_id=cliente["id"],
        week_start_iso=week_start_iso,
        week_end_iso=week_end_iso,
        fecha_corte_iso=str(fecha_corte),
        comision_pct=float(cliente["comision_pct"]),
        actor_id=user["id"],
    )
    st.info(f"Corte en BORRADOR · id={corte['id']}")

    maquinas = allowed_maquinas_for_cliente(user, cliente["id"])
    if not maquinas:
        st.warning("No hay máquinas visibles para ti en este cliente (rutas).")
        return

    # ensure detalle rows
    for m in maquinas:
        repo.upsert_detalle_base(corte["id"], m["id"], user["id"])

    detalle = repo.list_detalle(corte["id"])
    # map by machine
    det_by_mid = {d["maquina_id"]: d for d in detalle}

    st.subheader("Máquinas")
    tolerancia = get_float("tolerancia_pesos", 30.0)
    fondo_sugerido = get_float("fondo_sugerido", 500.0)

    cat_ir = repo.list_cats("cat_irregularidad")
    cat_om = repo.list_cats("cat_omision")
    cat_evt = repo.list_cats("cat_evento_contador")

    cat_ir_map = {c["id"]: c for c in cat_ir}
    cat_om_map = {c["id"]: c for c in cat_om}
    cat_evt_map = {c["id"]: c for c in cat_evt}

    for m in maquinas:
        d = det_by_mid[m["id"]]
        with st.expander(f"🕹️ {m['codigo']} · Estado actual: {d['estado_maquina']}", expanded=False):
            st.caption("Marca CAPTURADA u OMITIDA. Guarda por máquina.")
            estado = st.radio(
                "Estado de máquina",
                ["CAPTURADA", "OMITIDA"],
                index=0 if d["estado_maquina"] == "CAPTURADA" else 1,
                key=f"estado_{m['id']}",
                horizontal=True,
            )

            if estado == "CAPTURADA":
                prev = repo.last_capturada_counters(m["id"])
                prev_in = prev["in_act"] if prev else None
                prev_out = prev["out_act"] if prev else None
                st.caption(f"Previos (último corte CAPTURADA): entrada={prev_in} salida={prev_out}")

                col1, col2, col3 = st.columns(3)
                score = col1.number_input("score_tarjeta", min_value=0.0, value=float(d["score_tarjeta"] or 0.0), step=1.0, key=f"score_{m['id']}")
                efectivo = col2.number_input("efectivo_total", min_value=0.0, value=float(d["efectivo_total"] or 0.0), step=1.0, key=f"efec_{m['id']}")
                fondo = col3.number_input("fondo", min_value=0.0, value=float(d["fondo"] or fondo_sugerido), step=1.0, key=f"fondo_{m['id']}")

                col4, col5 = st.columns(2)
                c_in = col4.number_input("contador_entrada_actual", min_value=0, value=int(d["contador_entrada_actual"] or 0), step=1, key=f"cin_{m['id']}")
                c_out = col5.number_input("contador_salida_actual", min_value=0, value=int(d["contador_salida_actual"] or 0), step=1, key=f"cout_{m['id']}")

                # irregularidad inputs
                causa_id = d["causa_irregularidad_id"]
                causa_options = ["(ninguna)"] + [c["nombre"] for c in cat_ir if c["activo"]]
                causa_map_by_name = {c["nombre"]: c["id"] for c in cat_ir if c["activo"]}
                sel_name = "(ninguna)"
                if causa_id:
                    sel_name = next((c["nombre"] for c in cat_ir if c["id"] == causa_id), "(ninguna)")
                causa_sel = st.selectbox("Causa irregularidad (si aplica)", causa_options, index=causa_options.index(sel_name) if sel_name in causa_options else 0, key=f"causa_{m['id']}")
                causa_selected_id = None if causa_sel == "(ninguna)" else causa_map_by_name[causa_sel]
                req_nota_ir = bool(cat_ir_map.get(causa_selected_id, {}).get("requiere_nota", 0)) if causa_selected_id else False
                nota_ir = st.text_area("Nota irregularidad (cuando aplique)", value=d["nota_irregularidad"] or "", key=f"nota_ir_{m['id']}")

                # evento contador
                evento_id = d["evento_contador_id"]
                evento_options = ["(ninguno)"] + [c["nombre"] for c in cat_evt if c["activo"]]
                evento_map_by_name = {c["nombre"]: c["id"] for c in cat_evt if c["activo"]}
                sel_evt = "(ninguno)"
                if evento_id:
                    sel_evt = next((c["nombre"] for c in cat_evt if c["id"] == evento_id), "(ninguno)")
                evento_sel = st.selectbox("Motivo evento de contador (si aplica)", evento_options, index=evento_options.index(sel_evt) if sel_evt in evento_options else 0, key=f"evt_{m['id']}")
                evento_selected_id = None if evento_sel == "(ninguno)" else evento_map_by_name[evento_sel]
                nota_evt = st.text_area("Nota evento contador (obligatoria si actual < previo)", value=d["nota_evento_contador"] or "", key=f"nota_evt_{m['id']}")

                if st.button("Guardar máquina", key=f"save_{m['id']}"):
                    errs, computed = validate_capturada(
                        score_tarjeta=score,
                        efectivo_total=efectivo,
                        fondo=fondo,
                        contador_entrada_actual=c_in,
                        contador_salida_actual=c_out,
                        contador_entrada_prev=prev_in,
                        contador_salida_prev=prev_out,
                        tolerancia_pesos=tolerancia,
                        causa_irregularidad_id=causa_selected_id,
                        nota_irregularidad=nota_ir,
                        irregularidad_requiere_nota=req_nota_ir,
                        evento_contador_id=evento_selected_id,
                        nota_evento_contador=nota_evt,
                    )
                    if errs:
                        st.error("No se pudo guardar. Revisa:")
                        for e in errs:
                            st.write(f"- **{e.field}**: {e.message}")
                    else:
                        payload = {
                            "score_tarjeta": float(score),
                            "efectivo_total": float(efectivo),
                            "fondo": float(fondo),
                            "recaudable": float(computed["recaudable"]),
                            "diferencia_score": float(computed["diferencia_score"]),
                            "causa_irregularidad_id": causa_selected_id,
                            "nota_irregularidad": nota_ir.strip() or None,
                            "contador_entrada_actual": int(c_in),
                            "contador_salida_actual": int(c_out),
                            "contador_entrada_prev": prev_in,
                            "contador_salida_prev": prev_out,
                            "delta_entrada": computed.get("delta_entrada"),
                            "delta_salida": computed.get("delta_salida"),
                            "monto_estimado_contadores": computed.get("monto_estimado_contadores"),
                            "evento_contador_id": evento_selected_id,
                            "nota_evento_contador": nota_evt.strip() or None,
                        }
                        repo.save_detalle_capturada(corte["id"], m["id"], user["id"], payload)
                        st.success("Guardado.")
                        st.rerun()

                # preview calculations
                recaudable = float(efectivo - fondo)
                st.caption(f"Recaudable preliminar: ${recaudable:,.2f} · Diferencia vs score: ${recaudable - score:,.2f} (tol ±{tolerancia})")

            else:  # OMITIDA
                motivo_id = d["motivo_omision_id"]
                motivo_options = ["(selecciona)"] + [c["nombre"] for c in cat_om if c["activo"]]
                motivo_map = {c["nombre"]: c["id"] for c in cat_om if c["activo"]}
                sel_mot = "(selecciona)"
                if motivo_id:
                    sel_mot = next((c["nombre"] for c in cat_om if c["id"] == motivo_id), "(selecciona)")
                motivo_sel = st.selectbox("Motivo omisión", motivo_options, index=motivo_options.index(sel_mot) if sel_mot in motivo_options else 0, key=f"mot_{m['id']}")
                motivo_selected_id = None if motivo_sel == "(selecciona)" else motivo_map[motivo_sel]
                req_nota = bool(cat_om_map.get(motivo_selected_id, {}).get("requiere_nota", 0)) if motivo_selected_id else False
                nota = st.text_area("Nota omisión (obligatoria si aplica)", value=d["nota_omision"] or "", key=f"nota_om_{m['id']}")

                if st.button("Guardar omisión", key=f"saveom_{m['id']}"):
                    errs = validate_omitida(motivo_omision_id=motivo_selected_id, nota_omision=nota, requiere_nota=req_nota)
                    if errs:
                        st.error("No se pudo guardar. Revisa:")
                        for e in errs:
                            st.write(f"- **{e.field}**: {e.message}")
                    else:
                        repo.save_detalle_omitida(corte["id"], m["id"], user["id"], motivo_selected_id, nota.strip() or None)
                        st.success("Omisión guardada.")
                        st.rerun()

    st.divider()
    st.subheader("Cerrar corte")
    detalle = repo.list_detalle(corte["id"])
    msgs = can_close_corte(detalle)
    if msgs:
        for m in msgs:
            st.warning(m)
    can = len(msgs) == 0

    if st.button("Hacer corte (Cerrar)", type="primary", disabled=not can):
        # compute totals
        capt = [d for d in detalle if d["estado_maquina"] == "CAPTURADA"]
        neto = sum(float(d["recaudable"] or 0.0) for d in capt)
        pago, gan = reparto(neto, float(corte["comision_pct_usada"]))
        repo.close_corte(corte["id"], neto, pago, gan)
        st.success("Corte cerrado.")
        st.rerun()

def show_closed_corte(corte_id: int):
    corte = repo.corte_with_cliente_user(corte_id)
    detalle = repo.list_detalle(corte_id)

    st.subheader("Resumen")
    st.metric("Total recaudable", f"${float(corte['neto_cliente']):,.2f}")
    st.metric("Pago cliente", f"${float(corte['pago_cliente']):,.2f}")
    st.metric("Ganancia dueño", f"${float(corte['ganancia_dueno']):,.2f}")

    ctx = build_ticket_context(corte, detalle)
    html = render_ticket(ctx)
    st.components.v1.html(html, height=900, scrolling=True)

def build_ticket_context(corte: dict, detalle: list[dict]) -> dict:
    cfg = get_config()
    capt = []
    omit = []

    total_score = 0.0
    total_recaudable = 0.0
    total_diff = 0.0
    tolerancia = float(cfg.get("tolerancia_pesos", "30"))

    for d in detalle:
        if d["estado_maquina"] == "CAPTURADA":
            score = float(d["score_tarjeta"] or 0.0)
            rec = float(d["recaudable"] or 0.0)
            diff = float(d["diferencia_score"] or 0.0)
            total_score += score
            total_recaudable += rec
            total_diff += diff
            irregular = abs(diff) > tolerancia
            capt.append({
                "codigo": d["maquina_codigo"],
                "score_tarjeta": score,
                "efectivo_total": float(d["efectivo_total"] or 0.0),
                "fondo": float(d["fondo"] or 0.0),
                "recaudable": rec,
                "diferencia_score": diff,
                "irregular": irregular,
                "causa": d.get("causa_nombre"),
                "nota": d.get("nota_irregularidad"),
                "cont_in_act": d.get("contador_entrada_actual"),
                "cont_out_act": d.get("contador_salida_actual"),
                "cont_in_prev": d.get("contador_entrada_prev"),
                "cont_out_prev": d.get("contador_salida_prev"),
                "delta_in": d.get("delta_entrada"),
                "delta_out": d.get("delta_salida"),
                "monto_estimado": d.get("monto_estimado_contadores"),
                "evento": d.get("evento_nombre"),
                "nota_evento": d.get("nota_evento_contador"),
            })
        else:
            omit.append({
                "codigo": d["maquina_codigo"],
                "motivo": d.get("omision_nombre") or "",
                "nota": d.get("nota_omision") or "",
            })

    resumen = {
        "total_recaudable": float(corte["neto_cliente"]),
        "comision_pct": float(corte["comision_pct_usada"]),
        "pago_cliente": float(corte["pago_cliente"]),
        "ganancia_dueno": float(corte["ganancia_dueno"]),
        "total_score": total_score,
        "total_diferencia": total_diff,
    }

    return {
        "negocio_nombre": cfg.get("ticket_negocio_nombre", "Zoreza"),
        "footer": cfg.get("ticket_footer", ""),
        "cliente_nombre": corte["cliente_nombre"],
        "week_start": corte["week_start"],
        "week_end": corte["week_end"],
        "fecha_corte": corte["fecha_corte"],
        "created_at": corte["created_at"],
        "operador_nombre": corte["operador_nombre"],
        "resumen": resumen,
        "capturadas": capt,
        "omitidas": omit,
    }
