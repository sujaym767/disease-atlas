# Vision

## The one-liner

**For any disease, indication, or therapeutic area, generate — on demand — a highly detailed and accurate *atlas*: an interactive, self-contained web app that maps the entire treatment landscape, from patient burden to standard of care to the full mechanism-of-action and pipeline picture to the market and the open opportunities.**

## The problem

Getting oriented in a therapeutic area is slow and expensive. The knowledge is real but scattered — across ClinicalTrials.gov, drug labels, company pipelines, analyst notes, guidelines, and the literature. Pulling it into one coherent picture takes an analyst days to weeks, and the result is a static slide deck that's stale the moment it ships.

RA Capital's answer was the **landscape map**: a single, enormous, information-dense page where a domain expert can see an entire therapeutic area at once — every marketed drug and its sales, every mechanism of action and where it sits in the biology, the whole pipeline by phase and company, the market size, and the whitespace. Two of those maps sit in [`../reference-maps/`](../reference-maps/) as our north star.

We want that artifact, but **generated automatically, kept current, and interactive** — so anyone can get an expert-grade map of any disease in one request.

## What we're building

A **[Claude Agent Skill](https://code.claude.com/docs/en/skills)** that, given a disease name, orchestrates public data sources and Claude's own reasoning + web search into a validated data model, then renders it as **one self-contained `atlas_<disease>.html`** — a web app you can open by double-click, share as a file, or view as a Claude artifact.

The atlas is a **bird's-eye strategic map**. It optimizes for *breadth with enough depth per angle to be decision-useful* — the opposite of a 60-page dossier. You should be able to:

- grasp the **whole space in 60 seconds** from the overview and the headline numbers, and
- **drill into any angle** — a specific MoA class, a company's pipeline, the market forecast — without leaving the page.

### The information model (panels)

The atlas is a set of interlinked panels. The authoritative, evolving spec is [`../skills/disease-atlas/references/atlas-blueprint.md`](../skills/disease-atlas/references/atlas-blueprint.md); the shape below is the stable skeleton.

1. **Overview / the big picture** — definition, pathophysiology in brief, "state of play" narrative, and a headline-stats banner (prevalence, market size, # pipeline assets, # approved drugs, key unmet need).
2. **Patient burden & epidemiology** — prevalence & incidence (global + key geographies), demographics, severity/stage segmentation, mortality/morbidity, quality-of-life and unmet need, the patient journey and diagnostic odyssey.
3. **Disease biology** — pathophysiology, the key pathways and druggable targets, subtypes and biomarkers, and — where the biology supports it — a mechanistic schematic in the spirit of IO's cancer-immunity cycle.
4. **Standard of care** — the treatment paradigm by line/stage, the top marketed products (brand, generic, company, MoA class, approval year, key indications, annual sales), guideline anchors, and market share by class.
5. **Mechanism-of-action landscape** — *the core panel.* A proper breakdown of **every** therapeutic approach: for each MoA/target class, the rationale and mechanism, its clinical **validation status** (validated / emerging / unproven), representative drugs (marketed and pipeline), the trade-offs, and the key players.
6. **Clinical pipeline** — assets by phase (preclinical → filed → approved), by modality, by MoA, and by company; a filterable table and a phase-by-class matrix; the top companies and their portfolios.
7. **Competitive landscape** — who owns what, a company × MoA matrix, positioning, and deal flow (licensing / M&A / co-development).
8. **Market & opportunity** — current market size and forecast, growth drivers, top products and their forecasts, pricing/access notes, and — the payoff — **whitespace**: underserved segments, unmet needs, and patent cliffs that define where the opportunity is.
9. **Catalysts & milestones** — upcoming clinical readouts, PDUFA/regulatory dates, and patent expiries on a timeline.
10. **Evidence** — landmark trials and efficacy/safety benchmarks that ground the claims.
11. **Sources & methods** — provenance for every non-obvious fact, the generation date, and honest coverage/confidence notes.

Cross-cutting: a shared **legend** (phase codes, modality, route), **search & filter**, honest **empty states**, and **export**.

## Principles

1. **Accuracy is the product.** An atlas that's beautiful and wrong is worse than useless — it launders guesses into confident-looking charts. Every non-obvious fact is traceable to a source; estimates are labeled as estimates with their reasoning. We would rather show a gap than fill it with a plausible fabrication.
2. **Breadth first, then calibrated depth.** This is a map, not a dossier. Each panel goes deep enough to drive a decision and no deeper. When someone needs the 10× deeper cut on targets, omics, and evidence, that's [dbtips](https://github.com/aganitha/agentic-ai/tree/main/dbtips)'s job, not the atlas's.
3. **Standalone and portable.** Public data + Claude's reasoning, no internal infrastructure. The output is one HTML file with no external dependencies at view time. It should work on a laptop with no accounts and no network.
4. **Data separate from presentation.** A validated `atlas.json` is the interface; rendering is a pure function of it. That keeps the same data reusable for other renderers (deck, PDF) later, and keeps the pipeline testable.
5. **Intensive is fine.** Generating a great atlas can take many API calls and a lot of Claude reasoning. That's an acceptable cost for an on-demand, expert-grade map. We optimize the *result*, not the runtime.
6. **Honest about uncertainty.** Public data is uneven across diseases. The atlas states what it knows, what it's estimating, and what it can't see — per panel — rather than pretending to uniform coverage.

## What this is NOT

- **Not dbtips.** dbtips is Aganitha's deep disease-dossier platform — exhaustive literature, omics datasets, target assessment, animal models, evidence graphs, behind a rich backend. The atlas borrows dbtips' *sense of what sources exist* and nothing else. It is intentionally lighter, broader, standalone, and single-artifact.
- **Not investment advice.** Like the RA Capital maps, an atlas is an informational landscape, not a recommendation. The market/opportunity panel frames the space; it does not tell anyone what to buy.
- **Not a live dashboard (yet).** Each atlas is a snapshot with a generation date. Freshness comes from re-generating, not from live data binding.

## Who it's for

BD/strategy and corporate-development teams scoping a therapeutic area; investors building a first-principles landscape; scientists and clinicians orienting outside their subspecialty; and anyone who needs to *get the whole picture of a disease fast* and trust where it came from.

## What "great" looks like

A user names a disease. A few minutes later they open a single HTML file and — whether or not they knew the area — they come away with an accurate mental model of the whole landscape: what the disease does to patients, how it's treated today, every way people are trying to treat it better, who's ahead, how big the prize is, and where the gaps are — with a citation behind every claim they'd want to check. Good enough that a domain expert nods, and a newcomer suddenly has a map.
