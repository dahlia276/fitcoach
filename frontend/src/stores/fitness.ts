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
export interface WorkoutLog { id?: string; exercise_id?: string; exercise_name: string; completed_at?: string; created_at?: string; sets: number; reps: number; weight: number; rpe?: number; }
export interface ExerciseLogEntry { weight: number | null; reps: number; rpe: number | null }
export function getWorkoutLogTimestamp(log: WorkoutLog) {
  return log.completed_at ?? log.created_at ?? null;
}

const DAY_PREFIX = /^day\s*\d+\s*[:\-–—]?\s*/i;
export function cleanDayName(name: string) {
  const stripped = name.replace(DAY_PREFIX, "").trim();
  return stripped || name;
}

interface OnboardingInput {
  name: string; age: number | null; height: number | null; weight: number | null; goal: string; experience: string; equipment: string; injuries: string; training_days: number; session_minutes: number;
}

export const useFitnessStore = defineStore("fitness", () => {
  const profile = ref<TrainingProfile | null>(null);
  const program = ref<WorkoutProgram | null>(null);
  const isLoading = ref(false);
  const activeDay = ref(0);
  const completedExerciseIds = ref<string[]>([]);
  const exerciseLogs = ref<Record<string, ExerciseLogEntry>>({});
  const workoutHistory = ref<WorkoutLog[]>([]);
  const isSavingWorkout = ref(false);
  const currentWorkout = computed(() => program.value?.days[activeDay.value] ?? null);

  // Finds the program day whose exercises best match the most recently
  // logged session, then advances to the following day - so "next workout"
  // actually rotates through the split instead of always pointing at day 1.
  const nextDayIndex = computed(() => {
    const days = program.value?.days;
    if (!days?.length) return 0;

    const sortedLogs = [...workoutHistory.value]
      .filter((log) => getWorkoutLogTimestamp(log))
      .sort((left, right) => new Date(getWorkoutLogTimestamp(right)!).getTime() - new Date(getWorkoutLogTimestamp(left)!).getTime());

    const lastLog = sortedLogs[0];
    if (!lastLog) return 0;

    const lastSessionDate = new Date(getWorkoutLogTimestamp(lastLog)!).toDateString();
    const lastSessionExerciseIds = new Set(
      sortedLogs
        .filter((log) => new Date(getWorkoutLogTimestamp(log)!).toDateString() === lastSessionDate)
        .map((log) => log.exercise_id ?? log.exercise_name)
    );

    let lastDayIndex = -1;
    let bestOverlap = 0;
    days.forEach((day, index) => {
      const overlap = day.exercises.filter((exercise) => lastSessionExerciseIds.has(exercise.exercise_id) || lastSessionExerciseIds.has(exercise.exercise_name)).length;
      if (overlap > bestOverlap) {
        bestOverlap = overlap;
        lastDayIndex = index;
      }
    });

    if (lastDayIndex === -1) return 0;
    return (lastDayIndex + 1) % days.length;
  });

  async function createProfile(input: OnboardingInput) {
    isLoading.value = true;
    try {
      const { data } = await api.post<{ training_profile: TrainingProfile }>("/onboard", input);
      profile.value = data.training_profile;
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

      await Promise.all(completedExercises.map((exercise) => {
        const entry = exerciseLogs.value[exercise.exercise_id];
        return api.post("/log", {
          exercise_id: exercise.exercise_id,
          exercise_name: exercise.exercise_name,
          sets: exercise.sets,
          reps: entry?.reps ?? exercise.reps,
          weight: entry?.weight ?? 0,
          rpe: entry?.rpe ?? 0,
          notes: exercise.notes,
          completed_at: new Date().toISOString(),
        });
      }));
      await loadAccountData();
    } finally { isSavingWorkout.value = false; }
  }

  function selectDay(index: number) {
    activeDay.value = index;
    completedExerciseIds.value = [];
    const day = program.value?.days[index];
    exerciseLogs.value = Object.fromEntries(
      (day?.exercises ?? []).map((exercise) => [exercise.exercise_id, { weight: null, reps: exercise.reps, rpe: null }])
    );
  }
  function toggleExercise(id: string) { completedExerciseIds.value = completedExerciseIds.value.includes(id) ? completedExerciseIds.value.filter((item) => item !== id) : [...completedExerciseIds.value, id]; }
  function updateExerciseLog(id: string, patch: Partial<ExerciseLogEntry>) {
    exerciseLogs.value[id] = { ...exerciseLogs.value[id], ...patch } as ExerciseLogEntry;
  }
  // Fills in any exercises missing a log entry (e.g. landing on /workout
  // directly rather than via selectDay) without disturbing ones already
  // being edited.
  function ensureExerciseLogs() {
    for (const exercise of currentWorkout.value?.exercises ?? []) {
      if (!exerciseLogs.value[exercise.exercise_id]) {
        exerciseLogs.value[exercise.exercise_id] = { weight: null, reps: exercise.reps, rpe: null };
      }
    }
  }

  return { profile, program, isLoading, activeDay, completedExerciseIds, exerciseLogs, workoutHistory, isSavingWorkout, currentWorkout, nextDayIndex, createProfile, generateProgram, loadAccountData, completeWorkout, selectDay, toggleExercise, updateExerciseLog, ensureExerciseLogs };
});
