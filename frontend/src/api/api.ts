import axios from "axios";
import { supabase } from "../lib/supabase";

const fallbackApiUrl = "https://stellar-renewal-production-aca9.up.railway.app";
const configuredApiUrl = import.meta.env.VITE_API_URL?.trim();
const isLocalApiUrl = Boolean(configuredApiUrl && /(^https?:\/\/)?(localhost|127\.0\.0\.1)(:\d+)?/i.test(configuredApiUrl));
const apiBaseUrl = import.meta.env.DEV
  ? configuredApiUrl ?? "http://127.0.0.1:8000"
  : (configuredApiUrl && !isLocalApiUrl ? configuredApiUrl : fallbackApiUrl);

if (!import.meta.env.DEV) {
  if (!configuredApiUrl) {
    console.warn("FitCoach API is using the built-in Railway fallback. Set VITE_API_URL in Vercel to override it.");
  } else if (isLocalApiUrl) {
    console.warn(`FitCoach API ignored the localhost VITE_API_URL (${configuredApiUrl}) in production and fell back to Railway.`);
  }
}

const api = axios.create({ baseURL: apiBaseUrl });

api.interceptors.request.use(async (config) => {
  const { data } = await supabase?.auth.getSession() ?? { data: { session: null } };
  if (data.session?.access_token) config.headers.Authorization = `Bearer ${data.session.access_token}`;
  return config;
});

export default api;
