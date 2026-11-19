import axios from 'axios';

// Runtime API URL detection for production (avoids nginx proxy issues on Render)
const isProd = !import.meta.env.DEV;
const runtimeBaseUrl = isProd
  ? 'https://reconly-api.onrender.com/api/v1'
  : (import.meta.env.VITE_API_URL || '/api/v1');

const api = axios.create({
  baseURL: runtimeBaseUrl,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  },
);

export default api;
