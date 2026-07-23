#!/usr/bin/env python3
"""Scaffold a run directory for a new atlas.

    python new_atlas.py --disease "plaque psoriasis" --scope indication

Creates:
    runs/<slug>/raw/          # cached API pulls go here
    runs/<slug>/atlas.json    # stub with meta + empty sources (build it up section by section)
    runs/<slug>/notes.md      # scratch notes / source log
and prints the slug.
"""
from __future__ import annotations

import argparse
import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import util  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--disease", required=True)
    ap.add_argument("--scope", choices=["indication", "therapeutic_area"], default="indication")
    ap.add_argument("--base", default="runs", help="base directory for run dirs (default: runs)")
    ap.add_argument("--generator", default="disease-atlas skill v0.1")
    args = ap.parse_args()

    slug = util.slugify(args.disease)
    run_dir = os.path.join(args.base, slug)
    raw_dir = os.path.join(run_dir, "raw")
    os.makedirs(raw_dir, exist_ok=True)

    atlas_path = os.path.join(run_dir, "atlas.json")
    if not os.path.exists(atlas_path):
        stub = {
            "schema_version": "1.0",
            "meta": {
                "disease": args.disease,
                "scope": args.scope,
                "generated": datetime.date.today().isoformat(),
                "generator": args.generator,
                "one_liner": "",
                "coverage_note": "",
            },
            "sources": [],
            "disclaimers": [
                "Informational only. Not medical or investment advice.",
                "Generated from public data and cited web research as of the date shown; verify before relying on any figure.",
            ],
        }
        util.dump_json(stub, atlas_path)

    notes_path = os.path.join(run_dir, "notes.md")
    if not os.path.exists(notes_path):
        with open(notes_path, "w", encoding="utf-8") as f:
            f.write(f"# Atlas notes — {args.disease}\n\n"
                    f"- slug: `{slug}`\n- scope: {args.scope}\n\n"
                    "## Source log\n(add each source as you use it)\n\n## Open questions / gaps\n")

    print(slug)
    print(f"run_dir: {run_dir}")
    print(f"atlas:   {atlas_path}")
    print(f"raw:     {raw_dir}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
