#!/usr/bin/env python3
"""build_atlas.py — the atlas-build entry point.

    python build_atlas.py runs/<slug>/atlas.json --out runs/<slug>/atlas_<slug>.html

Compiles the semantic atlas.json into the property graph (compile_atlas.py) and injects it,
plus the title, into the interactive template (assets/atlas_template.html) to produce ONE
self-contained HTML file — inline CSS/JS, data embedded as a JSON <script> block, no external
requests at view time. Stdlib only; deterministic; no network.

Optionally writes the intermediate graph.json (--graph) for inspection/debugging.
"""
import argparse, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from compile_atlas import compile_atlas  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_TEMPLATE = os.path.join(HERE, "..", "assets", "atlas_template.html")


def slug(s):
    return re.sub(r"-{2,}", "-", re.sub(r"[^a-z0-9]+", "-", (s or "").lower())).strip("-")


def render(graph, template, title):
    # compact JSON, then neutralize "</" so it can't terminate the <script> tag (JSON.parse round-trips "<\/")
    data = json.dumps(graph, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return template.replace("__TITLE__", title).replace("__GRAPH__", data)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("atlas", help="path to atlas.json")
    ap.add_argument("--out", help="output HTML path (default alongside atlas.json)")
    ap.add_argument("--graph", help="also write the intermediate graph.json here")
    ap.add_argument("--template", default=DEFAULT_TEMPLATE)
    args = ap.parse_args()

    atlas = json.load(open(args.atlas, encoding="utf-8"))
    graph, stats = compile_atlas(atlas)
    if args.graph:
        json.dump(graph, open(args.graph, "w", encoding="utf-8"), indent=2, ensure_ascii=False)

    disease = (atlas.get("meta", {}) or {}).get("disease", "Disease")
    title = "%s — Atlas" % disease
    template = open(args.template, encoding="utf-8").read()
    html = render(graph, template, title)

    out = args.out or os.path.join(os.path.dirname(os.path.abspath(args.atlas)),
                                   "atlas_%s.html" % slug(disease))
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    open(out, "w", encoding="utf-8").write(html)
    print("wrote %s (%.0f KB)" % (out, len(html.encode()) / 1024))
    print("  graph: %(nodes)d nodes, %(edges)d edges, %(assets)d assets, %(families)d families, %(biology)d biology" % stats)
    return 0


if __name__ == "__main__":
    sys.exit(main())
