#!/usr/bin/env python3
"""Inject chart-first headings + images into whitepaper MD."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).parent
CHARTS = ROOT / "assets" / "charts"
DATA = ROOT / "assets" / "data"
SRC = ROOT / "赵岩的数字营销实战群-五年汇报白皮书-by加玮.md"
OUT = ROOT / "赵岩的数字营销实战群-五年汇报白皮书-by加玮.md"
# GitHub raw base — updated after push
GITHUB_RAW = "https://raw.githubusercontent.com/AAAAAAlone/zhaoyan-digital-marketing-5y-whitepaper/main"

BLOCKS: list[dict] = [
    {
        "anchor": "## 核心数据一览",
        "insert_after": False,
        "replace_section": True,
        "content": """
## 核心数据一览

> 下图与表均为 **342,260** 条全量扫描；本地路径 `assets/charts/`，GitHub 同步见仓库 `zhaoyan-digital-marketing-5y-whitepaper`。

---

## 6,549 条消息提及 SaaS/企业服务，为行业第一

### 核心数据 · 02 行业提及热度

![行业提及 Top8]({base}/assets/charts/c12-industry.png)

| 行业/赛道 | 命中条数 | 占全群 |
|-----------|----------|--------|
| SaaS/企业服务/软件 | 6,549 | 1.9% |
| 制造/工业 | 2,460 | 0.7% |
| 营销/广告/传媒 | 2,415 | 0.7% |
| 教育/培训 | 2,090 | 0.6% |
| 出海/外贸 | 1,669 | 0.5% |

*原始数据：* [`assets/data/manifest.json`](assets/data/manifest.json)

---

## 出海提及占比在 2025—2026 逆势升高（行业结构）

### 核心数据 · 02 行业占比 × 年

![行业占比 100% 堆叠]({base}/assets/charts/c13-industry-share-year.png)

---

## 2,045 条命中 SEO/收录类痛点，为五年最高

### 核心数据 · 03 痛点场景热度

![痛点 Top6]({base}/assets/charts/c14-pain.png)

| 痛点场景 | 命中条数 |
|----------|----------|
| SEO收录/排名 | 2,045 |
| GEO/AI搜索焦虑 | 1,516 |
| 官网/落地页转化 | 1,416 |
| 销售与市场互怼 | 960 |

---

## 2025 起 GEO/AI 焦虑占痛点结构第一（占比视角）

### 核心数据 · 03 痛点占比 × 年

![痛点占比 100%]({base}/assets/charts/c15-pain-share-year.png)

---

## 超过 14,529 条消息命中「线索·销售」；内容品牌 L1 命中 22,833 为最高

### 核心数据 · 04 L1 议题

![L1 议题分布]({base}/assets/charts/c11-l1-all.png)

---

## 2026 年 GEO 占营销议题约 19.1%，结构首超线索（8.8%）

### 核心数据 · 04 议题占比 × 年

![L1 占比 100%]({base}/assets/charts/c08-l1-share-year.png)

![议题结构桑基图 每年列=100%]({base}/assets/charts/c09-l1-sankey-share.png)

*读桑基图：列高一致，只看带宽占比变化，不看绝对条数递减。*

""",
    },
    {
        "anchor": "# 一、组织全景",
        "insert_after": True,
        "content": """
## 文本消息占全群 73.2%（250,605 条）

### 第一篇 · 组织全景 · 消息类型

![消息类型]({base}/assets/charts/c01-msg-type.png)

---

## 5/2/1 班承载约 68% 消息；7 班沉默率 81.3%

### 第一篇 · 组织全景 · 班级与沉默

![各班级消息量]({base}/assets/charts/c02-groups.png)

![各班沉默率]({base}/assets/charts/c19-silence-by-class.png)

---

## 42% 发言者仅发 1—9 条（734 人）

### 第一篇 · 组织全景 · 参与结构

![发言者层级]({base}/assets/charts/c03-speaker-tier.png)

---

## 10—11 时为发言高峰（合计约 9.6 万条）

### 第一篇 · 组织全景 · 活跃节律

![24小时分布]({base}/assets/charts/c18-hours.png)

""",
    },
    {
        "anchor": "# 二、五年演变",
        "insert_after": True,
        "content": """
## 年消息量 2021 峰值 8.0 万，2025 回落至 3.6 万

### 第二篇 · 五年演变 · 年度

![年度消息量]({base}/assets/charts/c04-year-volume.png)

---

## 单月峰值 2021-08：17,878 条

### 第二篇 · 五年演变 · 月度

![月度 Top15]({base}/assets/charts/c05-month-top15.png)

---

## 最热季度 2021-Q3：36,581 条

### 第二篇 · 五年演变 · 季度

![季度 Top12]({base}/assets/charts/c06-quarter-top12.png)

---

## 2021H2、2023H2 为两个半年爆发段

### 第二篇 · 五年演变 · 半年度

![半年度消息量]({base}/assets/charts/c07-halfyear.png)

---

## 线索/SEO 命中绝对值随总量下降；GEO 2026 逆势抬升

### 第二篇 · 五年演变 · 议题绝对值

![L1 绝对趋势]({base}/assets/charts/c10-l1-trend-abs.png)

---

## 百度提及 5,629 条；GEO 标签 2026 年 265 条

### 第二篇 · 五年演变 · 渠道

![平台词命中]({base}/assets/charts/c21-platform-l2.png)

---

## 2026 年 GEO-AI 命中 622 条，约为线索 287 条的 2.2 倍

### 第二篇 · 五年演变 · 2026 结构

![GEO vs 线索 2026]({base}/assets/charts/c22-geo-vs-lead-2026.png)

""",
    },
    {
        "anchor": "# 三、参与者",
        "insert_after": True,
        "content": """
## 赵岩 52,960 条（15.5%）；Zhaoy07331、始熊君分列二三

### 第三篇 · 参与者 · Top10

![发言人 Top10]({base}/assets/charts/c17-speakers-top10.png)

---

## 赵岩发言 2023 年峰值 12,849 条/年

### 第三篇 · 参与者 · 赵岩

![赵岩 × 年]({base}/assets/charts/c20-zhao-by-year.png)

""",
    },
    {
        "anchor": "## 2.5 痛点迁移",
        "insert_after": True,
        "content": """
![痛点绝对趋势]({base}/assets/charts/c16-pain-trend.png)

""",
    },
]


def main():
    base = GITHUB_RAW
    text = SRC.read_text(encoding="utf-8") if SRC.exists() else ""

    # Replace core data section entirely
    start = text.find("## 核心数据一览")
    end = text.find("\n---\n\n# 一、组织全景")
    if start >= 0 and end > start:
        core = BLOCKS[0]["content"].format(base=base).strip()
        text = text[:start] + core + "\n\n---\n\n" + text[end + len("\n---\n\n") :]

    for block in BLOCKS[1:]:
        ins = block["content"].format(base=base).strip()
        anchor = block["anchor"]
        pos = text.find(anchor)
        if pos < 0:
            continue
        if block.get("insert_after"):
            line_end = text.find("\n", pos)
            text = text[: line_end + 1] + "\n" + ins + "\n" + text[line_end + 1 :]

    # Update header with chart doc link
    if "03-图表规范" not in text:
        text = text.replace(
            "**范围：**",
            "**图表规范：** [`03-图表规范与清单.md`](03-图表规范与清单.md) · **图片目录：** `assets/charts/`\n\n**范围：**",
            1,
        )

    OUT.write_text(text, encoding="utf-8")
    print("Wrote", OUT, "chars", len(text))


if __name__ == "__main__":
    main()
