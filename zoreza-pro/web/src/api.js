// Tenant slug extracted from URL: /{slug}/...
export function getTenantSlug() {
  const parts = window.location.pathname.split('/').filter(Boolean);
  return parts[0] || '';
}

function getApiPrefix() {
  const slug = getTenantSlug();
  return slug ? `/${slug}/api/v1` : '/api/v1';
}

let accessToken = localStorage.getItem('access_token');
let refreshToken = localStorage.getItem('refresh_token');

function getBaseUrl() {
  return '';
}

async function request(path, options = {}) {
  const prefix = getApiPrefix();
  const url = `${getBaseUrl()}${prefix}${path}`;
  const headers = { 'Content-Type': 'application/json', ...options.headers };

  if (accessToken) {
    headers['Authorization'] = `Bearer ${accessToken}`;
  }

  let res = await fetch(url, { ...options, headers });

  // Auto-refresh on 401
  if (res.status === 401 && refreshToken) {
    const refreshRes = await fetch(`${getBaseUrl()}${prefix}/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
    if (refreshRes.ok) {
      const tokens = await refreshRes.json();
      accessToken = tokens.access_token;
      refreshToken = tokens.refresh_token;
      localStorage.setItem('access_token', accessToken);
      localStorage.setItem('refresh_token', refreshToken);
      headers['Authorization'] = `Bearer ${accessToken}`;
      res = await fetch(url, { ...options, headers });
    } else {
      logout();
      throw new Error('Sesión expirada');
    }
  }

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Error ${res.status}`);
  }
  if (res.status === 204) return null;
  return res.json();
}

export function setTokens(access, refresh) {
  accessToken = access;
  refreshToken = refresh;
  localStorage.setItem('access_token', access);
  localStorage.setItem('refresh_token', refresh);
}

export function logout() {
  accessToken = null;
  refreshToken = null;
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
}

export function isLoggedIn() {
  return !!accessToken;
}

// Auth
export const login = (username, password) =>
  request('/auth/login', { method: 'POST', body: JSON.stringify({ username, password }) });
export const getMe = () => request('/auth/me');

// Dashboard
export const getDashboard = (params) => {
  const qs = new URLSearchParams(params).toString();
  return request(`/dashboard/summary${qs ? '?' + qs : ''}`);
};

// Clientes
export const getClientes = (activo) =>
  request(`/clientes${activo !== undefined ? '?activo=' + activo : ''}`);
export const createCliente = (data) =>
  request('/clientes', { method: 'POST', body: JSON.stringify(data) });
export const updateCliente = (id, data) =>
  request(`/clientes/${id}`, { method: 'PATCH', body: JSON.stringify(data) });

// Máquinas
export const getMaquinas = (params = {}) => {
  const qs = new URLSearchParams(params).toString();
  return request(`/maquinas${qs ? '?' + qs : ''}`);
};
export const createMaquina = (data) =>
  request('/maquinas', { method: 'POST', body: JSON.stringify(data) });
export const updateMaquina = (id, data) =>
  request(`/maquinas/${id}`, { method: 'PATCH', body: JSON.stringify(data) });

// Rutas
export const getRutas = (activo) =>
  request(`/rutas${activo !== undefined ? '?activo=' + activo : ''}`);
export const createRuta = (data) =>
  request('/rutas', { method: 'POST', body: JSON.stringify(data) });
export const updateRuta = (id, data) =>
  request(`/rutas/${id}`, { method: 'PATCH', body: JSON.stringify(data) });
export const getRutaMaquinas = (rutaId) =>
  request(`/rutas/${rutaId}/maquinas`);
export const assignMaquinaToRuta = (rutaId, maqId) =>
  request(`/rutas/${rutaId}/maquinas/${maqId}`, { method: 'POST' });
export const unassignMaquinaFromRuta = (rutaId, maqId) =>
  request(`/rutas/${rutaId}/maquinas/${maqId}`, { method: 'DELETE' });

// Cortes
export const getCortes = (params = {}) => {
  const qs = new URLSearchParams(params).toString();
  return request(`/cortes${qs ? '?' + qs : ''}`);
};
export const getCorte = (id) => request(`/cortes/${id}`);
export const getCorteDetalles = (id) => request(`/cortes/${id}/detalles`);
export const closeCorte = (id) => request(`/cortes/${id}/close`, { method: 'POST' });

// Gastos
export const getGastos = (params = {}) => {
  const qs = new URLSearchParams(params).toString();
  return request(`/gastos${qs ? '?' + qs : ''}`);
};
export const createGasto = (data) =>
  request('/gastos', { method: 'POST', body: JSON.stringify(data) });
export const deleteGasto = (id) =>
  request(`/gastos/${id}`, { method: 'DELETE' });

// Usuarios
export const getUsuarios = () => request('/usuarios');
export const createUsuario = (data) =>
  request('/usuarios', { method: 'POST', body: JSON.stringify(data) });
export const updateUsuario = (id, data) =>
  request(`/usuarios/${id}`, { method: 'PATCH', body: JSON.stringify(data) });

// Catálogos
export const getCatalog = (type) => request(`/catalogs/${type}`);
export const createCatalogItem = (type, data) =>
  request(`/catalogs/${type}`, { method: 'POST', body: JSON.stringify(data) });
export const updateCatalogItem = (type, id, data) =>
  request(`/catalogs/${type}/${id}`, { method: 'PATCH', body: JSON.stringify(data) });

// Config
export const getAllConfig = () => request('/config');
export const getConfig = (key) => request(`/config/${key}`);
export const setConfig = (key, value) =>
  request(`/config/${key}`, { method: 'PUT', body: JSON.stringify({ value }) });
export const deleteConfig = (key) =>
  request(`/config/${key}`, { method: 'DELETE' });
export const uploadLogo = async (file) => {
  const url = `${getBaseUrl()}${getApiPrefix()}/config/logo/upload`;
  const form = new FormData();
  form.append('file', file);
  const headers = {};
  if (accessToken) headers['Authorization'] = `Bearer ${accessToken}`;
  const res = await fetch(url, { method: 'POST', headers, body: form });
  if (!res.ok) { const b = await res.json().catch(() => ({})); throw new Error(b.detail || `Error ${res.status}`); }
  return res.json();
};
