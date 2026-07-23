# Examples

Generated atlases. Each folder holds the `atlas.json` (the validated data) and the rendered self-contained `atlas_<slug>.html` (open it in any browser).

## plaque-psoriasis

![Plaque psoriasis atlas preview](plaque-psoriasis/preview.png)

- **[atlas_plaque-psoriasis.html](plaque-psoriasis/atlas_plaque-psoriasis.html)** — the interactive atlas (single self-contained file)
- **[atlas.json](plaque-psoriasis/atlas.json)** — the underlying data

A full walk through every panel: overview + headline stats, patient burden & epidemiology, disease biology (IL-23/IL-17 axis + druggable targets), standard of care (top products with sales, class share), the mechanism-of-action landscape (9 classes, color-coded by clinical validation), the clinical pipeline (filterable, with a phase × MoA-class matrix), competitive landscape + deals, market & opportunity, catalysts, evidence (approximate PASI-90 benchmarks + landmark trials), a strategic SWOT, and fully linked sources.

> **Note on how this example was built.** It is **corroborated by a live public-API pull** (2026-07-23): ClinicalTrials.gov returned 901 interventional psoriasis studies, Open Targets 946 associated targets and 167 drug candidates (top targets IL12B / TYK2 / IL23A / TNF / PDE4 / IL17A — matching the MoA panel), and openFDA the approved-product labels and boxed warnings. The pipeline, standard-of-care and MoA **structure match the live data**; company attribution and prose are curated, because raw trial sponsors are noisy (a shared trial can mis-tag a drug's sponsor) — a good illustration of why the skill's synthesis step curates rather than dumps. Epidemiology, market and sales figures come from the cited web sources; efficacy percentages are approximate cross-trial values. See `../skills/disease-atlas/SKILL.md` for the workflow.
