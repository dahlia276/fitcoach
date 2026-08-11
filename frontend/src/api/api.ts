import axios from "axios";
import { supabase } from "../lib/supabase";

const apiBaseUrl = import.meta.env.VITE_API_URL
  ?? (import.meta.env.DEV
    ? "http://127.0.0.1:8000"
    : "https://stellar-renewal-production-aca9.up.railway.app");

if (!import.meta.env.VITE_API_URL && !import.meta.env.DEV) {
  console.warn("FitCoach API is using the built-in Railway fallback. Set VITE_API_URL in Vercel to override it.");
}

const api = axios.create({ baseURL: apiBaseUrl });

api.interceptors.request.use(async (config) => {
  const { data } = await supabase?.auth.getSession() ?? { data: { session: null } };
  if (data.session?.access_token) config.headers.Authorization = `Bearer ${data.session.access_token}`;
  return config;
});

export default api;
