# Atlas blueprint — what goes in each panel

The [schema](atlas-schema.md) says what shape the data takes; this says **what makes each panel good** — the questions it answers, what to include, and how deep to go. It's distilled from the RA Capital landscape maps (see [`reference-maps/README.md`](../../../reference-maps/README.md)) plus the strategic angles the atlas is meant to cover.

**The altitude rule.** The atlas is a *bird's-eye map*, not a dossier. For every panel, ask: *"what would a smart person need to know here to make a decision, and no more?"* Go deep enough that each angle is genuinely useful; stop before it becomes a literature review. If you're tempted to list 40 preclinical papers, you've dropped too low — that's [dbtips](https://github.com/aganitha/agentic-ai/tree/main/dbtips)' altitude, not the atlas's.

## Table of contents
1. [Overview / big picture](#1-overview--big-picture)
2. [Patient burden & epidemiology](#2-patient-burden--epidemiology)
3. [Disease biology](#3-disease-biology)
4. [Standard of care](#4-standard-of-care)
5. [Mechanism-of-action landscape](#5-mechanism-of-action-landscape--the-core)
6. [Clinical pipeline](#6-clinical-pipeline)
7. [Competitive landscape](#7-competitive-landscape)
8. [Market & opportunity](#8-market--opportunity)
9. [Catalysts & milestones](#9-catalysts--milestones)
10. [Evidence](#10-evidence)
11. [Sources & methods](#11-sources--methods)

---

### 1. Overview / big picture
**Answers:** What is this disease, why does it matter, and what's the state of play in one screen?
**Include:** a crisp definition; 2–4 sentences of pathophysiology; a "state of play" narrative (what's solved, what isn't, where the field is heading); and a **headline-stats banner** — the 4–8 numbers that frame everything: prevalence, market size, # approved drugs, # active pipeline assets, and the single sharpest measure of unmet need (e.g. 5-yr survival, % refractory, mortality).
**Depth:** this is the elevator pitch. If a reader stopped here they should still have an accurate mental model.
**RA Capital echo:** the objective framing at the top of each map ("manage symptoms" vs "modify disease") — lead with the strategic tension.

### 2. Patient burden & epidemiology
**Answers:** Who gets this, how many, how bad is it, and where does treatment fall short today?
**Include:** prevalence & incidence (global + 1–3 key geographies); demographics (age, sex, risk factors); **severity/stage segmentation** with rough population splits (this drives everything downstream — mild vs moderate-to-severe, lines of therapy, biomarker-defined subsets); mortality/morbidity and quality-of-life impact; the **unmet need** stated plainly; and the **patient journey** (onset → diagnosis → treatment → progression), including diagnostic delay where relevant.
**Depth:** segmentation is the payload — a good split of the patient population is worth more than a pile of prevalence decimals.
**RA Capital echo:** the PD progression timeline (prodromal → advanced) mapped to treatment.

### 3. Disease biology
**Answers:** What's the underlying biology, and what does it hand us as drug targets?
**Include:** a short pathophysiology synthesis; the **key pathways** and the **druggable targets** on them (with why each matters and how tractable it is — Open Targets helps here); disease **subtypes/biomarkers** that define patient subsets; and, where the biology supports it, a **mechanistic schematic** in the spirit of IO's cancer-immunity cycle (even a structured node/edge description the renderer can lay out).
**Depth:** enough for a non-specialist to understand why the MoA landscape looks the way it does. This panel is the bridge from biology to the drugs.

### 4. Standard of care
**Answers:** How is this treated *today*, with what, by whom, and at what commercial scale?
**Include:** the **treatment paradigm by line/severity** (what's tried first, then next, and when); the **top marketed products** as a table — brand, generic, company, MoA class, approval year, key indications, and **annual sales** (the commercial reality check); **market share by class**; and the anchoring **guidelines**.
**Depth:** the reader should come away knowing what a patient actually gets and which products dominate.
**RA Capital echo:** the PD "standard of care" block — every marketed product with company, launch year, and sales, plus class-level market share. Sales figures are the honest signal of what matters commercially.

### 5. Mechanism-of-action landscape — *the core*
**Answers:** What are **all** the ways people are trying to treat this, and how proven is each?
**Include:** a **comprehensive breakdown of MoA/target classes** — not just the winners. For each class: the **rationale** (why this target in this disease), the **mechanism**, the **modality**, a **validation status** (`validated` / `emerging` / `unproven` / `failed`), the **trade-offs** (pros/cons — efficacy, safety, dosing, durability), the **key players**, and the **representative drugs** (marketed + pipeline, referenced by id into the pipeline). Capture **combinations** where they define the strategy (huge in IO).
**Depth:** breadth is the point here — this is where the atlas earns its keep. Include emerging and even failed classes (a failed class is a strategic signal). Organize classes by the biology from panel 3.
**RA Capital echo:** the entire spine of both maps — PD organized by drug class with mechanism/tolerability notes; IO organized by immune mechanism with dozens of target classes, each annotated with mechanism and whether the class has proven survival benefit. Reproduce that "every approach, with its mechanism and its status" density.

### 6. Clinical pipeline
**Answers:** What's coming, how far along, in what modality, and from whom?
**Include:** the **asset list** by **phase** (preclinical → filed → approved), filterable by MoA, modality, and company; a **phase × MoA-class matrix** (the at-a-glance "where is the innovation" view); a **modality breakdown**; and the **most advanced / most watched** assets called out.
**Depth:** completeness of the clinical-stage (Ph1+) picture matters; preclinical can be representative rather than exhaustive.
**RA Capital echo:** the dense pipeline rows — company (drug), phase, route, dosing — and the company × class competitive grid.

### 7. Competitive landscape
**Answers:** Who are the players, how are they positioned, and what's the deal activity?
**Include:** the **top companies** and their positioning; a **company × MoA matrix** (who's betting on what); and **deal flow** — licensing, M&A, co-development (counterparty, size, year, rationale). Optionally flag **acquirable assets** (small companies with a single differentiated program) — the classic investor lens.
**Depth:** name the handful of companies that matter and what distinguishes each; deals are the leading indicator of where value is moving.
**RA Capital echo:** the company-vs-class matrix and the "acquirable assets" call-out.

### 8. Market & opportunity
**Answers:** How big is the prize, where is it growing, and where's the whitespace?
**Include:** **current market size** and **forecast** (with year, geography, CAGR, and clearly-labeled estimates); **growth drivers**; **top products and their forecasts**; **pricing/access** dynamics; and the payoff — **opportunity/whitespace**: underserved segments, efficacy/safety/access gaps in current therapy, unmet needs, and **patent cliffs** that open the field. This is where you synthesize burden (panel 2) + SoC gaps (panel 4) + pipeline crowding (panel 6) into "where would a new entrant win?"
**Depth:** a defensible size with its source beats a precise-looking fabricated number. Prefer bottom-up sizing where feasible (eligible patients × treatment rate × price) and say so.
**RA Capital echo:** IO's market panel — total opportunity ($60B), checkpoint market now→future with per-product share — and the gap-analysis framing from the market-insights spec.

### 9. Catalysts & milestones
**Answers:** What should I watch, and when?
**Include:** upcoming **clinical readouts**, **PDUFA/regulatory dates**, **approvals**, and **patent expiries**, on a forward **timeline**, each with why it matters.
**Depth:** the next ~1–3 years of events that would move the landscape.
**RA Capital echo:** the "milestones: RCT dates" quarter-by-quarter readout timelines on both maps.

### 10. Evidence
**Answers:** What's the hard clinical evidence under the claims?
**Include:** **landmark trials** (name, NCT, intervention, endpoint, result) and **efficacy/safety benchmarks** on the endpoints that matter for the area (e.g. ORR/PFS/OS in oncology; PASI/EASI in derm; ACR in rheum), ideally cross-drug so classes can be compared. Note key safety signals (boxed warnings).
**Depth:** the few trials and benchmarks that anchor the field — not a trial registry dump.
**RA Capital echo:** IO's ORR-by-indication table and the Kaplan–Meier survival curves with citations.

### 11. Sources & methods
**Answers:** Where did every fact come from, and how much should I trust it?
**Include:** the full **`sources[]`** list (linked); the **generation date**; the **method/coverage note** (which panels are API-sourced vs web-synthesized); and honest **confidence/limitations**. Include the standard disclaimers (informational only; not medical/investment advice).
**Depth:** complete provenance is non-negotiable — this panel is what makes the atlas trustworthy rather than just plausible.

---

## Cross-cutting

- **Legend.** A shared key for phase codes, modality, and route keeps the density legible (both RA Capital maps devote real estate to this). The renderer supplies sensible defaults.
- **Filter & search.** Pipeline and MoA panels should be filterable (by phase, modality, company, class) and searchable.
- **Honest empty states.** A panel with thin public data says so ("insufficient public data for X") — it never invents filler.
- **Consistency of vocabulary.** Use the schema enums for phase/modality/route so cross-panel filtering and the matrix work. Group MoA classes the same way you describe the biology.
