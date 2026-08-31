<script setup lang="ts">
import { onMounted, ref } from "vue";
import { api } from "../api";
import { TICKET_PRIORITY, TICKET_STATUS, formatDateTime } from "@auto/shared";
import type { HumanTicket } from "@auto/shared";

const tickets = ref<HumanTicket[]>([]);
const loading = ref(false);

const statusText: Record<number, string> = {
  [TICKET_STATUS.PENDING]: "待处理",
  [TICKET_STATUS.ASSIGNED]: "已分配",
  [TICKET_STATUS.PROCESSING]: "处理中",
  [TICKET_STATUS.RESOLVED]: "已解决",
  [TICKET_STATUS.CLOSED]: "已关闭",
};

const priorityText: Record<number, string> = {
  [TICKET_PRIORITY.LOW]: "低",
  [TICKET_PRIORITY.MEDIUM]: "中",
  [TICKET_PRIORITY.HIGH]: "高",
  [TICKET_PRIORITY.URGENT]: "紧急",
};

async function load(): Promise<void> {
  loading.value = true;
  try {
    tickets.value = await api.tickets.list();
  } finally {
    loading.value = false;
  }
}

onMounted(load);
</script>

<template>
  <el-card>
    <template #header>人工工单</template>
    <el-table v-loading="loading" :data="tickets">
      <el-table-column prop="ticket_no" label="工单号" width="160" />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">{{ statusText[row.status] ?? row.status }}</template>
      </el-table-column>
      <el-table-column label="优先级" width="100">
        <template #default="{ row }">{{ priorityText[row.priority] ?? row.priority }}</template>
      </el-table-column>
      <el-table-column prop="reason" label="转接原因" />
      <el-table-column label="创建时间" width="180">
        <template #default="{ row }">{{ formatDateTime(row.created_at) }}</template>
      </el-table-column>
    </el-table>
  </el-card>
</template>