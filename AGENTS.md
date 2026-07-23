# AGENTS.md — operating manual for this repo

This file orients any AI agent (Claude Code and others) working in **disease-atlas**. Humans: this doubles as the contributor guide. `CLAUDE.md` points here.

## What this repo is

A single **Claude Agent Skill**, `disease-atlas`, that generates a market-research **atlas** — an interactive, self-contained HTML web app — for any disease, indication, or therapeutic area. The atlas is a *bird's-eye strategic map* (standard of care, MoA landscape, pipeline, competition, market, opportunity), dense but broad. Think RA Capital's single-page landscape posters, made interactive and generated on demand.

The skill lives at [`skills/disease-atlas/`](skills/disease-atlas/) and is the product. Everything else (docs, reference maps) supports it.

## Read these first

1. [`docs/vision.md`](docs/vision.md) — what we're building and why; the atlas information model.
2. [`skills/disease-atlas/SKILL.md`](skills/disease-atlas/SKILL.md) — the generation workflow the skill runs.
3. [`skills/disease-atlas/references/atlas-blueprint.md`](skills/disease-atlas/references/atlas-blueprint.md) — the section-by-section spec (derived from the RA Capital maps).
4. [`skills/disease-atlas/references/data-sources.md`](skills/disease-atlas/references/data-sources.md) — public APIs + how to query them.
5. [`skills/disease-atlas/references/atlas-schema.md`](skills/disease-atlas/references/atlas-schema.md) — the `atlas.json` contract the renderer consumes.

## Golden rules

These are the non-negotiables that make the output trustworthy and the skill portable.

1. **Accuracy over completeness. Every non-obvious fact carries a source.** A sourced "we don't know" beats a confident guess. Sales figures, market sizes, prevalence, approval dates, trial phases — all must be traceable to a citation in the atlas's `sources` list. When a number is a model estimate or synthesis, label it as such and show the reasoning. Never invent NCT IDs, drug names, company names, or dollar figures.
2. **Standalone by default — public sources only.** Hard data comes from public APIs (ClinicalTrials.gov, openFDA, Open Targets, PubMed/EuropePMC). Softer, commercial facts (market size, forecasts, deals) come from Claude web search, cited. **Do not** wire in Aganitha-internal services (`DBTIPS_BACKEND`, `*.aganitha.ai`, private PyPI, LDAP creds). The reference project `dbtips` hides its public sources behind an authenticated backend; we deliberately do not depend on it.
3. **The atlas is one self-contained `.html` file.** Inline all CSS/JS; embed the data as a JSON `<script>` block. No build step, no external requests at view time, no CDN. It must open by double-click and render as a Claude artifact.
4. **Data and presentation are separate.** The pipeline produces a validated `atlas.json`; `render_atlas.py` + `assets/atlas_template.html` turn it into HTML. Never hand-edit generated HTML — change the data or the template.
5. **Scripts are dependency-light and safe.** Prefer the Python standard library (`urllib`) so scripts run anywhere without `pip install`. Respect `HTTPS_PROXY`/`HTTP_PROXY`. Verify TLS — **never** disable certificate verification. Read API keys from env vars only; **never** commit secrets or hardcode keys (the `dbtips` repo has a committed NCBI key and a `CERT_NONE` client — do not copy those patterns).
6. **Degrade gracefully.** Not every disease has rich data for every panel. Missing data becomes an honest "insufficient public data" note in that panel, never a fabricated filler. The pipeline must not crash because one source is empty or an API is down.

## How the skill is structured

```
skills/disease-atlas/
├── SKILL.md               # entry point: when-to-use + the workflow
├── references/            # loaded on demand (progressive disclosure)
│   ├── atlas-blueprint.md #   section-by-section spec + what goes in each
│   ├── data-sources.md    #   public API endpoints, query recipes, rate limits
│   └── atlas-schema.md     #   atlas.json schema + field docs
├── scripts/               # deterministic helpers Claude runs
│   ├── lib/http.py        #   stdlib HTTP helper (retries, proxy, TLS)
│   ├── fetch_clinical_trials.py   # ClinicalTrials.gov API v2
│   ├── fetch_openfda.py           # openFDA drug labels/approvals
│   ├── fetch_open_targets.py      # Open Targets GraphQL (targets, drugs, tractability)
│   ├── fetch_pubmed.py            # NCBI E-utilities / EuropePMC
│   ├── new_atlas.py              # scaffold a run dir + empty atlas.json
│   ├── validate_atlas.py         # check atlas.json against the schema
│   └── render_atlas.py           # atlas.json -> single-file HTML
└── assets/
    └── atlas_template.html       # the interactive template (inline CSS/JS)
```

Progressive disclosure matters: keep `SKILL.md` lean (< ~500 lines) and push detail into `references/`. Claude loads a reference file only when the workflow needs it.

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
