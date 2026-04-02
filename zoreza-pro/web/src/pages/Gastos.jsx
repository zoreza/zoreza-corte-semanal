import { useState, useEffect } from 'react';
import { getGastos, createGasto, deleteGasto, getConfig } from '../api';

export default function Gastos() {
  const [items, setItems] = useState([]);
  const [categorias, setCategorias] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modal, setModal] = useState(false);

  const doFetch = () =>
    Promise.all([
      getGastos(),
      getConfig('categorias_gasto').catch(() => ({ value: 'OTRO' })),
    ])
      .then(([g, cfg]) => {
        setItems(g);
        setCategorias(cfg.value.split(',').map((s) => s.trim()).filter(Boolean));
      })
      .catch(() => {})
      .finally(() => setLoading(false));

  useEffect(() => { doFetch(); }, []);

  const reload = () => {
    setLoading(true);
    doFetch();
  };

  const handleSave = async (data) => {
    await createGasto(data);
    setModal(false);
    reload();
  };

  const handleDelete = async (id) => {
    if (!window.confirm('¿Eliminar este gasto?')) return;
    await deleteGasto(id);
    reload();
  };

  const fmt = (n) => `$${Number(n).toLocaleString('es-MX', { minimumFractionDigits: 2 })}`;

  if (loading) return <div className="spinner" />;

  return (
    <div>
      <div className="flex-between mb-24">
        <h1 className="page-title" style={{ marginBottom: 0 }}>Gastos</h1>
        <button className="btn btn-primary" onClick={() => setModal(true)}>+ Nuevo Gasto</button>
      </div>

      <div className="card">
        <table>
          <thead>
            <tr><th>Fecha</th><th>Categoría</th><th>Descripción</th><th>Monto</th><th>Acciones</th></tr>
          </thead>
          <tbody>
            {items.map((g) => (
              <tr key={g.uuid}>
                <td>{g.fecha}</td>
                <td>{g.categoria || '—'}</td>
                <td>{g.descripcion || '—'}</td>
                <td><strong>{fmt(g.monto)}</strong></td>
                <td>
                  <button className="btn btn-danger btn-sm" onClick={() => handleDelete(g.uuid)}>Eliminar</button>
                </td>
              </tr>
            ))}
            {items.length === 0 && <tr><td colSpan={5}>Sin gastos</td></tr>}
          </tbody>
        </table>
      </div>

      {modal && (
        <GastoModal
          categorias={categorias}
          onClose={() => setModal(false)}
          onSave={handleSave}
        />
      )}
    </div>
  );
}

function GastoModal({ categorias, onClose, onSave }) {
  const [fecha, setFecha] = useState(new Date().toISOString().slice(0, 10));
  const [categoria, setCategoria] = useState(categorias[0] || '');
  const [descripcion, setDescripcion] = useState('');
  const [monto, setMonto] = useState('');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    try {
      await onSave({
        fecha,
        categoria,
        descripcion,
        monto: parseFloat(monto),
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
        <div className="modal-header">Nuevo Gasto</div>
        <div className="modal-body">
          {error && <div className="error-msg">{error}</div>}
          <div className="form-group">
            <label>Fecha</label>
            <input type="date" value={fecha} onChange={(e) => setFecha(e.target.value)} required />
          </div>
          <div className="form-group">
            <label>Categoría</label>
            <select value={categoria} onChange={(e) => setCategoria(e.target.value)} required>
              {categorias.map((cat) => (
                <option key={cat} value={cat}>{cat}</option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label>Descripción</label>
            <input value={descripcion} onChange={(e) => setDescripcion(e.target.value)} />
          </div>
          <div className="form-group">
            <label>Monto</label>
            <input type="number" min="0" step="0.01" value={monto} onChange={(e) => setMonto(e.target.value)} required />
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
