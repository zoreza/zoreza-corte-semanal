import { useState, useEffect } from 'react';
import { NavLink } from 'react-router-dom';
import { logout, getAllConfig } from '../api';

const NAV = [
  { to: '/', icon: '📊', label: 'Dashboard' },
  { to: '/clientes', icon: '👤', label: 'Clientes' },
  { to: '/maquinas', icon: '🎰', label: 'Máquinas' },
  { to: '/rutas', icon: '🛣️', label: 'Rutas' },
  { to: '/cortes', icon: '📋', label: 'Cortes' },
  { to: '/gastos', icon: '💰', label: 'Gastos' },
  { to: '/usuarios', icon: '👥', label: 'Usuarios' },
  { to: '/reportes', icon: '📈', label: 'Reportes' },
  { to: '/configuracion', icon: '⚙️', label: 'Configuración' },
];

export default function Layout({ user, setUser, children }) {
  const [logo, setLogo] = useState(null);
  const [brandName, setBrandName] = useState('Zoreza Pro');

  useEffect(() => {
    getAllConfig().then((items) => {
      const map = {};
      items.forEach((i) => { map[i.key] = i.value; });
      if (map.logo) setLogo(map.logo);
      if (map.nombre_comercio) setBrandName(map.nombre_comercio);
    }).catch(() => {});
  }, []);

  const handleLogout = () => {
    logout();
    setUser(null);
  };

  return (
    <div className="app-layout">
      <aside className="sidebar">
        <div className="sidebar-brand" style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          {logo && <img src={logo} alt="Logo" style={{ maxHeight: 32, maxWidth: 48, objectFit: 'contain' }} />}
          {brandName}
        </div>
        <nav className="sidebar-nav">
          {NAV.map(({ to, icon, label }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              className={({ isActive }) => isActive ? 'active' : ''}
            >
              <span>{icon}</span> {label}
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-footer">
          <div>{user?.nombre || user?.username}</div>
          <div style={{ marginTop: 4 }}>{user?.rol}</div>
          <button
            className="btn btn-outline btn-sm"
            style={{ marginTop: 8, width: '100%', color: 'white', borderColor: 'rgba(255,255,255,.3)' }}
            onClick={handleLogout}
          >
            Cerrar sesión
          </button>
        </div>
      </aside>
      <main className="main-content">
        {children}
      </main>
    </div>
  );
}
