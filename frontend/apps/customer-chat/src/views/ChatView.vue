<script setup lang="ts">
import { computed, nextTick, onMounted, ref } from "vue";
import { useAuthStore } from "../stores/auth";
import { useChatStore } from "../stores/chat";
import { api } from "../api";
import MessageBubble from "../components/MessageBubble.vue";
import type { ChatMessage } from "@auto/shared";

const auth = useAuthStore();
const chat = useChatStore();

const input = ref("");
const scrollRef = ref<HTMLElement | null>(null);

const customerId = computed(() => auth.user?.username ?? "guest");

async function scrollToBottom(): Promise<void> {
  await nextTick();
  scrollRef.value?.scrollTo({ top: scrollRef.value.scrollHeight });
}

onMounted(async () => {
  try {
    const session = await chat.ensureSession(customerId.value);
    await chat.loadMessages(session.id);
    await scrollToBottom();
  } catch (e) {
    console.error("初始化会话失败", e);
  }
});

async function send(): Promise<void> {
  const text = input.value.trim();
  if (!text || chat.streaming) return;
  input.value = "";

  const session = await chat.ensureSession(customerId.value);
  chat.sendMessage(session.id, text);
  await scrollToBottom();
}

async function transfer(): Promise<void> {
  if (!chat.session) return;
  try {
    await api.chat.transfer(chat.session.id, "用户请求转人工");
  } catch (e) {
    console.error("转人工失败", e);
  }
}

const displayMessages = computed<ChatMessage[]>(() => {
  const list = [...chat.messages];
  if (chat.streaming && chat.streamBuffer) {
    list.push({
      id: 0,
      session_id: chat.session?.id ?? 0,
      role: "assistant",
      content: chat.streamBuffer,
      msg_type: "text",
      created_at: new Date().toISOString(),
    });
  }
  return list;
});
</script>

<template>
  <div class="chat">
    <header class="header">
      <span class="title">电商智能客服</span>
      <div class="actions">
        <button class="ghost" @click="transfer">转人工</button>
        <button class="ghost" @click="auth.logout()">退出</button>
      </div>
    </header>

    <main ref="scrollRef" class="messages">
      <div v-for="(m, i) in displayMessages" :key="i">
        <MessageBubble :message="m" />
      </div>
      <p v-if="displayMessages.length === 0" class="empty">您好，有什么可以帮您？</p>
    </main>

    <footer class="composer">
      <input
        v-model="input"
        type="text"
        placeholder="请输入您的问题…"
        :disabled="chat.streaming"
        @keydown.enter="send"
      />
      <button class="send" :disabled="chat.streaming || !input.trim()" @click="send">发送</button>
    </footer>
  </div>
</template>

<style scoped>
.chat {
  height: 100%;
  display: flex;
  flex-direction: column;
}
.header {
  height: 56px;
  padding: 0 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
}
.title {
  font-weight: 600;
  font-size: 16px;
}
.actions {
  display: flex;
  gap: 8px;
}
.ghost {
  height: 32px;
  padding: 0 12px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: transparent;
  cursor: pointer;
  font-size: 13px;
}
.messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
}
.empty {
  margin: auto;
  color: var(--color-text-secondary);
}
.composer {
  padding: 12px 16px;
  display: flex;
  gap: 8px;
  background: var(--color-surface);
  border-top: 1px solid var(--color-border);
}
.composer input {
  flex: 1;
  height: 40px;
  padding: 0 12px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: 14px;
}
.send {
  height: 40px;
  padding: 0 20px;
  border: none;
  border-radius: var(--radius-md);
  background: var(--color-primary);
  color: #fff;
  cursor: pointer;
  font-size: 14px;
}
.send:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>