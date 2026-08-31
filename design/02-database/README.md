# 数据库原型设计（MySQL 8.0 + Milvus 2.x）

> 配套图表：[er-diagram-mysql.png](./er-diagram-mysql.png)（29 表 / 6 主题域） · [milvus-collections.png](./milvus-collections.png)
>
> 本文档是数据库层的**唯一权威设计来源**。任何表结构变更必须先更新本文档与 ER 图（见 `/design/README.md` 的同步 SOP），再通过 Alembic 迁移落地。

## 1. 通用约定

| 约定项 | 规则 |
|---|---|
| 存储引擎 / 字符集 | InnoDB / `utf8mb4` |
| 主键 | `id BIGINT UNSIGNED AUTO_INCREMENT`（雪花 ID 预留：分库分表时切换） |
| 时间字段 | `created_at` / `updated_at DATETIME(3)`，默认 `CURRENT_TIMESTAMP(3)`，应用层不写 |
| 软删除 | 业务表带 `deleted_at DATETIME(3) NULL`，查询统一走 `deleted_at IS NULL` 过滤 |
| 状态字段 | `TINYINT` + 注释枚举（1/2/3...），禁止魔法数字散落代码 |
| 命名 | 表 `模块_实体`（snake_case）；索引 `idx_表_字段`；唯一索引 `uk_表_字段` |
| JSON 字段 | MySQL 8 原生 `JSON`，仅用于非结构化扩展（meta/snapshot/params），**禁止**承载需要查询的业务字段 |
| 敏感数据 | `password_hash`（argon2id）、`api_key_enc`（AES-GCM）、手机号/邮箱（脱敏存储或加密） |
| 外键 | **不建物理外键**（性能与运维考虑），通过应用层 Repository 保证一致性；本文档 FK 标记表示逻辑外键 |

## 2. 主题域划分

| 域 | 表数量 | 职责 |
|---|---|---|
| RBAC 用户与权限 | 10 | 用户、部门、角色、权限、菜单、数据范围、审计/登录日志 |
| 知识库 | 5 | 分类、文档、分片、问答对、导入任务 |
| 对话 | 5 | 会话、消息、检索日志、消息反馈、快捷回复 |
| 工单与坐席 | 5 | 客服组、坐席档案、人工工单、工单沟通、流转记录 |
| AI 配置 | 3 | 模型配置、Prompt 模板、检索配置 |
| 统计 | 1 | 日统计物化表 |

---

## 3. RBAC 用户与权限域（10 表）

### 3.1 sys_user 用户表

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| id | BIGINT UNSIGNED | PK, AI | 用户 ID |
| dept_id | BIGINT UNSIGNED | NULL, 逻辑FK→sys_dept | 所属部门（数据范围判定） |
| username | VARCHAR(64) | UK | 登录名 |
| password_hash | VARCHAR(255) | NOT NULL | argon2id 哈希 |
| nickname | VARCHAR(64) | | 显示名 |
| email | VARCHAR(128) | | 邮箱（加密存储可选） |
| phone | VARCHAR(32) | | 手机号（加密存储可选） |
| avatar_url | VARCHAR(512) | | 头像 |
| status | TINYINT | 1=启用 2=禁用 | 账号状态 |
| mfa_secret_enc | VARBINARY(255) | NULL | TOTP 密钥（AES-GCM 加密） |
| last_login_at | DATETIME(3) | | 最后登录时间 |
| created_at / updated_at / deleted_at | DATETIME(3) | | |

索引：`uk_sys_user_username(username)`；`idx_sys_user_dept_id(dept_id)`

### 3.2 sys_dept 部门表（树形）

| 字段 | 类型 | 说明 |
|---|---|---|
| id | BIGINT PK | |
| parent_id | BIGINT | 逻辑FK→本表，根节点为 0 |
| name / leader_user_id / sort / status / created_at / updated_at / deleted_at | | 部门名 / 负责人 / 排序 / 状态 |

索引：`idx_sys_dept_parent_id(parent_id)`

### 3.3 sys_role 角色表

| 字段 | 类型 | 说明 |
|---|---|---|
| id | BIGINT PK | |
| code | VARCHAR(64) UK | 角色码，如 `agent` |
| name | VARCHAR(64) | 显示名 |
| role_type | TINYINT | 1=内置系统 2=业务预置 3=自定义 |
| data_scope | TINYINT | 1=ALL 2=DEPT 3=DEPT_AND_CHILD 4=SELF 5=CUSTOM |
| is_system | BOOL | 内置角色不可删（可禁用） |
| remark / sort / status / created_at / updated_at / deleted_at | | |

### 3.4 sys_permission 权限点表

| 字段 | 类型 | 说明 |
|---|---|---|
| id | BIGINT PK | |
| menu_id | BIGINT | 逻辑FK→sys_menu（api/btn 类型可空） |
| code | VARCHAR(128) UK | `模块:资源:动作`，如 `kb:doc:publish` |
| name | VARCHAR(64) | 显示名 |
| type | TINYINT | 1=menu 2=btn 3=api |
| api_method | VARCHAR(8) | api 类型：GET/POST/PUT/DELETE |
| api_path | VARCHAR(255) | api 类型：`/api/v1/kb/documents/{id}/publish` |
| sort / status / created_at / updated_at | | |

> 新模块的权限点通过 **Alembic 种子迁移**插入，保证环境间一致（见 03-rbac/README.md）。

### 3.5 sys_user_role 用户-角色关联

| 字段 | 说明 |
|---|---|
| id / user_id / role_id / created_at | 联合唯一 `uk_user_role(user_id, role_id)`；一用户多角色，**权限取并集，数据范围取最宽档** |

### 3.6 sys_role_perm 角色-权限关联

| 字段 | 说明 |
|---|---|
| id / role_id / perm_id / created_at | 联合唯一 `uk_role_perm(role_id, perm_id)` |

### 3.7 sys_role_data_scope 角色自定义数据范围

| 字段 | 说明 |
|---|---|
| id / role_id / dept_id / created_at | `data_scope=CUSTOM` 时生效；联合唯一 `uk_scope(role_id, dept_id)` |

### 3.8 sys_menu 菜单表（树形，前端动态路由数据源）

| 字段 | 类型 | 说明 |
|---|---|---|
| id / parent_id | BIGINT | 树形结构 |
| name / path / component / icon | VARCHAR | 菜单名 / 路由 / 组件路径 / 图标 |
| perm_code | VARCHAR(128) | 显示该菜单所需权限码（可空=仅登录） |
| sort / visible / status / created_at / updated_at | | |

### 3.9 sys_audit_log 审计日志（只增不改）

| 字段 | 类型 | 说明 |
|---|---|---|
| id / user_id | BIGINT | 操作人 |
| action | VARCHAR(64) | 动作码，如 `rbac:role:create` |
| resource | VARCHAR(128) | 资源标识，如 `role:3` |
| detail | JSON | 变更前后快照 |
| ip / user_agent | VARCHAR | 来源 |
| created_at | DATETIME(3) | |

索引：`idx_audit_user(user_id, created_at)`；`idx_audit_action(action, created_at)`。按月分区，仅 `auditor` 角色可读。

### 3.10 sys_login_log 登录日志

| 字段 | 说明 |
|---|---|
| id / user_id / username / login_type / ip / user_agent / status(1 成功 2 失败) / msg / created_at | 防爆破分析数据源 |

---

## 4. 知识库域（5 表）

### 4.1 kb_category 知识分类（树形）

id / parent_id / name / sort / status / created_at / updated_at / deleted_at

### 4.2 kb_document 知识文档

| 字段 | 类型 | 说明 |
|---|---|---|
| id | BIGINT PK | |
| category_id | BIGINT | 逻辑FK→kb_category |
| title | VARCHAR(255) | 文档标题 |
| file_type | VARCHAR(16) | pdf/docx/md/txt/html |
| file_url | VARCHAR(512) | MinIO/OSS 对象地址 |
| file_hash | CHAR(64) | SHA-256，内容去重依据 |
| status | TINYINT | 1=draft 2=pending_review 3=published 4=offline |
| version | INT | 乐观锁版本号 |
| created_by | BIGINT | 逻辑FK→sys_user（数据范围 SELF 判定依据） |
| published_at | DATETIME(3) | |
| created_at / updated_at / deleted_at | | |

索引：`idx_doc_category(category_id, status)`；`uk_doc_hash(file_hash)`（同内容去重）

### 4.3 kb_chunk 知识分片（与 Milvus 1:1 对齐的核心表）

| 字段 | 类型 | 说明 |
|---|---|---|
| id | BIGINT PK | **同步写入 Milvus 的 chunk_id** |
| doc_id | BIGINT | 逻辑FK→kb_document |
| content | TEXT | 分片原文（检索命中后回显） |
| chunk_index | INT | 文档内序号，联合唯一 |
| token_count | INT | 分片 token 数 |
| meta | JSON | `{page, section, heading}` 结构化溯源信息 |
| status | TINYINT | 1=active 2=archived（同步 Milvus 过滤） |
| embedding_status | TINYINT | 1=pending 2=done 3=failed（向量化状态对账） |
| created_at / updated_at | | |

索引：`uk_chunk_doc_idx(doc_id, chunk_index)`；`idx_chunk_embedding_status(embedding_status)`

### 4.4 kb_qa_pair 问答对（人工运营的 FAQ，可选启用）

| 字段 | 说明 |
|---|---|
| id / doc_id(可空) / chunk_id(可空) / question / answer / hit_count / status / created_at / updated_at | 命中计数用于热门 FAQ 优化；可选生成 `kb_qa_vec` 向量 |

### 4.5 kb_import_task 导入任务（异步流水线状态机）

| 字段 | 说明 |
|---|---|
| id / doc_id / task_type(parse/chunk/embed/index) / status(pending/running/done/failed) / progress(0-100) / error_msg / started_at / finished_at | 前端轮询进度条数据源；失败重试 3 次后入死信

---

## 5. 对话域（5 表）

### 5.1 chat_session 会话

| 字段 | 类型 | 说明 |
|---|---|---|
| id | BIGINT PK | |
| customer_id | VARCHAR(64) | 外部电商用户标识（无物理用户表，对接电商主站） |
| source | VARCHAR(16) | web/h5/mini/wechat |
| status | TINYINT | 1=active 2=transferred 3=closed |
| rating | TINYINT | 1-5，会话级满意度 |
| model_config_id | BIGINT | 会话开始时的模型配置快照（FK→sys_model_config） |
| transferred_reason | VARCHAR(255) | 转人工原因（策略命中/主动要求/未命中） |
| last_msg_at / created_at / updated_at | | |

索引：`idx_session_customer(customer_id, status, last_msg_at)`；`idx_session_status_time(status, created_at)`

### 5.2 chat_message 消息

| 字段 | 类型 | 说明 |
|---|---|---|
| id / session_id | BIGINT | |
| role | VARCHAR(16) | user/assistant/system/agent（人工客服回复） |
| content | MEDIUMTEXT | 消息内容 |
| msg_type | VARCHAR(16) | text/card/transfer/rating |
| tokens | INT | 消耗 token 数 |
| model | VARCHAR(64) | 实际使用的模型名（成本归因） |
| retrieval_ids | JSON | 命中的 chunk_id 列表（**答案可溯源**） |
| latency_ms | INT | 端到端耗时 |
| created_at | DATETIME(3) | |

索引：`idx_msg_session(session_id, created_at)`；`idx_msg_created(created_at)`

### 5.3 chat_retrieval_log 检索日志（RAG 质量分析核心）

| 字段 | 说明 |
|---|---|
| id / message_id / query / topk_scores(JSON: [{chunk_id, score}...]) / threshold / hit_count / rerank_used(BOOL) / latency_ms / created_at | 未命中 Top 问题分析 → 知识库补全闭环的数据源 |

索引：`idx_retrieval_message(message_id)`；`idx_retrieval_time(created_at)`

### 5.4 chat_feedback 消息反馈

id / message_id / session_id / feedback_type(1=点赞 2=点踩) / reason / created_at

索引：`idx_feedback_message(message_id)`

### 5.5 chat_quick_reply 快捷回复

id / scene(如 greeting/refund/shipping) / title / content / sort / status / created_at / updated_at

---

## 6. 工单与坐席域（5 表）

### 6.1 agent_group 客服组

id / name / description / sort / status / created_at / updated_at / deleted_at

### 6.2 agent_profile 坐席档案

| 字段 | 说明 |
|---|---|
| id / user_id(UK，逻辑FK→sys_user) / group_id / agent_no / skill_tags(JSON) / max_concurrency(同时接待上限) / online_status(1=在线 2=忙碌 3=离线) / created_at / updated_at | 与 sys_user 1:1；分配策略按组+技能+负载路由 |

### 6.3 human_ticket 人工工单

| 字段 | 类型 | 说明 |
|---|---|---|
| id / session_id | BIGINT | 关联会话 |
| ticket_no | VARCHAR(32) UK | 展示用编号 `T20260819-0001` |
| reason | VARCHAR(255) | 转入原因 |
| status | TINYINT | 1=pending 2=assigned 3=processing 4=resolved 5=closed |
| priority | TINYINT | 1=低 2=中 3=高 4=紧急（超时升级依据） |
| assignee_id | BIGINT | 逻辑FK→agent_profile（数据范围 SELF） |
| group_id | BIGINT | 当前组 |
| snapshot | JSON | 转入时会话摘要+最近 N 条消息（分析时可独立还原） |
| first_response_at / resolved_at / created_at / updated_at | | SLA 统计字段 |

索引：`idx_ticket_assignee(assignee_id, status)`；`idx_ticket_status(status, priority, created_at)`

### 6.4 ticket_comment 工单沟通记录

id / ticket_id / author_id / content / is_internal(内部备注 or 对客回复) / created_at

### 6.5 ticket_assign_log 流转记录

id / ticket_id / from_agent_id / to_agent_id / action(assign/transfer/claim/escalate/close) / operator_id / created_at

---

## 7. AI 配置域（3 表）

### 7.1 sys_model_config 模型配置

| 字段 | 类型 | 说明 |
|---|---|---|
| id / model_type | | llm / embedding / rerank |
| provider | VARCHAR(32) | qwen/llama/chatglm/deepseek/openai_compat... |
| model_name / endpoint | VARCHAR | 模型名 / API 地址（vLLM/Ollama/商用） |
| api_key_enc | VARBINARY(512) | **AES-GCM 加密**，主密钥来自 KMS/ENV |
| params | JSON | `{temperature, max_tokens, top_p}` |
| is_default | BOOL | 同 model_type 仅一个默认 |
| status / created_at / updated_at | | |

### 7.2 sys_prompt_template Prompt 模板

| 字段 | 说明 |
|---|---|
| id / scene(chat_hit/chat_miss/rewrite/summarize) / name / content(含 `{{变量}}` 占位) / variables(JSON 声明) / version / status / created_at / updated_at | 模板热更新，无需发版 |

### 7.3 kb_retrieval_config 检索配置（作用域链）

| 字段 | 说明 |
|---|---|
| id / scope(global/category/doc) / target_id(scope 对应目标 ID，global 为 0) / topk / score_threshold / rerank_enabled / rerank_model_id / status | 查找顺序：doc → category → global，实现分品类差异化检索参数 |

---

## 8. 统计域（1 表）

### 8.1 stat_daily 日统计（物化表，Celery Beat 每日 1:00 聚合）

| 字段 | 说明 |
|---|---|
| id / stat_date(UK) / session_count / message_count / ticket_count / transfer_rate / hit_rate / avg_rating / avg_first_response_ms / llm_tokens_used / created_at | 报表页直查，避免对明细表实时聚合 |

---

## 9. Milvus 向量库设计

### 9.1 集合清单

| 集合 | 状态 | 用途 |
|---|---|---|
| `kb_chunk_vec` | 核心 | kb_chunk 向量，主检索入口 |
| `kb_qa_vec` | 可选 | kb_qa_pair 问题向量，FAQ 精准命中 |
| `chat_intent_vec` | 预留 | 意图聚类/相似问题推荐（二期） |

### 9.2 kb_chunk_vec Schema

| 字段 | 类型 | 说明 |
|---|---|---|
| chunk_id | INT64 | PRIMARY KEY，与 MySQL `kb_chunk.id` 1:1 |
| doc_id | INT64 | **partition key**（默认 8 分区，按文档裁剪扫描） |
| category_id | INT64 | 标量过滤（按分类检索） |
| embedding | FLOAT_VECTOR | dim 由 Embedding 模型决定（768/1024/1536），**同集合不可混 dim** |
| status | INT8 | 1=published（可检索） 2=offline（检索表达式过滤 `status == 1`）；与 MySQL `kb_chunk.status` 映射：active→1、archived→2 |
| created_at | INT64 | 毫秒时间戳 |

### 9.3 索引与检索参数

| 项 | 值 | 说明 |
|---|---|---|
| 索引类型 | HNSW（M=16, efConstruction=256） | 召回率优先；数据 <10w 可先 IVF_FLAT |
| 距离度量 | COSINE | 与 BGE 系模型匹配 |
| 检索 | topK=20 → BGE-Reranker → topN=5 | 两阶段检索 |
| ef（检索时） | 64 | 召回/延迟平衡点，压测后可调 |
| 命中阈值 | cosine score ≥ 0.78 | 低于阈值走"未命中→转人工"分支；阈值存 `kb_retrieval_config` 可调 |

### 9.4 与 MySQL 的一致性

```
文档发布 ──► MySQL kb_chunk 行写入（embedding_status=pending）
        └─► Celery 异步向量化 ──► Milvus upsert（chunk_id 幂等） ──► embedding_status=done
```

- **写入**：批量 64/批；失败重试 3 次入死信队列，`embedding_status=failed` 可手工重跑
- **更新**：文档新版本 → `delete(expr="doc_id in [...]")` + 重新写入，版本号乐观锁防并发
- **状态映射**：同步任务统一转换 `kb_chunk.status`（1=active / 2=archived）→ Milvus `status`（1=published / 2=offline）；文档下线/归档时按映射改写 Milvus 标量，检索表达式统一过滤 `status == 1`
- **对账（增量水位线，避免全量 count 慢查询）**：Redis 维护水位线 `milvus:reconcile:watermark`（已对账最大 chunk_id）；Celery Beat 每小时仅校验增量区间——MySQL `count(id > 水位线 AND embedding_status = done)` vs Milvus `query(expr="chunk_id > 水位线")` 计数，一致则前移水位线；全量 `count()` 对账仅在每日凌晨 / 部署后首次 / 人工触发时执行；不一致告警并自动补偿（缺失 chunk 重新入队向量化）
- **重建**：新建 `kb_chunk_vec_v2` → 双写 → **alias 切换** → 删除旧集合，全程无停服
- **降级**：Milvus 不可用时自动切 MySQL 全文索引（ngram）关键词检索兜底

## 10. 种子数据（首次部署初始化）

| 内容 | 方式 |
|---|---|
| 内置 10 角色 | Alembic 迁移插入，`is_system=1` |
| 权限点全量清单 | Alembic 迁移插入（与 03-rbac/README.md 权限码清单同步维护） |
| 菜单树 | 迁移插入（前端动态路由数据源） |
| 默认检索/Prompt/模型配置 | 迁移插入，敏感字段留空由部署时 ENV 注入 |
| 超级管理员 | 迁移插入，首次登录强制改密 |

## 11. 变更记录

| 日期 | 变更 | 关联 |
|---|---|---|
| 2026-08-20 | 可行性评审修正：对账改为增量水位线（全量 count 仅每日一次）；补充 MySQL↔Milvus 状态映射规则（active→published、archived→offline） | ER 图去重边、Milvus 图 v2 |
| 2026-08-19 | 初版：29 表 / 6 域 + Milvus 双集合设计 | ER 图 v1 |
