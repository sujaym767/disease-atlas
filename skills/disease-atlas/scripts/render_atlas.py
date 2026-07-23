#!/usr/bin/env python3
"""Render an atlas.json into a single self-contained HTML file.

    python render_atlas.py runs/<slug>/atlas.json --out runs/<slug>/atlas_<slug>.html

The output inlines all CSS/JS (from assets/atlas_template.html) and embeds the atlas data
as a JSON <script> block — no external requests at view time. Stdlib only.
"""
from __future__ import annotations

import argparse
import datetime
import html
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import util  # noqa: E402

DEFAULT_TEMPLATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "atlas_template.html")


def render(atlas: dict, template: str) -> str:
    meta = atlas.get("meta", {}) or {}
    disease = meta.get("disease", "Disease")
    title = f"{disease} — Disease Atlas"

    # Compact JSON, then neutralize any "</" so it cannot terminate the <script> tag.
    # "<\/" is a valid JSON escape for "/", so JSON.parse still round-trips it.
    data = json.dumps(atlas, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")

    out = template.replace("__ATLAS_TITLE__", html.escape(title))
    out = out.replace("__ATLAS_DATA_JSON__", data)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("atlas", help="path to atlas.json")
    ap.add_argument("--out", help="output HTML path (default: alongside atlas.json)")
    ap.add_argument("--template", default=DEFAULT_TEMPLATE)
    args = ap.parse_args()

    atlas = util.load_json(args.atlas)
    with open(args.template, "r", encoding="utf-8") as f:
        template = f.read()

    out_path = args.out
    if not out_path:
        slug = util.slugify((atlas.get("meta", {}) or {}).get("disease", "atlas"))
        out_path = os.path.join(os.path.dirname(os.path.abspath(args.atlas)), f"atlas_{slug}.html")

    rendered = render(atlas, template)
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(rendered)

    kb = len(rendered.encode("utf-8")) / 1024
    print(f"wrote {out_path} ({kb:.0f} KB) · generated {atlas.get('meta',{}).get('generated', datetime.date.today().isoformat())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
