import { useState, useEffect, useCallback } from 'react';
import { getCortes, getCorteDetalles, getGastos, getClientes } from '../api';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import * as XLSX from 'xlsx';

const COLORS = ['#2563eb', '#16a34a', '#eab308', '#dc2626', '#8b5cf6', '#f97316', '#06b6d4'];

export default function Reportes() {
  const [clientes, setClientes] = useState([]);
  const [cortes, setCortes] = useState([]);
  const [gastos, setGastos] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({
    cliente_id: '',
    estado: 'CERRADO',
    desde: getDefaultDesde(),
    hasta: new Date().toISOString().slice(0, 10),
  });

  useEffect(() => {
    getClientes().then(setClientes).catch(() => {});
  }, []);

  const loadReport = useCallback(async () => {
    setLoading(true);
    try {
      const params = {};
      if (filters.estado) params.estado = filters.estado;
      if (filters.cliente_id) params.cliente_id = filters.cliente_id;
      const [c, g] = await Promise.all([getCortes(params), getGastos()]);
      // Filter by date range
      const desde = filters.desde;
      const hasta = filters.hasta;
      const filteredCortes = c.filter((x) => x.week_start >= desde && x.week_start <= hasta);
      const filteredGastos = g.filter((x) => x.fecha >= desde && x.fecha <= hasta);
      setCortes(filteredCortes);
      setGastos(filteredGastos);
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => { loadReport(); }, [loadReport]);

  const clienteMap = Object.fromEntries(clientes.map((c) => [c.uuid, c.nombre]));

  // Aggregations
  const totalNeto = cortes.reduce((s, c) => s + (c.neto_cliente || 0), 0);
  const totalPago = cortes.reduce((s, c) => s + (c.pago_cliente || 0), 0);
  const totalGanancia = cortes.reduce((s, c) => s + (c.ganancia_dueno || 0), 0);
  const totalGastos = gastos.reduce((s, g) => s + (g.monto || 0), 0);
  const utilidadNeta = totalGanancia - totalGastos;

  // Chart: weekly revenue
  const weeklyData = cortes.map((c) => ({
    semana: c.week_start,
    neto: c.neto_cliente || 0,
    ganancia: c.ganancia_dueno || 0,
    pago: c.pago_cliente || 0,
  })).sort((a, b) => a.semana.localeCompare(b.semana));

  // Chart: by client
  const byClient = {};
  cortes.forEach((c) => {
    const name = clienteMap[c.cliente_id] || 'Desconocido';
    if (!byClient[name]) byClient[name] = 0;
    byClient[name] += c.ganancia_dueno || 0;
  });
  const clientPieData = Object.entries(byClient).map(([name, value]) => ({ name, value }));

  // Export
  const exportExcel = async () => {
    const wb = XLSX.utils.book_new();

    // Cortes sheet
    const cortesSheet = cortes.map((c) => ({
      Semana: `${c.week_start} — ${c.week_end}`,
      Cliente: clienteMap[c.cliente_id] || '',
      'Neto Cliente': c.neto_cliente,
      'Pago Cliente': c.pago_cliente,
      'Ganancia Dueño': c.ganancia_dueno,
      Estado: c.estado,
    }));
    XLSX.utils.book_append_sheet(wb, XLSX.utils.json_to_sheet(cortesSheet), 'Cortes');

    // Detalles sheet
    const allDetalles = [];
    for (const c of cortes) {
      try {
        const detalles = await getCorteDetalles(c.uuid);
        detalles.forEach((d) => {
          allDetalles.push({
            Semana: `${c.week_start} — ${c.week_end}`,
            Cliente: clienteMap[c.cliente_id] || '',
            Máquina: d.maquina_codigo || d.maquina_id,
            Estado: d.estado_maquina,
            Efectivo: d.efectivo_total,
            Score: d.score_tarjeta,
            Fondo: d.fondo,
            Recaudable: d.recaudable,
            Diferencia: d.diferencia,
          });
        });
      } catch {
        // skip
      }
    }
    if (allDetalles.length > 0) {
      XLSX.utils.book_append_sheet(wb, XLSX.utils.json_to_sheet(allDetalles), 'Detalles');
    }

    // Gastos sheet
    const gastosSheet = gastos.map((g) => ({
      Fecha: g.fecha,
      Descripción: g.descripcion || '',
      Monto: g.monto,
    }));
    if (gastosSheet.length > 0) {
      XLSX.utils.book_append_sheet(wb, XLSX.utils.json_to_sheet(gastosSheet), 'Gastos');
    }

    // Summary
    const summarySheet = [
      { Concepto: 'Total Neto Cliente', Valor: totalNeto },
      { Concepto: 'Total Pago Cliente', Valor: totalPago },
      { Concepto: 'Total Ganancia Dueño', Valor: totalGanancia },
      { Concepto: 'Total Gastos', Valor: totalGastos },
      { Concepto: 'Utilidad Neta', Valor: utilidadNeta },
      { Concepto: 'Cortes', Valor: cortes.length },
    ];
    XLSX.utils.book_append_sheet(wb, XLSX.utils.json_to_sheet(summarySheet), 'Resumen');

    XLSX.writeFile(wb, `reporte_${filters.desde}_${filters.hasta}.xlsx`);
  };

  const fmt = (n) => `$${Number(n).toLocaleString('es-MX', { minimumFractionDigits: 2 })}`;

  return (
    <div>
      <h1 className="page-title">Reportes</h1>

      {/* Filters */}
      <div className="card mb-24" style={{ display: 'flex', gap: 16, alignItems: 'flex-end', flexWrap: 'wrap' }}>
        <div className="form-group" style={{ margin: 0 }}>
          <label>Desde</label>
          <input type="date" value={filters.desde} onChange={(e) => setFilters((f) => ({ ...f, desde: e.target.value }))} />
        </div>
        <div className="form-group" style={{ margin: 0 }}>
          <label>Hasta</label>
          <input type="date" value={filters.hasta} onChange={(e) => setFilters((f) => ({ ...f, hasta: e.target.value }))} />
        </div>
        <div className="form-group" style={{ margin: 0 }}>
          <label>Cliente</label>
          <select value={filters.cliente_id} onChange={(e) => setFilters((f) => ({ ...f, cliente_id: e.target.value }))}>
            <option value="">Todos</option>
            {clientes.map((c) => <option key={c.uuid} value={c.uuid}>{c.nombre}</option>)}
          </select>
        </div>
        <div className="form-group" style={{ margin: 0 }}>
          <label>Estado</label>
          <select value={filters.estado} onChange={(e) => setFilters((f) => ({ ...f, estado: e.target.value }))}>
            <option value="">Todos</option>
            <option value="BORRADOR">Borrador</option>
            <option value="CERRADO">Cerrado</option>
          </select>
        </div>
        <button className="btn btn-primary" onClick={exportExcel}>📥 Exportar Excel</button>
      </div>

      {loading ? <div className="spinner" /> : (
        <>
          {/* KPIs */}
          <div className="kpi-grid mb-24">
            <div className="kpi-card">
              <div className="kpi-label">Neto Cliente</div>
              <div className="kpi-value">{fmt(totalNeto)}</div>
            </div>
            <div className="kpi-card">
              <div className="kpi-label">Pago Cliente</div>
              <div className="kpi-value">{fmt(totalPago)}</div>
            </div>
            <div className="kpi-card">
              <div className="kpi-label">Ganancia Dueño</div>
              <div className="kpi-value" style={{ color: 'var(--success)' }}>{fmt(totalGanancia)}</div>
            </div>
            <div className="kpi-card">
              <div className="kpi-label">Total Gastos</div>
              <div className="kpi-value" style={{ color: 'var(--danger)' }}>{fmt(totalGastos)}</div>
            </div>
            <div className="kpi-card">
              <div className="kpi-label">Utilidad Neta</div>
              <div className="kpi-value" style={{ color: utilidadNeta >= 0 ? 'var(--success)' : 'var(--danger)' }}>{fmt(utilidadNeta)}</div>
            </div>
            <div className="kpi-card">
              <div className="kpi-label">Cortes</div>
              <div className="kpi-value">{cortes.length}</div>
            </div>
          </div>

          {/* Charts */}
          <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 24, marginBottom: 24 }}>
            <div className="card">
              <h3 style={{ marginBottom: 12 }}>Ingresos Semanales</h3>
              {weeklyData.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={weeklyData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="semana" tick={{ fontSize: 11 }} />
                    <YAxis tick={{ fontSize: 11 }} />
                    <Tooltip formatter={(v) => fmt(v)} />
                    <Legend />
                    <Bar dataKey="neto" name="Neto" fill="#2563eb" />
                    <Bar dataKey="ganancia" name="Ganancia" fill="#16a34a" />
                  </BarChart>
                </ResponsiveContainer>
              ) : <p>Sin datos</p>}
            </div>

            <div className="card">
              <h3 style={{ marginBottom: 12 }}>Ganancia por Cliente</h3>
              {clientPieData.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie data={clientPieData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={100} label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}>
                      {clientPieData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                    </Pie>
                    <Tooltip formatter={(v) => fmt(v)} />
                  </PieChart>
                </ResponsiveContainer>
              ) : <p>Sin datos</p>}
            </div>
          </div>

          {/* Summary table */}
          <div className="card">
            <h3 style={{ marginBottom: 12 }}>Detalle de Cortes</h3>
            <table>
              <thead>
                <tr><th>Semana</th><th>Cliente</th><th>Neto</th><th>Pago</th><th>Ganancia</th></tr>
              </thead>
              <tbody>
                {cortes.map((c) => (
                  <tr key={c.uuid}>
                    <td>{c.week_start} — {c.week_end}</td>
                    <td>{clienteMap[c.cliente_id] || '—'}</td>
                    <td>{fmt(c.neto_cliente)}</td>
                    <td>{fmt(c.pago_cliente)}</td>
                    <td>{fmt(c.ganancia_dueno)}</td>
                  </tr>
                ))}
                {cortes.length > 0 && (
                  <tr style={{ fontWeight: 'bold', borderTop: '2px solid var(--border)' }}>
                    <td colSpan={2}>TOTAL</td>
                    <td>{fmt(totalNeto)}</td>
                    <td>{fmt(totalPago)}</td>
                    <td>{fmt(totalGanancia)}</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
}

function getDefaultDesde() {
  const d = new Date();
  d.setMonth(d.getMonth() - 3);
  return d.toISOString().slice(0, 10);
}
