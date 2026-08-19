# AutoCustomer 设计文档中心（/design）

> 本目录是 AutoCustomer（电商智能客服机器人）的**唯一权威设计与原型来源**：系统架构、前后端架构、数据库原型、RBAC 权限体系。
>
> 所有图片由 `/design/scripts/` 下的 Python 脚本生成（matplotlib + 内置中文字体），**图与文档可再生成、可版本化**。

## 1. 文档与图表索引

| 主题 | 说明文档 | 设计图 |
|---|---|---|
| 系统总览 | —（见各分册） | [01-architecture/system-architecture.png](./01-architecture/system-architecture.png) |
| 后端架构（Python · FastAPI） | [01-architecture/backend.md](./01-architecture/backend.md) | [01-architecture/backend-architecture.png](./01-architecture/backend-architecture.png) |
| 前端架构（Vue 3 双工程） | [01-architecture/frontend.md](./01-architecture/frontend.md) | [01-architecture/frontend-architecture.png](./01-architecture/frontend-architecture.png) |
| 数据库原型（MySQL 29 表 + Milvus） | [02-database/README.md](./02-database/README.md) | [02-database/er-diagram-mysql.png](./02-database/er-diagram-mysql.png) · [02-database/milvus-collections.png](./02-database/milvus-collections.png) |
| RBAC 权限体系 | [03-rbac/README.md](./03-rbac/README.md) | [03-rbac/rbac-model.png](./03-rbac/rbac-model.png) |

## 2. 目录结构

```
design/
├── README.md                  # 本文件：索引 + 变更同步 SOP
├── 01-architecture/           # 架构设计（图 + md）
├── 02-database/               # 数据库原型（ER 图 + Milvus 图 + md）
├── 03-rbac/                   # RBAC 权限体系（图 + md）
├── assets/fonts/              # 中文字体（Noto Sans SC，图片生成依赖）
└── scripts/                   # 设计图生成脚本（图的可再生来源）
    ├── plot_common.py         # 公共绘图模块（字体/色板/工具）
    ├── gen_er_diagram.py      # MySQL ER 图
    ├── gen_milvus_diagram.py  # Milvus 集合设计图
    ├── gen_backend_arch.py    # 后端 FastAPI 架构图
    ├── gen_system_frontend.py # 系统总览图 + 前端架构图
    └── gen_rbac_diagram.py    # RBAC 模型图
```

## 3. 设计变更同步 SOP（强制）

**原则：先改设计，再改代码。** 代码编写与修改过程中，凡涉及以下内容，必须同步更新本目录：

### 3.1 触发同步的变更类型

| 变更类型 | 必须更新 |
|---|---|
| 新增/删除/修改 MySQL 表、字段、索引 | `02-database/README.md` 对应表定义 + `scripts/gen_er_diagram.py`（TABLES/LAYOUT/RELATIONS） |
| Milvus 集合 Schema/索引/分区/阈值变更 | `02-database/README.md` 第 9 节 + `scripts/gen_milvus_diagram.py` |
| 后端分层/目录结构/技术选型/核心流程变更 | `01-architecture/backend.md` + `scripts/gen_backend_arch.py` |
| 前端工程结构/协议约定变更 | `01-architecture/frontend.md` + `scripts/gen_system_frontend.py` |
| 新增角色/权限点/数据范围变更 | `03-rbac/README.md` + `scripts/gen_rbac_diagram.py` |
| 整体拓扑（新增服务/中间件）变更 | `scripts/gen_system_frontend.py` 的 gen_system() |

### 3.2 操作步骤

1. **改脚本**：修改 `/design/scripts/` 下对应 `gen_*.py`（数据即代码，布局参数随内容调整）。
2. **重新生成图片**：
   ```bash
   cd /design/scripts
   python3 gen_er_diagram.py        # ER 图
   python3 gen_milvus_diagram.py    # Milvus 图
   python3 gen_backend_arch.py      # 后端架构图
   python3 gen_system_frontend.py   # 系统总览 + 前端架构图
   python3 gen_rbac_diagram.py      # RBAC 模型图
   # 依赖：pip install matplotlib pillow（字体已内置 assets/fonts）
   ```
3. **更新文档**：同步修改对应 README.md 的表格/说明，并在文末「变更记录」追加一行（日期 + 变更摘要）。
4. **提交**：设计与代码**同一 commit 或关联 commit** 提交，commit message 中标注 `[design-update]` 前缀，便于追溯。
5. **数据库变更**：表结构变更必须在 Alembic 迁移落地，且迁移顺序与文档变更记录一致。

### 3.3 一致性检查（CI 可选接入）

- `scripts/` 内脚本可重复执行且幂等（重新生成覆盖同名 PNG）；
- 表结构以 `02-database/README.md` 为准，ORM 模型（`app/models/`）与 ER 图 TABLES 清单做 CI diff 校验（表名集合一致性）；
- 权限码以 `03-rbac/README.md` 第 3 节清单为准，与 Alembic 种子迁移对齐。

## 4. 设计基线摘要（v1 · 2026-08-19）

| 维度 | 基线 |
|---|---|
| 架构形态 | 前后端分离 · 后端模块化单体（DDD 五层）· 未来可按域拆微服务 |
| 后端 | **Python 3.12 + FastAPI** · SQLAlchemy 2.0 async · Celery · pymilvus · httpx |
| 前端 | Vue 3 + Vite 5 + TS strict · 双工程 monorepo（customer-chat / admin-console） |
| 数据 | MySQL 8.0（29 表 / 6 域）+ Milvus（HNSW/COSINE，chunk_id 与 MySQL 1:1）+ Redis + MinIO |
| AI | RAG（向量检索 topK=20 → Rerank topN=5 → 阈值 0.78）· LLM/Embedding Provider 全 Protocol 抽象（Qwen/LLaMA/ChatGLM/DeepSeek 可插拔） |
| RBAC | 10 预置角色 / 4 分组 · 权限点三级（menu/btn/api）· 数据范围五档 · 新角色零代码接入 |
| 核心体验 | 知识库命中 → 流式回答（SSE）；未命中/主动 → 转人工工单（坐席分配/流转/超时升级） |

## 5. 变更记录（总）

| 日期 | 变更 | 影响文档 |
|---|---|---|
| 2026-08-19 | v1 初版：FastAPI 后端架构、MySQL 29 表 ER + Milvus 双集合、丰富 RBAC（10 角色）设计全部落盘 | 全部 |
