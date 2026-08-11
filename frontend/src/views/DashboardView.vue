<script setup lang="ts">
import { computed, onMounted } from "vue";
import { CalendarCheck, Flame, Target, TrendingUp } from "@lucide/vue";
import { getWorkoutLogTimestamp, useFitnessStore } from "../stores/fitness";
import { useAuthStore } from "../stores/auth";
const fitness = useFitnessStore();
const auth = useAuthStore();
const name = computed(() => auth.user?.email?.split("@")[0] ?? "there");
const nextWorkout = computed(() => fitness.program?.days[0] ?? null);
const recentWorkouts = computed(() => [...fitness.workoutHistory]
  .sort((left, right) => {
    const leftTime = new Date(getWorkoutLogTimestamp(left) ?? 0).getTime();
    const rightTime = new Date(getWorkoutLogTimestamp(right) ?? 0).getTime();
    return rightTime - leftTime;
  })
  .slice(0, 3));
const sessionsThisWeek = computed(() => {
  const weekStart = new Date();
  weekStart.setHours(0, 0, 0, 0);
  weekStart.setDate(weekStart.getDate() - ((weekStart.getDay() + 6) % 7));
  const sessionDates = fitness.workoutHistory.reduce<string[]>((dates, log) => {
    const timestamp = getWorkoutLogTimestamp(log);
    if (timestamp && new Date(timestamp) >= weekStart) dates.push(new Date(timestamp).toDateString());
    return dates;
  }, []);
  return new Set(sessionDates).size;
});
const completionRate = computed(() => fitness.program ? Math.min(100, Math.round((sessionsThisWeek.value / fitness.program.days.length) * 100)) : null);
onMounted(() => { void fitness.loadAccountData(); });
</script>

<template><main class="mx-auto max-w-6xl px-6 py-12 lg:px-10"><p class="text-sm font-semibold text-blue-600">Dashboard</p><h1 class="mt-1 text-3xl font-semibold tracking-tight">Good to see you, {{ name }}.</h1><p class="mt-3 text-slate-500">Small sessions add up. Here’s your training snapshot.</p><section class="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4"><div class="stat-card"><CalendarCheck class="text-blue-600" :size="20" /><p>Sessions this week</p><strong>{{ sessionsThisWeek }} <span>/ {{ fitness.program?.days.length ?? 0 }}</span></strong></div><div class="stat-card"><Flame class="text-orange-500" :size="20" /><p>Current streak</p><strong>{{ sessionsThisWeek ? 1 : 0 }} <span>days</span></strong></div><div class="stat-card"><TrendingUp class="text-emerald-600" :size="20" /><p>Completion rate</p><strong>{{ completionRate === null ? "—" : `${completionRate}%` }}</strong></div><div class="stat-card"><Target class="text-violet-600" :size="20" /><p>Primary goal</p><strong class="text-lg">{{ auth.trainingProfile?.goal ?? "Set a goal" }}</strong></div></section><section class="mt-8 grid gap-5 lg:grid-cols-[1.2fr_.8fr]"><div class="rounded-3xl border bg-white p-6 shadow-sm"><h2 class="text-lg font-semibold">{{ nextWorkout ? "Next workout" : "Current program" }}</h2><template v-if="nextWorkout"><p class="mt-3 text-xl font-semibold">{{ nextWorkout.name }}</p><p class="mt-1 text-sm text-slate-500">{{ nextWorkout.focus }} · {{ nextWorkout.estimated_duration_minutes }} min</p><RouterLink class="primary-button mt-5" to="/workout">Start workout</RouterLink></template><template v-else><p class="mt-2 text-sm text-slate-500">Create your first program to see the next workout.</p><RouterLink class="primary-button mt-5" to="/recommendation">Create program</RouterLink></template></div><div class="rounded-3xl border bg-white p-6 shadow-sm"><h2 class="text-lg font-semibold">Recent exercises</h2><div v-if="recentWorkouts.length" class="mt-4 space-y-3"><div v-for="workout in recentWorkouts" :key="workout.id ?? workout.exercise_name" class="flex justify-between text-sm"><span class="font-medium">{{ workout.exercise_name }}</span><span class="text-slate-400">{{ workout.sets }} × {{ workout.reps }}</span></div></div><p v-else class="mt-3 text-sm text-slate-500">Your completed sessions will appear here.</p></div></section><section class="mt-8 rounded-3xl border bg-white p-6 shadow-sm"><h2 class="text-lg font-semibold">Training history</h2><p class="mt-1 text-sm text-slate-500">{{ fitness.workoutHistory.length ? `${fitness.workoutHistory.length} exercises logged across ${sessionsThisWeek} session${sessionsThisWeek === 1 ? '' : 's'}.` : "A weekly view of your completed training will appear here." }}</p><div class="mt-8 flex h-24 items-end justify-between gap-2"><div v-for="day in ['M', 'T', 'W', 'T', 'F', 'S', 'S']" :key="day" class="flex flex-1 flex-col items-center gap-2"><div class="h-12 w-full max-w-10 rounded-t-lg bg-slate-100" /><span class="text-xs text-slate-400">{{ day }}</span></div></div></section></main></template>
