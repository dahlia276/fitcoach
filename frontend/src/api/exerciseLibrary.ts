import api from "./api";

export interface ExerciseLibraryEntry {
  id: string;
  name: string;
  force: string | null;
  level: string | null;
  mechanic: string | null;
  equipment: string | null;
  primary_muscles: string[] | null;
  secondary_muscles: string[] | null;
  instructions: string[] | null;
  category: string | null;
  images: string[] | null;
}

export async function fetchExerciseLibrary(ids: string[]): Promise<ExerciseLibraryEntry[]> {
  const uniqueIds = [...new Set(ids)];
  if (!uniqueIds.length) return [];
  const { data } = await api.get<ExerciseLibraryEntry[]>("/exercises/library", { params: { ids: uniqueIds.join(",") } });
  return data;
}
