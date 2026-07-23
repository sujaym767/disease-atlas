# Milestones

A phased roadmap from "first working atlas" to "expert-grade atlas for any disease, on demand." Each phase lists its goal, concrete deliverables, and a **done-when** bar. Status: ✅ done · 🟡 in progress · ⬜ not started.

Priorities will shift with what real atlases reveal — treat this as a living plan, not a contract.

---

## Phase 0 — Foundations 🟡

**Goal:** a proper project skeleton and an end-to-end pipeline that produces a real, if thin, atlas.

- ✅ Repo structured as a project (`AGENTS.md`, `CLAUDE.md`, `docs/`, reference maps analyzed).
- ✅ Vision and information model written (`docs/vision.md`).
- 🟡 `SKILL.md` + reference docs: blueprint (section spec), data-sources (public APIs), schema (`atlas.json`).
- 🟡 Core tooling: stdlib HTTP helper; fetchers for ClinicalTrials.gov, openFDA, Open Targets, PubMed/EuropePMC; `new_atlas.py`, `validate_atlas.py`, `render_atlas.py`; the HTML template.
- 🟡 First real atlas generated end-to-end for one indication and rendered as a standalone HTML file.

**Done when:** naming a disease produces a validated `atlas.json` and a self-contained `atlas_<disease>.html` that opens offline, with at least the overview, standard-of-care, MoA, and pipeline panels populated from live public data, every fact carrying a source.

---

## Phase 1 — A trustworthy single-disease atlas ⬜

**Goal:** all panels populated, honest, and legible for a typical well-studied indication.

- ⬜ Every blueprint panel renders from `atlas.json`, with graceful empty states where public data is thin.
- ⬜ Market size, forecast, and epidemiology sourced via Claude web search with inline citations; estimates clearly labeled.
- ⬜ Citation system end-to-end: each fact → a `sources[]` entry → a clickable reference in the UI.
- ⬜ Search + filter across pipeline and MoA; shared legend; light/dark, responsive, print-friendly.
- ⬜ Pipeline resilient to any single source failing or returning nothing.

**Done when:** a domain expert reviewing an atlas for a disease they know finds it accurate, appropriately scoped, and free of fabricated facts — and a newcomer finds it a genuinely useful map.

---

## Phase 2 — Depth and accuracy per angle ⬜

**Goal:** raise the quality bar within each panel so the depth-per-angle is decision-grade.

- ⬜ **MoA landscape:** systematic target-class taxonomy per area; validation-status rubric (validated / emerging / unproven) applied consistently; combinations captured.
- ⬜ **Market & opportunity:** more rigorous sizing (bottom-up where possible: eligible population × treatment rate × price), whitespace/unmet-need analysis, patent-cliff detection.
- ⬜ **Competitive landscape:** company × MoA matrix, positioning, and deal-flow (licensing / M&A / co-development) mined and cited.
- ⬜ **Evidence:** landmark trials and efficacy/safety benchmarks per standard endpoints for the area; biomarker/segmentation lens where relevant.
- ⬜ **Catalysts:** upcoming readouts and regulatory/patent dates assembled into a timeline.

**Done when:** each panel would survive scrutiny from a specialist in that dimension (a commercial lead on market, a clinician on evidence, a BD lead on deals).

---

## Phase 3 — Breadth and scale ⬜

**Goal:** works well across the diversity of disease types, and at therapeutic-area scope.

- ⬜ Handles the range: oncology, immunology/inflammation, neuroscience, metabolic, rare/genetic, infectious — each has different data availability and natural structure.
- ⬜ **Therapeutic-area atlases** spanning multiple indications (roll-up + drill-down), not just single indications.
- ⬜ Reproducibility: cached raw pulls, pinned generation date, deterministic re-render from `atlas.json`.
- ⬜ Evaluation harness (skill-creator evals) with a set of reference diseases and quality assertions; regression-checked across iterations.

**Done when:** picking a disease at random from any major area yields a solid atlas without hand-holding, and quality is measured, not vibed.

---

## Phase 4 — Interactivity and polish ⬜

**Goal:** make the atlas a pleasure to explore and to present.

- ⬜ Richer interactions: an interactive mechanistic schematic, a zoomable landscape/"map" view, cross-panel linking (click a drug → its MoA, company, trials).
- ⬜ Poster/print mode that echoes the single-canvas RA Capital feel.
- ⬜ Export to PDF and to a slide deck from the same `atlas.json`.
- ⬜ Theming and accessibility pass (contrast, keyboard nav, screen-reader labels).

**Done when:** the atlas is something people *want* to open and share, and it prints/exports cleanly for a readout.

---

## Phase 5 — Freshness and distribution ⬜

**Goal:** keep atlases current and get the skill into people's hands.

- ⬜ Re-generation and **diffing** (what changed since the last snapshot — new approvals, phase moves, deals).
- ⬜ Packaged as an installable skill (`.skill`) with a clean quickstart.
- ⬜ Optional, clearly-bounded hooks for richer internal data where available — without breaking the standalone default.

**Done when:** a user can install the skill, generate an atlas for their area, re-run it a quarter later, and see exactly what moved.

---

## Explicit non-goals

- Becoming dbtips — exhaustive literature/omics/target-assessment depth is out of scope by design (see `docs/vision.md`).
- Live/streaming data binding — atlases are dated snapshots refreshed by re-generation.
- Investment recommendations — the atlas frames the landscape; it does not advise.
