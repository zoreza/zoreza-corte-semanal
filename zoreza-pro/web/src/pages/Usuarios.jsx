import { useState, useEffect } from 'react';
import { getUsuarios, createUsuario, updateUsuario } from '../api';

const ROLES = ['ADMIN', 'SUPERVISOR', 'OPERADOR'];

export default function Usuarios() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modal, setModal] = useState(null);

  const load = () => {
    setLoading(true);
    getUsuarios().then(setItems).catch(() => {}).finally(() => setLoading(false));
  };

  useEffect(load, []);

  const handleSave = async (data) => {
    if (typeof modal === 'object' && modal?.uuid) {
      await updateUsuario(modal.uuid, data);
    } else {
      await createUsuario(data);
    }
    setModal(null);
    load();
  };

  if (loading) return <div className="spinner" />;

  return (
    <div>
      <div className="flex-between mb-24">
        <h1 className="page-title" style={{ marginBottom: 0 }}>Usuarios</h1>
        <button className="btn btn-primary" onClick={() => setModal('create')}>+ Nuevo Usuario</button>
      </div>

      <div className="card">
        <table>
          <thead>
            <tr><th>Username</th><th>Nombre</th><th>Teléfono</th><th>Email</th><th>Rol</th><th>Estado</th><th>Acciones</th></tr>
          </thead>
          <tbody>
            {items.map((u) => (
              <tr key={u.uuid}>
                <td><strong>{u.username}</strong></td>
                <td>{u.nombre}</td>
                <td>{u.telefono || '—'}</td>
                <td>{u.email || '—'}</td>
                <td><span className="badge">{u.rol}</span></td>
                <td><span className={`badge ${u.activo ? 'badge-success' : 'badge-danger'}`}>{u.activo ? 'Activo' : 'Inactivo'}</span></td>
                <td>
                  <button className="btn btn-outline btn-sm" onClick={() => setModal(u)}>Editar</button>
                  {' '}
                  <button
                    className={`btn btn-sm ${u.activo ? 'btn-danger' : 'btn-success'}`}
                    onClick={async () => { await updateUsuario(u.uuid, { activo: !u.activo }); load(); }}
                  >
                    {u.activo ? 'Desactivar' : 'Activar'}
                  </button>
                </td>
              </tr>
            ))}
            {items.length === 0 && <tr><td colSpan={7}>Sin usuarios</td></tr>}
          </tbody>
        </table>
      </div>

      {modal !== null && (
        <UsuarioModal
          item={typeof modal === 'object' ? modal : null}
          onClose={() => setModal(null)}
          onSave={handleSave}
        />
      )}
    </div>
  );
}

function UsuarioModal({ item, onClose, onSave }) {
  const [username, setUsername] = useState(item?.username || '');
  const [nombre, setNombre] = useState(item?.nombre || '');
  const [telefono, setTelefono] = useState(item?.telefono || '');
  const [email, setEmail] = useState(item?.email || '');
  const [rol, setRol] = useState(item?.rol || 'OPERADOR');
  const [password, setPassword] = useState('');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    try {
      const data = { username, nombre, telefono, email, rol };
      if (password) data.password = password;
      await onSave(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <form className="modal" onClick={(e) => e.stopPropagation()} onSubmit={handleSubmit}>
        <div className="modal-header">{item ? 'Editar Usuario' : 'Nuevo Usuario'}</div>
        <div className="modal-body">
          {error && <div className="error-msg">{error}</div>}
          <div className="form-group">
            <label>Username</label>
            <input value={username} onChange={(e) => setUsername(e.target.value)} required disabled={!!item} />
          </div>
          <div className="form-group">
            <label>Nombre completo *</label>
            <input value={nombre} onChange={(e) => setNombre(e.target.value)} required />
          </div>
          <div className="form-group">
            <label>Teléfono *</label>
            <input value={telefono} onChange={(e) => setTelefono(e.target.value)} required />
          </div>
          <div className="form-group">
            <label>Correo electrónico *</label>
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          </div>
          <div className="form-group">
            <label>Rol</label>
            <select value={rol} onChange={(e) => setRol(e.target.value)}>
              {ROLES.map((r) => <option key={r} value={r}>{r}</option>)}
            </select>
          </div>
          <div className="form-group">
            <label>{item ? 'Nueva contraseña (dejar vacío para no cambiar)' : 'Contraseña'}</label>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required={!item} />
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
