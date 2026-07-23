# Examples

Generated atlases. Each folder holds the `atlas.json` (the validated data) and the rendered self-contained `atlas_<slug>.html` (open it in any browser).

## plaque-psoriasis

![Plaque psoriasis atlas preview](plaque-psoriasis/preview.png)

- **[atlas_plaque-psoriasis.html](plaque-psoriasis/atlas_plaque-psoriasis.html)** — the interactive atlas (single self-contained file)
- **[atlas.json](plaque-psoriasis/atlas.json)** — the underlying data

A full walk through every panel: overview + headline stats, patient burden & epidemiology, disease biology (IL-23/IL-17 axis + druggable targets), standard of care (top products with sales, class share), the mechanism-of-action landscape (9 classes, color-coded by clinical validation), the clinical pipeline (filterable, with a phase × MoA-class matrix), competitive landscape + deals, market & opportunity, catalysts, evidence (approximate PASI-90 benchmarks + landmark trials), a strategic SWOT, and fully linked sources.

> **Note on how this example was built.** It was generated in an egress-restricted environment where the live public-API fetchers (ClinicalTrials.gov, Open Targets, openFDA) were blocked by network policy. The pipeline, standard-of-care and MoA content therefore reflect established public knowledge of the psoriasis landscape (what those APIs return when reachable), while epidemiology, market and sales figures come from the cited web sources. Efficacy percentages are approximate cross-trial values. Run the skill in a network-permitted environment for a fully API-sourced, dated snapshot — see `../skills/disease-atlas/SKILL.md`.
