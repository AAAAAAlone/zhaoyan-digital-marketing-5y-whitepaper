#!/usr/bin/env python3
"""Export charts as light + dark PNG (background matches slide)."""
from __future__ import annotations

import json
from pathlib import Path

from pyecharts import options as opts
from pyecharts.charts import Bar, Line, Pie, Sankey

from chart_theme import DARK, LIGHT, ChartTheme

ROOT = Path(__file__).parent
CHARTS = ROOT / "assets" / "charts"
DATA = ROOT / "assets" / "data"
CHARTS.mkdir(parents=True, exist_ok=True)
DATA.mkdir(parents=True, exist_ok=True)

MSG_TYPES = [
    ("文本", 250605), ("链接/文件", 53921), ("表情", 17092),
    ("图片", 14541), ("系统", 5567), ("其他", 1534),
]
GROUPS = [
    ("5班", 83555), ("2班", 78867), ("1班", 72947), ("3班", 44813),
    ("4班", 43152), ("6班", 17251), ("7班", 1675),
]
TIERS = [
    ("A层 ≥500条", 95), ("B层 100-499", 230), ("C层 10-99", 682), ("D层 1-9条", 734),
]
YEARS = ["2021", "2022", "2023", "2024", "2025", "2026"]
YEAR_VOL = [80239, 67144, 73610, 72610, 35893, 12764]
MONTH_TOP = [
    ("2021-08", 17878), ("2023-12", 12140), ("2021-11", 11364), ("2021-07", 9452),
    ("2024-01", 9283), ("2021-09", 9251), ("2021-12", 8827), ("2022-05", 8602),
    ("2023-08", 8545), ("2024-03", 8393), ("2021-06", 8333), ("2022-03", 7991),
    ("2024-05", 7933), ("2023-10", 7743), ("2022-06", 7496),
]
QUARTER_TOP = [
    ("2021-Q3", 36581), ("2023-Q4", 26689), ("2021-Q4", 26496), ("2022-Q2", 23057),
    ("2024-Q1", 22394), ("2023-Q3", 20628), ("2022-Q1", 20260), ("2024-Q2", 19324),
    ("2024-Q3", 17382), ("2021-Q2", 17162), ("2023-Q2", 15830), ("2022-Q3", 15348),
]
HALF = [
    ("2021H1", 17162), ("2021H2", 63077), ("2022H1", 43317), ("2022H2", 23827),
    ("2023H1", 26293), ("2023H2", 47317), ("2024H1", 41718), ("2024H2", 30892),
    ("2025H1", 19232), ("2025H2", 16661), ("2026H1", 12764),
]
L1_TOPICS = [
    ("内容·品牌", 22833), ("线索·销售", 14529), ("SEO·搜索", 13492),
    ("课程·活动", 10981), ("投放·广告", 9766), ("工具·SaaS", 9646),
    ("招聘·合作", 5325), ("私域·企微", 4189), ("出海", 2981), ("GEO·AI", 2569),
]
L1_YEAR = {
    "2021": {"线索": 3343, "内容": 3100, "SEO": 2978, "工具": 2367, "投放": 1834,
             "课程": 1536, "私域": 1146, "招聘": 732, "出海": 229, "GEO": 7},
    "2022": {"线索": 3550, "内容": 3211, "SEO": 2214, "工具": 1931, "投放": 1705,
             "课程": 1544, "私域": 589, "招聘": 607, "出海": 322, "GEO": 3},
    "2023": {"线索": 3558, "内容": 3659, "SEO": 2106, "工具": 2445, "投放": 1723,
             "课程": 2132, "私域": 581, "招聘": 680, "出海": 372, "GEO": 295},
    "2024": {"线索": 2658, "内容": 3647, "SEO": 1909, "工具": 1898, "投放": 1735,
             "课程": 1565, "私域": 411, "招聘": 650, "出海": 578, "GEO": 246},
    "2025": {"线索": 1102, "内容": 1971, "SEO": 1218, "工具": 1022, "投放": 1035,
             "课程": 827, "私域": 175, "招聘": 345, "出海": 432, "GEO": 697},
    "2026": {"线索": 287, "内容": 578, "SEO": 501, "工具": 554, "投放": 321,
             "课程": 189, "私域": 23, "招聘": 74, "出海": 120, "GEO": 622},
}
TOPICS_ORDER = ["线索", "SEO", "内容", "投放", "工具", "课程", "私域", "招聘", "出海", "GEO"]
INDUSTRIES = [
    ("SaaS/软件", 6549), ("制造/工业", 2460), ("营销/传媒", 2415), ("教育/培训", 2090),
    ("出海/外贸", 1669), ("人力/招聘", 1423), ("电商/零售", 1197), ("医疗/医药", 1148),
]
PAIN = [
    ("SEO收录/排名", 2045), ("GEO/AI焦虑", 1516), ("官网/落地页", 1416),
    ("销售市场互怼", 960), ("岗位/职业", 666), ("老板/战略", 642),
]
PAIN_YEAR = {
    "2021": {"SEO": 442, "官网": 565, "销售": 149, "GEO": 0},
    "2022": {"SEO": 427, "官网": 300, "销售": 276, "GEO": 0},
    "2023": {"SEO": 399, "销售": 277, "官网": 273, "GEO": 0},
    "2024": {"SEO": 467, "销售": 156, "官网": 155, "GEO": 0},
    "2025": {"SEO": 244, "GEO": 741, "官网": 74, "sales": 81},
    "2026": {"SEO": 66, "GEO": 735, "官网": 49, "sales": 21},
}
# fix key
for y in PAIN_YEAR:
    if "sales" in PAIN_YEAR[y]:
        PAIN_YEAR[y]["销售"] = PAIN_YEAR[y].pop("sales")

SPEAKERS = [
    ("赵岩", 52960), ("Zhaoy07331", 34881), ("始熊君", 27502), ("加玮", 10198),
    ("司司", 7595), ("邹叔Jerry", 5924), ("雍熙-Paul", 5662), ("R-市场", 4275),
    ("木辰", 3651), ("牛磊", 3639),
]
HOURS = [701, 102, 28, 15, 24, 26, 57, 355, 2957, 22659, 50269, 45642,
         15548, 14225, 29732, 35379, 35568, 34145, 22314, 11626, 7336, 6184, 4708, 2660]
SILENCE = [("1班", 37.3), ("2班", 31.6), ("3班", 31.2), ("4班", 27.5),
           ("5班", 37.1), ("6班", 65.3), ("7班", 81.3)]
ZHAO_YEAR = [6812, 10530, 12849, 12025, 7510, 3234]
PLATFORM = [
    ("百度", 5629), ("微信", 3468), ("官网", 3145), ("抖音", 2209),
    ("直播", 2344), ("Google", 1512), ("小红书", 1439), ("GEO", 450), ("ChatGPT", 564),
]


def _axis(t: ChartTheme) -> opts.AxisOpts:
    return opts.AxisOpts(
        axislabel_opts=opts.LabelOpts(color=t.text),
        splitline_opts=opts.SplitLineOpts(is_show=True, linestyle_opts=opts.LineStyleOpts(color=t.grid)),
    )


def _pie(t: ChartTheme, title: str, data: list[tuple[str, int]], radius=None) -> Pie:
    radius = radius or ["42%", "68%"]
    return (
        Pie(init_opts=opts.InitOpts(width="1920px", height="1080px", bg_color=t.bg))
        .add(
            "",
            data,
            radius=radius,
            center=["40%", "55%"],
            label_opts=opts.LabelOpts(formatter="{b}\n{d}%", color=t.text, font_size=14),
        )
        .set_colors(list(t.palette))
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title=title, pos_left="center",
                title_textstyle_opts=opts.TextStyleOpts(color=t.text, font_size=20),
            ),
            legend_opts=opts.LegendOpts(
                pos_right="5%", pos_top="middle",
                textstyle_opts=opts.TextStyleOpts(color=t.text),
            ),
        )
    )


def _bar_h(t: ChartTheme, title: str, names: list, vals: list, horizontal=True) -> Bar:
    b = Bar(init_opts=opts.InitOpts(width="1920px", height="1080px", bg_color=t.bg))
    if horizontal:
        b.add_xaxis(vals).add_yaxis("", names, label_opts=opts.LabelOpts(position="right", color=t.text))
        b.reversal_axis()
    else:
        b.add_xaxis(names).add_yaxis("", vals, label_opts=opts.LabelOpts(position="top", color=t.text))
    return b.set_colors([t.palette[1]]).set_global_opts(
        title_opts=opts.TitleOpts(title=title, title_textstyle_opts=opts.TextStyleOpts(color=t.text, font_size=20)),
        xaxis_opts=_axis(t),
        yaxis_opts=_axis(t),
    )


def _stack_percent(t: ChartTheme, title: str, years: list, series: dict[str, list[float]]) -> Bar:
    b = Bar(init_opts=opts.InitOpts(width="1920px", height="1080px", bg_color=t.bg))
    b.add_xaxis(years)
    for name, vals in series.items():
        b.add_yaxis(name, vals, stack="total", category_gap="30%", label_opts=opts.LabelOpts(is_show=False))
    return (
        b.set_colors(list(t.palette))
        .set_global_opts(
            title_opts=opts.TitleOpts(title=title, title_textstyle_opts=opts.TextStyleOpts(color=t.text, font_size=20)),
            legend_opts=opts.LegendOpts(pos_top="8%", textstyle_opts=opts.TextStyleOpts(color=t.text)),
            xaxis_opts=opts.AxisOpts(max_=100, axislabel_opts=opts.LabelOpts(formatter="{value}%", color=t.text)),
            yaxis_opts=_axis(t),
        )
    )


def l1_share_series() -> dict[str, list[float]]:
    out: dict[str, list[float]] = {k: [] for k in TOPICS_ORDER}
    for y in YEARS:
        d = L1_YEAR[y]
        total = sum(d.values()) or 1
        for k in TOPICS_ORDER:
            out[k].append(round(d.get(k, 0) / total * 100, 2))
    return out


def sankey_share(t: ChartTheme) -> Sankey:
    nodes, links = [], []
    for y in YEARS:
        ys = y[-2:]
        d = L1_YEAR[y]
        total = sum(d.values()) or 1
        for topic in TOPICS_ORDER:
            pct = d.get(topic, 0) / total * 100
            nodes.append({"name": f"{ys}·{topic}", "value": round(pct, 2)})
    for topic in TOPICS_ORDER:
        for i in range(len(YEARS) - 1):
            y0, y1 = YEARS[i][-2:], YEARS[i + 1][-2:]
            d1 = L1_YEAR[YEARS[i + 1]]
            total1 = sum(d1.values()) or 1
            v = round(d1.get(topic, 0) / total1 * 100, 2)
            if v > 0:
                links.append({"source": f"{y0}·{topic}", "target": f"{y1}·{topic}", "value": v})
    return (
        Sankey(init_opts=opts.InitOpts(width="1920px", height="1080px", bg_color=t.bg))
        .add(
            "", nodes, links,
            linestyle_opt=opts.LineStyleOpts(opacity=0.35, curve=0.5, color="source"),
            label_opts=opts.LabelOpts(color=t.text, font_size=11),
            node_gap=14, node_width=22,
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title="议题结构五年迁移",
                title_textstyle_opts=opts.TextStyleOpts(color=t.text, font_size=20),
            ),
        )
    )


def pain_share_series() -> dict[str, list[float]]:
    keys = ["SEO", "GEO", "官网", "销售"]
    out = {k: [] for k in keys}
    for y in YEARS:
        d = PAIN_YEAR.get(y, {})
        total = sum(d.values()) or 1
        for k in keys:
            out[k].append(round(d.get(k, 0) / total * 100, 2))
    return out


def build_charts(t: ChartTheme) -> list[tuple[str, object]]:
    charts = [
        ("c01-msg-type", _pie(t, "消息类型构成", MSG_TYPES)),
        ("c02-groups", _pie(t, "各班级消息量", GROUPS)),
        ("c03-speaker-tier", _pie(t, "发言者层级", TIERS, ["45%", "70%"])),
        ("c04-year-volume", _bar_h(t, "年度消息量", YEARS, YEAR_VOL, False)),
        ("c05-month-top15", _bar_h(t, "月度 Top15", [m for m, _ in MONTH_TOP], [v for _, v in MONTH_TOP], False)),
        ("c06-quarter-top12", _bar_h(t, "季度 Top12", [q for q, _ in QUARTER_TOP], [v for _, v in QUARTER_TOP], False)),
        ("c07-halfyear", _bar_h(t, "半年度消息量", [h for h, _ in HALF], [v for _, v in HALF], False)),
        ("c08-l1-share-year", _stack_percent(t, "营销 L1 议题占比", YEARS, l1_share_series())),
        ("c09-l1-sankey-share", sankey_share(t)),
        ("c11-l1-all", _pie(t, "营销 L1 议题命中", L1_TOPICS)),
        ("c12-industry", _pie(t, "行业提及 Top8", INDUSTRIES)),
        ("c14-pain", _pie(t, "痛点场景 Top6", PAIN)),
        ("c15-pain-share-year", _stack_percent(t, "痛点结构占比", YEARS, pain_share_series())),
        ("c17-speakers-top10", _bar_h(t, "发言人 Top10", [n for n, _ in SPEAKERS], [v for _, v in SPEAKERS])),
        ("c18-hours", _bar_h(t, "24 小时分布", [str(i) for i in range(24)], HOURS, False)),
        ("c19-silence-by-class", _bar_h(t, "各班沉默率", [c for c, _ in SILENCE], [v for _, v in SILENCE], False)),
        ("c21-platform-l2", _bar_h(t, "平台/渠道词", [n for n, _ in PLATFORM], [v for _, v in PLATFORM], False)),
    ]
    line_l1 = Line(init_opts=opts.InitOpts(width="1920px", height="1080px", bg_color=t.bg)).add_xaxis(YEARS)
    for topic in ["线索", "SEO", "GEO"]:
        line_l1.add_yaxis(topic, [L1_YEAR[y].get(topic, 0) for y in YEARS], is_smooth=True)
    charts.append(("c10-l1-trend-abs", line_l1.set_colors(list(t.palette[:3])).set_global_opts(
        title_opts=opts.TitleOpts(title="核心议题命中 × 年", title_textstyle_opts=opts.TextStyleOpts(color=t.text, font_size=20)),
        xaxis_opts=_axis(t), yaxis_opts=_axis(t),
    )))

    line_pain = Line(init_opts=opts.InitOpts(width="1920px", height="1080px", bg_color=t.bg)).add_xaxis(YEARS)
    for k in ["SEO", "GEO", "销售"]:
        line_pain.add_yaxis(k, [PAIN_YEAR[y].get(k, 0) for y in YEARS], is_smooth=True)
    charts.append(("c16-pain-trend", line_pain.set_colors(list(t.palette[:3])).set_global_opts(
        title_opts=opts.TitleOpts(title="痛点命中 × 年", title_textstyle_opts=opts.TextStyleOpts(color=t.text, font_size=20)),
        xaxis_opts=_axis(t), yaxis_opts=_axis(t),
    )))

    line_z = Line(init_opts=opts.InitOpts(width="1920px", height="1080px", bg_color=t.bg)).add_xaxis(YEARS)
    line_z.add_yaxis("赵岩", ZHAO_YEAR, is_smooth=True)
    charts.append(("c20-zhao-by-year", line_z.set_colors([t.palette[1]]).set_global_opts(
        title_opts=opts.TitleOpts(title="赵岩年度发言量", title_textstyle_opts=opts.TextStyleOpts(color=t.text, font_size=20)),
        xaxis_opts=_axis(t), yaxis_opts=_axis(t),
    )))

    charts.append(("c22-geo-vs-lead-2026", _bar_h(t, "2026 GEO vs 线索", ["GEO·AI", "线索·销售"], [622, 287], False)))

    exp = json.loads((ROOT / "expand-stats.json").read_text(encoding="utf-8"))
    ind_map = {
        "SaaS/企业服务/软件": "SaaS", "制造/工业/工业互联网": "制造",
        "营销/广告/传媒/公关": "营销", "教育/培训": "教育", "出海/外贸": "出海",
    }
    ind_keys = list(ind_map.values())
    ind_series = {k: [] for k in ind_keys}
    for y in YEARS:
        row = {ind_map.get(n, n): v for n, v in exp["industries_by_year"].get(y, []) if n in ind_map}
        total = sum(row.values()) or 1
        for k in ind_keys:
            ind_series[k].append(round(row.get(k, 0) / total * 100, 2))
    charts.append(("c13-industry-share-year", _stack_percent(t, "行业提及占比", YEARS, ind_series)))
    return charts


def export_png(chart, stem: str, theme: ChartTheme) -> None:
    html = CHARTS / f"{stem}-{theme.name}.html"
    png = CHARTS / f"{stem}-{theme.name}.png"
    alias = CHARTS / f"{stem}.png"
    chart.render(str(html))
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={"width": 1920, "height": 1080})
            page.goto(html.resolve().as_uri())
            page.wait_for_timeout(1000)
            page.screenshot(path=str(png), full_page=False)
            browser.close()
        if theme.name == "light":
            alias.write_bytes(png.read_bytes())
        print("png", png.name)
    except Exception as e:
        print("html only", png.name, e)


def save_json(name: str, obj) -> None:
    (DATA / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def main():
    stems = []
    for theme in (LIGHT, DARK):
        for stem, chart in build_charts(theme):
            export_png(chart, stem, theme)
            if stem not in stems:
                stems.append(stem)

    save_json("manifest.json", {
        "total_messages": 342260,
        "charts": stems,
        "themes": ["light", "dark"],
        "l1_year": L1_YEAR,
    })
    save_json("msg-types.json", MSG_TYPES)
    save_json("l1-topics.json", L1_TOPICS)
    print("done", len(stems), "charts × 2 themes")


if __name__ == "__main__":
    main()
