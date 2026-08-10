import type { User } from "@supabase/supabase-js";
import { computed, ref } from "vue";
import { defineStore } from "pinia";
import api from "../api/api";
import { isSupabaseConfigured, supabase, supabaseConfigError } from "../lib/supabase";
import type { TrainingProfile } from "./fitness";

export const useAuthStore = defineStore("auth", () => {
  const user = ref<User | null>(null);
  const trainingProfile = ref<TrainingProfile | null>(null);
  const isReady = ref(false);
  const isLoading = ref(false);
  const error = ref<string | null>(null);
  const isAuthenticated = computed(() => Boolean(user.value));
  const hasProfile = computed(() => Boolean(trainingProfile.value));

  async function loadAccount() {
    if (!user.value) { trainingProfile.value = null; return; }
    try { trainingProfile.value = (await api.get<{ profile: TrainingProfile | null }>("/profile/me")).data.profile; }
    catch { trainingProfile.value = null; }
  }

  async function initialize() {
    if (isReady.value) return;
    if (!supabase) { isReady.value = true; return; }
    const { data } = await supabase.auth.getSession();
    user.value = data.session?.user ?? null;
    await loadAccount();
    supabase.auth.onAuthStateChange(async (_event, session) => { user.value = session?.user ?? null; await loadAccount(); });
    isReady.value = true;
  }

  async function signIn(email: string, password: string) {
    if (!supabase) throw new Error(supabaseConfigError ?? "Supabase is not configured.");
    isLoading.value = true; error.value = null;
    try { const { error: authError } = await supabase.auth.signInWithPassword({ email, password }); if (authError) throw authError; }
    catch (exception) { error.value = exception instanceof Error ? exception.message : "Unable to sign in."; throw exception; }
    finally { isLoading.value = false; }
  }

  async function signUp(email: string, password: string) {
    if (!supabase) throw new Error(supabaseConfigError ?? "Supabase is not configured.");
    isLoading.value = true; error.value = null;
    try {
      const { data, error: authError } = await supabase.auth.signUp({ email, password });
      if (authError) throw authError;
      user.value = data.user;
      return Boolean(data.session);
    }
    catch (exception) { error.value = exception instanceof Error ? exception.message : "Unable to create your account."; throw exception; }
    finally { isLoading.value = false; }
  }

  async function signOut() { await supabase?.auth.signOut(); user.value = null; trainingProfile.value = null; }
  return { user, trainingProfile, isReady, isLoading, error, isAuthenticated, hasProfile, isSupabaseConfigured, supabaseConfigError, initialize, loadAccount, signIn, signUp, signOut };
});
