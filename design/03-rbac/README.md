# RBAC 权限体系设计

> 配套图表：[rbac-model.png](./rbac-model.png) · 表结构见 [../02-database/README.md](../02-database/README.md) 第 3 节

## 1. 模型总览

经典 RBAC + 两个扩展，满足电商客服组织的完整性诉求：

```
sys_user ─N:M─ sys_user_role ─N:M─ sys_role ─N:M─ sys_role_perm ─N:M─ sys_permission ─N:1─ sys_menu
                                      │
                                      ├─ data_scope 枚举（ALL/DEPT/DEPT_AND_CHILD/SELF/CUSTOM）
                                      └─ sys_role_data_scope（CUSTOM 时关联 sys_dept）
```

**核心规则**：

1. **多角色叠加**：一用户可绑多角色，权限码取**并集**；数据范围取**最宽档**（ALL > DEPT_AND_CHILD > DEPT > SELF；CUSTOM 取并集部门）。
2. **权限点三级**：`menu`（控制动态路由）/ `btn`（控制 v-perm）/ `api`（后端 require_permission 最终防线）。三级同源一个 perm_code，一处授权三处生效。
3. **内置角色保护**：`is_system=1` 的角色不可删除、不可改 code，可"另存为"派生成自定义角色。
4. **即时生效**：权限集 Redis 缓存（TTL 10min），角色/绑定变更主动失效，前端下次请求刷新菜单与 perms，**无需重启**。

## 2. 预置角色（10 个 / 4 分组）

### 系统管理组

| 角色 code | 名称 | 数据范围 | 权限摘要 |
|---|---|---|---|
| `super_admin` | 超级管理员 | ALL | 全部权限（含模型配置、角色管理、系统配置） |
| `sys_admin` | 系统管理员 | ALL | 用户/部门/角色/菜单/审计日志；不含模型配置 |
| `auditor` | 审计员 | ALL（只读） | 审计日志、登录日志只读；无任何写权限 |

### 业务运营组

| 角色 code | 名称 | 数据范围 | 权限摘要 |
|---|---|---|---|
| `operator` | 运营主管 | ALL | 仪表盘、知识库全量、报表导出、工单分配/转派 |
| `kb_editor` | 知识库编辑 | SELF | 文档 CRUD 限本人创建；提交审核，无发布权 |
| `kb_reviewer` | 知识库审核 | ALL | 文档发布/下线审核、版本回退 |
| `viewer` | 只读访客 | ALL（只读） | 各业务模块只读（参观/交接/风控查证） |

### 客服组

| 角色 code | 名称 | 数据范围 | 权限摘要 |
|---|---|---|---|
| `agent_leader` | 客服组长 | DEPT_AND_CHILD | 工单分配/转派、坐席在线监控、会话质检 |
| `agent` | 人工客服 | SELF | 回复分配给自己的工单、查看关联会话上下文 |

### 技术组

| 角色 code | 名称 | 数据范围 | 权限摘要 |
|---|---|---|---|
| `ai_engineer` | AI 工程师 | ALL | 模型配置、Prompt 模板、检索参数、黄金集评估任务 |

## 3. 权限码全量清单（种子数据，Alembic 维护）

命名规范：`模块:资源:动作`，全小写。新增模块时在迁移中追加本清单。

### 认证与账户

`auth:login` `auth:refresh` `auth:logout` `auth:password:change` `auth:mfa:setup`

### RBAC 管理

`rbac:user:view/create/update/delete` `rbac:role:view/create/update/delete` `rbac:perm:view` `rbac:menu:view/create/update/delete` `rbac:dept:view/create/update/delete` `rbac:audit:view` `rbac:loginlog:view`

### 知识库

`kb:category:view/create/update/delete` `kb:doc:view/create/update/delete/publish/offline` `kb:chunk:view/reindex` `kb:qa:view/create/update/delete` `kb:task:view/retry` `kb:import:create`

### 对话与工单

`chat:session:view` `chat:message:view` `chat:feedback:view` `chat:quickreply:view/create/update/delete` `ticket:view/assign/transfer/claim/reply/close` `ticket:comment:internal` `agent:group:view/create/update/delete` `agent:profile:view/update` `agent:monitor:view`

### AI 配置与报表

`system:model:view/create/update/delete/test` `system:prompt:view/create/update` `system:retrieval:view/update` `report:dashboard:view` `report:export` `golden:eval:run/view`

## 4. 数据范围（五档）与实现

| 枚举 | 含义 | Repository 注入的过滤条件（示例） |
|---|---|---|
| ALL | 全部 | 无附加条件 |
| DEPT | 本部门 | `dept_id == user.dept_id` |
| DEPT_AND_CHILD | 本部门及下级 | `dept_id IN (本部门+递归子部门)`（部门树缓存 Redis） |
| SELF | 仅本人 | `created_by == user.id` 或 `assignee_id == agent.id` |
| CUSTOM | 自定义部门 | `dept_id IN (sys_role_data_scope 关联部门)` |

- 过滤器由 `domain/rbac/data_scope.py` 统一生成，Repository 层套用，Service 无感知。
- 客户身份（`chat_session.customer_id` 为外部 ID）不参与 RBAC；C 端接口走独立 JWT（audience=customer）。

## 5. 新角色快速接入 SOP（零代码 · 约 5 分钟）

1. **新建角色**：后台「角色管理 → 新建」填 code（如 `vip_agent`）/ 名称 / role_type=自定义 / 数据范围。
2. **勾选权限**：权限树勾选（菜单+按钮+API 同步勾选）；可点「复制现有角色」以 `agent` 为模板加速。
3. **配置数据范围**：选枚举，或 CUSTOM 时勾选部门树节点。
4. **绑定用户**：单个或批量绑定；用户已有其他角色则权限并集、数据范围取宽。
5. **即时生效**：保存即失效相关权限缓存；该用户下一次请求自动应用新菜单/权限。

> **何时需要动代码**：仅当出现**全新权限点**（新模块/新动作）时，需在 Alembic 迁移中注册权限点并同步本清单第 3 节；角色层面的增删改全部无需代码变更。

## 6. 与审计联动

所有 `rbac:*` 写操作、权限缓存失效事件写入 `sys_audit_log`（detail 含变更前后快照）；`auditor` 可追溯"谁在何时给了谁什么权限"。

## 7. 变更记录

| 日期 | 变更 |
|---|---|
| 2026-08-19 | 初版：10 预置角色/4 分组、五档数据范围、权限码全量清单、新角色 5 步接入 SOP |
