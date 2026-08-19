# 后端服务架构设计（Python · FastAPI）

> 配套图表：[backend-architecture.png](./backend-architecture.png) · 总览见 [system-architecture.png](./system-architecture.png)
>
> 本文档是后端的**唯一权威架构设计来源**。架构变更必须先更新本文档与架构图，再落代码（同步 SOP 见 `/design/README.md`）。

## 1. 技术选型（锁定）

| 分类 | 选型 | 版本基线 | 选型理由 |
|---|---|---|---|
| Web 框架 | **FastAPI** | 0.115+ | 原生 async、Pydantic 集成、自动 OpenAPI 文档、DI 系统 |
| 数据校验 | Pydantic | v2 | 性能好（Rust core）、`model_config` 严格模式 |
| ASGI 服务器 | Uvicorn（Gunicorn 管理多 worker） | 1.30+ | 标准 ASGI，支持 HTTP/WS/SSE |
| ORM | SQLAlchemy 2.0（async + AsyncMy） | 2.0 | `Mapped[]` 声明式、异步引擎、连接池 |
| 迁移 | Alembic | 1.13+ | 表结构与种子数据版本化 |
| 异步任务 | Celery 5 + Redis（broker/backend） | 5.3+ | 向量化/统计/超时扫描等离线流水线 |
| 向量库 | pymilvus | 2.4+ | Milvus SDK |
| HTTP 客户端 | httpx（AsyncClient） | 0.27+ | 调 LLM/Embedding/Rerank，支持流式 |
| 认证 | PyJWT + passlib[argon2] | | JWT 双 Token + argon2id 密码哈希 |
| 日志 | structlog | | 结构化 JSON，request_id 贯穿 |
| 追踪/指标 | OpenTelemetry SDK + Prometheus | | OTLP 导出 |
| 测试 | pytest + pytest-asyncio + httpx | | 单测/集成/E2E 分层 |
| 代码质量 | ruff + mypy（strict 对 domain/） | | lint + 类型检查 |

**依赖管理**：`pyproject.toml` + uv（或 pdm），锁文件提交仓库。

## 2. 分层架构与依赖规则

```
L1 接入层 (api/)        → FastAPI 路由、WS/SSE 端点、中间件、异常处理器
L2 应用服务层 (services/) → UseCase 编排、事务边界、DTO 转换
L3 领域层 (domain/)      → 纯 Python：实体、值对象、策略、Protocol 接口
L4 基础设施层 (repositories/ + integrations/) → Protocol 的实现：MySQL/Milvus/LLM/Embedding
L5 异步任务 (workers/)   → Celery 任务，只调 L2 服务，不直接摸 L4
```

**铁律**：

1. **依赖方向只能向下**，且 L2/L3 只依赖 L3 定义的 `Protocol`，不 import 任何框架类型（L3 目录 `import fastapi` 直接 CI 报错）。
2. L3 领域层**零外部依赖**（无 SQLAlchemy/Pydantic/FastAPI import），保证可独立高速单测——这是可测试性的根基。
3. Protocol 定义在 `domain/`（如 `domain/ai/protocols.py` 的 `LLMProvider`），实现在 `integrations/`，由 `core/deps.py` 的 DI 容器装配。
4. 事务边界在 L2：Service 方法内 `async with session.begin()`，Repository 不自管事务。
5. L5 Worker 只通过调用 L2 Service 复用业务逻辑，禁止绕过直接操作 ORM。

## 3. 工程目录结构

```
backend/
├─ app/
│  ├─ main.py                  # create_app() 工厂 + lifespan（连接池/缓存/OTel 初始化）
│  ├─ core/
│  │  ├─ config.py            # Pydantic BaseSettings，.env 加载，分组嵌套
│  │  ├─ security.py          # JWT 签发/校验、argon2 哈希、AES-GCM 加解密
│  │  ├─ deps.py              # DI: get_db / get_current_user / require_permission / get_services
│  │  ├─ middleware.py        # RequestID → 访问日志 → 限流 → CORS
│  │  └─ exceptions.py        # 业务异常体系 + 全局异常处理器 → 统一错误响应
│  ├─ api/
│  │  ├─ deps.py              # 路由层公共依赖（分页、排序白名单）
│  │  └─ v1/
│  │     ├─ auth.py           # 登录/刷新/登出/2FA
│  │     ├─ users.py  roles.py  permissions.py  menus.py  depts.py
│  │     ├─ chat.py           # REST 会话管理
│  │     ├─ chat_stream.py    # SSE 流式对话 + WebSocket 端点
│  │     ├─ kb.py             # 分类/文档/分片/导入任务
│  │     ├─ tickets.py        # 工单分配/回复/流转
│  │     ├─ reports.py        # 统计看板/导出
│  │     └─ admin.py          # 模型配置/Prompt/检索配置/审计日志
│  ├─ schemas/                # Pydantic v2 DTO（Request/Response，OpenAPI 文档源）
│  ├─ services/               # L2 应用服务（每个域一个 Service 类）
│  │  ├─ chat_service.py  kb_service.py  rbac_service.py
│  │  ├─ ticket_service.py  report_service.py  rag_service.py
│  ├─ domain/                 # L3 领域层（纯 Python，CI 强制无框架 import）
│  │  ├─ chat/                # Session/Message 实体、TransferPolicy、RatingPolicy
│  │  ├─ kb/                  # Document/Chunk、ChunkingStrategy
│  │  ├─ rbac/                # PermissionSet（并集/范围计算）、数据范围过滤规则
│  │  └─ ai/                  # PromptRenderer、HitThresholdPolicy、protocols.py
│  ├─ repositories/           # L4：SQLAlchemy async 仓储（每聚合一个）
│  ├─ models/                 # SQLAlchemy ORM 表模型（与 02-database ER 图逐表对齐）
│  ├─ integrations/
│  │  ├─ llm/                 # base.py(实现 domain Protocol) + qwen/llama/chatglm/deepseek/openai_compat/mock
│  │  ├─ embedding/           # bge_m3.py / m3e.py / text2vec.py + factory
│  │  ├─ rerank/              # bge_reranker.py
│  │  ├─ milvus/              # MilvusGateway（检索/upsert/delete/对账/alias 切换）
│  │  └─ storage/             # MinIO 客户端
│  ├─ workers/                # Celery: kb_pipeline / index_sync / stat_rollup / ticket_timeout
│  └─ utils/                  # 分页、脱敏、雪花 ID（预留）
├─ alembic/versions/          # 表结构 + 种子数据迁移
├─ tests/
│  ├─ unit/                   # domain 纯逻辑（无 IO）
│  ├─ integration/            # TestClient + testcontainers(MySQL/Redis/Milvus)
│  ├─ e2e/                    # 关键链路
│  └─ golden/                 # AI 黄金集（200+ 问答对，Recall@K/相似度/拒答率）
├─ pyproject.toml  Dockerfile  docker-compose.yml  .env.example
```

## 4. 核心设计决策

### 4.1 依赖注入（FastAPI Depends 链）

```python
# 路由只声明"要什么"，不关心实现来自哪里
@router.post("/documents/{doc_id}/publish")
async def publish_document(
    doc_id: int,
    svc: KBService = Depends(get_kb_service),          # Service 已装配好 Repo/事件
    user: CurrentUser = Depends(require_permission("kb:doc:publish")),  # 鉴权+RBAC 一步完成
):
    ...
```

- `require_permission(code)`：校验 JWT → 加载用户角色并集权限集（Redis 缓存，变更失效）→ 拒绝则 403。
- 数据范围（SELF/DEPT/...）在 Repository 层由 `rbac/domain` 的过滤器统一注入，Service 不感知。

### 4.2 流式对话（SSE 为主，WS 备用）

- **SSE** `GET /api/v1/chat/stream`：`StreamingResponse`，httpx 异步迭代 LLM token → `yield f"data: {json}\n\n"`，前端打字机效果；断线用 `Last-Event-ID` 续传（Redis 暂存最近 N 条）。
- **WebSocket** `/api/v1/ws/chat`：需要客户端上行打断/心跳的场景；消息信封 `{type, seq, payload}`。
- LLM 调用超时 30s 熔断，失败自动降级备用 Provider，再失败回兜底模板 + 转人工卡片。

### 4.3 RAG 编排（rag_service.py，可被 chat/搜索复用）

```
query → 查询改写(LLM，可选) → Milvus topK=20(cosine, filter status=published)
      → BGE-Reranker 精排 topN=5 → 最高分 ≥ kb_retrieval_config.score_threshold ?
      ├─ 命中：PromptRenderer(sys_prompt_template.scene=chat_hit) → LLM 流式生成
      └─ 未命中：兜底模板 + TransferPolicy 判定 → human_ticket
全程写 chat_retrieval_log（含 topk_scores），供黄金集回归与未命中问题分析。
```

### 4.4 异常与错误码

- 领域层抛 `DomainError(code, message)`；全局 exception_handler 统一转 `{code, message, request_id, detail?}`。
- 错误码段：`1xxx` 通用 / `2xxx` 认证权限 / `3xxx` 知识库 / `4xxx` 对话 / `5xxx` 工单 / `6xxx` 模型服务。
- 5xx 不泄露堆栈，堆栈进日志（带 request_id 关联）。

### 4.5 配置管理（core/config.py）

- Pydantic `BaseSettings` 分组：`DB` / `REDIS` / `MILVUS` / `LLM` / `SECURITY` / `OTEL`。
- `.env.example` 提交仓库，真实密钥仅 ENV/KMS 注入；`api_key` 落库前 AES-GCM 加密。

### 4.6 权限缓存

- 用户权限集（角色并集后的 perm_code set + data_scope）缓存 Redis `TTL 10min`；角色/绑定变更时主动 delete 对应用户 key → ⑤ 即时生效（支撑 RBAC 零代码接入新角色）。

## 5. API 设计规范

| 规范 | 约定 |
|---|---|
| 路径 | `/api/v1/<模块>/<资源>`，资源复数；动作用子资源 `POST /documents/{id}/publish` |
| 方法语义 | GET 无副作用；POST 创建；PUT 全量；PATCH 部分变更 |
| 响应包裹 | 成功 `{"code":0, "data":..., "request_id":...}`；列表 `{items, total, page, page_size}` |
| 分页 | `?page=1&page_size=20`（上限 100），排序字段白名单校验 |
| 幂等 | 写接口支持 `Idempotency-Key` 头（Redis 去重 5min） |
| 版本 | URL 版本 `v1`；不兼容变更升 `v2`，`v1` 至少保留 2 个迭代 |

## 6. 测试策略（与代码同仓）

| 层 | 工具 | 覆盖目标 | 门禁 |
|---|---|---|---|
| 单元（domain/） | pytest | 策略/纯函数：转人工策略、切片、权限并集、阈值判定 | 行覆盖 ≥ 90% |
| 集成 | pytest-asyncio + httpx AsyncClient + testcontainers | API+DB+Milvus+Redis，LLM 用 MockProvider | ≥ 70% |
| E2E | httpx + docker-compose | 登录→建知识→提问→转人工 全链路 | 关键路径全过 |
| AI 黄金集 | pytest + 评测脚本 | Recall@5 ≥ 0.85、答案相似度 ≥ 0.8、拒答准确率 ≥ 0.95 | 回归不过禁止合并 |

## 7. 部署形态

- **开发**：`docker-compose up`（api/worker/mysql/redis/milvus/minio 一把起）。
- **生产**：K8s Deployment（api 多副本 HPA 按 CPU/QPS）+ Worker 独立 Deployment + Alembic Job（init container）。
- 健康检查：`/healthz`（存活）`/readyz`（DB/Redis/Milvus 连通）。
- CI 流水线：ruff+mypy → pytest（含黄金集）→ 构建镜像 → 灰度 10%/50%/100%。

## 8. 变更记录

| 日期 | 变更 |
|---|---|
| 2026-08-19 | 初版：确定 Python + FastAPI 技术栈、五层架构、目录结构、SSE 流式与 RAG 编排方案 |
