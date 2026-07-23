#!/usr/bin/env python3
"""Validate an atlas.json against the v1 schema (references/atlas-schema.md).

    python validate_atlas.py runs/<slug>/atlas.json

Errors (exit 1): structural problems that break rendering or signal fabrication risk —
missing required fields, bad enum values, duplicate/missing ids, dangling source or drug
refs. Warnings (exit 0): quality nudges — uncited numbers, empty panels. Stdlib only.
"""
from __future__ import annotations

import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import util  # noqa: E402

PHASES = {"preclinical", "phase1", "phase1_2", "phase2", "phase2_3", "phase3", "filed", "approved", "discontinued"}
VALIDATION = {"validated", "emerging", "unproven", "failed"}
SCOPES = {"indication", "therapeutic_area"}
SOURCE_TYPES = {"api", "web", "publication", "label", "guideline", "filing", "estimate"}
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

errors: list[str] = []
warnings: list[str] = []


def err(msg): errors.append(msg)
def warn(msg): warnings.append(msg)


def _walk_source_refs(node, source_ids, path="$"):
    """Recursively verify every `sources` array holds ids that exist in top-level sources[]."""
    if isinstance(node, dict):
        for k, v in node.items():
            if k == "sources" and isinstance(v, list):
                for ref in v:
                    if ref not in source_ids:
                        err(f"{path}.sources references unknown source id {ref!r}")
            else:
                _walk_source_refs(v, source_ids, f"{path}.{k}")
    elif isinstance(node, list):
        for i, item in enumerate(node):
            _walk_source_refs(item, source_ids, f"{path}[{i}]")


def validate(atlas: dict) -> None:
    # --- required top-level ---
    if not isinstance(atlas, dict):
        err("root is not a JSON object")
        return
    meta = atlas.get("meta")
    if not isinstance(meta, dict):
        err("missing required object: meta")
    else:
        if not meta.get("disease"):
            err("meta.disease is required")
        gen = meta.get("generated")
        if not gen or not ISO_DATE.match(str(gen)):
            err(f"meta.generated must be an ISO date (YYYY-MM-DD); got {gen!r}")
        if meta.get("scope") and meta["scope"] not in SCOPES:
            err(f"meta.scope must be one of {sorted(SCOPES)}; got {meta['scope']!r}")
        if not meta.get("coverage_note"):
            warn("meta.coverage_note is empty — add an honest note on data completeness")

    # --- sources ---
    sources = atlas.get("sources")
    source_ids = set()
    if not isinstance(sources, list):
        err("missing required list: sources (may be empty for a stub)")
    else:
        for i, s in enumerate(sources):
            if not isinstance(s, dict) or not s.get("id"):
                err(f"sources[{i}] must be an object with an 'id'")
                continue
            if s["id"] in source_ids:
                err(f"duplicate source id {s['id']!r}")
            source_ids.add(s["id"])
            if s.get("type") and s["type"] not in SOURCE_TYPES:
                warn(f"sources[{i}].type {s['type']!r} not in {sorted(SOURCE_TYPES)}")
            if not s.get("url") and s.get("type") not in (None, "estimate"):
                warn(f"sources[{i}] ({s['id']}) has no url")

    # --- dangling source refs anywhere ---
    if isinstance(sources, list):
        _walk_source_refs({k: v for k, v in atlas.items() if k != "sources"}, source_ids)

    # --- pipeline.assets ---
    asset_ids = set()
    pipeline = atlas.get("pipeline") or {}
    assets = pipeline.get("assets") if isinstance(pipeline, dict) else None
    if isinstance(assets, list):
        for i, a in enumerate(assets):
            if not isinstance(a, dict):
                err(f"pipeline.assets[{i}] is not an object")
                continue
            if not a.get("id"):
                err(f"pipeline.assets[{i}] missing 'id'")
            elif a["id"] in asset_ids:
                err(f"duplicate asset id {a['id']!r}")
            else:
                asset_ids.add(a["id"])
            if not a.get("name"):
                err(f"pipeline.assets[{i}] missing 'name'")
            if a.get("phase") and a["phase"] not in PHASES:
                err(f"pipeline.assets[{i}].phase {a['phase']!r} not in {sorted(PHASES)}")

    # --- moa_landscape ---
    moa = atlas.get("moa_landscape")
    if isinstance(moa, list):
        for i, m in enumerate(moa):
            if not isinstance(m, dict):
                err(f"moa_landscape[{i}] is not an object")
                continue
            if not m.get("class"):
                err(f"moa_landscape[{i}] missing 'class'")
            vs = m.get("validation_status")
            if vs and vs not in VALIDATION:
                err(f"moa_landscape[{i}].validation_status {vs!r} not in {sorted(VALIDATION)}")
            for ref in m.get("drugs", []) or []:
                if asset_ids and ref not in asset_ids:
                    warn(f"moa_landscape[{i}] ({m.get('class')}) drug ref {ref!r} not in pipeline.assets")

    # --- quality: uncited numeric claims ---
    for i, stat in enumerate(atlas.get("headline_stats", []) or []):
        if isinstance(stat, dict) and stat.get("value") and not stat.get("sources"):
            warn(f"headline_stats[{i}] ({stat.get('label')}) has a value but no sources")
    market = atlas.get("market") or {}
    cs = market.get("current_size") if isinstance(market, dict) else None
    if isinstance(cs, dict) and cs.get("value") and not cs.get("sources"):
        warn("market.current_size has a value but no sources")

    # --- empty-panel nudges ---
    for panel in ("overview", "epidemiology", "standard_of_care", "moa_landscape", "market"):
        v = atlas.get(panel)
        if v in (None, {}, []):
            warn(f"panel {panel!r} is empty")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("atlas", help="path to atlas.json")
    args = ap.parse_args()
    if not os.path.exists(args.atlas):
        print(f"ERROR: no such file: {args.atlas}", file=sys.stderr)
        return 2
    try:
        atlas = util.load_json(args.atlas)
    except Exception as e:
        print(f"ERROR: could not parse JSON: {e}", file=sys.stderr)
        return 2

    validate(atlas)

    for w in warnings:
        print(f"WARN:  {w}")
    for e in errors:
        print(f"ERROR: {e}")
    print(f"\n{len(errors)} error(s), {len(warnings)} warning(s)")
    if errors:
        return 1
    print("OK — atlas.json is structurally valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
