import { computed, ref } from "vue";
import { defineStore } from "pinia";
import { tokenStore } from "@auto/api";
import type { UserInfo } from "@auto/shared";
import { api, login as loginApi } from "../api";

export const useAuthStore = defineStore("auth", () => {
  const token = ref<string | null>(tokenStore.getAccessToken());
  const user = ref<UserInfo | null>(null);
  const loading = ref(false);
  const isLoggedIn = computed(() => token.value !== null);

  async function login(username: string, password: string): Promise<void> {
    loading.value = true;
    try {
      await loginApi(username, password);
      token.value = tokenStore.getAccessToken();
      user.value = await api.users.me();
    } finally {
      loading.value = false;
    }
  }

  function logout(): void {
    tokenStore.clear();
    token.value = null;
    user.value = null;
  }

  return { token, user, loading, isLoggedIn, login, logout };
});