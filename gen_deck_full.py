#!/usr/bin/env python3
"""Magazine PPT from whitepaper MD — dense layout, theme-matched chart PNGs."""
from __future__ import annotations

import shutil
from pathlib import Path

from md_slide_builder import load_slides

ROOT = Path(__file__).parent
TEMPLATE = Path("/Users/jiaweiwang/.codex/skills/magazine-web-ppt/assets/template.html")
OUT = ROOT / "ppt" / "index.html"
IMG = "images"

DECK_CSS = """
  .slide.slide-dense{padding:4.5vh 5vw 8vh 5vw}
  .slide.slide-dense::before{background:rgba(var(--paper-rgb),.88)}
  .slide.slide-dense.dark::before{background:rgba(var(--ink-rgb),.88)}
  .slide.slide-dense .dense-body{flex:1;display:flex;min-height:0;gap:2vw;margin-top:1vh}
  .slide.slide-dense.layout-stack .dense-body{flex-direction:column}
  .slide.slide-dense.layout-split .dense-body{flex-direction:row;align-items:stretch}
  .slide.slide-dense .dense-head{flex:0 0 auto;display:flex;flex-direction:column;gap:.8vh;max-height:32vh}
  .slide.slide-dense.layout-split .dense-head{width:36%;min-width:28%;max-height:none;padding-right:1vw}
  .slide.slide-dense .dense-title{font-family:var(--serif-zh);font-weight:700;font-size:clamp(1.15rem,2.55vw,2.15rem);line-height:1.14;letter-spacing:-.01em}
  .slide.slide-dense .dense-lead{font-family:var(--sans-zh);font-size:max(13px,.95vw);line-height:1.45;opacity:.82}
  .slide.slide-dense .dense-points{margin:.4vh 0 0;padding-left:1.15em;font-family:var(--sans-zh);font-size:max(12px,.88vw);line-height:1.42;opacity:.88}
  .slide.slide-dense .dense-points li{margin-bottom:.28em}
  .slide.slide-dense .dense-media{flex:1;min-height:0;display:flex;align-items:center;justify-content:center;background:transparent}
  .slide.slide-dense.layout-stack .dense-media{min-height:48vh}
  .slide.slide-dense.layout-split .dense-media{width:64%}
  .slide.slide-dense .dense-media img{max-width:100%;max-height:100%;width:auto;height:auto;object-fit:contain;display:block}
  .slide.slide-dense .kicker{margin-bottom:.6vh}
  .slide.slide-dense .rowline{padding:1.4vh 0}
  .slide.slide-dense .rowline .k{font-size:max(13px,1.05vw)}
  .slide.slide-dense .rowline .v{font-size:max(12px,.9vw)}
"""


def _theme_class(theme: str) -> str:
    if theme.startswith("hero"):
        return theme
    return "dark" if theme == "dark" else "light"


def _chart_file(chart: str, theme: str) -> str:
    base = chart.replace(".png", "")
    t = "dark" if theme == "dark" else "light"
    name = f"{base}-{t}.png"
    if not (ROOT / "assets" / "charts" / name).exists():
        name = f"{base}.png"
    return name


def _points_html(points: list[str]) -> str:
    if not points:
        return ""
    items = "".join(f"<li>{p}</li>" for p in points)
    return f'<ul class="dense-points" data-anim>{items}</ul>'


def _rows_html(rows: list) -> str:
    d = "div"
    lines = [f'<{d} class="col" style="margin-top:1vh;flex:1;min-height:0;overflow:auto" data-anim>']
    for item in rows:
        if isinstance(item, tuple) and len(item) >= 2:
            k, v = item[0], item[1]
            lines.append(
                f'<{d} class="rowline"><{d} class="k">{k}</{d}><{d} class="v">{v}</{d}></{d}>'
            )
    lines.append(f"</{d}>")
    return "\n".join(lines)


def render_slide(s: dict, idx: int, total: int) -> str:
    d = "div"
    theme = _theme_class(s.get("theme", "light"))
    kind = s.get("kind", "content")
    pg = f"{idx:02d}/{total:02d}"
    section = s.get("section", "")
    title = s.get("title", "")
    lead = s.get("lead", "")
    points = s.get("points", [])
    extra = ' data-animate="quote"' if kind == "quote" else ""

    if kind == "hero":
        hero_cls = s.get("theme", "hero dark")
        return f"""<section class="slide {hero_cls}"{extra}>
  <{d} class="chrome"><{d}>{section or ' '}</{d}><{d}>{pg}</{d}></{d}>
  <{d} class="frame center" style="justify-content:center;text-align:center;gap:2.5vh">
    <{d} class="kicker" data-anim>{section}</{d}>
    <h1 class="display-zh" data-anim>{title}</h1>
    <p class="lead" data-anim>{lead}</p>
  </{d}>
  <{d} class="foot"><{d}>{section}</{d}><{d}>{pg}</{d}></{d}>
</section>"""

    if kind == "quote":
        return f"""<section class="slide dark slide-dense"{extra}>
  <{d} class="chrome"><{d}>{section}</{d}><{d}>{pg}</{d}></{d}>
  <{d} class="frame center" style="justify-content:center;text-align:center;gap:2vh;padding:6vh 8vw">
    <{d} class="kicker" data-anim>{section}</{d}>
    <h2 class="dense-title" style="font-style:italic;text-align:center" data-anim>{title}</h2>
    <p class="dense-lead" data-anim>{lead}</p>
  </{d}>
  <{d} class="foot"><{d}>{section}</{d}><{d}>{pg}</{d}></{d}>
</section>"""

    layout = s.get("layout", "stack")
    chart = s.get("chart", "")
    img_html = ""
    if kind == "chart" and chart:
        fn = _chart_file(chart, theme)
        img_html = f'<{d} class="dense-media" data-anim><img src="{IMG}/{fn}" alt=""></{d}>'

    body_layout = f"layout-{layout}" if kind == "chart" else ""
    rows = s.get("rows", [])
    inner = f"""<{d} class="dense-head" data-anim>
      <{d} class="kicker">{section}</{d}>
      <h2 class="dense-title">{title}</h2>
      {f'<p class="dense-lead">{lead}</p>' if lead else ''}
      {_points_html(points)}
    </{d}>
    {img_html}
    {_rows_html(rows) if rows and kind == "table" else ''}"""

    if kind == "table" and rows:
        inner = f"""<{d} class="dense-head" data-anim>
      <{d} class="kicker">{section}</{d}>
      <h2 class="dense-title">{title}</h2>
    </{d}>
    {_rows_html(rows)}"""

    return f"""<section class="slide {theme} slide-dense {body_layout}"{extra}>
  <{d} class="chrome"><{d}>{section[:28]}</{d}><{d}>{pg}</{d}></{d}>
  <{d} class="dense-body">{inner}</{d}>
  <{d} class="foot"><{d}>{section.split('·')[-1].strip() if '·' in section else section[:12]}</{d}><{d}>{pg}</{d}></{d}>
</section>"""


def main():
    dest = ROOT / "ppt" / IMG
    dest.mkdir(parents=True, exist_ok=True)
    for png in (ROOT / "assets" / "charts").glob("c*.png"):
        shutil.copy2(png, dest / png.name)

    specs = load_slides()
    total = len(specs)
    slides_html = "\n\n".join(render_slide(s, i + 1, total) for i, s in enumerate(specs))

    html = TEMPLATE.read_text(encoding="utf-8")
    html = html.replace(
        "--ink:#0a0a0b;\n    --ink-rgb:10,10,11;\n    --paper:#f1efea;\n    --paper-rgb:241,239,234;",
        "--ink:#0a1f3d;\n    --ink-rgb:10,31,61;\n    --paper:#f1f3f5;\n    --paper-rgb:241,243,245;\n    --paper-tint:#e4e8ec;\n    --ink-tint:#152a4a;",
    )
    html = html.replace("</style>", DECK_CSS + "\n</style>", 1)
    html = html.replace("[必填] 替换为 PPT 标题 · Deck Title", "赵岩的数字营销实战群 · 五年白皮书")
    html = html.replace("<!-- SLIDES_HERE -->", slides_html)
    html = html.replace("./assets/motion.min.js", "./motion.min.js")
    OUT.write_text(html, encoding="utf-8")
    print(f"Built {OUT} — {total} slides")


if __name__ == "__main__":
    main()
