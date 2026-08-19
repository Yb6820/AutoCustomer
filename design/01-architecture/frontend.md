# 前端架构设计（Vue 3 双工程 Monorepo）

> 配套图表：[frontend-architecture.png](./frontend-architecture.png) · 总览见 [system-architecture.png](./system-architecture.png)

## 1. 工程组织

pnpm workspace monorepo，三个应用/包：

| 包 | 用途 |
|---|---|
| `apps/customer-chat` | C 端对话应用（客户使用，Web/H5/小程序内嵌） |
| `apps/admin-console` | 运营管理后台（Element Plus，运营/客服/AI 工程师使用） |
| `packages/@auto/api` | OpenAPI 生成的类型化 API 客户端 + WS/SSE 封装 |
| `packages/@auto/ui` | 跨工程通用组件（EmptyState、PageHeader、ConfirmDialog…） |
| `packages/@auto/shared` | 共享类型、常量（错误码/枚举）、工具函数 |

> API 客户端由后端 FastAPI 的 OpenAPI schema（`/openapi.json`）生成，保证前后端契约零漂移。

## 2. 技术栈（锁定）

Vite 5 · Vue 3.4（Composition API + `<script setup>`）· TypeScript strict · Pinia（持久化插件）· Vue Router 4（动态路由）· Element Plus（仅 admin）· axios · 原生 EventSource（SSE）· WebSocket（心跳重连封装）· ECharts（报表）· Vitest + Playwright · ESLint + Prettier + Stylelint

## 3. 目录结构（两个 app 一致骨架）

```
apps/customer-chat/
├─ src/
│  ├─ api/            # @auto/api 按域二次封装
│  ├─ views/          # 路由页面（聊天/会话列表/订单联查/FAQ/转接/评价）
│  ├─ components/     # 业务组件（ChatBox/MessageBubble/StreamingTyping/QuickReply...）
│  ├─ composables/    # useSSE/useWebSocket/useChatScroll/useTransfer
│  ├─ stores/         # auth / chat / faq
│  ├─ router/         # 静态路由 + 守卫
│  ├─ styles/         # 设计令牌（CSS vars，与 admin 共用色板）
│  └─ main.ts
└─ vite.config.ts

apps/admin-console/
├─ src/
│  ├─ views/          # dashboard/kb/sessions/tickets/rbac/models/reports/audit
│  ├─ components/     # DocEditor/ChunkPreview/PermTree/RoleMatrix/SessionViewer...
│  ├─ directives/     # v-perm 按钮级权限指令
│  ├─ stores/         # auth(user+perms) / app(动态菜单) / kb / rbac
│  └─ router/         # 动态路由：登录后拉取 sys_menu 生成
```

## 4. 权限控制三层（与 RBAC 设计联动）

| 层 | 机制 |
|---|---|
| 菜单级 | 登录后请求 `/api/v1/auth/menus`（后端按角色并集过滤 sys_menu）→ 动态注册路由 + 渲染侧边栏 |
| 按钮级 | `v-perm="'kb:doc:publish'"` 指令，权限集来自 `auth.perms`（Pinia） |
| API 级 | 后端 `require_permission` 最终防线（前端只是体验层，不承担安全） |

## 5. 通信协议

| 场景 | 协议 | 要点 |
|---|---|---|
| 常规 CRUD | axios（@auto/api 统一封装） | 拦截器：注入 JWT / 401 静默刷新 / 统一错误 toast |
| 流式对话 | **SSE（EventSource）** | `data:` 帧 `{delta, done, msg_id}`；断线 Last-Event-ID 续传 |
| 坐席实时工单 | WebSocket | 心跳 30s，指数退避重连，消息信封 `{type, seq, payload}` |

## 6. 质量门禁

- `vue-tsc --noEmit` + ESLint 零 error；
- Vitest 单测行覆盖 ≥ 70%（stores/composables/utils 必测）；
- Playwright E2E：C 端提问→流式渲染→转人工卡片；admin 登录→权限菜单→知识库发布；
- Storybook 管理 `@auto/ui` 与关键业务组件文档。

## 7. 变更记录

| 日期 | 变更 |
|---|---|
| 2026-08-19 | 初版：双工程 monorepo、动态路由权限、SSE/WS 协议约定 |
