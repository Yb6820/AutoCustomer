<script setup lang="ts">
import { onMounted, ref } from "vue";
import { ElMessage } from "element-plus";
import { api } from "../api";
import { DOCUMENT_STATUS, formatDateTime } from "@auto/shared";
import type { KbDocument } from "@auto/shared";

const docs = ref<KbDocument[]>([]);
const loading = ref(false);

const statusText: Record<number, string> = {
  [DOCUMENT_STATUS.DRAFT]: "草稿",
  [DOCUMENT_STATUS.PENDING_REVIEW]: "待审核",
  [DOCUMENT_STATUS.PUBLISHED]: "已发布",
  [DOCUMENT_STATUS.OFFLINE]: "已下线",
};

async function load(): Promise<void> {
  loading.value = true;
  try {
    docs.value = await api.kb.listDocuments();
  } finally {
    loading.value = false;
  }
}

async function publish(id: number): Promise<void> {
  try {
    await api.kb.publish(id);
    ElMessage.success("文档已发布");
    await load();
  } catch (e) {
    ElMessage.error("发布失败");
    console.error(e);
  }
}

async function offline(id: number): Promise<void> {
  try {
    await api.kb.offline(id);
    ElMessage.success("文档已下线");
    await load();
  } catch (e) {
    ElMessage.error("下线失败");
    console.error(e);
  }
}

onMounted(load);
</script>

<template>
  <el-card>
    <template #header>知识库文档</template>
    <el-table v-loading="loading" :data="docs">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="title" label="标题" />
      <el-table-column prop="file_type" label="类型" width="100" />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">{{ statusText[row.status] ?? row.status }}</template>
      </el-table-column>
      <el-table-column label="发布时间" width="180">
        <template #default="{ row }">{{ formatDateTime(row.published_at) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="160">
        <template #default="{ row }">
          <el-button v-if="row.status !== DOCUMENT_STATUS.PUBLISHED" size="small" type="primary" v-perm="'kb:doc:publish'" @click="publish(row.id)">
            发布
          </el-button>
          <el-button v-if="row.status === DOCUMENT_STATUS.PUBLISHED" size="small" type="danger" v-perm="'kb:doc:offline'" @click="offline(row.id)">
            下线
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </el-card>
</template>