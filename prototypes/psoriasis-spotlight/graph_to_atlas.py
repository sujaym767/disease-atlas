#!/usr/bin/env python3
"""Bootstrap tool: reverse-map the prototype's compiled graph.json back into a rich, SEMANTIC
atlas.json — the input contract that the general `atlas-build` skill's compile_atlas.py consumes.

This exists to (a) produce a full-richness reference atlas.json for plaque psoriasis without
re-typing the prototype's curated data, and (b) pin the atlas.json ⇄ graph.json contract by
round-trip (compile_atlas.py(graph_to_atlas.py(graph)) ≡ graph). It is psoriasis-bootstrap-
specific and one-time; the real producer of atlas.json is the `atlas-research` skill.

atlas.json is SEMANTIC (assets / companies / moa / biology as domain objects). It deliberately
does NOT carry the property-graph nodes/edges — compile_atlas.py authors those.
"""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
G = json.load(open(os.path.join(HERE, "graph.json"), encoding="utf-8"))
N = {n["id"]: n for n in G["nodes"]}
OUT = {e["source"]: [] for e in G["edges"]}
for e in G["edges"]:
    OUT.setdefault(e["source"], []).append(e)


def out_nodes(nid, etype):
    return [N[e["target"]] for e in OUT.get(nid, []) if e["type"] == etype and e["target"] in N]


def slug(s):
    return re.sub(r"-{2,}", "-", re.sub(r"[^a-z0-9]+", "-", (s or "").lower())).strip("-")


# ---- families (color lanes) straight from the MoAClass nodes ----
families = [{"key": f["key"], "label": f["label"], "colorVar": f["colorVar"],
             "order": f["order"], "anchor": f.get("anchor")} for f in G.get("families", [])]
SAFETY = {n["attrs"]["family_key"]: n["attrs"].get("safety")
          for n in G["nodes"] if n["type"] == "MoAClass" and n["attrs"].get("safety")}

# ---- pipeline.assets reconstructed from Drug nodes ----
assets = []
for n in G["nodes"]:
    if n["type"] != "Drug":
        continue
    a = n["attrs"]
    comp = out_nodes(n["id"], "DEVELOPED_BY")
    moa = out_nodes(n["id"], "HAS_MECHANISM")
    tgt = out_nodes(n["id"], "HITS")
    fam_key = moa[0]["attrs"]["family_key"] if moa else a.get("moa_family")
    rec = {
        "id": "d_" + slug(n["label"]),
        "name": n["label"],
        "brand": a.get("brand"),
        "company": comp[0]["label"] if comp else None,
        "family_key": fam_key,
        "moa_class": (moa[0]["label"] if moa else a.get("moa_family")),
        "sub_class": a.get("sub_class") or a.get("sub"),
        "target": tgt[0]["label"] if tgt else None,
        "modality": a.get("modality") or a.get("mod"),
        "phase": a.get("highest_phase"),
        "phase_num": a.get("phase_num"),
        "route": a.get("route"),
        "dose": a.get("dose"),
        "approval_year": a.get("appr"),
        "annual_sales_usd_m": a.get("annual_sales_usd_m") or a.get("sales"),
        "sales_year": a.get("sales_year") or a.get("syr"),
        "biosimilar": a.get("bios"),
        "is_combo": a.get("combo", False),
        "note": a.get("note"),
        "sources": n.get("sources", []),
    }
    eff = {k: a.get(k) for k in ("p75", "p90", "p100") if a.get(k) is not None}
    if eff:
        rec["efficacy"] = eff
    if a.get("detail"):
        rec["detail"] = a["detail"]
    assets.append({k: v for k, v in rec.items() if v is not None and v != []})

# ---- moa_landscape: one class per family, listing its member asset ids ----
by_fam = {}
for a in assets:
    by_fam.setdefault(a.get("family_key"), []).append(a["id"])
moa_landscape = []
for f in G.get("families", []):
    k = f["key"]
    moa_landscape.append({k2: v for k2, v in {
        "class": f["label"], "family_key": k, "colorVar": f["colorVar"], "order": f["order"],
        "anchor": f.get("anchor"), "safety": SAFETY.get(k),
        "drugs": by_fam.get(k, []),
    }.items() if v is not None})

# ---- companies from Company nodes ----
companies = []
for n in G["nodes"]:
    if n["type"] != "Company":
        continue
    devd = [N[e["source"]]["label"] for e in G["edges"]
            if e["type"] == "DEVELOPED_BY" and e["target"] == n["id"] and e["source"] in N]
    companies.append({"name": n["label"], "assets": ["d_" + slug(d) for d in devd]})

# ---- biology_graph: Biology nodes + their cascade/signal edges (semantic) ----
bio_nodes, bio_edges = [], []
BIO_TYPES = {"PRODUCES", "ACTS_ON", "SIGNALS_VIA", "LEADS_TO", "FEEDBACK", "BINDS",
             "ACTIVATES", "INDUCES", "SUSTAINS"}
for n in G["nodes"]:
    if n["type"] != "Biology":
        continue
    suf = n["id"].split(":", 1)[1]
    rec = {"id": suf, "kind": n["attrs"].get("kind"), "label": n["label"],
           "description": n["attrs"].get("description")}
    if n["attrs"].get("pos"):
        rec["pos"] = n["attrs"]["pos"]
    bio_nodes.append({k: v for k, v in rec.items() if v is not None})
for e in G["edges"]:
    if e["type"] in BIO_TYPES and e["source"].startswith("bio:") and e["target"].startswith("bio:"):
        bio_edges.append({"type": e["type"], "source": e["source"].split(":", 1)[1],
                          "target": e["target"].split(":", 1)[1]})
# target→biology bridges (which target symbol maps to which cascade node)
target_bio = {}
for e in G["edges"]:
    if e["type"] == "PART_OF" and e["source"].startswith("target:") and e["target"].startswith("bio:"):
        target_bio[e["source"].split(":", 1)[1]] = e["target"].split(":", 1)[1]
biology_graph = {"nodes": bio_nodes, "edges": bio_edges,
                 "signal_path": [{"from": s["from"].split(":", 1)[1], "to": s["to"].split(":", 1)[1], "label": s["label"]}
                                 for s in G.get("signal_path", [])],
                 "anchors": {f["key"]: f.get("anchor") for f in G.get("families", []) if f.get("anchor")},
                 "target_bio": target_bio}

# ---- catalysts reconstructed from Catalyst nodes (asset linkage lives on the HAS_CATALYST edge) ----
cat_asset = {e["target"]: N[e["source"]]["label"]
             for e in G["edges"] if e["type"] == "HAS_CATALYST" and e["source"] in N}
catalysts = []
for n in G["nodes"]:
    if n["type"] != "Catalyst":
        continue
    a = n["attrs"]
    catalysts.append({k: v for k, v in {
        "date": a.get("date"), "event": n["label"], "kind": a.get("kind"),
        "company": a.get("company"), "asset": cat_asset.get(n["id"]),
        "significance": a.get("significance"), "sources": n.get("sources", []),
    }.items() if v})

# ---- deals straight from the meta list ----
deals = G.get("deals", [])

# ---- market_research layer (already the ingest_report shape) ----
market_research = {k: G.get(k) for k in
                   ("forecast", "scenarios", "geo", "funnel", "segmentation", "opportunity",
                    "payers", "attribution", "attribution_total", "loe", "competitive",
                    "catalysts_watch", "risks", "thesis") if G.get(k) is not None}

atlas = {
    "schema_version": "1.1",
    "meta": {
        "disease": G["meta"]["focus"],
        "scope": G["meta"].get("scope", "indication"),
        "generated": G["meta"].get("generated"),
        "as_of": G["meta"].get("as_of"),
        "generator": "graph_to_atlas bootstrap (from prototype graph.json)",
        "one_liner": G["meta"].get("one_liner"),
        "sales_note": G["meta"].get("sales_note"),
        "mechanism_label": "IL-23 / IL-17 cascade → intracellular signalling",
        "efficacy_label": "PASI 90",
        "headline_stats": G["meta"].get("headline_stats", []),
    },
    "epidemiology": G.get("epi", {}),
    "sites": G.get("sites", []),
    "standard_of_care": {"lines": [{"tier": s["tier"], "label": s["label"], "agents": s["agents"],
                                    "note": s["note"], "colorVar": s.get("colorVar")} for s in G.get("soc", [])],
                         "note": G.get("soc_note")},
    "market_share": G.get("market_share", []),
    "families": families,
    "moa_landscape": moa_landscape,
    "pipeline": {"assets": assets},
    "companies": companies,
    "biology_graph": biology_graph,
    "strategy_map": G.get("hierarchy", []),
    "response_kinetics": ({**G["pasi_kinetics"], "metric": G["pasi_kinetics"].get("metric", "PASI 90")}
                          if G.get("pasi_kinetics") else None),
    "evidence": {"landmark_trials": G.get("trials", [])},
    "trials_focus": {"trials": G.get("trials_focus", []), "note": G.get("trials_focus_note")},
    "catalysts": catalysts,
    "deals": deals,
    "market_research": market_research,
    "glossary": [{"term": t["term"], "def": t["def"]} for t in G.get("glossary", [])],
    "safety": SAFETY,
    "sources": G.get("sources", []),
}

dst = os.path.join(HERE, "atlas.json")
json.dump(atlas, open(dst, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("wrote", dst)
print("  assets:", len(assets), "| moa/families:", len(moa_landscape), "| companies:", len(companies))
print("  biology nodes:", len(bio_nodes), "edges:", len(bio_edges),
      "| strategy objectives:", len(atlas["strategy_map"]))
print("  market_research keys:", list(market_research.keys()))
print("  trials_focus:", len(G.get("trials_focus", [])), "| glossary:", len(atlas["glossary"]),
      "| catalysts:", len(catalysts), "| deals:", len(deals), "| sources:", len(atlas["sources"]))
