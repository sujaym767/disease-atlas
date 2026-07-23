# Data sources

The atlas is **standalone**: hard facts come from public biomedical APIs; commercial/epidemiological facts that have no clean public API come from **Claude web search**, always cited. No Aganitha-internal services, no credentials required (a couple of optional keys just raise rate limits).

Each source below lists: base endpoint · what it's good for · which atlas panels it feeds · a copy-paste query recipe. The bundled `scripts/fetch_*.py` wrap these; this doc is the map so you can query them directly or extend them.

> Environment: outbound HTTPS may go through a proxy (`HTTPS_PROXY`). `scripts/lib/http.py` respects proxy env vars and **verifies TLS** — never disable verification, never hardcode an API key (see the anti-patterns in `dbtips`; don't copy them).

### Network requirements (important)

The fetchers need outbound HTTPS to the API hosts below. On a locked-down environment (e.g. Claude Code on the web with **Trusted** network access, which only allows package registries + GitHub) these are **blocked with a 403 at the egress proxy** and the fetchers return empty with an `error`. The market/epidemiology path (Claude web search) still works because that traffic is Anthropic-side, not container egress.

To enable the fetchers, set the environment's network access to **Full**, or to **Custom** with these **allowed domains** (keep the default package-manager list too):

```
clinicaltrials.gov
api.fda.gov
api.platform.opentargets.org
www.ebi.ac.uk
eutils.ncbi.nlm.nih.gov
```

**Transport note:** `lib/http.py` uses the system **`curl`** when present, falling back to `urllib`. This matters because ClinicalTrials.gov sits behind Akamai, which fingerprints and **403s the Python TLS client** even with browser-like headers, while accepting curl. curl is near-universal and already reads the proxy CA env vars; if it's absent, the other three APIs still work over urllib but CT.gov will 403.

## Table of contents
- [Source → panel map](#source--panel-map)
- [ClinicalTrials.gov API v2](#1-clinicaltrialsgov-api-v2) — pipeline, trials, sponsors
- [Open Targets Platform GraphQL](#2-open-targets-platform-graphql) — targets, MoA, known drugs
- [openFDA](#3-openfda) — approved drugs, labels, boxed warnings
- [Europe PMC](#4-europe-pmc) — literature, landmark trials
- [NCBI E-utilities](#5-ncbi-e-utilities-optional) — PubMed/gene (optional)
- [Claude web search](#6-claude-web-search--for-market-epi-deals) — market size, forecasts, deals, epi
- [Query hygiene](#query-hygiene)

## Source → panel map

| Panel | Primary source(s) |
|-------|-------------------|
| Overview / big picture | synthesized from all + web search |
| Epidemiology & patient burden | **web search** (GBD/IHME, CDC, WHO, disease foundations), cited |
| Disease biology / targets | **Open Targets** (targets, tractability), web search |
| Standard of care / top products | **openFDA** (labels, approvals), web search (sales), guidelines |
| **MoA landscape** | **Open Targets** knownDrugs (mechanismOfAction, target class, phase) + ClinicalTrials.gov + web search |
| Clinical pipeline | **ClinicalTrials.gov v2** + **Open Targets** knownDrugs |
| Competitive landscape / deals | ClinicalTrials.gov sponsors + **web search** (deals, M&A) |
| Market & opportunity | **web search** (analyst reports, company filings), cited |
| Catalysts & milestones | ClinicalTrials.gov (completion dates) + web search (PDUFA, patents) |
| Evidence / benchmarks | **Europe PMC** + ClinicalTrials.gov results + web search |

---

## 1. ClinicalTrials.gov API v2

- **Base:** `https://clinicaltrials.gov/api/v2/studies`
- **Auth:** none. **Format:** JSON. **Paging:** `pageToken` (returned as `nextPageToken`), `pageSize` ≤ 1000.
- **Good for:** the interventional pipeline — assets, phases, sponsors (→ companies), status, interventions, conditions, start/completion dates (→ catalysts).
- **Feeds:** pipeline, companies, catalysts, evidence.

**Recipe — interventional studies for a condition:**
```
GET https://clinicaltrials.gov/api/v2/studies
    ?query.cond=plaque%20psoriasis
    &filter.advanced=AREA[StudyType]INTERVENTIONAL
    &fields=NCTId,BriefTitle,Phase,OverallStatus,StartDate,PrimaryCompletionDate,
            LeadSponsorName,InterventionName,InterventionType,Condition
    &pageSize=200
```
Useful fields (dot-paths under `studies[].protocolSection`):
`identificationModule.nctId` · `.briefTitle` · `designModule.phases[]` · `statusModule.overallStatus` · `statusModule.primaryCompletionDateStruct.date` · `armsInterventionsModule.interventions[].name/.type` · `sponsorCollaboratorsModule.leadSponsor.name` · `conditionsModule.conditions[]`.

Map `Phase` (`PHASE1`,`PHASE1|PHASE2`,`PHASE2`,`PHASE3`,`NA`) and status to the schema's `phase`/`phase_num`. Aggregate interventions across trials to get the asset list (a drug appearing in a Phase 3 trial ⇒ at least Phase 3).

## 2. Open Targets Platform GraphQL

- **Endpoint:** `POST https://api.platform.opentargets.org/api/v4/graphql`
- **Auth:** none. **Format:** GraphQL/JSON.
- **Good for:** the **MoA landscape** and biology — disease→associated targets (with scores), and `knownDrugs` giving **drug → mechanismOfAction → target → clinical phase → status → trial ids**. This is the backbone for classifying approaches by mechanism.
- **Feeds:** biology, moa_landscape, pipeline (mechanism/target enrichment).

**Step 1 — resolve disease name → EFO id:**
```graphql
query ($q: String!) { search(queryString: $q, entityNames: ["disease"]) { hits { id name entity } } }
```
Take the top disease hit's `id` (e.g. `EFO_0000676` for psoriasis).

**Step 2 — associated targets:**
```graphql
query ($efo: String!) {
  disease(efoId: $efo) {
    name
    associatedTargets(page: {index: 0, size: 50}) {
      rows { score target { id approvedSymbol approvedName } }
    }
  }
}
```

**Step 3 — drugs & clinical candidates (drug × mechanism × stage):**
```graphql
query ($efo: String!) {
  disease(efoId: $efo) {
    drugAndClinicalCandidates {
      count
      rows {
        maxClinicalStage
        drug {
          id name drugType
          mechanismsOfAction { rows { mechanismOfAction actionType targets { approvedSymbol } } }
        }
      }
    }
  }
}
```
> Schema note: Open Targets **removed the old `disease.knownDrugs` field**; the current field is `drugAndClinicalCandidates`, whose rows carry a disease-specific `maxClinicalStage` and a nested `drug` (with `mechanismsOfAction.rows[]`). `drugType` → schema `modality`; `mechanismOfAction` + `targets[].approvedSymbol` → group into `moa_landscape` classes; `maxClinicalStage` (`APPROVAL`/`PHASE_3`/…) → asset phase (see `util.opentargets_stage_to_schema`). Disease resolution returns EFO **and MONDO** ids — take the top disease hit and pass its id straight back in.

## 3. openFDA

- **Base:** `https://api.fda.gov/drug/label.json` and `https://api.fda.gov/drug/drugsfda.json`
- **Auth:** none (rate limit 240/min, 1000/day per IP; optional `OPENFDA_API_KEY` raises it). **Format:** JSON. Query language is Lucene-style via `search=`; `limit` ≤ 100; `count=field` for aggregations.
- **Good for:** approved drugs, indications, **boxed warnings**, dosage forms, routes, sponsors, approval history.
- **Feeds:** standard_of_care, MoA validation, pipeline (approved), evidence (safety).

**Recipe — labels mentioning the disease:**
```
GET https://api.fda.gov/drug/label.json
    ?search=indications_and_usage:"psoriasis"
    &limit=100
```
Pull `openfda.brand_name`, `openfda.generic_name`, `openfda.manufacturer_name`, `openfda.route`, `boxed_warning`, `indications_and_usage`.

**Recipe — approval/sponsor history (Drugs@FDA):**
```
GET https://api.fda.gov/drug/drugsfda.json
    ?search=products.brand_name:"Skyrizi"
    &limit=10
```
`submissions[]` → first approval date; `sponsor_name`; `products[].marketing_status`.

## 4. Europe PMC

- **Base:** `https://www.ebi.ac.uk/europepmc/webservices/rest/search`
- **Auth:** none. **Format:** `format=json`. Easier than raw E-utilities and includes abstracts + citation counts.
- **Good for:** landmark trials, pivotal publications, reviews (for background/biology), KOL-adjacent author signals.
- **Feeds:** evidence, biology, overview.

**Recipe:**
```
GET https://www.ebi.ac.uk/europepmc/webservices/rest/search
    ?query=psoriasis%20AND%20(phase%203%20OR%20pivotal)%20AND%20SRC:MED
    &format=json&pageSize=25&sort=CITED%20desc
```
Fields: `id`, `pmid`, `title`, `authorString`, `journalTitle`, `pubYear`, `citedByCount`, `doi`. Link `https://europepmc.org/article/MED/{pmid}`.

## 5. NCBI E-utilities (optional)

- **Base:** `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/` (`esearch.fcgi`, `esummary.fcgi`, `efetch.fcgi`)
- **Auth:** optional `NCBI_API_KEY` env (raises 3→10 req/s). **Never hardcode a key.**
- **Good for:** PubMed searches and gene lookups when Europe PMC isn't enough. Prefer Europe PMC for most literature needs (simpler JSON).

## 6. Claude web search — for market, epi, deals

Some of the most important atlas facts have **no clean public API**: market size and forecasts, product sales, deal flow, and fine-grained epidemiology. Use Claude's **web search** for these, and **cite every one** with a real URL in `sources[]`.

Guidance for trustworthy web-sourced facts:
- **Prefer primary sources.** Product sales → the company's 10-K / annual report / quarterly release. Epidemiology → GBD/IHME, CDC, WHO, or a peer-reviewed prevalence study. Market size/forecast → a named analyst/market-research report (attribute it — "per <firm>, 2024") rather than an SEO listicle.
- **Triangulate.** If two reputable sources disagree on market size, show a range and cite both; don't average silently.
- **Date everything.** Market/epi numbers get a year. Set `is_estimate: true` for forecasts and syntheses.
- **Never fabricate a citation.** If you can't find a source for a number, leave the number out and note the gap in `coverage_note`. A missing figure is fine; a fake one poisons the whole atlas.

Typical searches: `"<disease> global market size 2024 forecast"`, `"<brand> annual sales 2023 10-K"`, `"<disease> prevalence incidence GBD"`, `"<disease> licensing acquisition deal 2024"`, `"<asset> PDUFA date"`, `"<drug> patent expiry loss of exclusivity"`.

## Query hygiene

- **Disease synonyms matter.** Query condition APIs with the common name *and* key synonyms (e.g. "NSCLC" and "non-small cell lung cancer"); merge results. Open Targets `search` resolves many synonyms to one EFO id — use it to canonicalize.
- **Deduplicate assets by normalized name** (lowercase, strip brand/generic parentheticals) when merging ClinicalTrials.gov + Open Targets. Keep the highest phase seen.
- **Be polite:** page rather than over-fetch, set a descriptive User-Agent (the http helper does), and cache raw responses under `runs/<slug>/raw/` so re-runs don't re-hit APIs.
- **Attribute in `sources[]` as you go** — add the source entry the moment you use a datum, so nothing ends up uncited.
