#!/usr/bin/env python3
"""Author a focused-but-genuine atopic-dermatitis atlas.json to prove the two-skill pipeline
on a second indication. Structural data (assets / mechanisms / companies / phases) is grounded in
the live Open Targets + ClinicalTrials.gov pulls; market figures are well-established public anchors
or labeled [Estimated]. This is the shape the disease-atlas research skill produces."""
import json, os

def slug(s):
    import re; return re.sub(r"[^a-z0-9]+","-",s.lower()).strip("-")

# ---- families (mechanism lanes) ----
families=[
 {"key":"il4_13","label":"IL-4 / IL-13 (type-2 core)","order":1,"anchor":"il13"},
 {"key":"il13","label":"IL-13 selective","order":2,"anchor":"il13"},
 {"key":"il31","label":"IL-31 (itch axis)","order":3,"anchor":"il31"},
 {"key":"jak","label":"Oral JAK inhibitors","order":4,"anchor":"jak1"},
 {"key":"topical_jak","label":"Topical JAK / PDE4","order":5,"anchor":"kera"},
 {"key":"tslp_ox40","label":"TSLP / OX40 (upstream)","order":6,"anchor":"tslp"},
 {"key":"topical_ns","label":"Topical non-steroidal","order":7,"anchor":"kera"},
 {"key":"conv","label":"Calcineurin / conventional","order":8,"anchor":"th2"},
]
# ---- roster (name, brand, company, family, sub, target, modality, phase, route, dose, appr, sales, syr, p75(EASI-75), note) ----
def D(n,b,co,f,sub,t,mod,ph,rt,dose,appr=None,sales=None,syr=None,e75=None,note=None):
    r=dict(name=n,brand=b,company=co,family_key=f,sub_class=sub,target=t,modality=mod,phase=ph,route=rt,dose=dose)
    if appr:r["approval_year"]=appr
    if sales is not None:r["annual_sales_usd_m"]=sales;r["sales_year"]=syr
    if e75 is not None:r["efficacy"]={"p75":e75}
    if note:r["note"]=note
    return r
ROSTER=[
 D("dupilumab","Dupixent","Sanofi / Regeneron","il4_13","IL-4Rα antagonist (blocks IL-4 & IL-13)","IL4R","mAb","approved","SC","q2w",2017,14150,2024,e75=51,note="FY2024 Dupixent global net sales ~$14.15B (all indications); the category anchor"),
 D("tralokinumab","Adbry / Adtralza","LEO Pharma","il13","IL-13 ligand inhibitor","IL13","mAb","approved","SC","q2w",2021,e75=33,note="first selective IL-13 mAb in AD"),
 D("lebrikizumab","Ebglyss","Eli Lilly / Almirall","il13","IL-13 ligand inhibitor (high affinity)","IL13","mAb","approved","SC","q4w",2024,e75=43,note="approved US Sep 2024; q4w maintenance"),
 D("cendakimab","—","Amgen","il13","IL-13 inhibitor","IL13","mAb","phase2","SC","q2w",e75=None,note="also in eosinophilic esophagitis"),
 D("nemolizumab","Nemluvio","Galderma","il31","IL-31RA antagonist (itch)","IL31RA","mAb","approved","SC","q4w",2024,note="targets pruritus / prurigo nodularis; approved AD 2024"),
 D("abrocitinib","Cibinqo","Pfizer","jak","Oral JAK1 inhibitor","JAK1","small_molecule","approved","PO","QD",2022,e75=63,note="JAK1-selective; boxed warning (JAK class)"),
 D("upadacitinib","Rinvoq","AbbVie","jak","Oral JAK1 inhibitor","JAK1","small_molecule","approved","PO","QD",2022,e75=70,note="highest EASI-75 among orals; boxed warning (JAK class)"),
 D("baricitinib","Olumiant","Eli Lilly","jak","Oral JAK1/2 inhibitor","JAK1","small_molecule","approved","PO","QD",2020,e75=45,note="approved AD in EU/Japan; not US for AD; boxed warning"),
 D("delgocitinib","Anzupgo","LEO Pharma","topical_jak","Topical pan-JAK inhibitor","JAK1","small_molecule","approved","topical","BID",2024,note="approved chronic hand eczema (EU 2024)"),
 D("ruxolitinib","Opzelura","Incyte","topical_jak","Topical JAK1/2 inhibitor","JAK1","small_molecule","approved","topical","BID",2021,note="first topical JAK for AD (US 2021)"),
 D("crisaborole","Eucrisa","Pfizer","topical_jak","Topical PDE4 inhibitor","PDE4","small_molecule","approved","topical","BID",2016,note="non-steroidal topical PDE4"),
 D("roflumilast","Zoryve","Arcutis","topical_ns","Topical PDE4 inhibitor","PDE4","small_molecule","approved","topical","QD",2024,note="cream 0.15% approved AD (US 2024)"),
 D("tapinarof","Vtama","Organon","topical_ns","Topical AhR agonist","AHR","small_molecule","approved","topical","QD",2024,note="approved AD ≥2y (US Dec 2024)"),
 D("tacrolimus","Protopic","LEO / generic","conv","Topical calcineurin inhibitor","FKBP1A","small_molecule","approved","topical","BID",2000,note="steroid-sparing; boxed warning (theoretical malignancy)"),
 D("pimecrolimus","Elidel","Bausch Health","conv","Topical calcineurin inhibitor","FKBP1A","small_molecule","approved","topical","BID",2001),
 D("amlitelimab","—","Sanofi","tslp_ox40","Anti-OX40L mAb","TNFSF4","mAb","phase3","SC","q4w",e75=None,note="non-depleting OX40L; Ph2 STREAM-AD positive; Ph3 ongoing"),
 D("rocatinlimab","—","Amgen / Kyowa Kirin","tslp_ox40","Anti-OX40 mAb (T-cell depleting)","TNFRSF4","mAb","phase3","SC","q4w",note="Ph3 ROCKET programme"),
 D("tezepelumab","Tezspire","Amgen / AstraZeneca","tslp_ox40","Anti-TSLP mAb","TSLP","mAb","phase2","SC","q4w",note="approved asthma; Ph2 AD mixed"),
]

# ---- MoA landscape (one class per family, with safety) ----
SAFETY={"jak":"JAK-class boxed warning: serious infection, MACE, thrombosis, malignancy, mortality — orals are second-line after biologics in many labels.",
 "il4_13":"Conjunctivitis / ocular surface disease; injection-site reactions; generally clean systemic profile — no boxed warning.",
 "il13":"Conjunctivitis (lower than IL-4Rα for some); injection-site reactions.",
 "il31":"Well tolerated; targets itch; peripheral effects under study.",
 "topical_jak":"Local; ruxolitinib carries the JAK class boxed warning by label despite topical use.",
 "tslp_ox40":"Emerging class; pyrexia/chills seen with OX40 agents; long dosing intervals a potential differentiator.",
 "topical_ns":"Local, steroid-sparing, well tolerated for chronic/sensitive-site use.",
 "conv":"Calcineurin inhibitors carry a (theoretical) boxed malignancy warning; burning on application."}

moa_landscape=[{"class":f["label"],"family_key":f["key"],"order":f["order"],"anchor":f["anchor"],
  "safety":SAFETY.get(f["key"]),"drugs":["d_"+slug(d["name"]) for d in ROSTER if d["family_key"]==f["key"]]} for f in families]

# ---- biology_graph: the type-2 (Th2) axis of AD ----
biology_graph={
 "nodes":[
  {"id":"tslp","kind":"cytokine","label":"TSLP / IL-33 / IL-25","description":"Epithelial alarmins released by a damaged skin barrier; they activate dendritic cells and ILC2s to initiate the type-2 response — the upstream trigger of AD.","pos":"dc"},
  {"id":"ilc2","kind":"cell","label":"ILC2 / Th2 cell","description":"Type-2 innate lymphoid and T-helper cells that, once activated by alarmins and OX40 co-stimulation, secrete the effector cytokines IL-4, IL-13 and IL-31.","pos":"th17"},
  {"id":"il4","kind":"cytokine","label":"IL-4","description":"Type-2 cytokine driving Th2 differentiation and IgE class-switch; signals via IL-4Rα — the target of dupilumab.","pos":"il23"},
  {"id":"il13","kind":"cytokine","label":"IL-13","description":"The dominant effector cytokine in lesional AD skin; drives keratinocyte dysfunction, barrier defects and inflammation. Blocked by tralokinumab/lebrikizumab and (with IL-4) by dupilumab.","pos":"il17"},
  {"id":"il31","kind":"cytokine","label":"IL-31","description":"The 'itch cytokine' — acts on sensory neurons via IL-31RA to drive pruritus, the defining symptom of AD. Blocked by nemolizumab.","pos":"il22"},
  {"id":"kera","kind":"cell","label":"Keratinocyte / skin barrier","description":"Under type-2 cytokines the keratinocyte downregulates filaggrin and barrier proteins, letting allergens/microbes in and amplifying inflammation — the self-perpetuating barrier–immune loop.","pos":"kera"},
  {"id":"lesion","kind":"outcome","label":"Eczematous lesion + itch","description":"The clinical outcome: itchy, inflamed, barrier-defective eczematous skin.","pos":"plaque"},
  {"id":"il4r","kind":"receptor","label":"IL-4Rα","description":"Shared receptor subunit for IL-4 and IL-13 signalling; blocking it (dupilumab) neutralizes both cytokines."},
  {"id":"jak1","kind":"intracellular","label":"JAK1","description":"Janus kinase transducing IL-4/IL-13/IL-31 receptor signalling to STAT6/STAT3; oral JAK1 inhibitors block the whole type-2 signalling node intracellularly."},
  {"id":"stat6","kind":"intracellular","label":"STAT6","description":"Transcription factor activated by JAK1 downstream of IL-4Rα; drives the type-2 gene programme."},
  {"id":"ox40","kind":"receptor","label":"OX40 / OX40L","description":"Co-stimulatory axis sustaining pathogenic memory T cells; targeted by rocatinlimab (OX40) and amlitelimab (OX40L) for potential durable, low-frequency dosing."},
 ],
 "edges":[
  {"type":"PRODUCES","source":"tslp","target":"ilc2"},{"type":"ACTS_ON","source":"ox40","target":"ilc2"},
  {"type":"PRODUCES","source":"ilc2","target":"il4"},{"type":"PRODUCES","source":"ilc2","target":"il13"},{"type":"PRODUCES","source":"ilc2","target":"il31"},
  {"type":"BINDS","source":"il4","target":"il4r"},{"type":"BINDS","source":"il13","target":"il4r"},
  {"type":"SIGNALS_VIA","source":"il4r","target":"jak1"},{"type":"ACTIVATES","source":"jak1","target":"stat6"},{"type":"SUSTAINS","source":"stat6","target":"ilc2"},
  {"type":"ACTS_ON","source":"il13","target":"kera"},{"type":"ACTS_ON","source":"il31","target":"lesion"},
  {"type":"LEADS_TO","source":"kera","target":"lesion"},{"type":"FEEDBACK","source":"kera","target":"tslp"},
 ],
 "signal_path":[{"from":"il4","to":"il4r","label":"IL-4/13 bind"},{"from":"il4r","to":"jak1","label":"receptor-associated"},
  {"from":"jak1","to":"stat6","label":"phosphorylate"},{"from":"stat6","to":"ilc2","label":"type-2 programme"}],
 "anchors":{"il4_13":"il13","il13":"il13","il31":"il31","jak":"jak1","topical_jak":"kera","tslp_ox40":"tslp","topical_ns":"kera","conv":"ilc2"},
 "target_bio":{"IL4R":"il4r","IL13":"il13","IL31RA":"il31","JAK1":"jak1","TSLP":"tslp","TNFSF4":"ox40","TNFRSF4":"ox40"},
}

# ---- strategy map ----
def L(t,drugs,d=None):
    r={"t":t,"k":"mech","drugs":drugs};
    if d:r["d"]=d
    return r
strategy_map=[
 {"t":"Control type-2 inflammation","k":"obj","c":"--s1","side":"left","d":"AD is driven by the IL-4/IL-13 type-2 axis; the dominant goal is durable suppression of that inflammation.","ch":[
   {"t":"Injectable type-2 cytokine blockade","k":"strat","d":"Biologics neutralising the core effector cytokines — the durable, best-tolerated backbone.","ch":[
     {"t":"Block IL-4 & IL-13 together","k":"appr","d":"Neutralise both type-2 effectors at the shared receptor.","ch":[
       L("IL-4Rα antagonists",["d_dupilumab"],"Blocks IL-4 and IL-13 signalling; the category anchor.")]},
     {"t":"Block IL-13 selectively","k":"appr","d":"Neutralise the dominant lesional cytokine.","ch":[
       L("IL-13 ligand inhibitors",["d_tralokinumab","d_lebrikizumab","d_cendakimab"],"Selective IL-13 mAbs; q4w maintenance a convenience edge.")]}]},
   {"t":"Oral small-molecule signalling blockade","k":"strat","d":"Intracellular JAK inhibition — fast, oral, deep, but second-line on class safety.","ch":[
     {"t":"Inhibit JAK1 signalling","k":"appr","d":"Block the intracellular node transducing IL-4/13/31.","ch":[
       L("Oral JAK1 inhibitors",["d_upadacitinib","d_abrocitinib","d_baricitinib"],"Highest short-term EASI-75; JAK-class boxed warning.")]}]}]},
 {"t":"Relieve the itch","k":"obj","c":"--s2","side":"right","d":"Pruritus is the defining, quality-of-life-dominating symptom; dedicated itch mechanisms are a distinct battleground.","ch":[
   {"t":"Target the itch cytokine","k":"strat","d":"Neuroimmune IL-31 signalling drives pruritus directly.","ch":[
     L("IL-31RA antagonists",["d_nemolizumab"],"Rapid antipruritic effect via the IL-31 receptor.")]},
   {"t":"Topical anti-inflammatory control","k":"strat","d":"Localised, steroid-sparing control for mild-moderate and maintenance.","ch":[
     L("Topical JAK inhibitors",["d_ruxolitinib","d_delgocitinib"],"Rapid local control; ruxolitinib carries a class boxed warning."),
     L("Topical non-steroidal (PDE4 / AhR)",["d_crisaborole","d_roflumilast","d_tapinarof"],"Non-steroidal agents extending to sensitive sites and children."),
     L("Topical calcineurin inhibitors",["d_tacrolimus","d_pimecrolimus"],"Established steroid-sparing maintenance.")]}]},
 {"t":"Intercept upstream & pursue durable remission","k":"obj","c":"--s7","side":"right","d":"Target the alarmin/OX40 apex for disease modification and low-frequency, potentially remission-inducing therapy.","ch":[
   {"t":"Upstream alarmin & co-stimulation blockade","k":"strat","d":"Hit the initiating signals rather than single effectors.","ch":[
     L("OX40 / OX40L antagonists",["d_amlitelimab","d_rocatinlimab"],"Non-depleting or depleting T-cell co-stimulation blockade; infrequent dosing bet."),
     L("Anti-TSLP",["d_tezepelumab"],"Alarmin blockade; AD signal weaker than in asthma.")]}]},
]

# ---- SoC, epi, market, evidence, market_research ----
soc={"lines":[
 {"tier":1,"label":"Emollients & barrier care","agents":"Moisturisers · gentle skin care","note":"Foundation of all AD care; barrier repair reduces flares.","colorVar":"--s4"},
 {"tier":2,"label":"Topical anti-inflammatories","agents":"TCS · calcineurin inhibitors · crisaborole · ruxolitinib · roflumilast · tapinarof","note":"First pharmacologic line for mild-moderate; non-steroidals extend to face/folds.","colorVar":"--s6"},
 {"tier":3,"label":"Phototherapy","agents":"NB-UVB","note":"Moderate disease or topical-refractory; access-limited.","colorVar":"--s8"},
 {"tier":4,"label":"Systemic biologics","agents":"Dupilumab · tralokinumab · lebrikizumab · nemolizumab","note":"Moderate-to-severe; durable, best-tolerated systemic backbone.","colorVar":"--s1"},
 {"tier":5,"label":"Oral JAK inhibitors","agents":"Upadacitinib · abrocitinib · baricitinib","note":"Moderate-to-severe; fast and deep but second-line on class safety.","colorVar":"--s3"}],
 "note":"Care escalates from barrier repair → topicals → phototherapy → biologics / oral JAKs. Basis: AAD & EADV guidelines."}

epi={"headline":"~223M globally · ~10% of children, ~7% of US adults","stats":[
 ("~223M","Global prevalence (GBD 2019)","gbd"),("~7%","US adults","aad"),("~13%","US children","aad"),
 ("~40%","Moderate-to-severe share","est"),("~1 in 4","Adults with inadequate control","est"),("#1","Skin disorder by disability (GBD)","gbd")],
 "comorbidities":"Type-2 comorbidities — asthma, allergic rhinitis, food allergy, eosinophilic esophagitis (the 'atopic march'); plus sleep disruption, anxiety/depression.",
 "unmet":"Pruritus control, durable remission, paediatric options, and steroid-phobia-driven under-treatment remain key gaps despite a crowded biologic/JAK field.",
 "dlqi":"AD carries one of the highest quality-of-life burdens in dermatology — itch and sleep loss dominate; POEM/DLQI improvements are core endpoints.",
 "drug_survival":"IL-4Rα/IL-13 biologics show high real-world persistence; oral JAKs face safety-driven discontinuation.",
 "comorbid":[("Asthma","~25–40%"),("Allergic rhinitis","~40–60%"),("Food allergy","~15–30%"),("Anxiety / depression","elevated"),("Sleep disturbance","common")],
 "mortality":"Not directly fatal; burden is chronic morbidity, itch and quality-of-life loss."}

sites=[("Face & eyelids","common","Sensitive-site tolerability drives non-steroidal choice; ocular surface disease with IL-4Rα."),
 ("Hands","~in a subset","Chronic hand eczema is a distinct, disabling phenotype (delgocitinib approved EU)."),
 ("Flexures","hallmark","Classic distribution; chronic lichenification with scratching."),
 ("Paediatric","~13% of children","Large label-expansion battleground; dupilumab down to 6 months.")]

market_share=[("IL-4Rα (dupilumab)","Dominant & growing","--s1"),("IL-13 selective","Growing challengers","--s2"),
 ("Oral JAK","Fast but safety-capped","--s3"),("Topical non-steroidal","Expanding","--s4"),("IL-31 / OX40 emerging","Nascent","--s7")]

response_kinetics={"metric":"EASI-75","weeks":[0,4,8,12,16],"note":"Class-representative EASI-75 trajectories (label/NMA-informed; illustrative). Oral JAKs act fastest; IL-4/13 biologics climb steadily to durable control.",
 "series":[{"label":"Oral JAK1 (upa/abro)","colorVar":"--s3","pts":[0,44,60,68,70]},
  {"label":"IL-4Rα (dupilumab)","colorVar":"--s1","pts":[0,18,37,48,60]},
  {"label":"IL-13 (lebri/tralo)","colorVar":"--s2","pts":[0,15,30,40,50]},
  {"label":"Topical non-steroidal","colorVar":"--s4","pts":[0,20,30,35,38]}]}

catalysts=[
 {"date":"2024-09","event":"Lebrikizumab (Ebglyss) FDA approval","kind":"approval","company":"Eli Lilly","asset":"lebrikizumab","significance":"Second selective IL-13 biologic; q4w maintenance differentiator."},
 {"date":"2024-12","event":"Tapinarof (Vtama) approved for AD","kind":"approval","company":"Organon","asset":"tapinarof","significance":"Non-steroidal topical AhR agonist extends into AD ≥2y."},
 {"date":"2025","event":"Amlitelimab & rocatinlimab Phase 3 readouts (OX40/OX40L)","kind":"readout","company":"Sanofi / Amgen","asset":"amlitelimab","significance":"First test of upstream co-stimulation blockade for durable, infrequent dosing."},
 {"date":"2025","event":"Dupixent paediatric & indication expansion continues","kind":"approval","company":"Sanofi / Regeneron","asset":"dupilumab","significance":"Franchise defence via new indications (COPD, others) and younger AD ages."}]

deals=[
 ("Sanofi","Kymab","amlitelimab","$1.45B","2021-04","M&A","Clinical","Sanofi acquired Kymab for the anti-OX40L mAb amlitelimab (KY1005)."),
 ("Amgen","Kyowa Kirin","rocatinlimab","co-development","2021-06","Partnership","Clinical","Amgen/Kyowa Kirin co-develop the anti-OX40 mAb rocatinlimab (KHK4083)."),
 ("Eli Lilly","Dermira","lebrikizumab","$1.1B","2020-01","M&A","Clinical","Lilly acquired Dermira, gaining lebrikizumab (ex-US to Almirall).")]

market_research={
 "forecast":{"years":[2024,2027,2030,2034],
  "segments":[
   {"label":"IL-4Rα / IL-13 biologics","short":"Type-2 biologics","key":"il4_13","vals":[15.0,20.0,24.0,27.0],"cagr":"9.9%","note":"Dupixent-led; IL-13 challengers add volume. [Estimated]"},
   {"label":"Oral JAK inhibitors","short":"Oral JAK","key":"jak","vals":[2.0,3.5,4.5,5.0],"cagr":"22.5%","note":"Fast growth capped by class-safety positioning. [Estimated]"},
   {"label":"Topical Rx (JAK/PDE4/AhR/CNI)","short":"Topical Rx","key":"topical_ns","vals":[2.0,3.0,4.0,5.0],"cagr":"22.5%","note":"Non-steroidal topicals take share from generic steroids. [Estimated]"},
   {"label":"IL-31 / OX40 & emerging","short":"Itch / upstream","key":"tslp_ox40","vals":[0.5,1.5,3.5,6.0],"cagr":"63%","note":"Nemolizumab + OX40 class if Ph3 delivers. [Estimated]"}],
  "total":{"vals":[19.5,28.0,36.0,43.0],"colorVar":"--ink"},
  "note":"[Estimated] bottom-up from indication-attributed biologic revenue (Dupixent ~$14B FY2024 across indications, AD the majority) + emerging classes; cross-checked against published $15–20B (2024) AD envelopes."},
 "scenarios":[
  {"name":"Base","y2031":38.0,"cagr":"~10%","swing":"IL-13 and topical non-steroidals expand the treated pool; OX40 class delivers a durable-dosing option; JAK stays second-line."},
  {"name":"Conservative","y2031":31.0,"cagr":"~7%","swing":"OX40 Ph3 disappoints; biosimilar/pricing pressure on the biologic backbone; JAK safety caps orals."},
  {"name":"Aggressive","y2031":45.0,"cagr":"~13%","swing":"Upstream/remission-inducing therapy reframes the category; strong paediatric expansion; net price defended on durability."}],
 "funnel":[
  {"stage":"US adults + children with AD","population":"~31M","pop_num":31.0,"basis":"~7% adults + ~13% children (AAD)","gap":False},
  {"stage":"Moderate-to-severe","population":"~7M","pop_num":7.0,"basis":"~40% of diagnosed [Estimated]","gap":False},
  {"stage":"Diagnosed & treated by a specialist","population":"~3.5M","pop_num":3.5,"basis":"[Estimated]","gap":False},
  {"stage":"On advanced therapy (biologic/JAK)","population":"~1.2M","pop_num":1.2,"basis":"[Estimated]","gap":False},
  {"stage":"Moderate-to-severe, not on advanced therapy","population":"~2.3M","pop_num":2.3,"basis":"Residual","gap":True,"note":"The core opportunity — steroid-phobia, access and under-referral, not efficacy."}],
 "competitive":[
  {"company":"Sanofi / Regeneron","position":"Dominant leader — Dupixent ~$14B franchise","posture":"Defend and expand the type-2 backbone across indications + amlitelimab optionality","strength":"Scale, prescriber entrenchment, cleanest biologic profile, paediatric breadth","vulnerability":"Single-asset concentration; oral and IL-13 substitution at the margins"},
  {"company":"Eli Lilly","position":"IL-13 challenger — Ebglyss (lebrikizumab)","posture":"Win on q4w convenience + IL-13 selectivity","strength":"Commercial muscle; immunology depth","vulnerability":"Second into IL-13 behind tralokinumab; behind Dupixent on breadth"},
  {"company":"AbbVie","position":"Oral JAK leader — Rinvoq (upadacitinib)","posture":"Own the fast, deep oral segment","strength":"Highest EASI-75; cross-indication scale","vulnerability":"JAK-class boxed warning caps first-line use"},
  {"company":"LEO Pharma","position":"IL-13 + topical JAK (tralokinumab, delgocitinib)","posture":"Dermatology-focused breadth incl. hand eczema","strength":"Derm specialism; first topical pan-JAK","vulnerability":"Smaller commercial scale vs pharma majors"},
  {"company":"Amgen","position":"Emerging OX40 + IL-13 (rocatinlimab, cendakimab)","posture":"Bet on upstream durability","strength":"Biologics scale; broad I&I pipeline","vulnerability":"Late to the effector classes; OX40 efficacy/tolerability unproven"},
  {"company":"Galderma","position":"Itch specialist — Nemluvio (nemolizumab)","posture":"Own the pruritus / prurigo niche","strength":"First-in-class IL-31 mechanism","vulnerability":"Narrower efficacy on inflammation vs IL-4/13"}],
 "thesis":[{"heading":"State of the field","text":"Atopic dermatitis has become the second great type-2 immunology market after asthma: a dominant IL-4Rα biologic (Dupixent) anchors a rapidly crowding field of selective IL-13 antibodies, oral JAK inhibitors, non-steroidal topicals and a new IL-31 itch mechanism, with upstream OX40/alarmin bets aiming at durable remission. The competitive question is shifting from 'can we clear the skin' to 'convenience, itch, safety and durability at what net price'."}]}

# ---- sources ----
sources=[
 {"id":"ot","type":"api","name":"Open Targets Platform","title":"Atopic dermatitis — targets & drug candidates (live pull)","url":"https://platform.opentargets.org/","accessed":"2026-07-23"},
 {"id":"ctgov","type":"api","name":"ClinicalTrials.gov","title":"Atopic dermatitis interventional trials (1427, live pull)","url":"https://clinicaltrials.gov/","accessed":"2026-07-23"},
 {"id":"fda","type":"label","name":"openFDA / Drugs@FDA","title":"Approved AD products, labels & boxed warnings","url":"https://www.accessdata.fda.gov/scripts/cder/daf/","accessed":"2026-07-23"},
 {"id":"gbd","type":"publication","name":"GBD 2019","title":"Global burden of atopic dermatitis","url":"https://www.thelancet.com/gbd","accessed":"2026-07-23"},
 {"id":"aad","type":"guideline","name":"AAD / EADV","title":"Atopic dermatitis prevalence & guidelines of care","url":"https://www.aad.org/","accessed":"2026-07-23"},
 {"id":"sanofi24","type":"filing","name":"Sanofi FY2024 results","title":"Dupixent net sales ~$14.15B (2024, all indications)","url":"https://www.sanofi.com/en/investors","accessed":"2026-07-23"},
 {"id":"est","type":"estimate","name":"Atlas model estimate","title":"Bottom-up AD market build & segment split (labeled [Estimated])","accessed":"2026-07-23"}]

glossary=[("EASI","Eczema Area and Severity Index — the primary AD efficacy score; EASI-75/90 = ≥75/90% improvement."),
 ("IGA","Investigator Global Assessment (0–4); IGA 0/1 = clear/almost-clear, a co-primary endpoint."),
 ("POEM","Patient-Oriented Eczema Measure — patient-reported symptom burden."),
 ("Type-2 inflammation","The IL-4/IL-13/IL-5 immune programme underlying AD, asthma and other atopic diseases."),
 ("IL-4Rα","Shared receptor subunit for IL-4 and IL-13; blocking it (dupilumab) neutralises both."),
 ("IL-13","The dominant effector cytokine in lesional AD skin."),
 ("IL-31","The 'itch cytokine' acting on sensory neurons; target of nemolizumab."),
 ("JAK1","Kinase transducing type-2 receptor signalling; oral JAK1 inhibitors block it intracellularly."),
 ("TSLP","Epithelial alarmin that initiates type-2 responses from a damaged barrier."),
 ("OX40 / OX40L","T-cell co-stimulatory axis targeted for durable, low-frequency therapy."),
 ("Atopic march","Progression from AD in infancy to food allergy, asthma and allergic rhinitis."),
 ("Filaggrin","Barrier protein; loss-of-function is a key genetic risk factor for AD.")]

# strategy_map leaves carry asset NAMES (the template matches by name); normalize any id→name
_id2name={"d_"+slug(d["name"]):d["name"] for d in ROSTER}
def _norm(node):
    if isinstance(node,dict):
        if "drugs" in node: node["drugs"]=[_id2name.get(x,x) for x in node["drugs"]]
        for c in node.get("ch",[]): _norm(c)
for _o in strategy_map: _norm(_o)

atlas={
 "schema_version":"1.1",
 "meta":{"disease":"Atopic dermatitis","scope":"indication","generated":"2026-07-23","as_of":"July 2026",
   "generator":"disease-atlas research skill (demonstration run)",
   "one_liner":"Chronic type-2 (IL-4/IL-13-driven), intensely itchy inflammatory skin disease — a maturing biologics + oral-JAK market anchored by Dupixent, now competing on itch, convenience, safety and durability.",
   "mechanism_label":"Type-2 (IL-4/IL-13/IL-31) cascade → intracellular signalling","efficacy_label":"EASI-75",
   "cascade_label":"Type-2 immune cascade","signal_tracks":["Type-2 differentiation (IL-4/IL-13)","Itch & barrier signalling"],
   "signal_caption":"Epithelial alarmins activate ILC2/Th2 cells → <b>IL-4/IL-13</b> signal via <b>IL-4Rα</b> and <b>JAK1/STAT6</b>; <b>IL-31</b> drives itch and <b>IL-13</b> drives keratinocyte barrier dysfunction. Click any node for the science.",
   "sales_note":"Dupixent sales are all-indication franchise totals (AD is the majority). Market and segment figures are bottom-up [Estimated] and cross-checked against published envelopes.",
   "coverage_note":"Demonstration atlas: structural data (assets, mechanisms, companies, phases) from live Open Targets + ClinicalTrials.gov + openFDA pulls; market/forecast figures are labeled [Estimated] or anchored to public company revenue. A full research pass would web-cite each market datum.",
   "headline_stats":[{"label":"Global prevalence (GBD)","value":"~223M"},{"label":"US adults / children","value":"~7% / ~13%"},
     {"label":"Global market (2024)","value":"~$19.5B"},{"label":"Forecast 2030 · base","value":"~$36B"}]},
 "epidemiology":{"headline":epi["headline"],"stats":epi["stats"],"comorbidities":epi["comorbidities"],"unmet":epi["unmet"],
   "dlqi":epi["dlqi"],"drug_survival":epi["drug_survival"],"comorbid":epi["comorbid"],"mortality":epi["mortality"],"sources":["gbd","aad"]},
 "sites":[{"site":s,"prev":p,"note":n} for s,p,n in sites],
 "standard_of_care":soc,
 "market_share":[{"cls":c,"trend":t,"colorVar":cv} for c,t,cv in market_share],
 "families":families,
 "moa_landscape":moa_landscape,
 "pipeline":{"assets":[dict(id="d_"+slug(d["name"]),**d) for d in ROSTER]},
 "companies":[],
 "biology_graph":biology_graph,
 "strategy_map":strategy_map,
 "response_kinetics":response_kinetics,
 "evidence":{"landmark_trials":[
   ["SOLO 1/2","dupilumab","il4_13",2016,"Ph3","EASI-75 ~44–51% vs ~12% placebo — established IL-4Rα blockade in AD.","ctgov"],
   ["Measure Up 1/2","upadacitinib","jak",2021,"Ph3","EASI-75 ~70% — highest among orals; opened the oral-JAK tier.","ctgov"],
   ["ADvocate 1/2","lebrikizumab","il13",2023,"Ph3","EASI-75 ~43% with q4w maintenance — selective IL-13.","ctgov"],
   ["ARCADIA 1/2","nemolizumab","il31",2024,"Ph3","Rapid itch reduction via IL-31RA — validated the itch axis.","ctgov"],
   ["STREAM-AD","amlitelimab","tslp_ox40",2024,"Ph2b","Durable responses off-drug with anti-OX40L — the remission bet.","ctgov"]]},
 "trials_focus":{"trials":[],"note":"Detailed trial cards would be pulled from ClinicalTrials.gov v2 by NCT id in a full run."},
 "catalysts":catalysts,
 "deals":[{"acquirer":a,"counterparty":c,"asset":ast,"value":v,"date":dt,"category":cat,"stage":st,"note":nt} for a,c,ast,v,dt,cat,st,nt in deals],
 "market_research":market_research,
 "glossary":[{"term":t,"def":d} for t,d in glossary],
 "sources":sources}

dst=os.path.join(os.path.dirname(os.path.abspath(__file__)),"atlas_ad.json")
json.dump(atlas,open(dst,"w",encoding="utf-8"),indent=1,ensure_ascii=False)
print("wrote",dst,"| assets:",len(ROSTER),"| families:",len(families),"| biology:",len(biology_graph["nodes"]))
