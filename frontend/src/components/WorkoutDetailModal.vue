<script setup lang="ts">
import { onMounted, ref } from "vue";
import { Activity, Dumbbell, Loader2, ListChecks, X } from "@lucide/vue";
import type { WorkoutDay, WorkoutExercise } from "../stores/fitness";
import { fetchExerciseLibrary, type ExerciseLibraryEntry } from "../api/exerciseLibrary";

const props = defineProps<{ day: WorkoutDay }>();
defineEmits<{ close: [] }>();

interface ExerciseWithDetails {
  exercise: WorkoutExercise;
  details: ExerciseLibraryEntry | null;
}

const isLoading = ref(true);
const exercisesWithDetails = ref<ExerciseWithDetails[]>([]);

onMounted(async () => {
  try {
    const entries = await fetchExerciseLibrary(props.day.exercises.map((exercise) => exercise.exercise_id));
    const detailsById = new Map(entries.map((entry) => [entry.id, entry]));
    exercisesWithDetails.value = props.day.exercises.map((exercise) => ({
      exercise,
      details: detailsById.get(exercise.exercise_id) ?? null,
    }));
  } finally {
    isLoading.value = false;
  }
});

function formatLabel(value: string | null | undefined) {
  if (!value) return null;
  return value.replace(/_/g, " ").replace(/\b\w/g, (char) => char.toUpperCase());
}

function muscleSummary(details: ExerciseLibraryEntry) {
  return [...(details.primary_muscles ?? []), ...(details.secondary_muscles ?? [])]
    .map(formatLabel)
    .join(", ");
}
</script>

<template>
  <Teleport to="body">
    <div class="fixed inset-0 z-100 flex items-center justify-center bg-slate-950/70 p-4 backdrop-blur-md" @click.self="$emit('close')">
      <div class="max-h-[85vh] w-full max-w-2xl overflow-y-auto rounded-3xl border border-slate-200 bg-white p-6 shadow-2xl sm:p-8">
        <div class="flex items-start justify-between gap-4">
          <div>
            <p class="text-sm font-semibold text-blue-600">{{ day.name }}</p>
            <h2 class="mt-1 text-2xl font-semibold tracking-tight">{{ day.focus }}</h2>
          </div>
          <button
            class="grid size-9 shrink-0 place-items-center rounded-full text-slate-400 hover:bg-slate-100 hover:text-slate-700"
            aria-label="Close"
            @click="$emit('close')"
          >
            <X :size="18" />
          </button>
        </div>

        <div v-if="isLoading" class="mt-10 flex flex-col items-center gap-3 py-10 text-slate-400">
          <Loader2 :size="24" class="animate-spin" />
          <p class="text-sm">Loading exercise details...</p>
        </div>

        <div v-else class="mt-6 space-y-4">
          <article v-for="{ exercise, details } in exercisesWithDetails" :key="exercise.exercise_id" class="rounded-2xl border border-slate-200 p-5">
            <div class="flex flex-wrap items-start justify-between gap-3">
              <h3 class="font-semibold">{{ exercise.exercise_name }}</h3>
              <div class="flex flex-wrap gap-2 text-xs font-medium text-slate-500">
                <span class="metric">{{ exercise.sets }} sets</span>
                <span class="metric">{{ exercise.reps }} reps</span>
                <span class="metric">{{ exercise.rest_seconds }}s rest</span>
              </div>
            </div>
            <p v-if="exercise.notes" class="mt-2 text-sm text-slate-500">{{ exercise.notes }}</p>

            <template v-if="details">
              <div class="mt-4 flex flex-wrap gap-2">
                <span v-if="formatLabel(details.equipment)" class="inline-flex items-center gap-1 rounded-full bg-blue-50 px-2.5 py-1 text-xs font-medium text-blue-700">
                  <Dumbbell :size="13" />{{ formatLabel(details.equipment) }}
                </span>
                <span v-if="formatLabel(details.level)" class="inline-flex items-center gap-1 rounded-full bg-blue-50 px-2.5 py-1 text-xs font-medium text-blue-700">{{ formatLabel(details.level) }}</span>
                <span v-if="formatLabel(details.category)" class="inline-flex items-center gap-1 rounded-full bg-blue-50 px-2.5 py-1 text-xs font-medium text-blue-700">{{ formatLabel(details.category) }}</span>
              </div>

              <div v-if="details.primary_muscles?.length" class="mt-3 flex items-start gap-2 text-sm text-slate-600">
                <Activity :size="15" class="mt-0.5 shrink-0 text-slate-400" />
                <span><span class="font-medium">Muscles worked:</span> {{ muscleSummary(details) }}</span>
              </div>

              <div v-if="details.instructions?.length" class="mt-4 flex items-start gap-2">
                <ListChecks :size="15" class="mt-0.5 shrink-0 text-slate-400" />
                <ol class="list-decimal space-y-1.5 pl-4 text-sm text-slate-600 marker:font-medium marker:text-slate-400">
                  <li v-for="(step, index) in details.instructions" :key="index">{{ step }}</li>
                </ol>
              </div>
            </template>
            <p v-else class="mt-3 text-sm text-slate-400">No detailed instructions available for this exercise.</p>
          </article>
        </div>
      </div>
    </div>
  </Teleport>
</template>
