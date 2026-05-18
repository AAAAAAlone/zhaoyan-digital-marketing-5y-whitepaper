#!/usr/bin/env python3
"""
c08 · 营销 L1 议题占比（按年 100% 堆叠柱）

版式（专为本图）：
  画布 1920×1080
  绘图区约占 78% 宽 × 72% 高
  图例 10 项，底部 2 行 × 5 列
  Y 轴 0–100%，6 个年份在 X 轴

只输出 PNG，不写 MD / PPT。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import font_manager
import numpy as np


def _setup_cjk_font() -> None:
    for name in (
        "PingFang SC",
        "Hiragino Sans GB",
        "Songti SC",
        "STHeiti",
        "Arial Unicode MS",
        "Noto Sans CJK SC",
    ):
        try:
            font_manager.findfont(name, fallback_to_default=False)
            plt.rcParams["font.sans-serif"] = [name, "DejaVu Sans"]
            plt.rcParams["axes.unicode_minus"] = False
            return
        except Exception:
            continue


_setup_cjk_font()

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from chart_theme import DARK, LIGHT, ChartTheme  # noqa: E402
from charts.common import theme_text  # noqa: E402

OUT = ROOT / "assets" / "charts"
DATA = ROOT / "assets" / "data" / "manifest.json"

# 图例顺序：与白皮书叙事一致
TOPICS = ["线索", "SEO", "内容", "投放", "工具", "课程", "私域", "招聘", "出海", "GEO"]
YEARS = ["2021", "2022", "2023", "2024", "2025", "2026"]

W_PX, H_PX, DPI = 1920, 1080, 100
TITLE = "营销 L1 议题占比"


def load_shares() -> np.ndarray:
    l1_year = json.loads(DATA.read_text(encoding="utf-8"))["l1_year"]
    mat = np.zeros((len(TOPICS), len(YEARS)), dtype=float)
    for j, y in enumerate(YEARS):
        row = l1_year[y]
        total = sum(row.values()) or 1
        for i, k in enumerate(TOPICS):
            mat[i, j] = row.get(k, 0) / total * 100
    return mat


def render(theme: ChartTheme) -> Path:
    shares = load_shares()
    fig_w, fig_h = W_PX / DPI, H_PX / DPI
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=DPI)
    fig.patch.set_facecolor(theme.bg)
    ax.set_facecolor(theme.bg)

    x = np.arange(len(YEARS))
    width = 0.62
    bottom = np.zeros(len(YEARS))
    colors = list(theme.palette[: len(TOPICS)])

    for i, topic in enumerate(TOPICS):
        ax.bar(
            x,
            shares[i],
            width,
            bottom=bottom,
            label=topic,
            color=colors[i],
            edgecolor=theme.bg,
            linewidth=0.6,
        )
        bottom += shares[i]

    ax.set_ylim(0, 100)
    ax.set_yticks([0, 25, 50, 75, 100])
    txt = theme_text(theme)
    ax.set_yticklabels(["0%", "25%", "50%", "75%", "100%"], fontsize=16, color=txt)
    ax.set_xticks(x)
    ax.set_xticklabels(YEARS, fontsize=18, color=txt)
    ax.tick_params(axis="x", length=0, pad=10)
    ax.tick_params(axis="y", colors=theme.axis, labelcolor=txt)
    ax.grid(axis="y", color=theme.axis, alpha=0.35, linewidth=0.8)
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_visible(False)

    ax.set_title(TITLE, fontsize=28, fontweight="bold", color=txt, pad=18)

    # 图例：2 行，占底部约 14%
    handles = [mpatches.Patch(facecolor=colors[i], edgecolor="none", label=TOPICS[i]) for i in range(len(TOPICS))]
    leg = fig.legend(
        handles=handles,
        loc="lower center",
        ncol=5,
        frameon=False,
        fontsize=14,
        labelcolor=txt,
        bbox_to_anchor=(0.5, 0.02),
        columnspacing=1.2,
        handletextpad=0.5,
        handlelength=1.4,
    )
    for t in leg.get_texts():
        t.set_color(txt)

    # 主绘图区边距（给标题 + 双行图例留位）
    fig.subplots_adjust(left=0.07, right=0.98, top=0.90, bottom=0.16)

    stem = f"c08-l1-share-year-{theme.name}"
    png = OUT / f"{stem}.png"
    fig.savefig(png, facecolor=theme.bg, edgecolor="none")
    plt.close(fig)
    if theme.name == "light":
        (OUT / "c08-l1-share-year.png").write_bytes(png.read_bytes())
    return png


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for theme in (LIGHT, DARK):
        p = render(theme)
        print("ok", p, p.stat().st_size, "bytes")


if __name__ == "__main__":
    main()
