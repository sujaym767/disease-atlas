# `atlas.json` — the build contract

`compile_atlas.py` reads this and authors the interactive atlas. Two layers: the **semantic core**
(the domain data) and the **render sections** (which drive the prototype-grade regions). Every
section is optional — the builder degrades gracefully and the template shows honest empty states.

The semantic core (`meta`, `overview`, `epidemiology`, `biology`, `standard_of_care`,
`moa_landscape`, `pipeline`, `companies`, `market`, `catalysts`, `evidence`, `sources`) follows the
base schema in `../../disease-atlas/references/atlas-schema.md`. Below is what the **builder adds on
top** — the fields and sections that unlock the strategy map, the mechanism schematic, and the
market-research bands. Numbers should be real and cited (`sources[]` ids); label estimates.

## Extended `pipeline.assets[]` fields

The base asset (`id`, `name`, `brand`, `company`, `moa_class`, `target`, `modality`, `phase`,
`route`, `mechanism`, `sources`) plus:

```jsonc
{
  "family_key": "il23",              // which mechanism lane (must match families[].key / moa_landscape[].family_key)
  "sub_class": "IL-23 p19 inhibitor",// sub-class label shown on the card
  "dose": "q12w",                    // maintenance dosing
  "approval_year": 2019,
  "annual_sales_usd_m": 17562,       // most-recent FY franchise sales ($M); powers the donut
  "sales_year": 2025,
  "biosimilar": "biosimilars from 2023 …",  // biosimilar/LOE note if any
  "is_combo": false,
  "efficacy": { "p75": 88, "p90": 75, "p100": 36 },  // response benchmark (e.g. PASI); powers the efficacy + kinetics panels
  "note": "…",
  "nct_ids": ["NCT03047395", "NCT02694523"],  // real ClinicalTrials.gov ids (from fetch_clinical_trials.py); enable resolvable trial deep-links
  "detail": { "openfda": {…}, "chembl": {…}, "pubchem": {…} }  // optional drug-detail enrichment (fetch_drug_detail.py)
}
```
**Deep-links resolve, never guess.** A trial link is canonical `clinicaltrials.gov/study/<NCT>` when an
`nct_id` is present, else a search scoped to the atlas's own disease (`meta.focus`) — so it always
returns results. Give `trials_focus[].nct_id` and `pipeline.assets[].nct_ids` real ids captured from
ClinicalTrials.gov; the builder does the rest. Never hand-type an NCT id you haven't verified.

## `families` — the mechanism colour lanes

```jsonc
[ { "key": "il23", "label": "IL-23 / Th17 axis", "colorVar": "--s1", "order": 1, "anchor": "il23" } ]
```
`colorVar` is a template palette slot (`--s1`…`--s8`, `--sN`); omit it and the compiler assigns one
by `order`. `anchor` is the `biology_graph` node this class acts on (for the schematic wiring).
If `families` is omitted, the compiler derives lanes from `moa_landscape[]`.

## `strategy_map` — the Objective→Asset decision tree (the hero)

A list of objective nodes; each node is `{ t, k, d?, c?, side?, ch | drugs }`:
- `t` title, `k` kind ∈ `obj` | `strat` | `appr` | `mech`, `d` one-line rationale, `c` colorVar
  (on objectives), `side` `left`|`right` (which side of the spine).
- Internal nodes carry `ch` (children); **mechanism leaves carry `drugs`** — a list of asset *names*
  (must match `pipeline.assets[].name`). Every asset should be placed exactly once.

```jsonc
[ { "t":"Clear the skin & control inflammation","k":"obj","c":"--s1","side":"left","d":"…","ch":[
    { "t":"Systemic cytokine-directed biologics","k":"strat","d":"…","ch":[
      { "t":"Block the IL-23 / Th17 axis","k":"appr","d":"…","ch":[
        { "t":"IL-23 p19 inhibitors","k":"mech","d":"…","drugs":["guselkumab","risankizumab"] } ] } ] } ] } ]
```

## `biology_graph` — the mechanism cascade as first-class nodes

```jsonc
{
  "nodes": [ { "id":"dc","kind":"cell","label":"Dendritic cell","description":"…","pos":"dc" },
             { "id":"il23","kind":"cytokine","label":"IL-23","description":"…","pos":"il23" },
             { "id":"tyk2","kind":"intracellular","label":"TYK2","description":"…" } ],
  "edges": [ { "type":"PRODUCES","source":"dc","target":"il23" },
             { "type":"ACTS_ON","source":"il23","target":"th17" } ],
  "signal_path": [ { "from":"il23","to":"il23r","label":"IL-23 binds" } ],  // ordered inset pathway
  "anchors":   { "il23":"il23","il17":"il17","kinase":"tyk2" },             // family_key → node id
  "target_bio":{ "IL23A":"il23","TYK2":"tyk2" }                            // target symbol → node id (path-finding bridge)
}
```
`kind` ∈ `cell` | `cytokine` | `intracellular` | `receptor` | `outcome`. `pos` keys the template's
schematic geometry (nodes with a `pos` are drawn on the mechanism poster; the rest live in the
signal-transduction inset and the network). Edge types: `PRODUCES`, `ACTS_ON`, `SIGNALS_VIA`,
`LEADS_TO`, `FEEDBACK`, `BINDS`, `ACTIVATES`, `INDUCES`, `SUSTAINS`.

## `market_research` — the lower bands (the shape `ingest_report.py` emits)

```jsonc
{
  "forecast": { "years":[2026,2029,2031,2036],
                "segments":[ {"label":"…","short":"Injectable IL-23","key":"il23","colorVar":"--s1","vals":[14,16,18,12],"cagr":"5.2%","note":"…"} ],
                "total": {"vals":[32,40,46.5,53.5],"colorVar":"--ink"}, "note":"…" },
  "scenarios":  [ {"name":"Base","y2031":46.5,"cagr":"7.8%","swing":"…"} ],
  "geo":        [ {"region":"US","eligible":"~1.1M","penetration":"~45%","net_price":"~$38k","market":19.0} ],
  "funnel":     [ {"stage":"US adults with psoriasis","population":"~7.6M","pop_num":7.6,"basis":"…","gap":false} ],
  "opportunity":[ {"gap":"…","severity":"High","coverage":"…","the_gap":"…","population":"~630k US","size":"~$3.7B US …"} ],
  "payers":     [ {"market":"US (Medicare Part D)","coverage":"…","hta":"CMS (IRA)","restriction":"…","net_price":"…"} ],
  "attribution":[ {"brand":"Skyrizi","inn":"risankizumab","company":"AbbVie","attr_val":9.0,"fy_val":17.56,"attr_frac":0.513} ],
  "attribution_total": 23.8,
  "competitive":[ {"company":"AbbVie","position":"Leader …","posture":"…","strength":"…","vulnerability":"…"} ],
  "catalysts_watch":[ {"catalyst":"…","type":"Access","expected":"H2 2026","why":"…"} ],
  "risks":      [ {"risk":"…","category":"Commercial/Access","prob":"M–H","impact":"H","horizon":"2026–2029","trigger":"…"} ],
  "thesis":     [ {"heading":"State of the field","text":"…"} ],
  "loe":        [ {"asset":"…","event":"…","timing":"…","consequence":"…"} ]
}
```

## Other render sections

- **`response_kinetics`**: `{ "metric":"PASI 90", "weeks":[0,4,8,12,16], "note":"…", "series":[ {"label":"IL-17","colorVar":"--s2","pts":[0,45,72,80,83]} ] }` — `metric` is the disease's registrational endpoint (PASI 90 / EASI-75 / ACR20 / …); it titles the kinetics panel.
- **`meta.mechanism_label`** (e.g. `"IL-23 / IL-17 cascade → intracellular signalling"`) captions the mechanism region; **`meta.efficacy_label`** (e.g. `"PASI 90"` / `"EASI-75"`) titles the efficacy panel. The efficacy panel auto-uses `efficacy.p90` if any asset has it, else `efficacy.p75`. These keep the atlas labelled for its own indication rather than psoriasis.
- **`trials_focus`**: `{ "trials":[ {"name","drug","fam","sponsor","phase","status","endpoints":[…],"readout","start","end","inclusion","sites","kols","significance"} ], "note":"…" }`
- **`standard_of_care.lines[]`** carries `{ "tier":1,"label":"Topical therapy","agents":"… · …","note":"…","colorVar":"--s4" }` for the severity table.
- **`sites`**: `[ {"site":"Scalp","prev":"~45–80%","note":"…"} ]` — hard-to-treat sites.
- **`market_share`**: `[ {"cls":"IL-23 p19","trend":"Largest & growing","colorVar":"--s1"} ]`.
- **`deals`**: `[ {"acquirer","counterparty","asset","value","date","category":"M&A|Licensing|Partnership","stage","note"} ]`.
- **`glossary`**: `[ {"term":"PASI","def":"…"} ]`.
- **`safety`**: `{ "il17":"class safety text…" }` keyed by family_key (else read from `moa_landscape[].safety`).
- **`epidemiology`** may carry burden extras: `stats` (`[[value,label,src]]`), `comorbid` (`[[label,val]]`), `dlqi`, `economic`, `drug_survival`, `mortality`, `unmet`, `comorbidities`.

## Reference

`examples/plaque-psoriasis/atlas.json` is the full worked example (57 assets, all sections) and the
builder's regression fixture. `prototypes/psoriasis-spotlight/graph_to_atlas.py` shows the exact
mapping from a compiled graph back to this contract.
