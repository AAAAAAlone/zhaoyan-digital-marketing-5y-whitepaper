#!/usr/bin/env python3
"""Clean MD: drop meta read-hints; use local chart paths; keep tables."""
import re
from pathlib import Path

ROOT = Path(__file__).parent
MD = ROOT / "赵岩的数字营销实战群-五年汇报白皮书-by加玮.md"
RAW = "https://raw.githubusercontent.com/AAAAAAlone/zhaoyan-digital-marketing-5y-whitepaper/main/assets/charts/"


def main():
    text = MD.read_text(encoding="utf-8")
    text = re.sub(r"\*读桑基图[^\n]*\*\s*\n", "", text)
    text = text.replace(RAW, "assets/charts/")
    text = re.sub(r"!\[([^\]]*)\]\(assets/charts/([^)]+)\)", r"![\1](assets/charts/\2)", text)
  # normalize duplicate blank lines
    text = re.sub(r"\n{4,}", "\n\n\n", text)
    MD.write_text(text, encoding="utf-8")
    print("fixed", MD)


if __name__ == "__main__":
    main()
