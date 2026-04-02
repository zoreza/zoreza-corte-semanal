import { useState, useEffect } from 'react';
import { getClientes, createCliente, updateCliente } from '../api';

export default function Clientes() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modal, setModal] = useState(null); // null | 'create' | item

  useEffect(() => {
    getClientes().then(setItems).catch(() => {}).finally(() => setLoading(false));
  }, []);

  const reload = () => {
    setLoading(true);
    getClientes().then(setItems).catch(() => {}).finally(() => setLoading(false));
  };

  const handleSave = async (data) => {
    if (typeof modal === 'object' && modal?.uuid) {
      await updateCliente(modal.uuid, data);
    } else {
      await createCliente(data);
    }
    setModal(null);
    reload();
  };

  if (loading) return <div className="spinner" />;

  return (
    <div>
      <div className="flex-between mb-24">
        <h1 className="page-title" style={{ marginBottom: 0 }}>Clientes</h1>
        <button className="btn btn-primary" onClick={() => setModal('create')}>+ Nuevo Cliente</button>
      </div>

      <div className="card">
        <table>
          <thead>
            <tr><th>Nombre</th><th>Teléfono</th><th>Email</th><th>Comisión %</th><th>Estado</th><th>Acciones</th></tr>
          </thead>
          <tbody>
            {items.map((c) => (
              <tr key={c.uuid}>
                <td><strong>{c.nombre}</strong></td>
                <td>{c.telefono || '—'}</td>
                <td>{c.email || '—'}</td>
                <td>{(c.comision_pct * 100).toFixed(0)}%</td>
                <td><span className={`badge ${c.activo ? 'badge-success' : 'badge-danger'}`}>{c.activo ? 'Activo' : 'Inactivo'}</span></td>
                <td>
                  <button className="btn btn-outline btn-sm" onClick={() => setModal(c)}>Editar</button>
                  {' '}
                  <button
                    className={`btn btn-sm ${c.activo ? 'btn-danger' : 'btn-success'}`}
                    onClick={async () => { await updateCliente(c.uuid, { activo: !c.activo }); reload(); }}
                  >
                    {c.activo ? 'Desactivar' : 'Activar'}
                  </button>
                </td>
              </tr>
            ))}
            {items.length === 0 && <tr><td colSpan={6}>Sin clientes</td></tr>}
          </tbody>
        </table>
      </div>

      {modal !== null && (
        <ClienteModal
          item={typeof modal === 'object' ? modal : null}
          onClose={() => setModal(null)}
          onSave={handleSave}
        />
      )}
    </div>
  );
}

function ClienteModal({ item, onClose, onSave }) {
  const [nombre, setNombre] = useState(item?.nombre || '');
  const [telefono, setTelefono] = useState(item?.telefono || '');
  const [email, setEmail] = useState(item?.email || '');
  const [direccion, setDireccion] = useState(item?.direccion_postal || '');
  const [comision, setComision] = useState(item ? (item.comision_pct * 100).toString() : '40');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    try {
      await onSave({
        nombre,
        telefono,
        email: email || null,
        direccion_postal: direccion || null,
        comision_pct: parseFloat(comision) / 100,
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <form className="modal" onClick={(e) => e.stopPropagation()} onSubmit={handleSubmit}>
        <div className="modal-header">{item ? 'Editar Cliente' : 'Nuevo Cliente'}</div>
        <div className="modal-body">
          {error && <div className="error-msg">{error}</div>}
          <div className="form-group">
            <label>Nombre *</label>
            <input value={nombre} onChange={(e) => setNombre(e.target.value)} required />
          </div>
          <div className="form-group">
            <label>Teléfono *</label>
            <input value={telefono} onChange={(e) => setTelefono(e.target.value)} required />
          </div>
          <div className="form-group">
            <label>Correo electrónico</label>
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
          </div>
          <div className="form-group">
            <label>Dirección postal</label>
            <input value={direccion} onChange={(e) => setDireccion(e.target.value)} />
          </div>
          <div className="form-group">
            <label>Comisión (%) *</label>
            <input type="number" min="0" max="100" step="1" value={comision} onChange={(e) => setComision(e.target.value)} required />
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
