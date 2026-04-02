import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import App from './App';
import SuperAdmin from './pages/SuperAdmin';
import './index.css';

// Determine context: super-admin panel or tenant app
const pathParts = window.location.pathname.split('/').filter(Boolean);
const firstSegment = pathParts[0] || '';

const isSuperAdmin = firstSegment === 'zoreza-admin';
const tenantSlug = (!isSuperAdmin && firstSegment) ? firstSegment : '';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    {isSuperAdmin ? (
      <BrowserRouter basename="/zoreza-admin">
        <SuperAdmin />
      </BrowserRouter>
    ) : tenantSlug ? (
      <BrowserRouter basename={`/${tenantSlug}`}>
        <App />
      </BrowserRouter>
    ) : (
      <BrowserRouter>
        <TenantLanding />
      </BrowserRouter>
    )}
  </React.StrictMode>
);

function TenantLanding() {
  return (
    <div style={{
      minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center',
      background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)', color: 'white',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    }}>
      <div style={{ textAlign: 'center', maxWidth: 500 }}>
        <h1 style={{ fontSize: '2.5rem', marginBottom: 8 }}>Zoreza Labs</h1>
        <p style={{ fontSize: '1.1rem', opacity: 0.8, marginBottom: 32 }}>
          Plataforma de gestión para máquinas de entretenimiento
        </p>
        <p style={{ opacity: 0.6 }}>
          Accede a tu panel en: <code style={{ background: 'rgba(255,255,255,0.1)', padding: '2px 8px', borderRadius: 4 }}>zorezalabs.mx/tu-negocio</code>
        </p>
      </div>
    </div>
  );
}
