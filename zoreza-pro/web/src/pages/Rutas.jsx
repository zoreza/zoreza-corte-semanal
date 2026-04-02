import { useState, useEffect, useCallback } from 'react';
import { getRutas, createRuta, updateRuta, getRutaMaquinas, getMaquinas, assignMaquinaToRuta, unassignMaquinaFromRuta } from '../api';

export default function Rutas() {
  const [rutas, setRutas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modal, setModal] = useState(null);
  const [assignModal, setAssignModal] = useState(null); // ruta object

  const load = useCallback(() => {
    setLoading(true);
    getRutas().then(setRutas).catch(() => {}).finally(() => setLoading(false));
  }, []);

  useEffect(load, [load]);

  const handleSave = async (data) => {
    if (typeof modal === 'object' && modal?.uuid) {
      await updateRuta(modal.uuid, data);
    } else {
      await createRuta(data);
    }
    setModal(null);
    load();
  };

  if (loading) return <div className="spinner" />;

  return (
    <div>
      <div className="flex-between mb-24">
        <h1 className="page-title" style={{ marginBottom: 0 }}>Rutas</h1>
        <button className="btn btn-primary" onClick={() => setModal('create')}>+ Nueva Ruta</button>
      </div>

      <div className="card">
        <table>
          <thead>
            <tr><th>Nombre</th><th>Descripción</th><th>Estado</th><th>Acciones</th></tr>
          </thead>
          <tbody>
            {rutas.map((r) => (
              <tr key={r.uuid}>
                <td><strong>{r.nombre}</strong></td>
                <td>{r.descripcion || '—'}</td>
                <td><span className={`badge ${r.activo ? 'badge-success' : 'badge-danger'}`}>{r.activo ? 'Activa' : 'Inactiva'}</span></td>
                <td>
                  <button className="btn btn-outline btn-sm" onClick={() => setModal(r)}>Editar</button>
                  {' '}
                  <button className="btn btn-outline btn-sm" onClick={() => setAssignModal(r)}>🎰 Máquinas</button>
                  {' '}
                  <button
                    className={`btn btn-sm ${r.activo ? 'btn-danger' : 'btn-success'}`}
                    onClick={async () => { await updateRuta(r.uuid, { activo: !r.activo }); load(); }}
                  >
                    {r.activo ? 'Desactivar' : 'Activar'}
                  </button>
                </td>
              </tr>
            ))}
            {rutas.length === 0 && <tr><td colSpan={4}>Sin rutas</td></tr>}
          </tbody>
        </table>
      </div>

      {modal !== null && (
        <RutaModal
          item={typeof modal === 'object' ? modal : null}
          onClose={() => setModal(null)}
          onSave={handleSave}
        />
      )}

      {assignModal && (
        <AssignMaquinasModal
          ruta={assignModal}
          onClose={() => setAssignModal(null)}
        />
      )}
    </div>
  );
}

function RutaModal({ item, onClose, onSave }) {
  const [nombre, setNombre] = useState(item?.nombre || '');
  const [descripcion, setDescripcion] = useState(item?.descripcion || '');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    try {
      await onSave({ nombre, descripcion });
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <form className="modal" onClick={(e) => e.stopPropagation()} onSubmit={handleSubmit}>
        <div className="modal-header">{item ? 'Editar Ruta' : 'Nueva Ruta'}</div>
        <div className="modal-body">
          {error && <div className="error-msg">{error}</div>}
          <div className="form-group">
            <label>Nombre</label>
            <input value={nombre} onChange={(e) => setNombre(e.target.value)} required />
          </div>
          <div className="form-group">
            <label>Descripción</label>
            <input value={descripcion} onChange={(e) => setDescripcion(e.target.value)} />
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

function AssignMaquinasModal({ ruta, onClose }) {
  const [assigned, setAssigned] = useState([]);
  const [allMaquinas, setAllMaquinas] = useState([]);
  const [loading, setLoading] = useState(true);

  const load = useCallback(() => {
    setLoading(true);
    Promise.all([getRutaMaquinas(ruta.uuid), getMaquinas()])
      .then(([a, all]) => { setAssigned(a); setAllMaquinas(all); })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [ruta.uuid]);

  useEffect(load, [load]);

  const assignedIds = new Set(assigned.map((m) => m.uuid));

  const handleAdd = async (maqId) => {
    await assignMaquinaToRuta(ruta.uuid, maqId);
    load();
  };

  const handleRemove = async (maqId) => {
    await unassignMaquinaFromRuta(ruta.uuid, maqId);
    load();
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()} style={{ maxWidth: 600 }}>
        <div className="modal-header">Máquinas en {ruta.nombre}</div>
        <div className="modal-body">
          {loading ? <div className="spinner" /> : (
            <>
              <h3 style={{ marginBottom: 8 }}>Asignadas ({assigned.length})</h3>
              {assigned.length === 0 && <p>Ninguna máquina asignada</p>}
              {assigned.map((m) => (
                <div key={m.uuid} className="flex-between" style={{ marginBottom: 4, padding: '4px 0' }}>
                  <span>{m.codigo}</span>
                  <button className="btn btn-danger btn-sm" onClick={() => handleRemove(m.uuid)}>Quitar</button>
                </div>
              ))}
              <hr style={{ margin: '16px 0' }} />
              <h3 style={{ marginBottom: 8 }}>Disponibles</h3>
              {allMaquinas.filter((m) => m.activo && !assignedIds.has(m.uuid)).map((m) => (
                <div key={m.uuid} className="flex-between" style={{ marginBottom: 4, padding: '4px 0' }}>
                  <span>{m.codigo}</span>
                  <button className="btn btn-primary btn-sm" onClick={() => handleAdd(m.uuid)}>Agregar</button>
                </div>
              ))}
            </>
          )}
        </div>
        <div className="modal-footer">
          <button className="btn btn-outline" onClick={onClose}>Cerrar</button>
        </div>
      </div>
    </div>
  );
}
