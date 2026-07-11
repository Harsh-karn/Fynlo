import axios from 'axios';
import { getSession } from 'next-auth/react';

// In a real app, we'd use environment variables
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

const api = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Interceptor to add auth token
api.interceptors.request.use(async (config) => {
  if (typeof window !== 'undefined') {
    let token = localStorage.getItem('access_token');
    if (!token) {
      const session = await getSession();
      if (session) {
        token = (session as { accessToken?: string }).accessToken || null;
      }
    }
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

export default api;

