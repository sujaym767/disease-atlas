# AGENTS.md — operating manual for this repo

This file orients any AI agent (Claude Code and others) working in **disease-atlas**. Humans: this doubles as the contributor guide. `CLAUDE.md` points here.

## What this repo is

Two complementary **Claude Agent Skills** that together generate a market-research **atlas** — an interactive, self-contained HTML web app — for any disease, indication, or therapeutic area. The atlas is a *bird's-eye strategic map* (standard of care, MoA landscape, pipeline, competition, market, opportunity), dense but broad. Think RA Capital's single-page landscape posters, made interactive and generated on demand.

The pipeline is split into a **researcher** and a **builder**, joined by one contract (`atlas.json`):

```
disease-atlas (research + author)  ──►  atlas.json  ──►  atlas-build (compile + render)  ──►  atlas_<disease>.html
```

- [`skills/disease-atlas/`](skills/disease-atlas/) — **the researcher.** Gathers the landscape from public APIs + cited web research and composes a semantic `atlas.json` (pipeline, MoA landscape, SoC, epidemiology, the biology cascade, the Objective→Asset strategy map, the market-research layer, catalysts, evidence). Standalone; public sources only.
- [`skills/atlas-build/`](skills/atlas-build/) — **the builder.** A pure, offline function of `atlas.json`: `compile_atlas.py` authors the property graph and `build_atlas.py` injects it into the interactive template → one self-contained HTML file. No APIs, no synthesis.

`atlas.json` is the seam: research is reusable and the atlas is re-renderable by editing the data and rebuilding. The plaque-psoriasis prototype in [`prototypes/psoriasis-spotlight/`](prototypes/psoriasis-spotlight/) is where the renderer + graph-authoring were validated by hand before being generalized into `atlas-build`.

## Read these first

1. [`docs/vision.md`](docs/vision.md) — what we're building and why; the atlas information model.
2. [`skills/disease-atlas/SKILL.md`](skills/disease-atlas/SKILL.md) — the research + authoring workflow.
3. [`skills/disease-atlas/references/render-sections.md`](skills/disease-atlas/references/render-sections.md) — how to synthesize the six sections that make the atlas RA-Capital-grade (strategy map, biology cascade, market-research layer, response kinetics, trials-in-focus, glossary).
4. [`skills/atlas-build/SKILL.md`](skills/atlas-build/SKILL.md) + [`skills/atlas-build/references/atlas-schema.md`](skills/atlas-build/references/atlas-schema.md) — the builder and the exact `atlas.json` contract.
5. [`skills/disease-atlas/references/atlas-blueprint.md`](skills/disease-atlas/references/atlas-blueprint.md) + [`data-sources.md`](skills/disease-atlas/references/data-sources.md) — the section spec and the public APIs.

## Golden rules

These are the non-negotiables that make the output trustworthy and the skill portable.

1. **Accuracy over completeness. Every non-obvious fact carries a source.** A sourced "we don't know" beats a confident guess. Sales figures, market sizes, prevalence, approval dates, trial phases — all must be traceable to a citation in the atlas's `sources` list. When a number is a model estimate or synthesis, label it as such and show the reasoning. Never invent NCT IDs, drug names, company names, or dollar figures.
2. **Standalone by default — public sources only.** Hard data comes from public APIs (ClinicalTrials.gov, openFDA, Open Targets, PubMed/EuropePMC). Softer, commercial facts (market size, forecasts, deals) come from Claude web search, cited. **Do not** wire in Aganitha-internal services (`DBTIPS_BACKEND`, `*.aganitha.ai`, private PyPI, LDAP creds). The reference project `dbtips` hides its public sources behind an authenticated backend; we deliberately do not depend on it.
3. **The atlas is one self-contained `.html` file.** Inline all CSS/JS; embed the data as a JSON `<script>` block. No build step, no external requests at view time, no CDN. It must open by double-click and render as a Claude artifact.
4. **Data and presentation are separate — that's the whole architecture.** The researcher produces a validated `atlas.json`; `atlas-build` (`compile_atlas.py` → the property graph → `assets/atlas_template.html`) turns it into HTML. Never hand-edit generated HTML — change the data (`atlas.json`) or the template.
5. **Scripts are dependency-light and safe.** No third-party Python packages — `scripts/lib/http.py` uses the system **`curl`** when present (it clears the WAF/bot fingerprinting that 403s the Python TLS client on some hosts, notably ClinicalTrials.gov) and falls back to `urllib`; both honor `HTTPS_PROXY`/`HTTP_PROXY` and **verify TLS** — **never** disable certificate verification. Read API keys from env vars only; **never** commit secrets or hardcode keys (the `dbtips` repo has a committed NCBI key and a `CERT_NONE` client — do not copy those patterns). Note the fetchers need the API hosts allowlisted in the environment's network policy (see `references/data-sources.md` → Network requirements).
6. **Degrade gracefully.** Not every disease has rich data for every panel. Missing data becomes an honest "insufficient public data" note in that panel, never a fabricated filler. The pipeline must not crash because one source is empty or an API is down.

## How the skills are structured

```
skills/
├── disease-atlas/                 # THE RESEARCHER — landscape → atlas.json
│   ├── SKILL.md                   #   research + authoring workflow
│   ├── references/                #   loaded on demand (progressive disclosure)
│   │   ├── atlas-blueprint.md     #     section-by-section editorial spec
│   │   ├── render-sections.md     #     how to synthesize the six RA-Capital render sections
│   │   ├── data-sources.md        #     public API endpoints, query recipes, rate limits
│   │   └── atlas-schema.md        #     atlas.json semantic-core schema
│   └── scripts/                   #   deterministic helpers Claude runs
│       ├── lib/http.py            #     stdlib HTTP helper (retries, proxy, TLS)
│       ├── fetch_clinical_trials.py · fetch_openfda.py · fetch_open_targets.py · fetch_pubmed.py
│       ├── ingest_report.py       #     report-model.json → market_research layer
│       ├── new_atlas.py           #     scaffold a run dir + stub atlas.json
│       └── validate_atlas.py      #     check atlas.json against the schema
└── atlas-build/                   # THE BUILDER — atlas.json → single-file HTML
    ├── SKILL.md
    ├── references/atlas-schema.md #   the full build contract (render sections + extended fields)
    ├── scripts/compile_atlas.py   #   author the property graph from atlas.json
    ├── scripts/build_atlas.py     #   compile + inject → self-contained HTML
    └── assets/atlas_template.html #   the interactive renderer (inline CSS/JS, vanilla SVG)
```

Progressive disclosure matters: keep each `SKILL.md` lean (< ~500 lines) and push detail into `references/`. Claude loads a reference file only when the workflow needs it.

## Conventions

- **Run directory.** A generation run works in `runs/<disease-slug>/` (git-ignored): raw API responses in `raw/`, the assembled `atlas.json`, and the rendered `atlas_<slug>.html`. Promote finished, curated atlases into `examples/`.
- **Slugs.** Lowercase, hyphenated, ASCII (`non-small-cell-lung-cancer`). One helper owns slugification; reuse it.
- **Python.** 3.9+. Standard library first. If a script truly needs a third-party package, add it to `skills/disease-atlas/scripts/requirements.txt` and make the import failure produce a clear, actionable message.
- **Every script is runnable standalone** (`python scripts/fetch_clinical_trials.py --help`) and prints JSON to stdout or a `--out` file, so steps are independently testable and re-runnable.
- **Citations are first-class.** Fetchers attach provenance (source name, URL, retrieval date) to every record. The renderer surfaces citations and links.

## Definition of done for a change

- [ ] Scripts run with stdlib-only (or a declared, guarded dependency) and handle empty/failed sources without crashing.
- [ ] `atlas.json` still validates against the schema (`python scripts/validate_atlas.py`).
- [ ] The rendered atlas opens standalone (no external requests) and every panel renders (or shows an honest empty state).
- [ ] No secrets, no internal-only endpoints, TLS verification intact.
- [ ] Docs/blueprint/schema updated if the data model or workflow changed.

## Git

Work on the branch you were assigned; commit with clear messages; push when a unit of work is complete. Don't open a PR unless explicitly asked.
