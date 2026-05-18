#!/usr/bin/env python3
"""
阶段2+3：抽样发现词 → 定 L2 标签 → 全量扫描统计
输出：tag-scan-full.json, 02-全量标签统计.md, sample-keywords.json
"""

from __future__ import annotations

import json
import random
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

import jieba.analyse

OUT = Path(__file__).parent
CACHE = OUT / "messages-all-groups.jsonl"
SAMPLE_SIZE = 12000
RANDOM_SEED = 42

# L1 — same as whitepaper
L1_TAGS: list[tuple[str, re.Pattern]] = [
    ("L1-线索销售", re.compile(r"线索|SDR|MQL|SQL|转化|销售|商机|CRM|公海|跟进|获客", re.I)),
    ("L1-投放广告", re.compile(r"投放|SEM|竞价|广告|oCPC|CPC|预算|千川|信息流|获客成本", re.I)),
    ("L1-SEO搜索", re.compile(r"SEO|收录|爬虫|关键词|排名|外链|反链|TDK|官网|落地页", re.I)),
    ("L1-GEO-AI", re.compile(r"GEO|AI搜索|大模型|ChatGPT|GPT|Perplexity|豆包|AIO|Claude", re.I)),
    ("L1-出海", re.compile(r"出海|跨境|海外|Google|独立站|外贸", re.I)),
    ("L1-私域企微", re.compile(r"私域|企微|企业微信|社群|裂变|朋友圈|群发", re.I)),
    ("L1-内容品牌", re.compile(r"内容|品牌|软文|PR|案例|直播|短视频|小红书|抖音|视频号", re.I)),
    ("L1-工具SaaS", re.compile(r"SaaS|工具|系统|平台|自动化|SCRM|龙虾|openclaw", re.I)),
    ("L1-招聘合作", re.compile(r"招聘|内推|简历|合作|对接|岗位|薪资", re.I)),
    ("L1-课程活动", re.compile(r"课程|培训|大会|线下|报名|作业|班长|赵老师", re.I)),
]

# L2 — preset (validated by sample keywords)
L2_TAGS: list[tuple[str, re.Pattern]] = [
    ("L2-百度", re.compile(r"百度|大搜|品专|基木鱼|爱采购", re.I)),
    ("L2-Google", re.compile(r"Google|谷歌|必应|Bing", re.I)),
    ("L2-抖音", re.compile(r"抖音|千川", re.I)),
    ("L2-小红书", re.compile(r"小红书", re.I)),
    ("L2-视频号", re.compile(r"视频号", re.I)),
    ("L2-企微", re.compile(r"企业微信|企微", re.I)),
    ("L2-微信", re.compile(r"微信(?!版本)", re.I)),
    ("L2-oCPC", re.compile(r"oCPC|OCPC", re.I)),
    ("L2-CPC", re.compile(r"\bCPC\b|按点击", re.I)),
    ("L2-线索质量", re.compile(r"线索质量|线索不准|甩锅|公海", re.I)),
    ("L2-MQL-SQL", re.compile(r"MQL|SQL|SDR|MDR", re.I)),
    ("L2-长尾词", re.compile(r"长尾", re.I)),
    ("L2-外链", re.compile(r"外链|反链", re.I)),
    ("L2-官网", re.compile(r"官网|落地页|着陆", re.I)),
    ("L2-GEO", re.compile(r"\bGEO\b|生成式搜索|AI搜索", re.I)),
    ("L2-ChatGPT", re.compile(r"ChatGPT|GPT-4|GPT4|大模型", re.I)),
    ("L2-直播", re.compile(r"直播|Webinar|研讨会", re.I)),
    ("L2-内容营销", re.compile(r"内容营销|白皮书|案例", re.I)),
    ("L2-招聘JD", re.compile(r"岗位职责|任职要求|投递邮箱|薪资范围", re.I)),
    ("L2-赵老师", re.compile(r"赵老师|赵岩|班长", re.I)),
    ("L2-提问", re.compile(r"[？?]|怎么|如何|有没有|请问", re.I)),
    ("L2-引用回复", re.compile(r"\[引用\]|↳", re.I)),
    ("L2-分享链接", re.compile(r"\[链接\]|https?://", re.I)),
]

STOP = set("的 了 是 在 我 有 和 就 不 人 都 一 一个 上 也 很 到 说 要 去 你 会 着 没有 看 好 自己 这".split())


def clean(c: str) -> str:
    c = re.sub(r"\s+", " ", (c or "").strip())
    if c.startswith("<?xml") or "<msg>" in c[:60]:
        return ""
    return c


def load_rows() -> list[dict]:
    rows = []
    with CACHE.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def substantive(row: dict) -> bool:
    if row.get("type") == "系统":
        return False
    c = clean(str(row.get("content") or ""))
    return len(c) >= 12 and row.get("type") in ("文本", "链接/文件", None) or row.get("type") in ("文本", "链接/文件")


def discover_keywords(rows: list[dict]) -> list[str]:
    pool = [clean(str(r.get("content") or "")) for r in rows if substantive(r)]
    random.seed(RANDOM_SEED)
    sample = random.sample(pool, min(SAMPLE_SIZE, len(pool)))
    blob = "\n".join(sample)
    tags = jieba.analyse.extract_tags(blob, topK=80, withWeight=True)
    return [t for t, w in tags if len(t) >= 2 and t not in STOP]


def scan_tags(rows: list[dict]) -> dict:
    l1_total = Counter()
    l2_total = Counter()
    l1_year: dict[str, Counter] = defaultdict(Counter)
    l2_year: dict[str, Counter] = defaultdict(Counter)
    l1_group: dict[str, Counter] = defaultdict(Counter)
    l2_group: dict[str, Counter] = defaultdict(Counter)
    l1_speaker: dict[str, Counter] = defaultdict(Counter)

    type_cnt = Counter()
    year_cnt = Counter()
    month_cnt = Counter()
    hour_cnt = Counter()
    weekday_cnt = Counter()
    question_cnt = 0
    quote_cnt = 0
    link_cnt = 0
    text_len_sum = 0
    text_n = 0
    active_days = set()
    speakers = set()
    speaker_counts = Counter()
    zy_year = Counter()
    group_year: dict[str, Counter] = defaultdict(Counter)

    for r in rows:
        typ = r.get("type", "?")
        type_cnt[typ] += 1
        t = r["time"]
        y, ym = t[:4], t[:7]
        year_cnt[y] += 1
        month_cnt[ym] += 1
        hour_cnt[int(t[11:13])] += 1
        wd = datetime.strptime(t[:10], "%Y-%m-%d").strftime("%a")
        weekday_cnt[wd] += 1
        active_days.add(t[:10])
        g = r.get("group_short", "?")
        group_year[g][y] += 1

        sn = r.get("sender_norm") or r.get("sender", "")
        if r.get("type") != "系统" and sn:
            speakers.add(sn)
            speaker_counts[sn] += 1
            if "赵岩" == sn:
                zy_year[y] += 1

        c = clean(str(r.get("content") or ""))
        if c:
            if "?" in c or "？" in c:
                question_cnt += 1
            if "[引用]" in c or "↳" in c:
                quote_cnt += 1
            if "[链接]" in c or re.search(r"https?://", c):
                link_cnt += 1
            if typ == "文本":
                text_len_sum += len(c)
                text_n += 1

        if not substantive(r):
            continue
        hit_l1 = False
        for name, pat in L1_TAGS:
            if pat.search(c):
                l1_total[name] += 1
                l1_year[y][name] += 1
                l1_group[g][name] += 1
                l1_speaker[sn][name] += 1
                hit_l1 = True
        if not hit_l1:
            l1_total["L1-综合日常"] += 1
            l1_year[y]["L1-综合日常"] += 1

        for name, pat in L2_TAGS:
            if pat.search(c):
                l2_total[name] += 1
                l2_year[y][name] += 1
                l2_group[g][name] += 1

    return {
        "total": len(rows),
        "substantive_est": sum(1 for r in rows if substantive(r)),
        "speakers": len(speakers),
        "active_days": len(active_days),
        "type_cnt": dict(type_cnt),
        "year_cnt": dict(year_cnt),
        "month_top20": month_cnt.most_common(20),
        "hour_top5": hour_cnt.most_common(5),
        "weekday": dict(weekday_cnt),
        "question_cnt": question_cnt,
        "quote_cnt": quote_cnt,
        "link_cnt": link_cnt,
        "avg_text_len": round(text_len_sum / text_n, 1) if text_n else 0,
        "l1_total": dict(l1_total.most_common()),
        "l2_total": dict(l2_total.most_common()),
        "l1_by_year": {y: dict(c.most_common()) for y, c in sorted(l1_year.items())},
        "l2_by_year": {y: dict(c.most_common(15)) for y, c in sorted(l2_year.items())},
        "l1_by_group": {g: dict(c.most_common(8)) for g, c in sorted(l1_group.items())},
        "group_by_year": {g: dict(c) for g, c in sorted(group_year.items())},
        "top_speakers": speaker_counts.most_common(30),
        "zhaoyan_by_year": dict(zy_year),
        "sample_keywords": [],  # filled later
    }


def render_md(stats: dict, keywords: list[str]) -> str:
    n = stats["total"]
    lines = [
        "# 02 · 全量标签扫描统计（阶段 2+3 产出）\n\n",
        f"*生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}*  \n",
        f"*数据：{CACHE.name}，**{n:,}** 条消息；抽样 **{SAMPLE_SIZE:,}** 条做 jieba 关键词发现。*\n\n",
        "---\n\n## 一、基础维度\n\n",
        "| 指标 | 数值 |\n|------|------|\n",
        f"| 消息总量 | {n:,} |\n",
        f"| 可读文本估计（≥12字） | {stats['substantive_est']:,} |\n",
        f"| 发言人数（归一） | {stats['speakers']:,} |\n",
        f"| 有消息的自然日 | {stats['active_days']:,} |\n",
        f"| 含问号（提问倾向） | {stats['question_cnt']:,}（{100*stats['question_cnt']/n:.1f}%） |\n",
        f"| 含引用链 | {stats['quote_cnt']:,}（{100*stats['quote_cnt']/n:.1f}%） |\n",
        f"| 含链接 | {stats['link_cnt']:,}（{100*stats['link_cnt']/n:.1f}%） |\n",
        f"| 文本平均长度 | {stats['avg_text_len']} 字 |\n\n",
        "### 消息类型\n\n",
    ]
    for k, v in sorted(stats["type_cnt"].items(), key=lambda x: -x[1]):
        lines.append(f"- `{k}`：{v:,}（{100*v/n:.1f}%）\n")

    lines.append("\n### 年度消息量\n\n| 年 | 条数 |\n|----|------|\n")
    for y in sorted(stats["year_cnt"]):
        lines.append(f"| {y} | {stats['year_cnt'][y]:,} |\n")

    lines.append("\n### 月度 Top20\n\n")
    for ym, c in stats["month_top20"]:
        lines.append(f"- {ym}：{c:,}\n")

    lines.append("\n### 活跃节律\n\n")
    lines.append("- 高峰小时：" + "、".join(f"{h}时({c:,})" for h, c in stats["hour_top5"]) + "\n")
    lines.append("- 星期：" + "、".join(f"{d}({c:,})" for d, c in sorted(stats["weekday"].items(), key=lambda x: -x[1])[:5]) + "\n")

    lines.append("\n---\n\n## 二、抽样关键词（阶段 2 发现，供 L2 校验）\n\n")
    lines.append("、".join(keywords[:40]) + "\n\n")

    lines.append("---\n\n## 三、L1 议题全量命中（消息级，可重叠 L2）\n\n| L1 | 命中条数 | 占比 |\n|----|----------|------|\n")
    for k, v in sorted(stats["l1_total"].items(), key=lambda x: -x[1]):
        lines.append(f"| {k} | {v:,} | {100*v/n:.1f}% |\n")

    lines.append("\n### L1 × 年份\n\n")
    for y, cnts in stats["l1_by_year"].items():
        top = " · ".join(f"{k.replace('L1-','')}({v})" for k, v in sorted(cnts.items(), key=lambda x: -x[1])[:4])
        lines.append(f"- **{y}**：{top}\n")

    lines.append("\n---\n\n## 四、L2 细标签全量命中（多标签）\n\n| L2 | 命中条数 | 占比 |\n|----|----------|------|\n")
    for k, v in sorted(stats["l2_total"].items(), key=lambda x: -x[1]):
        lines.append(f"| {k} | {v:,} | {100*v/n:.1f}% |\n")

    lines.append("\n### L2 × 年份（每年 Top8）\n\n")
    for y, cnts in stats["l2_by_year"].items():
        top = " · ".join(f"{k.replace('L2-','')}({v})" for k, v in sorted(cnts.items(), key=lambda x: -x[1])[:8])
        lines.append(f"- **{y}**：{top}\n")

    lines.append("\n### L2 × 班级（每班 Top5）\n\n")
    for g, cnts in stats["l1_by_group"].items():
        top = " · ".join(f"{k.replace('L1-','')}({v})" for k, v in sorted(cnts.items(), key=lambda x: -x[1])[:5])
        lines.append(f"- **{g}**：{top}\n")

    lines.append("\n---\n\n## 五、发言人 Top30\n\n| # | 昵称 | 条数 | 占全群 |\n|---|------|------|--------|\n")
    for i, (name, c) in enumerate(stats["top_speakers"], 1):
        lines.append(f"| {i} | {name} | {c:,} | {100*c/n:.2f}% |\n")

    lines.append("\n### 赵岩发言 × 年\n\n")
    for y in sorted(stats["zhaoyan_by_year"]):
        lines.append(f"- {y}：{stats['zhaoyan_by_year'][y]:,}\n")

    lines.append("\n---\n\n*本文件为详稿 v1 的数据底稿；写作时引用具体数字请注明「全量扫描 342,260 条」。*\n")
    return "".join(lines)


def main() -> None:
    print("load cache...")
    rows = load_rows()
    print("sample keywords...")
    kw = discover_keywords(rows)
    print("full scan...")
    stats = scan_tags(rows)
    stats["sample_keywords"] = kw
    (OUT / "tag-scan-full.json").write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "sample-keywords.json").write_text(json.dumps(kw, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "02-全量标签统计.md").write_text(render_md(stats, kw), encoding="utf-8")
    print("wrote tag-scan-full.json, 02-全量标签统计.md")


if __name__ == "__main__":
    main()
