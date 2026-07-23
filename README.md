# Disease Atlas

**Generate a market-research *atlas* — a highly detailed, interactive single-file web app — for any disease, indication, or therapeutic area, on demand.**

Inspired by the dense, single-page "landscape maps" that RA Capital publishes for therapeutic areas (two are included under [`reference-maps/`](reference-maps/) as the north-star for depth and information density), this project packages that capability as a reusable **[Claude Agent Skill](https://code.claude.com/docs/en/skills)**.

Point it at a disease and it produces a self-contained `atlas_<disease>.html` you can open in any browser or share — a birds-eye view of the whole space that still lets you drill into each angle:

- **Overview & the big picture** — what the disease is, why it matters, headline numbers
- **Patient burden & epidemiology** — prevalence, incidence, segments, natural history, unmet need
- **Disease biology** — pathophysiology, key pathways/targets, subtypes & biomarkers
- **Standard of care** — treatment paradigm by line, top marketed products (company, MoA, approval, sales)
- **Mechanism-of-action landscape** — a proper breakdown of *every* therapeutic approach, with validation status
- **Clinical pipeline** — assets by phase, modality, MoA and company; top companies and drugs
- **Competitive landscape** — who owns what, company × MoA matrix, deal flow
- **Market & opportunity** — market size & forecast, growth drivers, whitespace/unmet need
- **Catalysts & milestones** — upcoming readouts, PDUFA dates, patent cliffs
- **Evidence** — landmark trials and efficacy benchmarks
- **Sources & methods** — every fact traced to a citation

## How it works

The skill is **standalone** — it needs no internal infrastructure. Hard facts come from **public biomedical APIs** (ClinicalTrials.gov, openFDA, Open Targets, PubMed/EuropePMC); market sizing, forecasts and strategic framing come from **Claude with web search**, always cited. See [`docs/vision.md`](docs/vision.md) for the full picture and [`skills/disease-atlas/references/data-sources.md`](skills/disease-atlas/references/data-sources.md) for the exact endpoints.

```
Disease name
   │
   ├─ Public APIs ....... pipeline, trials, approved drugs, targets, literature   (scripts/fetch_*.py)
   ├─ Claude + web search  market size, forecasts, deals, epidemiology, framing    (cited)
   │
   ▼
atlas.json  ──(scripts/render_atlas.py + assets/atlas_template.html)──▶  atlas_<disease>.html
```

## Quickstart (for a person)

Open this repo in [Claude Code](https://www.claude.com/product/claude-code) and ask:

> Build a disease atlas for *[your disease or therapeutic area]*.

The `disease-atlas` skill (auto-discovered via `.claude/skills/`) drives the rest.

## Repository layout

| Path | What's there |
|------|--------------|
| [`skills/disease-atlas/`](skills/disease-atlas/) | **The skill** — `SKILL.md`, reference docs, fetch/render scripts, HTML template |
| [`docs/vision.md`](docs/vision.md) | North star: what the atlas is and the principles behind it |
| [`docs/milestones.md`](docs/milestones.md) | Phased roadmap |
| [`reference-maps/`](reference-maps/) | The RA Capital inspiration maps + a structural analysis |
| [`examples/`](examples/) | Generated example atlases |
| [`AGENTS.md`](AGENTS.md) | Operating manual for Claude / agents working in this repo |

## Status

Early. The skill and its tooling are functional; coverage and polish improve per [`docs/milestones.md`](docs/milestones.md). This is **not** a replacement for [dbtips](https://github.com/aganitha/agentic-ai/tree/main/dbtips) (Aganitha's deep disease-dossier builder) — the atlas deliberately trades dbtips' depth for a broad, fast, strategic bird's-eye view. dbtips is referenced only for its source landscape.
