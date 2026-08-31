import { computed, ref } from "vue";
import { defineStore } from "pinia";
import { tokenStore } from "@auto/api";
import type { UserInfo } from "@auto/shared";
import { api, login as loginApi } from "../api";

export const useAuthStore = defineStore("auth", () => {
  const token = ref<string | null>(tokenStore.getAccessToken());
  const user = ref<UserInfo | null>(null);
  const perms = ref<Set<string>>(new Set());
  const loading = ref(false);
  const isLoggedIn = computed(() => token.value !== null);

  async function login(username: string, password: string): Promise<void> {
    loading.value = true;
    try {
      await loginApi(username, password);
      token.value = tokenStore.getAccessToken();
      user.value = await api.users.me();
      await refreshPerms();
    } finally {
      loading.value = false;
    }
  }

  async function refreshPerms(): Promise<void> {
    // 后端 /auth/perm-codes 就绪后接入；当前从静态预置读取
    perms.value = new Set<string>();
  }

  function hasPerm(code: string): boolean {
    return perms.value.has(code);
  }

  function logout(): void {
    tokenStore.clear();
    token.value = null;
    user.value = null;
    perms.value = new Set();
  }

  return { token, user, perms, loading, isLoggedIn, login, logout, refreshPerms, hasPerm };
});