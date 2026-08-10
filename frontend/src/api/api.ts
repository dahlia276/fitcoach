import axios from "axios";
import { supabase } from "../lib/supabase";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000",
});

api.interceptors.request.use(async (config) => {
  const { data } = await supabase?.auth.getSession() ?? { data: { session: null } };
  if (data.session?.access_token) config.headers.Authorization = `Bearer ${data.session.access_token}`;
  return config;
});

export default api;
