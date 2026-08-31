import { createRouter, createWebHistory } from "vue-router";
import { tokenStore } from "@auto/api";
import ChatView from "../views/ChatView.vue";
import LoginView from "../views/LoginView.vue";

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/login", name: "login", component: LoginView, meta: { public: true } },
    { path: "/", name: "chat", component: ChatView },
  ],
});

router.beforeEach((to) => {
  const authed = tokenStore.getAccessToken() !== null;
  if (!to.meta.public && !authed) {
    return { path: "/login", query: { redirect: to.fullPath } };
  }
  return true;
});