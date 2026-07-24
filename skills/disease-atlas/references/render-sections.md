# Synthesizing the six render sections

The fetchers give you assets, targets, labels, and papers. They do **not** give you the six sections
that make the atlas read like an RA-Capital landscape rather than a dashboard. You synthesize these
from the gathered data + cited web research. All are optional (the builder degrades gracefully), but
together they are the difference in quality. Shapes are in
`../../atlas-build/references/atlas-schema.md`; this file is the *how*.

Rule throughout: **real, cited, labelled.** Estimates carry `[Estimated]` and a one-line method.
Never invent NCT IDs, names, or figures.

---

## 1. `strategy_map` — the Objective → Asset decision tree (the hero)

A left/right tree that organises the *whole* pipeline by **clinical intent**, not just mechanism.
Four levels: **Objective ▸ Strategy ▸ Approach ▸ Mechanism**, and mechanism leaves list **assets**.

How to build it:
1. Read the roster and cluster by mechanism into **mechanism leaves** (e.g. "IL-23 p19 inhibitors",
   "TYK2 allosteric inhibitors"). Each leaf's `drugs` = asset *names* (must match
   `pipeline.assets[].name`).
2. Group leaves into **approaches** (a shared mechanistic idea, e.g. "Block the IL-23/Th17 axis"),
   approaches into **strategies** (a delivery/therapeutic bet, e.g. "Systemic cytokine-directed
   biologics", "Oral small-molecule targeted therapy"), and strategies into **objectives** — the 2–4
   top-level clinical goals of the field (e.g. "Clear the skin & control inflammation", "Treat
   special/hard-to-treat disease", "Pursue durable remission").
3. Give every objective a `side` (`left`/`right`) and a `colorVar`; give internal nodes a one-line
   `d` rationale. **Place every asset exactly once** — the validator/compiler check for this.

The objectives are your editorial thesis about *what the field is trying to do*. Derive them from the
unmet-need and standard-of-care analysis, not from mechanism alone. This section is pure synthesis —
no API provides it — so it's where your understanding of the indication shows.

## 2. `biology_graph` — the mechanism cascade as first-class nodes

Model the disease's core signalling as a small graph so the schematic is clickable and path-finding
traverses the *biology*, not just the org chart.
1. **Nodes** — the cells, cytokines, receptors and intracellular signalling that define the disease
   (`kind` ∈ cell/cytokine/receptor/intracellular/outcome), each with a concise, original scientific
   `description`. Use Open Targets pathways + the review literature you pulled.
2. **Edges** — the real relationships (`PRODUCES`, `ACTS_ON`, `SIGNALS_VIA`, `LEADS_TO`, `FEEDBACK`,
   `BINDS`, `ACTIVATES`, `INDUCES`, `SUSTAINS`).
3. **`pos`** — give the handful of nodes that belong on the poster schematic a short `pos` key
   (cells + primary cytokines + the outcome); leave signalling nodes without `pos` (they render in
   the inset + network). **`signal_path`** — the ordered intracellular pathway for the inset.
4. **`anchors`** (family_key → node) and **`target_bio`** (target symbol → node) wire the mechanism
   lanes and the drug→target→biology path-finding bridges.

Keep it to ~10–18 nodes: the disease's spine, not a textbook. If the biology genuinely can't be
reduced to a clean cascade, provide fewer nodes (or omit) and let the MoA landscape lead — an honest
partial graph beats a fabricated one.

## 3. `market_research` — the lower bands (via a report-model)

The forecast/funnel/access/competitive layer is a compact **market-research report**. Compose it as a
`report-model.json` — the same method a therapeutic-area analyst uses — then convert it:

```bash
python <skill>/scripts/ingest_report.py runs/<slug>/report-model.json   # → report_data.json
# merge report_data.json into atlas.json under "market_research"
```

`ingest_report.py` reads a `{meta, sources[], sections[]}` model where table `rows` are **lists of
cell strings** parallel to a `columns` array, and maps these sections/tables (by id + column names):

| Section id | Table → atlas field |
|---|---|
| `market_forecast` | forecast-by-segment (`Segment, <years…>, CAGR, assumptions`), scenarios (`Scenario, <y> market, CAGR, swing`), geo (`Region, eligible, penetration, net price, market`) |
| `epidemiology` | patient funnel (`Stage, Population, Basis, Notes`) + segmentation |
| `unmet_need` | gap–opportunity matrix (`Segment, severity, coverage, the gap, addressable, opportunity size`) |
| `stakeholders_access` | payer dashboard (`Market, coverage, HTA body, restriction, net-price signal`) |
| `products_ip` | attribution (`Brand (INN), company, class, FY revenue, indication attribution, access, exclusivity`) + LOE |
| `competitive` | positioning (`Company, position, pipeline depth, posture, strength, vulnerability`) |
| `executive_summary` | catalysts-to-watch + thesis paragraphs |
| `risk_register` | risk register |

**Market-sizing method** (embed the numbers, show the working):
- **Bottom-up**: `diagnosed systemic-eligible patients × advanced-therapy penetration × annual net
  price × treatment duration`, summed across the geographies (US / EU5 / Japan / China / RoW). Net
  price, not list — the two diverge sharply (IRA MFP, biosimilars, confidential PAS).
- **Top-down cross-check**: reconcile against published analyst envelopes; if the headline market-
  research number is built on list prices, treat it as an upper bound and say so.
- **CAGR** = `(end/start)^(1/years) − 1`. State the base year and horizon; a 5y and a 10y CAGR that
  differ tells the LOE story.
- **Scenarios** vary penetration and net-price assumptions (not a multiplier): a Base, a
  Conservative (cannibalisation / step-edits / price war), and an Aggressive (guideline shift / label
  expansion / defended pricing).
- **Attribution**: company revenues are all-indication; estimate the indication-specific split so the
  atlas can correct the "all-indication donut" caveat. Flag every split `[Estimated]`.

If you don't need the full report elsewhere, you can compose `market_research` directly in the shape
in the schema — the report-model is a convenience, not a requirement. Either way, **cite every
figure**.

## 4. `response_kinetics` — the primary-endpoint onset curves

The disease's efficacy analogue of RA-Capital's PK curves: class-representative trajectories of the
**primary endpoint** over time (`weeks` + `series[].pts`). For psoriasis this is PASI-90 by class;
for another indication use its registrational endpoint (e.g. ACR20, EASI-75, HbA1c change, ORR).
Anchor to NMA / onset-of-action data where available; label illustrative.

## 5. `trials_focus` — the strategically important programmes

The handful of pivotal/registrational trials that decide the field, each with CT.gov-style detail
(endpoints, latest readout, timeline, key inclusion, sites, KOLs, why it matters). Pull the granular
fields live from ClinicalTrials.gov v2 by NCT id; curate the readout from cited toplines. Named KOLs
= pivotal-trial lead authors. **Always carry the real `nct_id`** — the builder turns it into a
canonical `clinicaltrials.gov/study/<NCT>` link, and every asset should carry its `nct_ids` (the
fetcher already aggregates them). Programmatic-first: NCT ids, phases, sponsors, targets, MoA,
approvals come from the APIs/MCP tools (`mcp__Clinical_Trials__*`, `mcp__Open_Targets__*`,
`mcp__ChEMBL__*`), verifiable and never guessed; only sales/market/deals/fine-epi are web-cited.

## 6. `glossary`

10–20 key terms a strategy reader needs (endpoints, targets, pathways, market terms). Keep
definitions one sentence and disease-specific.

---

## Working order

Compose the semantic core first (roster → families → MoA → SoC → epi → market → evidence), because
`strategy_map`, `biology_graph`, and `market_research` all build on it. Validate after each addition.
The atlas is only as good as the research beneath it — spend the reasoning there, then let the
builder render it faithfully.
