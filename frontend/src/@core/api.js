import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/',
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use(
  (config) => {
    // LocalStorage'dan token'ı alıp her isteğin header'ına ekliyoruz
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`; // DRF Token ise 'Token ${token}' yazabilirsin
    }
    return config;
  },
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => response,
  (error) => {
    // 401 hatası alınırsa (token geçersiz/süresi dolmuşsa) otomatik yönlendirme yapılabilir
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
    }
    console.error('[API Error]:', error.response || error.message);
    return Promise.reject(error);
  }
);

export default api;