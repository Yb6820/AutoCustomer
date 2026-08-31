<script setup lang="ts">
import { onMounted, ref } from "vue";
import { api } from "../api";
import type { UserInfo } from "@auto/shared";

const users = ref<UserInfo[]>([]);
const loading = ref(false);

async function load(): Promise<void> {
  loading.value = true;
  try {
    users.value = await api.users.list();
  } finally {
    loading.value = false;
  }
}

onMounted(load);
</script>

<template>
  <el-card>
    <template #header>用户管理</template>
    <el-table v-loading="loading" :data="users">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="username" label="用户名" />
      <el-table-column prop="nickname" label="昵称" />
      <el-table-column prop="email" label="邮箱" />
      <el-table-column prop="phone" label="手机号" />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.status === 1 ? 'success' : 'info'">
            {{ row.status === 1 ? "启用" : "禁用" }}
          </el-tag>
        </template>
      </el-table-column>
    </el-table>
  </el-card>
</template>