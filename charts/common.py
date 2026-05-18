"""Matplotlib 出图共用：画布、主题、字体、保存校验。"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import font_manager
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "charts"
W_PX, H_PX, DPI = 1920, 1080, 100


def setup_cjk_font() -> None:
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


setup_cjk_font()

# 浅色背景用深字、深色背景用浅字（扇区/柱上另按亮度自适应）
TEXT_LIGHT_BG = "#0a1f3d"
TEXT_DARK_BG = "#e8ecf2"


def theme_text(theme) -> str:
    return theme.text


def contrast_on_fill(facecolor) -> str:
    """根据色块亮度选黑字或白字，保证可读。"""
    from matplotlib import colors as mcolors

    r, g, b = mcolors.to_rgb(facecolor)[:3]
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    return TEXT_DARK_BG if lum < 0.52 else TEXT_LIGHT_BG


def new_figure(theme):
    fig_w, fig_h = W_PX / DPI, H_PX / DPI
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=DPI)
    fig.patch.set_facecolor(theme.bg)
    ax.set_facecolor(theme.bg)
    return fig, ax


def style_axes(ax, theme, *, y_grid: bool = True) -> None:
    if y_grid:
        ax.grid(axis="y", color=theme.axis, alpha=0.35, linewidth=0.8)
        ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_visible(False)


def save_figure(fig, stem: str, theme) -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    png = OUT / f"{stem}-{theme.name}.png"
    fig.savefig(png, facecolor=theme.bg, edgecolor="none")
    plt.close(fig)
    if theme.name == "light":
        (OUT / f"{stem}.png").write_bytes(png.read_bytes())
    return png


def verify_png(path: Path, min_bytes: int = 12000, min_std: float = 5.0) -> None:
    from PIL import Image

    im = np.array(Image.open(path))
    if im.std() < min_std:
        raise RuntimeError(f"空白或异常图: {path} (std={im.std():.2f})")
    if path.stat().st_size < min_bytes:
        raise RuntimeError(f"文件过小: {path} ({path.stat().st_size} bytes)")


def pie_donut(
    theme,
    stem: str,
    title: str,
    data: list[tuple[str, int]],
    *,
    legend_ncol: int | None = None,
    show_pct_labels: bool = True,
    bottom_margin: float = 0.14,
    pct_min: float = 4.0,
):
    """饼图 / 环图：数据不变，专注重心环图 + 底部图例。"""
    labels = [a for a, _ in data]
    sizes = [b for _, b in data]
    colors = list(theme.palette[: len(data)])
    n = len(data)
    ncol = legend_ncol or (5 if n > 6 else (2 if n <= 4 else 4))
    txt = theme_text(theme)
    # 项少、环区大 → 扇区百分比更大更粗
    if n <= 4:
        pct_fs, leg_fs, pct_min = 17, 16, 3.0
    elif n <= 6:
        pct_fs, leg_fs, pct_min = 15, 15, 4.0
    else:
        pct_fs, leg_fs = 14, 14

    fig, ax = new_figure(theme)
    wedges, _, autotexts = ax.pie(
        sizes,
        labels=None,
        autopct=(lambda p: f"{p:.1f}%" if p >= pct_min and show_pct_labels else ""),
        startangle=90,
        counterclock=False,
        colors=colors,
        wedgeprops=dict(width=0.42, edgecolor=theme.bg, linewidth=1.2),
        pctdistance=0.76,
        textprops=dict(color=txt, fontsize=pct_fs, fontweight="bold"),
    )
    for wedge, at in zip(wedges, autotexts):
        if at.get_text():
            at.set_fontsize(pct_fs)
            at.set_fontweight("bold")
            at.set_color(contrast_on_fill(wedge.get_facecolor()))

    ax.set_title(title, fontsize=30, fontweight="bold", color=txt, pad=16)
    handles = [mpatches.Patch(facecolor=colors[i], label=labels[i]) for i in range(n)]
    leg = fig.legend(
        handles=handles,
        loc="lower center",
        ncol=ncol,
        frameon=False,
        fontsize=leg_fs,
        bbox_to_anchor=(0.5, 0.02),
        columnspacing=1.0,
        handletextpad=0.45,
    )
    for t in leg.get_texts():
        t.set_color(txt)
        t.set_fontweight("bold" if n <= 6 else "normal")
    fig.subplots_adjust(left=0.04, right=0.96, top=0.88, bottom=bottom_margin)
    ax.set_aspect("equal")
    return save_figure(fig, stem, theme)


def bar_vertical(
    theme,
    stem: str,
    title: str,
    cats: list[str],
    vals: list,
    *,
    rotate: bool | None = None,
    color_index: int = 1,
):
    fig, ax = new_figure(theme)
    x = np.arange(len(cats))
    n = len(cats)
    rot = 40 if rotate is None else (40 if rotate else 0)
    if rotate is None:
        rot = 40 if n > 8 else 0

    ax.bar(x, vals, width=0.62 if n <= 8 else 0.78, color=theme.palette[color_index], edgecolor=theme.bg)
    ax.set_xticks(x)
    txt = theme_text(theme)
    ax.set_xticklabels(cats, fontsize=15 if n <= 12 else 13, color=txt, rotation=rot, ha="right" if rot else "center")
    ax.tick_params(axis="y", labelsize=15, labelcolor=txt, colors=theme.axis)
    style_axes(ax, theme)
    ax.set_title(title, fontsize=28, fontweight="bold", color=txt, pad=16)
    bottom = 0.22 if rot else 0.12
    fig.subplots_adjust(left=0.08, right=0.98, top=0.90, bottom=bottom)
    return save_figure(fig, stem, theme)


def bar_horizontal(theme, stem: str, title: str, cats: list[str], vals: list, *, pct: bool = False):
    fig, ax = new_figure(theme)
    y = np.arange(len(cats))
    ax.barh(y, vals, height=0.62, color=theme.palette[1], edgecolor=theme.bg)
    ax.set_yticks(y)
    txt = theme_text(theme)
    ax.set_yticklabels(cats, fontsize=15, color=txt)
    ax.invert_yaxis()
    ax.tick_params(axis="x", labelsize=15, labelcolor=txt, colors=theme.axis)
    if pct:
        ax.set_xlabel("占比 %", fontsize=14, color=txt)
    style_axes(ax, theme, y_grid=True)
    ax.xaxis.grid(True, color=theme.axis, alpha=0.35)
    ax.yaxis.grid(False)
    ax.set_title(title, fontsize=28, fontweight="bold", color=txt, pad=16)
    fig.subplots_adjust(left=0.22, right=0.96, top=0.90, bottom=0.10)
    return save_figure(fig, stem, theme)


def stack_percent(
    theme,
    stem: str,
    title: str,
    years: list[str],
    series: dict[str, list[float]],
    *,
    legend_ncol: int = 5,
):
    topics = list(series.keys())
    mat = np.array([series[k] for k in topics], dtype=float)
    fig, ax = new_figure(theme)
    x = np.arange(len(years))
    width = 0.62
    bottom = np.zeros(len(years))
    colors = list(theme.palette[: len(topics)])
    for i, name in enumerate(topics):
        ax.bar(
            x, mat[i], width, bottom=bottom, label=name, color=colors[i],
            edgecolor=theme.bg, linewidth=0.6,
        )
        bottom += mat[i]
    ax.set_ylim(0, 100)
    ax.set_yticks([0, 25, 50, 75, 100])
    txt = theme_text(theme)
    ax.set_yticklabels(["0%", "25%", "50%", "75%", "100%"], fontsize=15, color=txt)
    ax.set_xticks(x)
    ax.set_xticklabels(years, fontsize=17, color=txt)
    ax.tick_params(axis="y", labelcolor=txt, colors=theme.axis)
    style_axes(ax, theme)
    ax.set_title(title, fontsize=28, fontweight="bold", color=txt, pad=16)
    ncol = legend_ncol
    handles = [mpatches.Patch(facecolor=colors[i], label=topics[i]) for i in range(len(topics))]
    leg = fig.legend(handles=handles, loc="lower center", ncol=ncol, frameon=False, fontsize=14, bbox_to_anchor=(0.5, 0.02))
    for t in leg.get_texts():
        t.set_color(txt)
    bottom = 0.18 if len(topics) > 6 else 0.14
    fig.subplots_adjust(left=0.07, right=0.98, top=0.90, bottom=bottom)
    return save_figure(fig, stem, theme)


def line_multi(theme, stem: str, title: str, x_labels: list[str], series: dict[str, list], *, legend_ncol: int = 4):
    fig, ax = new_figure(theme)
    colors = list(theme.palette[: len(series)])
    for i, (name, vals) in enumerate(series.items()):
        ax.plot(x_labels, vals, marker="o", linewidth=2.8, markersize=8, label=name, color=colors[i])
    txt = theme_text(theme)
    ax.tick_params(axis="both", labelsize=15, labelcolor=txt, colors=theme.axis)
    style_axes(ax, theme)
    ax.set_title(title, fontsize=28, fontweight="bold", color=txt, pad=16)
    leg = ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.06), ncol=legend_ncol, frameon=False, fontsize=14)
    for t in leg.get_texts():
        t.set_color(txt)
    fig.subplots_adjust(left=0.08, right=0.98, top=0.88, bottom=0.18)
    return save_figure(fig, stem, theme)
