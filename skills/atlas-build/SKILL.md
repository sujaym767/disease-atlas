---
name: atlas-build
description: >-
  Build the interactive, self-contained HTML disease atlas from a semantic atlas.json.
  This is the BUILDER half of the atlas pipeline: it compiles a validated atlas.json (produced
  by the disease-atlas research skill, or hand-authored) into the RA-Capital-style interactive
  poster — the Objective→Asset strategy map, the IL-23/IL-17-style mechanism schematic, the
  ER-diagram popups, the force-directed network explorer, biology path-finding, and the
  market-research bands (forecast & scenarios, patient funnel & opportunity, payer access,
  competitive posture). Deterministic and offline: no APIs, no web search, no synthesis. Use this
  when you already have an atlas.json and want the HTML, when re-rendering after editing atlas.json,
  or as the final step of a disease-atlas research run. If you need to RESEARCH an indication first
  (gather the pipeline, market, epidemiology, etc.), use the disease-atlas skill — it produces the
  atlas.json this skill consumes.
---

# Atlas Build

Turn a semantic **`atlas.json`** into a single self-contained **`atlas_<disease>.html`** — the
interactive market-research atlas. This skill is a *pure function of its input*: same atlas.json →
same HTML, no network, no model synthesis. All the intelligence lives in `atlas.json`; this skill
compiles and renders it.

`<skill>` = this skill's directory (`skills/atlas-build`).

## What it does

```
atlas.json  ──compile_atlas.py──►  property graph (nodes+edges) + render sections  ──inject──►  atlas_<disease>.html
 (semantic)      authors the graph        (in-memory graph.json)          atlas_template.html      (self-contained)
```

- **`compile_atlas.py`** authors the property graph from the semantic sections: every
  `pipeline.assets[]` becomes a `Drug` node wired to its `Company`, `MoAClass`, `Target` and
  `Modality`; `moa_landscape`/`families` become the colour-coded mechanism lanes; `biology_graph`
  becomes first-class `Biology` nodes joined by the real cascade edges (so path-finding traverses
  the mechanism, not just the org chart); `catalysts` and `deals` become their own nodes. It then
  passes the render sections (`strategy_map`, `market_research`, `response_kinetics`, `trials_focus`,
  `standard_of_care`, `glossary`, …) through to the template.
- **`assets/atlas_template.html`** is the interactive renderer (inline CSS/JS, vanilla SVG — no
  libraries). It lays out the strategy tree with a tidy-tree algorithm, draws every panel, and wires
  the ER popup / network explorer / path-finding. Nothing is hand-positioned.
- **`build_atlas.py`** is the one-shot entry: compile + inject → HTML.

## Usage

```bash
# one shot: atlas.json → self-contained HTML
python <skill>/scripts/build_atlas.py runs/<slug>/atlas.json --out runs/<slug>/atlas_<slug>.html

# optional: also emit the intermediate graph for inspection
python <skill>/scripts/build_atlas.py runs/<slug>/atlas.json --out atlas.html --graph graph.json

# compiler alone (atlas.json → graph.json), e.g. to debug the authoring
python <skill>/scripts/compile_atlas.py runs/<slug>/atlas.json --out graph.json
```

Then open the HTML (it renders as a Claude artifact and opens by double-click). Drag to pan, scroll
to zoom, click any entity for its relationship map; use the `⌗` network toggle and the `TRACE` bar.

## The input contract

`atlas.json` is documented in **`references/atlas-schema.md`**. Two layers:

- **Semantic core** (the researcher's substance): `meta`, `pipeline.assets`, `companies`,
  `moa_landscape`/`families`, `standard_of_care`, `epidemiology`, `market`, `catalysts`, `evidence`,
  `sources`.
- **Render sections** (drive the prototype-grade regions, all optional): `strategy_map` (the
  Objective→Strategy→Approach→Mechanism→Asset tree), `biology_graph` (cascade nodes + edges +
  signal path + anchors), `market_research` (forecast/scenarios/geo/funnel/opportunity/payers/
  attribution/competitive/thesis/risks — the shape `ingest_report.py` emits), `response_kinetics`,
  `trials_focus`, `glossary`, `sites`, `market_share`, `deals`, `safety`.

**Every section is optional.** A thin atlas still builds; the template shows an honest empty state
for a missing region (golden rule #6 — degrade gracefully). Give the builder more and it renders
more.

## Guardrails

- **Don't hand-edit the rendered HTML** — change `atlas.json` and rebuild, or change
  `assets/atlas_template.html` (the renderer) if the *presentation* is wrong for all atlases.
- **The compiler never invents data** — it only re-shapes what `atlas.json` provides. Accuracy is
  the researcher's job; fidelity is the builder's.
- **Self-contained output** — no external requests at view time; the data is embedded as a JSON
  `<script>` block and `</` is neutralized so it can't break the tag.
- **Verify** after building: open headless, assert 0 JS errors, confirm the strategy map, schematic,
  the four market-research bands, the ER popup and path-finding all render (or show empty states).

## Provenance

The renderer and the compiler's authoring logic were factored out of the plaque-psoriasis prototype
(`prototypes/psoriasis-spotlight/`), where they were validated by hand before being generalized. The
psoriasis `atlas.json` in `examples/` is the reference input and the builder's regression fixture.
