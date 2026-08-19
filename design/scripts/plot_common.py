# -*- coding: utf-8 -*-
"""设计图绘制公共模块：字体注册、色板、卡片/连线绘制工具。

所有设计图脚本共享本模块。架构或模型变更时，修改对应 gen_*.py 脚本后重新执行即可
重新生成 /design 下的 PNG 图片（同步更新机制见 /design/README.md）。
"""
import matplotlib

matplotlib.use("Agg")

from matplotlib import font_manager
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

FONT_PATH = "/workspace/design/assets/fonts/NotoSansSC-Regular.ttf"


FONT_BOLD_PATH = "/workspace/design/assets/fonts/NotoSansSC-Bold.ttf"


def setup_font():
    """注册本地中文字体（Regular + Bold），全局启用。"""
    for p in (FONT_PATH, FONT_BOLD_PATH):
        try:
            font_manager.fontManager.addfont(p)
        except Exception:
            pass
    plt.rcParams["font.family"] = "Noto Sans SC"
    plt.rcParams["axes.unicode_minus"] = False
    plt.rcParams["savefig.facecolor"] = "white"


# 与整体设计一致的紫色主题色板
C = {
    "brand": "#4B3FE3",          # 主品牌色（焦点）
    "brand_dark": "#3C2ECA",
    "brand_soft": "#E5EAFF",     # 品牌浅底
    "brand_text": "#1A1759",
    "ink": "#1F2329",            # 主文字
    "ink2": "#4E5969",           # 次级文字
    "ink3": "#86909C",           # 辅助文字
    "line": "#C9CDD4",           # 常规连线
    "border": "#E5E6EB",
    "bg": "#F7F8FA",             # 分组底色
    "white": "#FFFFFF",
    "blue": "#22A5F7",           # 前端/检索层
    "teal": "#14B8A6",           # 数据层
    "amber": "#D97706",          # 提示
    "green": "#16A34A",          # 成功/正向
    "red": "#DC2626",            # 风险/告警
    "purple_soft": "#F2F3FF",
}

# 各主题域配色（ER 图/架构图统一使用）
DOMAIN_COLORS = {
    "rbac": "#4B3FE3",      # 用户与权限域（品牌紫）
    "kb": "#16A34A",        # 知识库域（绿）
    "chat": "#22A5F7",      # 对话域（蓝）
    "ticket": "#D97706",    # 工单坐席域（琥珀）
    "ai": "#7C3AED",        # AI 配置域（深紫）
    "stat": "#86909C",      # 统计域（灰）
}

DOMAIN_NAMES = {
    "rbac": "RBAC 用户与权限域",
    "kb": "知识库域",
    "chat": "对话域",
    "ticket": "工单与坐席域",
    "ai": "AI 配置域",
    "stat": "统计域",
}


def new_canvas(w, h, title, subtitle=None):
    """新建画布，返回 fig/ax。"""
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")
    fig.suptitle(title, fontsize=17, fontweight="bold", color=C["ink"], y=0.975)
    if subtitle:
        fig.text(0.5, 0.945, subtitle, ha="center", fontsize=10.5, color=C["ink2"])
    return fig, ax


def box(ax, x, y, w, h, fc, ec, lw=1.4, ls="-", r=0.6, z=3, alpha=1.0):
    """圆角矩形，(x, y) 为左下角。"""
    p = FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0,rounding_size={r}",
        fc=fc, ec=ec, lw=lw, ls=ls, zorder=z, alpha=alpha,
    )
    ax.add_patch(p)
    return p


def header_box(ax, x, y, w, h, title, fc, tc="white", fs=11, sub=None, z=3):
    """带标题栏的模块框，(x, y) 为左下角。"""
    box(ax, x, y, w, h, C["white"], fc, lw=1.6, r=0.6, z=z)
    head_h = 4.2 if not sub else 6.4
    box(ax, x, y + h - head_h, w, head_h, fc, fc, lw=0, r=0.6, z=z)
    if sub:
        ax.text(x + w / 2, y + h - 2.6, title, ha="center", va="center",
                fontsize=fs, fontweight="bold", color=tc, zorder=z + 1)
        ax.text(x + w / 2, y + h - 5.3, sub, ha="center", va="center",
                fontsize=fs - 2.6, color=tc, alpha=0.92, zorder=z + 1)
    else:
        ax.text(x + w / 2, y + h - head_h / 2, title, ha="center", va="center",
                fontsize=fs, fontweight="bold", color=tc, zorder=z + 1)
    return head_h


def line_text(ax, x, y, text, fs=7.2, color=None, ha="left", z=5, weight="normal"):
    ax.text(x, y, text, fontsize=fs, color=color or C["ink2"], ha=ha,
            va="center", zorder=z, fontweight=weight)


def arrow(ax, p1, p2, color=None, lw=1.3, ls="-", style="-|>", ms=10, z=2, connstyle=None):
    """带箭头连线。"""
    a = FancyArrowPatch(
        p1, p2,
        arrowstyle=style, mutation_scale=ms,
        color=color or C["ink3"], lw=lw, ls=ls, zorder=z,
        connectionstyle=connstyle or "arc3,rad=0",
        shrinkA=1, shrinkB=1,
    )
    ax.add_patch(a)
    return a


def link_label(ax, p, text, color=None, z=6):
    """连线中点标签（白底小胶囊）。"""
    x, y = p
    ax.text(x, y, text, fontsize=6.8, color=color or C["ink2"],
            ha="center", va="center", zorder=z,
            bbox=dict(boxstyle="round,pad=0.18", fc="white", ec="none", alpha=0.9))


def save(fig, path, dpi=160):
    fig.savefig(path, dpi=dpi, bbox_inches="tight", pad_inches=0.25)
    plt.close(fig)
    print(f"[saved] {path}")
