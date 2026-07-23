"""Shared, dependency-free utilities: slugs, JSON IO, phase mapping, name normalization."""

from __future__ import annotations

import json
import os
import re
import unicodedata

# ---------------------------------------------------------------------------
# Slugs & names
# ---------------------------------------------------------------------------

def slugify(text: str) -> str:
    """Lowercase, ASCII, hyphenated slug. `Non-Small Cell Lung Cancer` -> `non-small-cell-lung-cancer`."""
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return re.sub(r"-{2,}", "-", text).strip("-") or "atlas"


_DRUG_NOISE = re.compile(r"\b(injection|tablets?|capsules?|oral|solution|for injection)\b", re.I)


def normalize_drug_name(name: str) -> str:
    """Normalize a drug/intervention name for cross-source dedup.

    Strips dosage/parenthetical noise and lowercases so that
    'Skyrizi (risankizumab-rzaa)' and 'risankizumab' can be reconciled by callers.
    """
    if not name:
        return ""
    n = name.lower()
    n = re.sub(r"\([^)]*\)", " ", n)          # drop parentheticals
    n = re.sub(r"[-‐-―]", " ", n)    # unify dashes
    n = _DRUG_NOISE.sub(" ", n)
    n = re.sub(r"[^a-z0-9 ]+", " ", n)
    n = re.sub(r"\s+", " ", n).strip()
    return n


def drug_id(name: str) -> str:
    return "d_" + slugify(normalize_drug_name(name) or name)


# ---------------------------------------------------------------------------
# Clinical-trial phase mapping (see references/atlas-schema.md enums)
# ---------------------------------------------------------------------------

# schema phase string -> numeric rank used for sorting and the phase x class matrix
PHASE_NUM = {
    "preclinical": 0.0,
    "phase1": 1.0,
    "phase1_2": 1.5,
    "phase2": 2.0,
    "phase2_3": 2.5,
    "phase3": 3.0,
    "filed": 3.7,
    "approved": 4.0,
    "discontinued": -1.0,
}

# ClinicalTrials.gov v2 `phases` values -> schema phase string
_CTGOV_PHASE = {
    "EARLY_PHASE1": "phase1",
    "PHASE1": "phase1",
    "PHASE1|PHASE2": "phase1_2",
    "PHASE2": "phase2",
    "PHASE2|PHASE3": "phase2_3",
    "PHASE3": "phase3",
    "PHASE4": "approved",   # phase 4 = post-marketing => already approved
    "NA": "preclinical",
}


def ctgov_phase_to_schema(phases: list[str] | None) -> str:
    if not phases:
        return "preclinical"
    key = "|".join(phases)
    if key in _CTGOV_PHASE:
        return _CTGOV_PHASE[key]
    # fall back to the highest single phase present
    order = ["PHASE4", "PHASE3", "PHASE2", "PHASE1", "EARLY_PHASE1", "NA"]
    for p in order:
        if p in phases:
            return _CTGOV_PHASE.get(p, "preclinical")
    return "preclinical"


def opentargets_phase_to_schema(phase) -> str:
    """Open Targets numeric clinical `phase` (0-4, may be float) -> schema phase string."""
    try:
        p = float(phase)
    except (TypeError, ValueError):
        return "preclinical"
    if p >= 4:
        return "approved"
    if p >= 3:
        return "phase3"
    if p >= 2:
        return "phase2"
    if p >= 1:
        return "phase1"
    return "preclinical"


# Open Targets `maxClinicalStage` enum (drugAndClinicalCandidates) -> schema phase string
_OT_STAGE = {
    "APPROVAL": "approved",
    "PREAPPROVAL": "filed",
    "PHASE_4": "approved",
    "PHASE_3": "phase3",
    "PHASE_2_3": "phase2_3",
    "PHASE_2": "phase2",
    "PHASE_1_2": "phase1_2",
    "PHASE_1": "phase1",
    "EARLY_PHASE_1": "phase1",
    "PRECLINICAL": "preclinical",
    "UNKNOWN": "preclinical",
}


def opentargets_stage_to_schema(stage) -> str:
    return _OT_STAGE.get(str(stage or "").upper(), "preclinical")


def phase_num(phase_str: str) -> float:
    return PHASE_NUM.get(phase_str, 0.0)


def max_phase(a: str, b: str) -> str:
    return a if phase_num(a) >= phase_num(b) else b


# ---------------------------------------------------------------------------
# JSON IO
# ---------------------------------------------------------------------------

def load_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def dump_json(obj, path: str | None = None) -> str:
    text = json.dumps(obj, indent=2, ensure_ascii=False)
    if path:
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
    return text


def emit(obj, out: str | None):
    """Write JSON to `out` (and report) or print to stdout — the common fetcher tail."""
    if out:
        dump_json(obj, out)
        n = obj.get("count") if isinstance(obj, dict) else None
        print(f"wrote {out}" + (f" ({n} records)" if n is not None else ""))
    else:
        print(dump_json(obj))
