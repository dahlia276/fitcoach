<script setup lang="ts">
import { RouterLink } from "vue-router";
</script>

<template>
  <main class="mx-auto max-w-4xl px-6 py-20 text-center">
    <div class="mb-8">
      <h1 class="text-4xl font-bold">Welcome to FitCoach</h1>
      <p class="mt-4 text-lg text-slate-600">Personalized training plans, workout tracking, and an AI coach to help you reach your goals.</p>
    </div>

    <div class="grid gap-6 sm:grid-cols-3 mb-8">
      <div class="p-6 bg-white rounded-xl shadow-sm">
        <h2 class="font-semibold">Generate Plans</h2>
        <p class="mt-2 text-sm text-slate-500">Create a structured 4‑week program based on your saved preferences.</p>
      </div>
      <div class="p-6 bg-white rounded-xl shadow-sm">
        <h2 class="font-semibold">Track Workouts</h2>
        <p class="mt-2 text-sm text-slate-500">Log sets, reps and progress to keep your training on track.</p>
      </div>
      <div class="p-6 bg-white rounded-xl shadow-sm">
        <h2 class="font-semibold">AI Coach</h2>
        <p class="mt-2 text-sm text-slate-500">Get exercise selections and program structure powered by our assistant.</p>
      </div>
    </div>

    <div class="flex flex-col items-center gap-3 sm:flex-row sm:justify-center">
      <RouterLink class="primary-button" to="/onboarding">Get started</RouterLink>
      <RouterLink class="text-sm text-slate-600 hover:text-slate-800 ml-0 sm:ml-4" to="/login">Sign in</RouterLink>
    </div>

    <section class="mt-12 text-left">
      <h3 class="text-xl font-semibold mb-3">What you can do</h3>
      <ul class="list-disc pl-6 space-y-2 text-slate-600">
        <li>Save your profile and training preferences.</li>
        <li>Generate personalized workout programs using your history and goals.</li>
        <li>Log completed workouts and track progress over time.</li>
        <li>Ask the AI coach for help and adjustments.</li>
      </ul>
    </section>
  </main>
</template>
