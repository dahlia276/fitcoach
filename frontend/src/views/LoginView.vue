<script setup lang="ts">
import { computed, ref } from "vue";
import { useRouter } from "vue-router";
import { Activity, ArrowRight, CircleHelp, LockKeyhole, Mail } from "@lucide/vue";
import { useAuthStore } from "../stores/auth";

const router = useRouter();
const auth = useAuthStore();
const email = ref("");
const password = ref("");
const isSignUp = ref(false);
const notice = ref("");

const passwordRules = computed(() => ({
  length: password.value.length >= 8,
  uppercase: /[A-Z]/.test(password.value),
  lowercase: /[a-z]/.test(password.value),
  number: /\d/.test(password.value),
}));
const isPasswordValid = computed(() => Object.values(passwordRules.value).every(Boolean));

const submit = async () => {
  notice.value = "";
  auth.error = null;

  if (isSignUp.value && !isPasswordValid.value) {
    auth.error = "Choose a password that meets all of the requirements below.";
    return;
  }

  try {
    if (isSignUp.value) {
      const hasSession = await auth.signUp(email.value, password.value);
      if (hasSession) await router.push("/onboarding");
      else notice.value = "If this email isn't registered, we've sent you a confirmation email. If you already have an account, please sign in.";
      return;
    }

    await auth.signIn(email.value, password.value);
    await router.push(auth.hasProfile ? "/dashboard" : "/onboarding");
  } catch {
    // The store exposes a user-safe error message directly below the form.
  }
};

const toggleMode = () => {
  isSignUp.value = !isSignUp.value;
  auth.error = null;
  notice.value = "";
  password.value = "";
};
</script>

<template>
  <main class="grid min-h-screen place-items-center px-6 py-12">
    <section class="w-full max-w-md rounded-3xl border border-slate-200 bg-white p-7 shadow-xl shadow-slate-200/50 sm:p-9">
      <div class="grid size-11 place-items-center rounded-2xl bg-blue-600 text-white"><Activity :size="22" /></div>
      <h1 class="mt-6 text-2xl font-semibold tracking-tight">{{ isSignUp ? "Create your account" : "Welcome back" }}</h1>
      <p class="mt-2 text-sm leading-6 text-slate-500">{{ isSignUp ? "Start building training momentum today." : "Sign in to continue with your training." }}</p>

      <p v-if="!auth.isSupabaseConfigured" class="mt-5 rounded-xl bg-amber-50 px-3 py-2.5 text-sm leading-5 text-amber-800">
        {{ auth.supabaseConfigError }} Update <code class="font-medium">frontend/.env.local</code>, then restart Vite.
      </p>

      <form class="mt-7 space-y-5" @submit.prevent="submit">
        <label class="field">
          Email
          <div class="relative"><Mail :size="16" class="absolute left-3 top-3 text-slate-400" /><input v-model.trim="email" class="pl-10!" type="email" required autocomplete="email" placeholder="you@example.com" /></div>
        </label>

        <label class="field">
          <span class="flex items-center gap-1.5">Password
            <span class="group relative inline-flex"><button type="button" class="rounded text-slate-400 hover:text-slate-600" aria-label="View password requirements"><CircleHelp :size="15" /></button><span role="tooltip" class="pointer-events-none absolute bottom-6 left-1/2 z-10 w-56 -translate-x-1/2 rounded-xl bg-slate-800 p-3 text-xs font-normal leading-5 text-white opacity-0 shadow-lg transition group-hover:opacity-100 group-focus-within:opacity-100">Use at least 8 characters, including an uppercase letter, lowercase letter, and number.</span></span>
          </span>
          <div class="relative"><LockKeyhole :size="16" class="absolute left-3 top-3 text-slate-400" /><input v-model="password" class="pl-10!" type="password" required :minlength="isSignUp ? 8 : 6" :autocomplete="isSignUp ? 'new-password' : 'current-password'" placeholder="Enter your password" /></div>
        </label>

        <ul v-if="isSignUp" class="grid grid-cols-2 gap-2 text-xs">
          <li class="password-rule" :class="passwordRules.length ? 'met' : ''"><span />8+ characters</li>
          <li class="password-rule" :class="passwordRules.uppercase ? 'met' : ''"><span />Uppercase letter</li>
          <li class="password-rule" :class="passwordRules.lowercase ? 'met' : ''"><span />Lowercase letter</li>
          <li class="password-rule" :class="passwordRules.number ? 'met' : ''"><span />Number</li>
        </ul>

        <p v-if="auth.error" class="rounded-xl bg-rose-50 px-3 py-2 text-sm text-rose-600">{{ auth.error }}</p>
        <p v-if="notice" class="rounded-xl bg-emerald-50 px-3 py-2 text-sm text-emerald-700">{{ notice }}</p>
        <button class="primary-button w-full" :disabled="auth.isLoading || !auth.isSupabaseConfigured">{{ auth.isLoading ? "Please wait..." : isSignUp ? "Create account" : "Sign in" }}<ArrowRight :size="16" /></button>
      </form>

      <button class="mt-6 w-full text-sm font-medium text-blue-600 hover:text-blue-700" @click="toggleMode">{{ isSignUp ? "Already have an account? Sign in" : "New to FitCoach? Create an account" }}</button>
    </section>
  </main>
</template>

<style scoped>
.password-rule { align-items: center; color: #94a3b8; display: flex; gap: 0.375rem; }
.password-rule > span { background: #cbd5e1; border-radius: 9999px; height: 0.375rem; width: 0.375rem; }
.password-rule.met { color: #059669; }
.password-rule.met > span { background: #10b981; }
</style>
