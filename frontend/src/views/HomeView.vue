<script setup lang="ts">
import { ref } from "vue";
import api from "../api/api"

const form = ref({
  name: "",
  age: null as number | null,
  weight: null as number | null,
  goal: "",
  experience: "",
  equipment: "",
  injuries: "",
});

const plan = ref("");

const loading = ref(false);

const generatePlan = async () => {
  loading.value = true;

  try {
    const response = await api.post("/onboard", form.value);

    plan.value = response.data.plan;
  } catch (err) {
    console.error(err);
    alert("Something went wrong.");
  }

  loading.value = false;
};
</script>

<template>
  <main>
    <h1>FitCoach</h1>

    <input v-model="form.name" placeholder="Name" />

    <input
      v-model.number="form.age"
      type="number"
      placeholder="Age"
    />

    <input
      v-model.number="form.weight"
      type="number"
      placeholder="Weight"
    />

    <input
      v-model="form.goal"
      placeholder="Goal (Build muscle, Lose fat...)"
    />

    <input
      v-model="form.experience"
      placeholder="Experience"
    />

    <input
      v-model="form.equipment"
      placeholder="Equipment"
    />

    <input
      v-model="form.injuries"
      placeholder="Injuries"
    />

    <button @click="generatePlan" :disabled="loading">
      {{ loading ? "Generating..." : "Generate Plan" }}
    </button>

    <pre v-if="plan">{{ plan }}</pre>
  </main>
</template>

<style scoped>
main {
  max-width: 700px;
  margin: 40px auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

input {
  padding: 12px;
}

button {
  padding: 12px;
  cursor: pointer;
}

pre {
  white-space: pre-wrap;
  background: #f5f5f5;
  padding: 20px;
}
</style>
