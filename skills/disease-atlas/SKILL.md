---
name: disease-atlas
description: >-
  Research a disease, indication, or therapeutic area and produce a market-research ATLAS — a
  highly detailed, interactive, self-contained HTML web app in the spirit of RA Capital's landscape
  maps. This is the RESEARCH + AUTHORING skill: it gathers the landscape from public APIs + cited
  web research and composes a single semantic atlas.json (pipeline, MoA landscape, standard of care,
  epidemiology, biology cascade, the Objective→Asset strategy map, market forecast & scenarios,
  patient funnel & opportunity, payer access, competitive posture, catalysts, evidence), then hands
  off to the atlas-build skill to render it. Use this whenever the user wants to understand or map a
  therapeutic area at a strategic level — "build a disease atlas / landscape / market map for X",
  "map the treatment landscape / pipeline / competition for X", "size the market / show the MoA
  landscape for X", "give me the big picture on X disease" — even if they don't say "atlas". Produces
  atlas.json (+ the rendered atlas_<disease>.html via atlas-build). Standalone: public sources only.
  Not for single-target dossiers or individual clinical decisions.
---

# Disease Atlas — research & author `atlas.json`

The atlas is built in **two skills**: **this one researches** an indication and composes a semantic
**`atlas.json`**; **`atlas-build`** compiles that into the interactive HTML poster. This split means
the research is re-usable and re-renderable — edit `atlas.json`, rebuild, done. Keep them in sync via
the shared contract in **`../atlas-build/references/atlas-schema.md`**.

**Read alongside this file (progressive disclosure — load when the workflow reaches them):**
- `references/atlas-blueprint.md` — what each section should contain and how deep to go.
- `references/render-sections.md` — how to SYNTHESIZE the six render sections that make the atlas
  RA-Capital-grade: the strategy map, the biology cascade, and the market-research layer (forecast /
  funnel / access / competitive), plus response-kinetics, trials-in-focus, and the glossary.
- `references/data-sources.md` — public API endpoints, query recipes, and where each panel's data
  comes from.
- `../atlas-build/references/atlas-schema.md` — the exact `atlas.json` shape the builder consumes.

`<skill>` = this skill's directory (`skills/disease-atlas`). Work in `runs/<disease-slug>/` (git-ignored).

## Prime directives

1. **Accuracy is the product.** Every non-obvious fact (numbers, dates, sales, market size, phases)
   traces to a source in `atlas.json`'s `sources[]`. Label estimates `is_estimate`/`[Estimated]`.
   **Never invent** NCT IDs, drug/company names, or figures — a sourced gap beats a confident guess.
2. **Right altitude.** A strategic map, not a literature review. Breadth first; go deep enough per
   angle to be decision-useful, then stop.
3. **Standalone & cited.** Hard data from public APIs; market/epi/deals from web search with real
   URLs. No internal services or credentials.
4. **Honest empty states.** Thin public data on a section → say so and omit it; the builder shows an
   honest empty state. Never fill with plausible filler.
5. **Intensive is fine.** A great atlas is worth many API calls and a lot of reasoning. Optimize the
   result, not the runtime.

## Workflow

### 0. Scaffold
```bash
python <skill>/scripts/new_atlas.py --disease "plaque psoriasis" --scope indication
# → runs/plaque-psoriasis/{raw/, atlas.json (stub), notes.md}
```

### 1. Scope & resolve
Confirm the target and **scope** (`indication` vs `therapeutic_area`). Collect the common name +
synonyms/abbreviations (query APIs with all). Resolve the Open Targets EFO id
(`fetch_open_targets.py --resolve "<disease>"`).

### 2. Gather hard data (public APIs → `runs/<slug>/raw/`)
Run the fetchers together (standalone, cached, degrade gracefully):
```bash
python <skill>/scripts/fetch_clinical_trials.py --disease "<d>" --out runs/<slug>/raw/trials.json
python <skill>/scripts/fetch_open_targets.py    --disease "<d>" --out runs/<slug>/raw/opentargets.json
python <skill>/scripts/fetch_openfda.py         --disease "<d>" --out runs/<slug>/raw/openfda.json
python <skill>/scripts/fetch_pubmed.py          --disease "<d>" --focus "phase 3 pivotal" --out runs/<slug>/raw/literature.json
```
From these: the pipeline/assets + sponsors (trials), MoA classes + targets (Open Targets
`knownDrugs`), approved products + labels + boxed warnings (openFDA), landmark publications (PubMed).

### 3. Gather commercial / epidemiological facts (web search, cited)
Market size & forecast, product sales, deal flow, fine-grained epidemiology, payer/access — the
panels with no clean API — come from **web search**, each with a real primary source (10-K for
sales; GBD/CDC/WHO or a prevalence study for epi; named analyst report or company guidance for
market). Triangulate; label forecasts as estimates. This is the raw material for the market-research
layer (see `render-sections.md` for the market-sizing method: bottom-up
`patients × treatment-rate × net-price` reconciled against a top-down envelope).

### 4. Compose the SEMANTIC core of `atlas.json`
Follow `atlas-blueprint.md` (editorial) + `../atlas-build/references/atlas-schema.md` (shape). Work
incrementally; validate as you go. Key moves:
- **Normalize & dedupe assets** across trials + Open Targets into one `pipeline.assets[]` (lowercase
  match; keep the highest phase). Give each a stable `id` and the **extended render fields**
  (`family_key`, `sub_class`, `dose`, `annual_sales_usd_m`, `sales_year`, `efficacy`, `biosimilar`,
  `note`) — these drive the cards, donut, dev-matrix, and efficacy panels.
- **Build the MoA landscape / families** by grouping assets by mechanism into classes; each becomes a
  colour lane. Assets bind to a lane via `family_key`.
- **Fill** `overview`, `epidemiology` (with burden extras), `standard_of_care.lines`, `companies`,
  `market`, `catalysts`, `evidence.landmark_trials`, `sites`, `market_share`, attaching `sources` as
  you go.

### 5. Synthesize the SIX render sections — the RA-Capital depth
This is what lifts the atlas from a dashboard to a landscape. See **`references/render-sections.md`**
for the how-to. In brief:
- **`strategy_map`** — the Objective→Strategy→Approach→Mechanism→Asset decision tree; place every
  asset exactly once. (Synthesized from the roster + clinical intent — no API gives this.)
- **`biology_graph`** — the disease's mechanism cascade as first-class nodes + edges (cells,
  cytokines, receptors, intracellular signalling) with a `signal_path` and family `anchors`. Powers
  the clickable schematic and biology path-finding.
- **`market_research`** — forecast & scenarios, patient funnel & opportunity, payer/access, sales
  attribution & competitive posture. Compose a **report-model.json** for the market layer (the
  therapeutic-area research method in `render-sections.md`), then fold it in:
  `python <skill>/scripts/ingest_report.py runs/<slug>/report-model.json` → merge its `market_research`.
- **`response_kinetics`**, **`trials_focus`**, **`glossary`** — the primary-endpoint onset curves,
  the strategically important programmes (CT.gov detail), and key terms.

### 6. Validate
```bash
python <skill>/scripts/validate_atlas.py runs/<slug>/atlas.json
```
Fix every error (missing required fields, dangling `source` refs). Heed warnings (uncited numbers,
empty panels). Confirm `strategy_map` places each asset once and `family_key`s resolve.

### 7. Render (hand off to atlas-build)
```bash
python skills/atlas-build/scripts/build_atlas.py runs/<slug>/atlas.json \
       --out runs/<slug>/atlas_<slug>.html
```
Open it; confirm the strategy map, mechanism schematic, ER popup, network + path-finding, and the
four market-research bands render (or show honest empty states).

### 7b. QC gate (data + visual)
```bash
python skills/atlas-build/scripts/qc_atlas.py runs/<slug>/atlas.json \
       --html runs/<slug>/atlas_<slug>.html --check-links --shot runs/<slug>/qc.png
```
Blocks delivery on hard failures: malformed/dead NCT ids or source URLs, a data section that
rendered empty, or any JS error. It also reports a canvas **fill-ratio** (low = blank space to
tune). Then do the **LLM-judgment pass** on the saved screenshot — check for mislabelling (e.g. an
endpoint named for the wrong indication), overlaps, and aesthetic balance the deterministic gate
can't see. Fix and re-run until QC passes clean.

### 8. Deliver
Share the HTML (renders as a Claude artifact, opens by double-click). Summarize the headline picture,
what's well-covered vs thin, and the key caveats. Offer to promote a finished atlas into `examples/`.

## Tips & guardrails
- **Parallelize** independent fetches; **cache** raw responses.
- Always query condition APIs with the common name *and* abbreviations, then merge.
- Keys come from env vars; **TLS stays on**; never commit secrets (don't copy `dbtips` anti-patterns).
- **Don't hand-edit the rendered HTML** — change `atlas.json` and rebuild via atlas-build.
- If a source API is down or empty, continue with the others and reflect the gap honestly — the
  pipeline must never hard-fail on one source.
