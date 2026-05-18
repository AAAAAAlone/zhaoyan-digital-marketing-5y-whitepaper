#!/usr/bin/env python3
"""Build ~52-page magazine PPT: conclusion-first titles, section kicker, chart PNGs."""
from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).parent
TEMPLATE = Path("/Users/jiaweiwang/.codex/skills/magazine-web-ppt/assets/template.html")
OUT = ROOT / "ppt" / "index.html"
IMG = "images"

# section=kicker(白皮书结构), title=主结论, lead=副说明, img=chart, theme, kind, rows
SLIDES: list[dict] = [
    {"pg": "01/52", "section": "封面", "title": "342,260 条消息构成一部 ToB 营销活体案例库", "lead": "赵岩的数字营销实战群 · 2021—2026", "theme": "hero dark", "kind": "hero"},
    {"pg": "02/52", "section": "读图说明", "title": "结构变化看占比（每年 100%），体量看绝对值", "lead": "桑基图列高一致；带宽=议题占比迁移", "theme": "light", "kind": "text"},
    {"pg": "03/52", "section": "Act I · 组织全景", "title": "第一篇", "lead": "消息 · 班级 · 参与者 · 节律", "theme": "hero light", "kind": "hero"},
    {"pg": "04/52", "section": "第一篇 · 组织全景", "title": "文本消息占全群 73.2%（250,605 条）", "img": "c01-msg-type.png", "theme": "light", "kind": "chart"},
    {"pg": "05/52", "section": "第一篇 · 组织全景", "title": "5/2/1 班承载约 68% 消息量", "lead": "5班 83,555 · 2班 78,867 · 1班 72,947", "img": "c02-groups.png", "theme": "dark", "kind": "chart"},
    {"pg": "06/52", "section": "第一篇 · 组织全景", "title": "7 班沉默率 81.3%，不宜与 1—5 班比活跃", "img": "c19-silence-by-class.png", "theme": "dark", "kind": "chart"},
    {"pg": "07/52", "section": "第一篇 · 组织全景", "title": "42% 发言者仅发 1—9 条（734 人）", "lead": "围观层大于核心层人数", "img": "c03-speaker-tier.png", "theme": "light", "kind": "chart"},
    {"pg": "08/52", "section": "第一篇 · 活跃节律", "title": "10—11 时为发言高峰（合计约 9.6 万条）", "img": "c18-hours.png", "theme": "light", "kind": "chart"},
    {"pg": "09/52", "section": "第一篇 · 组织数据表", "title": "1,742 发言人 · 1,630 活跃日 · 链接占 15.8%", "theme": "light", "kind": "table", "rows": [
        ("总消息", "342,260"), ("文本", "250,605 (73.2%)"), ("链接/文件", "53,921"),
        ("A层发言者", "95 人 ≥500条"), ("Top10 发言", "约 50%"), ("7班消息", "1,675"),
    ]},
    {"pg": "10/52", "section": "Act II · 五年演变", "title": "第二篇", "lead": "体量 · 议题结构 · 渠道", "theme": "hero dark", "kind": "hero"},
    {"pg": "11/52", "section": "第二篇 · 年度体量", "title": "年消息量 2021 峰值 8.0 万，2025 回落至 3.6 万", "img": "c04-year-volume.png", "theme": "light", "kind": "chart"},
    {"pg": "12/52", "section": "第二篇 · 月度", "title": "单月峰值 2021-08：17,878 条", "img": "c05-month-top15.png", "theme": "light", "kind": "chart"},
    {"pg": "13/52", "section": "第二篇 · 季度", "title": "最热季度 2021-Q3：36,581 条", "img": "c06-quarter-top12.png", "theme": "dark", "kind": "chart"},
    {"pg": "14/52", "section": "第二篇 · 半年度", "title": "2021H2、2023H2 为两个半年爆发段", "img": "c07-halfyear.png", "theme": "dark", "kind": "chart"},
    {"pg": "15/52", "section": "第二篇 · 议题占比", "title": "2026 年 GEO 占营销议题 19.1%，结构首超线索（8.8%）", "lead": "100% 堆叠柱 · 每年十类 L1 合计", "img": "c08-l1-share-year.png", "theme": "light", "kind": "chart"},
    {"pg": "16/52", "section": "第二篇 · 议题结构", "title": "议题结构五年迁移：GEO 从可忽略到近两成", "lead": "桑基：每年列高=100%，只看占比带宽", "img": "c09-l1-sankey-share.png", "theme": "dark", "kind": "chart"},
    {"pg": "17/52", "section": "第二篇 · 议题绝对值", "title": "线索/SEO 命中随群总量下降，2026 GEO 逆势抬升", "img": "c10-l1-trend-abs.png", "theme": "light", "kind": "chart"},
    {"pg": "18/52", "section": "第二篇 · 渠道", "title": "百度提及 5,629 条；GEO 标签 2026 年 265 条", "img": "c21-platform-l2.png", "theme": "light", "kind": "chart"},
    {"pg": "19/52", "section": "第二篇 · 2026 结构", "title": "2026 年 GEO-AI 命中 622 条，约为线索 287 条的 2.2 倍", "img": "c22-geo-vs-lead-2026.png", "theme": "dark", "kind": "chart"},
    {"pg": "20/52", "section": "Act III · 核心数据", "title": "行业 · 痛点 · 议题", "lead": "前置统计盘", "theme": "hero light", "kind": "hero"},
    {"pg": "21/52", "section": "核心数据 · 02 行业提及热度", "title": "6,549 条消息提及 SaaS/企业服务，为行业第一", "img": "c12-industry.png", "theme": "light", "kind": "chart"},
    {"pg": "22/52", "section": "核心数据 · 02 行业占比", "title": "出海提及占比在 2025—2026 逆势升高", "img": "c13-industry-share-year.png", "theme": "light", "kind": "chart"},
    {"pg": "23/52", "section": "核心数据 · 03 痛点场景", "title": "2,045 条命中 SEO/收录类痛点，为五年最高", "img": "c14-pain.png", "theme": "dark", "kind": "chart"},
    {"pg": "24/52", "section": "核心数据 · 03 痛点占比", "title": "2025 起 GEO/AI 焦虑占痛点结构第一", "img": "c15-pain-share-year.png", "theme": "dark", "kind": "chart"},
    {"pg": "25/52", "section": "核心数据 · 03 痛点趋势", "title": "销售互怼痛点 2022—2023 最集中", "img": "c16-pain-trend.png", "theme": "light", "kind": "chart"},
    {"pg": "26/52", "section": "核心数据 · 04 L1 议题", "title": "内容品牌 L1 命中 22,833；线索 14,529 为获客主轴", "img": "c11-l1-all.png", "theme": "light", "kind": "chart"},
    {"pg": "27/52", "section": "Act IV · 参与者", "title": "第三篇", "lead": "赵岩主轴 · Top30 过半", "theme": "hero dark", "kind": "hero"},
    {"pg": "28/52", "section": "第三篇 · 参与者", "title": "赵岩 52,960 条（15.5%）；Zhaoy07331、始熊君分列二三", "img": "c17-speakers-top10.png", "theme": "light", "kind": "chart"},
    {"pg": "29/52", "section": "第三篇 · 赵岩", "title": "赵岩发言 2023 年峰值 12,849 条/年", "img": "c20-zhao-by-year.png", "theme": "light", "kind": "chart"},
    {"pg": "30/52", "section": "Act V · 讨论方向", "title": "第四篇", "lead": "场景 + 建议摘要（无原话堆砌）", "theme": "hero light", "kind": "hero"},
    {"pg": "31/52", "section": "第四篇 · 4.0 议题矩阵", "title": "线索 14,529 · 内容 22,833 · SEO 13,492 为 L1 前三", "lead": "话题段 13,187（>30min·≥2人）与消息 L1 口径不同", "theme": "light", "kind": "text"},
    {"pg": "32/52", "section": "第四篇 · 4.0 议题矩阵", "title": "L1 方向 × 高峰年 × 关联痛点（表）", "theme": "light", "kind": "table", "rows": [
        ("线索·销售", "14,529 · 峰2022-23"), ("内容·品牌", "22,833 · 峰2023-24"),
        ("SEO·搜索", "13,492 · 峰2021-22"), ("投放·广告", "9,766 · 峰2021-23"),
        ("GEO·AI", "2,569 · 峰2026"), ("私域·企微", "4,189 · 峰2021"),
    ]},
    {"pg": "33/52", "section": "第四篇 · 4.1 线索", "title": "超过 14,529 条消息讨论线索与销售协同", "lead": "2022—2023 各约 3,550；5班线索 L1 最高", "theme": "light", "kind": "text"},
    {"pg": "34/52", "section": "第四篇 · 4.1 线索", "title": "群内稳定建议：先定义线索，再用销售行为反推质量", "theme": "dark", "kind": "bullets", "rows": [
        "对齐意愿强/质量高维度，再谈工具", "销售嘴上说差却不放公海→问题或在转化",
        "直播/会展慢变量，SEM 短变量，KPI 分层", "非标制造慎信息流，重 SEO+线下",
    ]},
    {"pg": "35/52", "section": "第四篇 · 4.2 投放", "title": "9,766 条讨论投放；百度 L2 命中 5,629", "lead": "痛点「投放成本」422 · oCPC 高价频发", "theme": "light", "kind": "bullets", "rows": [
        "加玮路径：日线索→SEM→SEO→内容→品专（可跳过）", "落地页：官网完整度 vs 基木鱼单页",
        "缩词包、长尾、检查词路；窄人群慎信息流",
    ]},
    {"pg": "36/52", "section": "第四篇 · 4.3 SEO", "title": "13,492 条 SEO 议题；痛点 SEO 收录 2,045 为五年第一", "theme": "dark", "kind": "bullets", "rows": [
        "先确认静态 HTML 可见，再谈 TDK/内链", "长尾看词量+行业场景；工具只看趋势",
        "官网=SEO载体=SEM落地页=GEO权威源",
    ]},
    {"pg": "37/52", "section": "第四篇 · 4.4 GEO", "title": "2026 年 GEO L1 622 条，已超过同年线索 287 条", "lead": "7班 GEO 浓度约 8%；痛点 GEO 焦虑 2025+登顶", "theme": "light", "kind": "bullets", "rows": [
        "GEO 绑定可被引用内容+官网结构，非单独渠道", "AI 辅助草稿；判断仍靠业务与数据",
        "赵岩 2023 已埋「还会用搜索引擎吗」种子",
    ]},
    {"pg": "38/52", "section": "第四篇 · 4.5 出海", "title": "2,981 条出海议题；2024 单年命中 578 为峰", "theme": "dark", "kind": "bullets", "rows": [
        "与 Google L2（1,512）高度重叠", "官网本地化=价值主张+合规", "英语与 CRM 经验常为硬门槛",
    ]},
    {"pg": "39/52", "section": "第四篇 · 4.6 私域", "title": "私域 L1 峰在 2021（1,146），2026 仅 23 条", "theme": "light", "kind": "bullets", "rows": [
        "大群按行业×岗位分层；企微低频高价值", "私域不能替代大搜/SEO 验证", "行业 SOP 可复制 > 功能堆叠",
    ]},
    {"pg": "40/52", "section": "第四篇 · 4.7 内容", "title": "内容 L1 22,833 最高（含口语宽命中）", "lead": "直播 L2 2,344 · 抖音 2,209 · 小红书 2024 抬头", "theme": "light", "kind": "bullets", "rows": [
        "B2B 视频无成熟爆款公式", "品牌/获客/转化三层 KPI 勿混", "员工风貌有时优于 CEO IP",
    ]},
    {"pg": "41/52", "section": "第四篇 · 4.8 工具", "title": "9,646 条工具议题；2023 命中 2,445 为峰", "theme": "dark", "kind": "bullets", "rows": [
        "先流程后系统；字段进 CRM 再谈 MA", "致趣/销售易等多为语境非评测", "2026 Agent 与 GEO 同属人效焦虑",
    ]},
    {"pg": "42/52", "section": "第四篇 · 4.9 招聘", "title": "5,325 条招聘/合作；群是信任背书下的对接场", "theme": "light", "kind": "text"},
    {"pg": "43/52", "section": "第四篇 · 4.10 课程", "title": "10,981 条课程/活动；2023 与多班扩容同步", "lead": "活动促活，方法论仍在线索/SEO 段", "theme": "light", "kind": "text"},
    {"pg": "44/52", "section": "第四篇 · 4.11—4.12", "title": "短期 SEM 验证 · 长期 SEO/内容/私域 · 2026+ GEO 回到官网", "theme": "dark", "kind": "table", "rows": [
        ("SaaS×线索", "先定义线索与字段"), ("制造×投放", "慎信息流，重SEO+线下"),
        ("出海×GEO", "本地化+可引用内容"), ("市场vs销售", "行为数据减甩锅"),
    ]},
    {"pg": "45/52", "section": "Act VI · 原话", "title": "第六篇", "lead": "完整引文支撑可信度", "theme": "hero dark", "kind": "hero"},
    {"pg": "46/52", "section": "第六篇 · 投放", "title": "「先看日线索增长 → 验证 SEM → 再 SEO」", "lead": "加玮 · 2班 · 2023-12-16", "theme": "dark", "kind": "quote"},
    {"pg": "47/52", "section": "第六篇 · 线索", "title": "「销售跟进行为可反推线索质量」", "lead": "牛磊 · 5班 · 2023-06", "theme": "dark", "kind": "quote"},
    {"pg": "48/52", "section": "第六篇 · 工具", "title": "「营销软件价值在行业 SOP」", "lead": "赵岩 · 1班 · 2023-05", "theme": "light", "kind": "quote"},
    {"pg": "49/52", "section": "第六篇 · SEO", "title": "「基木鱼承载不了品牌与 SEO 自然流量」", "lead": "雍熙-Paul · 2班 · 2021-05", "theme": "light", "kind": "quote"},
    {"pg": "50/52", "section": "第六篇 · 内容", "title": "「直播要分层：品牌层 / 获客层 / 转化层」", "lead": "姚兆兆 · 1班 · 2021-08", "theme": "light", "kind": "quote"},
    {"pg": "51/52", "section": "第六篇 · GEO", "title": "「工作问题还会去搜索引擎吗？」", "lead": "赵岩 · 2班 · 2023-06（2026 大量接龙）", "theme": "dark", "kind": "quote"},
    {"pg": "52/52", "section": "附录", "title": "详稿 + 22 图 + assets/data 原始 JSON", "lead": "GitHub: zhaoyan-digital-marketing-5y-whitepaper", "theme": "hero dark", "kind": "hero"},
]


def _rows_html(rows: list) -> str:
    if not rows:
        return ""
    d = "div"
    lines = [f'<{d} class="col" style="margin-top:2vh;font-size:max(14px,1.05vw)" data-anim>']
    for item in rows:
        if isinstance(item, tuple) and len(item) == 2:
            k, v = item
            lines.append(
                f'<{d} class="rowline"><{d} class="k">{k}</{d}>'
                f'<{d} class="v">{v}</{d}></{d}>'
            )
        else:
            lines.append(f'<{d} class="rowline"><{d} class="v" style="flex:1">{item}</{d}></{d}>')
    lines.append(f"</{d}>")
    return "\n".join(lines)


def render_slide(s: dict) -> str:
    d = "div"
    theme = s.get("theme", "light")
    kind = s.get("kind", "text")
    section = s["section"]
    title = s["title"]
    lead = s.get("lead", "")
    pg = s["pg"]
    img = s.get("img")
    extra = ' data-animate="quote"' if kind == "quote" else ""

    o = [f'<section class="slide {theme}"{extra}>']
    o.append(f'  <{d} class="chrome"><{d}>{section}</{d}><{d}>{pg}</{d}></{d}>')

    if kind == "hero":
        o += [
            f'  <{d} class="frame center" style="justify-content:center;text-align:center;gap:3vh">',
            f'    <{d} class="kicker" data-anim>{section}</{d}>',
            f'    <h1 class="h-hero" style="font-size:clamp(2rem,6vw,5rem)" data-anim>{title}</h1>',
        ]
        if lead:
            o.append(f'    <p class="lead" data-anim>{lead}</p>')
        o.append(f"  </{d}>")
    elif kind == "chart" and img:
        o += [
            f'  <{d} class="frame" style="padding-top:2.5vh">',
            f'    <{d} class="kicker" data-anim>{section}</{d}>',
            f'    <h2 class="h-xl" data-anim>{title}</h2>',
        ]
        if lead:
            o.append(f'    <p class="lead" style="margin-bottom:1.5vh" data-anim>{lead}</p>')
        o += [
            f'    <figure class="frame-img r-16x9 fit-contain" style="max-height:58vh" data-anim>',
            f'      <img src="{IMG}/{img}" alt="{title}">',
            f"    </figure>",
            f"  </{d}>",
        ]
    elif kind == "quote":
        o += [
            f'  <{d} class="frame center" style="justify-content:center;text-align:center;gap:2vh;padding:8vh 6vw">',
            f'    <{d} class="kicker" data-anim>{section}</{d}>',
            f'    <h2 class="h-xl" style="font-size:clamp(1.4rem,3.2vw,2.8rem);font-style:italic" data-anim>{title}</h2>',
        ]
        if lead:
            o.append(f'    <p class="lead" data-anim>{lead}</p>')
        o.append(f"  </{d}>")
    else:
        o += [
            f'  <{d} class="frame" style="padding-top:3vh">',
            f'    <{d} class="kicker" data-anim>{section}</{d}>',
            f'    <h2 class="h-xl" data-anim>{title}</h2>',
        ]
        if lead:
            o.append(f'    <p class="lead" data-anim>{lead}</p>')
        if s.get("rows"):
            o.append(_rows_html(s["rows"]))
        o.append(f"  </{d}>")

    foot = s.get("foot", section.split("·")[-1].strip() if "·" in section else section)
    o.append(f'  <{d} class="foot"><{d}>{foot}</{d}><{d}>{pg}</{d}></{d}>')
    o.append("</section>")
    return "\n".join(o)


def main():
    dest = ROOT / "ppt" / IMG
    dest.mkdir(parents=True, exist_ok=True)
    for png in (ROOT / "assets" / "charts").glob("c*.png"):
        shutil.copy2(png, dest / png.name)

    slides_html = "\n\n".join(render_slide(s) for s in SLIDES)
    html = TEMPLATE.read_text(encoding="utf-8")
    html = html.replace(
        "--ink:#0a0a0b;\n    --ink-rgb:10,10,11;\n    --paper:#f1efea;\n    --paper-rgb:241,239,234;",
        "--ink:#0a1f3d;\n    --ink-rgb:10,31,61;\n    --paper:#f1f3f5;\n    --paper-rgb:241,243,245;\n    --paper-tint:#e4e8ec;\n    --ink-tint:#152a4a;",
    )
    html = html.replace("[必填] 替换为 PPT 标题 · Deck Title", "赵岩的数字营销实战群 · 五年白皮书 · 完整可视化")
    html = html.replace("<!-- SLIDES_HERE -->", slides_html)
    html = html.replace("./assets/motion.min.js", "./motion.min.js")
    OUT.write_text(html, encoding="utf-8")
    print(f"Built {OUT} — {len(SLIDES)} slides, {len(list(dest.glob('c*.png')))} images")


if __name__ == "__main__":
    main()
