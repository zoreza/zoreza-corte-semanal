import { useState, useEffect } from 'react';
import {
  login as apiLogin,
  getMe,
  setTokens,
  supportsPasskeys,
  passkeyAuthStart,
  passkeyAuthFinish,
  browserPasskeyAuth,
} from '../api';

export default function Login({ onLogin }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [hasPasskeys, setHasPasskeys] = useState(false);

  useEffect(() => {
    setHasPasskeys(supportsPasskeys());
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const tokens = await apiLogin(username, password);
      setTokens(tokens.access_token, tokens.refresh_token);
      const user = await getMe();
      onLogin(user);
    } catch (err) {
      setError(err.message || 'Error de autenticación');
    } finally {
      setLoading(false);
    }
  };

  const handlePasskeyLogin = async () => {
    setError('');
    setLoading(true);
    try {
      const { options } = await passkeyAuthStart(null);
      const credential = await browserPasskeyAuth(options);
      const tokens = await passkeyAuthFinish(credential, null);
      setTokens(tokens.access_token, tokens.refresh_token);
      const user = await getMe();
      onLogin(user);
    } catch (err) {
      if (err.name === 'NotAllowedError') {
        setError('Autenticación cancelada');
      } else {
        setError(err.message || 'Error con passkey');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <form className="login-box" onSubmit={handleSubmit}>
        <h1>Zoreza Pro</h1>
        <p className="subtitle">Panel de Administración</p>
        {error && <div className="error-msg">{error}</div>}
        <div className="form-group">
          <label>Usuario</label>
          <input
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            autoComplete="username"
            required
          />
        </div>
        <div className="form-group">
          <label>Contraseña</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete="current-password"
            required
          />
        </div>
        <button className="btn btn-primary" style={{ width: '100%' }} disabled={loading}>
          {loading ? 'Ingresando...' : 'Ingresar'}
        </button>
        {hasPasskeys && (
          <button
            type="button"
            className="btn"
            style={{
              width: '100%',
              marginTop: 12,
              background: '#1e1e1e',
              border: '1px solid #333',
              color: '#fff',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: 8,
            }}
            disabled={loading}
            onClick={handlePasskeyLogin}
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M15 3a6 6 0 0 1 0 12h-1.5M9 9a6 6 0 1 0 0 12M12 15l3 3m0 0l3-3m-3 3V9" />
            </svg>
            Ingresar con Passkey
          </button>
        )}
      </form>
    </div>
  );
}
