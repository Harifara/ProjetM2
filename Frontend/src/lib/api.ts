const API_BASE_URL = "http://localhost:9000/api";

// ------------------------
// Gestion des tokens
// ------------------------
const DRF_TOKEN_KEY = "drf_token";
const KONG_TOKEN_KEY = "kong_token";

const cleanUUID = (id: string) => id.replace(/\s/g, "");

export const getDrfToken = () => localStorage.getItem(DRF_TOKEN_KEY);
export const setDrfToken = (token: string) => localStorage.setItem(DRF_TOKEN_KEY, token);
export const clearDrfToken = () => localStorage.removeItem(DRF_TOKEN_KEY);

export const getKongToken = () => localStorage.getItem(KONG_TOKEN_KEY);
export const setKongToken = (token: string) => localStorage.setItem(KONG_TOKEN_KEY, token);
export const clearKongToken = () => localStorage.removeItem(KONG_TOKEN_KEY);

const getHeaders = (token?: string | null, json = true) => {
  const headers: Record<string, string> = {};
  if (json) headers["Content-Type"] = "application/json";
  if (token) headers["Authorization"] = `Bearer ${token}`;
  return headers;
};

const fetchWithLog = async (url: string, options: RequestInit = {}) => {
  console.log("➡️ REQUEST:", url, options);
  const res = await fetch(url, options);
  let data: any;
  try { data = await res.json(); } catch { data = {}; }
  console.log("⬅️ RESPONSE:", res.status, data);
  if (!res.ok) {
    const msg = data?.detail || data?.message || `Erreur HTTP ${res.status}`;
    throw new Error(msg);
  }
  return data;
};

// ------------------------
// AUTH API
// ------------------------
const authApi = {
  login: async (username: string, password: string) => {
    const data = await fetchWithLog(`${API_BASE_URL}/auth/login/`, {
      method: "POST",
      headers: getHeaders(),
      body: JSON.stringify({ username, password }),
    });
    if (data.access) setDrfToken(data.access);
    if (data.kong_token) setKongToken(data.kong_token);
    return data;
  },

  logout: async () => {
    const token = getDrfToken();
    await fetchWithLog(`${API_BASE_URL}/auth/logout/`, { method: "POST", headers: getHeaders(token) });
    clearDrfToken(); clearKongToken();
  },

  getMe: async () => {
    const token = getDrfToken();
    return fetchWithLog(`${API_BASE_URL}/auth/me/`, { headers: getHeaders(token) });
  },

  getUsers: async () => {
    const token = getDrfToken();
    return fetchWithLog(`${API_BASE_URL}/auth/users/`, { headers: getHeaders(token) });
  },

  register: async (payload: any) => {
    return fetchWithLog(`${API_BASE_URL}/auth/register/`, { method: "POST", headers: getHeaders(), body: JSON.stringify(payload) });
  },

  updateUser: async (userId: string, payload: any) => {
    const token = getDrfToken();
    return fetchWithLog(`${API_BASE_URL}/auth/users/${cleanUUID(userId)}/`, { method: "PATCH", headers: getHeaders(token), body: JSON.stringify(payload) });
  },

  deleteUser: async (userId: string) => {
    const token = getDrfToken();
    return fetchWithLog(`${API_BASE_URL}/auth/users/${cleanUUID(userId)}/`, { method: "DELETE", headers: getHeaders(token) });
  },

  getAuditLogs: async () => {
    const token = getDrfToken();
    return fetchWithLog(`${API_BASE_URL}/auth/logs/`, { headers: getHeaders(token) });
  },

  fetchKongToken: async () => {
    const token = getDrfToken();
    if (!token) throw new Error("Aucun token DRF trouvé");
    const data = await fetchWithLog(`${API_BASE_URL}/auth/kong-token/`, { headers: getHeaders(token) });
    if (data.kong_token) setKongToken(data.kong_token);
    return data.kong_token;
  },
};

// ------------------------
// RH API
// ------------------------
const ensureKongToken = async (): Promise<string> => {
  let token = getKongToken();
  if (!token) token = await authApi.fetchKongToken();
  if (!token) throw new Error("Impossible de récupérer le token Kong");
  return token;
};

const rhApi = {
  // Districts
  getDistricts: async () => {
    const kong = await ensureKongToken();
    return fetchWithLog(`${API_BASE_URL}/rh/districts/`, { headers: getHeaders(kong) });
  },
  createDistrict: async (payload: any) => {
    const kong = await ensureKongToken();
    return fetchWithLog(`${API_BASE_URL}/rh/districts/`, { method: "POST", headers: getHeaders(kong), body: JSON.stringify(payload) });
  },
  updateDistrict: async (id: string, payload: any) => {
    const kong = await ensureKongToken();
    return fetchWithLog(`${API_BASE_URL}/rh/districts/${id}/`, { method: "PATCH", headers: getHeaders(kong), body: JSON.stringify(payload) });
  },

  // Communes
  getCommunes: async () => {
    const kong = await ensureKongToken();
    return fetchWithLog(`${API_BASE_URL}/rh/communes/`, { headers: getHeaders(kong) });
  },
  createCommune: async (payload: any) => {
    const kong = await ensureKongToken();
    return fetchWithLog(`${API_BASE_URL}/rh/communes/`, { method: "POST", headers: getHeaders(kong), body: JSON.stringify(payload) });
  },
  updateCommune: async (id: string, payload: any) => {
    const kong = await ensureKongToken();
    return fetchWithLog(`${API_BASE_URL}/rh/communes/${id}/`, { method: "PATCH", headers: getHeaders(kong), body: JSON.stringify(payload) });
  },

  // Fokontanys
  getFokontanys: async () => {
    const kong = await ensureKongToken();
    return fetchWithLog(`${API_BASE_URL}/rh/fokontanys/`, { headers: getHeaders(kong) });
  },
  createFokontany: async (payload: any) => {
    const kong = await ensureKongToken();
    return fetchWithLog(`${API_BASE_URL}/rh/fokontanys/`, { method: "POST", headers: getHeaders(kong), body: JSON.stringify(payload) });
  },
  updateFokontany: async (id: string, payload: any) => {
    const kong = await ensureKongToken();
    return fetchWithLog(`${API_BASE_URL}/rh/fokontanys/${id}/`, { method: "PATCH", headers: getHeaders(kong), body: JSON.stringify(payload) });
  },
};

export { rhApi, authApi };
