#!/usr/bin/env python3
"""Enrich the roster with public drug detail: openFDA (label) + ChEMBL (molecule/mechanism).
Writes drug_detail.json keyed by drug slug. PubChem is intentionally omitted (not reachable in
this environment; ChEMBL supplies structure). Standalone, public sources only."""
import json, os, re, subprocess, urllib.parse
HERE=os.path.dirname(os.path.abspath(__file__))
def slug(s): return re.sub(r"-{2,}","-",re.sub(r"[^a-z0-9]+","-",(s or "").lower())).strip("-")
def curl(url):
    try:
        r=subprocess.run(["curl","-s","--max-time","18",url],capture_output=True,text=True,timeout=22)
        t=r.stdout.strip()
        return json.loads(t) if t[:1] in "{[" else None
    except Exception: return None
def clip(v,n):
    if not v: return None
    if isinstance(v,list): v=v[0] if v else None
    if not v: return None
    v=re.sub(r"^\s*\d+(\.\d+)*\s+","",str(v))          # strip leading "12.1 " label numbers
    v=re.sub(r"\s+"," ",v).strip()
    return v[:n]+("…" if len(v)>n else "")
def openfda(name,brand):
    for q in ([f'openfda.brand_name:"{brand}"'] if brand and brand!="—" else [])+[f'openfda.generic_name:"{name}"',f'openfda.substance_name:"{name}"']:
        d=curl("https://api.fda.gov/drug/label.json?search="+urllib.parse.quote(q)+"&limit=1")
        if d and d.get("results"):
            r=d["results"][0]
            return {k:v for k,v in {
                "indication":clip(r.get("indications_and_usage"),260),
                "dosing":clip(r.get("dosage_and_administration"),190),
                "moa":clip(r.get("mechanism_of_action"),280),
                "boxed":clip(r.get("boxed_warning"),200)}.items() if v}
    return None
def chembl(name):
    d=curl("https://www.ebi.ac.uk/chembl/api/data/molecule/search?q="+urllib.parse.quote(name)+"&format=json&limit=1")
    if not d or not d.get("molecules"): return None
    m=d["molecules"][0]; p=m.get("molecule_properties") or {}; s=m.get("molecule_structures") or {}
    out={k:v for k,v in {"chembl_id":m.get("molecule_chembl_id"),"mol_type":m.get("molecule_type"),
        "max_phase":m.get("max_phase"),"mw":p.get("full_mwt"),"formula":p.get("full_molformula"),
        "smiles":s.get("canonical_smiles")}.items() if v}
    if out.get("chembl_id"):
        me=curl("https://www.ebi.ac.uk/chembl/api/data/mechanism.json?molecule_chembl_id="+out["chembl_id"]+"&format=json")
        if me and me.get("mechanisms"):
            mm=me["mechanisms"][0]; out["mech"]=mm.get("mechanism_of_action"); out["action"]=mm.get("action_type")
    return out or None
def pubchem(name):  # optional — only reachable if pubchem.ncbi.nlm.nih.gov is allowlisted
    d=curl("https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/"+urllib.parse.quote(name)+"/property/MolecularFormula,MolecularWeight,IUPACName,CanonicalSMILES/JSON")
    try:
        p=d["PropertyTable"]["Properties"][0]
        return {k:v for k,v in {"cid":p.get("CID"),"formula":p.get("MolecularFormula"),"mw":p.get("MolecularWeight"),"iupac":p.get("IUPACName")}.items() if v}
    except Exception: return None
def main():
    g=json.load(open(os.path.join(HERE,"graph.json"),encoding="utf-8"))
    drugs=[(n["label"],n["attrs"].get("brand")) for n in g["nodes"] if n["type"]=="Drug"]
    out={}; ok_fda=ok_ch=0
    for name,brand in drugs:
        det={}
        fda=openfda(name,brand);
        if fda: det["openfda"]=fda; ok_fda+=1
        ch=chembl(name)
        if ch: det["chembl"]=ch; ok_ch+=1
        pc=pubchem(name)
        if pc: det["pubchem"]=pc
        if det: out[slug(name)]=det
        print(("  fda✓" if fda else "  fda·")+("  chembl✓" if ch else "  chembl·")+("  pc✓" if pc else "  pc·"),name)
    json.dump(out,open(os.path.join(HERE,"drug_detail.json"),"w",encoding="utf-8"),indent=1,ensure_ascii=False)
    print(f"DONE: {len(out)}/{len(drugs)} drugs enriched  (openFDA {ok_fda}, ChEMBL {ok_ch})")
if __name__=="__main__": main()
