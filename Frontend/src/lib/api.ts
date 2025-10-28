// ============================================================================
// Configuration API centralisée pour l'architecture microservices avec Kong Gateway
// Compatible avec Kong strip_path: true
// ============================================================================

declare global {
  interface Window {
    ENV?: {
      VITE_API_URL?: string;
    };
  }
}

const getApiBaseUrl = () => {
  if (typeof window !== "undefined" && window.ENV?.VITE_API_URL) {
    return window.ENV.VITE_API_URL;
  }
  return import.meta.env.VITE_API_URL || "http://localhost:9000/api";
};

const API_BASE_URL = getApiBaseUrl();

console.log('🌐 API Base URL:', API_BASE_URL);

const getAuthToken = () => localStorage.getItem("token");

const getAuthHeaders = (isJson = true) => {
  const headers: Record<string, string> = {};
  if (isJson) headers["Content-Type"] = "application/json";
  const token = getAuthToken();
  if (token) headers["Authorization"] = `Bearer ${token}`;
  return headers;
};

const handleResponse = async (response: Response) => {
  const text = await response.text();
  let data: any = {};
  try {
    data = JSON.parse(text);
  } catch {
    data = { detail: text || "Erreur réseau inconnue" };
  }

  if (!response.ok) {
    throw new Error(data.detail || data.message || "Erreur réseau");
  }

  return data;
};

// =======================================================
// 🔐 AUTH SERVICE
// =======================================================
export const authApi = {
  login: (username: string, password: string) =>
    fetch(`${API_BASE_URL}/auth/login/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
      credentials: "include",
    }).then(handleResponse),

  logout: () =>
    fetch(`${API_BASE_URL}/auth/logout/`, {
      method: "POST",
      headers: getAuthHeaders(),
    }).then(handleResponse),

  getMe: () =>
    fetch(`${API_BASE_URL}/auth/me/`, {
      method: "GET",
      headers: getAuthHeaders(),
    }).then(handleResponse),

  register: (data: any) => {
    const payload = {
      username: data.username,
      email: data.email,
      full_name: data.full_name,
      password: data.password,
      password_confirm: data.password_confirm || data.password,
      role: data.role,
      is_active: data.is_active
    };

    return fetch(`${API_BASE_URL}/auth/register/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }).then(handleResponse);
  },

  updateUser: (id: string, data: any) =>
    fetch(`${API_BASE_URL}/auth/users/${id}/`, {
      method: "PATCH",
      headers: getAuthHeaders(),
      body: JSON.stringify(data),
    }).then(handleResponse),

  deleteUser: (id: string) =>
    fetch(`${API_BASE_URL}/auth/users/${id}/`, {
      method: "DELETE",
      headers: getAuthHeaders(),
    }).then(handleResponse),

  refreshToken: (refreshToken: string) =>
    fetch(`${API_BASE_URL}/auth/refresh/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh: refreshToken }),
    }).then(handleResponse),

  getUsers: () =>
    fetch(`${API_BASE_URL}/auth/users/`, {
      method: "GET",
      headers: getAuthHeaders(),
    }).then(handleResponse),

  getAuditLogs: () =>
    fetch(`${API_BASE_URL}/auth/logs/`, {
      method: "GET",
      headers: getAuthHeaders(),
    }).then(handleResponse),
};

// =======================================================
// 📦 STOCK SERVICE (complet)
// =======================================================
export const stockApi = {
  getStockItems: () =>
    fetch(`${API_BASE_URL}/stock/items/`, {
      method: "GET",
      headers: getAuthHeaders(),
    }).then(handleResponse),

  getStockItem: (id: string | number) =>
    fetch(`${API_BASE_URL}/stock/items/${id}/`, {
      method: "GET",
      headers: getAuthHeaders(),
    }).then(handleResponse),

  createStockItem: (data: any) =>
    fetch(`${API_BASE_URL}/stock/items/`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify(data),
    }).then(handleResponse),

  updateStockItem: (id: string | number, data: any) =>
    fetch(`${API_BASE_URL}/stock/items/${id}/`, {
      method: "PUT",
      headers: getAuthHeaders(),
      body: JSON.stringify(data),
    }).then(handleResponse),

  deleteStockItem: (id: string | number) =>
    fetch(`${API_BASE_URL}/stock/items/${id}/`, {
      method: "DELETE",
      headers: getAuthHeaders(),
    }).then(handleResponse),

  getTransferRequests: () =>
    fetch(`${API_BASE_URL}/stock/transfers/`, {
      method: "GET",
      headers: getAuthHeaders(),
    }).then(handleResponse),

  approveTransfer: (id: string | number) =>
    fetch(`${API_BASE_URL}/stock/transfers/${id}/approve/`, {
      method: "POST",
      headers: getAuthHeaders(),
    }).then(handleResponse),

  rejectTransfer: (id: string | number) =>
    fetch(`${API_BASE_URL}/stock/transfers/${id}/reject/`, {
      method: "POST",
      headers: getAuthHeaders(),
    }).then(handleResponse),

  getInventoryChecks: () =>
    fetch(`${API_BASE_URL}/stock/inventories/`, {
      method: "GET",
      headers: getAuthHeaders(),
    }).then(handleResponse),

  getPurchaseRequests: () =>
    fetch(`${API_BASE_URL}/stock/purchase-requests/`, {
      method: "GET",
      headers: getAuthHeaders(),
    }).then(handleResponse),

  validatePurchaseRequest: (id: string | number) =>
    fetch(`${API_BASE_URL}/stock/purchase-requests/${id}/validate/`, {
      method: "POST",
      headers: getAuthHeaders(),
    }).then(handleResponse),

  getAuditLogs: () =>
    fetch(`${API_BASE_URL}/stock/logs/`, {
      method: "GET",
      headers: getAuthHeaders(),
    }).then(handleResponse),
};

// =======================================================
// RH API CLIENT (uniformisé)
// =======================================================
export const rhApi = {
  getEmployees: () => fetch(`${API_BASE_URL}/rh/employees/`, { headers: getAuthHeaders() }).then(handleResponse),
  getEmployee: (id: string) => fetch(`${API_BASE_URL}/rh/employees/${id}/`, { headers: getAuthHeaders() }).then(handleResponse),
  createEmployee: (data: any) => fetch(`${API_BASE_URL}/rh/employees/`, { method: "POST", headers: getAuthHeaders(), body: JSON.stringify(data) }).then(handleResponse),
  updateEmployee: (id: string, data: any) => fetch(`${API_BASE_URL}/rh/employees/${id}/`, { method: "PUT", headers: getAuthHeaders(), body: JSON.stringify(data) }).then(handleResponse),
  deleteEmployee: (id: string) => fetch(`${API_BASE_URL}/rh/employees/${id}/`, { method: "DELETE", headers: getAuthHeaders() }).then(handleResponse),
  getEmployeeStats: () => fetch(`${API_BASE_URL}/rh/employees/stats/`, { headers: getAuthHeaders() }).then(handleResponse),

  getContracts: () => fetch(`${API_BASE_URL}/rh/contracts/`, { headers: getAuthHeaders() }).then(handleResponse),
  createContract: (data: any) => fetch(`${API_BASE_URL}/rh/contracts/`, { method: "POST", headers: getAuthHeaders(), body: JSON.stringify(data) }).then(handleResponse),
  updateContract: (id: string, data: any) => fetch(`${API_BASE_URL}/rh/contracts/${id}/`, { method: "PUT", headers: getAuthHeaders(), body: JSON.stringify(data) }).then(handleResponse),

  getLeaveRequests: () => fetch(`${API_BASE_URL}/rh/leave-requests/`, { headers: getAuthHeaders() }).then(handleResponse),
  createLeaveRequest: (data: any) => fetch(`${API_BASE_URL}/rh/leave-requests/`, { method: "POST", headers: getAuthHeaders(), body: JSON.stringify(data) }).then(handleResponse),
  validateLeaveRequest: (id: string, status: string, rejection_reason?: string) =>
    fetch(`${API_BASE_URL}/rh/leave-requests/${id}/validate/`, { method: "POST", headers: getAuthHeaders(), body: JSON.stringify({ status, rejection_reason }) }).then(handleResponse),

  getAssignments: () => fetch(`${API_BASE_URL}/rh/assignments/`, { headers: getAuthHeaders() }).then(handleResponse),
  createAssignment: (data: any) => fetch(`${API_BASE_URL}/rh/assignments/`, { method: "POST", headers: getAuthHeaders(), body: JSON.stringify(data) }).then(handleResponse),
  validateAssignment: (id: string, status: string) => fetch(`${API_BASE_URL}/rh/assignments/${id}/validate/`, { method: "POST", headers: getAuthHeaders(), body: JSON.stringify({ status }) }).then(handleResponse),

  getPaymentRequests: () => fetch(`${API_BASE_URL}/rh/payment-requests/`, { headers: getAuthHeaders() }).then(handleResponse),
  createPaymentRequest: (data: any) => fetch(`${API_BASE_URL}/rh/payment-requests/`, { method: "POST", headers: getAuthHeaders(), body: JSON.stringify(data) }).then(handleResponse),

  getPurchaseRequests: () => fetch(`${API_BASE_URL}/rh/purchase-requests/`, { headers: getAuthHeaders() }).then(handleResponse),
  createPurchaseRequest: (data: any) => fetch(`${API_BASE_URL}/rh/purchase-requests/`, { method: "POST", headers: getAuthHeaders(), body: JSON.stringify(data) }).then(handleResponse),

  getDistricts: () => fetch(`${API_BASE_URL}/rh/districts/`, { headers: getAuthHeaders() }).then(handleResponse),
  createDistrict: (data: any) => fetch(`${API_BASE_URL}/rh/districts/`, { method: "POST", headers: getAuthHeaders(), body: JSON.stringify(data) }).then(handleResponse),
  updateDistrict: (id: string, data: any) => fetch(`${API_BASE_URL}/rh/districts/${id}/`, { method: "PUT", headers: getAuthHeaders(), body: JSON.stringify(data) }).then(handleResponse),
  deleteDistrict: (id: string) => fetch(`${API_BASE_URL}/rh/districts/${id}/`, { method: "DELETE", headers: getAuthHeaders() }).then(handleResponse),

  getCommunes: () => fetch(`${API_BASE_URL}/rh/communes/`, { headers: getAuthHeaders() }).then(handleResponse),
  createCommune: (data: any) => fetch(`${API_BASE_URL}/rh/communes/`, { method: "POST", headers: getAuthHeaders(), body: JSON.stringify(data) }).then(handleResponse),
  updateCommune: (id: string, data: any) => fetch(`${API_BASE_URL}/rh/communes/${id}/`, { method: "PUT", headers: getAuthHeaders(), body: JSON.stringify(data) }).then(handleResponse),
  deleteCommune: (id: string) => fetch(`${API_BASE_URL}/rh/communes/${id}/`, { method: "DELETE", headers: getAuthHeaders() }).then(handleResponse),

  getFokontany: () => fetch(`${API_BASE_URL}/rh/fokontany/`, { headers: getAuthHeaders() }).then(handleResponse),
  createFokontany: (data: any) => fetch(`${API_BASE_URL}/rh/fokontany/`, { method: "POST", headers: getAuthHeaders(), body: JSON.stringify(data) }).then(handleResponse),
  updateFokontany: (id: string, data: any) => fetch(`${API_BASE_URL}/rh/fokontany/${id}/`, { method: "PUT", headers: getAuthHeaders(), body: JSON.stringify(data) }).then(handleResponse),
  deleteFokontany: (id: string) => fetch(`${API_BASE_URL}/rh/fokontany/${id}/`, { method: "DELETE", headers: getAuthHeaders() }).then(handleResponse),
};



// =======================================================
// 💰 FINANCE SERVICE
// =======================================================
export const financeApi = {
  getTransactions: () =>
    fetch(`${API_BASE_URL}/finance/transactions/`, {
      method: "GET",
      headers: getAuthHeaders(),
    }).then(handleResponse),

  getTransaction: (id: string | number) =>
    fetch(`${API_BASE_URL}/finance/transactions/${id}/`, {
      method: "GET",
      headers: getAuthHeaders(),
    }).then(handleResponse),

  createTransaction: (data: any) =>
    fetch(`${API_BASE_URL}/finance/transactions/`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify(data),
    }).then(handleResponse),

  getInvoices: () =>
    fetch(`${API_BASE_URL}/finance/invoices/`, {
      method: "GET",
      headers: getAuthHeaders(),
    }).then(handleResponse),

  getPayments: () =>
    fetch(`${API_BASE_URL}/finance/payments/`, {
      method: "GET",
      headers: getAuthHeaders(),
    }).then(handleResponse),

  getReport: (params?: Record<string, string>) => {
    const queryString = params ? `?${new URLSearchParams(params)}` : "";
    return fetch(`${API_BASE_URL}/finance/report/${queryString}`, {
      method: "GET",
      headers: getAuthHeaders(),
    }).then(handleResponse);
  },
};

// =======================================================
// 🧭 COORDINATEUR SERVICE
// =======================================================
export const coordinateurApi = {
  getProjects: () =>
    fetch(`${API_BASE_URL}/coordinateur/projects/`, {
      method: "GET",
      headers: getAuthHeaders(),
    }).then(handleResponse),

  getProject: (id: string | number) =>
    fetch(`${API_BASE_URL}/coordinateur/projects/${id}/`, {
      method: "GET",
      headers: getAuthHeaders(),
    }).then(handleResponse),

  createProject: (data: any) =>
    fetch(`${API_BASE_URL}/coordinateur/projects/`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify(data),
    }).then(handleResponse),

  updateProject: (id: string | number, data: any) =>
    fetch(`${API_BASE_URL}/coordinateur/projects/${id}/`, {
      method: "PUT",
      headers: getAuthHeaders(),
      body: JSON.stringify(data),
    }).then(handleResponse),

  getTasks: () =>
    fetch(`${API_BASE_URL}/coordinateur/tasks/`, {
      method: "GET",
      headers: getAuthHeaders(),
    }).then(handleResponse),

  createTask: (data: any) =>
    fetch(`${API_BASE_URL}/coordinateur/tasks/`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify(data),
    }).then(handleResponse),
};

// =======================================================
// 🔔 NOTIFICATION SERVICE
// =======================================================
export const notificationApi = {
  getNotifications: () =>
    fetch(`${API_BASE_URL}/notifications/`, {
      method: "GET",
      headers: getAuthHeaders(),
    }).then(handleResponse),

  markAsRead: (id: string | number) =>
    fetch(`${API_BASE_URL}/notifications/${id}/read/`, {
      method: "POST",
      headers: getAuthHeaders(),
    }).then(handleResponse),

  markAllAsRead: () =>
    fetch(`${API_BASE_URL}/notifications/mark-all-read/`, {
      method: "POST",
      headers: getAuthHeaders(),
    }).then(handleResponse),

  deleteNotification: (id: string | number) =>
    fetch(`${API_BASE_URL}/notifications/${id}/`, {
      method: "DELETE",
      headers: getAuthHeaders(),
    }).then(handleResponse),
};

// =======================================================
// 🧩 EXPORT GLOBAL
// =======================================================
export default {
  authApi,
  stockApi,
  rhApi,
  financeApi,
  coordinateurApi,
  notificationApi,
};
