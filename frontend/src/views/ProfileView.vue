<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from "vue";
import { useRouter } from "vue-router";
import { ArrowRight, CalendarDays, CircleUserRound, Dumbbell, Plus, Save, Sparkles, TriangleAlert } from "@lucide/vue";
import { useAuthStore } from "../stores/auth";
import { useFitnessStore } from "../stores/fitness";
import api from "../api/api";

const router = useRouter();
const auth = useAuthStore();
const fitness = useFitnessStore();
const form = reactive({ name: "", age: 0, height: 0, weight: 0, goal: "", experience: "", equipment: "", injuries: "", training_days: 3, session_minutes: 45 });
const canSave = computed(() => form.name.trim() && form.age > 0 && form.height > 0 && form.weight > 0);
const saveStatus = ref<"idle" | "saved" | "error">("idle");
const injuryNotes = ref<string[]>([]);

watch([() => auth.account, () => auth.trainingProfile], ([account, profile]) => {
  if (!account || !profile) return;
  Object.assign(form, { ...account, training_days: profile.training_days, session_minutes: profile.session_minutes });
}, { immediate: true });

watch(() => [form.name, form.age, form.height, form.weight, form.goal, form.experience, form.equipment, form.injuries, form.training_days, form.session_minutes], () => {
  saveStatus.value = "idle";
});

const save = async () => {
  if (!canSave.value) return;
  try {
    await fitness.createProfile({ ...form });
    await auth.loadAccount();
    saveStatus.value = "saved";
  } catch {
    saveStatus.value = "error";
  }
};

function addInjuryNote(note: string) {
  if (form.injuries.includes(note)) return;
  form.injuries = form.injuries ? `${form.injuries}\n${note}` : note;
}

onMounted(async () => {
  try {
    const { data } = await api.get<{ notes: string[] }>("/coach/injury-notes");
    injuryNotes.value = data.notes;
  } catch { injuryNotes.value = []; }
});
</script>

<template>
  <main class="mx-auto max-w-5xl px-6 py-12 lg:px-10">
    <div class="flex flex-col justify-between gap-5 sm:flex-row sm:items-end"><div><p class="text-sm font-semibold text-blue-600">Profile & preferences</p><h1 class="mt-1 text-3xl font-semibold tracking-tight">Keep your coaching current.</h1><p class="mt-3 max-w-2xl text-slate-500">Update your current details whenever your body, routine, or goals change. Your existing plan stays active until you choose to create a new one.</p></div><span class="inline-flex w-fit items-center gap-2 rounded-full bg-slate-100 px-3 py-1.5 text-sm text-slate-600"><CircleUserRound :size="16" />{{ auth.user?.email }}</span></div>

    <section class="mt-8 grid gap-6 lg:grid-cols-[1fr_.72fr]"><form class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8" @submit.prevent="save"><div class="flex items-center gap-3"><div class="grid size-10 place-items-center rounded-xl bg-blue-50 text-blue-600"><CircleUserRound :size="20" /></div><div><h2 class="font-semibold">Your details</h2><p class="text-sm text-slate-500">Used to personalise your recommendations.</p></div></div><div class="mt-7 grid gap-5 sm:grid-cols-2"><label class="field sm:col-span-2">Name<input v-model.trim="form.name" required /></label><label class="field">Age<input v-model.number="form.age" type="number" min="14" max="100" required /></label><label class="field">Weight (kg)<input v-model.number="form.weight" type="number" min="30" max="300" step="0.1" required /></label><label class="field">Height (cm)<input v-model.number="form.height" type="number" min="100" max="250" required /></label><label class="field">Experience<select v-model="form.experience"><option>Beginner</option><option>Intermediate</option><option>Advanced</option></select></label></div><div class="mt-5 grid gap-5 sm:grid-cols-2"><label class="field">Primary goal<select v-model="form.goal"><option>Build muscle</option><option>Lose fat</option><option>Get stronger</option><option>Improve fitness</option></select></label><label class="field">Equipment<select v-model="form.equipment"><option>Full gym</option><option>Home gym</option><option>Dumbbells only</option><option>Bodyweight only</option></select></label><label class="field">Days per week<select v-model.number="form.training_days"><option :value="2">2 days</option><option :value="3">3 days</option><option :value="4">4 days</option><option :value="5">5 days</option></select></label><label class="field">Session length<select v-model.number="form.session_minutes"><option :value="30">30 min</option><option :value="45">45 min</option><option :value="60">60 min</option><option :value="75">75 min</option></select></label></div><label class="field mt-5">Injuries or limitations <span class="font-normal text-slate-400">Optional</span><textarea v-model.trim="form.injuries" rows="3" placeholder="Movements to avoid or prior injuries" /></label><div v-if="injuryNotes.length" class="mt-3 rounded-xl border border-amber-100 bg-amber-50 p-3.5"><p class="flex items-center gap-1.5 text-xs font-semibold text-amber-800"><TriangleAlert :size="14" />Mentioned to your coach in chat</p><ul class="mt-2.5 space-y-2"><li v-for="note in injuryNotes" :key="note" class="flex items-start justify-between gap-3 text-sm text-amber-900"><span class="min-w-0 flex-1">{{ note }}</span><button v-if="!form.injuries.includes(note)" type="button" class="inline-flex shrink-0 items-center gap-1 text-xs font-semibold text-blue-600 hover:text-blue-700" @click="addInjuryNote(note)"><Plus :size="12" />Add</button><span v-else class="shrink-0 text-xs font-medium text-emerald-600">Added</span></li></ul></div><div class="mt-7 flex items-center gap-4"><button class="primary-button" :disabled="!canSave || fitness.isLoading"><Save :size="16" />{{ fitness.isLoading ? "Saving changes..." : "Save changes" }}</button><span v-if="saveStatus === 'saved'" class="text-sm font-medium text-emerald-600">Saved.</span><span v-else-if="saveStatus === 'error'" class="text-sm font-medium text-red-600">Couldn't save. Please try again.</span></div></form>

      <aside class="space-y-5"><section class="rounded-3xl border border-blue-100 bg-blue-50 p-6"><div class="grid size-10 place-items-center rounded-xl bg-white text-blue-600 shadow-sm"><Sparkles :size="20" /></div><h2 class="mt-5 text-lg font-semibold">Ready for a new plan?</h2><p class="mt-2 text-sm leading-6 text-slate-600">Use your saved preferences to generate a fresh program. Your past workouts and history will remain intact.</p><button class="primary-button mt-5 w-full" @click="router.push({ name: 'recommendation' })">Create new plan<ArrowRight :size="16" /></button></section><section class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm"><div class="flex items-center gap-3"><CalendarDays :size="19" class="text-blue-600" /><h2 class="font-semibold">Current training</h2></div><p class="mt-4 text-sm font-medium text-slate-700">{{ auth.trainingProfile?.recommended_split ?? "No active split" }}</p><p class="mt-1 text-sm text-slate-500">{{ auth.trainingProfile?.training_days ?? 0 }} days each week · {{ auth.trainingProfile?.session_minutes ?? 0 }} min sessions</p><RouterLink class="mt-5 inline-flex items-center gap-1 text-sm font-semibold text-blue-600 hover:text-blue-700" to="/program"><Dumbbell :size="16" />View current program</RouterLink></section></aside>
    </section>
  </main>
</template>
