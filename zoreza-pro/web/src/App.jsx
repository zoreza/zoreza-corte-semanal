import { useState, useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { isLoggedIn, getMe, logout } from './api';
import Layout from './components/Layout';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Clientes from './pages/Clientes';
import Maquinas from './pages/Maquinas';
import Rutas from './pages/Rutas';
import Cortes from './pages/Cortes';
import CorteDetail from './pages/CorteDetail';
import Gastos from './pages/Gastos';
import Usuarios from './pages/Usuarios';
import Reportes from './pages/Reportes';
import Configuracion from './pages/Configuracion';

function App() {
  const [user, setUser] = useState(null);
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    if (isLoggedIn()) {
      getMe()
        .then(setUser)
        .catch(() => setUser(null))
        .finally(() => setChecking(false));
    } else {
      setChecking(false);
    }
  }, []);

  if (checking) return <div className="spinner" />;

  if (!user) return <Login onLogin={setUser} />;

  if (user.rol !== 'ADMIN') {
    return (
      <div className="login-container">
        <div className="login-box">
          <h1>Acceso Denegado</h1>
          <p className="subtitle">Esta interfaz es solo para administradores.</p>
          <button
            className="btn btn-primary"
            style={{ marginTop: 16, width: '100%' }}
            onClick={() => { logout(); setUser(null); }}
          >
            Cerrar sesión
          </button>
        </div>
      </div>
    );
  }

  return (
    <Layout user={user} setUser={setUser}>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/clientes" element={<Clientes />} />
        <Route path="/maquinas" element={<Maquinas />} />
        <Route path="/rutas" element={<Rutas />} />
        <Route path="/cortes" element={<Cortes />} />
        <Route path="/cortes/:corteId" element={<CorteDetail />} />
        <Route path="/gastos" element={<Gastos />} />
        <Route path="/usuarios" element={<Usuarios />} />
        <Route path="/reportes" element={<Reportes />} />
        <Route path="/configuracion" element={<Configuracion />} />
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </Layout>
  );
}

export default App;
