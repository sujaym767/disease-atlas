# Spotlight Atlas — interactive prototype (plaque psoriasis)

A **presentation prototype** in the visual language of an RA-Capital landscape *poster*, made interactive. The main canvas stays a clean, dense, printed-map view; all the entity-relationship complexity lives in a **large ER-diagram popup** that opens when you click any entity — so the map never turns into a hairball.

**Open [`index.html`](index.html)** (self-contained, offline). Previews: [poster](preview_poster.png) · [ER popup — drug](preview_er_drug.png) · [ER popup — mechanism](preview_er_mechanism.png).

## The poster (main canvas)
Cream paper, condensed masthead, and the pipeline organised into labelled **regions** (IL-23/IL-17 core → oral targeted → TNF & conventional → topical → novel/withdrawn). Each region holds flat **mechanism blocks**; each block lists its drugs as dense rows with a **clinical-stage code** gutter (`M` marketed · `III/II/I` phase · `✕` discontinued) and a compact meta line (company · route + dosing · PASI 90 · FY2025 sales), plus `B` biosimilar / `+` combo / `⚠` boxed-warning markers. A right rail carries RA-style annotations: **market**, a **PASI-90 benchmark**, a dated **catalysts & exclusivity** timeline, top companies, and the legend.

## The ER popup (click anything)
Click a drug, company, mechanism, or target → a large modal opens with, on the left, the entity's **brief description + key facts** (phase, sales, PASI, route/dose, class safety, sources) and, on the right, an **entity-relationship diagram**:
- **A distinct shape per entity type** — drug ● circle, company ▭ rectangle, mechanism ◆ diamond, target ▲ triangle, segment ⬡ hexagon, catalyst ⬠ pentagon, modality ▪ square (shape legend included, so it's not colour-alone).
- **Labelled, directional arrows** naming each relationship (*developed by, has mechanism, targets, serves, catalyst, studied in, modality*).
- Every neighbour is **clickable to re-centre** the diagram — walk the graph one hop at a time.
Search and light/dark are in the masthead; `⎋` closes the popup.

## What's on it (depth ≈ RA Capital density)
- **55 assets** across **10 mechanism families** and the **full phase ladder** (approved → Ph1 → discontinued), mined from the live Open Targets pull (167 candidates) + ClinicalTrials.gov, curated with the well-established late-stage assets.
- Per-drug: company, sub-class, route + maintenance dosing, clinical-stage code, **PASI-90**, **FY2025 sales**, and biosimilar / combo / boxed-warning markers.
- **Efficacy benchmark** — PASI-90 at wk 12–16 (cross-trial, NMA-anchored).
- **Catalysts & exclusivity** — dated 2023→2033 timeline (Humira/Stelara biosimilar cliffs, ICOTYDE approval, oral-TYK2 Phase 3 readouts, patent expiries).
- **Class safety** per mechanism (IL-17 Candida/IBD, TNF boxed warnings, TYK2 vs JAK, IL-23 cleanest) — surfaced in the ER popup.

## Sourcing & accuracy
Pipeline/mechanism/phase from the **live APIs**; sales (FY2025), PASI benchmarks (Armstrong 2020 NMA + pivotal trials), catalysts and biosimilar/patent dates from **cited web research** (see the source chips in each rail). Sales are **all-indication franchise totals**, not psoriasis-only; PASI values are cross-trial unless a head-to-head is noted; a few sales figures are approximate (flagged). It's **July 2026** in the data, so icotrokinra (ICOTYDE) is shown approved (Mar 2026).

## Build
`build_deep.py` (authors the graph from the live roster + cited facts → `graph.json`) → `build.py` (injects into `template.html` → `index.html`).
```bash
python build_deep.py && python build.py
```
See [`docs/data-model.md`](../../docs/data-model.md) for the graph model and the therapeutic-area vs. indication distinction.

## Status
Prototype for **ideation**. Rough edges: a few pipeline sales/PASI values are approximate; a mechanistic pathway schematic and site-level segmentation (scalp/nail/palmoplantar/genital) are not built yet; the therapeutic-area (multi-indication) view is a different poster layout, not built here.
