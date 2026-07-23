# `atlas.json` schema (v1)

The atlas is data first. The whole pipeline produces one validated JSON document — `atlas.json` — and the renderer is a pure function of it. This file is the contract between the data-gathering steps and `render_atlas.py`. Keep them in sync: if you add a field here, teach the renderer to show it; if the renderer needs something, add it here first.

`scripts/validate_atlas.py` enforces the structural rules below (stdlib only, no `jsonschema` dependency). Run it before rendering.

## Table of contents
- [Design rules](#design-rules)
- [Top-level shape](#top-level-shape)
- [Shared conventions: sources, estimates, refs](#shared-conventions)
- [Section-by-section](#section-by-section)
- [Enumerations](#enumerations)
- [Minimal valid example](#minimal-valid-example)

## Design rules

1. **Every section is optional except `meta` and `sources`.** A thin atlas is valid; a fabricated one is not. Omit what you can't source rather than inventing it. The renderer shows an honest empty state for missing/empty sections.
2. **Facts cite sources.** Any object carrying a non-obvious claim (a number, a date, a sales figure, a market size) SHOULD include a `sources` array of source ids. The renderer makes these clickable.
3. **Estimates are labeled.** If a value is a model estimate or a synthesis rather than a directly reported figure, set `is_estimate: true`. Never present an estimate as a reported fact.
4. **Drugs live once.** Every drug/asset is defined once in `pipeline.assets` with a stable `id`. Other sections (`moa_landscape`, `companies`) reference it by id. This keeps filtering and cross-linking coherent.
5. **Strings are display-ready.** Values like `"~7.5M"` or `"$21.2B"` may be pre-formatted for humans; numeric fields with a `_usd_m`/`_pct`/`_num` suffix are machine numbers the renderer may chart. Provide the numeric form when you can.

## Top-level shape

```jsonc
{
  "schema_version": "1.0",
  "meta":            { ... },          // required
  "headline_stats":  [ Stat, ... ],
  "overview":        { ... },
  "epidemiology":    { ... },
  "biology":         { ... },
  "standard_of_care":{ ... },
  "moa_landscape":   [ MoAClass, ... ],
  "pipeline":        { "assets": [ Asset, ... ], ... },
  "companies":       [ Company, ... ],
  "market":          { ... },
  "catalysts":       [ Catalyst, ... ],
  "evidence":        { ... },
  "swot":            { ... },          // optional strategic synthesis
  "legend":          { ... },          // usually filled by render defaults
  "sources":         [ Source, ... ],  // required (may be empty only for a stub)
  "disclaimers":     [ "string", ... ]
}
```

## Shared conventions

**Source** (entry in top-level `sources[]`):
```jsonc
{
  "id": "s1",                     // unique, referenced elsewhere as "sources": ["s1"]
  "type": "api",                  // api | web | publication | label | guideline | filing | estimate
  "name": "ClinicalTrials.gov",   // short source name
  "title": "NCT01234567 – A Study of …",
  "url": "https://clinicaltrials.gov/study/NCT01234567",
  "accessed": "2026-07-23",       // ISO date the data was retrieved
  "note": "phase, sponsor, status"
}
```

**source refs** — anywhere you see `"sources": ["s1","s7"]`, those must resolve to `sources[].id`. `validate_atlas.py` flags dangling refs.

**Stat** (used by `headline_stats`):
```jsonc
{ "label": "US prevalence", "value": "~7.5M", "detail": "~2–3% of adults",
  "value_num": 7500000, "is_estimate": false, "sources": ["s3"] }
```

## Section-by-section

### `meta` (required)
```jsonc
{
  "disease": "Plaque psoriasis",         // required
  "aliases": ["psoriasis vulgaris"],
  "scope": "indication",                  // "indication" | "therapeutic_area"
  "generated": "2026-07-23",              // required, ISO date
  "generator": "disease-atlas skill v0.1",
  "one_liner": "Chronic immune-mediated skin disease driven by the IL-23/IL-17 axis.",
  "coverage_note": "Pipeline from ClinicalTrials.gov + Open Targets; market from cited analyst sources."
}
```

### `overview`
```jsonc
{ "definition": "…", "pathophysiology": "…", "state_of_play": "…narrative…", "sources": ["s1"] }
```

### `epidemiology`
```jsonc
{
  "summary": "…",
  "measures": [ { "label": "Global prevalence", "value": "≈125M", "value_num": 125000000,
                  "year": 2023, "geography": "Global", "is_estimate": true, "sources": ["s3"] } ],
  "segments": [ { "name": "Moderate-to-severe", "share": "~20%", "share_pct": 20, "note": "…", "sources": [] } ],
  "demographics": "…", "unmet_need": "…",
  "patient_journey": [ { "stage": "Onset", "description": "…" } ],
  "sources": []
}
```

### `biology`
```jsonc
{
  "summary": "…",
  "pathways": [ { "name": "IL-23/IL-17 axis", "role": "…", "sources": [] } ],
  "targets":  [ { "symbol": "IL17A", "name": "Interleukin-17A", "rationale": "…",
                  "tractability": "clinically drugged", "sources": [] } ],
  "subtypes": [ { "name": "…", "description": "…", "biomarker": "…" } ],
  "schematic": null                       // reserved for a structured mechanistic diagram
}
```

### `standard_of_care`
```jsonc
{
  "paradigm": "…narrative by line/severity…",
  "lines": [ { "line": "First-line (mild)", "options": ["topical corticosteroids","vitamin D analogs"], "note": "…" } ],
  "top_products": [ { "brand": "Humira", "generic": "adalimumab", "company": "AbbVie",
                      "moa_class": "TNF inhibitor", "modality": "mAb", "approval_year": 2002,
                      "key_indications": ["plaque psoriasis"], "annual_sales_usd_m": 21200,
                      "sales_year": 2022, "note": "…", "sources": ["s5"] } ],
  "class_share": [ { "class": "IL-17 inhibitors", "share_pct": 28, "basis": "2023 sales", "sources": [] } ],
  "guidelines": [ { "name": "AAD-NPF 2019", "note": "…", "url": "…" } ],
  "sources": []
}
```

### `moa_landscape` — the core panel (array of MoAClass)
```jsonc
{
  "class": "IL-23 inhibitors",
  "target": "IL23 (p19 subunit)",
  "rationale": "why this target matters in the disease",
  "mechanism": "what the drugs do mechanistically",
  "modality": "mAb",                       // see modalities enum
  "validation_status": "validated",        // validated | emerging | unproven | failed
  "pros": ["durable response","q8–12w dosing"],
  "cons": ["cost","parenteral"],
  "key_players": ["Janssen","AbbVie","Sun Pharma"],
  "drugs": ["d_risankizumab","d_guselkumab"],   // ids into pipeline.assets
  "sources": []
}
```

### `pipeline`
```jsonc
{
  "summary": "…",
  "assets": [ {
    "id": "d_risankizumab",                // required, unique, stable
    "name": "risankizumab",                // required (generic/INN preferred)
    "brand": "Skyrizi",
    "company": "AbbVie",
    "moa_class": "IL-23 inhibitor",
    "target": "IL23A",
    "modality": "mAb",                     // see modalities enum
    "phase": "approved",                   // see phases enum (string)
    "phase_num": 5,                        // numeric rank for sorting/matrix (see enum)
    "indications": ["plaque psoriasis","psoriatic arthritis"],
    "route": "SC",
    "mechanism": "anti-IL-23 p19 mAb",
    "nct_ids": ["NCT03047395"],
    "is_combo": false,
    "sources": ["s7"]
  } ]
}
```

### `companies`
```jsonc
{ "name": "AbbVie", "type": "large pharma", "positioning": "…",
  "moa_classes": ["IL-23 inhibitor","TNF inhibitor"], "assets": ["d_risankizumab"],
  "deals": [ { "type": "acquisition", "counterparty": "…", "value": "$X", "year": 2020, "note": "…", "sources": [] } ],
  "sources": [] }
```

### `market`
```jsonc
{
  "summary": "…",
  "current_size": { "value_usd_m": 30000, "value": "$30B", "year": 2023, "geography": "Global", "is_estimate": true, "sources": ["s9"] },
  "forecast":     [ { "year": 2030, "value_usd_m": 47000, "value": "$47B", "is_estimate": true, "sources": ["s9"] } ],
  "cagr_pct": 6.5,
  "drivers": ["biologic adoption","new orals"],
  "top_products_forecast": [ { "product": "Skyrizi", "value_usd_m": 17000, "year": 2027, "sources": [] } ],
  "pricing_access": "…",
  "opportunity": [ { "title": "Oral IL-23 pathway", "rationale": "…", "segment": "moderate-to-severe", "sources": [] } ],
  "sources": []
}
```

### `catalysts` (array)
```jsonc
{ "date": "2026-Q4", "event": "Ph3 topline", "asset": "…", "company": "…",
  "type": "readout", "significance": "…", "sources": [] }   // type: readout | pdufa | approval | patent_expiry | data | other
```

### `evidence`
```jsonc
{
  "summary": "…",
  "landmark_trials": [ { "name": "UltIMMa-1", "nct_id": "NCT02684370", "intervention": "risankizumab",
                         "endpoint": "PASI 90 (wk16)", "result": "75% vs 5% placebo", "sources": [] } ],
  "benchmarks": [ { "metric": "PASI 90 at wk16", "unit": "%",
                    "by": [ { "label": "risankizumab", "value": 75 }, { "label": "adalimumab", "value": 48 } ],
                    "sources": [] } ]
}
```

### `swot` (optional)
```jsonc
{ "strengths": ["…"], "weaknesses": ["…"], "opportunities": ["…"], "threats": ["…"], "sources": [] }
```

## Enumerations

**`meta.scope`**: `indication` · `therapeutic_area`

**phases** (`pipeline.assets[].phase` string → `phase_num`):
| phase | phase_num |
|-------|-----------|
| `preclinical` | 0 |
| `phase1` | 1 |
| `phase1_2` | 1.5 |
| `phase2` | 2 |
| `phase2_3` | 2.5 |
| `phase3` | 3 |
| `filed` | 3.7 |
| `approved` | 4 |
| `discontinued` | -1 |

**modalities** (extend as needed): `small_molecule` · `mAb` · `bispecific` · `ADC` · `peptide` · `protein` · `oligonucleotide` (ASO/siRNA) · `gene_therapy` · `cell_therapy` · `vaccine` · `radiopharmaceutical` · `device` · `other`

**routes**: `PO` · `SC` · `IV` · `IM` · `IT` · `TD` · `IN` · `topical` · `other`

**`moa_landscape[].validation_status`**: `validated` (approved drugs / positive Ph3) · `emerging` (positive early clinical) · `unproven` (preclinical/mechanistic only) · `failed` (negative pivotal / discontinued class)

## Minimal valid example

```json
{
  "schema_version": "1.0",
  "meta": { "disease": "Example disease", "scope": "indication", "generated": "2026-07-23" },
  "sources": []
}
```

Everything beyond `meta` + `sources` is additive. Build the atlas up section by section, validating as you go.
