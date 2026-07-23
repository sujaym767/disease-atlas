#!/usr/bin/env python3
"""Fetch disease biology + drug mechanisms from the Open Targets Platform GraphQL API.

Two modes:
    # resolve a disease name to an EFO id (prints candidates)
    python fetch_open_targets.py --resolve "plaque psoriasis"

    # full pull: associated targets + knownDrugs, grouped by mechanism of action
    python fetch_open_targets.py --disease "plaque psoriasis" --out raw/opentargets.json
    python fetch_open_targets.py --efo EFO_0000676 --out raw/opentargets.json

`knownDrugs` (drug -> mechanismOfAction -> target -> phase) seeds the MoA landscape and
enriches the pipeline; `associatedTargets` seeds the biology panel. Stdlib-only, graceful.
"""
from __future__ import annotations

import argparse
import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib.http import FetchError, post_json  # noqa: E402
from lib import util  # noqa: E402

ENDPOINT = "https://api.platform.opentargets.org/api/v4/graphql"

SEARCH_Q = """
query Search($q: String!) {
  search(queryString: $q, entityNames: ["disease"], page: {index: 0, size: 6}) {
    hits { id name entity description }
  }
}"""

DATA_Q = """
query Atlas($efo: String!, $size: Int!) {
  disease(efoId: $efo) {
    id
    name
    description
    associatedTargets(page: {index: 0, size: 50}) {
      count
      rows { score target { id approvedSymbol approvedName } }
    }
    knownDrugs(size: $size) {
      count
      rows {
        drugId prefName drugType mechanismOfAction phase status
        targetId target { approvedSymbol }
        ctIds
        disease { id name }
      }
    }
  }
}"""


def _gql(query: str, variables: dict) -> dict:
    resp = post_json(ENDPOINT, {"query": query, "variables": variables})
    if resp and resp.get("errors"):
        raise FetchError("GraphQL: " + "; ".join(e.get("message", "?") for e in resp["errors"]))
    return (resp or {}).get("data") or {}


def resolve(disease: str) -> list[dict]:
    data = _gql(SEARCH_Q, {"q": disease})
    return (data.get("search") or {}).get("hits", [])


def _roll_up_drugs(rows: list[dict]):
    """Dedupe knownDrugs rows into drug-level assets and mechanism-of-action groups."""
    drugs: dict[str, dict] = {}
    moa: dict[str, dict] = {}
    for r in rows:
        did = r.get("drugId") or r.get("prefName")
        if not did:
            continue
        phase_schema = util.opentargets_phase_to_schema(r.get("phase"))
        mech = (r.get("mechanismOfAction") or "").strip() or "Unspecified mechanism"
        tgt = (r.get("target") or {}).get("approvedSymbol")

        d = drugs.setdefault(did, {
            "drug_id": did, "name": r.get("prefName"), "drug_type": r.get("drugType"),
            "phase": "preclinical", "status": r.get("status"),
            "mechanisms": set(), "targets": set(), "indications": set(), "ct_ids": set(),
        })
        d["phase"] = util.max_phase(d["phase"], phase_schema)
        if r.get("mechanismOfAction"):
            d["mechanisms"].add(r["mechanismOfAction"])
        if tgt:
            d["targets"].add(tgt)
        ind = (r.get("disease") or {}).get("name")
        if ind:
            d["indications"].add(ind)
        for c in (r.get("ctIds") or []):
            d["ct_ids"].add(c)

        m = moa.setdefault(mech, {
            "mechanism": mech, "targets": set(), "drug_types": set(),
            "phase": "preclinical", "drugs": set(),
        })
        m["phase"] = util.max_phase(m["phase"], phase_schema)
        if tgt:
            m["targets"].add(tgt)
        if r.get("drugType"):
            m["drug_types"].add(r["drugType"])
        if r.get("prefName"):
            m["drugs"].add(r["prefName"])

    drug_list = []
    for d in drugs.values():
        drug_list.append({
            "drug_id": d["drug_id"], "name": d["name"], "drug_type": d["drug_type"],
            "phase": d["phase"], "phase_num": util.phase_num(d["phase"]), "status": d["status"],
            "mechanisms": sorted(d["mechanisms"]), "targets": sorted(d["targets"]),
            "indications": sorted(d["indications"])[:15], "ct_ids": sorted(d["ct_ids"])[:20],
        })
    drug_list.sort(key=lambda x: (-x["phase_num"], x["name"] or ""))

    moa_list = []
    for m in moa.values():
        moa_list.append({
            "mechanism": m["mechanism"], "targets": sorted(m["targets"]),
            "drug_types": sorted(m["drug_types"]), "phase": m["phase"],
            "phase_num": util.phase_num(m["phase"]),
            "n_drugs": len(m["drugs"]), "drugs": sorted(m["drugs"])[:40],
        })
    moa_list.sort(key=lambda x: (-x["phase_num"], -x["n_drugs"]))
    return drug_list, moa_list


def fetch(disease: str | None, efo: str | None, size: int = 800) -> dict:
    result = {
        "source": "Open Targets Platform (GraphQL v4)",
        "endpoint": ENDPOINT,
        "disease": disease,
        "retrieved": datetime.date.today().isoformat(),
    }
    try:
        if not efo:
            hits = resolve(disease)
            result["resolved_candidates"] = hits[:6]
            if not hits:
                result["error"] = f"no EFO disease match for {disease!r}"
                result["count"] = 0
                return result
            efo = hits[0]["id"]
        result["efo_id"] = efo

        data = _gql(DATA_Q, {"efo": efo, "size": size})
        dis = data.get("disease")
        if not dis:
            result["error"] = f"no Open Targets disease for {efo}"
            result["count"] = 0
            return result

        result["disease_name"] = dis.get("name")
        result["description"] = dis.get("description")
        at = dis.get("associatedTargets") or {}
        result["targets"] = [
            {"symbol": (row.get("target") or {}).get("approvedSymbol"),
             "name": (row.get("target") or {}).get("approvedName"),
             "id": (row.get("target") or {}).get("id"),
             "association_score": round(row.get("score", 0), 4)}
            for row in at.get("rows", [])
        ]
        kd = dis.get("knownDrugs") or {}
        drugs, moa = _roll_up_drugs(kd.get("rows", []))
        result["known_drugs_total"] = kd.get("count")
        result["drugs"] = drugs
        result["moa_groups"] = moa
        result["count"] = len(drugs)
    except FetchError as e:
        result["error"] = str(e)
        result["count"] = 0
        print(f"WARN: {e}", file=sys.stderr)
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--disease", help="disease name (resolved to an EFO id)")
    ap.add_argument("--efo", help="EFO id directly (skips resolution)")
    ap.add_argument("--resolve", metavar="NAME", help="only resolve a name to EFO candidates")
    ap.add_argument("--out", help="write JSON here (default: stdout)")
    ap.add_argument("--size", type=int, default=800, help="max knownDrugs rows")
    args = ap.parse_args()

    if args.resolve:
        try:
            util.emit({"query": args.resolve, "candidates": resolve(args.resolve)}, args.out)
        except FetchError as e:
            util.emit({"query": args.resolve, "error": str(e), "candidates": []}, args.out)
        return 0

    if not (args.disease or args.efo):
        ap.error("provide --disease, --efo, or --resolve")
    util.emit(fetch(args.disease, args.efo, args.size), args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
