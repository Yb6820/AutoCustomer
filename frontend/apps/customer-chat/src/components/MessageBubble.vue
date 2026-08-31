<script setup lang="ts">
import { computed } from "vue";
import type { ChatMessage } from "@auto/shared";

const props = defineProps<{ message: ChatMessage }>();

const isUser = computed(() => props.message.role === "user");
const isAssistant = computed(() => props.message.role === "assistant");
</script>

<template>
  <div class="bubble" :class="[isUser ? 'user' : 'assistant']">
    <div class="content">{{ message.content }}</div>
    <div class="meta">
      <span v-if="isAssistant && message.id === 0">流式生成中…</span>
      <span v-else-if="isUser">我</span>
      <span v-else>客服</span>
    </div>
  </div>
</template>

<style scoped>
.bubble {
  max-width: 72%;
  margin-bottom: 12px;
}
.bubble.user {
  align-self: flex-end;
}
.bubble.assistant {
  align-self: flex-start;
}
.content {
  padding: 10px 14px;
  border-radius: var(--radius-lg);
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-word;
}
.user .content {
  background: var(--color-primary);
  color: #fff;
  border-bottom-right-radius: 4px;
}
.assistant .content {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-bottom-left-radius: 4px;
}
.meta {
  margin-top: 4px;
  font-size: 12px;
  color: var(--color-text-secondary);
}
.user .meta {
  text-align: right;
}
</style>