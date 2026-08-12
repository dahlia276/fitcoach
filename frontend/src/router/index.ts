import { createRouter, createWebHistory } from "vue-router";
import HomeView from "../views/HomeView.vue";
import RecommendationView from "../views/RecommendationView.vue";
import ProgramView from "../views/ProgramView.vue";
import WorkoutView from "../views/WorkoutView.vue";
import DashboardView from "../views/DashboardView.vue";
import CoachView from "../views/CoachView.vue";
import LoginView from "../views/LoginView.vue";
import ProfileView from "../views/ProfileView.vue";
import { useAuthStore } from "../stores/auth";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      name: "home",
      redirect: "/dashboard",
    },
    { path: "/login", name: "login", component: LoginView, meta: { guestOnly: true } },
    { path: "/onboarding", name: "onboarding", component: HomeView, meta: { requiresAuth: false, requiresProfile: false } },
    { path: "/profile", name: "profile", component: ProfileView, meta: { requiresAuth: true, requiresProfile: true } },
    { path: "/recommendation", name: "recommendation", component: RecommendationView, meta: { requiresAuth: true, requiresProfile: true } },
    { path: "/program", name: "program", component: ProgramView, meta: { requiresAuth: true, requiresProfile: true } },
    { path: "/workout", name: "workout", component: WorkoutView, meta: { requiresAuth: true, requiresProfile: true } },
    { path: "/dashboard", name: "dashboard", component: DashboardView, meta: { requiresAuth: true, requiresProfile: true } },
    { path: "/coach", name: "coach", component: CoachView, meta: { requiresAuth: true, requiresProfile: true } },
  ],
});

router.beforeEach(async (to) => {
  const auth = useAuthStore(); await auth.initialize();
  if (!auth.isSupabaseConfigured) return to.name === "login" ? true : { name: "login" };
  if (to.meta.requiresAuth && !auth.isAuthenticated) return { name: "login" };
  if (to.meta.guestOnly && auth.isAuthenticated) return { name: auth.hasProfile ? "dashboard" : "onboarding" };
  if (to.meta.requiresProfile && !auth.hasProfile) return { name: "onboarding" };
  if (to.meta.requiresProfile === false && auth.hasProfile) return { name: "dashboard" };
  return true;
});

export default router;
