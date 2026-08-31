<script setup lang="ts">
import { useRoute, useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";
import { menuItems } from "../router";

const auth = useAuthStore();
const route = useRoute();
const router = useRouter();

function logout(): void {
  auth.logout();
  void router.push("/login");
}
</script>

<template>
  <el-container class="layout">
    <el-aside width="200px" class="aside">
      <div class="brand">AutoCustomer</div>
      <el-menu :default-active="route.path" router>
        <el-menu-item v-for="m in menuItems" :key="m.path" :index="m.path">
          {{ m.title }}
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="header">
        <span class="page-title">{{ route.meta.title }}</span>
        <div class="right">
          <span class="user">{{ auth.user?.nickname || auth.user?.username }}</span>
          <el-button size="small" @click="logout">退出</el-button>
        </div>
      </el-header>
      <el-main class="main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<style scoped>
.layout {
  height: 100vh;
}
.aside {
  background: #001529;
}
.brand {
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-weight: 600;
}
.aside :deep(.el-menu) {
  border-right: none;
  background: #001529;
}
.aside :deep(.el-menu-item) {
  color: rgba(255, 255, 255, 0.7);
}
.aside :deep(.el-menu-item.is-active) {
  color: #fff;
  background: #4f7cff;
}
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #e5e6eb;
}
.page-title {
  font-weight: 600;
}
.right {
  display: flex;
  align-items: center;
  gap: 12px;
}
.user {
  color: #646a73;
}
.main {
  background: #f5f7fa;
}
</style>