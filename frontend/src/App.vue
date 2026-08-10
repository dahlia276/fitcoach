<script setup lang="ts">
import { computed } from "vue";
import { RouterLink, RouterView, useRoute } from "vue-router";
import { Activity, MessageCircle, LayoutDashboard } from "@lucide/vue";
import "./assets/main.css";

const route = useRoute();
const showNavigation = computed(() => !["home", "login", "onboarding", "recommendation", "profile"].includes(String(route.name)));
</script>

<template>
  <div class="min-h-screen bg-slate-50 text-slate-900">
    <header v-if="showNavigation" class="border-b border-slate-200/70 bg-white/80 backdrop-blur">
      <nav class="mx-auto flex h-16 max-w-7xl items-center justify-between px-6 lg:px-10">
        <RouterLink class="flex items-center gap-2 font-semibold tracking-tight" to="/"><span class="grid size-8 place-items-center rounded-lg bg-blue-600 text-white"><Activity :size="18" /></span>FitCoach</RouterLink>
        <div class="flex items-center gap-1 text-sm font-medium text-slate-500">
          <RouterLink class="nav-link" to="/program">Program</RouterLink><RouterLink class="nav-link" to="/dashboard"><LayoutDashboard :size="16" />Dashboard</RouterLink><RouterLink class="nav-link" to="/coach"><MessageCircle :size="16" />Coach</RouterLink><RouterLink class="nav-link" to="/profile">Profile</RouterLink>
        </div>
      </nav>
    </header>
    <RouterView />
  </div>
</template>
