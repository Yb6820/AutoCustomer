/**
 * @auto/shared —— 共享类型、常量、工具函数。
 *
 * 与后端 FastAPI 的 Pydantic Schema 对齐，作为前后端契约的唯一 TS 来源。
 */

// ============ 通用响应 ============
export interface ApiError {
  detail: string;
}

export interface PageQuery {
  skip?: number;
  limit?: number;
}

// ============ 认证 ============
export interface LoginRequest {
  username: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface UserInfo {
  id: number;
  username: string;
  nickname: string;
  email: string;
  phone: string;
  status: number;
  dept_id: number | null;
}

// ============ 对话域 ============
export type MessageRole = "user" | "assistant" | "system" | "agent";

export type SessionStatus = 1 | 2 | 3; // 1=active 2=transferred 3=closed

export interface ChatSession {
  id: number;
  customer_id: string;
  source: string;
  status: SessionStatus;
  last_msg_at: string | null;
}

export interface ChatMessage {
  id: number;
  session_id: number;
  role: MessageRole;
  content: string;
  msg_type: string;
  created_at: string;
}

export interface StreamTicketResponse {
  ticket: string;
}

// ============ 知识库域 ============
export type DocumentStatus = 1 | 2 | 3 | 4; // 1=draft 2=pending_review 3=published 4=offline

export interface KbDocument {
  id: number;
  title: string;
  file_type: string;
  file_url: string;
  status: DocumentStatus;
  category_id: number | null;
  created_by: number | null;
  published_at: string | null;
}

// ============ 工单域 ============
export type TicketStatus = 1 | 2 | 3 | 4 | 5; // 1=pending 2=assigned 3=processing 4=resolved 5=closed

export type TicketPriority = 1 | 2 | 3 | 4; // 1=低 2=中 3=高 4=紧急

export interface HumanTicket {
  id: number;
  ticket_no: string;
  session_id: number;
  reason: string | null;
  status: TicketStatus;
  priority: TicketPriority;
  assignee_id: number | null;
  created_at: string;
}

// ============ RBAC 域 ============
export interface RoleInfo {
  id: number;
  code: string;
  name: string;
  role_type: number;
  data_scope: number;
  is_system: boolean;
  status: number;
}

// ============ 常量 ============
export const SESSION_STATUS = {
  ACTIVE: 1,
  TRANSFERRED: 2,
  CLOSED: 3,
} as const;

export const DOCUMENT_STATUS = {
  DRAFT: 1,
  PENDING_REVIEW: 2,
  PUBLISHED: 3,
  OFFLINE: 4,
} as const;

export const TICKET_STATUS = {
  PENDING: 1,
  ASSIGNED: 2,
  PROCESSING: 3,
  RESOLVED: 4,
  CLOSED: 5,
} as const;

export const TICKET_PRIORITY = {
  LOW: 1,
  MEDIUM: 2,
  HIGH: 3,
  URGENT: 4,
} as const;

// ============ 工具函数 ============
export function formatDateTime(iso: string | null | undefined): string {
  if (!iso) return "-";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "-";
  return d.toLocaleString("zh-CN", { hour12: false });
}

export function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}