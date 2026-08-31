<script setup lang="ts">
import { ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";

const auth = useAuthStore();
const router = useRouter();
const route = useRoute();

const username = ref("");
const password = ref("");
const error = ref("");

async function submit(): Promise<void> {
  error.value = "";
  try {
    await auth.login(username.value, password.value);
    const redirect = (route.query.redirect as string) ?? "/";
    void router.push(redirect);
  } catch (e) {
    error.value = "登录失败，请检查用户名或密码";
    console.error(e);
  }
}
</script>

<template>
  <div class="login">
    <form class="card" @submit.prevent="submit">
      <h1>智能客服</h1>
      <p class="subtitle">请登录后开始咨询</p>
      <input v-model="username" type="text" placeholder="用户名" autocomplete="username" required />
      <input v-model="password" type="password" placeholder="密码" autocomplete="current-password" required />
      <p v-if="error" class="error">{{ error }}</p>
      <button type="submit" :disabled="auth.loading">{{ auth.loading ? "登录中…" : "登录" }}</button>
    </form>
  </div>
</template>

<style scoped>
.login {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}
.card {
  width: 320px;
  padding: 32px;
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  display: flex;
  flex-direction: column;
  gap: 12px;
}
h1 {
  margin: 0;
  font-size: 20px;
}
.subtitle {
  margin: 0 0 8px;
  color: var(--color-text-secondary);
  font-size: 14px;
}
input {
  height: 40px;
  padding: 0 12px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: 14px;
}
button {
  height: 40px;
  border: none;
  border-radius: var(--radius-md);
  background: var(--color-primary);
  color: #fff;
  font-size: 15px;
  cursor: pointer;
}
button:hover:not(:disabled) {
  background: var(--color-primary-hover);
}
.error {
  margin: 0;
  color: #e5484d;
  font-size: 13px;
}
</style>