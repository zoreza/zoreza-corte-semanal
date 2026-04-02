import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getCortes, getClientes } from '../api';

export default function Cortes() {
  const [items, setItems] = useState([]);
  const [clientes, setClientes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({ estado: '', cliente_id: '' });
  const navigate = useNavigate();

  useEffect(() => {
    getClientes().then(setClientes).catch(() => {});
  }, []);

  useEffect(() => {
    setLoading(true);
    const params = {};
    if (filters.estado) params.estado = filters.estado;
    if (filters.cliente_id) params.cliente_id = filters.cliente_id;
    getCortes(params).then(setItems).catch(() => {}).finally(() => setLoading(false));
  }, [filters]);

  const clienteMap = Object.fromEntries(clientes.map((c) => [c.uuid, c.nombre]));

  const estadoBadge = (estado) => {
    const cls = estado === 'CERRADO' ? 'badge-success' : estado === 'BORRADOR' ? 'badge-warning' : '';
    return <span className={`badge ${cls}`}>{estado}</span>;
  };

  const fmt = (n) => n != null ? `$${Number(n).toLocaleString('es-MX', { minimumFractionDigits: 2 })}` : '—';

  return (
    <div>
      <h1 className="page-title">Cortes Semanales</h1>

      <div className="card mb-24" style={{ display: 'flex', gap: 16, alignItems: 'flex-end', flexWrap: 'wrap' }}>
        <div className="form-group" style={{ margin: 0 }}>
          <label>Estado</label>
          <select value={filters.estado} onChange={(e) => setFilters((f) => ({ ...f, estado: e.target.value }))}>
            <option value="">Todos</option>
            <option value="BORRADOR">Borrador</option>
            <option value="CERRADO">Cerrado</option>
          </select>
        </div>
        <div className="form-group" style={{ margin: 0 }}>
          <label>Cliente</label>
          <select value={filters.cliente_id} onChange={(e) => setFilters((f) => ({ ...f, cliente_id: e.target.value }))}>
            <option value="">Todos</option>
            {clientes.map((c) => (
              <option key={c.uuid} value={c.uuid}>{c.nombre}</option>
            ))}
          </select>
        </div>
      </div>

      {loading ? <div className="spinner" /> : (
        <div className="card">
          <table>
            <thead>
              <tr>
                <th>Semana</th>
                <th>Cliente</th>
                <th>Neto Cliente</th>
                <th>Ganancia Dueño</th>
                <th>Estado</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {items.map((c) => (
                <tr key={c.uuid}>
                  <td>{c.week_start} — {c.week_end}</td>
                  <td>{clienteMap[c.cliente_id] || c.cliente_nombre || '—'}</td>
                  <td>{fmt(c.neto_cliente)}</td>
                  <td>{fmt(c.ganancia_dueno)}</td>
                  <td>{estadoBadge(c.estado)}</td>
                  <td>
                    <button className="btn btn-outline btn-sm" onClick={() => navigate(`/cortes/${c.uuid}`)}>
                      Ver Detalle
                    </button>
                  </td>
                </tr>
              ))}
              {items.length === 0 && <tr><td colSpan={6}>Sin cortes</td></tr>}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
