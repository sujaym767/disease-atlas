#!/usr/bin/env python3
"""compile_atlas.py — the atlas COMPILER.

Read a semantic `atlas.json` (what the atlas-research skill produces) and author the
property graph (`graph.json`) that the interactive template renders. This is the general,
indication-agnostic form of the psoriasis prototype's build_deep.py: nothing is hardcoded;
every node/edge and every panel's data comes from atlas.json.

Two responsibilities:
  (A) AUTHOR the property graph — turn pipeline.assets / companies / moa_landscape /
      biology_graph / catalysts / deals into typed nodes + labelled edges (Drug, Company,
      MoAClass, Target, Modality, MarketSegment, Catalyst, Deal, Biology, Indication).
  (B) PASS THROUGH the render sections — strategy_map, biology signal_path, market_research
      (forecast / funnel / access / competitive), response_kinetics, trials, glossary, SoC,
      sites, market_share — into graph.json top-level, lightly normalized.

Every section is optional: a thin atlas still compiles, and the template shows honest empty
states for missing regions (golden rule: degrade gracefully). Stdlib only.

    python compile_atlas.py runs/<slug>/atlas.json --out runs/<slug>/graph.json
"""
import argparse, json, os, re, sys

PALETTE = ["--s1", "--s2", "--s5", "--s3", "--s7", "--s4", "--s6", "--s8", "--sN", "--sN"]
PHASE_NUM = {"approved": 4, "filed": 3.7, "phase3": 3, "phase2_3": 2.5, "phase2": 2,
             "phase1_2": 1.5, "phase1": 1, "preclinical": 0, "discontinued": -1}


def slug(s):
    return re.sub(r"-{2,}", "-", re.sub(r"[^a-z0-9]+", "-", (s or "").lower())).strip("-")


def compile_atlas(atlas):
    meta_in = atlas.get("meta", {})
    disease = meta_in.get("disease", "Disease")

    nodes, edges = {}, []

    def node(nid, ntype, label, attrs=None, sources=None):
        nodes[nid] = {"id": nid, "type": ntype, "label": label,
                      "attrs": attrs or {}, "sources": sources or []}
        return nid

    def edge(t, s, tg, a=None):
        edges.append({"type": t, "source": s, "target": tg, "attrs": a or {}})

    comp_ids = {}

    def company(name):
        if not name:
            return None
        if name in comp_ids:
            return comp_ids[name]
        return comp_ids.setdefault(name, node("company:" + slug(name), "Company", name, {"type": "company"}))

    IND = node("ind:" + slug(disease), "Indication", disease, {"area": meta_in.get("area", "")})

    # ---- families (color lanes). Prefer an explicit families[]; else derive from moa_landscape. ----
    fams_in = atlas.get("families")
    moa_land = atlas.get("moa_landscape", []) or []
    if not fams_in:
        fams_in = [{"key": (m.get("family_key") or slug(m.get("class", ""))), "label": m.get("class"),
                    "colorVar": m.get("colorVar"), "order": i + 1, "anchor": m.get("anchor")}
                   for i, m in enumerate(moa_land)]
    FAM = {}
    for i, f in enumerate(sorted(fams_in, key=lambda x: x.get("order", 999))):
        key = f.get("key") or slug(f.get("label", "fam%d" % i))
        FAM[key] = {"label": f.get("label", key), "colorVar": f.get("colorVar") or PALETTE[i % len(PALETTE)],
                    "order": f.get("order", i + 1), "anchor": f.get("anchor")}

    # class-level safety: explicit atlas.safety, else moa_landscape[].safety
    SAFETY = dict(atlas.get("safety") or {})
    for m in moa_land:
        if m.get("safety") and m.get("family_key"):
            SAFETY.setdefault(m["family_key"], m["safety"])

    # ---- MoAClass nodes ----
    for k, f in FAM.items():
        node("moa:" + k, "MoAClass", f["label"],
             {"family_key": k, "colorVar": f["colorVar"], "order": f["order"], "safety": SAFETY.get(k)})

    # ---- market segments (mild / systemic-eligible) ----
    node("seg:mild", "MarketSegment", "Mild (topical-managed)", {"share_pct": 80})
    node("seg:modsev", "MarketSegment", "Moderate-to-severe (systemic-eligible)", {"share_pct": 20})

    # ---- Drug nodes + edges from pipeline.assets ----
    assets = (atlas.get("pipeline", {}) or {}).get("assets", []) or []
    for d in assets:
        name = d.get("name")
        if not name:
            continue
        did = "drug:" + slug(name)
        phase = d.get("phase", "phase2")
        fam = d.get("family_key")
        eff = d.get("efficacy", {}) or {}
        attrs = {
            "brand": d.get("brand"), "sub": d.get("sub_class"), "sub_class": d.get("sub_class"),
            "route": d.get("route"), "dose": d.get("dose"), "appr": d.get("approval_year"),
            "bios": d.get("biosimilar"), "combo": d.get("is_combo", False),
            "disc": phase == "discontinued", "note": d.get("note"),
            "mod": d.get("modality"), "modality": d.get("modality"),
            "moa_family": FAM.get(fam, {}).get("label"), "highest_phase": phase,
            "phase_num": d.get("phase_num", PHASE_NUM.get(phase, 2)),
            "p75": eff.get("p75"), "p90": eff.get("p90"), "p100": eff.get("p100"),
        }
        if d.get("annual_sales_usd_m") is not None:
            attrs["sales"] = d["annual_sales_usd_m"]
            attrs["annual_sales_usd_m"] = d["annual_sales_usd_m"]
            attrs["sales_year"] = d.get("sales_year")
            attrs["syr"] = d.get("sales_year")
        if d.get("detail"):
            attrs["detail"] = d["detail"]
        attrs = {k: v for k, v in attrs.items() if v is not None}
        node(did, "Drug", name, attrs, d.get("sources", []))
        edge("DEVELOPED_BY", did, company(d.get("company")))
        if fam and "moa:" + fam in nodes:
            edge("HAS_MECHANISM", did, "moa:" + fam)
        edge("DEVELOPED_IN", did, IND, {"phase": phase, "approved": phase == "approved"})
        tgt = d.get("target")
        if tgt and re.match(r"^[A-Za-z0-9]+$", tgt):
            edge("HITS", did, node("target:" + tgt, "Target", tgt, {}))
        mod = d.get("modality")
        if mod:
            edge("HAS_MODALITY", did, node("modality:" + slug(mod), "Modality", mod, {}))
        if fam in ("topical", "steroid"):
            edge("SERVES", did, "seg:mild")
        elif fam == "conv":
            edge("SERVES", did, "seg:mild"); edge("SERVES", did, "seg:modsev")
        else:
            edge("SERVES", did, "seg:modsev")

    # ---- Biology graph (cells / cytokines / intracellular) + cascade + bridges ----
    bio = atlas.get("biology_graph", {}) or {}
    for b in bio.get("nodes", []):
        node("bio:" + b["id"], "Biology", b.get("label", b["id"]),
             {k: v for k, v in {"kind": b.get("kind"), "pos": b.get("pos"),
                                "description": b.get("description")}.items() if v is not None})
    for e in bio.get("edges", []):
        s, t = "bio:" + e["source"], "bio:" + e["target"]
        if s in nodes and t in nodes:
            edge(e["type"], s, t)
    for sym, biok in (bio.get("target_bio") or {}).items():
        if "target:" + sym in nodes and "bio:" + biok in nodes:
            edge("PART_OF", "target:" + sym, "bio:" + biok)
    for fk, biok in (bio.get("anchors") or {}).items():
        if "moa:" + fk in nodes and "bio:" + biok in nodes:
            edge("ACTS_ON", "moa:" + fk, "bio:" + biok)

    # ---- Catalysts ----
    for i, c in enumerate(atlas.get("catalysts", []) or [], 1):
        cid = node("catalyst:c%d" % i, "Catalyst", c.get("event", "catalyst"),
                   {"date": c.get("date"), "kind": c.get("kind"), "significance": c.get("significance"),
                    "company": c.get("company")}, c.get("sources", []))
        asset = c.get("asset")
        if asset and "drug:" + slug(asset) in nodes:
            edge("HAS_CATALYST", "drug:" + slug(asset), cid)

    # ---- Deals ----
    for i, d in enumerate(atlas.get("deals", []) or [], 1):
        dt = str(d.get("date", ""))
        dl = node("deal:d%d" % i, "Deal", "%s ← %s" % (d.get("acquirer", "?"), d.get("counterparty", "?")),
                  {"value": d.get("value"), "year": int(dt[:4]) if dt[:4].isdigit() else None,
                   "date": d.get("date"), "category": d.get("category"), "stage": d.get("stage"),
                   "kind": d.get("category"), "note": d.get("note"),
                   "counterparty": d.get("counterparty"), "acquirer": d.get("acquirer"), "asset": d.get("asset")})
        a = company(d.get("acquirer"))
        if a:
            edge("PARTY_TO", a, dl, {"role": "acquirer"})
        if d.get("asset") and "drug:" + slug(d["asset"]) in nodes:
            edge("INVOLVES", dl, "drug:" + slug(d["asset"]))

    # ---------- (B) assemble graph.json (author + passthrough) ----------
    soc_in = atlas.get("standard_of_care", {}) or {}
    rk = atlas.get("response_kinetics")
    mr = atlas.get("market_research", {}) or {}
    tf = atlas.get("trials_focus", {}) or {}
    bio_sp = [{"from": "bio:" + s["from"], "to": "bio:" + s["to"], "label": s.get("label", "")}
              for s in bio.get("signal_path", [])]

    graph = {
        "meta": {
            "scope": meta_in.get("scope", "indication"), "focus": disease,
            "generated": meta_in.get("generated"), "as_of": meta_in.get("as_of"),
            "one_liner": meta_in.get("one_liner", ""),
            "sales_note": meta_in.get("sales_note", ""),
            "headline_stats": meta_in.get("headline_stats", []),
            "mechanism_label": meta_in.get("mechanism_label"),
            "efficacy_label": meta_in.get("efficacy_label"),
        },
        "families": [{"key": k, "label": f["label"], "colorVar": f["colorVar"],
                      "order": f["order"], "anchor": f.get("anchor") or "th17"} for k, f in FAM.items()],
        "epi": atlas.get("epidemiology", {}),
        "sites": atlas.get("sites", []),
        "deals": atlas.get("deals", []),
        "soc": [{"tier": s.get("tier"), "label": s.get("label"), "agents": s.get("agents"),
                 "note": s.get("note"), "colorVar": s.get("colorVar")} for s in soc_in.get("lines", [])],
        "soc_note": soc_in.get("note"),
        "glossary": atlas.get("glossary", []),
        "trials": [dict(zip(["trial", "asset", "family_key", "year", "phase", "result", "src"], t))
                   if isinstance(t, list) else t
                   for t in (atlas.get("evidence", {}) or {}).get("landmark_trials", [])],
        "trials_focus": tf.get("trials", []),
        "trials_focus_note": tf.get("note"),
        "market_share": atlas.get("market_share", []),
        "market_note": atlas.get("market_note"),
        "pasi_kinetics": rk,
        "signal_path": bio_sp,
        "hierarchy": atlas.get("strategy_map", []),
        # ---- market-research layer (passthrough) ----
        "forecast": mr.get("forecast", {}), "scenarios": mr.get("scenarios", []),
        "geo": mr.get("geo", []), "funnel": mr.get("funnel", []),
        "segmentation": mr.get("segmentation", []), "opportunity": mr.get("opportunity", []),
        "payers": mr.get("payers", []), "attribution": mr.get("attribution", []),
        "attribution_total": mr.get("attribution_total"), "loe": mr.get("loe", []),
        "competitive": mr.get("competitive", []), "catalysts_watch": mr.get("catalysts_watch", []),
        "risks": mr.get("risks", []), "thesis": mr.get("thesis", []),
        "nodes": list(nodes.values()), "edges": edges, "sources": atlas.get("sources", []),
    }
    return graph, {"nodes": len(nodes), "edges": len(edges), "assets": len(assets),
                   "families": len(FAM), "biology": len(bio.get("nodes", []))}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("atlas", help="path to atlas.json")
    ap.add_argument("--out", help="output graph.json (default: alongside atlas.json)")
    args = ap.parse_args()
    atlas = json.load(open(args.atlas, encoding="utf-8"))
    graph, stats = compile_atlas(atlas)
    out = args.out or os.path.join(os.path.dirname(os.path.abspath(args.atlas)), "graph.json")
    json.dump(graph, open(out, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    print("wrote", out)
    print("  nodes: %(nodes)d  edges: %(edges)d  assets: %(assets)d  families: %(families)d  biology: %(biology)d" % stats)
    from collections import Counter
    print("  node types:", dict(Counter(n["type"] for n in graph["nodes"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
