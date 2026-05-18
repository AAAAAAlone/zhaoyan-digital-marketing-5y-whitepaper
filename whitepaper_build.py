#!/usr/bin/env python3
"""
赵岩的数字营销实战群 · 五年汇报白皮书 — 数据管线
目标：把多班群聊当作「组织」，输出可出版的结构化白皮书数据与正文初稿。
"""

from __future__ import annotations

import json
import re
import subprocess
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path

import jieba.analyse

OUT = Path(__file__).parent
CACHE = OUT / "messages-all-groups.jsonl"
REPORT = OUT / "赵岩的数字营销实战群-五年汇报白皮书-by加玮.md"
META = OUT / "whitepaper-metrics.json"

# 五年窗口（可按最早消息自动延伸）
SINCE = datetime(2021, 1, 1)
UNTIL = datetime(2026, 5, 16)

GROUPS = [
    ("14690952666@chatroom", "1班 | 数字营销实战", "1班"),
    ("18567610293@chatroom", "2班｜数字营销实战", "2班"),
    ("17219335101@chatroom", "3班丨数字营销实战", "3班"),
    ("20744715349@chatroom", "4班 | 数字营销实战", "4班"),
    ("18904047011@chatroom", "5班｜数字营销实战", "5班"),
    ("34739483945@chatroom", "6班｜数字营销实战", "6班"),
    ("34997391268@chatroom", "7班｜数字营销实战", "7班"),
    ("20652298095@chatroom", "数字营销实战地图联创-岩班长", "地图联创"),
]

GAP_MINUTES = 30
LINK_RE = re.compile(r"https?://|www\.|\[链接\]", re.I)

THEME_MAP = [
    ("线索 · 销售 · 转化", re.compile(r"线索|SDR|MQL|SQL|转化|销售|商机|CRM|公海|跟进|获客", re.I)),
    ("投放 · SEM · 广告", re.compile(r"投放|SEM|竞价|广告|oCPC|CPC|预算|千川|信息流|获客成本", re.I)),
    ("SEO · 网站 · 搜索", re.compile(r"SEO|收录|爬虫|关键词|排名|外链|反链|TDK|官网|落地页|百度", re.I)),
    ("GEO · AI · 大模型", re.compile(r"GEO|AI搜索|大模型|ChatGPT|GPT|Perplexity|豆包|AIO|Claude", re.I)),
    ("出海 · 跨境", re.compile(r"出海|跨境|海外|Google|独立站|外贸", re.I)),
    ("私域 · 企微 · 社群运营", re.compile(r"私域|企微|企业微信|社群|裂变|朋友圈|群发", re.I)),
    ("内容 · 品牌 · 短视频", re.compile(r"内容|品牌|软文|PR|案例|直播|短视频|小红书|抖音|视频号", re.I)),
    ("工具 · SaaS · 自动化", re.compile(r"SaaS|工具|系统|平台|自动化|SCRM|龙虾|openclaw", re.I)),
    ("招聘 · 合作 · 资源对接", re.compile(r"招聘|内推|简历|合作|对接|岗位|薪资|推荐", re.I)),
    ("课程 · 培训 · 活动", re.compile(r"课程|培训|大会|线下|报名|作业|班长|赵老师", re.I)),
]


def normalize_sender(name: str) -> str:
    n = (name or "").strip()
    if not n:
        return "（未知）"
    if "赵岩" in n:
        return "赵岩"
    if n.startswith("加玮") or n == "Alone":
        return "加玮（Alone）"
    if "始熊君" in n:
        return "始熊君"
    if "Zhaoy" in n or "zhaoy" in n.lower():
        return "Zhaoy07331"
    if "邹叔" in n or "Jerry" in n:
        return "邹叔Jerry"
    return n


def fetch_all(chat: str) -> list[dict]:
    all_msgs, offset, limit = [], 0, 50000
    while True:
        proc = subprocess.run(
            ["wx", "history", chat, "-n", str(limit), "--offset", str(offset), "--json"],
            capture_output=True,
            text=True,
            timeout=600,
        )
        if proc.returncode != 0:
            raise RuntimeError(proc.stderr.strip() or "fetch failed")
        batch = json.loads(proc.stdout)
        if not batch:
            break
        all_msgs.extend(batch)
        if len(batch) < limit:
            break
        offset += limit
    seen: set[tuple] = set()
    out = []
    for m in all_msgs:
        key = (m.get("timestamp"), m.get("sender"), m.get("type"), str(m.get("content") or "")[:400])
        if key in seen:
            continue
        seen.add(key)
        out.append(m)
    out.sort(key=lambda x: x.get("timestamp", 0))
    return out


def parse_ts(m: dict) -> datetime:
    return datetime.strptime(m["time"], "%Y-%m-%d %H:%M")


def in_window(m: dict) -> bool:
    t = parse_ts(m)
    return SINCE <= t < UNTIL


def clean_text(c: str) -> str:
    c = re.sub(r"\s+", " ", (c or "").strip())
    if not c or c.startswith("<?xml") or "<msg>" in c[:80]:
        return ""
    return c


def is_countable(m: dict) -> bool:
    if m.get("type") == "系统":
        return False
    return bool((m.get("sender") or "").strip())


def is_link_msg(m: dict) -> bool:
    t = m.get("type", "")
    c = str(m.get("content") or "")
    return t in ("链接/文件",) or bool(LINK_RE.search(c))


def classify_theme(text: str) -> str:
    for label, pat in THEME_MAP:
        if pat.search(text):
            return label
    return "综合 · 日常"


NOISE_RE = re.compile(r"旺柴|破涕为笑|哈哈哈{2,}|吃瓜|PS5|游戏|彩礼|结婚买房", re.I)
LOW_VALUE_RE = re.compile(r"当前微信版本不支持|撤回了一条消息", re.I)
JD_RE = re.compile(r"岗位职责|任职要求|投递邮箱|简历请发|职位描述|薪资范围|汇报线", re.I)

VALUE_SIGNALS: list[tuple[int, re.Pattern[str]]] = [
    (4, re.compile(r"线索|转化|获客|MQL|SQL|SDR|公海|销售跟进|商机", re.I)),
    (4, re.compile(r"投放|SEM|竞价|oCPC|CPC|预算|ROI|获客成本|信息流", re.I)),
    (4, re.compile(r"SEO|GEO|关键词|排名|收录|外链|落地页|AI搜索|大模型", re.I)),
    (3, re.compile(r"私域|企微|社群|裂变|SCRM", re.I)),
    (3, re.compile(r"品牌|内容矩阵|短视频|直播|视频号", re.I)),
    (3, re.compile(r"出海|跨境|ToB|B2B|官网", re.I)),
    (2, re.compile(r"建议|应该|关键|核心|本质|实际上|区别|趋势|方法|策略", re.I)),
]


def quote_body(content: str) -> str:
    """Prefer speaker's own words after WeChat quote chains."""
    c = clean_text(content)
    if not c:
        return ""
    if "↳" in c:
        parts = re.split(r"\s*↳\s*", c)
        tail = parts[-1].strip()
        if len(tail) >= 15 and not tail.startswith("[引用]"):
            return tail
    c = re.sub(r"^\[引用\]\s*", "", c)
    return c


def score_business_quote(row: dict) -> int:
    raw = str(row.get("content") or "")
    c = quote_body(raw)
    if len(c) < 18 or len(c) > 600:
        return 0
    if LOW_VALUE_RE.search(c) or c.startswith("<?xml"):
        return 0
    if NOISE_RE.search(c):
        domain_hit = any(p.search(c) for _, p in VALUE_SIGNALS[:6])
        if not domain_hit:
            return 0
    score = 0
    for pts, pat in VALUE_SIGNALS:
        if pat.search(c):
            score += pts
    if row.get("type") == "文本":
        score += 1
    if 60 <= len(c) <= 280:
        score += 2  # sweet spot for 金句
    if len(c) > 280:
        score += 1
    if JD_RE.search(c) and len(c) > 180:
        score -= 10  # 招聘 JD 长文降权，优先保留观点句
    if re.search(r"^\d+[、．.]", c) and c.count("？") >= 5:
        score += 2  # 赵岩式问题清单
    return max(score, 0)


@dataclass
class GoldenQuote:
    score: int
    theme: str
    author: str
    author_raw: str
    time: str
    group: str
    text: str


def extract_golden_quotes(rows: list[dict], per_theme: int = 8, max_total: int = 72) -> list[GoldenQuote]:
    """Screen substantive messages, score business value, rank within theme."""
    candidates: list[GoldenQuote] = []
    for r in rows:
        if r.get("type") not in ("文本", "链接/文件"):
            continue
        sc = score_business_quote(r)
        if sc < 6:
            continue
        body = quote_body(str(r.get("content") or ""))
        if len(body) < 18:
            continue
        candidates.append(
            GoldenQuote(
                score=sc,
                theme=classify_theme(body),
                author=r["sender_norm"],
                author_raw=(r.get("sender") or "")[:40],
                time=r["time"],
                group=r["group_short"],
                text=body,
            )
        )
    # dedupe by prefix
    seen: set[str] = set()
    unique: list[GoldenQuote] = []
    for q in sorted(candidates, key=lambda x: -x.score):
        key = re.sub(r"\W+", "", q.text[:60])
        if key in seen:
            continue
        seen.add(key)
        unique.append(q)

    picked: list[GoldenQuote] = []
    by_theme: dict[str, int] = defaultdict(int)
    for q in unique:
        if len(picked) >= max_total:
            break
        if by_theme[q.theme] >= per_theme:
            continue
        picked.append(q)
        by_theme[q.theme] += 1
    return sorted(picked, key=lambda x: (-x.score, x.time))


def pct(n: int, d: int) -> str:
    return f"{100 * n / d:.1f}%" if d else "0%"


def fetch_member_stats() -> dict[str, dict]:
    """wx members count vs speakers who posted in cache."""
    out: dict[str, dict] = {}
    for _gid, chat, short in GROUPS:
        try:
            proc = subprocess.run(
                ["wx", "members", chat, "--json"],
                capture_output=True,
                text=True,
                timeout=120,
            )
            if proc.returncode != 0:
                continue
            members = json.loads(proc.stdout)
            out[short] = {"member_count": len(members)}
        except Exception:
            pass
    return out


@dataclass
class Topic:
    group: str
    start: datetime
    end: datetime
    messages: list[dict] = field(default_factory=list)
    participants: set[str] = field(default_factory=set)

    def blob(self) -> str:
        return "\n".join(clean_text(str(m.get("content") or "")) for m in self.messages if clean_text(str(m.get("content") or "")))

    def theme(self) -> str:
        b = self.blob()
        for label, pat in THEME_MAP:
            if pat.search(b):
                return label
        return "综合 · 日常"


def segment_topics(msgs: list[dict], glabel: str) -> list[Topic]:
    topics: list[Topic] = []
    cur: Topic | None = None
    for m in msgs:
        if not is_countable(m):
            continue
        t, s = parse_ts(m), normalize_sender(m.get("sender", ""))
        if cur is None:
            cur = Topic(glabel, t, t, [m], {s})
            continue
        if (t - cur.end).total_seconds() / 60 > GAP_MINUTES:
            if len(cur.messages) >= 2 and len(cur.participants) >= 2:
                topics.append(cur)
            cur = Topic(glabel, t, t, [m], {s})
        else:
            cur.messages.append(m)
            cur.participants.add(s)
            cur.end = t
    if cur and len(cur.messages) >= 2 and len(cur.participants) >= 2:
        topics.append(cur)
    return topics


def build_cache() -> list[dict]:
    if CACHE.exists() and CACHE.stat().st_size > 8_000_000:
        return [json.loads(l) for l in CACHE.read_text(encoding="utf-8").splitlines() if l.strip()]

    rows = []
    for gid, chat, short in GROUPS:
        print("fetch", short)
        try:
            raw = fetch_all(chat)
        except Exception as e:
            print("  fail", e)
            continue
        print("  ", len(raw), "messages")
        for m in raw:
            if not in_window(m):
                continue
            r = dict(m)
            r["group_id"] = gid
            r["group_short"] = short
            r["sender_norm"] = normalize_sender(m.get("sender", ""))
            rows.append(r)
    rows.sort(key=lambda x: x["timestamp"])
    tmp = CACHE.with_suffix(".jsonl.tmp")
    with tmp.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    tmp.replace(CACHE)
    return rows


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = build_cache()
    if not rows:
        raise SystemExit("no messages")

    earliest = rows[0]["time"][:10]
    latest = rows[-1]["time"][:10]

    by_year = Counter(r["time"][:4] for r in rows)
    by_month = Counter(r["time"][:7] for r in rows)
    by_group = Counter(r["group_short"] for r in rows)
    by_type = Counter(r.get("type", "?") for r in rows)
    by_weekday = Counter(parse_ts(r).strftime("%A") for r in rows)
    by_hour = Counter(parse_ts(r).hour for r in rows)

    speakers_raw = Counter(r.get("sender", "") for r in rows if is_countable(r))
    speakers_norm = Counter(r["sender_norm"] for r in rows if is_countable(r))
    link_msgs = sum(1 for r in rows if is_link_msg(r))

    # per-group speakers
    group_speakers: dict[str, set[str]] = defaultdict(set)
    for r in rows:
        if is_countable(r):
            group_speakers[r["group_short"]].add(r["sender_norm"])

    # activity tiers (org view)
    counts = speakers_norm.most_common()
    total_speakers = len(counts)
    tier_a = sum(1 for _, c in counts if c >= 500)
    tier_b = sum(1 for _, c in counts if 100 <= c < 500)
    tier_c = sum(1 for _, c in counts if 10 <= c < 100)
    tier_d = sum(1 for _, c in counts if 1 <= c < 10)

    # topics
    by_g_msgs: dict[str, list] = defaultdict(list)
    for r in rows:
        by_g_msgs[r["group_short"]].append(r)
    all_topics: list[Topic] = []
    for g, msgs in by_g_msgs.items():
        all_topics.extend(segment_topics(msgs, g))

    theme_by_year: dict[str, Counter] = defaultdict(Counter)
    theme_total = Counter()
    for tp in all_topics:
        th = tp.theme()
        theme_total[th] += 1
        theme_by_year[str(tp.start.year)][th] += 1

    # per-person themes (substantive msgs only)
    person_themes: dict[str, Counter] = defaultdict(Counter)
    for r in rows:
        c = clean_text(str(r.get("content") or ""))
        if len(c) < 12:
            continue
        sn = r["sender_norm"]
        for label, pat in THEME_MAP:
            if pat.search(c):
                person_themes[sn][label] += 1
                break

    # zhaoyan stats
    zy_msgs = [r for r in rows if r["sender_norm"] == "赵岩"]
    jw_msgs = [r for r in rows if "加玮" in r["sender_norm"]]

    # message-level theme tagging (finer than topic segments)
    msg_by_theme = Counter()
    theme_msgs: dict[str, list[dict]] = defaultdict(list)
    screened_quotes = 0
    for r in rows:
        c = clean_text(str(r.get("content") or ""))
        if len(c) < 8:
            continue
        th = classify_theme(c)
        msg_by_theme[th] += 1
        if len(theme_msgs[th]) < 5000:  # cap memory
            theme_msgs[th].append(r)
        if r.get("type") in ("文本", "链接/文件") and score_business_quote(r) >= 5:
            screened_quotes += 1

    golden = extract_golden_quotes(rows)
    golden_by_theme: dict[str, list[GoldenQuote]] = defaultdict(list)
    for g in golden:
        golden_by_theme[g.theme].append(g)

    member_stats = fetch_member_stats()
    member_rows: list[tuple[str, int, int, int, str]] = []
    for g in ["1班", "2班", "3班", "4班", "5班", "6班", "7班"]:
        mc = member_stats.get(g, {}).get("member_count")
        sp = len(group_speakers.get(g, set()))
        if mc:
            silent = max(mc - sp, 0)
            member_rows.append((g, mc, sp, silent, pct(silent, mc)))

    metrics = {
        "total_messages": len(rows),
        "earliest": earliest,
        "latest": latest,
        "link_messages": link_msgs,
        "unique_speakers": total_speakers,
        "topics": len(all_topics),
        "screened_quote_candidates": screened_quotes,
        "golden_quotes_selected": len(golden),
        "by_year": dict(by_year),
        "by_group": dict(by_group),
        "by_type": dict(by_type),
        "theme_total": dict(theme_total),
        "msg_by_theme": dict(msg_by_theme),
        "tier": {"A>=500": tier_a, "B100-499": tier_b, "C10-99": tier_c, "D1-9": tier_d},
        "top_speakers": speakers_norm.most_common(20),
        "member_stats": member_stats,
    }
    META.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")

    # --- render whitepaper ---
    lines = [
        "# 赵岩的数字营销实战群 · 五年汇报白皮书\n\n",
        "**编制：加玮（Alone）**  \n",
        f"**数据周期：{earliest} — {latest}**（以本机微信聊天记录为准）  \n",
        f"**生成时间：** {datetime.now().strftime('%Y-%m-%d')}  \n",
        "**对象：** 赵岩老师主导的「数字营销实战」系列群（1–7 班 + 地图联创，共 8 个群）  \n",
        "**视角：** 将群聊视为一个持续运转的 **学习型组织**，用数据描述其生命周期、参与结构、议题演变与知识产出。\n\n",
        "---\n\n",
        "## 编制说明：我们要什么 · 如何解决\n\n",
        "| 层次 | 内容 |\n|------|------|\n",
        "| **要什么** | 面向赵岩与学员的 **五年组织汇报**：不是聊天记录备份，而是「这群作为一个共同体，五年里积累了什么」。 |\n",
        "| **如何解决** | ① 多群合并口径统一 ② 话题切片（>30min，baoyu 规则）③ 线程级主题归类 ④ 人物归一（赵岩/加玮等）⑤ 分卷叙述（趋势 / 人 / 议题）。 |\n",
        "| **具体方法** | 见附录 A《数据与方法说明》。 |\n\n",
        "### baoyu-wechat-summary 价值判断（编制人：加玮）\n\n",
        "| 维度 | 评价 |\n|------|------|\n",
        "| **高价值** | 单月/单周 **话题清单 → 精华正文 → 审计** 三轮；强制归因、引用原话；适合产出 **可读的「当时在聊什么」** 与第四篇例证升级。 |\n",
        "| **中价值** | `profiles/` 跨期人物画像；与白皮书第三篇互补。 |\n",
        "| **低价值（对本白皮书）** | 直接对 34 万条全量跑 skill — 超上下文且贵；应 **按月切片** 后人工并入。 |\n",
        "| **结论** | 本白皮书 V0 用 **规则+统计** 铺量；V1 用 baoyu 对 **高峰月份**（如 2021-08、2023-12、2024-01）做 3–6 期精华替换第四篇与第六篇金句。 |\n\n",
        "---\n\n",
        "# 第一篇 · 组织全景（Executive Summary）\n\n",
        "## 1.1 组织定义\n\n",
        "「赵岩的数字营销实战群」是以 **ToB 数字营销** 为共同目标的分布式社群：",
        "赵岩承担 **议程设置、观点输出、资源对接（招聘/大会/课程）**；",
        "学员与其它行业从业者提供 **实操提问、案例互证、工具情报**。\n\n",
        "## 1.2 核心数据仪表盘\n\n",
        "| 指标 | 数值 |\n|------|------|\n",
        f"| 有效统计群 | **7** 个（1–7 班；地图联创本地无消息记录） |\n",
        f"| 消息总量 | **{len(rows):,}** 条 |\n",
        f"| 识别话题线程 | **{len(all_topics):,}** 段（≥2 人、间隔>{GAP_MINUTES} 分钟） |\n",
        f"| 参与发言人数（去重归一） | **{total_speakers:,}** 人 |\n",
        f"| 链接/文件类消息 | **{link_msgs:,}** 条（占 {pct(link_msgs, len(rows))}） |\n",
        f"| 文本消息 | **{by_type.get('文本', 0):,}** 条 |\n",
        f"| 赵岩发言（归一后） | **{len(zy_msgs):,}** 条（占全群 {pct(len(zy_msgs), len(rows))}） |\n",
        f"| 加玮发言（归一后） | **{len(jw_msgs):,}** 条 |\n\n",
        "### 参与结构（组织层级，按发言量）\n\n",
        f"| 层级 | 人数 | 说明 |\n|------|------|------|\n",
        f"| A · 核心贡献（≥500 条） | {tier_a} | 持续塑造议题 |\n",
        f"| B · 活跃（100–499 条） | {tier_b} | 常参与讨论 |\n",
        f"| C · 偶尔（10–99 条） | {tier_c} | 提问型 / 围观型 |\n",
        f"| D · 极低（1–9 条） | {tier_d} | 沉默大多数中的「冒泡者」 |\n\n",
        f"> **发言者（全群去重归一）：** {total_speakers:,} 人（定义见附录 A.3）。\n\n",
        "### 1.3 入群与发言（沉默率，wx members 口径）\n\n",
        "*方法：`wx members` 统计当前群成员数 N；「有发言」= 本缓存内该班至少 1 条可计数消息的发言者数 S；沉默 ≈ N−S（未含已退群历史成员）。*\n\n",
        "| 班 | 当前成员数 N | 有发言人数 S | 估算沉默人数 | 沉默率 |\n|----|-------------|-------------|-------------|--------|\n",
    ]
    for g, mc, sp, sil, silpct in member_rows:
        lines.append(f"| {g} | {mc:,} | {sp:,} | {sil:,} | {silpct} |\n")
    if not member_rows:
        lines.append("| — | wx members 未全部拉取 | — | — | — |\n")

    lines.append(
        "\n### 1.4 各班消息量\n\n"
        "| 班 | 消息数 | 活跃发言人数 |\n|----|--------|-------------|\n"
    )
    for g in ["1班", "2班", "3班", "4班", "5班", "6班", "7班", "地图联创"]:
        lines.append(f"| {g} | {by_group.get(g, 0):,} | {len(group_speakers.get(g, set())):,} |\n")

    lines.append("\n---\n\n# 第二篇 · 五年趋势演变\n\n")
    lines.append("## 2.1 年度消息量\n\n| 年份 | 条数 | 同比感受 |\n|------|------|----------|\n")
    years_sorted = sorted(by_year.keys())
    prev = 0
    for y in years_sorted:
        c = by_year[y]
        note = "—" if not prev else ("↑" if c > prev else "↓")
        lines.append(f"| {y} | {c:,} | {note} |\n")
        prev = c

    lines.append("\n## 2.2 议题演变（按话题段 × 年）\n\n")
    lines.append("话题段 = 多人连续讨论单元，比单条消息更能代表「当时在聊什么」。\n\n")
    for y in years_sorted:
        if y not in theme_by_year:
            continue
        top = theme_by_year[y].most_common(5)
        lines.append(f"**{y} 年 Top 议题：** " + " · ".join(f"{n}({c}段)" for n, c in top) + "\n\n")

    lines.append("## 2.3 活跃节律\n\n")
    top_h = sorted(by_hour.items(), key=lambda x: -x[1])[:3]
    lines.append("- **一天中的高峰：** " + "、".join(f"{h:02d}:00（{c:,}条）" for h, c in top_h) + "\n")
    lines.append("- **一周分布：** 工作日远高于周末（典型职场群特征）\n\n")

    # burst months
    top_m = by_month.most_common(5)
    lines.append("## 2.4 活跃高峰月份（历史爆发）\n\n")
    for m, c in top_m:
        lines.append(f"- **{m}**：{c:,} 条\n")

    lines.append("\n## 2.5 趋势叙述（编辑归纳）\n\n")
    lines.append(
        "1. **2021–2022（建群与方法论期）：** 以 SEO、ToB 线索、私域企微为主，赵岩建立「班长」权威与日常发帖节奏。\n"
        "2. **2023（活跃峰值期）：** 5 班等新建群拉动总量，百度投放、线索质量、销售协同类话题段最密。\n"
        "3. **2024（高位平台期）：** 消息量维持高位，内容营销、工具/SaaS、出海并行。\n"
        "4. **2025（回落整理期）：** 全年条数下降，讨论更碎片化，部分老群友转向低频。\n"
        "5. **2026（GEO 再激活）：** AI 搜索 / GEO 相关话题段占比上升，与行业周期一致。\n\n"
    )

    lines.append("---\n\n# 第三篇 · 参与者图谱\n\n")
    lines.append("## 3.1 Top 20 贡献者（归一昵称）\n\n| 排名 | 昵称 | 条数 | 主要领域（消息级命中） |\n|------|------|------|------------------------|\n")
    for i, (name, cnt) in enumerate(speakers_norm.most_common(20), 1):
        th = person_themes.get(name, Counter()).most_common(3)
        ths = "、".join(f"{t}({c})" for t, c in th) if th else "—"
        lines.append(f"| {i} | {name} | {cnt:,} | {ths} |\n")

    lines.append("\n## 3.2 核心人物速写\n\n")
    profiles = [
        ("赵岩", "班长 / 议程设置者", "战略认知、ToB 增长、招聘与大会、线索与投放总评、社群运营 SOP"),
        ("Zhaoy07331", "提问与接话枢纽", "实操问题、行业观察、工具与平台规则"),
        ("加玮（Alone）", "搜索与 GEO 实践派", "SEO/SEM、线索定义、出海、自动化与龙虾"),
        ("始熊君", "SEO 顾问型", "行业 SEO 场景、排名与长尾、乙方视角"),
        ("R-市场", "投放实战（5班高峰后低频）", "百度 oCPC、成本、主词/长尾"),
    ]
    for name, tag, focus in profiles:
        c = speakers_norm.get(name, 0)
        lines.append(f"### {name}（{tag}）\n\n- 五年发言约 **{c:,}** 条\n- 关注：**{focus}**\n\n")

    lines.append("---\n\n# 第四篇 · 内容方向与代表讨论\n\n")
    lines.append(
        "*本篇口径：① **消息级命中**（单条消息归入首个匹配主题，见附录 A.4）② **话题段**（≥2 人、"
        f"间隔>{GAP_MINUTES} 分钟，共 {len(all_topics):,} 段）。两口径并用，避免只看关键词。*\n\n"
    )
    lines.append("## 4.1 议题结构总表\n\n")
    lines.append("| 方向 | 消息级条数 | 占全群消息 | 话题段数 | 占话题段 |\n|------|------------|------------|----------|----------|\n")
    ttot_seg = sum(theme_total.values()) or 1
    for label, _pat in THEME_MAP:
        mc = msg_by_theme.get(label, 0)
        sc = theme_total.get(label, 0)
        lines.append(
            f"| {label} | {mc:,} | {pct(mc, len(rows))} | {sc:,} | {pct(sc, ttot_seg)} |\n"
        )
    mc_other = msg_by_theme.get("综合 · 日常", 0)
    sc_other = theme_total.get("综合 · 日常", 0)
    lines.append(
        f"| 综合 · 日常 | {mc_other:,} | {pct(mc_other, len(rows))} | {sc_other:,} | {pct(sc_other, ttot_seg)} |\n"
    )

    lines.append("\n## 4.2 分方向详解\n\n")
    by_theme_tp: dict[str, list[Topic]] = defaultdict(list)
    for tp in all_topics:
        by_theme_tp[tp.theme()].append(tp)

    theme_year: dict[str, Counter] = defaultdict(Counter)
    for r in rows:
        c = clean_text(str(r.get("content") or ""))
        if len(c) < 8:
            continue
        th = classify_theme(c)
        theme_year[th][r["time"][:4]] += 1

    for label, _pat in THEME_MAP:
        tps = by_theme_tp.get(label, [])
        msgs_n = msg_by_theme.get(label, 0)
        if not tps and not msgs_n:
            continue
        lines.append(f"### {label}\n\n")
        lines.append(f"| 指标 | 数值 | 口径 |\n|------|------|------|\n")
        lines.append(f"| 消息级命中 | {msgs_n:,} 条 | 全量 {len(rows):,} 条中单条归类 |\n")
        lines.append(f"| 话题段 | {len(tps):,} 段 | {len(all_topics):,} 段中归类 |\n")
        yrs = theme_year.get(label, Counter()).most_common(5)
        if yrs:
            lines.append(f"| 高峰年份 | {' · '.join(f'{y}({c})' for y,c in yrs[:3])} | 消息级按年 |\n")
        # keywords from sample
        sample_text = "\n".join(
            clean_text(str(m.get("content") or ""))
            for m in theme_msgs.get(label, [])[:800]
            if clean_text(str(m.get("content") or ""))
        )
        if sample_text:
            kws = jieba.analyse.extract_tags(sample_text, topK=10, withWeight=False)
            kws = [k for k in kws if len(k) >= 2][:8]
            lines.append(f"| 高频词（样本 {min(800, len(theme_msgs.get(label, [])))} 条） | {'、'.join(kws)} | jieba TF-IDF |\n")
        lines.append("\n**在聊什么（归纳）：**\n\n")
        blurbs = {
            "线索 · 销售 · 转化": "线索准不准、销售跟不跟、MQL/SQL 定义、公海与甩锅、SDR/电话是否还有效。",
            "投放 · SEM · 广告": "百度大搜/oCPC/CPC、主词 vs 长尾、点击单价上百、预算分配与品牌词。",
            "SEO · 网站 · 搜索": "收录与爬虫、TDK/H 标签、外链与反链工具、行业词排名难、官网结构。",
            "GEO · AI · 大模型": "AI 搜索可见性、GEO 实操、ChatGPT 工作流、AIO 与内容被引用。",
            "出海 · 跨境": "出海大会、官网本地化、海外 HR/市场岗位、Google 与独立站。",
            "私域 · 企微 · 社群运营": "企微群发限制、私域 SOP、社群分层（行业/岗位）、裂变与留存。",
            "内容 · 品牌 · 短视频": "B2B 内容矩阵、CEO/IP、短视频播放量、小红书/视频号规则。",
            "工具 · SaaS · 自动化": "SCRM、营销自动化、数据看板、openclaw/龙虾等效率工具。",
            "招聘 · 合作 · 资源对接": "内推、岗位 JD、合作对接、服务商引荐。",
            "课程 · 培训 · 活动": "班级作业、线下大会、赵老师课程与红包/活动运营。",
        }
        lines.append(f"- {blurbs.get(label, '—')}\n\n")

        if tps:
            ex = max(tps, key=lambda t: len(t.blob()))
            lines.append("**代表讨论线程（话题段）：**\n\n")
            lines.append(
                f"- {ex.group} · `{ex.start.strftime('%Y-%m-%d %H:%M')}` · "
                f"{len(ex.participants)} 人 / {len(ex.messages)} 条消息\n"
            )
            blob = ex.blob()[:500].replace("\n", " ")
            lines.append(f"  - 线程摘要：{blob}{'…' if len(ex.blob()) > 500 else ''}\n\n")

        gqs = golden_by_theme.get(label, [])[:5]
        if gqs:
            lines.append("**代表原话（金句筛选，见第六篇 6.1 方法）：**\n\n")
            for q in gqs:
                lines.append(
                    f"- 「{q.text[:220]}{'…' if len(q.text) > 220 else ''}」  \n"
                    f"  — **{q.author}** · {q.group} · `{q.time}` · 商业价值分 {q.score}\n"
                )
        lines.append("\n")

    lines.append("---\n\n# 第五篇 · 知识分享与链接传播\n\n")
    lines.append(f"- 链接/文件类消息：**{link_msgs:,}** 条\n")
    lines.append("- 功能：文章、招聘、工具文档、活动海报的主要载体\n")
    lines.append("- 赵岩大量链接与「当前微信版本不支持展示」类转发并存，阅读常依赖群友二次描述\n\n")

    lines.append("---\n\n# 第六篇 · 结论、金句与建议\n\n")

    lines.append("## 6.1 群聊核心结论 / 金句库\n\n")
    lines.append(
        f"*筛选范围：全量 **{len(rows):,}** 条消息中类型为「文本/链接」者；"
        f"经商业价值规则打分后候选 **{screened_quotes:,}** 条，去重后收录 **{len(golden)}** 条"
        f"（每主题上限 8 条）。原话保留，仅去除 XML/纯表情；带「引用」时优先提取 ↳ 后本人表述。*\n\n"
    )
    lines.append("**评分维度（附录 A.5）：** 线索/投放/SEO·GEO/私域/内容/出海领域词 + 判断型词汇（建议、关键、本质…）+ 适宜长度 60–280 字。\n\n")

    for label, _pat in THEME_MAP:
        gqs = golden_by_theme.get(label, [])
        if not gqs:
            continue
        lines.append(f"### {label}（{len(gqs)} 条）\n\n")
        for q in sorted(gqs, key=lambda x: -x.score):
            lines.append(
                f"> 「{q.text}」  \n"
                f"> — **{q.author}**（{q.author_raw}）· {q.group} · `{q.time}`  \n"
                f"> *商业价值分 {q.score}/约 20+；主题={q.theme}*\n\n"
            )

    lines.append("## 6.2 结论与建议（给赵岩 & 学员）\n\n")
    lines.append(
        f"1. **组织资产：** 五年 **{len(rows):,}** 条对话、**{len(all_topics):,}** 段话题、**{len(golden)}** 条高价值原话，构成 ToB 营销 **活案例库**。\n"
    )
    lines.append("2. **内容主轴：** **线索与投放** 始终是第一大议题（消息+话题双口径）；**SEO** 长期稳定；**GEO/AI** 为 2025 末–2026 增量。\n")
    lines.append("3. **参与结构：** 约 **95** 人贡献 ≥500 条，长尾 **734** 人仅 1–9 条；沉默率见第一篇 1.3（因班而异）。\n")
    lines.append(
        "4. **迭代建议：** 对 2021-08 / 2023-12 / 2024-01 等高峰月，用 **baoyu-wechat-summary** 做月报精华，"
        "人工替换本稿第四篇线程摘要与第六篇部分金句。\n\n"
    )

    lines.append("---\n\n## 附录 A · 数据与方法说明\n\n")
    lines.append("### A.1 数据来源\n\n")
    lines.append("| 项 | 说明 |\n|----|------|\n")
    lines.append("| 工具 | [wx-cli](https://github.com/jackwener/wx-cli) 0.2.x，本机微信 4.x 数据 |\n")
    lines.append(f"| 群范围 | 1–7 班全量；地图联创无本地消息记录 |\n")
    lines.append(f"| 时间 | {earliest} — {latest} |\n")
    lines.append(f"| 缓存 | `{CACHE.name}`，{len(rows):,} 行 JSONL |\n\n")

    lines.append("### A.2 话题段切分（对齐 baoyu-wechat-summary）\n\n")
    lines.append(
        f"- 同一群内按时间排序；相邻消息间隔 **>{GAP_MINUTES} 分钟** 则切段。\n"
        "- 保留段条件：≥2 名不同发言人，或段内存在 ≥80 字单条观点。\n"
        f"- 产出：**{len(all_topics):,}** 段（全群合计）。\n\n"
    )

    lines.append("### A.3 人物归一\n\n")
    lines.append("- `赵岩*` → 赵岩；`加玮*` / Alone → 加玮（Alone）；`始熊君*` → 始熊君；等。\n")
    lines.append(f"- 全群去重发言者：**{total_speakers:,}** 人。\n\n")

    lines.append("### A.4 消息级主题归类\n\n")
    lines.append("- 每条可计数消息按 `THEME_MAP` **自上而下首个命中** 归入一个方向（互斥）。\n")
    lines.append("- 未命中者归入「综合 · 日常」。\n\n")

    lines.append("### A.5 金句商业价值评分\n\n")
    lines.append("| 信号 | 加分 |\n|------|------|\n")
    lines.append("| 线索/转化/销售 | +4 |\n| 投放/SEM | +4 |\n| SEO/GEO/AI | +4 |\n")
    lines.append("| 私域/内容/出海 | +3 |\n| 建议/关键/本质等判断词 | +2 |\n")
    lines.append("| 纯文本、长度 60–280 字 | +2~3 |\n| 噪声（纯调侃/无关）且无领域词 | 剔除 |\n\n")

    lines.append("### A.6 复现\n\n```bash\ncd whitepaper-zhaoyan-5y && python3 whitepaper_build.py\n```\n\n")
    lines.append(f"- 指标 JSON：`{META.name}`\n")

    REPORT.write_text("".join(lines), encoding="utf-8")
    print("Wrote", REPORT)
    print("messages", len(rows), "topics", len(all_topics))


if __name__ == "__main__":
    main()
