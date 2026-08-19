# -*- coding: utf-8 -*-
"""生成 RBAC 权限体系设计图。

内容：RBAC 核心模型（用户 N:M 角色 N:M 权限点 + 数据范围）、
10 个预置角色（4 分组）、权限码规范、新角色 5 步接入流程（零代码）。

同步更新：角色体系变更时修改本脚本后重新执行：
    python3 /workspace/design/scripts/gen_rbac_diagram.py
"""
import sys

sys.path.insert(0, "/workspace/design/scripts")
from plot_common import setup_font, new_canvas, box, header_box, line_text, arrow, link_label, save, C

setup_font()

GROUP_COLORS = {
    "sys": "#4B3FE3",      # 系统管理组
    "biz": "#16A34A",      # 业务运营组
    "cs": "#D97706",       # 客服组
    "tech": "#7C3AED",     # 技术组
}


def entity(ax, x, y, w, h, title, sub, color):
    box(ax, x, y, w, h, C["white"], color, lw=1.6, r=0.55, z=3)
    ax.text(x + w / 2, y + h * 0.62, title, ha="center", va="center",
            fontsize=8.6, fontweight="bold", color=C["ink"], zorder=5)
    ax.text(x + w / 2, y + h * 0.26, sub, ha="center", va="center",
            fontsize=6.6, color=C["ink2"], zorder=5)


def gen_rbac():
    fig, ax = new_canvas(
        30, 17.5,
        "AutoCustomer · RBAC 权限体系设计（多角色叠加 + 数据范围 + 零代码接入新角色）",
        "用户可持多角色（权限取并集）· 权限点三级（菜单/按钮/API）· 数据范围五档 · 新角色全程后台 UI 配置，无需改代码、无需重启",
    )

    # ================================================================ 顶部：核心模型
    y = 74
    entity(ax, 2, y, 13, 8, "sys_user 用户", "一个用户可绑定多个角色", C["brand"])
    entity(ax, 20, y + 1.5, 13, 5, "sys_user_role", "用户-角色关联 N:M", C["ink2"])
    entity(ax, 38, y, 13, 8, "sys_role 角色", "内置/业务/自定义三类", C["brand"])
    entity(ax, 56, y + 1.5, 13, 5, "sys_role_perm", "角色-权限关联 N:M", C["ink2"])
    entity(ax, 74, y, 13, 8, "sys_permission 权限点", "menu / btn / api 三级", C["brand"])
    entity(ax, 90.5, y + 1.5, 7.5, 5, "sys_menu", "菜单树", C["ink2"])
    entity(ax, 38, y - 13, 13, 7, "sys_role_data_scope", "自定义数据范围", C["teal"])
    entity(ax, 56, y - 13, 13, 7, "sys_dept 部门树", "数据范围的判定依据", C["teal"])

    arrow(ax, (15, y + 4), (20, y + 4), color=C["ink3"], lw=1.5, style="-|>", ms=11)
    arrow(ax, (33, y + 4), (38, y + 4), color=C["ink3"], lw=1.5, style="-|>", ms=11)
    arrow(ax, (51, y + 4), (56, y + 4), color=C["ink3"], lw=1.5, style="-|>", ms=11)
    arrow(ax, (87, y + 4), (90.5, y + 4), color=C["ink3"], lw=1.5, style="-|>", ms=11)
    arrow(ax, (44.5, y), (44.5, y - 6), color=C["teal"], lw=1.5, style="-|>", ms=11)
    arrow(ax, (51, y - 9.5), (56, y - 9.5), color=C["teal"], lw=1.5, style="-|>", ms=11)
    # 数据范围枚举
    box(ax, 2, y - 16, 30, 9.5, C["bg"], C["border"], lw=1.0, r=0.6, z=2)
    ax.text(3.4, y - 8.9, "数据范围枚举（sys_role.data_scope）", fontsize=8,
            fontweight="bold", color=C["ink"], zorder=5)
    scopes = [("ALL", "全部数据"), ("DEPT", "本部门"), ("DEPT_AND_CHILD", "本部门及下级"),
              ("SELF", "仅本人相关"), ("CUSTOM", "自定义部门(关联表)")]
    for i, (k, v) in enumerate(scopes):
        ax.text(3.4 + (i % 3) * 9.8, y - 11.6 - (i // 3) * 2.6,
                f"{k}={v}", fontsize=6.4, color=C["ink2"], va="center", zorder=5)

    # 权限码规范
    box(ax, 74, y - 16, 23.8, 9.5, C["bg"], C["border"], lw=1.0, r=0.6, z=2)
    ax.text(75.4, y - 8.9, "权限码命名规范", fontsize=8, fontweight="bold",
            color=C["ink"], zorder=5)
    for i, s in enumerate(["模块:资源:动作 全小写", "如 kb:doc:publish",
                           "chat:ticket:assign · rbac:role:create", "新权限点走 Alembic 种子迁移"]):
        ax.text(75.4, y - 11.4 - i * 2.4, "· " + s, fontsize=6.6, color=C["ink2"],
                va="center", zorder=5)

    # ================================================================ 左下：预置角色
    box(ax, 2, 3.5, 52, 49, C["bg"], C["border"], lw=1.0, r=0.8, z=2)
    ax.text(3.6, 50.2, "预置角色体系（10 角色 / 4 分组 · 内置角色 is_system 不可删，可派生）",
            fontsize=9.5, fontweight="bold", color=C["ink"], zorder=5)

    roles = [
        # (组, code, 名称, 数据范围, 核心权限摘要)
        ("sys", "super_admin", "超级管理员", "ALL", "全部权限 · 模型配置 · 角色管理"),
        ("sys", "sys_admin", "系统管理员", "ALL", "用户/角色/菜单/审计 · 不含模型配置"),
        ("sys", "auditor", "审计员", "ALL·只读", "审计/登录日志只读 · 不可修改删除"),
        ("biz", "operator", "运营主管", "ALL", "仪表盘/知识库/报表/工单分配"),
        ("biz", "kb_editor", "知识库编辑", "SELF", "文档 CRUD 限本人创建 · 提审不可发布"),
        ("biz", "kb_reviewer", "知识库审核", "ALL", "文档发布/下线审核 · 版本回退"),
        ("biz", "viewer", "只读访客", "ALL·只读", "各业务模块只读 · 供参观/交接"),
        ("cs", "agent_leader", "客服组长", "DEPT_AND_CHILD", "工单分配/转派 · 坐席监控 · 质检"),
        ("cs", "agent", "人工客服", "SELF", "回复分配工单 · 查看关联会话"),
        ("tech", "ai_engineer", "AI 工程师", "ALL", "模型/Prompt/检索参数 · 黄金集评估"),
    ]
    ry = 46.5
    for grp, code, name, scope, perms in roles:
        col = GROUP_COLORS[grp]
        box(ax, 3.6, ry - 3.9, 48.8, 4.1, C["white"], C["border"], lw=0.9, r=0.35, z=3)
        box(ax, 3.6, ry - 3.9, 1.6, 4.1, col, col, lw=0, r=0.35, z=4)
        ax.text(6.2, ry - 1.9, code, fontsize=7.6, fontweight="bold", color=col,
                va="center", zorder=5)
        ax.text(17.5, ry - 1.9, name, fontsize=7.2, color=C["ink"],
                va="center", zorder=5)
        ax.text(24.5, ry - 1.9, scope, fontsize=6.4, color=C["teal"],
                va="center", zorder=5, fontweight="bold")
        ax.text(52.0, ry - 1.9, perms, fontsize=6.3, color=C["ink2"],
                va="center", ha="right", zorder=5)
        ry -= 4.35

    # 图例（分组）
    for i, (g, n) in enumerate([("sys", "系统管理"), ("biz", "业务运营"),
                                ("cs", "客服"), ("tech", "技术")]):
        ax.text(3.6 + i * 12.5, 6.2, "■ " + n, fontsize=6.8,
                color=GROUP_COLORS[g], va="center", zorder=5)

    # ================================================================ 右下：新角色接入流程
    box(ax, 56, 3.5, 42, 49, C["bg"], C["border"], lw=1.0, r=0.8, z=2)
    ax.text(57.6, 50.2, "新角色快速接入流程（全程后台 UI · 零代码 · 不重启）",
            fontsize=9.5, fontweight="bold", color=C["ink"], zorder=5)
    steps = [
        ("① 新建角色", "角色管理 → 新建：code / 名称 / role_type=custom / 数据范围", C["brand"]),
        ("② 勾选权限", "权限树勾选（菜单+按钮+API）；支持「复制现有角色」模板加速", C["brand"]),
        ("③ 配置数据范围", "选枚举或 CUSTOM 关联部门；立即影响该角色所有查询过滤", "#16A34A"),
        ("④ 绑定用户", "单个/批量绑定；用户多角色权限取并集，数据范围取最宽档", "#D97706"),
        ("⑤ 即时生效", "Redis 权限缓存失效重载 · 前端动态路由/菜单自动刷新", "#16A34A"),
    ]
    sy = 46.5
    for i, (t, d, col) in enumerate(steps):
        yy = sy - i * 8.4
        box(ax, 57.6, yy - 7.2, 38.8, 7.4, C["white"], col, lw=1.3, r=0.5, z=3)
        ax.text(59.2, yy - 2.4, t, fontsize=8, fontweight="bold", color=col,
                va="center", zorder=5)
        # 描述自动换行
        cur, lines = "", []
        for ch in d:
            if len(cur) >= 26:
                lines.append(cur)
                cur = ch
            else:
                cur += ch
        lines.append(cur)
        for j, ln in enumerate(lines[:2]):
            ax.text(59.2, yy - 4.6 - j * 2.0, ln, fontsize=6.4, color=C["ink2"],
                    va="center", zorder=5)
        if i < len(steps) - 1:
            arrow(ax, (77, yy - 7.3), (77, yy - 8.5), color=C["ink3"],
                  lw=1.3, style="-|>", ms=10, z=5)

    # 底部支撑说明
    ax.text(77, 6.0, "设计支撑：权限点全部存库（Alembic 种子）· 后端 require_permission 依赖按码拦截 ·"
                     "前端 v-perm 指令 + 动态路由",
            fontsize=6.6, color=C["ink2"], ha="center", va="center", zorder=5,
            bbox=dict(boxstyle="round,pad=0.35", fc=C["white"], ec=C["border"]))

    save(fig, "/workspace/design/03-rbac/rbac-model.png", dpi=150)


if __name__ == "__main__":
    gen_rbac()
