<script setup lang="ts">
import { useRouter } from "vue-router";
import { ArrowRight, Clock3, Dumbbell, Play } from "@lucide/vue";
import { useFitnessStore } from "../stores/fitness";

const router = useRouter();
const fitness = useFitnessStore();
const startWorkout = (index: number) => { fitness.selectDay(index); router.push({ name: "workout" }); };
</script>

<template>
  <main v-if="fitness.program" class="mx-auto max-w-5xl px-6 py-12 lg:px-10"><div class="flex flex-col justify-between gap-4 sm:flex-row sm:items-end"><div><p class="text-sm font-semibold text-blue-600">Your training program</p><h1 class="mt-1 text-3xl font-semibold tracking-tight">A week built for progress.</h1><p class="mt-3 text-slate-500">Start with any session that fits your schedule this week.</p></div><span class="inline-flex w-fit items-center gap-2 rounded-full bg-emerald-50 px-3 py-1.5 text-sm font-medium text-emerald-700"><Dumbbell :size="16" />{{ fitness.program.days.length }} training days</span></div>
    <div class="mt-9 grid gap-5 md:grid-cols-2"><article v-for="(day, index) in fitness.program.days" :key="`${day.name}-${index}`" class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm"><div class="flex items-start justify-between"><div><p class="text-sm font-medium text-blue-600">Day {{ index + 1 }}</p><h2 class="mt-1 text-xl font-semibold">{{ day.name }}</h2><p class="mt-1 text-sm text-slate-500">{{ day.focus }}</p></div><span class="rounded-xl bg-slate-100 p-2.5 text-slate-600"><Clock3 :size="18" /></span></div><div class="mt-6 flex items-center justify-between border-y border-slate-100 py-4 text-sm text-slate-500"><span>{{ day.exercises.length }} exercises</span><span>{{ day.estimated_duration_minutes }} min</span></div><ol class="mt-5 space-y-3"><li v-for="exercise in day.exercises.slice(0, 3)" :key="exercise.exercise_id" class="flex justify-between gap-4 text-sm"><span class="font-medium text-slate-700">{{ exercise.exercise_name }}</span><span class="shrink-0 text-slate-400">{{ exercise.sets }} × {{ exercise.reps }}</span></li><li v-if="day.exercises.length > 3" class="text-sm text-slate-400">+ {{ day.exercises.length - 3 }} more exercises</li></ol><button class="primary-button mt-6 w-full" @click="startWorkout(index)"><Play :size="16" fill="currentColor" />Start workout</button></article></div></main>
  <main v-else class="mx-auto max-w-xl px-6 py-24 text-center"><h1 class="text-2xl font-semibold">Your program is waiting to be created.</h1><p class="mt-3 text-slate-500">First, we’ll use your profile to build your sessions.</p><RouterLink class="primary-button mt-7" to="/recommendation">View recommendation<ArrowRight :size="16" /></RouterLink></main>
</template>
