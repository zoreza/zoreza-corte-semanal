import { useState, useEffect, useCallback } from 'react';
import { getAllConfig, setConfig, uploadLogo } from '../api';

const CONFIG_LABELS = {
  nombre_comercio: { label: 'Nombre del Comercio', desc: 'Se muestra en el ticket y encabezados' },
  ticket_negocio_nombre: { label: 'Nombre en Ticket', desc: 'Nombre corto para el ticket impreso' },
  ticket_footer: { label: 'Pie de Ticket', desc: 'Texto al final del ticket' },
  tolerancia_pesos: { label: 'Tolerancia (pesos)', desc: 'Diferencia máxima permitida entre efectivo y score' },
  fondo_sugerido: { label: 'Fondo Sugerido', desc: 'Monto de fondo predeterminado para máquinas' },
  semana_inicia: { label: 'Semana inicia', desc: 'Día que inicia la semana de corte' },
};

export default function Configuracion() {
  const [configs, setConfigs] = useState({});
  const [categorias, setCategorias] = useState([]);
  const [logoPreview, setLogoPreview] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState({});
  const [newCat, setNewCat] = useState('');

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const items = await getAllConfig();
      const map = {};
      items.forEach((i) => { map[i.key] = i.value; });
      setConfigs(map);
      if (map.categorias_gasto) {
        setCategorias(map.categorias_gasto.split(',').map((s) => s.trim()).filter(Boolean));
      }
      if (map.logo) {
        setLogoPreview(map.logo);
      }
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  const saveKey = async (key, value) => {
    setSaving((s) => ({ ...s, [key]: true }));
    try {
      await setConfig(key, value);
      setConfigs((c) => ({ ...c, [key]: value }));
    } catch (err) {
      alert(err.message);
    } finally {
      setSaving((s) => ({ ...s, [key]: false }));
    }
  };

  const handleLogoUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setSaving((s) => ({ ...s, logo: true }));
    try {
      await uploadLogo(file);
      // Reload to get the data URI
      await load();
    } catch (err) {
      alert(err.message);
    } finally {
      setSaving((s) => ({ ...s, logo: false }));
    }
  };

  const addCategoria = () => {
    const cat = newCat.trim().toUpperCase();
    if (!cat || categorias.includes(cat)) return;
    const updated = [...categorias, cat];
    setCategorias(updated);
    setNewCat('');
    saveKey('categorias_gasto', updated.join(','));
  };

  const removeCategoria = (cat) => {
    const updated = categorias.filter((c) => c !== cat);
    setCategorias(updated);
    saveKey('categorias_gasto', updated.join(','));
  };

  if (loading) return <div className="spinner" />;

  return (
    <div>
      <h1 className="page-title">Configuración</h1>

      {/* Logo */}
      <div className="card mb-24">
        <h3 style={{ marginBottom: 16 }}>Logotipo de la Empresa</h3>
        <div style={{ display: 'flex', alignItems: 'center', gap: 24 }}>
          {logoPreview ? (
            <img src={logoPreview} alt="Logo" style={{ maxWidth: 200, maxHeight: 100, objectFit: 'contain', border: '1px solid var(--border)', borderRadius: 8, padding: 8 }} />
          ) : (
            <div style={{ width: 200, height: 100, display: 'flex', alignItems: 'center', justifyContent: 'center', border: '2px dashed var(--border)', borderRadius: 8, color: '#718096' }}>
              Sin logotipo
            </div>
          )}
          <div>
            <label className="btn btn-primary" style={{ cursor: 'pointer' }}>
              {saving.logo ? 'Subiendo...' : '📷 Subir Logotipo'}
              <input type="file" accept="image/png,image/jpeg,image/webp" onChange={handleLogoUpload} style={{ display: 'none' }} />
            </label>
            <p style={{ fontSize: '0.85rem', color: '#718096', marginTop: 8 }}>PNG, JPEG o WEBP. Máximo 2MB.</p>
          </div>
        </div>
      </div>

      {/* General settings */}
      <div className="card mb-24">
        <h3 style={{ marginBottom: 16 }}>Configuración General</h3>
        {Object.entries(CONFIG_LABELS).map(([key, { label, desc }]) => (
          <ConfigField
            key={key}
            configKey={key}
            label={label}
            description={desc}
            value={configs[key] || ''}
            saving={saving[key]}
            onSave={(val) => saveKey(key, val)}
          />
        ))}
      </div>

      {/* Expense categories */}
      <div className="card mb-24">
        <h3 style={{ marginBottom: 16 }}>Categorías de Gastos</h3>
        <p style={{ fontSize: '0.85rem', color: '#718096', marginBottom: 12 }}>
          Estas categorías aparecen en el menú al registrar un gasto.
        </p>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginBottom: 16 }}>
          {categorias.map((cat) => (
            <span key={cat} className="badge" style={{ fontSize: '0.9rem', padding: '6px 12px', display: 'inline-flex', alignItems: 'center', gap: 8 }}>
              {cat}
              <button
                onClick={() => removeCategoria(cat)}
                style={{ background: 'none', border: 'none', color: 'var(--danger)', cursor: 'pointer', fontWeight: 'bold', padding: 0, fontSize: '1rem' }}
                title="Eliminar"
              >
                ×
              </button>
            </span>
          ))}
          {categorias.length === 0 && <span style={{ color: '#718096' }}>Sin categorías definidas</span>}
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <input
            value={newCat}
            onChange={(e) => setNewCat(e.target.value)}
            placeholder="Nueva categoría..."
            onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addCategoria())}
            style={{ flex: 1 }}
          />
          <button className="btn btn-primary" onClick={addCategoria} disabled={!newCat.trim()}>Agregar</button>
        </div>
      </div>
    </div>
  );
}

function ConfigField({ label, description, value, saving, onSave }) {
  const [val, setVal] = useState(value);
  const [dirty, setDirty] = useState(false);

  // Reset local state when prop changes — safe: derived from prop, no cascade
  if (val !== value && !dirty) {
    setVal(value);
  }

  const handleChange = (e) => {
    setVal(e.target.value);
    setDirty(e.target.value !== value);
  };

  const handleSave = () => {
    onSave(val);
    setDirty(false);
  };

  return (
    <div className="form-group" style={{ display: 'flex', alignItems: 'flex-end', gap: 12, marginBottom: 16 }}>
      <div style={{ flex: 1 }}>
        <label>{label}</label>
        {description && <p style={{ fontSize: '0.8rem', color: '#718096', margin: '2px 0 6px' }}>{description}</p>}
        <input value={val} onChange={handleChange} />
      </div>
      <button
        className={`btn ${dirty ? 'btn-primary' : 'btn-outline'}`}
        onClick={handleSave}
        disabled={!dirty || saving}
        style={{ whiteSpace: 'nowrap' }}
      >
        {saving ? 'Guardando...' : 'Guardar'}
      </button>
    </div>
  );
}
