import { describe, expect, it } from "vitest";
import { mount } from "@vue/test-utils";
import { createPinia } from "pinia";
import { createRouter, createWebHistory } from "vue-router";
import App from "../App.vue";

describe("App", () => {
  it("renders the onboarding route", async () => {
    const router = createRouter({
      history: createWebHistory(),
      routes: [{ path: "/", component: { template: "<p>Onboarding</p>" } }],
    });
    await router.push("/");
    await router.isReady();

    const wrapper = mount(App, { global: { plugins: [createPinia(), router] } });

    expect(wrapper.text()).toContain("Onboarding");
  });
});
