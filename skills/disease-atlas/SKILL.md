---
name: disease-atlas
description: >-
  Generate a market-research "atlas" — a highly detailed, interactive, self-contained
  HTML web app — for any disease, indication, or therapeutic area. The atlas is a
  bird's-eye strategic landscape (in the spirit of RA Capital's landscape maps): patient
  burden & epidemiology, standard of care with top products and sales, a full
  mechanism-of-action breakdown, the clinical pipeline by phase/company, the competitive
  landscape and deals, market size & forecast, opportunity/whitespace, catalysts, and
  cited evidence. Use this whenever the user wants to understand or map a therapeutic
  area or indication at a strategic level — e.g. "build a disease atlas / landscape /
  market map for X", "map the treatment landscape / competitive landscape / pipeline for
  X", "what are the mechanisms of action / SoC / market size / players in X", "give me
  the big picture on X disease", or asks for a therapeutic-area overview, drug-development
  landscape, or MoA/pipeline map — even if they don't use the word "atlas". Produces a
  standalone atlas_<disease>.html from public APIs + cited web research. Not for deep
  single-target dossiers (that's dbtips) or individual patient/clinical decisions.
---

# Disease Atlas

Generate an interactive market-research **atlas** for a disease, indication, or therapeutic area: a single self-contained `atlas_<disease>.html` that maps the whole landscape and lets the reader drill into each angle.

**Read alongside this file (load as needed — progressive disclosure):**
- `references/atlas-blueprint.md` — what each panel should contain and how deep to go.
- `references/atlas-schema.md` — the `atlas.json` contract the renderer consumes.
- `references/data-sources.md` — public API endpoints, query recipes, and where each panel's data comes from.

Below, `<skill>` = this skill's directory (in the repo, `skills/disease-atlas`). Work in a run directory `runs/<disease-slug>/` (git-ignored).

## The prime directives

1. **Accuracy is the product.** Every non-obvious fact (numbers, dates, sales, market size, phases) must trace to a source in `atlas.json`'s `sources[]`. Label estimates as estimates. **Never invent** NCT IDs, drug/company names, or figures — a sourced gap beats a confident fabrication.
2. **Right altitude.** This is a strategic map, not a literature review. Breadth first; go deep enough per angle to be decision-useful, then stop.
3. **Standalone & cited.** Hard data from public APIs; market/epi/deals from web search, always with real URLs. No internal services or credentials.
4. **Honest empty states.** Thin public data on a panel → say so. Never fill with plausible filler.
5. **Intensive is fine.** A great atlas is worth many API calls and a lot of reasoning. Optimize the result, not the runtime.

## Workflow

### 0. Scaffold the run
```bash
python <skill>/scripts/new_atlas.py --disease "plaque psoriasis" --scope indication
# creates runs/plaque-psoriasis/{raw/,atlas.json (stub),notes.md} and prints the slug
```

### 1. Scope & resolve
- Confirm the target and **scope**: a single `indication` (e.g. plaque psoriasis) or a broader `therapeutic_area` (e.g. immuno-oncology) that rolls up several indications. If the user's request is broad ("oncology"), consider narrowing or note that the atlas will be area-level. Ask only if genuinely ambiguous.
- Collect the **common name + key synonyms/abbreviations** (query APIs with all of them).
- Resolve the **Open Targets EFO id** (`fetch_open_targets.py --resolve "<disease>"`) — it canonicalizes synonyms and unlocks targets/known-drugs.

### 2. Gather hard data (public APIs → `runs/<slug>/raw/`)
Run the fetchers (they're standalone, cache to `--out`, and degrade gracefully). These are independent — run them together.
```bash
python <skill>/scripts/fetch_clinical_trials.py --disease "plaque psoriasis" --out runs/plaque-psoriasis/raw/trials.json
python <skill>/scripts/fetch_open_targets.py   --disease "plaque psoriasis" --out runs/plaque-psoriasis/raw/opentargets.json
python <skill>/scripts/fetch_openfda.py        --disease "psoriasis"       --out runs/plaque-psoriasis/raw/openfda.json
python <skill>/scripts/fetch_pubmed.py         --disease "plaque psoriasis" --focus "phase 3 pivotal" --out runs/plaque-psoriasis/raw/literature.json
```
Then read the raw files. From them you get: the pipeline/assets and sponsors (trials), mechanism-of-action classes and targets (Open Targets `knownDrugs`), approved products + labels + boxed warnings (openFDA), and landmark publications (PubMed/Europe PMC). See `data-sources.md` for field maps.

### 3. Gather commercial / epidemiological facts (web search, cited)
The panels with no clean API — **market size & forecast, product sales, deal flow, fine-grained epidemiology** — come from **web search**. For each: find a real, preferably primary source (company 10-K for sales; GBD/CDC/WHO or a prevalence study for epi; a named analyst report for market size), capture the URL, and add a `sources[]` entry. Triangulate when sources disagree; label forecasts `is_estimate: true`. If you can't source a number, leave it out and note it in `coverage_note`. (See `data-sources.md` §6.)

### 4. Synthesize `atlas.json`
Build the atlas **section by section** following `atlas-blueprint.md` for editorial guidance and `atlas-schema.md` for shape. Work incrementally — write the file, add sections, re-validate. Key moves:
- **Normalize & dedupe assets** across trials + Open Targets into one `pipeline.assets` list (lowercase-match names; keep the highest phase). Give each a stable `id`.
- **Build the MoA landscape** by grouping assets/known-drugs by mechanism/target into classes; for each class write rationale, mechanism, trade-offs, validation status, key players; reference member drug ids. Include emerging and failed classes — breadth is the point.
- **Attach `sources` as you go** so nothing ends up uncited. Add the source entry the moment you use a datum.
- Fill `overview`, `epidemiology`, `biology`, `standard_of_care`, `companies`, `market`, `catalysts`, `evidence`, and (optionally) `swot`. Set `meta.coverage_note` honestly.

For anything but a trivial disease this is a lot of structured writing — that's expected. If helpful, assemble large sections as separate JSON fragments and merge, keeping `atlas.json` the single source of truth.

### 5. Validate
```bash
python <skill>/scripts/validate_atlas.py runs/plaque-psoriasis/atlas.json
```
Fix every error (missing required fields, dangling `source` refs, bad enums) and heed warnings (uncited numbers, empty panels).

### 6. Render
```bash
python <skill>/scripts/render_atlas.py runs/plaque-psoriasis/atlas.json \
       --out runs/plaque-psoriasis/atlas_plaque-psoriasis.html
```
This inlines everything into one HTML file (no external requests at view time). Open it to confirm every panel renders (or shows an honest empty state), filters/search work, and citations link out.

### 7. Deliver
Share the HTML (it renders as a Claude artifact and opens by double-click). Summarize for the user: the headline picture, what's well-covered vs thin, and the key caveats from `coverage_note`. Offer to promote a finished atlas into `examples/`.

## Tips & guardrails
- **Parallelize** the independent fetches; **cache** raw responses so re-runs don't re-hit APIs.
- **Synonyms**: always query condition APIs with the common name *and* abbreviations, then merge.
- **Don't** copy `dbtips` anti-patterns (committed keys, disabled TLS). Keys come from env vars; TLS stays on.
- **Don't** hand-edit the rendered HTML — change `atlas.json` or `assets/atlas_template.html` and re-render.
- If a source API is down or empty, continue with the others and reflect the gap honestly — the pipeline must never hard-fail on one source.
