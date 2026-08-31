/**
 * @auto/api —— 类型化 API 客户端 + SSE/WS 封装统一出口。
 */
import type { AxiosInstance } from "axios";
import type {
  ChatMessage,
  ChatSession,
  HumanTicket,
  KbDocument,
  LoginRequest,
  RoleInfo,
  StreamTicketResponse,
  TokenResponse,
  UserInfo,
} from "@auto/shared";
import type { SseChatOptions } from "./sse";
import { SseChatStream } from "./sse";

export { createApiClient, login as rawLogin } from "./client";
export { tokenStore } from "./token";
export { SseChatStream } from "./sse";
export { WsClient } from "./ws";
export type { StreamFrame, SseChatOptions } from "./sse";
export type { WsClientOptions, WsMessage } from "./ws";

/** 按后端路由域组织的类型化 API。 */
export interface AutoApi {
  auth: {
    login(req: LoginRequest): Promise<TokenResponse>;
    logout(): Promise<{ message: string }>;
  };
  users: {
    list(skip?: number, limit?: number): Promise<UserInfo[]>;
    me(): Promise<UserInfo>;
    create(req: Partial<UserInfo> & { username: string; password: string }): Promise<UserInfo>;
  };
  roles: {
    list(): Promise<RoleInfo[]>;
    create(req: { code: string; name: string; data_scope?: number; remark?: string }): Promise<RoleInfo>;
    assignPermission(roleId: number, permId: number): Promise<{ message: string }>;
  };
  kb: {
    listDocuments(categoryId?: number, skip?: number, limit?: number): Promise<KbDocument[]>;
    createDocument(req: {
      title: string;
      file_type: string;
      file_url: string;
      file_hash: string;
      category_id?: number;
    }): Promise<KbDocument>;
    publish(docId: number): Promise<{ message: string }>;
    offline(docId: number): Promise<{ message: string }>;
  };
  chat: {
    createSession(customerId: string, source?: string): Promise<ChatSession>;
    messages(sessionId: number, skip?: number, limit?: number): Promise<ChatMessage[]>;
    streamTicket(sessionId: number): Promise<string>;
    /** 建立 SSE 流式对话，回调见 SseChatOptions */
    stream(sessionId: number, opts: Omit<SseChatOptions, "url" | "fetchTicket">): SseChatStream;
    transfer(sessionId: number, reason?: string): Promise<{ message: string }>;
  };
  tickets: {
    list(skip?: number, limit?: number): Promise<HumanTicket[]>;
    create(req: { session_id: number; reason?: string; priority?: number }): Promise<HumanTicket>;
    assign(ticketId: number, assigneeId: number): Promise<{ message: string }>;
    resolve(ticketId: number): Promise<{ message: string }>;
  };
  admin: {
    auditLogs(skip?: number, limit?: number): Promise<Record<string, unknown>[]>;
  };
}

export function createApi(client: AxiosInstance): AutoApi {
  return {
    auth: {
      login: (req) => client.post("/auth/login", req).then((r) => r.data),
      logout: () => client.post("/auth/logout").then((r) => r.data),
    },
    users: {
      list: (skip = 0, limit = 100) => client.get("/users", { params: { skip, limit } }).then((r) => r.data),
      me: () => client.get("/users/me").then((r) => r.data),
      create: (req) => client.post("/users", req).then((r) => r.data),
    },
    roles: {
      list: () => client.get("/roles").then((r) => r.data),
      create: (req) => client.post("/roles", req).then((r) => r.data),
      assignPermission: (roleId, permId) =>
        client.post(`/roles/${roleId}/permissions/${permId}`).then((r) => r.data),
    },
    kb: {
      listDocuments: (categoryId, skip = 0, limit = 100) =>
        client
          .get("/kb/documents", { params: { category_id: categoryId, skip, limit } })
          .then((r) => r.data),
      createDocument: (req) => client.post("/kb/documents", req).then((r) => r.data),
      publish: (docId) => client.post(`/kb/documents/${docId}/publish`).then((r) => r.data),
      offline: (docId) => client.post(`/kb/documents/${docId}/offline`).then((r) => r.data),
    },
    chat: {
      createSession: (customerId, source = "web") =>
        client.post("/chat/sessions", { customer_id: customerId, source }).then((r) => r.data),
      messages: (sessionId, skip = 0, limit = 100) =>
        client.get(`/chat/sessions/${sessionId}/messages`, { params: { skip, limit } }).then((r) => r.data),
      streamTicket: (sessionId) =>
        client.post<StreamTicketResponse>("/chat/stream-ticket", null, { params: { session_id: sessionId } }).then((r) => r.data.ticket),
      stream: (sessionId, opts) =>
        new SseChatStream({
          ...opts,
          url: `${client.defaults.baseURL ?? ""}/chat/sessions/${sessionId}/stream`,
          fetchTicket: () => createApi(client).chat.streamTicket(sessionId),
        }),
      transfer: (sessionId, reason = "用户请求转人工") =>
        client.post(`/chat/sessions/${sessionId}/transfer`, null, { params: { reason } }).then((r) => r.data),
    },
    tickets: {
      list: (skip = 0, limit = 50) => client.get("/tickets", { params: { skip, limit } }).then((r) => r.data),
      create: (req) => client.post("/tickets", req).then((r) => r.data),
      assign: (ticketId, assigneeId) =>
        client.post(`/tickets/${ticketId}/assign`, null, { params: { assignee_id: assigneeId } }).then((r) => r.data),
      resolve: (ticketId) => client.post(`/tickets/${ticketId}/resolve`).then((r) => r.data),
    },
    admin: {
      auditLogs: (skip = 0, limit = 100) =>
        client.get("/admin/audit-logs", { params: { skip, limit } }).then((r) => r.data),
    },
  };
}