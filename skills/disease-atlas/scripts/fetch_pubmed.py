#!/usr/bin/env python3
"""Fetch key literature for a disease from Europe PMC (abstracts + citation counts).

    python fetch_pubmed.py --disease "plaque psoriasis" --focus "phase 3 pivotal" --out raw/literature.json

Europe PMC is preferred over raw NCBI E-utilities for simpler JSON. Sorted by citation
count to surface landmark papers for the evidence/biology panels. Stdlib-only, graceful.
"""
from __future__ import annotations

import argparse
import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib.http import FetchError, get_json  # noqa: E402
from lib import util  # noqa: E402

ENDPOINT = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"


def _build_query(disease: str, focus: str | None) -> str:
    q = f'"{disease}"'
    if focus:
        # OR-together the focus terms so any match boosts recall
        terms = " OR ".join(t.strip() for t in focus.split() if t.strip())
        if terms:
            q += f" AND ({terms})"
    q += " AND SRC:MED"  # restrict to MEDLINE-indexed
    return q


def _article_url(rec: dict) -> str | None:
    if rec.get("pmid"):
        return f"https://europepmc.org/article/MED/{rec['pmid']}"
    if rec.get("doi"):
        return f"https://doi.org/{rec['doi']}"
    return None


def fetch(disease: str, focus: str | None = None, page_size: int = 25) -> dict:
    result = {
        "source": "Europe PMC",
        "endpoint": ENDPOINT,
        "disease": disease,
        "retrieved": datetime.date.today().isoformat(),
    }
    params = {
        "query": _build_query(disease, focus),
        "format": "json",
        "pageSize": min(page_size, 100),
        "sort": "CITED desc",
        "resultType": "core",
    }
    try:
        data = get_json(ENDPOINT, params=params)
        result["total_matched"] = (data or {}).get("hitCount")
        articles = []
        for r in ((data or {}).get("resultList", {}) or {}).get("result", []):
            articles.append({
                "pmid": r.get("pmid"),
                "doi": r.get("doi"),
                "title": r.get("title"),
                "authors": r.get("authorString"),
                "journal": r.get("journalTitle"),
                "year": r.get("pubYear"),
                "cited_by": r.get("citedByCount"),
                "type": (r.get("pubTypeList", {}) or {}).get("pubType"),
                "url": _article_url(r),
                "abstract": (r.get("abstractText") or "")[:800] or None,
            })
        result["articles"] = articles
        result["count"] = len(articles)
    except FetchError as e:
        result["error"] = str(e)
        result["count"] = 0
        print(f"WARN: {e}", file=sys.stderr)
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--disease", required=True)
    ap.add_argument("--focus", help="extra terms OR'd in (e.g. 'phase 3 pivotal guideline')")
    ap.add_argument("--out", help="write JSON here (default: stdout)")
    ap.add_argument("--page-size", type=int, default=25)
    args = ap.parse_args()
    util.emit(fetch(args.disease, args.focus, args.page_size), args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
