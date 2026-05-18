#!/usr/bin/env python3
"""Build slide specs from whitepaper MD — conclusion title, section, bullets, chart."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).parent
MD_PATH = ROOT / "赵岩的数字营销实战群-五年汇报白皮书-by加玮.md"

# pie / ring → side-by-side; wide charts → stacked (image max)
SPLIT_CHARTS = {
    "c01-msg-type", "c02-groups", "c03-speaker-tier", "c11-l1-all",
    "c12-industry", "c14-pain",
}

CHART_RE = re.compile(
    r"!\[[^\]]*\]\((?:assets/charts/|images/)?(c\d{2}[^)\s]+?)(?:-\w+)?\.png\)",
    re.I,
)


def _chart_id(path: str) -> str | None:
    m = CHART_RE.search(path) or re.search(r"(c\d{2}[\w-]+)", path)
    return m.group(1) if m else None


def _bullets_from_block(body: str, limit: int = 4) -> list[str]:
    out: list[str] = []
    for line in body.splitlines():
        line = line.strip()
        if line.startswith("- "):
            t = line[2:].strip()
            if len(t) > 120:
                t = t[:117] + "…"
            out.append(t)
        if len(out) >= limit:
            break
    return out


def _data_line(body: str) -> str:
    m = re.search(r"\*\*数据：\*\*\s*(.+)", body)
    return m.group(1).strip() if m else ""


def parse_md(text: str) -> list[dict]:
    text = re.sub(r"\*读桑基图[^\n]*\*\s*\n", "", text)
    slides: list[dict] = []
    # Chapter curtains (# 一、…)
    for m in re.finditer(r"^# (一、|二、|三、|四、|五、|六、)(.+)$", text, re.M):
        slides.append({
            "kind": "hero",
            "theme": "hero light" if m.group(1) in ("一、", "三、", "五、") else "hero dark",
            "section": m.group(1) + m.group(2).strip(),
            "title": m.group(2).strip(),
            "lead": "",
            "points": [],
        })

    parts = re.split(r"\n(?=## )", text)

    slides.append({
        "kind": "hero",
        "theme": "hero dark",
        "section": "封面",
        "title": "342,260 条消息 · 赵岩数字营销实战群五年白皮书",
        "lead": "2021-04 — 2026-05 · 七班全量",
        "points": [],
    })

    for part in parts:
        if not part.strip().startswith("## "):
            continue
        lines = part.splitlines()
        h2 = lines[0][3:].strip()
        if h2 in ("摘要", "核心数据一览"):
            continue
        if h2.startswith("6."):
            continue

        section = ""
        title = h2
        body = "\n".join(lines[1:])
        sm = re.search(r"^### (.+)$", body, re.M)
        if sm:
            section = sm.group(1).strip()
        if not section and re.match(r"^4\.\d+", h2):
            section = f"第四篇 · {h2.split()[0]}"
        elif not section and h2.startswith(("1.", "2.", "3.")):
            section = h2

        chart_ids = list(dict.fromkeys(_chart_id(x) or "" for x in CHART_RE.findall(body)))
        chart_ids = [c for c in chart_ids if c]

        points: list[str] = []
        data = _data_line(body)
        if data:
            points.append(data[:140] + ("…" if len(data) > 140 else ""))

        for label in ("典型场景", "群内反复出现的建议", "在聊什么"):
            sub = re.search(
                rf"\*\*{re.escape(label)}[^*]*\*\*\s*\n((?:- .+\n?)+)",
                body,
            )
            if sub:
                points.extend(_bullets_from_block(sub.group(1), limit=4 - len(points)))

        if not points and "4." in h2:
            points = _bullets_from_block(body, 4)

        # table-only ## blocks (appendix style)
        if "|" in body and not chart_ids and len(points) < 2:
            rows = []
            for ln in body.splitlines():
                if ln.startswith("|") and "---" not in ln and "指标" not in ln:
                    cells = [c.strip() for c in ln.split("|")[1:-1]]
                    if len(cells) >= 2:
                        rows.append((cells[0], cells[1] if len(cells) > 1 else ""))
            if rows:
                slides.append({
                    "kind": "table",
                    "theme": "light",
                    "section": section or h2[:20],
                    "title": title,
                    "lead": "",
                    "points": [],
                    "rows": rows[:8],
                })
                continue

        if chart_ids:
            for cid in chart_ids:
                layout = "split" if cid in SPLIT_CHARTS else "stack"
                theme = "light" if len(slides) % 3 else "dark"
                slides.append({
                    "kind": "chart",
                    "theme": theme,
                    "section": section,
                    "title": title,
                    "lead": data[:100] if data and cid == chart_ids[0] else "",
                    "points": points[:4],
                    "chart": cid,
                    "layout": layout,
                })
        elif points or data or h2.startswith("4."):
            slides.append({
                "kind": "content",
                "theme": "light" if len(slides) % 2 else "dark",
                "section": section,
                "title": title,
                "lead": data[:120] if data else "",
                "points": points[:4],
            })

    # quotes from chapter 6
    if "# 六、" in text:
        qpart = text.split("# 六、", 1)[1]
        for m in re.finditer(
            r"### (.+?)\n\n> \*\*(.+?)\*\*[^「]*「([^」]+)」",
            qpart,
            re.S,
        ):
            slides.append({
                "kind": "quote",
                "theme": "dark",
                "section": f"第六篇 · {m.group(1).strip()}",
                "title": f"「{m.group(3).strip()}」",
                "lead": m.group(2).strip(),
                "points": [],
            })

    slides.append({
        "kind": "hero",
        "theme": "hero dark",
        "section": "收尾",
        "title": "Thank you",
        "lead": "加玮 · 2026",
        "points": [],
    })
    return slides


def load_slides() -> list[dict]:
    text = MD_PATH.read_text(encoding="utf-8")
    return parse_md(text)
