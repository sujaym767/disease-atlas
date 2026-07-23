#!/usr/bin/env python3
"""Inject graph.json into template.html -> index.html (self-contained). Run build_graph.py first."""
import json, os
H = os.path.dirname(os.path.abspath(__file__))
graph = json.load(open(os.path.join(H, "graph.json"), encoding="utf-8"))
tpl = open(os.path.join(H, "template.html"), encoding="utf-8").read()
data = json.dumps(graph, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
out = tpl.replace("__TITLE__", "Plaque psoriasis — Spotlight Atlas").replace("__GRAPH__", data)
open(os.path.join(H, "index.html"), "w", encoding="utf-8").write(out)
print("wrote index.html (%.0f KB)" % (len(out.encode()) / 1024))
