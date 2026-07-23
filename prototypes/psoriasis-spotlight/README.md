# Spotlight Atlas — interactive prototype (plaque psoriasis)

A **presentation prototype** built as a single **wall-poster on a zoom/pan canvas** (in the spirit of the RA-Capital landscape maps), made interactive. The pipeline hangs off a **central, clickable IL-23/IL-17 biology schematic**; per-entity relationships live in a **large ER-diagram popup** (1-hop or 2-hop) on click; and a **focused force-directed Network explorer** plus **"how are X and Y connected" path-finding** let you walk the graph — including *through the biology cascade itself*, which is modelled as first-class nodes. So the map stays a clean poster, and the relationship depth is one click (or one trace) away.

**Open [`index.html`](index.html)** (self-contained, offline). Drag to pan, scroll to zoom, click any entity. Previews: [poster](preview_poster.png) · [central schematic](preview_schematic.png) · [signal transduction](preview_signal.png) · [standard of care](preview_soc.png) · [cell ER popup](preview_bio_cell.png) · [2-hop](preview_2hop.png) · [network explorer](preview_network.png) · [path trace](preview_path.png).

## The poster (single canvas)
A cream-paper canvas anchored by the **IL-23 / IL-17 immune cascade** schematic in the centre (dendritic cell → IL-23 → Th17 → IL-17A/F → keratinocyte → plaque, over faint dermis/epidermis bands, with clickable cells, ringed cytokine nodes, intracellular TYK2/PDE4, and short annotations along the arrows — *secretes, sustains Th17, signals via TYK2, amplifies, self-amplifying feedback loop*). Each **mechanism block** sits at the edge and is joined to *its point of action on the schematic* by a colour-coded **orthogonal elbow** connector (staggered per family so parallel runs don't collide) — so you read the biology and the drugs that engage it together. Blocks list drugs as dense rows: a **clinical-stage-code** gutter (`M` marketed · `III/II/I` phase · `P` preclin · `✕` disc.) + a compact meta line (company · route+dosing · PASI 90 · FY2025 sales) + `B`/`+`/`⚠` markers. Data panels are tucked into the corners like the real thing: **patient burden**, **market**, a **PASI-90 benchmark**, **hard-to-treat sites & populations**, a dated **catalysts & exclusivity** timeline, **deal-flow**, and the **legend**.

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
`build_deep.py` (authors the graph from the live roster + cited facts, incl. the 17 **Biology** cascade + signalling nodes and their bridge edges, plus the standard-of-care / trial / glossary data → `graph.json`) → `build.py` (injects into `template.html` → `index.html`). `verify.py` headless-checks it (no JS errors; cell click; 2-hop; network expand; path trace) and regenerates the previews.
```bash
python build_deep.py && python build.py && python verify.py
```
See [`docs/data-model.md`](../../docs/data-model.md) for the graph model and the therapeutic-area vs. indication distinction.

## Status
Prototype for **ideation**. A single zoom/pan canvas: central clickable IL-23/IL-17 **schematic**, orthogonal-elbow connectors, **hard-to-treat-site** segmentation, **deal-flow**, **patient-burden** panel; a 1-/2-hop **ER popup**; a focused force-directed **Network explorer**; and **path-finding** through the cascade. Rough edges: the fixed layout is hand-tuned, so it isn't responsive; a couple of edge labels can crowd at high 2-hop fan-out; a few sales/PASI values are approximate; the therapeutic-area (multi-indication) view is a different poster layout, not built here.
