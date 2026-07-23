#!/usr/bin/env python3
"""Transform the plaque-psoriasis atlas.json (v1 panels) into the v2 graph model
(nodes + edges) that the spotlight prototype traverses. See docs/data-model.md.

    python build_graph.py            # writes graph.json next to this file
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ATLAS = os.path.join(HERE, "..", "..", "examples", "plaque-psoriasis", "atlas.json")

def slug(s): return re.sub(r"-{2,}", "-", re.sub(r"[^a-z0-9]+", "-", (s or "").lower())).strip("-")

a = json.load(open(ATLAS, encoding="utf-8"))
nodes, edges = {}, []
def node(nid, ntype, label, attrs=None, sources=None):
    nodes[nid] = {"id": nid, "type": ntype, "label": label, "attrs": attrs or {}, "sources": sources or []}
    return nid
def edge(etype, s, t, attrs=None):
    edges.append({"type": etype, "source": s, "target": t, "attrs": attrs or {}})

IND = node("ind:plaque-psoriasis", "Indication", a["meta"]["disease"],
           {"area": "Immuno-dermatology", "one_liner": a["meta"].get("one_liner")})

# --- sales lookup from standard_of_care.top_products (by generic name) ---
sales = {}
for p in a.get("standard_of_care", {}).get("top_products", []):
    if p.get("annual_sales_usd_m") is not None:
        sales[slug(p["generic"])] = {"usd_m": p["annual_sales_usd_m"], "year": p.get("sales_year"), "brand": p.get("brand")}

# --- MoA classes ---
drug_to_moa = {}   # asset id -> moa node id
for m in a.get("moa_landscape", []):
    mid = node("moa:" + slug(m["class"]), "MoAClass", m["class"], {
        "validation_status": m.get("validation_status"), "rationale": m.get("rationale"),
        "mechanism": m.get("mechanism"), "modality": m.get("modality"),
        "pros": m.get("pros", []), "cons": m.get("cons", []), "key_players": m.get("key_players", []),
    }, m.get("sources"))
    for did in m.get("drugs", []):
        drug_to_moa[did] = mid
    # class -> target(s)
    for sym in re.split(r"[\/,]", m.get("target", "") or ""):
        sym = sym.strip()
        if sym and re.match(r"^[A-Za-z0-9]+$", sym):
            tid = node("target:" + sym, "Target", sym, {})
            edge("ACTS_ON", mid, tid)

# --- Companies (from companies[] + any referenced by assets) ---
comp_id = {}
for c in a.get("companies", []):
    cid = node("company:" + slug(c["name"]), "Company", c["name"],
               {"type": c.get("type"), "positioning": c.get("positioning")}, c.get("sources"))
    comp_id[c["name"]] = cid
    for d in c.get("deals", []):
        did = "deal:" + slug(c["name"]) + "-" + slug(d.get("type", "deal"))
        node(did, "Deal", (d.get("type", "deal").title() + " · " + (d.get("counterparty") or "")).strip(" ·"),
             {"value": d.get("value"), "year": d.get("year"), "note": d.get("note")}, d.get("sources"))
        edge("PARTY_TO", cid, did, {"role": "acquirer" if d.get("type") == "acquisition" else "party"})

def company_node(name):
    if not name: return None
    if name in comp_id: return comp_id[name]
    return comp_id.setdefault(name, node("company:" + slug(name), "Company", name, {"type": "company"}))

# --- Drugs (pipeline.assets) ---
for d in a.get("pipeline", {}).get("assets", []):
    did = "drug:" + slug(d["name"])
    attrs = {"brand": d.get("brand"), "highest_phase": d.get("phase"), "phase_num": d.get("phase_num"),
             "modality": d.get("modality"), "route": d.get("route"), "mechanism": d.get("mechanism"),
             "indications": d.get("indications", []), "moa_class": d.get("moa_class")}
    s = sales.get(slug(d["name"]))
    if s: attrs["annual_sales_usd_m"] = s["usd_m"]; attrs["sales_year"] = s["year"]
    node(did, "Drug", d["name"], attrs, d.get("sources"))
    # DEVELOPED_BY
    cid = company_node(d.get("company"))
    if cid: edge("DEVELOPED_BY", did, cid)
    # HAS_MECHANISM (prefer moa_landscape membership, fall back to moa_class string)
    mid = drug_to_moa.get(d["id"])
    if not mid and d.get("moa_class"):
        # fuzzy match moa_class to an MoAClass node
        for k, v in nodes.items():
            if v["type"] == "MoAClass" and d["moa_class"].split()[0].lower() in v["label"].lower():
                mid = k; break
    if mid: edge("HAS_MECHANISM", did, mid)
    # HITS target
    for sym in re.split(r"[\/,]", d.get("target", "") or ""):
        sym = sym.strip()
        if sym and re.match(r"^[A-Za-z0-9]+$", sym):
            tid = node("target:" + sym, "Target", sym, {})
            edge("HITS", did, tid)
    # HAS_MODALITY
    if d.get("modality"):
        modid = node("modality:" + slug(d["modality"]), "Modality", d["modality"], {})
        edge("HAS_MODALITY", did, modid)
    # DEVELOPED_IN this indication
    edge("DEVELOPED_IN", did, IND, {"phase": d.get("phase"), "approved": d.get("phase") == "approved"})

# --- Targets: attach Open Targets association scores where known (from live pull) ---
OT = {"IL12B": 0.74, "TYK2": 0.71, "IL23A": 0.64, "TNF": 0.61, "PDE4": 0.61, "PDE4A": 0.61,
      "NR3C1": 0.60, "VDR": 0.60, "IL17A": 0.60, "IL17RA": 0.58, "IL23R": 0.55, "AHR": 0.45}
for b in a.get("biology", {}).get("targets", []):
    sym = b.get("symbol")
    if not sym: continue
    tid = node("target:" + sym, "Target", sym,
               {"name": b.get("name"), "rationale": b.get("rationale"), "tractability": b.get("tractability")})
    if sym in OT: nodes[tid]["attrs"]["ot_association_score"] = OT[sym]
for tid, n in list(nodes.items()):
    if n["type"] == "Target" and n["label"] in OT and "ot_association_score" not in n["attrs"]:
        n["attrs"]["ot_association_score"] = OT[n["label"]]

# --- Market segments (from epidemiology) ---
seg_ids = []
for s in a.get("epidemiology", {}).get("segments", []):
    sid = node("seg:" + slug(s["name"]), "MarketSegment", s["name"],
               {"share_pct": s.get("share_pct"), "note": s.get("note")}, s.get("sources"))
    seg_ids.append((sid, s["name"]))
def serves_segment(drug_node):
    """Heuristic: biologics/oral-targeted -> moderate-to-severe; topicals/conventional -> mild."""
    cls = (drug_node["attrs"].get("moa_class") or "").lower()
    mod = (drug_node["attrs"].get("modality") or "").lower()
    is_foundational = "topical" in cls or "conventional" in cls
    for sid, name in seg_ids:
        n = name.lower()
        if is_foundational and "mild" in n: edge("SERVES", drug_node["id"], sid)
        if not is_foundational and ("moderate" in n or "severe" in n): edge("SERVES", drug_node["id"], sid)

for nid, n in list(nodes.items()):
    if n["type"] == "Drug": serves_segment(n)

# --- Catalysts ---
name_to_drug = {n["label"].lower(): nid for nid, n in nodes.items() if n["type"] == "Drug"}
for i, c in enumerate(a.get("catalysts", []), 1):
    cid = node(f"catalyst:c{i}", "Catalyst", c.get("event", "event"),
               {"date": c.get("date"), "kind": c.get("type"), "significance": c.get("significance"),
                "company": c.get("company")}, c.get("sources"))
    asset = (c.get("asset") or "").lower()
    for lbl, did in name_to_drug.items():
        if asset and (asset in lbl or lbl in asset):
            edge("HAS_CATALYST", did, cid)
    # biosimilar catalyst -> ustekinumab
    if "biosimilar" in (c.get("event", "").lower()) and "drug:ustekinumab" in nodes:
        edge("HAS_CATALYST", "drug:ustekinumab", cid)

graph = {
    "meta": {"scope": a["meta"].get("scope", "indication"), "focus": a["meta"]["disease"],
             "generated": a["meta"].get("generated"), "one_liner": a["meta"].get("one_liner"),
             "headline_stats": a.get("headline_stats", []),
             "market": {"current_size": a.get("market", {}).get("current_size"),
                        "summary": a.get("market", {}).get("summary")}},
    "nodes": list(nodes.values()),
    "edges": edges,
    "sources": a.get("sources", []),
}
out = os.path.join(HERE, "graph.json")
json.dump(graph, open(out, "w", encoding="utf-8"), indent=2, ensure_ascii=False)

from collections import Counter
print("wrote", out)
print("nodes:", len(graph["nodes"]), dict(Counter(n["type"] for n in graph["nodes"])))
print("edges:", len(graph["edges"]), dict(Counter(e["type"] for e in graph["edges"])))
