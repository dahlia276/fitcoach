<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from "vue";
import {
  Brain,
  Search,
  Dumbbell,
  ShieldCheck,
  Sparkles,
  CheckCircle2,
} from "@lucide/vue";

const props = defineProps<{
  finished: boolean;
}>();

const currentStep = ref(0);

const steps = [
  {
    title: "Analyzing your training profile",
    icon: Brain,
  },
  {
    title: "Searching 873 exercises",
    icon: Search,
  },
  {
    title: "Selecting optimal movements",
    icon: Dumbbell,
  },
  {
    title: "Checking injuries & recovery",
    icon: ShieldCheck,
  },
  {
    title: "Finalizing your program",
    icon: Sparkles,
  },
];

let timer: number;
onMounted(() => {
  timer = window.setInterval(() => {
      if (props.finished) return;
      if (currentStep.value < steps.length - 1) {
      currentStep.value++;
    }
    }, 1400);
  });

onUnmounted(() => {
  clearInterval(timer);
});

const progress = computed(() => {
  if (props.finished) return 100;
  return ((currentStep.value + 1) / steps.length) * 100;
});
</script>

<template>
  <Teleport to="body">
    <div
      class="fixed inset-0 z-[100] flex items-center justify-center bg-slate-950/70 backdrop-blur-md"
    >
      <div
        class="w-full max-w-lg rounded-3xl border border-slate-700 bg-slate-900 p-8 shadow-2xl"
      >
        <div class="flex justify-center">
          <div
            class="flex h-20 w-20 items-center justify-center rounded-full bg-blue-500/15"
          >
            <Sparkles
              class="animate-pulse text-blue-400"
              :size="34"
            />
          </div>
        </div>

        <h2
          class="mt-6 text-center text-3xl font-semibold text-white"
        >
          {{ finished ? "Program Ready!" : "Creating your program" }}
        </h2>

        <p
          class="mt-3 text-center text-slate-400"
        >
          {{
            finished
              ? "Taking you to your personalized workout..."
              : "Your workout is being generated using AI and our curated exercise library."
          }}
        </p>

        <div class="mt-10 space-y-4">
          <div
            v-for="(step, index) in steps"
            :key="step.title"
            class="flex items-center gap-4 rounded-xl p-3 transition-all"
            :class="{
              'bg-slate-800': index <= currentStep || finished,
            }"
          >
            <CheckCircle2
              v-if="finished || index < currentStep"
              class="text-emerald-400"
              :size="20"
            />

            <component
              v-else
              :is="step.icon"
              :size="20"
              :class="[
                index === currentStep
                  ? 'animate-pulse text-blue-400'
                  : 'text-slate-500',
              ]"
            />

            <span
              class="text-sm"
              :class="{
                'text-white': index <= currentStep || finished,
                'text-slate-500': index > currentStep,
              }"
            >
              {{ step.title }}
            </span>
          </div>
        </div>

        <div class="mt-8">
          <div
            class="h-2 overflow-hidden rounded-full bg-slate-700"
          >
            <div
              class="h-full rounded-full bg-gradient-to-r from-blue-500 to-emerald-400 transition-all duration-700"
              :style="{ width: `${progress}%` }"
            />
          </div>

          <p
            class="mt-4 text-center text-sm text-slate-400"
          >
            This usually takes around 20-30 seconds.
          </p>
        </div>
      </div>
    </div>
  </Teleport>
</template>
