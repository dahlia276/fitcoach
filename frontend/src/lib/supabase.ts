import { createClient, type SupabaseClient } from "@supabase/supabase-js";

const url = import.meta.env.VITE_SUPABASE_URL;
const publicKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

function isSecretKey(key: string | undefined) {
  if (!key) return false;
  if (key.startsWith("sb_secret_")) return true;

  try {
    const encodedPayload = key.split(".")[1];
    if (!encodedPayload) return false;
    const payload = JSON.parse(atob(encodedPayload));
    return payload.role === "service_role";
  } catch {
    return false;
  }
}

const hasSecretKey = isSecretKey(publicKey);
export const supabaseConfigError = hasSecretKey
  ? "A Supabase secret/service-role key was supplied to the browser. Replace it with the project's anon or publishable key."
  : !url || !publicKey
    ? "Supabase is not configured. Add VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY to frontend/.env.local."
    : null;

export const isSupabaseConfigured = !supabaseConfigError;
export const supabase: SupabaseClient | null = isSupabaseConfigured
  ? createClient(url, publicKey, { auth: { persistSession: true, autoRefreshToken: true, detectSessionInUrl: true } })
  : null;
