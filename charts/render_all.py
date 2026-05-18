#!/usr/bin/env python3
"""
重绘全部图表（除 c08 已由 render_c08.py 负责）。

- 数据与图类型与 export_all_charts.py 一致
- Matplotlib：饼图、柱图、折线、堆叠占比
- 桑基 c09：pyecharts + 本地 echarts + Playwright 等画布就绪

不写入 MD / PPT。
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from chart_theme import DARK, LIGHT  # noqa: E402
from charts import data as D  # noqa: E402
from charts.common import (  # noqa: E402
    bar_horizontal,
    bar_vertical,
    line_multi,
    pie_donut,
    stack_percent,
    verify_png,
)


def render_one(theme, stem: str, fn) -> None:
    p = fn(theme)
    verify_png(p)
    print("ok", p.name, p.stat().st_size)


def render_matplotlib_charts(theme) -> None:
    render_one(theme, "c01", lambda t: pie_donut(t, "c01-msg-type", "消息类型构成", D.MSG_TYPES, legend_ncol=3))
    render_one(theme, "c02", lambda t: pie_donut(t, "c02-groups", "各班级消息量", D.GROUPS, legend_ncol=4))
    render_one(theme, "c03", lambda t: pie_donut(t, "c03-speaker-tier", "发言者层级", D.TIERS, legend_ncol=2, bottom_margin=0.12))
    render_one(
        theme,
        "c04",
        lambda t: bar_vertical(t, "c04-year-volume", "年度消息量", D.YEARS, D.YEAR_VOL),
    )
    render_one(
        theme,
        "c05",
        lambda t: bar_vertical(
            t, "c05-month-top15", "月度 Top15",
            [m for m, _ in D.MONTH_TOP], [v for _, v in D.MONTH_TOP], rotate=True,
        ),
    )
    render_one(
        theme,
        "c06",
        lambda t: bar_vertical(
            t, "c06-quarter-top12", "季度 Top12",
            [q for q, _ in D.QUARTER_TOP], [v for _, v in D.QUARTER_TOP], rotate=True,
        ),
    )
    render_one(
        theme,
        "c07",
        lambda t: bar_vertical(
            t, "c07-halfyear", "半年度消息量",
            [h for h, _ in D.HALF], [v for _, v in D.HALF], rotate=True,
        ),
    )
    render_one(
        theme,
        "c11",
        lambda t: pie_donut(
            t, "c11-l1-all", "营销 L1 议题命中", D.L1_TOPICS,
            legend_ncol=5, show_pct_labels=True, bottom_margin=0.16, pct_min=5.0,
        ),
    )
    render_one(theme, "c12", lambda t: pie_donut(t, "c12-industry", "行业提及 Top8", D.INDUSTRIES, legend_ncol=4))
    render_one(theme, "c14", lambda t: pie_donut(t, "c14-pain", "痛点场景 Top6", D.PAIN, legend_ncol=3))
    render_one(
        theme,
        "c15",
        lambda t: stack_percent(t, "c15-pain-share-year", "痛点结构占比", D.YEARS, D.pain_share_series(), legend_ncol=4),
    )
    render_one(
        theme,
        "c13",
        lambda t: stack_percent(
            t, "c13-industry-share-year", "行业提及占比", D.YEARS, D.industry_share_series(), legend_ncol=5,
        ),
    )
    render_one(
        theme,
        "c17",
        lambda t: bar_horizontal(
            t, "c17-speakers-top10", "发言人 Top10",
            [n for n, _ in D.SPEAKERS], [v for _, v in D.SPEAKERS],
        ),
    )
    render_one(
        theme,
        "c18",
        lambda t: bar_vertical(
            t, "c18-hours", "24 小时分布",
            [str(i) for i in range(24)], D.HOURS, rotate=True,
        ),
    )
    render_one(
        theme,
        "c19",
        lambda t: bar_horizontal(
            t, "c19-silence-by-class", "各班沉默率 %",
            [c for c, _ in D.SILENCE], [v for _, v in D.SILENCE], pct=True,
        ),
    )
    render_one(
        theme,
        "c21",
        lambda t: bar_horizontal(
            t, "c21-platform-l2", "平台/渠道词",
            [n for n, _ in D.PLATFORM], [v for _, v in D.PLATFORM],
        ),
    )
    l1 = D.l1_year()
    render_one(
        theme,
        "c10",
        lambda t: line_multi(
            t, "c10-l1-trend-abs", "核心议题命中 × 年", D.YEARS,
            {k: [l1[y].get(k, 0) for y in D.YEARS] for k in ["线索", "SEO", "GEO"]},
        ),
    )
    render_one(
        theme,
        "c16",
        lambda t: line_multi(
            t, "c16-pain-trend", "痛点命中 × 年", D.YEARS,
            {k: [D.PAIN_YEAR[y].get(k, 0) for y in D.YEARS] for k in ["SEO", "GEO", "销售"]},
        ),
    )
    render_one(
        theme,
        "c20",
        lambda t: line_multi(t, "c20-zhao-by-year", "赵岩年度发言量", D.YEARS, {"赵岩": D.ZHAO_YEAR}, legend_ncol=1),
    )
    render_one(
        theme,
        "c22",
        lambda t: bar_vertical(t, "c22-geo-vs-lead-2026", "2026 GEO vs 线索", ["GEO·AI", "线索·销售"], [622, 287]),
    )


def main() -> None:
    from charts.render_c08 import main as render_c08  # noqa: WPS433
    from charts.render_c09_sankey import main as render_c09  # noqa: WPS433

    for theme in (LIGHT, DARK):
        render_matplotlib_charts(theme)
    render_c08()
    render_c09()
    print("done — 22 charts × light/dark (+ c08 verified)")


if __name__ == "__main__":
    main()
