#!/usr/bin/env python3
"""Transform a therapeutic-area research report (reportmodel.json) into normalized
atlas data (report_data.json) that build_deep.py folds into the atlas graph.

This is the *ingestion* half of the intended two-skill split: a research skill emits
the report model; this transform maps its known section/table schema into the compact
structures the atlas renderers consume. It keys off STABLE section ids + column names
(not psoriasis-specific text), so the same transform generalizes to any indication the
research skill produces. Rows in the report model are lists of cell strings — every
mapping goes through `rowdicts()`, which zips them against the table's `columns`.

Standalone, standard-library only. Run:  python ingest_report.py [reportmodel.json]
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))


# ---------- generic report-model helpers ----------
def norm(s):
    """Normalize a column header for fuzzy matching."""
    return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()


def sections_by_id(report):
    return {s.get("id"): s for s in report.get("sections", [])}


def find_table(section, want_cols=None, title_sub=None, idx=None):
    """Locate a table within a section by (optional) column signature, title substring,
    or positional index. Returns the table dict or None. Column/title matching makes the
    transform resilient to table reordering across report versions."""
    tabs = (section or {}).get("tables") or []
    if not tabs:
        return None
    if idx is not None and idx < len(tabs):
        return tabs[idx]
    for t in tabs:
        cols = [norm(c) for c in t.get("columns", [])]
        if want_cols and all(any(w in c for c in cols) for w in want_cols):
            return t
        if title_sub and title_sub in norm(t.get("title")):
            return t
    return tabs[0] if tabs else None


def rowdicts(table):
    """Zip each list-row against the table's columns → list of {normalized_col: cell}.
    Also keeps the raw ordered cells under '_cells'."""
    if not table:
        return []
    cols = [norm(c) for c in table.get("columns", [])]
    out = []
    for row in table.get("rows", []):
        d = {cols[i]: (row[i] if i < len(row) else "") for i in range(len(cols))}
        d["_cells"] = row
        out.append(d)
    return out


def col(d, *subs):
    """Fetch a cell from a row-dict by fuzzy column-name substring(s)."""
    for k, v in d.items():
        if k == "_cells":
            continue
        if all(s in k for s in subs):
            return v
    return ""


def money_b(s):
    """Parse a dollar figure into a $B float. Prefers an explicit $x.xB / $xxxM; a bare
    number is read as $B. Returns None when no figure is present ('n/a', 'Material')."""
    if not s:
        return None
    s = str(s)
    m = re.search(r"\$\s*([\d.]+)\s*([BM])", s)
    if m:
        v = float(m.group(1))
        return round(v / 1000, 3) if m.group(2) == "M" else v
    m = re.search(r"([\d.]+)\s*([BM])", s)          # e.g. "€2.22B" fallback
    if m:
        v = float(m.group(1))
        return round(v / 1000, 3) if m.group(2) == "M" else v
    m = re.match(r"~?\s*([\d.]+)\s*$", s.strip())    # bare number = $B
    return float(m.group(1)) if m else None


def pop_millions(s):
    """Parse a population string into millions: '~7.6M'→7.6, '~630k'→0.63."""
    if not s:
        return None
    m = re.search(r"([\d.]+)\s*([MmKk])", str(s))
    if not m:
        return None
    v = float(m.group(1))
    return round(v / 1000, 4) if m.group(2) in "Kk" else v


# ---------- segment → atlas semantic key (for colour binding downstream) ----------
def seg_key(label):
    L = (label or "").lower()
    if "il-23" in L or "il23" in L:
        return "il23"
    if "il-17" in L or "il17" in L:
        return "il17"
    if "oral" in L:
        return "oral"
    if "tnf" in L:
        return "tnf"
    if "topical" in L or "conventional" in L:
        return "topical"
    if "total" in L:
        return "total"
    return "other"


def short_seg(label):
    """A tight chart label for a long segment name."""
    key = seg_key(label)
    return {"il23": "Injectable IL-23", "il17": "IL-17", "oral": "Oral targeted",
            "tnf": "TNF + biosimilars", "topical": "Topical + conv.", "total": "Total"}.get(key, label[:18])


# ---------- section transforms ----------
def x_forecast(sec):
    t0 = find_table(sec, want_cols=["segment", "2026", "2031"])
    years = []
    for c in (t0 or {}).get("columns", []):
        m = re.match(r"^(20\d\d)$", str(c).strip())
        if m:
            years.append(int(m.group(1)))
    segments, total = [], None
    for d in rowdicts(t0):
        label = col(d, "segment")
        vals = []
        for y in years:
            vals.append(money_b(d.get(str(y), "")) )
        rec = {"label": label, "short": short_seg(label), "key": seg_key(label),
               "vals": vals, "cagr": col(d, "cagr"), "note": col(d, "assumption") or col(d, "key")}
        if rec["key"] == "total":
            total = rec
        else:
            segments.append(rec)
    scen = find_table(sec, want_cols=["scenario", "2031"])
    scenarios = []
    for d in rowdicts(scen):
        scenarios.append({"name": col(d, "scenario"),
                          "y2031": money_b(col(d, "2031")),
                          "cagr": col(d, "cagr"),
                          "swing": col(d, "swing") or col(d, "assumption")})
    geo_t = find_table(sec, want_cols=["region", "market"])
    geo = []
    for d in rowdicts(geo_t):
        geo.append({"region": col(d, "region"),
                    "eligible": col(d, "eligible") or col(d, "diagnosed"),
                    "penetration": col(d, "penetration"),
                    "net_price": col(d, "net price") or col(d, "price"),
                    "market": money_b(col(d, "market")),
                    "market_str": col(d, "market")})
    return {"years": years, "segments": segments, "total": total,
            "note": " ".join((t0 or {}).get("notes", []) if isinstance((t0 or {}).get("notes"), list) else [(t0 or {}).get("notes") or ""]).strip(),
            "scenarios": scenarios, "geo": geo}


def x_funnel(sec):
    t0 = find_table(sec, want_cols=["stage", "population"])
    rows = []
    for d in rowdicts(t0):
        stage = col(d, "stage")
        rows.append({"stage": stage, "population": col(d, "population"),
                     "pop_num": pop_millions(col(d, "population")),
                     "basis": col(d, "basis") or col(d, "source"),
                     "note": col(d, "note"),
                     "gap": "not on advanced" in stage.lower() or "not on" in stage.lower()})
    seg_t = find_table(sec, want_cols=["segment", "share"])
    segmentation = [{"segment": col(d, "segment"), "share": col(d, "share"),
                     "why": col(d, "why") or col(d, "differs")} for d in rowdicts(seg_t)]
    return {"funnel": rows, "segmentation": segmentation}


def x_opportunity(sec):
    t0 = find_table(sec, want_cols=["gap", "opportunity"])
    out = []
    for d in rowdicts(t0):
        out.append({"gap": col(d, "segment") or col(d, "gap"),
                    "severity": col(d, "severity"),
                    "coverage": col(d, "current coverage") or col(d, "coverage"),
                    "the_gap": col(d, "the gap"),
                    "population": col(d, "addressable") or col(d, "population"),
                    "size": col(d, "opportunity size") or col(d, "size"),
                    "size_b": money_b(col(d, "opportunity size") or col(d, "size"))})
    return out


def x_payers(sec):
    t0 = find_table(sec, want_cols=["market", "coverage"])
    return [{"market": col(d, "market"), "coverage": col(d, "coverage"),
             "hta": col(d, "hta") or col(d, "decision"),
             "restriction": col(d, "restriction"),
             "net_price": col(d, "net price") or col(d, "price")} for d in rowdicts(t0)]


def x_attribution(sec):
    t0 = find_table(sec, want_cols=["brand", "company", "attribution"])
    out = []
    for d in rowdicts(t0):
        brand_inn = col(d, "brand")
        m = re.match(r"\s*([^(]+?)\s*\(([^)]+)\)", brand_inn or "")
        brand, inn = (m.group(1).strip(), m.group(2).strip()) if m else (brand_inn, "")
        attr = col(d, "attribution")
        fy_rev = col(d, "revenue") or col(d, "fy2025")
        av = money_b(attr)
        fv = money_b(fy_rev)
        out.append({"brand": brand, "inn": inn, "company": col(d, "company"),
                    "class_route": col(d, "class"), "fy_rev": fy_rev, "fy_val": fv,
                    "attr_str": attr, "attr_val": av,
                    "attr_frac": (round(av / fv, 3) if av and fv else None),
                    "access": col(d, "access") or col(d, "price note"),
                    "exclusivity": col(d, "exclusivity")})
    loe_t = find_table(sec, want_cols=["event", "timing"])
    loe = [{"asset": col(d, "asset") or col(d, "class"), "event": col(d, "event"),
            "timing": col(d, "timing"), "consequence": col(d, "consequence")} for d in rowdicts(loe_t)]
    return {"attribution": out, "loe": loe}


def x_competitive(sec):
    t0 = find_table(sec, want_cols=["company", "position"])
    return [{"company": col(d, "company"), "position": col(d, "position"),
             "depth": col(d, "depth"), "posture": col(d, "posture"),
             "strength": col(d, "strength"), "vulnerability": col(d, "vulnerability")} for d in rowdicts(t0)]


def x_catalysts(sec):
    t0 = find_table(sec, want_cols=["catalyst", "expected"])
    cats = [{"catalyst": col(d, "catalyst"), "type": col(d, "type"),
             "expected": col(d, "expected"), "why": col(d, "why")} for d in rowdicts(t0)]
    thesis = []
    blocks = sec.get("blocks") or []
    cur = None
    for b in blocks:
        typ = b.get("type", "")
        txt = b.get("text") or b.get("content") or ""
        if typ in ("heading3", "heading2", "heading"):
            cur = {"heading": txt, "text": ""}
            thesis.append(cur)
        elif typ == "paragraph" and cur is not None:
            cur["text"] = (cur["text"] + " " + txt).strip()
    thesis = [t for t in thesis if t["text"]]
    return {"catalysts_watch": cats, "thesis": thesis}


def x_transactions(sec):
    t0 = find_table(sec, want_cols=["date", "parties"])
    return [{"date": col(d, "date"), "type": col(d, "type"), "parties": col(d, "parties"),
             "asset": col(d, "asset") or col(d, "stage"), "value": col(d, "value"),
             "read": col(d, "read")} for d in rowdicts(t0)]


def x_risks(sec):
    t0 = find_table(sec, want_cols=["risk", "category"])
    return [{"risk": col(d, "risk"), "category": col(d, "category"),
             "prob": col(d, "prob"), "impact": col(d, "impact"),
             "horizon": col(d, "horizon"),
             "trigger": col(d, "would change") or col(d, "view")} for d in rowdicts(t0)]


def x_snapshot(sec):
    t0 = find_table(sec, want_cols=["field", "value"])
    return [{"field": col(d, "field"), "value": col(d, "value")} for d in rowdicts(t0)]


# ---------- driver ----------
def main():
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "reportmodel.json")
    report = json.load(open(src, encoding="utf-8"))
    S = sections_by_id(report)
    meta = report.get("meta", {})

    out = {
        "meta": {k: meta.get(k) for k in
                 ("subject", "subject_type", "indication_type", "scope", "as_of",
                  "currency", "region_focus", "version")},
        "sources": report.get("sources", []),
        "snapshot": x_snapshot(S.get("snapshot", {})),
    }
    out.update(x_forecast(S.get("market_forecast", {})))          # years, segments, total, note, scenarios, geo
    out.update(x_funnel(S.get("epidemiology", {})))               # funnel, segmentation
    out["opportunity"] = x_opportunity(S.get("unmet_need", {}))
    out["payers"] = x_payers(S.get("stakeholders_access", {}))
    out.update(x_attribution(S.get("products_ip", {})))           # attribution, loe
    out["competitive"] = x_competitive(S.get("competitive", {}))
    out.update(x_catalysts(S.get("executive_summary", {})))       # catalysts_watch, thesis
    out["deals_report"] = x_transactions(S.get("transactions", {}))
    out["risks"] = x_risks(S.get("risk_register", {}))

    dst = os.path.join(HERE, "report_data.json")
    json.dump(out, open(dst, "w", encoding="utf-8"), indent=1, ensure_ascii=False)

    # provenance / sanity print
    attr_total = sum(a["attr_val"] for a in out["attribution"] if a.get("attr_val"))
    print("ingested:", os.path.basename(src), "→ report_data.json")
    print("  forecast segments:", len(out["segments"]), "| years:", out["years"],
          "| total 2031:", (out["total"] or {}).get("vals"))
    print("  scenarios:", [s["name"] for s in out["scenarios"]])
    print("  geo rows:", len(out["geo"]), "| funnel stages:", len(out["funnel"]),
          "| gap flagged:", sum(1 for f in out["funnel"] if f["gap"]))
    print("  opportunity rows:", len(out["opportunity"]), "| payers:", len(out["payers"]))
    print("  attribution rows:", len(out["attribution"]), "| psoriasis-attributed $B captured:", round(attr_total, 1))
    print("  competitive:", len(out["competitive"]), "| catalysts_watch:", len(out["catalysts_watch"]),
          "| thesis blocks:", len(out["thesis"]), "| risks:", len(out["risks"]))


if __name__ == "__main__":
    main()
