<script setup lang="ts">
import { computed } from "vue";
import { useRouter } from "vue-router";
import { ArrowRight, CalendarDays, Clock3, Dumbbell, Sparkles } from "@lucide/vue";
import { useFitnessStore } from "../stores/fitness";

const router = useRouter();
const fitness = useFitnessStore();
const profile = computed(() => fitness.profile);

const createProgram = async () => {
  try { await fitness.generateProgram(); await router.push({ name: "program" }); }
  catch { await router.push({ name: "home" }); }
};
</script>

<template>
  <main v-if="profile" class="mx-auto max-w-3xl px-6 py-14 sm:py-20">
    <div class="text-center"><div class="mx-auto grid size-12 place-items-center rounded-2xl bg-emerald-100 text-emerald-600"><Sparkles :size="23" /></div><p class="mt-6 text-sm font-semibold text-blue-600">Your FitCoach recommendation</p><h1 class="mt-2 text-3xl font-semibold tracking-tight sm:text-4xl">A plan designed for {{ profile.goal.toLowerCase() }}.</h1><p class="mx-auto mt-4 max-w-xl leading-7 text-slate-500">{{ profile.reasoning }}</p></div>
    <section class="mt-10 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8"><div class="flex flex-col justify-between gap-6 sm:flex-row sm:items-start"><div><p class="text-sm font-medium text-slate-500">Recommended training split</p><h2 class="mt-1 text-2xl font-semibold">{{ profile.recommended_split }}</h2></div><span class="rounded-full bg-blue-50 px-3 py-1.5 text-sm font-medium text-blue-700">{{ profile.experience }}</span></div><div class="my-7 h-px bg-slate-100" /><div class="grid gap-4 sm:grid-cols-3"><div class="info-card"><CalendarDays :size="18" class="text-blue-600" /><span>{{ profile.training_days }} days a week</span></div><div class="info-card"><Clock3 :size="18" class="text-blue-600" /><span>{{ profile.session_minutes }} min sessions</span></div><div class="info-card"><Dumbbell :size="18" class="text-blue-600" /><span>{{ profile.equipment }}</span></div></div></section>
    <button class="primary-button mx-auto mt-8 w-full sm:w-auto" :disabled="fitness.isLoading" @click="createProgram">{{ fitness.isLoading ? "Creating your program..." : "Create my program" }}<ArrowRight :size="17" /></button>
  </main>
  <main v-else class="mx-auto max-w-xl px-6 py-24 text-center"><h1 class="text-2xl font-semibold">Let’s start with your profile.</h1><p class="mt-3 text-slate-500">We need a few details before we can make a recommendation.</p><RouterLink class="primary-button mt-7" to="/">Create profile</RouterLink></main>
</template>
