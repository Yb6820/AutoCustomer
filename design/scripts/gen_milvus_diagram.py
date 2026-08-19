# -*- coding: utf-8 -*-
"""生成 Milvus 向量库集合设计图。

内容：MySQL↔Milvus 双写同步、集合 Schema、索引/检索参数、分区策略、
生命周期管理（写入/删除/重建）、降级策略。

同步更新：集合结构变更时修改本脚本后重新执行：
    python3 /workspace/design/scripts/gen_milvus_diagram.py
"""
import sys

sys.path.insert(0, "/workspace/design/scripts")
from plot_common import setup_font, new_canvas, box, header_box, line_text, arrow, link_label, save, C

setup_font()


def kv_panel(ax, x, y, w, title, color, items, fs=7.4, title_fs=9.5, row_h=None):
    """键值面板卡片，items: [(k, v)] 或 [(k,)] 单行文本。"""
    row_h = row_h or 2.4
    h = 5.0 + row_h * len(items)
    header_box(ax, x, y, w, h, title, color, fs=title_fs)
    for i, item in enumerate(items):
        yy = y + h - 5.0 - row_h * i - row_h / 2
        if len(item) == 2:
            line_text(ax, x + 1.2, yy, item[0], fs=fs, color=C["ink"], weight="bold")
            line_text(ax, x + w - 1.2, yy, item[1], fs=fs - 0.2, color=C["ink2"], ha="right")
        else:
            line_text(ax, x + 1.2, yy, item[0], fs=fs, color=C["ink2"])
    return h


def main():
    fig, ax = new_canvas(
        30, 16.5,
        "AutoCustomer · Milvus 向量库集合设计",
        "与 MySQL kb_chunk / kb_qa_pair 通过主键 1:1 对齐 · cosine 相似度 · HNSW 索引 · 版本化重建",
    )

    # ================================================================ 顶部：双写同步流
    ytop = 86
    steps = [
        ("① 文档发布/更新", "运营后台触发", C["ink2"]),
        ("② 生成 chunk 行", "MySQL kb_chunk", C["green"]),
        ("③ 异步向量化", "Celery: embed(chunk)", C["brand"]),
        ("④ Milvus upsert", "kb_chunk_vec 集合", C["brand"]),
    ]
    sw, sx, sy = 20, 2.5, ytop - 8.5
    for i, (t1, t2, col) in enumerate(steps):
        x = sx + i * (sw + 3.8)
        box(ax, x, sy, sw, 8.2, C["white"], col, lw=1.6, r=0.7, z=3)
        ax.text(x + sw / 2, sy + 5.4, t1, ha="center", va="center",
                fontsize=9, fontweight="bold", color=C["ink"], zorder=5)
        ax.text(x + sw / 2, sy + 2.4, t2, ha="center", va="center",
                fontsize=7.6, color=col, zorder=5)
        if i < len(steps) - 1:
            arrow(ax, (x + sw + 0.4, sy + 4.1), (x + sw + 3.4, sy + 4.1),
                  color=C["ink3"], lw=1.5, style="-|>", ms=12, z=4)

    # 幂等与一致性标注
    ax.text(50, sy - 2.2, "幂等：chunk_id 主键 upsert 覆盖 · 事务外异步（最终一致）· 失败重试入死信队列 · 校验任务 count(MySQL chunk) == count(Milvus)",
            ha="center", va="center", fontsize=7.6, color=C["ink2"], zorder=5,
            bbox=dict(boxstyle="round,pad=0.35", fc=C["bg"], ec=C["border"]))

    # ================================================================ 中部：集合 Schema
    y2 = 40
    # kb_chunk_vec
    kv_panel(ax, 2.5, y2, 24, "Collection · kb_chunk_vec（主集合）", C["brand"], [
        ("chunk_id", "INT64 · PRIMARY KEY"),
        ("doc_id", "INT64 · 分区键 partition key"),
        ("category_id", "INT64 · 标量过滤"),
        ("embedding", "FLOAT_VECTOR · dim 768/1024/1536"),
        ("status", "INT8 · published / offline"),
        ("created_at", "INT64 · 毫秒时间戳"),
    ], fs=7.8, row_h=2.9)

    # kb_qa_vec
    kv_panel(ax, 28.5, y2, 24, "Collection · kb_qa_vec（QA 对集合，可选）", C["brand"], [
        ("qa_id", "INT64 · PK，对齐 kb_qa_pair.id"),
        ("question_vec", "FLOAT_VECTOR · 问题向量"),
        ("doc_id", "INT64 · 分区键"),
        ("answer_digest", "VARCHAR(512) · 冗余摘要"),
    ], fs=7.8, row_h=2.9)

    # 索引/检索参数
    kv_panel(ax, 54.5, y2, 21, "索引与检索参数", C["teal"], [
        ("索引类型", "HNSW（M=16, efC=256）"),
        ("相似度", "COSINE"),
        ("检索 topK", "20 → rerank → topN 5"),
        ("ef (HNSW)", "64"),
        ("命中阈值", "score ≥ 0.78"),
        ("未命中", "低于阈值 → 转人工分支"),
    ], fs=7.6, row_h=2.9)

    # 分区策略
    kv_panel(ax, 78, y2, 19.5, "分区策略", C["blue"], [
        ("partition key", "doc_id 取模（默认 8 分区）"),
        ("收益", "按文档过滤裁剪扫描"),
        ("扩容", "分区数可调（重建时切换）"),
        ("多租户预留", "tenant_id 字段预留"),
    ], fs=7.6, row_h=2.9)

    # ================================================================ 底部：生命周期
    y3 = 4
    lc = [
        ("写入", "Celery 任务 embed → upsert；批量 64/批"),
        ("更新", "文档新版本 → 新 chunk 全量替换（delete by doc_id + 重新 upsert）"),
        ("删除", "kb_document 软删 → Milvus delete(expr=doc_id in [...]) 定时对账"),
        ("重建", "新建 kb_chunk_vec_v2 集合 → 双写 → alias 切换 → 删旧集合（无停服）"),
        ("降级", "Milvus 不可用 → MySQL 全文索引/BM25 关键词检索兜底"),
    ]
    bw = 18.6
    for i, (t, d) in enumerate(lc):
        x = 2.5 + i * (bw + 1.1)
        box(ax, x, y3, bw, 15.5, C["white"], C["border"], lw=1.2, r=0.6, z=3)
        box(ax, x, y3 + 11.6, bw, 3.9, C["brand_soft"], C["brand_soft"], lw=0, r=0.6, z=3)
        ax.text(x + bw / 2, y3 + 13.5, t, ha="center", va="center",
                fontsize=9, fontweight="bold", color=C["brand_text"], zorder=5)
        # 描述换行
        words, lines, cur = d, [], ""
        for ch in words:
            if len(cur) >= 13:
                lines.append(cur)
                cur = ch
            else:
                cur += ch
        lines.append(cur)
        for j, ln in enumerate(lines[:4]):
            ax.text(x + bw / 2, y3 + 9.6 - j * 2.4, ln, ha="center", va="center",
                    fontsize=6.9, color=C["ink2"], zorder=5)

    save(fig, "/workspace/design/02-database/milvus-collections.png", dpi=150)


if __name__ == "__main__":
    main()
