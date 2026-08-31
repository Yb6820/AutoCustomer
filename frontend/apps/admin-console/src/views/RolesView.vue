<script setup lang="ts">
import { onMounted, ref } from "vue";
import { api } from "../api";
import type { RoleInfo } from "@auto/shared";

const roles = ref<RoleInfo[]>([]);
const loading = ref(false);

async function load(): Promise<void> {
  loading.value = true;
  try {
    roles.value = await api.roles.list();
  } finally {
    loading.value = false;
  }
}

onMounted(load);
</script>

<template>
  <el-card>
    <template #header>角色管理</template>
    <el-table v-loading="loading" :data="roles">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="code" label="角色编码" />
      <el-table-column prop="name" label="角色名称" />
      <el-table-column prop="role_type" label="类型" width="90" />
      <el-table-column prop="data_scope" label="数据范围" width="100" />
      <el-table-column label="系统内置" width="100">
        <template #default="{ row }">
          <el-tag :type="row.is_system ? 'info' : 'success'">
            {{ row.is_system ? "内置" : "自定义" }}
          </el-tag>
        </template>
      </el-table-column>
    </el-table>
  </el-card>
</template>