#!/usr/bin/env python3
"""Copy canonical stats into assets/data for GitHub + MD references."""
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).parent
DATA = ROOT / "assets" / "data"
DATA.mkdir(parents=True, exist_ok=True)

exp = ROOT / "expand-stats.json"
if exp.exists():
    shutil.copy2(exp, DATA / "expand-stats.json")

# Re-run export manifest if present
manifest = DATA / "manifest.json"
if not manifest.exists():
    print("Run export_all_charts.py first for manifest.json")

print("Synced", list(DATA.glob("*.json")))
