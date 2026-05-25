import axios from 'axios';

// Create a configured Axios instance
export const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // For HttpOnly cookies (refresh tokens)
});

// Add a request interceptor to attach JWT tokens if stored in memory/localStorage (optional)
api.interceptors.request.use((config) => {
  // If using localStorage token approach instead of HttpOnly cookies:
  // const token = localStorage.getItem('access_token');
  // if (token) config.headers.Authorization = \`Bearer \${token}\`;
  return config;
});

// Add a response interceptor to handle 401s and refresh tokens seamlessly
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        // Attempt to refresh token
        await api.post('/auth/refresh');
        return api(originalRequest);
      } catch (refreshError) {
        // Refresh failed, trigger logout
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  }
);
