import { useState, useEffect } from 'react';
import { getMaquinas, createMaquina, updateMaquina, getClientes } from '../api';

export default function Maquinas() {
  const [items, setItems] = useState([]);
  const [clientes, setClientes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modal, setModal] = useState(null);

  const load = () => {
    setLoading(true);
    Promise.all([getMaquinas(), getClientes()])
      .then(([m, c]) => { setItems(m); setClientes(c); })
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  const handleSave = async (data) => {
    if (typeof modal === 'object' && modal?.uuid) {
      await updateMaquina(modal.uuid, data);
    } else {
      await createMaquina(data);
    }
    setModal(null);
    load();
  };

  const clienteMap = Object.fromEntries(clientes.map((c) => [c.uuid, c.nombre]));

  if (loading) return <div className="spinner" />;

  return (
    <div>
      <div className="flex-between mb-24">
        <h1 className="page-title" style={{ marginBottom: 0 }}>Máquinas</h1>
        <button className="btn btn-primary" onClick={() => setModal('create')}>+ Nueva Máquina</button>
      </div>

      <div className="card">
        <table>
          <thead>
            <tr><th>Número de Máquina</th><th>Fondo</th><th>Cliente</th><th>Estado</th><th>Acciones</th></tr>
          </thead>
          <tbody>
            {items.map((m) => (
              <tr key={m.uuid}>
                <td><strong>{m.codigo}</strong></td>
                <td>${Number(m.fondo || 0).toLocaleString('es-MX', { minimumFractionDigits: 2 })}</td>
                <td>{m.cliente_id ? (clienteMap[m.cliente_id] || '—') : <span className="badge">Pool</span>}</td>
                <td><span className={`badge ${m.activo ? 'badge-success' : 'badge-danger'}`}>{m.activo ? 'Activa' : 'Inactiva'}</span></td>
                <td>
                  <button className="btn btn-outline btn-sm" onClick={() => setModal(m)}>Editar</button>
                  {' '}
                  <button
                    className={`btn btn-sm ${m.activo ? 'btn-danger' : 'btn-success'}`}
                    onClick={async () => { await updateMaquina(m.uuid, { activo: !m.activo }); load(); }}
                  >
                    {m.activo ? 'Desactivar' : 'Activar'}
                  </button>
                </td>
              </tr>
            ))}
            {items.length === 0 && <tr><td colSpan={5}>Sin máquinas</td></tr>}
          </tbody>
        </table>
      </div>

      {modal !== null && (
        <MaquinaModal
          item={typeof modal === 'object' ? modal : null}
          clientes={clientes}
          onClose={() => setModal(null)}
          onSave={handleSave}
        />
      )}
    </div>
  );
}

function MaquinaModal({ item, clientes, onClose, onSave }) {
  const [codigo, setCodigo] = useState(item?.codigo || '');
  const [fondo, setFondo] = useState(item?.fondo?.toString() || '0');
  const [clienteId, setClienteId] = useState(item?.cliente_id || '');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    try {
      await onSave({ codigo, fondo: parseFloat(fondo), cliente_id: clienteId || null });
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <form className="modal" onClick={(e) => e.stopPropagation()} onSubmit={handleSubmit}>
        <div className="modal-header">{item ? 'Editar Máquina' : 'Nueva Máquina'}</div>
        <div className="modal-body">
          {error && <div className="error-msg">{error}</div>}
          <div className="form-group">
            <label>Número de Máquina *</label>
            <input value={codigo} onChange={(e) => setCodigo(e.target.value)} required />
          </div>
          <div className="form-group">
            <label>Fondo *</label>
            <input type="number" min="0" step="0.01" value={fondo} onChange={(e) => setFondo(e.target.value)} required />
          </div>
          <div className="form-group">
            <label>Cliente (vacío = Pool)</label>
            <select value={clienteId} onChange={(e) => setClienteId(e.target.value)}>
              <option value="">— Sin cliente (Pool) —</option>
              {clientes.filter((c) => c.activo).map((c) => (
                <option key={c.uuid} value={c.uuid}>{c.nombre}</option>
              ))}
            </select>
          </div>
        </div>
        <div className="modal-footer">
          <button type="button" className="btn btn-outline" onClick={onClose}>Cancelar</button>
          <button className="btn btn-primary" disabled={saving}>{saving ? 'Guardando...' : 'Guardar'}</button>
        </div>
      </form>
    </div>
  );
}
