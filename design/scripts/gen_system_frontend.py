# -*- coding: utf-8 -*-
"""生成系统总览架构图 + 前端架构图（Vue 3 双工程）。

同步更新：架构变更时修改本脚本后重新执行：
    python3 /workspace/design/scripts/gen_system_frontend.py
"""
import sys

sys.path.insert(0, "/workspace/design/scripts")
from plot_common import setup_font, new_canvas, box, header_box, line_text, arrow, link_label, save, C

setup_font()


def chip(ax, x, y, w, h, title, sub, color, fs=8.2, sub_fs=6.6):
    """通用小卡片。"""
    box(ax, x, y, w, h, C["white"], color, lw=1.4, r=0.55, z=3)
    if sub:
        ax.text(x + w / 2, y + h * 0.66, title, ha="center", va="center",
                fontsize=fs, fontweight="bold", color=C["ink"], zorder=5)
        ax.text(x + w / 2, y + h * 0.28, sub, ha="center", va="center",
                fontsize=sub_fs, color=C["ink2"], zorder=5)
    else:
        ax.text(x + w / 2, y + h / 2, title, ha="center", va="center",
                fontsize=fs, fontweight="bold", color=C["ink"], zorder=5)


def gen_system():
    fig, ax = new_canvas(
        30, 17.5,
        "AutoCustomer · 系统总览架构（前后端分离）",
        "Vue 3 前端双工程 + FastAPI 后端（Python）+ RAG/Milvus + 多开源大模型 · Nginx 统一入口 · Redis 缓存/队列 · MinIO 对象存储",
    )

    # L1 用户层
    chip(ax, 6, 90, 36, 6.5, "电商客户", "Web / H5 / 小程序 · 聊天窗口", C["ink2"])
    chip(ax, 58, 90, 36, 6.5, "运营 / 管理员 / 客服", "PC 管理后台 · 坐席工作台", C["ink2"])

    # L2 前端层
    chip(ax, 6, 79, 36, 7.5, "customer-chat（C 端）", "Vite · Pinia · Vue Router · SSE/WS", C["blue"])
    chip(ax, 58, 79, 36, 7.5, "admin-console（运营后台）", "Element Plus · v-perm 指令 · ECharts", C["blue"])
    ax.text(50, 82.7, "pnpm\nmonorepo", ha="center", va="center", fontsize=6.8,
            color=C["blue"], zorder=5)

    arrow(ax, (24, 90), (24, 86.6), style="-|>", ms=11, color=C["ink3"])
    arrow(ax, (76, 90), (76, 86.6), style="-|>", ms=11, color=C["ink3"])

    # L3 网关
    chip(ax, 26, 69.5, 48, 6.5, "Nginx · 统一入口", "TLS 终止 · 静态资源/CDN · 反向代理 · 负载均衡 · 限流", C["ink2"], fs=9)
    arrow(ax, (24, 79), (35, 76.2), style="-|>", ms=11, color=C["ink3"])
    arrow(ax, (76, 79), (65, 76.2), style="-|>", ms=11, color=C["ink3"])

    # L4 后端 FastAPI（核心）
    header_box(ax, 8, 52, 84, 15.5, "FastAPI 后端（Python · 模块化单体 · 全异步）", C["brand"], fs=10.5)
    mods = [
        ("用户/权限服务", "RBAC·JWT·审计"),
        ("对话引擎服务", "会话·上下文·转人工"),
        ("知识库服务", "文档·切片·RAG 编排"),
        ("工单坐席服务", "分配·流转·超时"),
        ("统计报表服务", "看板·导出"),
    ]
    mw = 15.2
    for i, (t, s) in enumerate(mods):
        chip(ax, 10 + i * (mw + 1.0), 53.5, mw, 6.2, t, s, C["brand"], fs=7.6, sub_fs=6.2)
    arrow(ax, (50, 69.5), (50, 67.7), style="-|>", ms=11, color=C["ink3"])

    # L5 AI 适配层
    header_box(ax, 8, 36, 84, 13.5, "AI 适配层（Strategy + Factory · 全部 Protocol 抽象）", C["brand_dark"], fs=10.5)
    aims = [
        ("RAG 检索编排", "向量检索+Rerank+阈值判定"),
        ("LLM Providers", "Qwen/LLaMA/GLM/DeepSeek"),
        ("Embedding", "BGE-m3/m3e/text2vec"),
        ("Prompt 引擎", "模板管理+变量注入"),
        ("Celery Workers", "切片/向量化/统计"),
    ]
    for i, (t, s) in enumerate(aims):
        chip(ax, 10 + i * (mw + 1.0), 37.5, mw, 6.2, t, s, C["brand_dark"], fs=7.6, sub_fs=6.2)
    arrow(ax, (50, 52), (50, 49.7), style="-|>", ms=11, color=C["ink3"])

    # L6 数据层
    stores = [
        ("MySQL 8.0", "业务数据 · 29 表", "#16A34A"),
        ("Milvus", "向量检索 · HNSW", "#16A34A"),
        ("Redis", "缓存 · Celery Broker", "#16A34A"),
        ("MinIO / OSS", "原始文档存储", "#16A34A"),
        ("vLLM / Ollama", "自托管开源模型 GPU", "#D97706"),
    ]
    for i, (t, s, col) in enumerate(stores):
        chip(ax, 10 + i * (mw + 1.0), 24, mw, 6.8, t, s, col, fs=8, sub_fs=6.4)
    for i in range(5):
        x = 10 + i * (mw + 1.0) + mw / 2
        arrow(ax, (x if 0 < i < 4 else 30 if i == 0 else 80, 36),
              (x, 30.9), style="-|>", ms=10, color=C["ink3"],
              connstyle="arc3,rad=0" if 0 < i < 4 else "arc3,rad=0.15")

    # 底部横切
    box(ax, 8, 11, 84, 9.5, C["bg"], C["border"], lw=1.0, r=0.7, z=2)
    ax.text(50, 18.2, "横切关注点", ha="center", fontsize=8.6, fontweight="bold",
            color=C["ink"], zorder=5)
    cross = ["OpenTelemetry 全链路追踪", "structlog 结构化日志", "Prometheus 指标",
             "Alembic 迁移", "Feature Flag 灰度", "Docker/K8s 部署"]
    for i, t in enumerate(cross):
        ax.text(12 + i * 13.6, 14.2, "· " + t, fontsize=6.9, color=C["ink2"],
                va="center", zorder=5)

    save(fig, "/workspace/design/01-architecture/system-architecture.png", dpi=150)


def gen_frontend():
    fig, ax = new_canvas(
        30, 15.5,
        "AutoCustomer · 前端架构（Vue 3 双工程 Monorepo）",
        "pnpm workspace · Vite 5 · TypeScript 严格模式 · 共享 @auto/api（API 客户端）与 @auto/ui（通用组件）",
    )

    # 顶部共享层
    box(ax, 2, 87, 96, 8.5, C["brand_soft"], C["brand"], lw=1.4, r=0.8, z=3)
    ax.text(50, 93.4, "Monorepo 共享层 · packages/", fontsize=9.5, fontweight="bold",
            color=C["brand_text"], zorder=5)
    ax.text(50, 89.6, "@auto/api（OpenAPI 生成的 API 客户端 + WS/SSE 封装） · @auto/ui（通用组件） · @auto/shared（类型/工具/常量）",
            fontsize=7.2, color=C["brand_text"], zorder=5, ha="center")

    # 左：customer-chat
    header_box(ax, 2, 42, 46, 42, "customer-chat · C 端对话应用", C["blue"], fs=10)
    # pages
    box(ax, 3.6, 70, 42.8, 11.5, C["bg"], C["border"], lw=0.9, r=0.5, z=3)
    ax.text(4.8, 79.6, "views/ 页面", fontsize=8, fontweight="bold", color=C["ink"], zorder=5)
    pages1 = ["聊天页 Chat", "会话列表 History", "订单联查 Order", "常见问题 FAQ", "人工转接 Transfer", "评价 Rating"]
    for i, p in enumerate(pages1):
        ax.text(4.8 + (i % 3) * 14.2, 76.6 - (i // 3) * 3.4, p, fontsize=6.8,
                color=C["ink2"], va="center", zorder=5)
    # components
    box(ax, 3.6, 56.5, 42.8, 12, C["bg"], C["border"], lw=0.9, r=0.5, z=3)
    ax.text(4.8, 66.2, "components/ 业务组件", fontsize=8, fontweight="bold", color=C["ink"], zorder=5)
    comps1 = ["ChatBox 对话框", "MessageBubble 气泡", "StreamingTyping 打字机",
              "QuickReply 快捷指令", "TransferCard 转人工卡片", "RatingPanel 评价",
              "Uploader 附件", "OrderCard 订单卡片"]
    for i, p in enumerate(comps1):
        ax.text(4.8 + (i % 2) * 21.2, 63.4 - (i // 2) * 3.2, p, fontsize=6.8,
                color=C["ink2"], va="center", zorder=5)
    # store/api
    box(ax, 3.6, 43.4, 20.8, 11.5, C["bg"], C["border"], lw=0.9, r=0.5, z=3)
    ax.text(14, 52.6, "stores/ (Pinia)", fontsize=7.6, fontweight="bold",
            color=C["ink"], zorder=5, ha="center")
    for i, s in enumerate(["auth.user", "chat.session", "chat.messages", "faq.quickReplies"]):
        ax.text(14, 50.0 - i * 2.4, s, fontsize=6.4, color=C["ink2"],
                va="center", zorder=5, ha="center")
    box(ax, 25.6, 43.4, 20.8, 11.5, C["bg"], C["border"], lw=0.9, r=0.5, z=3)
    ax.text(36, 52.6, "composables/", fontsize=7.6, fontweight="bold",
            color=C["ink"], zorder=5, ha="center")
    for i, s in enumerate(["useSSE 流式订阅", "useWebSocket", "useChatScroll", "useTransfer"]):
        ax.text(36, 50.0 - i * 2.4, s, fontsize=6.4, color=C["ink2"],
                va="center", zorder=5, ha="center")

    # 右：admin-console
    header_box(ax, 52, 42, 46, 42, "admin-console · 运营管理后台（Element Plus）", C["blue"], fs=10)
    box(ax, 53.6, 70, 42.8, 11.5, C["bg"], C["border"], lw=0.9, r=0.5, z=3)
    ax.text(54.8, 79.6, "views/ 页面", fontsize=8, fontweight="bold", color=C["ink"], zorder=5)
    pages2 = ["仪表盘 Dashboard", "知识库 Knowledge", "对话记录 Sessions", "工单中心 Tickets",
              "用户角色 RBAC", "模型配置 Models", "报表 Reports", "审计日志 Audit"]
    for i, p in enumerate(pages2):
        ax.text(54.8 + (i % 4) * 10.6, 76.6 - (i // 4) * 3.4, p, fontsize=6.5,
                color=C["ink2"], va="center", zorder=5)
    box(ax, 53.6, 56.5, 42.8, 12, C["bg"], C["border"], lw=0.9, r=0.5, z=3)
    ax.text(54.8, 66.2, "components/ 业务组件", fontsize=8, fontweight="bold", color=C["ink"], zorder=5)
    comps2 = ["DocEditor 文档编辑器", "ChunkPreview 分片预览", "PermTree 权限树",
              "RoleMatrix 角色矩阵", "SessionViewer 会话回放", "ModelPicker 模型选择",
              "ChartCard 图表卡", "AgentBoard 坐席看板"]
    for i, p in enumerate(comps2):
        ax.text(54.8 + (i % 2) * 21.2, 63.4 - (i // 2) * 3.2, p, fontsize=6.8,
                color=C["ink2"], va="center", zorder=5)
    box(ax, 53.6, 43.4, 20.8, 11.5, C["bg"], C["border"], lw=0.9, r=0.5, z=3)
    ax.text(64, 52.6, "stores/ (Pinia)", fontsize=7.6, fontweight="bold",
            color=C["ink"], zorder=5, ha="center")
    for i, s in enumerate(["auth.user/perms", "app.menus", "kb.documents", "rbac.roles"]):
        ax.text(64, 50.0 - i * 2.4, s, fontsize=6.4, color=C["ink2"],
                va="center", zorder=5, ha="center")
    box(ax, 75.6, 43.4, 20.8, 11.5, C["bg"], C["border"], lw=0.9, r=0.5, z=3)
    ax.text(86, 52.6, "权限控制", fontsize=7.6, fontweight="bold",
            color=C["ink"], zorder=5, ha="center")
    for i, s in enumerate(["v-perm 按钮级指令", "路由守卫菜单级", "axios 401 拦截", "数据范围过滤"]):
        ax.text(86, 50.0 - i * 2.4, s, fontsize=6.4, color=C["ink2"],
                va="center", zorder=5, ha="center")

    # 底部脚手架
    box(ax, 2, 12, 96, 26, C["bg"], C["border"], lw=1.0, r=0.8, z=2)
    ax.text(50, 35.2, "工程脚手架与规范", fontsize=9.5, fontweight="bold",
            color=C["ink"], zorder=5, ha="center")
    cols = [
        ("构建与工具", ["Vite 5 构建", "TypeScript strict", "ESLint + Prettier", "Stylelint"]),
        ("状态与路由", ["Pinia 持久化", "Vue Router 4 动态路由", "按权限生成菜单", "keep-alive 会话缓存"]),
        ("通信协议", ["axios 统一封装", "SSE 流式 Token", "WebSocket 心跳重连", "OpenAPI 类型生成"]),
        ("质量保障", ["Vitest 单测 ≥70%", "Playwright E2E", "Storybook 组件文档", "Sentry 错误监控"]),
    ]
    for i, (t, items) in enumerate(cols):
        x = 5 + i * 23.5
        ax.text(x, 30.6, t, fontsize=7.8, fontweight="bold", color=C["brand_text"], zorder=5)
        for j, it in enumerate(items):
            ax.text(x, 27.4 - j * 3.0, "· " + it, fontsize=6.8, color=C["ink2"],
                    va="center", zorder=5)

    save(fig, "/workspace/design/01-architecture/frontend-architecture.png", dpi=150)


if __name__ == "__main__":
    gen_system()
    gen_frontend()
