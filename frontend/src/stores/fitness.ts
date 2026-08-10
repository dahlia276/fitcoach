import { computed, ref } from "vue";
import { defineStore } from "pinia";
import api from "../api/api";
import { useAuthStore } from "./auth";

export interface TrainingProfile {
  goal: string;
  experience: string;
  equipment: string;
  injuries: string;
  training_days: number;
  session_minutes: number;
  recommended_split: string;
  reasoning: string;
}

export interface WorkoutExercise { exercise_id: string; exercise_name: string; sets: number; reps: number; rest_seconds: number; notes: string }
export interface WorkoutDay { name: string; focus: string; estimated_duration_minutes: number; exercises: WorkoutExercise[] }
export interface WorkoutProgram { days: WorkoutDay[] }
export interface WorkoutLog { id?: string; exercise_name: string; completed_at?: string; sets: number; reps: number; weight: number; }

interface OnboardingInput {
  name: string; age: number | null; height: number | null; weight: number | null; goal: string; experience: string; equipment: string; injuries: string; training_days: number; session_minutes: number;
}

export const useFitnessStore = defineStore("fitness", () => {
  const profile = ref<TrainingProfile | null>(null);
  const program = ref<WorkoutProgram | null>(null);
  const isLoading = ref(false);
  const activeDay = ref(0);
  const completedExerciseIds = ref<string[]>([]);
  const workoutHistory = ref<WorkoutLog[]>([]);
  const isSavingWorkout = ref(false);
  const currentWorkout = computed(() => program.value?.days[activeDay.value] ?? null);

  async function createProfile(input: OnboardingInput) {
    isLoading.value = true;
    try {
      const { data } = await api.post<{ training_profile: TrainingProfile }>("/onboard", input);
      profile.value = data.training_profile;
      useAuthStore().trainingProfile = data.training_profile;
    } finally { isLoading.value = false; }
  }

  async function generateProgram() {
    if (!useAuthStore().user) throw new Error("You must be signed in before generating a program.");
    isLoading.value = true;
    try { program.value = (await api.post<{ program: WorkoutProgram }>("/program")).data.program; }
    finally { isLoading.value = false; }
  }

  async function loadAccountData() {
    if (!useAuthStore().user) return;
    const [planResponse, logsResponse] = await Promise.all([api.get<{ plan?: WorkoutProgram } | null>("/plan"), api.get<WorkoutLog[]>("/logs")]);
    program.value = planResponse.data?.plan ?? null;
    workoutHistory.value = logsResponse.data;
  }

  async function completeWorkout() {
    if (!currentWorkout.value) return;
    isSavingWorkout.value = true;
    try {
      const completedExercises = completedExerciseIds.value.length
        ? currentWorkout.value.exercises.filter((exercise) => completedExerciseIds.value.includes(exercise.exercise_id))
        : currentWorkout.value.exercises;

      await Promise.all(completedExercises.map((exercise) => api.post("/log", {
        exercise_id: exercise.exercise_id,
        exercise_name: exercise.exercise_name,
        sets: exercise.sets,
        reps: exercise.reps,
        weight: 0,
        rpe: 0,
        notes: exercise.notes,
      })));
      await loadAccountData();
    } finally { isSavingWorkout.value = false; }
  }

  function selectDay(index: number) { activeDay.value = index; completedExerciseIds.value = []; }
  function toggleExercise(id: string) { completedExerciseIds.value = completedExerciseIds.value.includes(id) ? completedExerciseIds.value.filter((item) => item !== id) : [...completedExerciseIds.value, id]; }

  return { profile, program, isLoading, activeDay, completedExerciseIds, workoutHistory, isSavingWorkout, currentWorkout, createProfile, generateProgram, loadAccountData, completeWorkout, selectDay, toggleExercise };
});
