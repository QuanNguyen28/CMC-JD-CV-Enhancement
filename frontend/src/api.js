// frontend/src/api.js
import axios from 'axios';

const baseURL = import.meta.env.VITE_API_BASE || 'http://localhost:8001';

const api = axios.create({ baseURL });

// ---- attach token on every request
api.interceptors.request.use((config) => {
  const t = localStorage.getItem('access_token');
  if (t) config.headers.Authorization = `Bearer ${t}`;
  return config;
});

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err?.response?.status === 401) {
      localStorage.removeItem('access_token');
    }
    return Promise.reject(err);
  }
);

// ---- logical API groups
export const AuthAPI = {
  async login(username, password) {
    const body = new URLSearchParams();
    body.append('username', username);
    body.append('password', password);
    const { data } = await api.post('/auth/token', body, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    localStorage.setItem('access_token', data.access_token);
    return data;
  },
  async me() {
    const { data } = await api.get('/auth/me');
    return data;
  },
};

export const JDAPI = {
  async generateJD(payload) {
    // payload: { title, department?, level?, job_family? }
    const { data } = await api.post('/v1/jd/generate', payload);
    return data; // { jd_id, content_md, version }
  },
  async update(payload) {
    // payload: { jd_id, content_md, change_summary? }
    const { data } = await api.put('/v1/jd/update', payload);
    return data;
  },
  async versions(jdId) {
    const { data } = await api.get(`/v1/jd/version-history/${jdId}`);
    return data; // [{version_number|version, content_md, edited_by|updated_by, edited_at|updated_at}]
  },
  async exportJD(jdId, format = 'pdf') {
    const res = await api.get(`/v1/jd/export/${jdId}?format=${format}`, {
      responseType: 'blob',
    });
    return res.data; // blob
  },
};

export const RetrieverAPI = {
  async similar(query, top_k = 5) {
    const { data } = await api.post('/v1/retrieve/similar', { query, top_k });
    return data; // [{chunk_id, jd_id, chunk_index, object_url, score}]
  },
  async simple(query, top_k = 5) {
    const { data } = await api.post('/v1/retrieve', { query, top_k });
    return data;
  },
};

export const InterviewAPI = {
  async generate(payload) {
    // payload: { jd_id?, title, level, department, focus:[], count, mix:[], language }
    const { data } = await api.post('/v1/interview/generate', payload);
    return data; // { questions: [...] }
  },
};

export const RolesAPI = {
  async list() {
    const { data } = await api.get('/v1/roles/list');
    return data;
  },
};

// api.js
export const improveJD = (payload) => api.post('/v1/jd/improve', payload); 
// payload: { content_md, instruction, language: 'en' }

export const suggestJD = (payload) => api.post('/v1/jd/suggest', payload);
// payload: { content_md, section, goal, language: 'en', chunks_text }


export default api;