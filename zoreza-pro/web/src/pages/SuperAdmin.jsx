/**
 * SuperAdmin panel — Zoreza Labs tenant management.
 * Accessed at /zoreza-admin/...
 */
import { useState, useEffect, useCallback } from 'react';
import { Routes, Route, NavLink, Navigate } from 'react-router-dom';

const SA_API = '/zoreza-admin/api';

/* ── Dark theme styles ─────────────────────────────────────────────── */
const dark = {
  page: { background: '#000', color: '#e2e8f0', minHeight: '100vh' },
  sidebar: { background: '#0a0a0a', borderRight: '1px solid #1a1a1a' },
  main: { background: '#000' },
  card: { background: '#111', borderRadius: 8, border: '1px solid #222', overflow: 'hidden' },
  table: { background: '#111' },
  th: { background: '#0a0a0a', color: '#999', borderBottom: '1px solid #222' },
  td: { borderBottom: '1px solid #1a1a1a', color: '#ccc' },
  trHover: { background: '#1a1a1a' },
  input: { background: '#1a1a1a', border: '1px solid #333', color: '#e2e8f0', borderRadius: 6, padding: '8px 12px', width: '100%', fontSize: '.9rem', fontFamily: 'inherit' },
  modal: { background: '#111', border: '1px solid #333', color: '#e2e8f0' },
  modalHeader: { borderBottom: '1px solid #222' },
  modalFooter: { borderTop: '1px solid #222' },
  label: { color: '#aaa' },
  title: { color: '#fff' },
  muted: { color: '#666' },
  accent: '#E87C1E',
  accentLight: '#f59e42',
};

let saToken = localStorage.getItem('sa_access_token');

async function saRequest(path, options = {}) {
  const url = `${SA_API}${path}`;
  const headers = { 'Content-Type': 'application/json', ...options.headers };
  if (saToken) headers['Authorization'] = `Bearer ${saToken}`;
  const res = await fetch(url, { ...options, headers });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Error ${res.status}`);
  }
  if (res.status === 204) return null;
  return res.json();
}

function saLogout() {
  saToken = null;
  localStorage.removeItem('sa_access_token');
  localStorage.removeItem('sa_refresh_token');
}

export default function SuperAdmin() {
  const [admin, setAdmin] = useState(null);
  const [checking, setChecking] = useState(() => !!saToken);

  useEffect(() => {
    if (!saToken) return;
    let cancelled = false;
    saRequest('/auth/me')
      .then((u) => { if (!cancelled) setAdmin(u); })
      .catch(() => { if (!cancelled) { saLogout(); setAdmin(null); } })
      .finally(() => { if (!cancelled) setChecking(false); });
    return () => { cancelled = true; };
  }, []);

  if (checking) return <div style={dark.page}><div className="spinner" /></div>;
  if (!admin) return <SALogin onLogin={setAdmin} />;

  return (
    <div className="app-layout" style={dark.page}>
      <aside className="sidebar" style={dark.sidebar}>
        <div className="sidebar-brand" style={{ padding: '16px 20px', borderBottom: '1px solid #1a1a1a', textAlign: 'center' }}>
          <img src="/zoreza-labs-logo.svg" alt="Zoreza Labs" style={{ width: 120, height: 'auto', marginBottom: 4 }} />
        </div>
        <nav className="sidebar-nav">
          <NavLink to="/" end className={({ isActive }) => isActive ? 'active' : ''}>
            <span>🏢</span> Tenants
          </NavLink>
          <NavLink to="/releases" className={({ isActive }) => isActive ? 'active' : ''}>
            <span>📱</span> App Releases
          </NavLink>
        </nav>
        <div className="sidebar-footer" style={{ opacity: 1, borderTop: '1px solid #1a1a1a' }}>
          <div style={{ color: '#fff', fontWeight: 500, fontSize: '.9rem' }}>{admin.nombre}</div>
          <div style={{ marginTop: 4, fontSize: '0.75rem', color: dark.accent, fontWeight: 600, letterSpacing: 1 }}>SUPERADMIN</div>
          <button
            className="btn btn-sm"
            style={{ marginTop: 10, width: '100%', background: 'transparent', border: '1px solid #333', color: '#999' }}
            onClick={() => { saLogout(); setAdmin(null); }}
          >
            Cerrar sesión
          </button>
        </div>
      </aside>
      <main className="main-content" style={dark.main}>
        <Routes>
          <Route path="/" element={<TenantsPage />} />
          <Route path="/releases" element={<ReleasesPage />} />
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </main>
    </div>
  );
}

/* ── Login ─────────────────────────────────────────────────────────── */
function SALogin({ onLogin }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const res = await fetch(`${SA_API}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      });
      if (!res.ok) { const b = await res.json().catch(() => ({})); throw new Error(b.detail || `Error ${res.status}`); }
      const data = await res.json();
      saToken = data.access_token;
      localStorage.setItem('sa_access_token', data.access_token);
      localStorage.setItem('sa_refresh_token', data.refresh_token);
      onLogin({ nombre: data.nombre, rol: data.rol });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container" style={{ background: '#000' }}>
      <form className="login-box" onSubmit={handleSubmit} style={{ background: '#111', border: '1px solid #222', color: '#e2e8f0' }}>
        <div style={{ textAlign: 'center', marginBottom: 16 }}>
          <img src="/zoreza-labs-logo.svg" alt="Zoreza Labs" style={{ width: 180, height: 'auto' }} />
        </div>
        <p className="subtitle" style={{ color: '#888' }}>Panel de Administración</p>
        {error && <div className="error-msg">{error}</div>}
        <div className="form-group">
          <label style={{ color: '#aaa' }}>Usuario</label>
          <input value={username} onChange={(e) => setUsername(e.target.value)} required autoFocus style={dark.input} />
        </div>
        <div className="form-group">
          <label style={{ color: '#aaa' }}>Contraseña</label>
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required style={dark.input} />
        </div>
        <button className="btn btn-primary" style={{ width: '100%', background: dark.accent, borderColor: dark.accent, color: '#fff', fontWeight: 600 }} disabled={loading}>
          {loading ? 'Ingresando...' : 'Ingresar'}
        </button>
      </form>
    </div>
  );
}

/* ── Tenants Page ──────────────────────────────────────────────────── */
function TenantsPage() {
  const [tenants, setTenants] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modal, setModal] = useState(false);
  const [pwModal, setPwModal] = useState(null); // slug for password reset

  const load = useCallback(() => {
    setLoading(true);
    saRequest('/tenants').then(setTenants).catch(() => {}).finally(() => setLoading(false));
  }, []);
  useEffect(() => {
    saRequest('/tenants').then(setTenants).catch(() => {}).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="spinner" />;

  return (
    <div>
      <div className="flex-between mb-24">
        <h1 className="page-title" style={dark.title}>Tenants</h1>
        <button className="btn" style={{ background: dark.accent, color: '#fff', fontWeight: 600 }} onClick={() => setModal(true)}>+ Nuevo Tenant</button>
      </div>

      <div style={dark.card}>
        <table>
          <thead>
            <tr>
              <th style={dark.th}>Slug</th>
              <th style={dark.th}>Nombre</th>
              <th style={dark.th}>Contacto</th>
              <th style={dark.th}>Plan</th>
              <th style={dark.th}>Estado</th>
              <th style={dark.th}>Creado</th>
              <th style={dark.th}>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {tenants.map((t) => (
              <tr key={t.uuid} style={{ cursor: 'default' }}
                onMouseEnter={e => e.currentTarget.style.background = '#1a1a1a'}
                onMouseLeave={e => e.currentTarget.style.background = ''}
              >
                <td style={dark.td}>
                  <strong><a href={`/${t.slug}/`} target="_blank" rel="noopener noreferrer" style={{ color: dark.accent }}>{t.slug}</a></strong>
                </td>
                <td style={{ ...dark.td, color: '#fff' }}>{t.nombre}</td>
                <td style={dark.td}>
                  {t.contacto_nombre || '—'}
                  {t.contacto_email && <div style={{ fontSize: '0.8rem', color: '#666' }}>{t.contacto_email}</div>}
                </td>
                <td style={dark.td}><span className="badge" style={{ background: '#222', color: '#aaa' }}>{t.plan}</span></td>
                <td style={dark.td}>
                  <span style={{
                    display: 'inline-block', padding: '2px 8px', borderRadius: 12, fontSize: '.75rem', fontWeight: 600,
                    background: t.activo ? 'rgba(56,161,105,.15)' : 'rgba(229,62,62,.15)',
                    color: t.activo ? '#68d391' : '#fc8181',
                  }}>
                    {t.activo ? 'Activo' : 'Inactivo'}
                  </span>
                </td>
                <td style={{ ...dark.td, fontSize: '0.85rem', color: '#888' }}>{t.created_at?.split('T')[0]}</td>
                <td style={{ ...dark.td, whiteSpace: 'nowrap' }}>
                  <div style={{ display: 'flex', gap: 4 }}>
                    <button
                      className="btn btn-sm"
                      style={{ background: '#1a1a1a', border: '1px solid #333', color: '#ccc', fontSize: '.78rem' }}
                      onClick={() => setPwModal(t.slug)}
                      title="Cambiar contraseña del admin"
                    >
                      🔑 Contraseña
                    </button>
                    <button
                      className={`btn btn-sm ${t.activo ? 'btn-danger' : 'btn-success'}`}
                      onClick={async () => {
                        await saRequest(`/tenants/${t.slug}`, {
                          method: 'PUT',
                          body: JSON.stringify({ activo: !t.activo }),
                        });
                        load();
                      }}
                    >
                      {t.activo ? 'Desactivar' : 'Activar'}
                    </button>
                  </div>
                </td>
              </tr>
            ))}
            {tenants.length === 0 && <tr><td colSpan={7} style={{ ...dark.td, textAlign: 'center', padding: '2rem', color: '#666' }}>Sin tenants</td></tr>}
          </tbody>
        </table>
      </div>

      {modal && <NewTenantModal onClose={() => setModal(false)} onCreated={() => { setModal(false); load(); }} />}
      {pwModal && <ResetPasswordModal slug={pwModal} onClose={() => setPwModal(null)} />}
    </div>
  );
}

/* ── New Tenant Modal ──────────────────────────────────────────────── */
function NewTenantModal({ onClose, onCreated }) {
  const [form, setForm] = useState({
    slug: '', nombre: '', contacto_nombre: '', contacto_email: '', contacto_telefono: '', admin_password: 'admin123',
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    try {
      await saRequest('/tenants', { method: 'POST', body: JSON.stringify(form) });
      onCreated();
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose} style={{ background: 'rgba(0,0,0,.7)' }}>
      <form className="modal" onClick={(e) => e.stopPropagation()} onSubmit={handleSubmit} style={dark.modal}>
        <div className="modal-header" style={dark.modalHeader}>Nuevo Tenant</div>
        <div className="modal-body">
          {error && <div className="error-msg">{error}</div>}
          <div className="form-group">
            <label style={dark.label}>Slug (URL) *</label>
            <input value={form.slug} onChange={set('slug')} required placeholder="mi-negocio" pattern="[a-z0-9][a-z0-9\-]{1,48}[a-z0-9]" style={dark.input} />
            <p style={{ fontSize: '0.8rem', color: '#666', marginTop: 4 }}>Letras minúsculas, números y guiones. Se accede en: zorezalabs.mx/<b style={{ color: dark.accent }}>{form.slug || '...'}</b></p>
          </div>
          <div className="form-group">
            <label style={dark.label}>Nombre del Negocio *</label>
            <input value={form.nombre} onChange={set('nombre')} required style={dark.input} />
          </div>
          <div className="form-group">
            <label style={dark.label}>Nombre de Contacto</label>
            <input value={form.contacto_nombre} onChange={set('contacto_nombre')} style={dark.input} />
          </div>
          <div className="form-group">
            <label style={dark.label}>Email de Contacto</label>
            <input type="email" value={form.contacto_email} onChange={set('contacto_email')} style={dark.input} />
          </div>
          <div className="form-group">
            <label style={dark.label}>Teléfono de Contacto</label>
            <input value={form.contacto_telefono} onChange={set('contacto_telefono')} style={dark.input} />
          </div>
          <div className="form-group">
            <label style={dark.label}>Contraseña Admin Inicial</label>
            <input value={form.admin_password} onChange={set('admin_password')} placeholder="admin123" style={dark.input} />
          </div>
        </div>
        <div className="modal-footer" style={dark.modalFooter}>
          <button type="button" className="btn" style={{ background: '#222', border: '1px solid #333', color: '#aaa' }} onClick={onClose}>Cancelar</button>
          <button className="btn" style={{ background: dark.accent, color: '#fff', fontWeight: 600 }} disabled={saving}>{saving ? 'Creando...' : 'Crear Tenant'}</button>
        </div>
      </form>
    </div>
  );
}

/* ── Reset Password Modal ──────────────────────────────────────────── */
function ResetPasswordModal({ slug, onClose }) {
  const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (password.length < 6) { setError('Mínimo 6 caracteres'); return; }
    if (password !== confirm) { setError('Las contraseñas no coinciden'); return; }
    setSaving(true);
    setError('');
    try {
      await saRequest(`/tenants/${slug}/reset-password`, {
        method: 'POST',
        body: JSON.stringify({ password }),
      });
      setSuccess(true);
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose} style={{ background: 'rgba(0,0,0,.7)' }}>
      <form className="modal" onClick={(e) => e.stopPropagation()} onSubmit={handleSubmit} style={{ ...dark.modal, maxWidth: 420 }}>
        <div className="modal-header" style={dark.modalHeader}>
          🔑 Cambiar contraseña — <span style={{ color: dark.accent }}>{slug}</span>
        </div>
        <div className="modal-body">
          {error && <div className="error-msg">{error}</div>}
          {success ? (
            <div style={{ textAlign: 'center', padding: '20px 0' }}>
              <div style={{ fontSize: '2rem', marginBottom: 8 }}>✅</div>
              <p style={{ color: '#68d391', fontWeight: 600 }}>Contraseña actualizada correctamente</p>
              <p style={{ color: '#888', fontSize: '.85rem', marginTop: 8 }}>El admin del tenant <b>{slug}</b> ya puede usar la nueva contraseña.</p>
            </div>
          ) : (
            <>
              <p style={{ color: '#888', fontSize: '.85rem', marginBottom: 16 }}>
                Esto cambiará la contraseña del usuario <b>admin</b> del tenant <b style={{ color: dark.accent }}>{slug}</b>.
              </p>
              <div className="form-group">
                <label style={dark.label}>Nueva contraseña *</label>
                <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required minLength={6} placeholder="Mínimo 6 caracteres" style={dark.input} autoFocus />
              </div>
              <div className="form-group">
                <label style={dark.label}>Confirmar contraseña *</label>
                <input type="password" value={confirm} onChange={(e) => setConfirm(e.target.value)} required placeholder="Repetir contraseña" style={dark.input} />
              </div>
            </>
          )}
        </div>
        <div className="modal-footer" style={dark.modalFooter}>
          <button type="button" className="btn" style={{ background: '#222', border: '1px solid #333', color: '#aaa' }} onClick={onClose}>
            {success ? 'Cerrar' : 'Cancelar'}
          </button>
          {!success && (
            <button className="btn" style={{ background: dark.accent, color: '#fff', fontWeight: 600 }} disabled={saving}>
              {saving ? 'Guardando...' : 'Cambiar contraseña'}
            </button>
          )}
        </div>
      </form>
    </div>
  );
}

/* ── Releases Page ─────────────────────────────────────────────────── */
function ReleasesPage() {
  const [releases, setReleases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modal, setModal] = useState(false);

  const load = useCallback(() => {
    setLoading(true);
    saRequest('/releases').then(setReleases).catch(() => {}).finally(() => setLoading(false));
  }, []);
  useEffect(() => {
    saRequest('/releases').then(setReleases).catch(() => {}).finally(() => setLoading(false));
  }, []);

  const formatSize = (bytes) => {
    if (!bytes) return '—';
    return (bytes / 1024 / 1024).toFixed(1) + ' MB';
  };

  if (loading) return <div className="spinner" />;

  return (
    <div>
      <div className="flex-between mb-24">
        <h1 className="page-title" style={dark.title}>App Releases (APK)</h1>
        <button className="btn" style={{ background: dark.accent, color: '#fff', fontWeight: 600 }} onClick={() => setModal(true)}>+ Subir APK</button>
      </div>

      <div style={dark.card}>
        <table>
          <thead>
            <tr>
              <th style={dark.th}>Versión</th>
              <th style={dark.th}>Código</th>
              <th style={dark.th}>Tamaño</th>
              <th style={dark.th}>Notas</th>
              <th style={dark.th}>Obligatoria</th>
              <th style={dark.th}>Estado</th>
              <th style={dark.th}>Fecha</th>
              <th style={dark.th}>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {releases.map((r) => (
              <tr key={r.uuid}
                onMouseEnter={e => e.currentTarget.style.background = '#1a1a1a'}
                onMouseLeave={e => e.currentTarget.style.background = ''}
              >
                <td style={{ ...dark.td, color: '#fff' }}><strong>v{r.version_name}</strong></td>
                <td style={dark.td}>{r.version_code}</td>
                <td style={dark.td}>{formatSize(r.file_size)}</td>
                <td style={{ ...dark.td, maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {r.release_notes || '—'}
                </td>
                <td style={dark.td}>
                  <span style={{
                    display: 'inline-block', padding: '2px 8px', borderRadius: 12, fontSize: '.75rem', fontWeight: 600,
                    background: r.is_mandatory ? 'rgba(229,62,62,.15)' : '#222',
                    color: r.is_mandatory ? '#fc8181' : '#888',
                  }}>
                    {r.is_mandatory ? 'Sí' : 'No'}
                  </span>
                </td>
                <td style={dark.td}>
                  <span style={{
                    display: 'inline-block', padding: '2px 8px', borderRadius: 12, fontSize: '.75rem', fontWeight: 600,
                    background: r.activo ? 'rgba(56,161,105,.15)' : 'rgba(229,62,62,.15)',
                    color: r.activo ? '#68d391' : '#fc8181',
                  }}>
                    {r.activo ? 'Activa' : 'Inactiva'}
                  </span>
                </td>
                <td style={{ ...dark.td, fontSize: '0.85rem', color: '#888' }}>{r.created_at?.split('T')[0]}</td>
                <td style={dark.td}>
                  <div style={{ display: 'flex', gap: 4 }}>
                    <a href={r.download_url} className="btn btn-sm" style={{ background: '#1a1a1a', border: '1px solid #333', color: '#ccc', textDecoration: 'none' }} download>⬇ Descargar</a>
                    <button
                      className="btn btn-sm btn-danger"
                      onClick={async () => {
                        if (!confirm(`¿Eliminar v${r.version_name}?`)) return;
                        await saRequest(`/releases/${r.uuid}`, { method: 'DELETE' });
                        load();
                      }}
                    >
                      Eliminar
                    </button>
                  </div>
                </td>
              </tr>
            ))}
            {releases.length === 0 && (
              <tr>
                <td colSpan={8} style={{ ...dark.td, textAlign: 'center', padding: '2rem', color: '#666' }}>
                  No hay releases. Sube tu primer APK para habilitar actualizaciones automáticas.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {modal && <UploadApkModal onClose={() => setModal(false)} onUploaded={() => { setModal(false); load(); }} />}
    </div>
  );
}

/* ── Upload APK Modal ──────────────────────────────────────────────── */
function UploadApkModal({ onClose, onUploaded }) {
  const [versionName, setVersionName] = useState('');
  const [versionCode, setVersionCode] = useState('');
  const [releaseNotes, setReleaseNotes] = useState('');
  const [isMandatory, setIsMandatory] = useState(false);
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) { setError('Selecciona un archivo APK'); return; }
    setUploading(true);
    setError('');
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('version_name', versionName);
      formData.append('version_code', versionCode);
      formData.append('release_notes', releaseNotes);
      formData.append('is_mandatory', isMandatory);

      const xhr = new XMLHttpRequest();
      xhr.open('POST', `${SA_API}/releases`);
      if (saToken) xhr.setRequestHeader('Authorization', `Bearer ${saToken}`);

      xhr.upload.onprogress = (ev) => {
        if (ev.lengthComputable) setProgress(Math.round((ev.loaded / ev.total) * 100));
      };

      await new Promise((resolve, reject) => {
        xhr.onload = () => {
          if (xhr.status >= 200 && xhr.status < 300) resolve();
          else {
            try { reject(new Error(JSON.parse(xhr.responseText).detail)); }
            catch { reject(new Error(`Error ${xhr.status}`)); }
          }
        };
        xhr.onerror = () => reject(new Error('Error de red'));
        xhr.send(formData);
      });

      onUploaded();
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose} style={{ background: 'rgba(0,0,0,.85)' }}>
      <form onClick={(e) => e.stopPropagation()} onSubmit={handleSubmit} style={{ ...dark.modal, maxWidth: 500 }}>
        <div style={dark.modalHeader}>Subir APK</div>
        <div style={{ padding: '1.25rem' }}>
          {error && <div style={{ background: 'rgba(229,62,62,.15)', color: '#fc8181', padding: '8px 12px', borderRadius: 6, fontSize: '.85rem', marginBottom: 12 }}>{error}</div>}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
            <div style={{ marginBottom: 12 }}>
              <label style={dark.label}>Versión (nombre) *</label>
              <input value={versionName} onChange={(e) => setVersionName(e.target.value)} required placeholder="1.2.0" pattern="\d+\.\d+\.\d+" style={dark.input} />
            </div>
            <div style={{ marginBottom: 12 }}>
              <label style={dark.label}>Código de versión *</label>
              <input type="number" value={versionCode} onChange={(e) => setVersionCode(e.target.value)} required min="1" placeholder="2" style={dark.input} />
              <p style={{ fontSize: '0.75rem', color: '#888', marginTop: 2 }}>Debe ser mayor al anterior</p>
            </div>
          </div>
          <div style={{ marginBottom: 12 }}>
            <label style={dark.label}>Notas de la versión</label>
            <textarea value={releaseNotes} onChange={(e) => setReleaseNotes(e.target.value)} rows={3} placeholder="Correcciones y mejoras..." style={{ ...dark.input, resize: 'vertical' }} />
          </div>
          <div style={{ marginBottom: 12 }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer', color: '#ccc', fontSize: '.85rem' }}>
              <input type="checkbox" checked={isMandatory} onChange={(e) => setIsMandatory(e.target.checked)} />
              Actualización obligatoria
            </label>
            <p style={{ fontSize: '0.75rem', color: '#888', marginTop: 2 }}>Si se marca, el usuario no podrá omitir la actualización</p>
          </div>
          <div style={{ marginBottom: 12 }}>
            <label style={dark.label}>Archivo APK *</label>
            <input type="file" accept=".apk" onChange={(e) => setFile(e.target.files[0])} required style={{ ...dark.input, padding: 8 }} />
            {file && <p style={{ fontSize: '0.8rem', marginTop: 4, color: '#aaa' }}>{file.name} ({(file.size / 1024 / 1024).toFixed(1)} MB)</p>}
          </div>
          {uploading && (
            <div style={{ marginTop: 8 }}>
              <div style={{ background: '#222', borderRadius: 4, overflow: 'hidden' }}>
                <div style={{ background: dark.accent, height: 8, width: `${progress}%`, transition: 'width 0.3s' }} />
              </div>
              <p style={{ fontSize: '0.8rem', textAlign: 'center', marginTop: 4, color: '#aaa' }}>{progress}%</p>
            </div>
          )}
        </div>
        <div style={dark.modalFooter}>
          <button type="button" onClick={onClose} disabled={uploading} style={{ padding: '8px 16px', borderRadius: 6, border: '1px solid #333', background: '#1a1a1a', color: '#ccc', cursor: 'pointer' }}>Cancelar</button>
          <button disabled={uploading} style={{ padding: '8px 16px', borderRadius: 6, border: 'none', background: uploading ? '#555' : dark.accent, color: '#fff', cursor: uploading ? 'not-allowed' : 'pointer', fontWeight: 600 }}>
            {uploading ? `Subiendo... ${progress}%` : 'Subir APK'}
          </button>
        </div>
      </form>
    </div>
  );
}
