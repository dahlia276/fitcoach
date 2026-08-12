<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { ArrowRight, Check, Dumbbell, Sparkles } from "@lucide/vue";
import { useFitnessStore } from "../stores/fitness";
import { useAuthStore } from "../stores/auth";

const router = useRouter();
const fitness = useFitnessStore();
const auth = useAuthStore();
const error = ref("");
const DRAFT_KEY = "fitcoach_draft_onboarding";

const form = ref({
  name: "",
  age: null as number | null,
  height: null as number | null,
  weight: null as number | null,
  goal: "Build muscle",
  experience: "Beginner",
  equipment: "Full gym",
  injuries: "",
  training_days: 3,
  session_minutes: 45,
});

const canSubmit = computed(
  () =>
    form.value.name.trim() &&
    form.value.age &&
    form.value.height &&
    form.value.weight,
);

function saveDraft() {
  localStorage.setItem(DRAFT_KEY, JSON.stringify(form.value));
}

function clearDraft() {
  localStorage.removeItem(DRAFT_KEY);
}

onMounted(() => {
  const saved = localStorage.getItem(DRAFT_KEY);
  if (saved) {
    try { Object.assign(form.value, JSON.parse(saved)); } catch { /* ignore a corrupted draft */ }
  }
});

async function submitProfile() {
  await fitness.createProfile({ ...form.value, injuries: form.value.injuries || "None" });
  clearDraft();
  await router.push({ name: "recommendation" });
}

const submit = async () => {
  if (!canSubmit.value) {
    error.value = "Please complete your basic details to continue.";
    return;
  }

  error.value = "";

  if (!auth.isAuthenticated) {
    saveDraft();
    showAuthGate.value = true;
    return;
  }

  try {
    await submitProfile();
  } catch {
    error.value = "We couldn't save your profile. Check that the API is running and try again.";
  }
};

// --- Inline account creation, shown only once the profile form is ready to submit ---
const showAuthGate = ref(false);
const authMode = ref<"signup" | "signin">("signup");
const authEmail = ref("");
const authPassword = ref("");
const authNotice = ref("");
const isAuthSubmitting = ref(false);

const submitAuth = async () => {
  authNotice.value = "";
  auth.error = null;
  isAuthSubmitting.value = true;
  try {
    if (authMode.value === "signup") {
      const hasSession = await auth.signUp(authEmail.value, authPassword.value);
      if (!hasSession) {
        authNotice.value = "Account created. Check your email to confirm your address, then come back and sign in. Your details are saved.";
        return;
      }
    } else {
      await auth.signIn(authEmail.value, authPassword.value);
    }
    await submitProfile();
    showAuthGate.value = false;
  } catch {
  } finally {
    isAuthSubmitting.value = false;
  }
};

const toggleAuthMode = () => {
  authMode.value = authMode.value === "signup" ? "signin" : "signup";
  auth.error = null;
  authNotice.value = "";
  authPassword.value = "";
};
</script>

<template>
  <main class="mx-auto grid min-h-screen max-w-7xl items-center gap-12 px-6 py-12 lg:grid-cols-[0.9fr_1.1fr] lg:px-10">
    <section class="max-w-xl">
      <div class="mb-8 inline-flex items-center gap-2 rounded-full border border-blue-100 bg-blue-50 px-3 py-1.5 text-sm font-medium text-blue-700">
        <Sparkles :size="15" />
        Personal training, thoughtfully generated
      </div>
      <h1 class="text-4xl font-semibold tracking-tight text-slate-900 sm:text-5xl">
        Training that fits your life.
      </h1>
      <p class="mt-5 max-w-lg text-lg leading-8 text-slate-500">
        Tell us a little about yourself. FitCoach will turn it into a practical training plan built around your goals, schedule, and equipment.
      </p>
      <div class="mt-10 space-y-4 text-sm text-slate-600">
        <p class="flex items-center gap-3"><span class="grid size-6 place-items-center rounded-full bg-emerald-100 text-emerald-600"><Check :size="14" /></span>Adaptive plans based on your experience</p>
        <p class="flex items-center gap-3"><span class="grid size-6 place-items-center rounded-full bg-emerald-100 text-emerald-600"><Check :size="14" /></span>Clear workouts with no guesswork</p>
        <p class="flex items-center gap-3"><span class="grid size-6 place-items-center rounded-full bg-emerald-100 text-emerald-600"><Check :size="14" /></span>Progress that stays in one place</p>
      </div>
    </section>

    <section class="rounded-3xl border border-slate-200/80 bg-white p-6 shadow-xl shadow-slate-200/50 sm:p-8">
      <div class="mb-8 flex items-start justify-between">
        <div>
          <p class="text-sm font-medium text-blue-600">Step 1 of 3</p>
          <h2 class="mt-1 text-2xl font-semibold tracking-tight text-slate-900">Build your profile</h2>
          <p class="mt-2 text-sm text-slate-500">This takes about two minutes.</p>
        </div>
        <div class="grid size-11 place-items-center rounded-2xl bg-slate-900 text-white"><Dumbbell :size="20" /></div>
      </div>

      <form class="space-y-6" @submit.prevent="submit">
        <div class="grid gap-5 sm:grid-cols-2">
          <label class="field sm:col-span-2">Your name<input v-model.trim="form.name" autocomplete="name" placeholder="Alex Morgan" /></label>
          <label class="field">Age<input v-model.number="form.age" type="number" min="14" max="100" placeholder="28" /></label>
          <label class="field">Height (cm)<input v-model.number="form.height" type="number" min="100" max="250" placeholder="175" /></label>
          <label class="field">Weight (kg)<input v-model.number="form.weight" type="number" min="30" max="300" step="0.1" placeholder="72" /></label>
          <label class="field">Experience<select v-model="form.experience"><option>Beginner</option><option>Intermediate</option><option>Advanced</option></select></label>
        </div>

        <div class="grid gap-5 sm:grid-cols-2">
          <label class="field">Primary goal<select v-model="form.goal"><option>Build muscle</option><option>Lose fat</option><option>Get stronger</option><option>Improve fitness</option></select></label>
          <label class="field">Available equipment<select v-model="form.equipment"><option>Full gym</option><option>Home gym</option><option>Dumbbells only</option><option>Bodyweight only</option></select></label>
          <label class="field">Days per week<select v-model.number="form.training_days"><option :value="2">2 days</option><option :value="3">3 days</option><option :value="4">4 days</option><option :value="5">5 days</option></select></label>
          <label class="field">Session length<select v-model.number="form.session_minutes"><option :value="30">30 min</option><option :value="45">45 min</option><option :value="60">60 min</option><option :value="75">75 min</option></select></label>
        </div>

        <label class="field">Anything we should know? <span class="font-normal text-slate-400">Optional</span><textarea v-model.trim="form.injuries" rows="2" placeholder="Past injuries or movements to avoid" /></label>
        <p v-if="error" class="rounded-xl bg-rose-50 px-3 py-2 text-sm text-rose-600">{{ error }}</p>
        <button class="primary-button w-full" type="submit" :disabled="fitness.isLoading"><span>{{ fitness.isLoading ? "Saving your profile..." : "See my recommendation" }}</span><ArrowRight :size="17" /></button>
      </form>
    </section>

    <div v-if="showAuthGate" class="fixed inset-0 z-30 grid place-items-center bg-slate-900/40 px-4" @click.self="showAuthGate = false">
      <div class="w-full max-w-sm rounded-3xl border border-slate-200 bg-white p-7 shadow-xl">
        <div class="grid size-11 place-items-center rounded-2xl bg-blue-600 text-white"><Dumbbell :size="20" /></div>
        <h2 class="mt-5 text-xl font-semibold tracking-tight text-slate-900">{{ authMode === "signup" ? "Create an account to see your plan" : "Sign in to continue" }}</h2>
        <p class="mt-2 text-sm leading-6 text-slate-500">Your details are saved — this just takes a second.</p>

        <form class="mt-6 space-y-4" @submit.prevent="submitAuth">
          <label class="field">Email<input v-model.trim="authEmail" type="email" autocomplete="email" required /></label>
          <label class="field">Password<input v-model="authPassword" type="password" autocomplete="new-password" minlength="8" required /></label>
          <p v-if="auth.error" class="rounded-xl bg-rose-50 px-3 py-2 text-sm text-rose-600">{{ auth.error }}</p>
          <p v-if="authNotice" class="rounded-xl bg-emerald-50 px-3 py-2 text-sm text-emerald-700">{{ authNotice }}</p>
          <button class="primary-button w-full" type="submit" :disabled="isAuthSubmitting"><span>{{ isAuthSubmitting ? "Please wait..." : authMode === "signup" ? "Create account & continue" : "Sign in & continue" }}</span><ArrowRight :size="17" /></button>
        </form>

        <button class="mt-4 w-full text-center text-sm font-medium text-blue-600 hover:text-blue-700" type="button" @click="toggleAuthMode">
          {{ authMode === "signup" ? "Already have an account? Sign in" : "New here? Create an account" }}
        </button>
      </div>
    </div>
  </main>
</template>
