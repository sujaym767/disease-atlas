#!/usr/bin/env python3
"""Fetch approved drugs, pharmacologic classes, and boxed warnings from openFDA drug labels.

    python fetch_openfda.py --disease "psoriasis" --out raw/openfda.json

Deduplicates labels into a `products` list (generic -> brands, manufacturers, routes,
established pharmacologic class, MoA class, boxed-warning flag) for the standard-of-care
panel and MoA validation. Optional OPENFDA_API_KEY env var raises the rate limit.
Stdlib-only, graceful.
"""
from __future__ import annotations

import argparse
import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib.http import FetchError, get_json  # noqa: E402
from lib import util  # noqa: E402

ENDPOINT = "https://api.fda.gov/drug/label.json"


def _first(v):
    if isinstance(v, list):
        return v[0] if v else None
    return v


def _uniq(seq):
    out = []
    for x in seq or []:
        if x and x not in out:
            out.append(x)
    return out


def _roll_up(results: list[dict]) -> list[dict]:
    products: dict[str, dict] = {}
    for r in results:
        of = r.get("openfda", {}) or {}
        generic = _first(of.get("generic_name")) or _first(of.get("substance_name"))
        brand = _first(of.get("brand_name"))
        key = (generic or brand or "").lower().strip()
        if not key:
            continue
        p = products.setdefault(key, {
            "generic": generic, "brands": [], "manufacturers": [], "routes": [],
            "pharm_class_epc": [], "pharm_class_moa": [], "has_boxed_warning": False,
            "indication_snippet": None,
        })
        for b in _uniq(of.get("brand_name")):
            if b not in p["brands"]:
                p["brands"].append(b)
        for m in _uniq(of.get("manufacturer_name")):
            if m not in p["manufacturers"]:
                p["manufacturers"].append(m)
        for rt in _uniq(of.get("route")):
            if rt not in p["routes"]:
                p["routes"].append(rt)
        for c in _uniq(of.get("pharm_class_epc")):
            if c not in p["pharm_class_epc"]:
                p["pharm_class_epc"].append(c)
        for c in _uniq(of.get("pharm_class_moa")):
            if c not in p["pharm_class_moa"]:
                p["pharm_class_moa"].append(c)
        if r.get("boxed_warning"):
            p["has_boxed_warning"] = True
        if not p["indication_snippet"]:
            ind = _first(r.get("indications_and_usage"))
            if ind:
                p["indication_snippet"] = ind.strip().replace("\n", " ")[:400]
    return sorted(products.values(), key=lambda x: (x["generic"] or "").lower())


def fetch(disease: str, limit: int = 100) -> dict:
    result = {
        "source": "openFDA (drug labels)",
        "endpoint": ENDPOINT,
        "disease": disease,
        "retrieved": datetime.date.today().isoformat(),
    }
    params = {"search": f'indications_and_usage:"{disease}"', "limit": min(limit, 100)}
    api_key = os.environ.get("OPENFDA_API_KEY")
    if api_key:
        params["api_key"] = api_key
    try:
        data = get_json(ENDPOINT, params=params)
        results = (data or {}).get("results", []) or []
        result["total_matched"] = ((data or {}).get("meta", {}).get("results", {}) or {}).get("total")
        result["products"] = _roll_up(results)
        result["count"] = len(result["products"])
    except FetchError as e:
        # openFDA returns HTTP 404 when a search has zero matches — treat as "no data".
        msg = str(e)
        if "HTTP 404" in msg:
            result["products"] = []
            result["count"] = 0
            result["note"] = "no openFDA labels matched this indication phrase"
        else:
            result["error"] = msg
            result["count"] = 0
            print(f"WARN: {e}", file=sys.stderr)
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--disease", required=True, help="indication phrase to match in labels")
    ap.add_argument("--out", help="write JSON here (default: stdout)")
    ap.add_argument("--limit", type=int, default=100)
    args = ap.parse_args()
    util.emit(fetch(args.disease, args.limit), args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
