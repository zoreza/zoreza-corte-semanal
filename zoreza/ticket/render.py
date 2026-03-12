from __future__ import annotations
from html import escape

# -----------------------
# Helpers
# -----------------------
def money(x: float) -> str:
    return f"${x:,.2f}"

def _to_float(v, default=0.0) -> float:
    try:
        return float(v)
    except Exception:
        return float(default)

# -----------------------
# Thermal 80mm (OPTIMIZADO)
# -----------------------
CSS_THERMAL_80 = """<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  
  body { 
    margin: 0; 
    padding: 0;
    font-family: 'Courier New', Courier, monospace;
  }
  
  .ticket {
    width: 80mm;
    padding: 8mm 4mm;
    color: #000;
    font-size: 10pt;
    line-height: 1.3;
  }
  
  .center { text-align: center; }
  .right { text-align: right; }
  .bold { font-weight: bold; }
  
  .header {
    text-align: center;
    margin-bottom: 8px;
    padding-bottom: 8px;
    border-bottom: 2px solid #000;
  }
  
  .header .title {
    font-size: 14pt;
    font-weight: bold;
    margin-bottom: 4px;
  }
  
  .header .subtitle {
    font-size: 9pt;
    margin-bottom: 2px;
  }
  
  .section {
    margin: 8px 0;
    padding: 6px 0;
    border-bottom: 1px dashed #000;
  }
  
  .section-title {
    font-weight: bold;
    font-size: 11pt;
    margin-bottom: 4px;
    text-transform: uppercase;
  }
  
  .row {
    display: flex;
    justify-content: space-between;
    padding: 2px 0;
  }
  
  .row.total {
    font-weight: bold;
    font-size: 11pt;
    padding: 4px 0;
    border-top: 1px solid #000;
    margin-top: 4px;
  }
  
  .machine {
    margin: 6px 0;
    padding: 4px;
    background: #f5f5f5;
  }
  
  .machine-header {
    font-weight: bold;
    font-size: 11pt;
    margin-bottom: 3px;
  }
  
  .alert {
    background: #fff3cd;
    padding: 3px;
    margin: 3px 0;
    font-weight: bold;
  }
  
  .small {
    font-size: 8pt;
    color: #666;
  }
  
  .signatures {
    margin-top: 12px;
    padding-top: 8px;
    border-top: 2px solid #000;
  }
  
  .signature-line {
    margin: 16px 0 4px 0;
    border-top: 1px solid #000;
    width: 60%;
  }
  
  .footer {
    text-align: center;
    font-size: 8pt;
    color: #666;
    margin-top: 8px;
    padding-top: 8px;
    border-top: 1px dashed #000;
  }
  
  @media print {
    @page { 
      size: 80mm auto; 
      margin: 0; 
    }
    body { margin: 0; }
    .no-print { display: none !important; }
    .ticket { padding: 4mm 2mm; }
  }
</style>"""

def render_ticket_thermal_80(ctx: dict) -> str:
    """Ticket optimizado para impresoras térmicas de 80mm."""
    
    # Datos básicos
    negocio = escape(ctx.get("negocio_nombre", "Zoreza"))
    footer = escape(ctx.get("footer", "Gracias por su preferencia"))
    cliente = escape(ctx.get("cliente_nombre", "—"))
    ws = escape(ctx.get("week_start", ""))
    we = escape(ctx.get("week_end", ""))
    fecha_corte = escape(ctx.get("fecha_corte", ""))
    created_at = escape(ctx.get("created_at", ""))
    operador = escape(ctx.get("operador_nombre", "—"))
    r = ctx["resumen"]
    
    # Resumen financiero (invertido para el cliente)
    total_recaudable = money(_to_float(r.get("total_recaudable")))
    comision_cliente_pct = f"{_to_float(r.get('comision_pct'))*100:.1f}%"
    comision_casa_pct = f"{(1 - _to_float(r.get('comision_pct')))*100:.1f}%"
    ganancia_cliente = money(_to_float(r.get("pago_cliente")))  # Lo que recibe el cliente
    comision_casa = money(_to_float(r.get("ganancia_dueno")))   # Lo que se queda la casa
    
    # Máquinas capturadas
    maquinas_html = []
    for d in ctx.get("capturadas", []):
        codigo = escape(d.get("codigo", "—"))
        efectivo = money(_to_float(d.get("efectivo_total")))
        fondo = money(_to_float(d.get("fondo")))
        recaudable = money(_to_float(d.get("recaudable")))
        dif_val = _to_float(d.get("diferencia_score"))
        dif = money(dif_val)
        
        irregular = bool(d.get("irregular"))
        causa = escape(d.get("causa") or "")
        
        # Alerta si hay irregularidad
        alert_html = ""
        if irregular:
            alert_html = f'<div class="alert">⚠ IRREGULARIDAD: {causa}</div>'
        
        maquinas_html.append(f"""
        <div class="machine">
          <div class="machine-header">🎰 {codigo}</div>
          <div class="row">
            <span>Efectivo:</span>
            <span>{efectivo}</span>
          </div>
          <div class="row">
            <span>Fondo:</span>
            <span>{fondo}</span>
          </div>
          <div class="row total">
            <span>RECAUDABLE:</span>
            <span>{recaudable}</span>
          </div>
          <div class="row small">
            <span>Diferencia:</span>
            <span class="{'bold' if irregular else ''}">{dif}</span>
          </div>
          {alert_html}
        </div>
        """)
    
    maquinas_content = "".join(maquinas_html) if maquinas_html else '<div class="small center">Sin máquinas capturadas</div>'
    
    # Máquinas omitidas
    omitidas_html = ""
    omitidas = ctx.get("omitidas", [])
    if omitidas:
        omitidas_rows = []
        for o in omitidas:
            cod = escape(o.get("codigo", "—"))
            motivo = escape(o.get("motivo", ""))
            omitidas_rows.append(f'<div class="row small"><span>• {cod}</span><span>{motivo}</span></div>')
        
        omitidas_html = f"""
        <div class="section">
          <div class="section-title">Máquinas Omitidas</div>
          {''.join(omitidas_rows)}
        </div>
        """
    
    # Construir HTML completo
    html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Ticket de Corte - {cliente}</title>
  {CSS_THERMAL_80}
</head>
<body>
  <div class="no-print" style="padding: 10px; background: #f0f0f0; text-align: center;">
    <button onclick="window.print()" style="padding: 10px 20px; font-size: 14px; cursor: pointer;">
      🖨️ Imprimir Ticket
    </button>
  </div>

  <div class="ticket">
    <!-- ENCABEZADO -->
    <div class="header">
      <div class="title">{negocio}</div>
      <div class="subtitle">CORTE SEMANAL</div>
      <div class="subtitle bold">{cliente}</div>
      <div class="small">Semana: {ws[:10]} al {we[:10]}</div>
      <div class="small">Fecha corte: {fecha_corte}</div>
      <div class="small">Operador: {operador}</div>
    </div>

    <!-- RESUMEN FINANCIERO -->
    <div class="section">
      <div class="section-title">Resumen</div>
      <div class="row">
        <span>Total Recaudable:</span>
        <span class="bold">{total_recaudable}</span>
      </div>
      <div class="row">
        <span>Comisión Casa ({comision_casa_pct}):</span>
        <span>{comision_casa}</span>
      </div>
      <div class="row total">
        <span>PAGO AL CLIENTE ({comision_cliente_pct}):</span>
        <span>{ganancia_cliente}</span>
      </div>
    </div>

    <!-- DETALLE DE MÁQUINAS -->
    <div class="section">
      <div class="section-title">Detalle por Máquina</div>
      {maquinas_content}
    </div>

    <!-- OMITIDAS (si hay) -->
    {omitidas_html}

    <!-- FOOTER -->
    <div class="footer">
      {footer}
      <div class="small">Generado: {created_at[:16]}</div>
    </div>
  </div>
</body>
</html>"""
    
    return html


# -----------------------
# Report (diseño original carta)
# -----------------------
CSS_REPORT = """<style>
  body { font-family: Arial, sans-serif; margin: 18px; }
  .header { display:flex; justify-content:space-between; align-items:flex-start; }
  h1 { margin:0; font-size: 20px; }
  .meta { font-size: 12px; color: #333; }
  .box { border: 1px solid #ddd; padding: 10px; border-radius: 8px; margin-top: 10px; }
  table { width:100%; border-collapse: collapse; font-size: 12px; }
  th, td { border-bottom: 1px solid #eee; padding: 6px 6px; text-align:left; vertical-align: top;}
  th { background: #fafafa; }
  .right { text-align:right; }
  .small { font-size: 11px; color:#555; }
  .muted { color:#777; }
  .warn { color:#a94442; font-weight:600; }
  .sign { display:flex; gap:24px; margin-top: 18px; }
  .line { border-top: 1px solid #333; width: 260px; margin-top: 32px; }
  @media print { .no-print { display:none; } body { margin: 0; } }
</style>"""

def render_ticket_report(ctx: dict) -> str:
    negocio = escape(ctx.get("negocio_nombre", "Zoreza"))
    footer = escape(ctx.get("footer", ""))
    cliente = escape(ctx.get("cliente_nombre", "—"))
    ws = escape(ctx.get("week_start", ""))
    we = escape(ctx.get("week_end", ""))
    fecha_corte = escape(ctx.get("fecha_corte", ""))
    created_at = escape(ctx.get("created_at", ""))
    operador = escape(ctx.get("operador_nombre", "—"))
    r = ctx["resumen"]

    capt_rows: list[str] = []
    for d in ctx.get("capturadas", []):
        irregular = bool(d.get("irregular"))
        causa = escape(d.get("causa") or "")
        nota = escape(d.get("nota") or "")
        evento = escape(d.get("evento") or "")
        nota_evt = escape(d.get("nota_evento") or "")

        if d.get("cont_in_prev") is None:
            cont_prev = '<div class="muted">Sin previos (baseline)</div>'
        else:
            cont_prev = (
                f"<div>Prev: E{d.get('cont_in_prev')} / S{d.get('cont_out_prev')}</div>"
                f"<div>Δ: E{d.get('delta_in')} / S{d.get('delta_out')} → {money(_to_float(d.get('monto_estimado')))}</div>"
            )

        evento_html = ""
        if evento:
            evento_html = f'<div class="warn">Evento: {evento}</div>' + (f"<div>{nota_evt}</div>" if nota_evt else "")

        ir_html = '<span class="muted">OK</span>'
        if irregular:
            ir_html = f'<div class="warn">{causa}</div>' + (f"<div>{nota}</div>" if nota else "")

        capt_rows.append(
            "<tr>"
            f"<td><b>{escape(d['codigo'])}</b></td>"
            f"<td class='right'>{money(_to_float(d.get('score_tarjeta')))}</td>"
            f"<td class='right'>{money(_to_float(d.get('efectivo_total')))}</td>"
            f"<td class='right'>{money(_to_float(d.get('fondo')))}</td>"
            f"<td class='right'><b>{money(_to_float(d.get('recaudable')))}</b></td>"
            f"<td class='right {'warn' if irregular else ''}'>{money(_to_float(d.get('diferencia_score')))}</td>"
            f"<td class='small'>{ir_html}</td>"
            "<td class='small'>"
            f"<div>Act: E{d.get('cont_in_act')} / S{d.get('cont_out_act')}</div>"
            f"{cont_prev}{evento_html}</td></tr>"
        )

    om_rows: list[str] = []
    for o in ctx.get("omitidas", []):
        om_rows.append(
            "<tr>"
            f"<td><b>{escape(o['codigo'])}</b></td>"
            f"<td>{escape(o.get('motivo',''))}</td>"
            f"<td class='small'>{escape(o.get('nota') or '')}</td>"
            "</tr>"
        )

    if not om_rows:
        om_rows = ['<tr><td colspan="3" class="muted">Sin omitidas</td></tr>']

    capt_body = "".join(capt_rows) if capt_rows else '<tr><td colspan="8" class="muted">Sin capturadas</td></tr>'
    om_body = "".join(om_rows)

    html = f"""<!doctype html>
<html><head><meta charset="utf-8"/><title>Zoreza · Corte Semanal</title>{CSS_REPORT}</head>
<body>
  <div class="no-print" style="margin-bottom:10px;">
    <button onclick="window.print()">Imprimir</button>
  </div>

  <div class="header">
    <div>
      <h1>{negocio} · Corte Semanal</h1>
      <div class="meta">Cliente: <b>{cliente}</b></div>
      <div class="meta">Semana: {ws} — {we}</div>
    </div>
    <div class="meta right">
      <div>Fecha corte: {fecha_corte}</div>
      <div>Creado: {created_at}</div>
      <div>Operador: {operador}</div>
    </div>
  </div>

  <div class="box">
    <b>Resumen</b>
    <table>
      <tr><td>Total recaudable</td><td class="right">{money(_to_float(r['total_recaudable']))}</td></tr>
      <tr><td>Comisión aplicada</td><td class="right">{_to_float(r['comision_pct'])*100:.2f}%</td></tr>
      <tr><td>Pago al cliente</td><td class="right">{money(_to_float(r['pago_cliente']))}</td></tr>
      <tr><td>Ganancia dueño</td><td class="right">{money(_to_float(r['ganancia_dueno']))}</td></tr>
      <tr><td class="small muted">Total score tarjeta (opcional)</td><td class="right small muted">{money(_to_float(r['total_score']))}</td></tr>
      <tr><td class="small muted">Suma diferencias (recaudable - score)</td><td class="right small muted">{money(_to_float(r['total_diferencia']))}</td></tr>
    </table>
  </div>

  <div class="box">
    <b>Detalle · Máquinas CAPTURADAS</b>
    <table>
      <thead>
        <tr>
          <th>Máquina</th>
          <th class="right">Score</th>
          <th class="right">Efectivo</th>
          <th class="right">Fondo</th>
          <th class="right">Recaudable</th>
          <th class="right">Dif.</th>
          <th>Irregularidad</th>
          <th>Contadores</th>
        </tr>
      </thead>
      <tbody>{capt_body}</tbody>
    </table>
  </div>

  <div class="box">
    <b>Máquinas OMITIDAS</b>
    <table>
      <thead><tr><th>Máquina</th><th>Motivo</th><th>Nota</th></tr></thead>
      <tbody>{om_body}</tbody>
    </table>
  </div>

  <div class="sign">
    <div style="flex:1">
      <div class="line"></div>
      <div class="small">Recibí (Cliente)</div>
    </div>
    <div style="flex:1">
      <div class="line"></div>
      <div class="small">Operador</div>
    </div>
  </div>

  <div class="small muted" style="margin-top:12px;">{footer}</div>
</body></html>"""
    return html


# -----------------------
# Router
# -----------------------
def render_ticket(ctx: dict, mode: str | None = None) -> str:
    """
    Genera ticket en el formato especificado.
    
    Args:
        ctx: Contexto con datos del corte
        mode: Modo de ticket:
            - "thermal" o "thermal_80": Ticket térmico 80mm (RECOMENDADO)
            - "report": Reporte tamaño carta
            - None: Usa configuración por defecto
    
    Returns:
        HTML del ticket
    """
    cfg = ctx.get("config", {}) or {}
    if mode is None:
        mode = str(cfg.get("ticket_mode_default", "thermal")).strip().lower()
    
    # Usar thermal_80 por defecto para impresoras térmicas
    if mode in ("thermal", "thermal_80", "receipt", "80mm"):
        return render_ticket_thermal_80(ctx)
    
    return render_ticket_report(ctx)

# Made with Bob
