import axios from "axios";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

const api = axios.create({
  baseURL: API_BASE,
  headers: { "Content-Type": "application/json" },
});

// JWT interceptor
api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("vf_access_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

// Token refresh on 401
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config;
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true;
      try {
        const refreshToken = localStorage.getItem("vf_refresh_token");
        const { data } = await axios.post(`${API_BASE}/auth/refresh`, {
          refresh_token: refreshToken,
        });
        localStorage.setItem("vf_access_token", data.access_token);
        localStorage.setItem("vf_refresh_token", data.refresh_token);
        original.headers.Authorization = `Bearer ${data.access_token}`;
        return api(original);
      } catch {
        localStorage.removeItem("vf_access_token");
        localStorage.removeItem("vf_refresh_token");
        if (typeof window !== "undefined") {
          window.location.href = "/login";
        }
      }
    }
    return Promise.reject(error);
  }
);

// ── Auth API ──
export const authAPI = {
  register: (data: {
    email: string;
    password: string;
    full_name: string;
    company_name: string;
    company_slug: string;
  }) => api.post("/auth/register", data),

  login: (data: { email: string; password: string }) =>
    api.post("/auth/login", data),

  me: () => api.get("/auth/me"),
};

// ── CRM API ──
export const crmAPI = {
  getLeads: (params?: Record<string, string>) => api.get("/leads", { params }),
  createLead: (data: Record<string, unknown>) => api.post("/leads", data),
  getLead: (id: string) => api.get(`/leads/${id}`),
  updateLead: (id: string, data: Record<string, unknown>) => api.put(`/leads/${id}`, data),
  deleteLead: (id: string) => api.delete(`/leads/${id}`),

  getConversations: (params?: Record<string, string>) =>
    api.get("/conversations", { params }),
  getConversation: (id: string) => api.get(`/conversations/${id}`),

  getAppointments: () => api.get("/appointments"),
  createAppointment: (data: Record<string, unknown>) =>
    api.post("/appointments", data),

  getDashboardStats: () => api.get("/analytics/dashboard"),
};

// ── Knowledge API ──
export const knowledgeAPI = {
  upload: (file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    return api.post("/knowledge/upload", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
  getDocuments: () => api.get("/knowledge/documents"),
  deleteDocument: (id: string) => api.delete(`/knowledge/${id}`),
  query: (query: string, top_k = 5) =>
    api.post("/knowledge/query", { query, top_k }),
};

export default api;
