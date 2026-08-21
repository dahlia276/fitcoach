<script setup lang="ts">
import { computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import { Check, ChevronLeft, Clock3, Pause, Timer } from "@lucide/vue";
import { cleanDayName, useFitnessStore } from "../stores/fitness";

const router = useRouter();
const fitness = useFitnessStore();
const workout = computed(() => fitness.currentWorkout);
const completed = computed(() => fitness.completedExerciseIds.length);
onMounted(() => fitness.ensureExerciseLogs());
const finishWorkout = async () => {
  try {
    await fitness.completeWorkout();
  } finally {
    await router.replace({ name: "dashboard" });
  }
};
</script>

<template>
  <main v-if="workout" class="mx-auto max-w-3xl px-6 py-10"><button class="mb-8 inline-flex items-center gap-1 text-sm font-medium text-slate-500 hover:text-slate-900" @click="router.push({ name: 'program' })"><ChevronLeft :size="17" />Back to program</button><div class="rounded-3xl bg-slate-900 p-6 text-white sm:p-8"><div class="flex justify-between gap-4"><div><p class="text-sm font-medium text-blue-300">Today’s session</p><h1 class="mt-1 text-3xl font-semibold">{{ cleanDayName(workout.name) }}</h1><p class="mt-2 text-slate-300">{{ workout.focus }}</p></div><div class="rounded-2xl bg-white/10 p-3"><Clock3 :size="20" /></div></div><div class="mt-8 h-2 overflow-hidden rounded-full bg-white/15"><div class="h-full rounded-full bg-emerald-400 transition-all" :style="{ width: `${(completed / workout.exercises.length) * 100}%` }" /></div><p class="mt-3 text-sm text-slate-300">{{ completed }} of {{ workout.exercises.length }} exercises complete</p></div><section class="mt-7 space-y-3"><article v-for="(exercise, index) in workout.exercises" :key="exercise.exercise_id" class="flex gap-4 rounded-2xl border bg-white p-5 shadow-sm transition" :class="fitness.completedExerciseIds.includes(exercise.exercise_id) ? 'border-emerald-200 bg-emerald-50/40' : 'border-slate-200'"><button class="mt-0.5 grid size-6 shrink-0 place-items-center rounded-full border" :class="fitness.completedExerciseIds.includes(exercise.exercise_id) ? 'border-emerald-500 bg-emerald-500 text-white' : 'border-slate-300'" :aria-label="`Mark ${exercise.exercise_name} complete`" @click="fitness.toggleExercise(exercise.exercise_id)"><Check v-if="fitness.completedExerciseIds.includes(exercise.exercise_id)" :size="15" /></button><div class="min-w-0 flex-1"><p class="text-xs font-medium text-slate-400">EXERCISE {{ index + 1 }}</p><h2 class="mt-1 font-semibold">{{ exercise.exercise_name }}</h2><p class="mt-1 text-sm text-slate-500">{{ exercise.notes }}</p><div class="mt-4 flex flex-wrap gap-2 text-sm font-medium"><span class="metric">{{ exercise.sets }} sets</span><span class="metric">{{ exercise.reps }} reps</span><span class="metric"><Timer :size="14" />{{ exercise.rest_seconds }}s rest</span></div><div v-if="fitness.exerciseLogs[exercise.exercise_id]" class="mt-4 flex flex-wrap gap-3"><label class="flex items-center gap-1.5 text-xs font-medium text-slate-500">Weight<input v-model.number="fitness.exerciseLogs[exercise.exercise_id].weight" type="number" min="0" step="0.5" placeholder="lb" class="ml-1.5 w-20 rounded-lg border border-slate-200 px-2 py-1.5 text-sm text-slate-900 outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10" /></label><label class="flex items-center gap-1.5 text-xs font-medium text-slate-500">Reps<input v-model.number="fitness.exerciseLogs[exercise.exercise_id].reps" type="number" min="0" class="ml-1.5 w-16 rounded-lg border border-slate-200 px-2 py-1.5 text-sm text-slate-900 outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10" /></label><label class="flex items-center gap-1.5 text-xs font-medium text-slate-500">RPE<input v-model.number="fitness.exerciseLogs[exercise.exercise_id].rpe" type="number" min="1" max="10" step="0.5" placeholder="1-10" class="ml-1.5 w-16 rounded-lg border border-slate-200 px-2 py-1.5 text-sm text-slate-900 outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10" /></label></div></div></article></section><button class="primary-button mt-7 w-full" :disabled="fitness.isSavingWorkout" @click="finishWorkout"><Pause :size="16" />{{ fitness.isSavingWorkout ? "Saving workout..." : "Finish workout" }}</button></main>
  <main v-else class="mx-auto max-w-xl px-6 py-24 text-center"><h1 class="text-2xl font-semibold">Choose a workout first.</h1><RouterLink class="primary-button mt-7" to="/program">View program</RouterLink></main>
</template>
