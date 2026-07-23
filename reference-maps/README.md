# Reference maps — the RA Capital inspiration

Two RA Capital "landscape maps" are included here as the **north-star** for what a disease atlas should feel like: enormous information density on a single canvas, organized so an expert can both take in the whole space at a glance *and* drill into any corner.

| File | Area | Format |
|------|------|--------|
| `RACapital_Parkinsons_Disease_V2.pdf` | Parkinson's disease | Single giant-format poster (May 2017) |
| `RACapital_ImmunoOncology_V3.pdf` | Immuno-oncology | Single giant-format poster (Feb 2017) |

> These are third-party materials included for reference/inspiration only. They carry RA Capital's own confidentiality and disclaimer language; treat them as read-only source material, not something we redistribute or reproduce.

## What we learned from them (the structural analysis)

Both maps are a *single page* that an expert can read like a terrain map. Decomposing them gives the atlas its information model.

### Parkinson's map — organized by **treatment objective → symptom → mechanism**
- **Two overarching objectives:** *Manage symptoms* (dopaminergic replacement, the current reality) vs *Neuroprotection / regeneration* (disease modification, the frontier).
- **Standard of care with commercial reality:** every marketed product with company, launch year, and annual sales; total market ($3.18B in 2014); **market share by drug class** (levodopa 28.5%, DA agonists 35.2%, MAO-B 20.2%, COMT 14.8%…).
- **Symptom-based segmentation:** primary motor symptoms, "off" time, levodopa-induced dyskinesia, and non-motor symptoms (psychosis, orthostatic hypotension, constipation, dementia) — each its own sub-landscape.
- **MoA/class breakdown:** for each class, the *mechanism*, its *efficacy/tolerability trade-off*, and the drugs in it (marketed + pipeline) with clinical-stage codes, route, and dosing.
- **Disease-progression timeline:** −20 to +15 years around diagnosis (prodromal → mild → moderate → advanced) mapped to which treatments are used when.
- **Catalysts:** a quarter-by-quarter timeline of expected clinical readouts ("milestones: RCT dates").
- **Competitive matrix:** companies × drug classes, plus a call-out of "acquirable assets" (the investor lens).

### Immuno-oncology map — organized by **mechanistic pathway (the cancer-immunity cycle)**
- **A mechanistic schematic** (the cancer-immunity cycle) anchors the map; every therapeutic class hangs off a step in that biology.
- **Dozens of MoA/target classes** — checkpoints (PD1/PDL1/CTLA4/LAG3/TIM3/VISTA…), T-cell costimulation (OX40/4-1BB/GITR/CD27), T-cell growth factors (IL-2/7/12/15/10), NK-cell targets, and reversing the suppressive microenvironment (TGFβ, IDO, MDSCs, Tregs, CD47/SIRPα, TLR/STING agonists) — each with mechanism, drugs, routes, phases, indications, and **combinations**.
- **Market sizing:** potential immunotherapy market ($60B); checkpoint-inhibitor market $6.2B (2016) → $25.2B (2020) with per-product share (Opdivo, Keytruda, Yervoy, Tecentriq…).
- **Efficacy benchmarks:** overall response rate by indication and agent; **Kaplan–Meier survival curves** (with citations); tumor **neoantigen burden** by indication as a biomarker/segmentation lens.
- **Catalysts:** readout timeline (2016–2020) by company/drug/indication.
- **A rich legend:** clinical-stage codes, routes of delivery, dosing — the shared vocabulary that keeps the density legible.

### The distilled pattern → the atlas panels
Big picture · Patient burden & epidemiology · Disease biology (mechanistic map) · Standard of care (with commercial reality) · **MoA landscape** (the core) · Clinical pipeline · Competitive landscape · Market & opportunity · Catalysts & milestones · Evidence · Sources.

The full, current spec lives in [`../skills/disease-atlas/references/atlas-blueprint.md`](../skills/disease-atlas/references/atlas-blueprint.md).

## How to re-extract the text

The PDFs are image-heavy single pages. To pull their text for analysis:

```python
import fitz  # PyMuPDF
doc = fitz.open("RACapital_Parkinsons_Disease_V2.pdf")
print("\n".join(page.get_text() for page in doc))
```
