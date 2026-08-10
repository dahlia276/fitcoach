import { computed, ref } from "vue";
import { defineStore } from "pinia";
import api from "../api/api";

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

interface OnboardingInput {
  name: string; age: number | null; height: number | null; weight: number | null; goal: string; experience: string; equipment: string; injuries: string; training_days: number; session_minutes: number;
}

export const useFitnessStore = defineStore("fitness", () => {
  const userId = ref<string | null>(sessionStorage.getItem("fitcoach-user-id"));
  const profile = ref<TrainingProfile | null>(null);
  const program = ref<WorkoutProgram | null>(null);
  const isLoading = ref(false);
  const activeDay = ref(0);
  const completedExerciseIds = ref<string[]>([]);
  const currentWorkout = computed(() => program.value?.days[activeDay.value] ?? null);

  async function createProfile(input: OnboardingInput) {
    isLoading.value = true;
    try {
      const { data } = await api.post<{ user_id: string; training_profile: TrainingProfile }>("/onboard", input);
      userId.value = data.user_id;
      profile.value = data.training_profile;
      sessionStorage.setItem("fitcoach-user-id", data.user_id);
    } finally { isLoading.value = false; }
  }

  async function generateProgram() {
    if (!userId.value) throw new Error("A profile is required before generating a program.");
    isLoading.value = true;
    try { program.value = (await api.post<{ program: WorkoutProgram }>("/program", { user_id: userId.value })).data.program; }
    finally { isLoading.value = false; }
  }

  function selectDay(index: number) { activeDay.value = index; completedExerciseIds.value = []; }
  function toggleExercise(id: string) { completedExerciseIds.value = completedExerciseIds.value.includes(id) ? completedExerciseIds.value.filter((item) => item !== id) : [...completedExerciseIds.value, id]; }

  return { userId, profile, program, isLoading, activeDay, completedExerciseIds, currentWorkout, createProfile, generateProgram, selectDay, toggleExercise };
});
