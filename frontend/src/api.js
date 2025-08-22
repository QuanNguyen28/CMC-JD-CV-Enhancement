// src/api.js
import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8001',
  // withCredentials: true, // bật nếu backend dùng cookie
});

// tự động gắn Bearer token từ localStorage
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export default api;

// optional: tiện đổi baseURL lúc runtime
export const setBaseURL = (url) => { api.defaults.baseURL = url; };