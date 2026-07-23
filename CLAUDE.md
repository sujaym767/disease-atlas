# CLAUDE.md

The operating manual for this repo is **[AGENTS.md](AGENTS.md)** — read it first. It covers the mission, the golden rules (accuracy + citations, standalone/public sources, single-file HTML, no internal deps, no committed secrets), the skill layout, and the definition of done. This file only adds Claude-Code-specific quick facts.

## What this repo is

The atlas pipeline is **two skills** joined by one contract (`atlas.json`):
- **`disease-atlas`** ([`skills/disease-atlas/`](skills/disease-atlas/)) — the **researcher**: gathers the landscape (public APIs + cited web research) and composes a semantic `atlas.json`.
- **`atlas-build`** ([`skills/atlas-build/`](skills/atlas-build/)) — the **builder**: compiles `atlas.json` into the interactive, self-contained HTML atlas. Deterministic, offline.

The plaque-psoriasis prototype ([`prototypes/psoriasis-spotlight/`](prototypes/psoriasis-spotlight/)) is where the renderer was validated by hand before being generalized into `atlas-build`.

## The skills auto-load

`.claude/skills/{disease-atlas,atlas-build}` symlink into `skills/`, so both are discovered automatically here. To use elsewhere, copy or symlink both `skills/disease-atlas/` and `skills/atlas-build/` into `~/.claude/skills/`.

When a user asks for an atlas / landscape / market map / competitive picture for a disease, indication, or therapeutic area, **invoke `disease-atlas`** and follow its `SKILL.md` — it produces `atlas.json` and hands off to `atlas-build` to render. If they already have an `atlas.json` and just want the HTML (or are re-rendering after an edit), **invoke `atlas-build`** directly.

## Running the tools

From the repo root:

```bash
# 1) RESEARCH (disease-atlas): each fetcher is standalone and prints/writes JSON
python skills/disease-atlas/scripts/fetch_clinical_trials.py --disease "psoriasis" --out runs/psoriasis/raw/trials.json
python skills/disease-atlas/scripts/fetch_openfda.py        --disease "psoriasis" --out runs/psoriasis/raw/openfda.json
python skills/disease-atlas/scripts/ingest_report.py        runs/psoriasis/report-model.json   # market_research layer
python skills/disease-atlas/scripts/validate_atlas.py       runs/psoriasis/atlas.json

# 2) BUILD (atlas-build): compile atlas.json → one self-contained HTML file
python skills/atlas-build/scripts/build_atlas.py runs/psoriasis/atlas.json --out runs/psoriasis/atlas_psoriasis.html
```

Scripts target Python 3.9+ and prefer the standard library, so no environment setup is normally required.

## Don't

- Don't depend on Aganitha-internal infrastructure or credentials — the skills are standalone (see AGENTS.md rule 2).
- Don't hand-edit rendered HTML; change `atlas.json` (data) or `skills/atlas-build/assets/atlas_template.html` (renderer) and rebuild.
- Don't commit secrets or disable TLS verification.
