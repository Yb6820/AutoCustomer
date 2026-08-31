<script setup lang="ts">
import { reactive } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";

const auth = useAuthStore();
const router = useRouter();
const route = useRoute();

const form = reactive({ username: "", password: "" });

async function submit(): Promise<void> {
  try {
    await auth.login(form.username, form.password);
    const redirect = (route.query.redirect as string) ?? "/";
    void router.push(redirect);
  } catch (e) {
    console.error("登录失败", e);
  }
}
</script>

<template>
  <div class="login">
    <el-card class="card">
      <h1>AutoCustomer 管理后台</h1>
      <el-form label-position="top" @submit.prevent="submit">
        <el-form-item label="用户名">
          <el-input v-model="form.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="form.password" type="password" placeholder="请输入密码" show-password />
        </el-form-item>
        <el-button type="primary" class="submit" :loading="auth.loading" @click="submit">
          登录
        </el-button>
      </el-form>
    </el-card>
  </div>
</template>

<style scoped>
.login {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
}
.card {
  width: 360px;
}
h1 {
  margin: 0 0 20px;
  font-size: 20px;
  text-align: center;
}
.submit {
  width: 100%;
}
</style>