# CLAUDE.md

The operating manual for this repo is **[AGENTS.md](AGENTS.md)** — read it first. It covers the mission, the golden rules (accuracy + citations, standalone/public sources, single-file HTML, no internal deps, no committed secrets), the skill layout, and the definition of done. This file only adds Claude-Code-specific quick facts.

## What this repo is

One thing: the **`disease-atlas`** skill, which generates an interactive market-research atlas (a self-contained HTML web app) for any disease or therapeutic area. The skill is at [`skills/disease-atlas/`](skills/disease-atlas/).

## The skill auto-loads

`.claude/skills/disease-atlas` symlinks to `skills/disease-atlas/`, so when you run Claude Code in this repo the skill is discovered automatically. To use it elsewhere, copy or symlink `skills/disease-atlas/` into `~/.claude/skills/`.

When a user asks for an atlas / landscape / market map / competitive picture for a disease, indication, or therapeutic area, **invoke the `disease-atlas` skill** and follow `SKILL.md`.

## Running the tools

From the repo root:

```bash
# Each fetcher is standalone and prints/writes JSON
python skills/disease-atlas/scripts/fetch_clinical_trials.py --disease "psoriasis" --out runs/psoriasis/raw/trials.json
python skills/disease-atlas/scripts/fetch_openfda.py        --disease "psoriasis" --out runs/psoriasis/raw/openfda.json

# Validate and render
python skills/disease-atlas/scripts/validate_atlas.py runs/psoriasis/atlas.json
python skills/disease-atlas/scripts/render_atlas.py  runs/psoriasis/atlas.json --out runs/psoriasis/atlas_psoriasis.html
```

Scripts target Python 3.9+ and prefer the standard library, so no environment setup is normally required.

## Don't

- Don't depend on Aganitha-internal infrastructure or credentials — this skill is standalone (see AGENTS.md rule 2).
- Don't hand-edit rendered HTML; change `atlas.json` or `assets/atlas_template.html`.
- Don't commit secrets or disable TLS verification.
