# Spotlight Atlas — interactive prototype (plaque psoriasis)

A **presentation prototype** exploring where the disease-atlas skill should go: the RA-Capital single-canvas *landscape*, made alive. Click any entity — a drug, a company, an MoA class, a target — and the whole map responds: unrelated things dim, related things highlight, connector wires draw the relationships, and a detail rail shows that entity's profile + everything it connects to (with a little relationship graph).

**Open [`index.html`](index.html)** (self-contained, offline).

## What it demonstrates
- **The landscape (hero):** MoA classes as lanes (columns), development **phase** as the vertical axis, each drug a card. Card colour = the current **lens** (MoA / modality / validation / phase); a sales bar makes the blockbusters pop. This is the RA-Capital density.
- **Spotlight on click** (the whole point):
  - **drug →** its market/sales, developer, MoA, targets, the segment it serves, and its same-MoA **competitors** — with wires to each.
  - **company →** every **MoA it's pursuing** in this indication + its whole portfolio (your example).
  - **MoA class →** its drugs, targets, and the companies playing in it.
  - **target →** every drug that hits it and the classes acting on it.
- **Detail rail** with a radial **ego-graph** (focused node + its neighbourhood, click a neighbour to re-focus), relationship groups, and sources.
- Lens switcher, search, light/dark, keyboard `⎋` to reset.

## How it's built
`atlas.json` (the curated psoriasis atlas) → **`build_graph.py`** → **`graph.json`** (the [graph data model](../../docs/data-model.md): 69 nodes / 138 edges) → injected by **`build.py`** into **`template.html`** → **`index.html`**.

```bash
python build_graph.py && python build.py   # regenerate index.html
```

## Status
Prototype for **ideation**, not the finished renderer. Known rough edges: with 9 MoA lanes the landscape scrolls horizontally on narrow screens; the phase ladder is short here because psoriasis is a mature space (mostly Approved + Phase 3). The **therapeutic-area** view (multiple indications) is a different hero layout — see [`docs/data-model.md`](../../docs/data-model.md) § *Indication atlas vs. therapeutic-area atlas*.
