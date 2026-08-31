<script setup lang="ts">
import { onMounted, ref } from "vue";
import { api } from "../api";

const stats = ref([
  { label: "今日会话", value: 0 },
  { label: "今日消息", value: 0 },
  { label: "人工工单", value: 0 },
  { label: "回答命中率", value: "—" },
]);

onMounted(async () => {
  // 后端 /stats 就绪后可替换为真实统计；此处演示数据载入骨架
  try {
    const tickets = await api.tickets.list(0, 1);
    void tickets;
  } catch {
    /* 统计接口未实现时忽略 */
  }
});
</script>

<template>
  <div>
    <el-row :gutter="16">
      <el-col v-for="s in stats" :key="s.label" :span="6">
        <el-card shadow="hover">
          <div class="stat-value">{{ s.value }}</div>
          <div class="stat-label">{{ s.label }}</div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped>
.stat-value {
  font-size: 28px;
  font-weight: 600;
}
.stat-label {
  margin-top: 8px;
  color: #646a73;
}
</style>