#!/usr/bin/env python3
"""
c09 · 议题结构五年迁移（桑基图）

数据与原先 pyecharts 版一致：每年 10 个 L1 议题占比，同议题跨年连线。
用 Plotly 导出，避免 ECharts 桑基挤在画布左侧的问题。
"""
from __future__ import annotations

import sys
from pathlib import Path

import plotly.graph_objects as go

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from chart_theme import DARK, LIGHT, ChartTheme  # noqa: E402
from charts.data import TOPICS_ORDER, YEARS, l1_year  # noqa: E402
from charts.common import OUT, verify_png  # noqa: E402

TITLE = "议题结构五年迁移"
W, H = 1920, 1080


def _build_graph(theme: ChartTheme):
    l1 = l1_year()
    node_names: list[str] = []
    node_colors: list[str] = []
    palette = list(theme.palette)

    for y in YEARS:
        ys = y[-2:]
        d = l1[y]
        total = sum(d.values()) or 1
        for i, topic in enumerate(TOPICS_ORDER):
            node_names.append(f"{ys}·{topic}")
            node_colors.append(palette[i % len(palette)])

    name_to_idx = {n: i for i, n in enumerate(node_names)}
    sources, targets, values = [], [], []
    for topic in TOPICS_ORDER:
        for i in range(len(YEARS) - 1):
            y0, y1 = YEARS[i][-2:], YEARS[i + 1][-2:]
            src, tgt = f"{y0}·{topic}", f"{y1}·{topic}"
            d1 = l1[YEARS[i + 1]]
            total1 = sum(d1.values()) or 1
            v = d1.get(topic, 0) / total1 * 100
            if v > 0:
                sources.append(name_to_idx[src])
                targets.append(name_to_idx[tgt])
                values.append(round(v, 2))

    link_colors = []
    for s in sources:
        c = node_colors[s]
        if c.startswith("#") and len(c) == 7:
            r, g, b = int(c[1:3], 16), int(c[3:5], 16), int(c[5:7], 16)
            link_colors.append(f"rgba({r},{g},{b},0.35)")
        else:
            link_colors.append("rgba(128,128,128,0.35)")

    sankey = go.Sankey(
        arrangement="snap",
        valueformat=".1f",
        valuesuffix="%",
        node=dict(
            pad=14,
            thickness=22,
            line=dict(color=theme.bg, width=1),
            label=node_names,
            color=node_colors,
            hovertemplate="%{label}<br>%{value:.1f}%<extra></extra>",
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            color=link_colors,
            hovertemplate="%{source.label} → %{target.label}<br>%{value:.1f}%<extra></extra>",
        ),
    )
    fig = go.Figure(data=[sankey])
    fig.update_layout(
        title=dict(text=TITLE, x=0.5, xanchor="center", font=dict(size=28, color=theme.text, family="PingFang SC, Hiragino Sans GB, sans-serif")),
        width=W,
        height=H,
        paper_bgcolor=theme.bg,
        plot_bgcolor=theme.bg,
        font=dict(size=13, color=theme.text, family="PingFang SC, Hiragino Sans GB, sans-serif"),
        margin=dict(l=24, r=24, t=72, b=24),
    )
    return fig


def export_png(theme: ChartTheme, stem: str) -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    png = OUT / f"{stem}-{theme.name}.png"
    fig = _build_graph(theme)
    fig.write_image(str(png), scale=1)
    if theme.name == "light":
        (OUT / f"{stem}.png").write_bytes(png.read_bytes())
    verify_png(png, min_bytes=40_000, min_std=15)
    return png


def main() -> None:
    for theme in (LIGHT, DARK):
        p = export_png(theme, "c09-l1-sankey-share")
        print("ok", p, p.stat().st_size)


if __name__ == "__main__":
    main()
