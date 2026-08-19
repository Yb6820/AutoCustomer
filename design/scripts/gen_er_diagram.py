# -*- coding: utf-8 -*-
"""生成 MySQL ER 图（29 张表、6 大主题域 + Milvus 映射节点）。

布局说明：
- 画布按上/下两排、6 个主题域分区布局（RBAC / 知识库 / AI 配置 / 对话 / 工单坐席 / 统计）
- 域内核心关系用实线，跨域弱关联用虚线
- kb_chunk 与 Milvus 集合通过 chunk_id 1:1 对齐（品牌色虚线）
- 每张表仅展示核心字段，完整字段定义见 /design/02-database/README.md

同步更新：表结构变更时修改本脚本的 TABLES/LAYOUT/RELATIONS 后重新执行：
    python3 /workspace/design/scripts/gen_er_diagram.py
"""
import sys

sys.path.insert(0, "/workspace/design/scripts")
from plot_common import (
    setup_font, new_canvas, box, line_text, arrow, link_label, save,
    DOMAIN_COLORS, DOMAIN_NAMES, C,
)

setup_font()

# ---------------------------------------------------------------- 表定义
# 字段: (名称, 类型, 标记) 标记: PK / FK / UQ / "" / "IDX"
F = lambda n, t, m="": (n, t, m)

TABLES = {
    # ---- RBAC 域 ----
    "sys_user": ("rbac", "sys_user · 用户", [
        F("id", "BIGINT", "PK"), F("dept_id", "BIGINT", "FK"),
        F("username", "VARCHAR(64)", "UQ"), F("password_hash", "VARCHAR(255)"),
        F("email", "VARCHAR(128)"), F("phone", "VARCHAR(32)"),
        F("status", "TINYINT"), F("last_login_at", "DATETIME"),
    ]),
    "sys_dept": ("rbac", "sys_dept · 部门", [
        F("id", "BIGINT", "PK"), F("parent_id", "BIGINT", "FK"),
        F("name", "VARCHAR(64)"), F("leader_user_id", "BIGINT", "FK"),
        F("sort", "INT"), F("status", "TINYINT"),
    ]),
    "sys_role": ("rbac", "sys_role · 角色", [
        F("id", "BIGINT", "PK"), F("code", "VARCHAR(64)", "UQ"),
        F("name", "VARCHAR(64)"), F("role_type", "TINYINT"),
        F("data_scope", "TINYINT"), F("is_system", "BOOL"),
        F("remark", "VARCHAR(255)"), F("status", "TINYINT"),
    ]),
    "sys_permission": ("rbac", "sys_permission · 权限点", [
        F("id", "BIGINT", "PK"), F("menu_id", "BIGINT", "FK"),
        F("code", "VARCHAR(128)", "UQ"), F("name", "VARCHAR(64)"),
        F("type", "TINYINT"), F("api_method", "VARCHAR(8)"),
        F("api_path", "VARCHAR(255)"),
    ]),
    "sys_user_role": ("rbac", "sys_user_role · 用户-角色", [
        F("id", "BIGINT", "PK"), F("user_id", "BIGINT", "FK"),
        F("role_id", "BIGINT", "FK"),
    ]),
    "sys_role_perm": ("rbac", "sys_role_perm · 角色-权限", [
        F("id", "BIGINT", "PK"), F("role_id", "BIGINT", "FK"),
        F("perm_id", "BIGINT", "FK"),
    ]),
    "sys_role_data_scope": ("rbac", "sys_role_data_scope · 自定义数据范围", [
        F("id", "BIGINT", "PK"), F("role_id", "BIGINT", "FK"),
        F("dept_id", "BIGINT", "FK"),
    ]),
    "sys_menu": ("rbac", "sys_menu · 菜单", [
        F("id", "BIGINT", "PK"), F("parent_id", "BIGINT", "FK"),
        F("name", "VARCHAR(64)"), F("path", "VARCHAR(255)"),
        F("component", "VARCHAR(255)"), F("icon", "VARCHAR(64)"),
        F("sort", "INT"), F("visible", "BOOL"),
    ]),
    "sys_audit_log": ("rbac", "sys_audit_log · 审计日志", [
        F("id", "BIGINT", "PK"), F("user_id", "BIGINT", "FK"),
        F("action", "VARCHAR(64)"), F("resource", "VARCHAR(128)"),
        F("detail", "JSON"), F("ip", "VARCHAR(64)"),
        F("created_at", "DATETIME"),
    ]),
    "sys_login_log": ("rbac", "sys_login_log · 登录日志", [
        F("id", "BIGINT", "PK"), F("user_id", "BIGINT", "FK"),
        F("username", "VARCHAR(64)"), F("login_type", "VARCHAR(16)"),
        F("ip", "VARCHAR(64)"), F("status", "TINYINT"),
        F("created_at", "DATETIME"),
    ]),
    # ---- 知识库域 ----
    "kb_category": ("kb", "kb_category · 知识分类", [
        F("id", "BIGINT", "PK"), F("parent_id", "BIGINT", "FK"),
        F("name", "VARCHAR(64)"), F("sort", "INT"), F("status", "TINYINT"),
    ]),
    "kb_document": ("kb", "kb_document · 知识文档", [
        F("id", "BIGINT", "PK"), F("category_id", "BIGINT", "FK"),
        F("title", "VARCHAR(255)"), F("file_type", "VARCHAR(16)"),
        F("file_url", "VARCHAR(512)"), F("file_hash", "CHAR(64)", "IDX"),
        F("status", "TINYINT"), F("version", "INT"),
        F("created_by", "BIGINT", "FK"),
    ]),
    "kb_chunk": ("kb", "kb_chunk · 知识分片", [
        F("id", "BIGINT", "PK"), F("doc_id", "BIGINT", "FK"),
        F("content", "TEXT"), F("chunk_index", "INT"),
        F("token_count", "INT"), F("meta", "JSON"),
        F("status", "TINYINT"),
    ]),
    "kb_qa_pair": ("kb", "kb_qa_pair · 问答对", [
        F("id", "BIGINT", "PK"), F("doc_id", "BIGINT", "FK"),
        F("chunk_id", "BIGINT", "FK"), F("question", "VARCHAR(512)"),
        F("answer", "TEXT"), F("hit_count", "INT"),
        F("status", "TINYINT"),
    ]),
    "kb_import_task": ("kb", "kb_import_task · 导入任务", [
        F("id", "BIGINT", "PK"), F("doc_id", "BIGINT", "FK"),
        F("task_type", "VARCHAR(16)"), F("status", "TINYINT"),
        F("progress", "TINYINT"), F("error_msg", "VARCHAR(512)"),
        F("finished_at", "DATETIME"),
    ]),
    # ---- 对话域 ----
    "chat_session": ("chat", "chat_session · 会话", [
        F("id", "BIGINT", "PK"), F("customer_id", "VARCHAR(64)", "IDX"),
        F("source", "VARCHAR(16)"), F("status", "TINYINT"),
        F("rating", "TINYINT"), F("model_config_id", "BIGINT", "FK"),
        F("last_msg_at", "DATETIME"), F("created_at", "DATETIME"),
    ]),
    "chat_message": ("chat", "chat_message · 消息", [
        F("id", "BIGINT", "PK"), F("session_id", "BIGINT", "FK"),
        F("role", "VARCHAR(16)"), F("content", "MEDIUMTEXT"),
        F("tokens", "INT"), F("model", "VARCHAR(64)"),
        F("retrieval_ids", "JSON"), F("latency_ms", "INT"),
        F("msg_type", "VARCHAR(16)"),
    ]),
    "chat_retrieval_log": ("chat", "chat_retrieval_log · 检索日志", [
        F("id", "BIGINT", "PK"), F("message_id", "BIGINT", "FK"),
        F("query", "TEXT"), F("topk_scores", "JSON"),
        F("threshold", "FLOAT"), F("hit_count", "INT"),
        F("rerank_used", "BOOL"), F("latency_ms", "INT"),
    ]),
    "chat_feedback": ("chat", "chat_feedback · 消息反馈", [
        F("id", "BIGINT", "PK"), F("message_id", "BIGINT", "FK"),
        F("session_id", "BIGINT", "FK"), F("feedback_type", "TINYINT"),
        F("reason", "VARCHAR(255)"), F("created_at", "DATETIME"),
    ]),
    "chat_quick_reply": ("chat", "chat_quick_reply · 快捷回复", [
        F("id", "BIGINT", "PK"), F("scene", "VARCHAR(32)"),
        F("title", "VARCHAR(128)"), F("content", "TEXT"),
        F("sort", "INT"), F("status", "TINYINT"),
    ]),
    # ---- 工单坐席域 ----
    "agent_group": ("ticket", "agent_group · 客服组", [
        F("id", "BIGINT", "PK"), F("name", "VARCHAR(64)"),
        F("description", "VARCHAR(255)"), F("sort", "INT"),
    ]),
    "agent_profile": ("ticket", "agent_profile · 坐席档案", [
        F("id", "BIGINT", "PK"), F("user_id", "BIGINT", "FK/UQ"),
        F("group_id", "BIGINT", "FK"), F("agent_no", "VARCHAR(32)"),
        F("skill_tags", "JSON"), F("max_concurrency", "INT"),
        F("online_status", "TINYINT"),
    ]),
    "human_ticket": ("ticket", "human_ticket · 人工工单", [
        F("id", "BIGINT", "PK"), F("session_id", "BIGINT", "FK"),
        F("ticket_no", "VARCHAR(32)", "UQ"), F("reason", "VARCHAR(255)"),
        F("status", "TINYINT"), F("priority", "TINYINT"),
        F("assignee_id", "BIGINT", "FK"), F("group_id", "BIGINT", "FK"),
        F("snapshot", "JSON"),
    ]),
    "ticket_comment": ("ticket", "ticket_comment · 工单沟通", [
        F("id", "BIGINT", "PK"), F("ticket_id", "BIGINT", "FK"),
        F("author_id", "BIGINT", "FK"), F("content", "TEXT"),
        F("is_internal", "BOOL"), F("created_at", "DATETIME"),
    ]),
    "ticket_assign_log": ("ticket", "ticket_assign_log · 流转记录", [
        F("id", "BIGINT", "PK"), F("ticket_id", "BIGINT", "FK"),
        F("from_agent_id", "BIGINT"), F("to_agent_id", "BIGINT"),
        F("action", "VARCHAR(16)"), F("operator_id", "BIGINT"),
        F("created_at", "DATETIME"),
    ]),
    # ---- AI 配置域 ----
    "sys_model_config": ("ai", "sys_model_config · 模型配置", [
        F("id", "BIGINT", "PK"), F("model_type", "VARCHAR(16)"),
        F("provider", "VARCHAR(32)"), F("model_name", "VARCHAR(64)"),
        F("endpoint", "VARCHAR(255)"), F("api_key_enc", "VARBINARY(512)"),
        F("params", "JSON"), F("is_default", "BOOL"),
    ]),
    "sys_prompt_template": ("ai", "sys_prompt_template · Prompt 模板", [
        F("id", "BIGINT", "PK"), F("scene", "VARCHAR(32)"),
        F("name", "VARCHAR(64)"), F("content", "TEXT"),
        F("variables", "JSON"), F("version", "INT"),
        F("status", "TINYINT"),
    ]),
    "kb_retrieval_config": ("ai", "kb_retrieval_config · 检索配置", [
        F("id", "BIGINT", "PK"), F("scope", "VARCHAR(32)"),
        F("target_id", "BIGINT"), F("topk", "INT"),
        F("score_threshold", "FLOAT"), F("rerank_enabled", "BOOL"),
        F("rerank_model_id", "BIGINT", "FK"),
    ]),
    # ---- 统计域 ----
    "stat_daily": ("stat", "stat_daily · 日统计", [
        F("id", "BIGINT", "PK"), F("stat_date", "DATE", "UQ"),
        F("session_count", "INT"), F("message_count", "INT"),
        F("ticket_count", "INT"), F("transfer_rate", "DECIMAL(5,4)"),
        F("hit_rate", "DECIMAL(5,4)"), F("avg_rating", "DECIMAL(3,2)"),
    ]),
}

# ---------------------------------------------------------------- 布局
# 每域: (x0, y_top, 卡片宽, 列数, 表列表按行)
LAYOUT = {
    "rbac":  dict(x=1.5, ytop=96.5, w=8.6, cols=4, rows=[
        ["sys_user", "sys_dept", "sys_role", "sys_permission"],
        ["sys_user_role", "sys_role_perm", "sys_role_data_scope", "sys_menu"],
        ["sys_audit_log", "sys_login_log"],
    ]),
    "kb":    dict(x=41, ytop=96.5, w=14.6, cols=2, rows=[
        ["kb_category", "kb_document"],
        ["kb_chunk", "kb_qa_pair"],
        ["kb_import_task"],
    ]),
    "ai":    dict(x=73.5, ytop=96.5, w=24.5, cols=1, rows=[
        ["sys_model_config"], ["sys_prompt_template"], ["kb_retrieval_config"],
    ]),
    "chat":  dict(x=1.5, ytop=47, w=11.8, cols=3, rows=[
        ["chat_session", "chat_message", "chat_feedback"],
        ["chat_retrieval_log", "chat_quick_reply"],
    ]),
    "ticket": dict(x=41, ytop=47, w=14.6, cols=2, rows=[
        ["agent_group", "agent_profile"],
        ["human_ticket"],
        ["ticket_comment", "ticket_assign_log"],
    ]),
    "stat":  dict(x=73.5, ytop=47, w=24.5, cols=1, rows=[
        ["stat_daily"],
    ]),
}

TITLE_H, ROW_H, PAD = 3.6, 1.72, 0.9
GAP_X, GAP_Y = 1.1, 3.2

# name -> (x, y_bottom, w, h)
POS = {}


def place_tables(ax):
    for domain, lay in LAYOUT.items():
        color = DOMAIN_COLORS[domain]
        # 计算域框范围
        col_w = lay["w"] + GAP_X
        row_hs = []
        for row in lay["rows"]:
            row_hs.append(max(len(TABLES[t][2]) for t in row) * ROW_H + TITLE_H + PAD)
        total_h = sum(row_hs) + GAP_Y * (len(lay["rows"]) - 1)
        # 域底框
        box(ax, lay["x"] - 1.2, lay["ytop"] - total_h - 4.6,
            col_w * lay["cols"] - GAP_X + 2.4, total_h + 7.4,
            C["bg"], color, lw=1.1, ls=(0, (5, 4)), r=1.2, z=1, alpha=0.55)
        ax.text(lay["x"] - 0.4, lay["ytop"] - 1.5, DOMAIN_NAMES[domain],
                fontsize=11.5, fontweight="bold", color=color, zorder=5)

        y = lay["ytop"] - 3.4
        for ri, row in enumerate(lay["rows"]):
            for ci, name in enumerate(row):
                _, title, fields = TABLES[name]
                w = lay["w"]
                h = len(fields) * ROW_H + TITLE_H + PAD
                x = lay["x"] + ci * col_w
                yb = y - h
                # 卡片
                box(ax, x, yb, w, h, C["white"], C["border"], lw=1.0, r=0.5, z=3)
                box(ax, x, yb + h - TITLE_H, w, TITLE_H, color, color, lw=0, r=0.5, z=3)
                ax.text(x + w / 2, yb + h - TITLE_H / 2, title, ha="center",
                        va="center", fontsize=8.2, fontweight="bold",
                        color="white", zorder=4)
                # 字段
                for fi, (fn, ft, fm) in enumerate(fields):
                    fy = y + -TITLE_H - fi * ROW_H - ROW_H / 2
                    fy = yb + h - TITLE_H - fi * ROW_H - ROW_H / 2
                    is_pk = fm == "PK"
                    is_fk = "FK" in fm
                    fn_color = color if is_pk else (C["ink"] if not is_fk else C["ink2"])
                    weight = "bold" if is_pk else "normal"
                    line_text(ax, x + 0.55, fy, fn, fs=6.8,
                              color=fn_color, weight=weight, z=5)
                    tag = f"{ft} {fm}".strip()
                    line_text(ax, x + w - 0.55, fy, tag, fs=5.8,
                              color=C["ink3"], ha="right", z=5)
                POS[name] = (x, yb, w, h)
            y -= row_hs[ri] + GAP_Y


def anchor(name, side, frac=0.5):
    """取卡片锚点: side in l/r/t/b。"""
    x, yb, w, h = POS[name]
    if side == "l":
        return (x, yb + h * frac)
    if side == "r":
        return (x + w, yb + h * frac)
    if side == "t":
        return (x + w * frac, yb + h)
    return (x + w * frac, yb)


# ---------------------------------------------------------------- 关系
# (from, from_side, to, to_side, label, kind)  kind: in=域内实线 cross=跨域虚线 vec=Milvus
RELATIONS = [
    # RBAC 域内
    ("sys_dept", "b", "sys_user", "t", "1:N", "in"),
    ("sys_user", "b", "sys_user_role", "t", "1:N", "in"),
    ("sys_role", "b", "sys_role_perm", "t", "1:N", "in"),
    ("sys_permission", "b", "sys_role_perm", "t", "1:N", "in"),
    ("sys_menu", "l", "sys_permission", "r", "1:N", "in"),
    ("sys_role_data_scope", "r", "sys_role", "l", "N:1", "in"),
    # 知识库域内
    ("kb_category", "r", "kb_document", "l", "1:N", "in"),
    ("kb_document", "b", "kb_chunk", "t", "1:N", "in"),
    ("kb_document", "b", "kb_import_task", "t", "1:N", "in"),
    ("kb_chunk", "r", "kb_qa_pair", "l", "1:N", "in"),
    # 对话域内
    ("chat_session", "r", "chat_message", "l", "1:N", "in"),
    ("chat_session", "b", "chat_feedback", "t", "1:N", "in"),
    ("chat_message", "b", "chat_retrieval_log", "t", "1:1", "in"),
    # 工单坐席域内
    ("agent_group", "r", "agent_profile", "l", "1:N", "in"),
    ("agent_profile", "b", "human_ticket", "t", "1:N", "in"),
    ("human_ticket", "b", "ticket_comment", "t", "1:N", "in"),
    ("human_ticket", "b", "ticket_assign_log", "t", "1:N", "in"),
    # 跨域
    ("sys_user", "b", "agent_profile", "t", "1:1", "cross"),
    ("sys_user", "r", "kb_document", "l", "创建人 1:N", "cross"),
    ("chat_session", "r", "human_ticket", "l", "1:N", "cross"),
    ("chat_message", "r", "chat_retrieval_log", "l", "检索引用", "cross"),
]


def draw_milvus_node(ax):
    """Milvus 集合节点（非关系表，特殊样式）。"""
    x, yb, w, h = POS["kb_import_task"]
    mx = x + LAYOUT["kb"]["w"] + GAP_X + 0.4
    my = yb
    box(ax, mx, my, 14.2, 11.5, C["brand_soft"], C["brand"], lw=1.8, r=0.8, z=3)
    ax.text(mx + 7.1, my + 9.2, "Milvus · kb_chunk_vec", ha="center", va="center",
            fontsize=9, fontweight="bold", color=C["brand_text"], zorder=5)
    for i, t in enumerate(["chunk_id INT64 PK (对齐 MySQL)",
                           "doc_id INT64 · partition key",
                           "embedding FLOAT_VECTOR(dyn)",
                           "metric=COSINE · HNSW"]):
        ax.text(mx + 1.0, my + 7.0 - i * 1.8, t, fontsize=6.6,
                color=C["brand_text"], va="center", zorder=5)
    # kb_chunk -> Milvus 虚线
    p1 = anchor("kb_chunk", "b", 0.5)
    p2 = (mx + 1.0, my + 11.5)
    arrow(ax, p1, (p2[0], p2[1] + 0.2), color=C["brand"], lw=1.6,
          ls=(0, (5, 3)), style="-|>", ms=11, z=2)
    link_label(ax, ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2), "chunk_id 1:1",
               color=C["brand"])


def draw_relations(ax):
    for src, ss, dst, ds, label, kind in RELATIONS:
        p1, p2 = anchor(src, ss), anchor(dst, ds)
        if kind == "in":
            arrow(ax, p1, p2, color=C["ink3"], lw=1.15, style="-", z=2)
            lc = C["ink2"]
        elif kind == "cross":
            arrow(ax, p1, p2, color=C["teal"], lw=1.5, ls=(0, (5, 3)),
                  style="-", z=2)
            lc = C["teal"]
        # 标签放在线段中点附近，向下偏移避免压线
        mx, my = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2
        link_label(ax, (mx, my), label, color=lc)


def main():
    fig, ax = new_canvas(
        30, 19,
        "AutoCustomer · MySQL 数据库 ER 图（29 表 / 6 主题域）",
        "实线=域内关系 · 青色虚线=跨域关联 · 紫色虚线=Milvus 向量映射 · PK 主键加粗着色 · 完整字段见 02-database/README.md",
    )
    place_tables(ax)
    draw_relations(ax)
    draw_milvus_node(ax)

    # 图例
    lx, ly = 73.5, 30.5
    box(ax, lx, ly, 24.5, 11.5, C["white"], C["border"], lw=1.0, r=0.6, z=3)
    ax.text(lx + 1.2, ly + 9.6, "图例", fontsize=9, fontweight="bold",
            color=C["ink"], zorder=5)
    items = [
        ("PK", "主键（加粗 + 域色）", C["brand"]),
        ("FK", "外键（关联目标见表说明）", C["ink2"]),
        ("UQ / IDX", "唯一索引 / 普通索引", C["ink3"]),
        ("——", "域内 1:N / 1:1 关系", C["ink3"]),
        ("- - -", "跨域弱关联 / Milvus 映射", C["teal"]),
    ]
    for i, (k, v, col) in enumerate(items):
        yy = ly + 7.6 - i * 1.7
        ax.text(lx + 1.6, yy, k, fontsize=7, color=col, fontweight="bold",
                va="center", zorder=5)
        ax.text(lx + 6.6, yy, v, fontsize=7, color=C["ink2"], va="center", zorder=5)

    save(fig, "/workspace/design/02-database/er-diagram-mysql.png", dpi=150)


if __name__ == "__main__":
    main()
