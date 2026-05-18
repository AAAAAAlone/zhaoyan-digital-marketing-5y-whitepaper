#!/usr/bin/env python3
"""Extended stats: industry, pain points, quarterly, topic segments."""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

CACHE = Path(__file__).parent / "messages-all-groups.jsonl"
OUT = Path(__file__).parent / "expand-stats.json"

INDUSTRIES: list[tuple[str, re.Pattern]] = [
    ("SaaS/企业服务/软件", re.compile(r"SaaS|企业服务|B2B软件|营销软件|SCRM|CRM|致趣|纷享|销售易|北森|用友|金蝶", re.I)),
    ("制造/工业/工业互联网", re.compile(r"制造|工业|工业互联网|工厂|设备|机床|零部件|项目申报", re.I)),
    ("知识产权/专利/法律", re.compile(r"知识产权|专利|商标|版权|律所|法律", re.I)),
    ("教育/培训", re.compile(r"教育|培训|学校|院校|职教|K12", re.I)),
    ("医疗/健康/医药", re.compile(r"医疗|医药|健康|医院|器械|生物", re.I)),
    ("金融/保险", re.compile(r"金融|保险|银行|证券|基金|理财", re.I)),
    ("电商/零售/消费品", re.compile(r"电商|零售|消费品|快消|品牌方", re.I)),
    ("房地产/建筑/装修", re.compile(r"房地产|地产|建筑|装修|建材", re.I)),
    ("物流/供应链", re.compile(r"物流|供应链|仓储|快递", re.I)),
    ("人力资源/招聘", re.compile(r"人力资源|猎头|招聘|HR\b|人事", re.I)),
    ("营销/广告/传媒/公关", re.compile(r"公关|传媒|广告代理|4A|品牌咨询|市场总监", re.I)),
    ("环保/能源/新能源", re.compile(r"环保|能源|新能源|光伏|碳", re.I)),
    ("汽车/出行", re.compile(r"汽车|车联网|出行|新能源车企", re.I)),
    ("游戏/文娱", re.compile(r"游戏|文娱|影视|动漫", re.I)),
    ("出海/外贸", re.compile(r"出海|外贸|跨境|海外业务", re.I)),
]

PAIN_POINTS: list[tuple[str, re.Pattern]] = [
    ("线索不准/找不到客户", re.compile(r"线索不准|线索质量|没找到客户|客户不存在|线索差|无效线索", re.I)),
    ("销售与市场互怼", re.compile(r"销售.*线索|线索.*销售|甩锅|公海|跟进.*勤|市场背锅", re.I)),
    ("投放成本高/oCPC", re.compile(r"oCPC|点击.*贵|成本高|单价.*百|预算.*不够|烧不起", re.I)),
    ("主词难/长尾取舍", re.compile(r"主词|长尾|抢不到|词包|关键词.*难", re.I)),
    ("SEO收录/排名", re.compile(r"收录|排名|爬虫|TDK|外链|不收录", re.I)),
    ("官网/落地页转化", re.compile(r"落地页|基木鱼|转化率|官网.*差|着陆页", re.I)),
    ("一个人的市场部", re.compile(r"一个人.*市场|市场部.*一人|全能|啥都要干", re.I)),
    ("老板/认知/战略乱", re.compile(r"老板.*不懂|认知|战略.*乱|南辕北辙|老板让", re.I)),
    ("内容难做/播放低", re.compile(r"播放量|没人看|内容.*难|不会做视频|短视频.*低", re.I)),
    ("私域/企微触达", re.compile(r"企微.*限制|群发|私域.*难|触达", re.I)),
    ("工具选型/数据打通", re.compile(r"工具.*选|打通|CDP|数据.*孤岛|MTL", re.I)),
    ("岗位能力/职业路径", re.compile(r"加薪|职业|转行|市场人.*能力|要不要做市场", re.I)),
    ("GEO/AI搜索焦虑", re.compile(r"GEO|AI搜索|还会.*百度|ChatGPT.*搜索|大模型.*取代", re.I)),
    ("招聘/JD/内推", re.compile(r"岗位职责|任职要求|内推|投递|薪资范围", re.I)),
    ("非标/窄行业投放", re.compile(r"非标|窄|工业制造|项目申报|不适合.*信息流", re.I)),
]

L1_ORDER = [
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


def clean(c: str) -> str:
    c = re.sub(r"\s+", " ", (c or "").strip())
    if c.startswith("<?xml") or "<msg>" in c[:60]:
        return ""
    return c


def load_rows():
    rows = []
    with CACHE.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def norm_sender(s: str) -> str:
    s = (s or "").strip()
    if s.startswith("赵岩"):
        return "赵岩"
    if "加玮" in s or s == "Alone":
        return "加玮（Alone）"
    if s.startswith("始熊君"):
        return "始熊君"
    return s


def main():
    rows = load_rows()
    n = len(rows)
    ind_total = Counter()
    ind_year: dict[str, Counter] = defaultdict(Counter)
    pain_total = Counter()
    pain_year: dict[str, Counter] = defaultdict(Counter)
    l1_year: dict[str, Counter] = defaultdict(Counter)
    quarter_cnt = Counter()
    group_cnt = Counter()
    group_speakers: dict[str, set] = defaultdict(set)
    topic_sizes = []
    cross_group_speakers = Counter()

    # topic segments per group (simple 30min gap)
    by_group_msgs: dict[str, list] = defaultdict(list)
    speaker_groups: dict[str, set] = defaultdict(set)

    for r in rows:
        g = r.get("group") or "?"
        group_cnt[g] += 1
        sender = norm_sender(r.get("sender") or "")
        if sender:
            group_speakers[g].add(sender)
            speaker_groups[sender].add(g)
        ts = r.get("timestamp") or 0
        if ts:
            dt = datetime.fromtimestamp(ts)
            y = str(dt.year)
            q = f"{y}-Q{(dt.month - 1) // 3 + 1}"
            quarter_cnt[q] += 1
        c = clean(str(r.get("content") or ""))
        if len(c) < 4:
            continue
        for name, pat in INDUSTRIES:
            if pat.search(c):
                ind_total[name] += 1
                if ts:
                    ind_year[y][name] += 1
        for name, pat in PAIN_POINTS:
            if pat.search(c):
                pain_total[name] += 1
                if ts:
                    pain_year[y][name] += 1
        for l1, pat in L1_ORDER:
            if pat.search(c):
                l1_year[y][l1] += 1
                break
        by_group_msgs[g].append((ts, sender, c))

    for sender, gs in speaker_groups.items():
        if len(gs) >= 2:
            cross_group_speakers[sender] = len(gs)

    # segment count rough per group
    seg_count = 0
    for g, msgs in by_group_msgs.items():
        msgs.sort(key=lambda x: x[0])
        seg = []
        last_ts = 0
        speakers = set()
        for ts, s, c in msgs:
            if not ts:
                continue
            if seg and (ts - last_ts) > 1800:
                if len(speakers) >= 2 and len(seg) >= 2:
                    seg_count += 1
                    topic_sizes.append(len(seg))
                seg = []
                speakers = set()
            seg.append(c)
            speakers.add(s)
            last_ts = ts
        if len(speakers) >= 2 and len(seg) >= 2:
            seg_count += 1
            topic_sizes.append(len(seg))

    avg_seg = sum(topic_sizes) / len(topic_sizes) if topic_sizes else 0

    out = {
        "total": n,
        "industries": ind_total.most_common(),
        "industries_by_year": {y: c.most_common() for y, c in sorted(ind_year.items())},
        "pain_points": pain_total.most_common(),
        "pain_by_year": {y: c.most_common(8) for y, c in sorted(pain_year.items())},
        "l1_by_year": {y: c.most_common() for y, c in sorted(l1_year.items())},
        "quarterly": quarter_cnt.most_common(),
        "by_group": group_cnt.most_common(),
        "group_speaker_count": {g: len(s) for g, s in group_speakers.items()},
        "cross_group_count": len(cross_group_speakers),
        "cross_group_top20": cross_group_speakers.most_common(20),
        "topic_segments_est": seg_count,
        "avg_msgs_per_segment": round(avg_seg, 1),
    }
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=2)[:8000])


if __name__ == "__main__":
    main()
