# Spotlight Atlas — interactive prototype (plaque psoriasis)

A **presentation prototype** pushing the disease-atlas toward RA-Capital depth *and* interactivity: the dense single-canvas landscape, made alive. Click any entity — a drug, a company, a mechanism, a target — and the whole map responds: unrelated things dim, related things highlight, connector wires draw the relationships, and a detail rail shows that entity's full profile + everything it connects to (with a relationship graph).

**Open [`index.html`](index.html)** (self-contained, offline). Previews: [overview](preview_overview.png) · [drug spotlight](preview_drug_focus.png) · [panels](preview_panels.png).

## Depth (≈ RA Capital density)
- **55 assets** across **10 mechanism families** and the **full phase ladder** (approved → Ph1 → discontinued), mined from the live Open Targets pull (167 candidates) + ClinicalTrials.gov, curated with the well-established late-stage assets.
- **Dense cards:** company, sub-class, route + maintenance dosing, phase, **PASI-90** bar, **FY2025 sales**, and markers for ◆ biosimilar, + combo, ⚠ boxed warning.
- **Competitive matrix** — company × mechanism asset-count heatmap.
- **Efficacy benchmark** — PASI-90 at wk 12–16 (cross-trial, NMA-anchored) for 16 agents.
- **Catalysts & exclusivity** — dated 2023→2033 timeline (Humira/Stelara biosimilar cliffs, ICOTYDE approval, oral-TYK2 Phase 3 readouts, patent expiries).
- **Class safety** notes per mechanism (IL-17 Candida/IBD, TNF boxed warnings, TYK2 vs JAK, IL-23 cleanest).

## Spotlight interactions
- **drug →** market/sales, developer, mechanism, targets, segment, same-**sub-class** competitors, catalysts, class safety.
- **company →** every **mechanism it's pursuing** + portfolio + deals (click a matrix row/header too).
- **mechanism →** its drugs, players, best-in-class PASI, safety.
- **target →** every drug that hits it.
Plus a radial **ego-graph** in the rail, lens switcher (mechanism / modality / phase), search, light/dark, `⎋` to reset.

## Sourcing & accuracy
Pipeline/mechanism/phase from the **live APIs**; sales (FY2025), PASI benchmarks (Armstrong 2020 NMA + pivotal trials), catalysts and biosimilar/patent dates from **cited web research** (see the source chips in each rail). Sales are **all-indication franchise totals**, not psoriasis-only; PASI values are cross-trial unless a head-to-head is noted; a few sales figures are approximate (flagged). It's **July 2026** in the data, so icotrokinra (ICOTYDE) is shown approved (Mar 2026).

## Build
`build_deep.py` (authors the graph from the live roster + cited facts → `graph.json`) → `build.py` (injects into `template.html` → `index.html`).
```bash
python build_deep.py && python build.py
```
See [`docs/data-model.md`](../../docs/data-model.md) for the graph model and the therapeutic-area vs. indication distinction.

## Status
Prototype for **ideation**. Rough edges: 10 lanes scroll horizontally on narrow screens; a few pipeline sales/PASI values are approximate; the therapeutic-area (multi-indication) view is a different hero layout, not built here.
