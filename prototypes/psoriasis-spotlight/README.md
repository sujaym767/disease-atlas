# Spotlight Atlas — interactive prototype (plaque psoriasis)

A **presentation prototype** built as a single **wall-poster on a zoom/pan canvas**, modelled on RA Capital's *TechAtlas* landscape maps (the Parkinson's map in particular) and made interactive. The hero is a **strategy mind-map** — every asset placed on a decision tree of **Objective ▸ Strategy ▸ Approach ▸ Mechanism ▸ Asset** — surrounded by the data "regions" RA Capital pairs with its maps: a **standard-of-care severity table**, a **franchise-sales donut**, a **company × mechanism development matrix**, an efficacy benchmark, burden/market/deal panels, and a glossary. On top of the paper we add what a printed map can't: **click any asset (or cell/cytokine) for a large ER-diagram popup** (1- or 2-hop), a **focused force-directed Network explorer**, and **"how are X and Y connected" path-finding** that walks *through the biology cascade itself* (modelled as first-class nodes).

**Open [`index.html`](index.html)** (self-contained, offline). Drag to pan, scroll to zoom, click any entity. Previews: [full poster](preview_poster.png) · [strategy map](preview_strategymap.png) · [SoC / sales / dev-matrix](preview_regions.png) · [mechanism schematic](preview_schematic.png) · [signal transduction](preview_signal.png) · [cell ER popup](preview_bio_cell.png) · [2-hop](preview_2hop.png) · [network explorer](preview_network.png) · [path trace](preview_path.png).

## The strategy map (the hero)
The centre is a horizontal **decision tree**, laid out with a tidy-tree algorithm and joined by colour-coded curves, that organises the *whole* landscape by clinical intent — the way RA Capital does — rather than by mechanism family alone:
- **Objective ▸ Strategy ▸ Approach ▸ Mechanism ▸ Asset.** Three objectives (**clear the skin & control inflammation**; **treat special & hard-to-treat disease**; **pursue durable remission & disease interception**) branch down through strategies and approaches to **mechanism boxes**, each carrying a one-line rationale and its **asset rows** — clinical-stage code (`M`/`III`/`II`/`I`/`P`/`✕`), name, `B`/`⚠` markers, and company. All 57 assets are placed exactly once; every row is clickable → its ER popup.
- A **mechanism region** off to the side keeps the clickable **IL-23 / IL-17 cascade** schematic (dendritic cell → IL-23 → Th17 → IL-17A/F → keratinocyte → plaque) and the **intracellular signal-transduction** inset (IL-23R → TYK2/JAK2 → STAT3 → RORγt).
- Corner **regions** (all derivable on demand from the pipeline + cited research): a **standard-of-care severity table** (mild/moderate/severe × therapy bars), a **2025 franchise-sales donut**, a **company × mechanism development matrix**, a **PASI-90 efficacy benchmark**, **patient-burden**, **market**, **catalysts & exclusivity**, **deal-flow**, **comorbidity/QoL**, **market-share & durability**, **trial milestones**, and a **glossary**.

## The ER popup (click anything)
Click a drug, company, mechanism, target, **or a cell/cytokine on the schematic** → a large modal opens with, on the left, the entity's **brief description + key facts** (phase, sales, PASI, route/dose, class safety, sources; for biology nodes, an original scientific summary + the assets that engage it) and, on the right, an **entity-relationship diagram**:
- **A distinct shape per entity type** — drug ● circle, company ▭ rectangle, mechanism ◆ diamond, target ▲ triangle, **biology ⬬ ellipse**, segment ⬡ hexagon, catalyst ⬠ pentagon, modality ▪ square (shape legend included, so it's not colour-alone).
- **Labelled, directional arrows** naming each relationship (*developed by, has mechanism, targets, serves, catalyst, studied in, modality; produces, acts on, signals via, leads to, feedback loop, part of*).
- Every neighbour is **clickable to re-centre** the diagram, and a **1-hop / 2-hop** toggle expands to neighbours-of-neighbours (each 1-hop node gets its own angular wedge; hub types are down-weighted so the ring never explodes).
- **Explore ▸** drops the entity into the Network explorer (below).
Search and light/dark are in the masthead; `⎋` closes the popup.

## The deep-relationship layer (beyond RA Capital)
- **Biology as first-class nodes.** The cascade itself — dendritic cell, Th17, keratinocyte, plaque; IL-23/p40/IL-17/IL-22/TNF; TYK2, PDE4 — is modelled as graph nodes wired by real edges (`produces`, `acts on`, `signals via`, `leads to`, `feedback loop`), and bridged to the pipeline (`target —part of→ biology`, `mechanism —acts on→ biology`). So relationships traverse the *mechanism*, not just the org chart.
- **Network explorer (⌗ toggle).** A **focused** force-directed view (hand-written vanilla sim — repulsion + springs + centering, alpha-cooled): seed from one entity, **click a node to expand** its links hop-by-hop, drag to rearrange, double-click for its card, scroll to zoom. Not a whole-graph hairball — you grow only what you're curious about.
- **Path-finding — "how are X and Y connected".** Pick two entities in the **TRACE** bar → **BFS shortest path** over the undirected graph (the shared indication/modality hubs are excluded as intermediates, so paths go *through the biology*, e.g. `risankizumab —has mechanism→ IL-23/Th17 axis —acts on→ IL-23 —produces→ dendritic cell —feedback loop→ keratinocyte`). The chain is highlighted in the network and spelled out as a text ribbon.

## What's on it (depth ≈ RA Capital density)
- **57 assets** across **10 mechanism families** and the **full phase ladder** (approved → Ph1 → discontinued), mined from the live Open Targets pull (167 candidates) + ClinicalTrials.gov, curated with the well-established late-stage assets.
- Per-drug: company, sub-class, route + maintenance dosing, clinical-stage code, **PASI-90**, **FY2025 sales**, and biosimilar / combo / boxed-warning markers.
- **Efficacy benchmark** — PASI-90 at wk 12–16 (cross-trial, NMA-anchored).
- **Catalysts & exclusivity** — dated 2023→2033 timeline (Humira/Stelara biosimilar cliffs, ICOTYDE approval, oral-TYK2 Phase 3 readouts, patent expiries).
- **Class safety** per mechanism (IL-17 Candida/IBD, TNF boxed warnings, TYK2 vs JAK, IL-23 cleanest) — surfaced in the ER popup.

### Deeper-dive band (added depth across the board)
- **Intracellular signal transduction** — a dedicated pathway inset and 6 new graph nodes (IL-23R, IL-17RA, TYK2, JAK2, STAT3, RORγt, NF-κB): IL-23 → IL-23R → TYK2/JAK2 → STAT3 → RORγt → Th17, and IL-17 → IL-17RA → NF-κB → keratinocyte. Every node is clickable and reachable by path-finding.
- **Standard of care** — a colour-coded **line-of-therapy ladder** (topical → phototherapy → conventional systemics → advanced oral → biologics) with positioning, per AAD-NPF guidance.
- **Landmark clinical-trial milestones** — the pivotal trials that defined each class (ERASURE/UNCOVER/VOYAGE/UltIMMa/ECLIPSE/BE VIVID/POETYK/ICONIC-LEAD…), dated, class-coloured, and click-through to the asset.
- **Glossary** — 18 key terms (PASI, DLQI, TYK2, JAK-STAT, RORγt, drug survival, biosimilar…).
- **Comorbidity & QoL burden** (PsA, metabolic, CV, depression, IBD; DLQI, economics, mortality) and **market share & durability** (share by mechanism class + real-world drug survival).

## Sourcing & accuracy
Pipeline/mechanism/phase from the **live APIs**; sales (FY2025), PASI benchmarks (Armstrong 2020 NMA + pivotal trials), catalysts and biosimilar/patent dates from **cited web research** (see the source chips in each rail). Sales are **all-indication franchise totals**, not psoriasis-only; PASI values are cross-trial unless a head-to-head is noted; a few sales figures are approximate (flagged). It's **July 2026** in the data, so icotrokinra (ICOTYDE) is shown approved (Mar 2026).

## Build
`fetch_drug_detail.py` (optional — enriches every drug from **openFDA** labels + **ChEMBL** molecule/mechanism, writing `drug_detail.json`; PubChem is wired in and used once its host is allowlisted) → `build_deep.py` (authors the graph from the live roster + cited facts, merging any `drug_detail.json` — 17 **Biology** cascade + signalling nodes, the **Objective→Asset hierarchy** placing all 57 assets, and the standard-of-care / trial / glossary / market-share data → `graph.json`; it validates that every asset is placed exactly once) → `build.py` (injects into `template.html` → `index.html`). `verify.py` headless-checks it (no JS errors; asset-chip click; cell click; 2-hop; network expand; path trace) and regenerates the previews. The strategy tree is laid out by a **tidy-tree algorithm** in the renderer, so nothing is hand-positioned.
```bash
python build_deep.py && python build.py && python verify.py
```
See [`docs/data-model.md`](../../docs/data-model.md) for the graph model and the therapeutic-area vs. indication distinction.

## Scope (what's derivable on demand)
This deliberately builds only the regions we can regenerate for *any* indication from public APIs + cited research — the strategy tree is an **organisation of the pipeline** we already fetch; the SoC table, sales donut, and dev matrix are **derived** from guideline knowledge and our own sales/company/phase data. We do **not** reproduce RA Capital's hand-curated, hard-to-get artefacts (quarter-precise PCT-date Gantts, per-drug pharmacokinetic curves) — those would require manual curation that doesn't generalise.

## Status
Prototype for **ideation**. Adds a dedicated **Clinical trials in focus** section (click a trial → endpoints, latest readout, timeline, key inclusion, sites, KOLs; CT.gov-sourced), **separate catalyst and patent-cliff timelines**, a **richer deal-flow** panel (M&A / licensing / partnership × development stage), and **DrugBank / DailyMed / ClinicalTrials.gov** deep-links on every drug card. A single zoom/pan canvas built around the **Objective→Asset strategy map** (tidy-tree layout, all 57 assets placed once), with the IL-23/IL-17 **schematic** + **signal-transduction** inset as a mechanism region, an **SoC severity table**, **franchise-sales donut**, **company × mechanism dev matrix**, efficacy/burden/market/deal/catalyst panels, and a glossary — plus a 1-/2-hop **ER popup**, a focused **Network explorer**, and **path-finding** through the cascade. Rough edges: the canvas is large (zoom/pan, not responsive); a couple of edge labels can crowd at high 2-hop fan-out; a few sales/PASI values are approximate; the therapeutic-area (multi-indication) view is a different layout, not built here.
