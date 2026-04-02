import { useState, useEffect } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend,
} from 'recharts';
import { getDashboard, getCortes, getGastos } from '../api';

const COLORS = ['#38a169', '#d69e2e', '#e53e3e', '#3182ce', '#805ad5', '#dd6b20'];

const money = (v) => `$${(v || 0).toLocaleString('es-MX', { minimumFractionDigits: 0 })}`;

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [recentCortes, setRecentCortes] = useState([]);
  const [gastosByCat, setGastosByCat] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      getDashboard(),
      getCortes({ limit: 10 }),
      getGastos(),
    ]).then(([d, cortes, gastos]) => {
      setData(d);
      setRecentCortes(cortes);
      // Aggregate gastos by category
      const catMap = {};
      gastos.forEach((g) => {
        catMap[g.categoria] = (catMap[g.categoria] || 0) + g.monto;
      });
      setGastosByCat(Object.entries(catMap).map(([name, value]) => ({ name, value })));
    }).catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="spinner" />;
  if (!data) return <p>Error cargando dashboard</p>;

  const chartData = recentCortes
    .filter((c) => c.estado === 'CERRADO')
    .slice(0, 8)
    .reverse()
    .map((c) => ({
      name: (c.cliente_nombre || '').substring(0, 10),
      neto: c.neto_cliente,
      ganancia: c.ganancia_dueno,
    }));

  return (
    <div>
      <h1 className="page-title">Dashboard</h1>

      <div className="kpi-grid">
        <div className="kpi-card">
          <div className="label">Total cortes</div>
          <div className="value primary">{data.total_cortes}</div>
        </div>
        <div className="kpi-card">
          <div className="label">Cortes cerrados</div>
          <div className="value primary">{data.cortes_cerrados}</div>
        </div>
        <div className="kpi-card">
          <div className="label">Neto clientes</div>
          <div className="value money">{money(data.total_neto)}</div>
        </div>
        <div className="kpi-card">
          <div className="label">Ganancia dueño</div>
          <div className="value money">{money(data.total_ganancia_dueno)}</div>
        </div>
        <div className="kpi-card">
          <div className="label">Total gastos</div>
          <div className="value danger">{money(data.total_gastos)}</div>
        </div>
        <div className="kpi-card">
          <div className="label">Ganancia neta</div>
          <div className="value money">{money(data.ganancia_neta)}</div>
        </div>
      </div>

      <div className="grid-2 mb-24">
        <div className="card">
          <div className="card-header"><h2>Últimos cortes cerrados</h2></div>
          <div className="card-body">
            {chartData.length > 0 ? (
              <ResponsiveContainer width="100%" height={260}>
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" fontSize={12} />
                  <YAxis fontSize={12} />
                  <Tooltip formatter={(v) => money(v)} />
                  <Bar dataKey="neto" name="Neto" fill="#3182ce" radius={[4,4,0,0]} />
                  <Bar dataKey="ganancia" name="Ganancia" fill="#38a169" radius={[4,4,0,0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : <p style={{ color: '#718096' }}>Sin datos</p>}
          </div>
        </div>

        <div className="card">
          <div className="card-header"><h2>Gastos por categoría</h2></div>
          <div className="card-body">
            {gastosByCat.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie data={gastosByCat} dataKey="value" nameKey="name" cx="50%" cy="45%" outerRadius={80} label={({ name, value }) => `${name} ${money(value)}`} labelLine={{ stroke: '#718096' }} fontSize={12}>
                    {gastosByCat.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                  </Pie>
                  <Legend wrapperStyle={{ fontSize: 12 }} />
                  <Tooltip formatter={(v) => money(v)} />
                </PieChart>
              </ResponsiveContainer>
            ) : <p style={{ color: '#718096' }}>Sin gastos</p>}
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-header"><h2>Cortes recientes</h2></div>
        <table>
          <thead>
            <tr><th>Cliente</th><th>Semana</th><th>Estado</th><th>Neto</th><th>Ganancia</th></tr>
          </thead>
          <tbody>
            {recentCortes.map((c) => (
              <tr key={c.uuid}>
                <td>{c.cliente_nombre}</td>
                <td>{c.week_start} → {c.week_end}</td>
                <td><span className={`badge ${c.estado === 'CERRADO' ? 'badge-success' : 'badge-warning'}`}>{c.estado}</span></td>
                <td>{money(c.neto_cliente)}</td>
                <td>{money(c.ganancia_dueno)}</td>
              </tr>
            ))}
            {recentCortes.length === 0 && <tr><td colSpan={5}>Sin cortes</td></tr>}
          </tbody>
        </table>
      </div>
    </div>
  );
}
