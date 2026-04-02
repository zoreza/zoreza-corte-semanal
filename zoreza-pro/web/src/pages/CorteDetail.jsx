import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getCorte, getCorteDetalles, closeCorte } from '../api';

export default function CorteDetail() {
  const { corteId } = useParams();
  const navigate = useNavigate();
  const [corte, setCorte] = useState(null);
  const [detalles, setDetalles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [closing, setClosing] = useState(false);

  useEffect(() => {
    Promise.all([getCorte(corteId), getCorteDetalles(corteId)])
      .then(([c, d]) => { setCorte(c); setDetalles(d); })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [corteId]);

  const fmt = (n) => n != null ? `$${Number(n).toLocaleString('es-MX', { minimumFractionDigits: 2 })}` : '—';

  const handleClose = async () => {
    if (!window.confirm('¿Cerrar este corte? Esta acción no se puede deshacer.')) return;
    setClosing(true);
    try {
      const updated = await closeCorte(corteId);
      setCorte(updated);
    } catch (err) {
      alert(err.message);
    } finally {
      setClosing(false);
    }
  };

  if (loading) return <div className="spinner" />;
  if (!corte) return <div className="card"><p>Corte no encontrado</p></div>;

  const captured = detalles.filter((d) => d.estado_maquina === 'CAPTURADA');
  const omitted = detalles.filter((d) => d.estado_maquina === 'OMITIDA');

  return (
    <div>
      <button className="btn btn-outline mb-24" onClick={() => navigate('/cortes')}>← Volver</button>

      <div className="card mb-24">
        <h2 style={{ marginBottom: 16 }}>
          Corte: {corte.week_start} — {corte.week_end}
          <span className={`badge ${corte.estado === 'CERRADO' ? 'badge-success' : 'badge-warning'}`} style={{ marginLeft: 12, verticalAlign: 'middle' }}>
            {corte.estado}
          </span>
        </h2>
        <div className="kpi-grid">
          <div className="kpi-card">
            <div className="kpi-label">Cliente</div>
            <div className="kpi-value" style={{ fontSize: '1.2rem' }}>{corte.cliente_nombre || '—'}</div>
          </div>
          <div className="kpi-card">
            <div className="kpi-label">Comisión</div>
            <div className="kpi-value">{(corte.comision_pct_usada * 100).toFixed(0)}%</div>
          </div>
          <div className="kpi-card">
            <div className="kpi-label">Neto Cliente</div>
            <div className="kpi-value">{fmt(corte.neto_cliente)}</div>
          </div>
          <div className="kpi-card">
            <div className="kpi-label">Pago Cliente</div>
            <div className="kpi-value">{fmt(corte.pago_cliente)}</div>
          </div>
          <div className="kpi-card">
            <div className="kpi-label">Ganancia Dueño</div>
            <div className="kpi-value">{fmt(corte.ganancia_dueno)}</div>
          </div>
          <div className="kpi-card">
            <div className="kpi-label">Máquinas</div>
            <div className="kpi-value">{detalles.length}</div>
          </div>
        </div>

        {corte.estado === 'BORRADOR' && (
          <div style={{ marginTop: 16 }}>
            <button className="btn btn-primary" onClick={handleClose} disabled={closing}>
              {closing ? 'Cerrando...' : '🔒 Cerrar Corte'}
            </button>
          </div>
        )}
      </div>

      {/* Captured detalles */}
      <div className="card mb-24">
        <h3 style={{ marginBottom: 12 }}>Capturadas ({captured.length})</h3>
        <table>
          <thead>
            <tr>
              <th>Máquina</th>
              <th>Efectivo</th>
              <th>Score</th>
              <th>Fondo</th>
              <th>Recaudable</th>
              <th>Diferencia</th>
            </tr>
          </thead>
          <tbody>
            {captured.map((d) => (
              <tr key={d.uuid}>
                <td><strong>{d.maquina_codigo || d.maquina_id?.slice(0, 8)}</strong></td>
                <td>{fmt(d.efectivo_total)}</td>
                <td>{fmt(d.score_tarjeta)}</td>
                <td>{fmt(d.fondo)}</td>
                <td>{fmt(d.recaudable)}</td>
                <td style={{ color: d.diferencia < 0 ? 'var(--danger)' : 'var(--success)' }}>{fmt(d.diferencia)}</td>
              </tr>
            ))}
            {captured.length === 0 && <tr><td colSpan={6}>Ninguna máquina capturada</td></tr>}
          </tbody>
        </table>
      </div>

      {/* Omitted detalles */}
      {omitted.length > 0 && (
        <div className="card">
          <h3 style={{ marginBottom: 12 }}>Omitidas ({omitted.length})</h3>
          <table>
            <thead>
              <tr><th>Máquina</th><th>Motivo</th><th>Nota</th></tr>
            </thead>
            <tbody>
              {omitted.map((d) => (
                <tr key={d.uuid}>
                  <td><strong>{d.maquina_codigo || d.maquina_id?.slice(0, 8)}</strong></td>
                  <td>{d.motivo_omision_nombre || d.motivo_omision_id || '—'}</td>
                  <td>{d.nota_omision || '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
