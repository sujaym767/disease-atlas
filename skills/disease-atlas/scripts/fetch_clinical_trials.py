#!/usr/bin/env python3
"""Fetch the interventional clinical pipeline for a disease from ClinicalTrials.gov API v2.

Emits per-trial records AND a deduplicated `assets` roll-up (each intervention with its
highest phase across trials, sponsors, and NCT ids) — the backbone of the pipeline panel.

    python fetch_clinical_trials.py --disease "plaque psoriasis" --out raw/trials.json

Standalone, stdlib-only, degrades gracefully (emits an `error` field rather than crashing).
"""
from __future__ import annotations

import argparse
import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib.http import FetchError, get_json  # noqa: E402
from lib import util  # noqa: E402

ENDPOINT = "https://clinicaltrials.gov/api/v2/studies"
_SKIP = ("placebo", "standard of care", "best supportive care", "saline", "vehicle")
_DRUG_TYPES = {"DRUG", "BIOLOGICAL", "GENETIC", "COMBINATION_PRODUCT"}


def _g(d: dict, *path, default=None):
    cur = d
    for key in path:
        if isinstance(cur, dict) and key in cur:
            cur = cur[key]
        else:
            return default
    return cur


def _extract(study: dict) -> dict:
    ps = study.get("protocolSection", {})
    interventions = []
    for iv in _g(ps, "armsInterventionsModule", "interventions", default=[]) or []:
        interventions.append({"type": iv.get("type"), "name": iv.get("name")})
    return {
        "nct_id": _g(ps, "identificationModule", "nctId"),
        "title": _g(ps, "identificationModule", "briefTitle"),
        "phases": _g(ps, "designModule", "phases", default=[]) or [],
        "study_type": _g(ps, "designModule", "studyType"),
        "status": _g(ps, "statusModule", "overallStatus"),
        "start": _g(ps, "statusModule", "startDateStruct", "date"),
        "primary_completion": _g(ps, "statusModule", "primaryCompletionDateStruct", "date"),
        "lead_sponsor": _g(ps, "sponsorCollaboratorsModule", "leadSponsor", "name"),
        "conditions": _g(ps, "conditionsModule", "conditions", default=[]) or [],
        "interventions": interventions,
    }


def _roll_up_assets(records: list[dict]) -> list[dict]:
    assets: dict[str, dict] = {}
    for rec in records:
        phase_schema = util.ctgov_phase_to_schema(rec.get("phases"))
        for iv in rec.get("interventions", []):
            name = (iv.get("name") or "").strip()
            typ = iv.get("type")
            if not name or typ not in _DRUG_TYPES:
                continue
            norm = util.normalize_drug_name(name)
            if not norm or any(s in norm for s in _SKIP):
                continue
            a = assets.setdefault(norm, {
                "name": name, "normalized": norm, "types": set(),
                "phase": "preclinical", "sponsors": set(), "nct_ids": [],
                "statuses": set(),
            })
            a["types"].add(typ)
            a["phase"] = util.max_phase(a["phase"], phase_schema)
            if rec.get("lead_sponsor"):
                a["sponsors"].add(rec["lead_sponsor"])
            if rec.get("status"):
                a["statuses"].add(rec["status"])
            if rec.get("nct_id"):
                a["nct_ids"].append(rec["nct_id"])
    out = []
    for a in assets.values():
        out.append({
            "name": a["name"], "normalized": a["normalized"],
            "types": sorted(a["types"]), "phase": a["phase"],
            "phase_num": util.phase_num(a["phase"]),
            "sponsors": sorted(a["sponsors"]), "statuses": sorted(a["statuses"]),
            "nct_ids": a["nct_ids"][:25], "n_trials": len(a["nct_ids"]),
        })
    out.sort(key=lambda x: (-x["phase_num"], -x["n_trials"]))
    return out


def fetch(disease: str, page_size: int = 1000, max_pages: int = 3) -> dict:
    result = {
        "source": "ClinicalTrials.gov API v2",
        "endpoint": ENDPOINT,
        "disease": disease,
        "retrieved": datetime.date.today().isoformat(),
    }
    records: list[dict] = []
    page_token = None
    try:
        for _ in range(max_pages):
            params = {
                "query.cond": disease,
                "filter.advanced": "AREA[StudyType]INTERVENTIONAL",
                "pageSize": page_size,
                "countTotal": "true",
            }
            if page_token:
                params["pageToken"] = page_token
            data = get_json(ENDPOINT, params=params)
            if not data:
                break
            result.setdefault("total_matched", data.get("totalCount"))
            for study in data.get("studies", []):
                records.append(_extract(study))
            page_token = data.get("nextPageToken")
            if not page_token:
                break
    except FetchError as e:
        result["error"] = str(e)
        print(f"WARN: {e}", file=sys.stderr)

    result["count"] = len(records)
    result["assets"] = _roll_up_assets(records)
    result["records"] = records
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--disease", required=True, help="condition / disease name to query")
    ap.add_argument("--out", help="write JSON here (default: stdout)")
    ap.add_argument("--page-size", type=int, default=1000)
    ap.add_argument("--max-pages", type=int, default=3, help="up to page-size*max-pages trials")
    args = ap.parse_args()
    util.emit(fetch(args.disease, args.page_size, args.max_pages), args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
