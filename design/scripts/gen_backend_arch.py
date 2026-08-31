# -*- coding: utf-8 -*-
"""生成后端服务架构图（Python + FastAPI 专项）。

内容：技术栈总览、FastAPI 五层架构、工程目录结构、请求生命周期管道、
异步任务与流式响应路径。

同步更新：后端架构变更时修改本脚本后重新执行：
    python3 /workspace/design/scripts/gen_backend_arch.py
"""
import sys

sys.path.insert(0, "/workspace/design/scripts")
from plot_common import setup_font, new_canvas, box, header_box, line_text, arrow, link_label, save, C

setup_font()


def layer(ax, x, y, w, h, title, sub, color, chips, chip_w=None, chip_h=4.6):
    """分层条带：标题 + 芯片组件。chips: [(文本, 说明)]"""
    header_box(ax, x, y, w, h, title, color, fs=10, sub=sub)
    n = len(chips)
    gap = 0.9
    cw = (w - 2.4 - gap * (n - 1)) / n
    cw = min(cw, chip_w or 99)
    for i, (name, desc) in enumerate(chips):
        cx = x + 1.2 + i * (cw + gap)
        box(ax, cx, y + 1.4, cw, h - 7.4, C["white"], C["border"], lw=1.0, r=0.5, z=4)
        ax.text(cx + cw / 2, y + h - 8.2, name, ha="center", va="center",
                fontsize=7.8, fontweight="bold", color=C["ink"], zorder=5)
        if desc:
            ax.text(cx + cw / 2, y + h - 10.8, desc, ha="center", va="center",
                    fontsize=6.2, color=C["ink2"], zorder=5)


def tree(ax, x, y, lines, fs=7.0):
    """等宽目录树。lines: (缩进级, 文本, 是否强调)"""
    for i, (lv, text, strong) in enumerate(lines):
        prefix = "    " * lv + ("├─ " if lv > 0 else "")
        col = C["brand_text"] if strong else C["ink2"]
        weight = "bold" if strong else "normal"
        ax.text(x, y - i * 1.92, prefix + text, fontsize=fs, color=col,
                va="center", ha="left", zorder=5, fontweight=weight)


def main():
    fig, ax = new_canvas(
        32, 18,
        "AutoCustomer · 后端服务架构（Python + FastAPI）",
        "模块化单体 · DDD 分层 · 全异步 (asyncio) · 领域层零框架依赖 · 依赖倒置（Protocol 定义在领域层，实现在基础设施层）",
    )

    # ================================================================ 顶部技术栈
    ts = [
        ("Web 框架", "FastAPI 0.115+"),
        ("数据校验", "Pydantic v2"),
        ("ASGI 服务器", "Uvicorn + Gunicorn"),
        ("ORM / 迁移", "SQLAlchemy 2.0 async · Alembic"),
        ("异步任务", "Celery + Redis"),
        ("向量库", "pymilvus"),
        ("HTTP 客户端", "httpx (LLM/Embedding)"),
        ("认证", "PyJWT · argon2-cffi"),
        ("可观测", "structlog · OTel SDK"),
        ("测试", "pytest · pytest-asyncio"),
    ]
    bw, by = 9.55, 88.5
    for i, (k, v) in enumerate(ts):
        x = 2 + i * (bw + 0.55)
        box(ax, x, by, bw, 6.8, C["brand_soft"], C["brand_soft"], lw=0, r=0.5, z=3, alpha=0.55)
        ax.text(x + bw / 2, by + 4.4, k, ha="center", va="center", fontsize=7,
                color=C["brand_text"], zorder=4, fontweight="bold")
        ax.text(x + bw / 2, by + 1.9, v, ha="center", va="center", fontsize=6.6,
                color=C["ink2"], zorder=4)

    # ================================================================ 左侧：五层架构
    lx, lw_ = 2, 55
    layers = [
        ("L1 · 接入层 (Interface)", "中间件链 + 协议适配", C["ink2"], [
            ("中间件链", "RequestID·CORS·限流·访问日志"),
            ("REST APIRouter", "api/v1/* 按域分组"),
            ("WebSocket", "/ws/chat 双向对话"),
            ("SSE", "/chat/stream 流式输出"),
            ("异常处理器", "统一错误码响应"),
        ]),
        ("L2 · 应用服务层 (Application)", "用例编排 + 事务边界", "#22A5F7", [
            ("ChatService", "对话编排·上下文·转人工"),
            ("KBService", "文档·切片·索引任务"),
            ("RBACService", "用户·角色·权限·数据范围"),
            ("TicketService", "工单分配·流转·超时升级"),
            ("ReportService", "统计聚合·报表导出"),
        ]),
        ("L3 · 领域层 (Domain · 纯 Python)", "业务规则 · 零外部依赖", C["brand"], [
            ("chat 聚合", "Session/Message/转人工策略"),
            ("kb 聚合", "Document/Chunk/切片策略"),
            ("rbac 聚合", "User/Role/Perm/判定"),
            ("ai 聚合", "Prompt组装/阈值判定"),
            ("Protocol 接口", "Repo/LLM/Embed 抽象"),
        ]),
        ("L4 · 基础设施层 (Infrastructure)", "Protocol 实现者", "#16A34A", [
            ("MySQL Repos", "SQLAlchemy 2.0 async"),
            ("Milvus Gateway", "pymilvus 检索/写入"),
            ("LLM Providers", "Qwen/LLaMA/GLM 适配"),
            ("Embedding", "BGE/m3e 适配"),
            ("Redis / OSS", "缓存·会话·对象存储"),
        ]),
        ("L5 · 异步与任务 (Workers)", "Celery Beat + Worker", "#D97706", [
            ("kb_pipeline", "解析→切片→向量化"),
            ("index_sync", "Milvus upsert/对账"),
            ("stat_rollup", "日统计聚合"),
            ("ticket_timeout", "工单超时升级"),
            ("retry/DLQ", "失败重试·死信"),
        ]),
    ]
    y = 84
    for title, sub, color, chips in layers:
        h = 13.6
        layer(ax, lx, y - h, lw_, h, title, sub, color, chips)
        y -= h + 1.6

    # 层间依赖箭头
    for i in range(len(layers) - 1):
        yy = 84 - (i + 1) * 13.6 - i * 1.6 + 0.8
        arrow(ax, (lx + lw_ / 2, yy + 0.9), (lx + lw_ / 2, yy - 0.7),
              color=C["ink3"], lw=1.4, style="-|>", ms=11, z=6)
    ax.text(lx + lw_ / 2, 84 - 4 * 15.2 - 2.6, "依赖方向：上层依赖下层抽象接口（Protocol），实现由 DI 容器注入",
            ha="center", fontsize=7.2, color=C["ink2"], zorder=5)

    # ================================================================ 右上：工程目录
    rx, rw = 59, 39
    box(ax, rx, 47.5, rw, 43, C["bg"], C["border"], lw=1.0, r=0.8, z=2)
    ax.text(rx + 1.4, 88.4, "工程目录结构（monorepo: backend/）", fontsize=10,
            fontweight="bold", color=C["ink"], zorder=5)
    tlines = [
        (0, "backend/", True),
        (0, "├─ app/", False),
        (1, "main.py            # FastAPI 工厂 + lifespan", True),
        (1, "core/             # config(Pydantic Settings)·security·deps·middleware·exceptions", False),
        (1, "api/v1/           # 路由: auth·users·roles·perms·chat·kb·tickets·reports·admin", False),
        (1, "schemas/          # Pydantic v2 DTO（请求/响应模型）", False),
        (1, "services/         # 应用服务（UseCase 编排，事务边界）", True),
        (1, "domain/           # 领域模型+策略+Protocol（纯 Python，无框架 import）", True),
        (1, "repositories/     # SQLAlchemy async 仓储实现", False),
        (1, "models/           # ORM 表模型（与 /design ER 图对齐）", False),
        (1, "integrations/     # llm/·embedding/·milvus/·storage/ 外部适配器", False),
        (1, "workers/          # Celery 任务定义", False),
        (1, "utils/            # 通用工具（分页·加密·脱敏）", False),
        (0, "├─ alembic/            # 数据库迁移版本", False),
        (0, "├─ tests/              # unit/·integration/·e2e/·golden/(AI 黄金集)", False),
        (0, "├─ pyproject.toml      # uv/pdm 依赖管理 + ruff + mypy", False),
        (0, "└─ Dockerfile · docker-compose.yml · .env.example", False),
    ]
    tree(ax, rx + 1.6, 85.2, tlines, fs=6.7)

    # ================================================================ 右下：请求生命周期
    box(ax, rx, 4, rw, 40.5, C["bg"], C["border"], lw=1.0, r=0.8, z=2)
    ax.text(rx + 1.4, 42.6, "请求生命周期（对话流式场景）", fontsize=10,
            fontweight="bold", color=C["ink"], zorder=5)
    steps = [
        ("① WS/SSE 连接", "网关 → Uvicorn", C["ink2"]),
        ("② 中间件链", "RequestID → 限流 → JWT/ticket 鉴权", C["ink2"]),
        ("③ 依赖注入", "get_db·get_current_user·require_perm", "#22A5F7"),
        ("④ ChatService", "上下文组装 + Query 改写", "#22A5F7"),
        ("⑤ 领域策略", "阈值判定·命中/未命中分支", C["brand"]),
        ("⑥ Milvus 检索", "topK=20 → rerank → topN=5", "#16A34A"),
        ("⑦ LLM 流式", "httpx async stream", C["brand"]),
        ("⑧ SSE 增量推送", "yield token → 前端打字机", C["brand"]),
    ]
    sy = 38.6
    for i, (t, d, col) in enumerate(steps):
        yy = sy - i * 4.3
        box(ax, rx + 1.6, yy - 3.4, rw - 3.2, 3.8, C["white"], col, lw=1.2, r=0.4, z=4)
        ax.text(rx + 3.0, yy - 1.5, t, fontsize=7.4, fontweight="bold",
                color=C["ink"], va="center", zorder=5)
        ax.text(rx + rw - 3.0, yy - 1.5, d, fontsize=6.4, color=col,
                va="center", ha="right", zorder=5)
        if i < len(steps) - 1:
            arrow(ax, (rx + rw / 2, yy - 3.5), (rx + rw / 2, yy - 4.2),
                  color=C["ink3"], lw=1.2, style="-|>", ms=9, z=5)

    save(fig, "/workspace/design/01-architecture/backend-architecture.png", dpi=150)


if __name__ == "__main__":
    main()
