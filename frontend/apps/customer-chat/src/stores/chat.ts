import { ref } from "vue";
import { defineStore } from "pinia";
import type { ChatMessage, ChatSession } from "@auto/shared";
import type { SseChatStream } from "@auto/api";
import { api } from "../api";

export const useChatStore = defineStore("chat", () => {
  const session = ref<ChatSession | null>(null);
  const messages = ref<ChatMessage[]>([]);
  const streaming = ref(false);
  const streamBuffer = ref("");

  let activeStream: SseChatStream | null = null;

  async function ensureSession(customerId: string): Promise<ChatSession> {
    if (!session.value) {
      session.value = await api.chat.createSession(customerId);
    }
    return session.value;
  }

  async function loadMessages(sessionId: number): Promise<void> {
    messages.value = await api.chat.messages(sessionId);
  }

  function pushMessage(message: ChatMessage): void {
    messages.value.push(message);
  }

  function sendMessage(sessionId: number, text: string): void {
    pushMessage({
      id: 0,
      session_id: sessionId,
      role: "user",
      content: text,
      msg_type: "text",
      created_at: new Date().toISOString(),
    });

    streaming.value = true;
    streamBuffer.value = "";

    activeStream = api.chat.stream(sessionId, {
      onDelta: (delta) => {
        streamBuffer.value += delta;
      },
      onDone: (msgId) => {
        pushMessage({
          id: msgId ?? 0,
          session_id: sessionId,
          role: "assistant",
          content: streamBuffer.value,
          msg_type: "text",
          created_at: new Date().toISOString(),
        });
        streaming.value = false;
        streamBuffer.value = "";
      },
      onError: () => {
        streaming.value = false;
        streamBuffer.value = "";
      },
    });
    void activeStream.start();
  }

  function stopStream(): void {
    activeStream?.close();
    streaming.value = false;
  }

  return { session, messages, streaming, streamBuffer, ensureSession, loadMessages, sendMessage, stopStream };
});