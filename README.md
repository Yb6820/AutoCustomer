# AutoCustomer · 电商智能客服机器人

> 基于 **RAG + 可插拔大模型** 的电商智能客服系统：能自动回答客户高频问题，未命中或需人工时自动流转工单，并提供完整的管理后台与 RBAC 权限体系。

## 1. 项目概要

AutoCustomer 是一套**前后端分离**的智能客服机器人，面向电商场景（商品咨询、订单、物流、售后、活动规则等）。

- **后端**：Python 3.12 + FastAPI，采用 DDD 五层架构（接入层 / 应用服务层 / 领域层 / 基础设施层 / 异步任务层），模块化单体设计，未来可平滑拆分为微服务。
- **前端**：Vue 3 + Vite 5 + TypeScript strict 的 pnpm 双工程 monorepo（C 端对话应用 + 运营管理后台）。
- **数据**：MySQL 8.0（业务数据，29 表）· Milvus（向量检索）· Redis（缓存 / Celery Broker）· MinIO（对象存储）。
- **AI**：RAG 检索增强生成（向量检索 → 重排 → 阈值过滤 → 大模型生成），LLM / Embedding / Rerank 均以 Protocol 抽象，可插拔接入 Qwen / DeepSeek / ChatGLM / LLaMA 等多种开源或闭源模型。
- **权限**：RBAC 权限模型（10 个预置角色 / 三级权限点 / 五档数据范围），支持新角色零代码快速接入。

详细设计见 [`/design`](./design/README.md)（含系统架构图、后端架构图、前端架构图、MySQL ER 图、Milvus 集合设计、RBAC 模型图）。

## 2. 解决了什么问题

电商客服场景的典型痛点，本项目逐一解决：

| 痛点 | 方案 |
|---|---|
| 重复问题占比高、人力成本大 | RAG 知识库自动应答高频问题，大幅降低人工介入率 |
| 响应不及时、无法 7×24 服务 | 机器人 7×24 实时流式响应，夜间与大促高峰不宕机 |
| 客服回答水平参差、口径不一 | 答案统一来自受审知识库，保证一致性 |
| 知识库更新需重启、生效慢 | **动态更新**：文档新增/更新/下线后异步向量化与索引对账，无需重启服务 |
| 客户问题超出机器人能力时体验割裂 | 未命中/主动请求自动创建工单并流转坐席，支持分配/转派/超时升级 |
| 多团队权限与数据隔离难 | RBAC 三级权限 + 五档数据范围，按角色/部门隔离数据与操作 |

## 3. 可以做到哪些目标

| 目标 | 达成方式 |
|---|---|
| 降低人工客服成本 | 自动应答高频重复问题，显著降低人工介入率与人力投入 |
| 提升响应速度与可用性 | 7×24 秒级流式响应，大促高峰、夜间无人值守仍稳定服务 |
| 保证回答口径一致 | 答案统一来自受审知识库，避免客服回答参差 |
| 加速知识运营迭代 | 文档动态更新（新增/更新/下线）后异步向量化，无需重启服务 |
| 打通问题闭环 | 未命中或主动转人工时自动建单、分配、转派、超时升级，全程可追溯 |
| 强化权限与数据安全 | RBAC 三级权限 + 五档数据范围，按角色/部门隔离数据与操作 |
| 便于运维与治理 | 结构化日志、审计日志、核心指标统计，问题可观测、可追溯 |

## 4. 核心能力

- **智能问答**：知识库命中 → 流式回答（SSE）；支持追问、上下文多轮会话。
- **转人工工单**：未命中 / 客户主动请求 → 自动建单 → 坐席分组分配 → 流转 → 解决，全程可追溯。
- **知识库管理**：文档上传 → 分片 → 向量化 → 审核 → 发布 / 下线，贯穿状态机与版本管理。
- **多模型可插拔**：`LLMProvider` / `EmbeddingProvider` / `RerankProvider` 统一抽象，改配置即可切换模型。
- **RBAC 权限**：三级权限（菜单 / 按钮 / API）+ 五档数据范围（全部 / 本部门 / 本部门及子部门 / 本人 / 自定义），内置系统管理员、运营、客服坐席、AI 工程师、质检等 10 个角色。
- **会话与客服中心**：会话列表、历史消息、满意度评价、快捷回复、坐席状态与并发管理。
- **可观测与审计**：结构化日志、审计日志、登录日志、核心指标统计。

## 5. 工程结构

```
.
├── backend/                 # FastAPI 后端（Python 3.12）
│   ├── app/
│   │   ├── api/v1/          # 接口层（auth/users/roles/kb/chat/tickets/admin）
│   │   ├── core/            # 配置、安全、依赖注入、异常、中间件
│   │   ├── domain/          # 领域层（rbac/chat/kb/ai 实体与策略）
│   │   ├── models/          # SQLAlchemy ORM（29 表）
│   │   ├── repositories/    # 仓储层
│   │   ├── services/        # 应用服务层
│   │   ├── integrations/    # 集成层（LLM/Embedding/Rerank/Milvus/Storage）
│   │   └── workers/         # Celery 异步任务
│   ├── alembic/             # 数据库迁移
│   ├── tests/               # 单元 / 集成测试
│   └── docker-compose.yml   # MySQL/Redis/Milvus/etcd/MinIO/API/Worker/Beat
├── frontend/                # Vue 3 双工程 monorepo
│   ├── apps/customer-chat/  # C 端对话应用
│   ├── apps/admin-console/  # 运营管理后台（Element Plus）
│   └── packages/@auto/{shared,api}  # 共享类型 / API 客户端（axios + SSE + WS）
└── design/                  # 设计文档与架构/ER 图（唯一权威来源）
```

## 6. 快速开始

### 6.1 环境要求

- Python ≥ 3.12、Node ≥ 20、pnpm ≥ 10
- Docker + Docker Compose（用于一键启动依赖中间件）

### 6.2 方式一：Docker Compose 一键启动（推荐）

```bash
cd backend
cp .env.example .env      # 修改 JWT/AES/LLM 等密钥为真实值
docker compose up -d      # 启动 MySQL、Redis、Milvus、etcd、MinIO、API、Worker、Beat
```

启动后：
- API 文档（Swagger）：http://localhost:8000/api/docs
- 健康检查：GET http://localhost:8000/healthz

### 6.3 方式二：本地开发

**① 启动依赖中间件**（仅基础设施）：

```bash
cd backend
docker compose up -d mysql redis etcd minio milvus
```

**② 启动后端**：

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env        # 按需修改数据库/Redis/Milvus/LLM 连接
alembic upgrade head        # 初始化数据库表结构
uvicorn app.main:app --reload --port 8000
```

**③ 启动前端**：

```bash
cd frontend
pnpm install
pnpm dev:customer           # C 端对话应用 → http://localhost:5173
pnpm dev:admin              # 运营管理后台 → http://localhost:5174
```

> 前端开发服务器已代理 `/api` 到 `http://localhost:8000`，跨域无需额外配置。

### 6.4 运行测试与质量检查

```bash
# 后端：单元 + 集成测试
cd backend
pytest

# 后端：静态检查
ruff check app
mypy app

# 前端：类型检查
cd frontend
pnpm -r typecheck

# 前端：生产构建
pnpm --filter @auto/customer-chat build
pnpm --filter @auto/admin-console build
```

## 7. 配置说明

核心环境变量见 [`backend/.env.example`](./backend/.env.example)，主要包括：

- **数据库**：`DB_HOST/DB_PORT/DB_USER/DB_PASSWORD/DB_NAME`
- **Redis**：`REDIS_URL`、`REDIS_CELERY_BROKER/BACKEND`
- **Milvus**：`MILVUS_HOST/MILVUS_PORT`
- **JWT**：`JWT_SECRET_KEY`（生产务必更换）、`JWT_ACCESS_TOKEN_EXPIRE_MINUTES`
- **加密**：`AES_ENCRYPTION_KEY`（用于加密模型 API Key 等敏感字段）
- **模型**：`LLM_DEFAULT_*`、`EMBEDDING_*`、`RERANK_*`（可分别指向不同厂商/本地模型服务）
- **对象存储**：`MINIO_ENDPOINT/ACCESS_KEY/SECRET_KEY/BUCKET`

## 8. 设计文档与更多

架构、数据库、RBAC 的完整设计文档与图表（系统架构图、前后端架构图、MySQL ER 图、Milvus 集合设计、RBAC 模型图）见 [`/design`](./design/README.md)。代码与设计保持一致，架构或原型变更需同步更新 `/design` 目录。