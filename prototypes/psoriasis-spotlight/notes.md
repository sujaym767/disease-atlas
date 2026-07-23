# Deep psoriasis spotlight — provenance

- Pipeline backbone: live Open Targets (167 drug candidates for EFO_1001494) + ClinicalTrials.gov (901 trials), pulled 2026-07-23.
- Sales: company FY2025 results (AbbVie, J&J, Novartis, UCB, Amgen, BMS, Arcutis) — all-indication franchise totals; a few approximate (flagged).
- PASI 75/90/100: Armstrong 2020 JAMA Dermatol NMA + pivotal trials (UltIMMa, BE VIVID/RADIANT, VOYAGE, ERASURE/FIXTURE, POETYK); cross-trial unless H2H noted.
- Catalysts/exclusivity: company press releases + DrugPatentWatch (2023 Humira & 2025 Stelara biosimilar cliffs; ICOTYDE approval Mar 2026; oral-TYK2 Ph3 readouts; patent expiries 2028-2033).
- Class safety: Cochrane NMA (Sbidian 2023) + reviews.

Regenerate: `python build_deep.py && python build.py`
