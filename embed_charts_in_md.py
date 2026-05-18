#!/usr/bin/env python3
"""
Keep original MD prose (## 1.1 / 2.1 …), remove injected duplicate ## chart sections,
embed each chart once inside the matching subsection. GitHub raw URLs for preview.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).parent
MD = ROOT / "赵岩的数字营销实战群-五年汇报白皮书-by加玮.md"
def img(alt: str, stem: str) -> str:
    return f"\n![{alt}](assets/charts/{stem}.png)\n"


def normalize_chart_urls(text: str) -> str:
    """统一为仓库内相对路径，本地 / GitHub 均可预览。"""
    return re.sub(
        r"!\[([^\]]*)\]\((?:https://raw\.githubusercontent\.com/[^)]+/)?assets/charts/([a-z0-9-]+)\.png\)",
        r"![\1](assets/charts/\2.png)",
        text,
    )


def remove_injected_blocks(text: str) -> str:
    """Drop ## conclusion + chart blocks between # chapter and ## N.1."""
    specs = [
        ("# 一、组织全景", r"## (?!1\.1 )"),
        ("# 二、五年演变", r"## (?!2\.1 )"),
        ("# 三、参与者", r"## (?!3\.1 )"),
    ]
    for head, sec_pat in specs:
        while True:
            pat = (
                re.escape(head)
                + r"\n\n"
                + sec_pat
                + r"[^\n]+\n\n"
                r"(?:### [^\n]+\n\n)?"
                r"(?:!\[[^\]]*\]\([^)]+\)\n\n)+"
                r"(?:---\n\n)?"
            )
            new = re.sub(pat, head + "\n\n", text, count=1)
            if new == text:
                break
            text = new
    text = re.sub(r"\*读桑基图[^\n]*\*\s*\n", "", text)
    text = re.sub(
        r"(!\[痛点绝对趋势\]\([^)]+\)\n\n)+",
        lambda _: img("痛点绝对趋势", "c16-pain-trend"),
        text,
        count=1,
    )
    return text


def rebuild_core_data(text: str) -> str:
    core = f"""## 核心数据一览

> 全量 **342,260** 条；原始 JSON 见 [`assets/data/manifest.json`](assets/data/manifest.json)。

### 行业提及热度

{img("行业提及 Top8", "c12-industry").strip()}

| 行业/赛道 | 命中条数 | 占全群 |
|-----------|----------|--------|
| SaaS/企业服务/软件 | 6,549 | 1.9% |
| 制造/工业 | 2,460 | 0.7% |
| 营销/广告/传媒 | 2,415 | 0.7% |
| 教育/培训 | 2,090 | 0.6% |
| 出海/外贸 | 1,669 | 0.5% |

### 行业占比 × 年

{img("行业占比", "c13-industry-share-year").strip()}

### 痛点场景热度

{img("痛点 Top6", "c14-pain").strip()}

| 痛点场景 | 命中条数 |
|----------|----------|
| SEO收录/排名 | 2,045 |
| GEO/AI搜索焦虑 | 1,516 |
| 官网/落地页转化 | 1,416 |
| 销售与市场互怼 | 960 |

### 痛点占比 × 年

{img("痛点占比", "c15-pain-share-year").strip()}

### L1 议题分布

{img("L1 议题", "c11-l1-all").strip()}

### 议题占比 × 年 · 结构迁移

{img("L1 占比", "c08-l1-share-year").strip()}

{img("议题结构桑基", "c09-l1-sankey-share").strip()}

"""
    start = text.find("## 核心数据一览")
    end = text.find("\n---\n\n# 一、组织全景")
    if start < 0 or end < 0:
        return text
    return text[:start] + core + text[end + len("\n---\n\n") :]


def has_chart(text: str, stem: str) -> bool:
    return stem in text


def insert_once(text: str, anchor: str, block: str, stem: str) -> str:
    if has_chart(text, stem):
        return text
    pos = text.find(anchor)
    if pos < 0:
        return text
    at = pos + len(anchor)
    return text[:at] + block + text[at:]


def embed_inline(text: str) -> str:
    pairs = [
        ("| 话题性讨论段（≥2 人、间隔 >30 分钟） | 13,187 |\n", "c01-msg-type", "消息类型构成"),
        ("占全群约 **68%**；6 班、7 班体量小", "c02-groups", "各班级消息量"),
        ("7 班约 **82%**（小班后入群、围观为主）。", "c19-silence-by-class", "各班沉默率"),
        ("- **可读文本：** 估计 **304,526** 条", "c18-hours", "24 小时分布"),
        ("| **合计** | **1,742** | 100% | 人均约 **197** 条/人（中位数远低于均值） |\n", "c03-speaker-tier", "发言者层级"),
        ("\\*分年发言人数见 `02-全量标签统计.md`", "c04-year-volume", "年度消息量"),
        ("**节律结论：** 高峰月集中在 **2021 夏—秋** 与 **2023 冬**", "c05-month-top15", "月度 Top15"),
        ("## 2.2 议题重心迁移\n\n", "c08-l1-share-year", "L1 占比"),
        ("## 2.2 议题重心迁移\n\n", "c09-l1-sankey-share", "议题结构桑基"),
        ("**2025—2026：** 整体讨论频次下降", "c10-l1-trend-abs", "议题绝对趋势"),
        ("2025 年起单季跌破 **1.2 万**", "c06-quarter-top12", "季度 Top12"),
        ("**半年度结论：** **2021H2** 为第一个全量爆发半期", "c07-halfyear", "半年度消息量"),
        ("**2021—2024：** 百度 + 官网 + 微信 为默认三角", "c21-platform-l2", "平台/渠道词"),
        ("| 2026 | **GEO/AI**、SEO、官网 | GEO 单年命中", "c22-geo-vs-lead-2026", "2026 GEO vs 线索"),
        ("Top10 合计约占全群 **45%** 以上发言。\n", "c17-speakers-top10", "发言人 Top10"),
        ("| 占全群 | 15.5%；为单一账号绝对第一 |\n", "c20-zhao-by-year", "赵岩年度发言量"),
        ("**L2 高频子标签（全群）：** 引用回复 13.0%", "c11-l1-all", "L1 议题"),
    ]
    for anchor, stem, alt in pairs:
        text = insert_once(text, anchor, img(alt, stem), stem)
    if not has_chart(text, "c16-pain-trend"):
        text = insert_once(text, "## 2.5 痛点迁移", img("痛点趋势", "c16-pain-trend"), "c16-pain-trend")
    return text


def main():
    text = MD.read_text(encoding="utf-8")
    text = remove_injected_blocks(text)
    text = rebuild_core_data(text)
    text = embed_inline(text)
    text = normalize_chart_urls(text)
    text = re.sub(r"\n{4,}", "\n\n\n", text)
    MD.write_text(text, encoding="utf-8")
    n_img = len(re.findall(r"!\[", text))
    print(f"Wrote {MD} — {n_img} images, paths assets/charts/*.png")


if __name__ == "__main__":
    main()
