import { createRouter, createWebHistory } from "vue-router";
import HomeView from "../views/HomeView.vue";
import RecommendationView from "../views/RecommendationView.vue";
import ProgramView from "../views/ProgramView.vue";
import WorkoutView from "../views/WorkoutView.vue";
import DashboardView from "../views/DashboardView.vue";
import CoachView from "../views/CoachView.vue";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      name: "home",
      component: HomeView,
    },
    { path: "/recommendation", name: "recommendation", component: RecommendationView },
    { path: "/program", name: "program", component: ProgramView },
    { path: "/workout", name: "workout", component: WorkoutView },
    { path: "/dashboard", name: "dashboard", component: DashboardView },
    { path: "/coach", name: "coach", component: CoachView },
  ],
});

export default router;
