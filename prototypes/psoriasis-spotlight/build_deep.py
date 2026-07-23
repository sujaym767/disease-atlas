#!/usr/bin/env python3
"""Author a DEEP plaque-psoriasis graph (RA-Capital density) and emit graph.json.

Roster backbone = the live Open Targets pull (real names/mechanism/phase) + the
well-established late-stage assets, with curated per-drug attributes. Sales/PASI/
catalyst figures are refined from cited research (see notes.md); values flagged
est=True are approximate pending/among cited sources.
"""
import json, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
def slug(s): return re.sub(r"-{2,}","-",re.sub(r"[^a-z0-9]+","-",(s or "").lower())).strip("-")

# ---- families (lanes), each a palette slot ----
FAM = {  # key: (label, colorVar, order)
 "il23": ("IL-23 / Th17 axis","--s1",1),
 "il17": ("IL-17 axis","--s2",2),
 "tnf":  ("TNF inhibitors","--s5",3),
 "kinase":("Oral kinase inhibitors (TYK2 / JAK)","--s3",4),
 "pde4": ("PDE4 inhibitors","--s7",5),
 "topical":("Topical non-steroidal","--s4",6),
 "steroid":("Topical corticosteroids","--sN",7),
 "conv": ("Conventional systemics","--s8",8),
 "novel":("Novel / emerging mechanisms","--s6",9),
 "hist": ("Withdrawn / discontinued","--sN",10),
}

# ---- roster: (name, brand, company, fam, sub_class, target, modality, phase, route, dosing,
#               approval_yr, sales_usd_m, sales_yr, biosimilar, combo, discontinued, p75, p90, p100, note) ----
def D(name,brand,company,fam,sub,target,mod,phase,route,dose,appr=None,sales=None,syr=None,bios=None,combo=False,disc=False,p75=None,p90=None,p100=None,note=None):
    return dict(name=name,brand=brand,company=company,fam=fam,sub=sub,target=target,mod=mod,phase=phase,route=route,
                dose=dose,appr=appr,sales=sales,syr=syr,bios=bios,combo=combo,disc=disc,p75=p75,p90=p90,p100=p100,note=note)

ROSTER = [
 # ---- IL-23 axis ----
 D("guselkumab","Tremfya","Johnson & Johnson","il23","IL-23 p19 inhibitor","IL23A","mAb","approved","SC","q8w",2017,5200,2025,p75=91,p90=73,p100=37),
 D("risankizumab","Skyrizi","AbbVie","il23","IL-23 p19 inhibitor","IL23A","mAb","approved","SC","q12w",2019,17562,2025,p75=88,p90=75,p100=36,note="FY2025 sales all-indication (PsO+PsA+IBD); AbbVie's top product"),
 D("tildrakizumab","Ilumya","Sun Pharma","il23","IL-23 p19 inhibitor","IL23A","mAb","approved","SC","q12w",2018,p75=64,p90=35,p100=14),
 D("mirikizumab","Omvoh","Eli Lilly","il23","IL-23 p19 inhibitor","IL23A","mAb","phase3","SC","q8w",note="approved in UC; Ph3 in psoriasis",p90=74),
 D("icotrokinra","Icotyde","Johnson & Johnson","il23","Oral IL-23R antagonist","IL23R","peptide","approved","PO","QD",appr=2026,note="first oral IL-23R peptide; FDA-approved Mar 2026 (JNJ-2113)"),
 D("ustekinumab","Stelara","Johnson & Johnson","il23","IL-12/23 p40 inhibitor","IL12B","mAb","approved","SC","q12w",2009,6080,2025,bios="biosimilars from Jan 2025 (Wezlana, Steqeyma…); sales −41% YoY",p75=67,p90=42,p100=20),
 D("briakinumab","—","Abbott","il23","IL-12/23 p40 inhibitor","IL12B","mAb","discontinued","SC","q4w",disc=True,note="Ph3; withdrawn (cardiovascular signal)"),
 D("ebdarokimab","—","Akeso","il23","IL-12/23 p40 inhibitor","IL12B","mAb","phase3","SC","q12w",note="Ph3 in China"),
 # ---- IL-17 axis ----
 D("secukinumab","Cosentyx","Novartis","il17","IL-17A inhibitor","IL17A","mAb","approved","SC","q4w",2015,6700,2025,p75=82,p90=59,p100=29),
 D("ixekizumab","Taltz","Eli Lilly","il17","IL-17A inhibitor","IL17A","mAb","approved","SC","q4w",2016,3260,2024,p75=89,p90=71,p100=40),
 D("vunakizumab","—","Jiangsu Hengrui","il17","IL-17A inhibitor","IL17A","mAb","phase3","SC","q8w",note="Ph3 in China"),
 D("bimekizumab","Bimzelx","UCB","il17","IL-17A/F inhibitor","IL17A","mAb","approved","SC","q8w",2023,2400,2025,p75=93,p90=85,p100=61,note="dual IL-17A and IL-17F; highest PASI 100; sales +>200% YoY"),
 D("sonelokimab","—","MoonLake Immunotherapeutics","il17","IL-17A/F inhibitor","IL17A","protein","phase2","SC","q8w",note="IL-17A/F Nanobody (M-1095); Ph2 MIRA in PsO, sponsor prioritizing HS",p90=80),
 D("brodalumab","Siliq","Bausch Health","il17","IL-17RA inhibitor","IL17RA","mAb","approved","SC","q2w",2017,p75=86,p90=70,p100=44,note="boxed warning (suicidal ideation)"),
 D("izokibep","—","ACELYRIN / Alumis","il17","IL-17A (small protein)","IL17A","protein","phase2","SC","q2w",note="IL-17A affibody; derm development deprioritized (2024)"),
 D("DC-806","—","Eli Lilly (DICE)","il17","Oral IL-17 inhibitor","IL17A","small_molecule","phase1","PO","QD",note="oral IL-17A antagonist"),
 D("DC-853","—","Eli Lilly (DICE)","il17","Oral IL-17 inhibitor","IL17A","small_molecule","preclinical","PO","QD",note="next-gen oral IL-17A"),
 D("CJM-112","—","Novartis","il17","IL-17A inhibitor","IL17A","mAb","phase1","SC","—"),
 D("LEO-153339","—","LEO Pharma / UNION","il17","Oral IL-17 inhibitor","IL17A","small_molecule","preclinical","PO","QD",note="oral IL-17 program"),
 # ---- TNF ----
 D("adalimumab","Humira","AbbVie","tnf","TNF inhibitor","TNF","mAb","approved","SC","q2w",2008,sales=4540,syr=2025,bios="biosimilars from 2023 (US); sales collapsed from ~$21B peak",p75=71,p90=45,p100=17),
 D("etanercept","Enbrel","Amgen","tnf","TNF inhibitor","TNF","protein","approved","SC","weekly",2004,sales=2200,syr=2025,bios="biosimilars in EU; none in US (patents ~2029)",p75=44,p90=21,p100=4),
 D("infliximab","Remicade","Johnson & Johnson","tnf","TNF inhibitor","TNF","mAb","approved","IV","q8w",2006,sales=1768,syr=2025,bios="biosimilars since 2016 (Inflectra, Renflexis, Avsola)",p75=80,p90=57),
 D("certolizumab pegol","Cimzia","UCB","tnf","TNF inhibitor","TNF","mAb","approved","SC","q2w",2018,sales=2100,syr=2025,p75=83,p90=60,note="PEGylated Fab' (no Fc); used more in arthritis than PsO"),
 # ---- Oral kinase inhibitors ----
 D("deucravacitinib","Sotyktu","Bristol Myers Squibb","kinase","TYK2 allosteric inhibitor","TYK2","small_molecule","approved","PO","QD",2022,sales=291,syr=2025,p75=58,p90=35,p100=17,note="first oral TYK2; FY2025 sales $291M"),
 D("zasocitinib","—","Takeda","kinase","TYK2 allosteric inhibitor","TYK2","small_molecule","phase3","PO","QD",note="next-gen oral TYK2 (TAK-279)",p90=45),
 D("ESK-001","—","Alumis","kinase","TYK2 allosteric inhibitor","TYK2","small_molecule","phase3","PO","BID"),
 D("ropsacitinib","—","Pfizer","kinase","TYK2 inhibitor","TYK2","small_molecule","phase2","PO","QD",note="PF-06826647"),
 D("brepocitinib","—","Priovant / Pfizer","kinase","TYK2/JAK1 inhibitor","TYK2","small_molecule","phase2","PO","QD",note="dual TYK2/JAK1"),
 D("tofacitinib","Xeljanz","Pfizer","kinase","JAK inhibitor","JAK3","small_molecule","phase3","PO","BID",note="studied in Ph3; not approved for psoriasis (US)"),
 D("peficitinib","Smyraf","Astellas","kinase","JAK inhibitor","JAK1","small_molecule","phase3","PO","QD",note="Ph3 (Japan)"),
 D("ruxolitinib","Opzelura","Incyte","kinase","JAK inhibitor (topical)","JAK1","small_molecule","phase2","topical","BID"),
 # ---- PDE4 ----
 D("apremilast","Otezla","Amgen","pde4","Oral PDE4 inhibitor","PDE4","small_molecule","approved","PO","BID",2014,sales=2400,syr=2025,p75=33,p90=10,note="FY2025 approx; selected for Medicare IRA price-setting"),
 D("orismilast","—","UNION therapeutics","pde4","Oral PDE4 inhibitor","PDE4","small_molecule","phase2","PO","BID",note="Ph2b positive in PsO; sponsor advancing Ph3 in atopic dermatitis"),
 D("roflumilast","Zoryve","Arcutis Biotherapeutics","pde4","Topical PDE4 inhibitor","PDE4","small_molecule","approved","topical","QD",2022,sales=372,syr=2025,note="FY2025 franchise (PsO+seb derm+AD); scalp/body foam approved May 2025"),
 D("crisaborole","Eucrisa","Pfizer","pde4","Topical PDE4 inhibitor","PDE4","small_molecule","phase2","topical","BID",note="approved in atopic dermatitis"),
 # ---- Topical non-steroidal ----
 D("tapinarof","Vtama","Organon (Dermavant)","topical","AhR agonist (topical)","AHR","small_molecule","approved","topical","QD",2022),
 D("calcipotriene","Dovonex / Enstilar","LEO Pharma","topical","Vitamin D analog (topical)","VDR","small_molecule","approved","topical","QD-BID",1993,combo=True,note="often co-formulated with a steroid"),
 D("calcitriol","Vectical","LEO / Galderma","topical","Vitamin D analog (topical)","VDR","small_molecule","approved","topical","BID",2009),
 D("tazarotene","Tazorac","Allergan","topical","Retinoid (topical)","RARB","small_molecule","approved","topical","QD",1997),
 # ---- Topical corticosteroids ----
 D("clobetasol propionate","Temovate / Clobex","generic","steroid","Topical corticosteroid","NR3C1","small_molecule","approved","topical","BID",note="super-high potency"),
 D("betamethasone dipropionate","Diprolene","generic","steroid","Topical corticosteroid","NR3C1","small_molecule","approved","topical","QD-BID",combo=True),
 D("halobetasol propionate","Ultravate","Bausch Health","steroid","Topical corticosteroid","NR3C1","small_molecule","approved","topical","QD",combo=True,note="also co-formulated with tazarotene (Duobrii)"),
 D("desoximetasone","Topicort","generic","steroid","Topical corticosteroid","NR3C1","small_molecule","approved","topical","BID"),
 # ---- Conventional systemics ----
 D("methotrexate","—","generic","conv","Antimetabolite (DHFR)","DHFR","small_molecule","approved","PO","weekly",p75=38,p90=16),
 D("cyclosporine","Neoral","generic","conv","Calcineurin inhibitor","PPIA","small_molecule","approved","PO","BID",p75=50),
 D("acitretin","Soriatane","generic","conv","Systemic retinoid","RARA","small_molecule","approved","PO","QD",note="teratogenic; often combined with phototherapy"),
 D("dimethyl fumarate","Skilarence","Almirall","conv","Fumaric acid ester","NFE2L2","small_molecule","approved","PO","BID",appr=2017,note="approved in EU"),
 # ---- Novel / emerging ----
 D("piclidenoson","—","Can-Fite BioPharma","novel","A3 adenosine agonist","ADORA3","small_molecule","phase3","PO","BID",note="Ph3 COMFORT efficacy weak (PASI75 ~10%); stalled"),
 D("fezakinumab","—","Pfizer","novel","IL-22 inhibitor","IL22","mAb","phase2","SC","q2w"),
 D("vixarelimab","—","Genentech","novel","OSMRβ inhibitor (IL-31/OSM)","OSMR","mAb","phase2","SC","q2w"),
 D("namilumab","—","Roivant","novel","GM-CSF inhibitor","CSF2","mAb","phase2","SC","q4w"),
 D("spesolimab","Spevigo","Boehringer Ingelheim","novel","IL-36R inhibitor","IL1RL2","mAb","approved","IV/SC","—",appr=2022,note="approved for generalized pustular psoriasis (adjacent)"),
 D("imsidolimab","—","AnaptysBio","novel","IL-36R inhibitor","IL1RL2","mAb","phase3","SC","—",note="Ph3 in GPP (adjacent)"),
 D("GSK2982772","—","GSK","novel","RIPK1 inhibitor","RIPK1","small_molecule","phase2","PO","TID"),
 D("ponesimod","Ponvory","Johnson & Johnson","novel","S1P receptor modulator","S1PR1","small_molecule","discontinued","PO","QD",disc=True,note="Ph2 for psoriasis discontinued; approved in MS"),
 # ---- Historical / withdrawn ----
 D("efalizumab","Raptiva","Genentech / Merck","hist","Anti-CD11a (LFA-1)","ITGAL","mAb","discontinued","SC","weekly",disc=True,note="withdrawn 2009 (PML risk)"),
 D("alefacept","Amevive","Astellas","hist","Anti-CD2 (LFA-3 fusion)","CD2","protein","discontinued","IM","weekly",disc=True,note="discontinued (commercial)"),
]

PHASE_NUM={"approved":4,"filed":3.7,"phase3":3,"phase2_3":2.5,"phase2":2,"phase1_2":1.5,"phase1":1,"preclinical":0,"discontinued":-1}

# sources (from the live pulls + cited research agents)
SOURCES=[
 {"id":"ot","type":"api","name":"Open Targets Platform","title":"Psoriasis vulgaris (EFO_1001494) — targets & drug candidates","url":"https://platform.opentargets.org/disease/EFO_1001494","accessed":"2026-07-23"},
 {"id":"ctgov","type":"api","name":"ClinicalTrials.gov","title":"Interventional psoriasis trials (901, live pull)","url":"https://clinicaltrials.gov/","accessed":"2026-07-23"},
 {"id":"fda","type":"label","name":"openFDA / Drugs@FDA","title":"FDA approvals, classes & boxed warnings","url":"https://www.accessdata.fda.gov/scripts/cder/daf/","accessed":"2026-07-23"},
 {"id":"xtalks","type":"web","name":"Xtalks","title":"Top-selling immunology drugs — sales","url":"https://xtalks.com/top-10-best-selling-immunology-drugs-by-recent-sales-data-4025/","accessed":"2026-07-23"},
 {"id":"npf","type":"web","name":"National Psoriasis Foundation","title":"Psoriasis statistics / prevalence","url":"https://www.psoriasis.org/psoriasis-statistics/","accessed":"2026-07-23"},
 {"id":"gbd","type":"publication","name":"GBD 2019","title":"Global burden of psoriasis","url":"https://pmc.ncbi.nlm.nih.gov/articles/PMC8716585/","accessed":"2026-07-23"},
 {"id":"usprev","type":"publication","name":"JAMA Dermatol","title":"Psoriasis prevalence in US adults","url":"https://pmc.ncbi.nlm.nih.gov/articles/PMC8246333/","accessed":"2026-07-23"},
 {"id":"armstrong","type":"publication","name":"Armstrong 2020 (JAMA Dermatol NMA)","title":"Comparative efficacy (PASI 90) network meta-analysis, 60 trials","url":"https://pmc.ncbi.nlm.nih.gov/articles/PMC7042876/","accessed":"2026-07-23"},
 {"id":"cochrane","type":"publication","name":"Cochrane NMA (Sbidian 2023)","title":"Systemic psoriasis therapies — efficacy & safety NMA","url":"https://pubmed.ncbi.nlm.nih.gov/37436070/","accessed":"2026-07-23"},
 {"id":"jnj_icotyde","type":"web","name":"Johnson & Johnson","title":"FDA approval of ICOTYDE (icotrokinra), Mar 2026","url":"https://www.jnj.com/media-center/press-releases/fda-approval-of-icotyde-icotrokinra-ushers-in-new-era-for-first-line-systemic-treatment-of-plaque-psoriasis-with-a-targeted-oral-peptide","accessed":"2026-07-23"},
 {"id":"takeda_zaso","type":"web","name":"Takeda","title":"Zasocitinib positive Phase 3 topline (Dec 2025)","url":"https://www.takeda.com/newsroom/newsreleases/2025/takeda-zasocitinib-phase-3-plaque-psoriasis-data-once-daily-pill/","accessed":"2026-07-23"},
 {"id":"alumis_esk","type":"web","name":"Alumis","title":"Envudeucitinib (ESK-001) positive Phase 3 (Jan 2026)","url":"https://investors.alumis.com/news-releases/news-release-details/alumis-envudeucitinib-delivers-leading-skin-clearance-among-next","accessed":"2026-07-23"},
 {"id":"cfb_stelara","type":"web","name":"Center for Biosimilars","title":"First Stelara biosimilar (Wezlana) launches, Jan 2025","url":"https://www.centerforbiosimilars.com/view/welcome-wezlana-the-first-stelara-biosimilar-to-launch-in-the-us","accessed":"2026-07-23"},
 {"id":"ajmc_humira","type":"web","name":"AJMC","title":"First Humira biosimilar (Amjevita) launches in the US","url":"https://www.ajmc.com/view/first-humira-biosimilar-amjevita-launches-in-the-united-states","accessed":"2026-07-23"},
 {"id":"arcutis_foam","type":"web","name":"Arcutis","title":"Zoryve foam 0.3% approved for scalp & body psoriasis (May 2025)","url":"https://www.arcutis.com/arcutis-zoryve-roflumilast-topical-foam-0-3-approved-by-u-s-fda-for-the-treatment-of-plaque-psoriasis-in-adults-and-adolescents-ages-12-and-older/","accessed":"2026-07-23"},
 {"id":"dpw","type":"web","name":"DrugPatentWatch","title":"Biologic patent-expiry / loss-of-exclusivity projections","url":"https://www.drugpatentwatch.com/","accessed":"2026-07-23"},
 {"id":"abbvie25","type":"filing","name":"AbbVie FY2025 results","title":"Skyrizi $17.56B, Humira $4.54B (all-indication)","url":"https://news.abbvie.com/2026-02-04-AbbVie-Reports-Full-Year-and-Fourth-Quarter-2025-Financial-Results","accessed":"2026-07-23"},
 {"id":"jnj25","type":"filing","name":"Johnson & Johnson FY2025 results","title":"Stelara $6.08B, Tremfya ~$5.2B, Remicade $1.77B","url":"https://www.investor.jnj.com/investor-news/news-details/2026/Johnson--Johnson-reports-Q4-and-Full-Year-2025-results/default.aspx","accessed":"2026-07-23"},
 {"id":"nvs25","type":"filing","name":"Novartis FY2025 results","title":"Cosentyx $6.7B","url":"https://www.novartis.com/news/media-releases/novartis-delivered-high-single-digit-sales-growth-achieved-40-core-margin-and-further-advanced-pipeline-2025","accessed":"2026-07-23"},
 {"id":"ucb25","type":"filing","name":"UCB FY2025 results","title":"Bimzelx >€2.2B, Cimzia €1.95B","url":"https://www.ucb.com/sites/default/files/2026-02/UCB-PR-2025-FY-Results-ENG.pdf","accessed":"2026-07-23"},
 {"id":"amgen25","type":"filing","name":"Amgen FY2025 results","title":"Otezla, Enbrel (Q4 absolutes; FY approximate)","url":"https://www.amgen.com/newsroom/press-releases/2026/02/amgen-reports-fourth-quarter-and-full-year-2025-financial-results","accessed":"2026-07-23"},
 {"id":"bms25","type":"filing","name":"Bristol Myers Squibb FY2025 results","title":"Sotyktu $291M","url":"https://www.bms.com/assets/bms/us/en-us/pdf/investor-info/doc_financials/quarterly_reports/2025/BMY-Q4-2025-Earnings-Press-Release.pdf","accessed":"2026-07-23"},
 {"id":"lilly_taltz","type":"web","name":"Eli Lilly / IBJ","title":"Taltz FY2024 $3.26B; FY2025 tracking ~$3.4B","url":"https://www.ibj.com/articles/lillys-hot-selling-taltz-approaching-blockbuster-status","accessed":"2026-07-23"},
 {"id":"arcutis25","type":"filing","name":"Arcutis FY2025 results","title":"Zoryve franchise $372.1M","url":"https://www.globenewswire.com/news-release/2026/02/25/3244953/0/en/Arcutis-Announces-Fourth-Quarter-and-Full-Year-2025-Financial-Results-and-Provides-Business-Update.html","accessed":"2026-07-23"},
 {"id":"aadnpf","type":"guideline","name":"AAD–NPF Guidelines","title":"Joint AAD–NPF guidelines of care for psoriasis (topicals, phototherapy, systemics, biologics)","url":"https://www.aad.org/member/clinical-quality/guidelines/psoriasis","accessed":"2026-07-23"},
 {"id":"dlqi","type":"publication","name":"NPF / QoL literature","title":"DLQI, work productivity & economic burden of psoriasis","url":"https://www.psoriasis.org/psoriasis-statistics/","accessed":"2026-07-23"},
 {"id":"drugsurv","type":"publication","name":"BADBIR / PsoBest registries","title":"Real-world biologic drug survival (persistence) in psoriasis","url":"https://pubmed.ncbi.nlm.nih.gov/33739452/","accessed":"2026-07-23"},
 {"id":"voyage","type":"publication","name":"VOYAGE 1/2 (Blauvelt/Reich 2017, JAAD)","title":"Guselkumab pivotal Phase 3 vs adalimumab & placebo","url":"https://pubmed.ncbi.nlm.nih.gov/28057360/","accessed":"2026-07-23"},
 {"id":"ultimma","type":"publication","name":"UltIMMa-1/2 (Gordon 2018, Lancet)","title":"Risankizumab vs ustekinumab & placebo","url":"https://pubmed.ncbi.nlm.nih.gov/30097359/","accessed":"2026-07-23"},
 {"id":"eclipse","type":"publication","name":"ECLIPSE (Reich 2019, Lancet)","title":"Guselkumab vs secukinumab — head-to-head, week-48 superiority","url":"https://pubmed.ncbi.nlm.nih.gov/31543211/","accessed":"2026-07-23"},
 {"id":"uncover","type":"publication","name":"UNCOVER-1/2/3 (Gordon 2016, NEJM)","title":"Ixekizumab pivotal Phase 3","url":"https://pubmed.ncbi.nlm.nih.gov/27299809/","accessed":"2026-07-23"},
 {"id":"erasure","type":"publication","name":"ERASURE / FIXTURE (Langley 2014, NEJM)","title":"Secukinumab pivotal Phase 3 vs etanercept & placebo","url":"https://pubmed.ncbi.nlm.nih.gov/25007392/","accessed":"2026-07-23"},
 {"id":"bevivid","type":"publication","name":"BE VIVID / BE READY / BE SURE (2021, Lancet/NEJM)","title":"Bimekizumab pivotal Phase 3 — deepest PASI 100","url":"https://pubmed.ncbi.nlm.nih.gov/33549193/","accessed":"2026-07-23"},
 {"id":"poetyk","type":"publication","name":"POETYK PSO-1/PSO-2 (Armstrong 2023, JAAD)","title":"Deucravacitinib vs apremilast & placebo — first oral TYK2","url":"https://pubmed.ncbi.nlm.nih.gov/36191693/","accessed":"2026-07-23"},
 {"id":"iconic","type":"web","name":"ICONIC-LEAD (Johnson & Johnson, 2025)","title":"Icotrokinra Phase 3 — first oral IL-23R peptide","url":"https://www.jnj.com/media-center/press-releases","accessed":"2026-07-23"},
]
# which FY2025 source backs each company's reported sales
COMP_SALES_SRC={"AbbVie":"abbvie25","Johnson & Johnson":"jnj25","Novartis":"nvs25","UCB":"ucb25",
 "Amgen":"amgen25","Bristol Myers Squibb":"bms25","Eli Lilly":"lilly_taltz","Arcutis Biotherapeutics":"arcutis25"}

# class-level safety signals (per family) — from Cochrane NMA + reviews (cited)
SAFETY={
 "il17":"Mucocutaneous Candida (highest with bimekizumab); caution/avoid in IBD; brodalumab carries a boxed warning for suicidal ideation. No consistent MACE/malignancy signal.",
 "il23":"Cleanest profile — no increased candidiasis or IBD signal (may be IBD-protective), low serious-infection rates, no boxed warnings.",
 "tnf":"Boxed warnings: serious infections (incl. TB reactivation — screen first) and malignancy (lymphoma). HBV reactivation, demyelination, CHF worsening; highest herpes-zoster rate.",
 "kinase":"Selective TYK2 (deucravacitinib) does NOT carry the JAK boxed warning; 5-yr data show no MACE/VTE/malignancy signal. Classic JAK inhibitors carry the class boxed warning (infection, MACE, thrombosis, malignancy).",
 "pde4":"No boxed warning, no lab monitoring. GI (diarrhea/nausea), weight loss, and a depression/mood warning (apremilast).",
 "topical":"Local, well-tolerated; steroid-sparing. Suitable for chronic use and sensitive sites.",
 "steroid":"Skin atrophy, striae, tachyphylaxis and HPA-axis suppression with chronic/high-potency use.",
 "conv":"Organ toxicity and monitoring: MTX (hepatotoxicity, cytopenia, teratogenic), cyclosporine (nephrotoxicity, hypertension), acitretin (teratogenic, hyperlipidemia).",
}

# dated catalysts (cited) — kind: patent_expiry | approval | readout | filing
CAT=[
 ("2023-07","Humira (adalimumab) biosimilars enter US","patent_expiry","AbbVie","adalimumab","First big psoriasis-biologic patent cliff; ~9 biosimilars in 2023.","ajmc_humira"),
 ("2023-10","Bimzelx (bimekizumab) approved for plaque psoriasis (US)","approval","UCB","bimekizumab","First IL-17A and IL-17F inhibitor; deepest skin-clearance benchmark.","fda"),
 ("2025-01","Stelara (ustekinumab) US biosimilar cliff","patent_expiry","Johnson & Johnson","ustekinumab","~7 biosimilars launch in 2025 at up to ~85% discount; Stelara ~$10.4B (2024).","cfb_stelara"),
 ("2025-05","Zoryve (roflumilast) foam approved for scalp & body","approval","Arcutis Biotherapeutics","roflumilast","Extends the topical PDE4 franchise into scalp.","arcutis_foam"),
 ("2025-12","Zasocitinib (TAK-279) positive Phase 3 topline","readout","Takeda","zasocitinib",">50% PASI 90, ~30% PASI 100 at wk16; positions oral TYK2 as a 2026 filer.","takeda_zaso"),
 ("2026-01","Envudeucitinib (ESK-001) positive Phase 3 topline","readout","Alumis","ESK-001","~74% PASI 75; oral TYK2 competitor; NDA planned H2 2026.","alumis_esk"),
 ("2026-03","ICOTYDE (icotrokinra) FDA-approved","approval","Johnson & Johnson","icotrokinra","First targeted ORAL IL-23R peptide; category-defining first-line oral.","jnj_icotyde"),
 ("2028","Otezla (apremilast) earliest generic entry (proj.)","patent_expiry","Amgen","apremilast","Oral PDE4 loss of exclusivity.","dpw"),
 ("2029","Cosentyx (secukinumab) US patent expiry (proj.)","patent_expiry","Novartis","secukinumab","IL-17 biosimilars already in Phase 3.","dpw"),
 ("2031","Tremfya (guselkumab) US patent expiry (proj.)","patent_expiry","Johnson & Johnson","guselkumab","IL-23 franchise exclusivity.","dpw"),
 ("2033","Skyrizi (risankizumab) basic patent expiry (proj.)","patent_expiry","AbbVie","risankizumab","Longest runway of the IL-23 class; AbbVie's post-Humira anchor.","dpw"),
]

# --- patient burden / epidemiology ---
EPI={
 "headline":"~125M worldwide · ~7.5M US adults · ~20% moderate-to-severe",
 "stats":[("~125M","Worldwide (2–3% of population)","npf"),("~7.5M","US adults (3.0%)","npf"),
   ("~20%","Moderate-to-severe (systemic-eligible)","npf"),("~30%","Develop psoriatic arthritis","gbd"),
   ("~600k","US adults undiagnosed","npf"),("4.3%","Peak prevalence (age 50–59)","npf")],
 "comorbidities":"Elevated cardiovascular, metabolic-syndrome, IBD and depression risk; psoriatic arthritis in ~30%.",
 "journey":["Onset (bimodal ~20s & ~50s) → clinical diagnosis, often delayed","Topicals ± phototherapy for mild disease",
   "Step-up to oral systemics / biologics for moderate-to-severe","Biologic maintenance; switching on loss of response / comorbidity"],
 "unmet":"Large share of moderate-to-severe patients remain untreated or under-treated (cost, access, injection aversion). Durable drug-free remission and hard-to-treat sites remain the key gaps.",
 "sources":["npf","gbd","usprev"] if False else ["npf","gbd"],
}
# --- hard-to-treat sites / special populations ---
SITES=[
 ("Scalp","~45–80% of patients","High-visibility, itch-driven; foams/solutions; a common driver of systemic step-up."),
 ("Nails","~50% (lifetime)","Slow to respond; often needs systemic therapy; predicts psoriatic arthritis."),
 ("Palmoplantar","~12–16%","Painful, disabling, frequently refractory to standard therapy."),
 ("Genital / inverse","~30–60% (genital ever)","Major QoL impact; sensitive-site tolerability; historically understudied."),
 ("Pediatric","~1% of children","Growing label set (etanercept, ustekinumab, ixekizumab, secukinumab, apremilast, icotrokinra ≥12)."),
]
# --- deal flow (Deal nodes + edges) ---  (acquirer, counterparty, asset, value, date, category, stage, note)
# category ∈ {M&A, Licensing, Partnership}; stage = asset's development stage at deal time
DEALS=[
 ("Bristol Myers Squibb","Celgene","deucravacitinib","$74B",  "2019-11","M&A","Clinical","Deucravacitinib (oral TYK2, then BMS-986165) entered BMS via the $74B Celgene acquisition."),
 ("Amgen","Celgene / BMS","apremilast","$13.4B","2019-11","M&A","Marketed","Otezla (PDE4) was divested for antitrust clearance during the BMS–Celgene merger."),
 ("Takeda","Nimbus Therapeutics","zasocitinib","$4.0B upfront +$2B milestones","2023-02","M&A","Clinical","Allosteric oral TYK2 TAK-279 acquired from Nimbus after strong Ph2b."),
 ("Eli Lilly","DICE Therapeutics","DC-806","$2.4B","2023-08","M&A","Preclinical","Oral IL-17 antagonist platform (DELSCAPE) acquired for early oral biologics-alternatives."),
 ("Organon","Dermavant","tapinarof","up to ~$1.2B","2024-10","M&A","Marketed","Topical AhR agonist Vtama acquired to build Organon's dermatology franchise."),
 ("Alumis","ACELYRIN","ESK-001 / izokibep","all-stock merger","2025-02","M&A","Clinical","Merged next-gen oral-immunology pipelines (ESK-001 TYK2 + izokibep IL-17)."),
 ("Johnson & Johnson","Protagonist Therapeutics","icotrokinra","co-development + royalties","2017-07","Licensing","Discovery","Oral IL-23R peptide (JNJ-2113) discovered by Protagonist, co-developed and commercialised by J&J."),
 ("Sun Pharma","Merck (MSD)","tildrakizumab","$80M upfront + royalties","2014-09","Licensing","Clinical","Ex-license of the IL-23 p19 mAb (then MK-3222) to Sun for worldwide development."),
 ("LEO Pharma","UNION therapeutics","orismilast","option / partnership","2021-01","Partnership","Clinical","Collaboration on next-gen PDE4 inhibition in inflammatory skin disease."),
]
# --- schematic anchor per mechanism family (IL-23/IL-17 cascade node) ---
ANCHOR={"il23":"il23","il17":"il17","tnf":"tnf","kinase":"tyk2","pde4":"pde4","topical":"kera","steroid":"kera","conv":"th17","novel":"th17","hist":"th17"}

# --- biology of the cascade: cells / cytokines / intracellular nodes (Biology node type) ---
# (pos = key in the template's SCH geometry map; description = original scientific summary)
BIO=[
 ("dc","Dendritic cell","cell","dc","Dermal antigen-presenting cell. On activation it secretes IL-23, IL-12 and TNF, initiating and sustaining the pathogenic T-cell response that drives psoriatic plaques."),
 ("th17","Th17 cell","cell","th17","IL-23-dependent effector T cell. It signals intracellularly through TYK2 / JAK-STAT and secretes the effector cytokines IL-17A, IL-17F and IL-22."),
 ("kera","Keratinocyte","cell","kera","Epidermal cell. Under IL-17 and TNF it hyperproliferates and releases further chemokines and cytokines, closing a self-amplifying inflammatory loop that forms the scaly plaque."),
 ("plaque","Psoriatic plaque","outcome","plaque","The clinical lesion — a well-demarcated, thickened, scaly erythematous plaque produced by keratinocyte hyperproliferation and immune infiltration."),
 ("il23","IL-23","cytokine","il23","Dendritic-cell cytokine (p19 + p40) that maintains pathogenic Th17 cells — the most disease-specific and best-validated target in psoriasis."),
 ("p40","IL-12/23 p40","cytokine","p40","Shared subunit of IL-12 and IL-23. Blocking p40 (ustekinumab) inhibits both; selective p19 blockade has since proven more effective."),
 ("il17","IL-17A / IL-17F","cytokine","il17","The effector cytokines acting on keratinocytes. Neutralising them delivers the fastest, deepest skin clearance of any class."),
 ("il22","IL-22","cytokine","il22","Th17-derived cytokine promoting keratinocyte proliferation and epidermal acanthosis."),
 ("tnf","TNF-α","cytokine","tnf","Pleiotropic pro-inflammatory cytokine that amplifies the cascade at multiple points; the first successful biologic target in psoriasis."),
 ("tyk2","TYK2","intracellular","tyk2","Intracellular pseudokinase that transduces IL-23 (and type-I interferon) signalling — the basis of oral allosteric TYK2 inhibition."),
 ("pde4","PDE4 / cAMP","intracellular","pde4","Phosphodiesterase-4 regulates intracellular cAMP in immune cells; inhibiting it dampens pro-inflammatory cytokine output (apremilast, roflumilast)."),
]
# cascade edges among biology nodes: (type, from_suffix, to_suffix)
CASCADE=[("PRODUCES","dc","il23"),("PRODUCES","dc","p40"),("PRODUCES","dc","tnf"),
 ("ACTS_ON","il23","th17"),("SIGNALS_VIA","il23","tyk2"),
 ("PRODUCES","th17","il17"),("PRODUCES","th17","il22"),("PRODUCES","th17","tnf"),
 ("ACTS_ON","il17","kera"),("ACTS_ON","il22","kera"),("ACTS_ON","tnf","kera"),
 ("LEADS_TO","kera","plaque"),("FEEDBACK","kera","dc")]
# --- intracellular signal-transduction depth (receptors + kinases + transcription factors) ---
# rendered in a dedicated "signal transduction" inset; also first-class graph nodes for exploration.
SIGNAL=[
 ("il23r","IL-23 receptor","receptor","Cell-surface receptor complex (IL-23R + IL-12Rβ1) on Th17 cells. Engaged by IL-23; the target of the first oral IL-23R peptide antagonist (icotrokinra)."),
 ("il17r","IL-17RA receptor","receptor","Keratinocyte receptor (IL-17RA/RC) for IL-17A/F. Neutralised directly by brodalumab; signals via Act1 to NF-κB."),
 ("jak2","JAK2","intracellular","Janus kinase paired with TYK2 beneath the IL-23 receptor; together they phosphorylate STAT3 on cytokine binding."),
 ("stat3","STAT3","intracellular","Transcription factor phosphorylated by TYK2/JAK2. It translocates to the nucleus and switches on the Th17 genetic programme."),
 ("rorgt","RORγt","intracellular","Master transcription factor of Th17 identity, induced downstream of STAT3; it drives IL-17/IL-22 production and is an emerging small-molecule target."),
 ("nfkb","NF-κB","intracellular","Central inflammatory transcription factor activated in keratinocytes by IL-17 and TNF, amplifying chemokine and cytokine output."),
]
# signalling edges (added to the cascade graph)
SIGNAL_EDGES=[("BINDS","il23","il23r"),("SIGNALS_VIA","il23r","tyk2"),("SIGNALS_VIA","il23r","jak2"),
 ("ACTIVATES","tyk2","stat3"),("ACTIVATES","jak2","stat3"),("INDUCES","stat3","rorgt"),("SUSTAINS","rorgt","th17"),
 ("BINDS","il17","il17r"),("SIGNALS_VIA","il17r","nfkb"),("ACTS_ON","nfkb","kera"),("SIGNALS_VIA","tnf","nfkb")]
# ordered pathway for the inset renderer: (from, to, label)
SIGNAL_PATH=[("il23","il23r","IL-23 binds"),("il23r","tyk2","receptor-associated"),("il23r","jak2",""),
 ("tyk2","stat3","phosphorylate"),("jak2","stat3",""),("stat3","rorgt","induces"),("rorgt","th17","Th17 programme"),
 ("il17","il17r","IL-17 binds"),("il17r","nfkb","via Act1"),("nfkb","kera","inflammation")]

# bridge target -> biology (lets drug->target->biology path-finding reach the cascade)
TARGET_BIO={"IL23A":"il23","IL12B":"p40","IL17A":"il17","IL17RA":"il17r","TNF":"tnf","TYK2":"tyk2","PDE4":"pde4","IL23R":"il23r"}

# =====================================================================
# OBJECTIVE -> STRATEGY -> APPROACH -> MECHANISM -> ASSET mind-map (RA-Capital-style tree)
# Leaves carry an explicit drug list (drug names from ROSTER). Every asset is placed once.
# node: {t: title, d: desc?, k: kind(obj|strat|appr|mech), c: colorVar?, side?, ch: children | drugs: [names]}
# =====================================================================
def L(title, drugs, d=None):            # leaf mechanism node
    return {"t":title,"k":"mech","drugs":drugs,**({"d":d} if d else {})}
def NODE(title,kind,children,d=None,c=None,side=None):
    n={"t":title,"k":kind,"ch":children}
    if d:n["d"]=d
    if c:n["c"]=c
    if side:n["side"]=side
    return n
HIER=[
 NODE("Clear the skin & control inflammation","obj",[
   NODE("Systemic cytokine-directed biologics","strat",[
     NODE("Block the IL-23 / Th17 axis","appr",[
       L("IL-23 p19 inhibitors",["guselkumab","risankizumab","tildrakizumab","mirikizumab"],"Selective p19 blockade starves pathogenic Th17 cells — the deepest, most durable maintenance class."),
       L("IL-12/23 p40 inhibitors",["ustekinumab","briakinumab","ebdarokimab"],"Blocks the shared p40 subunit (IL-12 + IL-23); first-generation, now facing biosimilars."),
       L("Oral IL-23R antagonist",["icotrokinra"],"First targeted oral peptide blocking the IL-23 receptor — biologic-like selectivity in a pill."),
     ],"Neutralise the IL-23 signal that sustains Th17 cells — the most disease-specific axis."),
     NODE("Block IL-17 effector signalling","appr",[
       L("IL-17A inhibitors",["secukinumab","ixekizumab","vunakizumab","CJM-112"],"Neutralise the dominant effector cytokine; fast, deep clearance."),
       L("IL-17A/F inhibitors",["bimekizumab","sonelokimab"],"Dual IL-17A + IL-17F blockade — the deepest PASI-100 rates to date."),
       L("IL-17RA inhibitors",["brodalumab"],"Blocks the receptor (all IL-17 ligands); boxed warning shaped uptake."),
       L("Oral / small-protein IL-17",["izokibep","DC-806","DC-853","LEO-153339"],"Affibody and oral small-molecule attempts to bring IL-17 blockade to a pill."),
     ],"Neutralise the effector cytokines acting on keratinocytes."),
     NODE("Block TNF-α","appr",[
       L("TNF inhibitors",["adalimumab","etanercept","infliximab","certolizumab pegol"],"The original biologic target; now biosimilar-eroded but still workhorses, esp. with joint disease."),
     ]),
   ],"Neutralise a specific cytokine or receptor with an engineered protein — the deepest, most durable clearance."),
   NODE("Oral small-molecule targeted therapy","strat",[
     NODE("Intracellular kinase inhibition","appr",[
       L("TYK2 allosteric inhibitors",["deucravacitinib","zasocitinib","ESK-001"],"Allosteric TYK2 blockade avoids the JAK boxed warning; the fast-growing oral class."),
       L("TYK2 / JAK inhibitors",["ropsacitinib","brepocitinib","tofacitinib","peficitinib","ruxolitinib"],"Broader kinase inhibition (incl. topical JAK); efficacy vs class safety trade-offs."),
     ],"Inhibit the intracellular signalling that transduces IL-23 and other cytokines."),
     NODE("Raise cAMP (PDE4)","appr",[
       L("Oral PDE4 inhibitors",["apremilast","orismilast"],"Dampen cytokine output; modest efficacy, benign safety, no monitoring."),
     ]),
   ],"Convenient oral therapy — increasingly a first-line systemic choice."),
   NODE("Topical therapy","strat",[
     L("Non-steroidal topicals",["tapinarof","calcipotriene","calcitriol","tazarotene","roflumilast","crisaborole"],"Steroid-sparing keratinocyte-normalising agents (AhR, vitamin-D, retinoid, PDE4) now reaching scalp & folds."),
     L("Topical corticosteroids",["clobetasol propionate","betamethasone dipropionate","halobetasol propionate","desoximetasone"],"Anti-inflammatory mainstay for mild / localised disease."),
   ],"First line for mild or localised disease (~80% of patients)."),
   NODE("Conventional systemics","strat",[
     L("Legacy oral systemics",["methotrexate","cyclosporine","acitretin","dimethyl fumarate"],"Low-cost, widely used globally; require organ-toxicity monitoring."),
   ],"Cost-effective moderate-to-severe therapy where biologics are inaccessible."),
 ],"Psoriasis is a chronic IL-23/IL-17-driven disease; the dominant goal is durable skin clearance (PASI 90–100), escalating from topicals to cytokine blockade and oral targeted agents.","--s1","left"),

 NODE("Treat special & hard-to-treat disease","obj",[
   NODE("Generalised pustular psoriasis (GPP)","strat",[
     L("IL-36 receptor inhibitors",["spesolimab","imsidolimab"],"A distinct IL-36-driven neutrophilic variant; spesolimab is the first approved GPP-specific therapy."),
   ],"A severe, distinct pustular variant driven by the IL-36 axis rather than IL-23/IL-17."),
   NODE("Hard-to-treat sites & populations","strat",[
     L("Site-directed label expansion",[],"Scalp, nails, palmoplantar, genital and pediatric disease drive systemic step-up. No unique mechanism — the battleground is label expansion of IL-17 / IL-23 agents (see the sites panel)."),
   ],"Special sites and pediatrics carry outsized QoL impact and shape switching."),
 ],"Beyond plaque clearance, distinct variants and hard-to-treat sites need dedicated mechanisms and label expansion.","--s2","right"),

 NODE("Pursue durable remission & disease interception","obj",[
   NODE("Novel effector & cytokine mechanisms","strat",[
     L("Emerging cytokine targets",["fezakinumab","vixarelimab","namilumab"],"IL-22, OSMRβ/IL-31 and GM-CSF — exploratory effectors beyond the IL-23/IL-17 core."),
     L("Intracellular / other novel",["GSK2982772","piclidenoson"],"RIPK1 and A3-adenosine programmes probing new inflammatory nodes (efficacy so far modest)."),
   ],"Exploratory mechanisms seeking efficacy or durability the core axes don't deliver."),
   NODE("Immune trafficking & tolerance","strat",[
     L("T-cell / trafficking modulators",["ponesimod","efalizumab","alefacept"],"S1P modulation and (withdrawn) T-cell-directed agents — the historical arc toward immune modulation and, aspirationally, drug-free remission."),
   ],"The whitespace: durable, treatment-free remission remains unproven — the field's biggest unmet goal."),
 ],"No therapy yet delivers durable drug-free remission; this is the field's aspirational frontier, sparsely populated and high-risk.","--s7","right"),
]

# --- standard-of-care treatment ladder (line of therapy; AAD-NPF) ---
# (tier index, short label, typical agents, positioning, colorVar) — escalates left->right
SOC=[
 (1,"Topical therapy","Corticosteroids · vit-D analogs · tapinarof · roflumilast","First line for mild / localised disease (~80% of patients). Steroid-sparing non-steroidals now extend to face, folds and scalp.","--s4"),
 (2,"Phototherapy","NB-UVB · excimer · PUVA","Moderate disease or topical-refractory; office- or home-based. Safe in pregnancy; limited by access and time burden.","--s6"),
 (3,"Conventional systemics","Methotrexate · cyclosporine · acitretin","Moderate-to-severe; low-cost and widely used globally. Requires organ-toxicity monitoring; cyclosporine for short bursts.","--s8"),
 (4,"Advanced oral","Apremilast (PDE4) · deucravacitinib (TYK2) · icotrokinra (IL-23R)","Oral targeted therapy — the fastest-growing tier; increasingly a first-line systemic choice for oral-preferring patients.","--s3"),
 (5,"Biologics","IL-23 · IL-17 · IL-12/23 · TNF","Moderate-to-severe; the deepest, most durable clearance (PASI 90–100). IL-23 and IL-17 are the modern anchors.","--s1"),
]
SOC_NOTE="Escalation is not strictly stepwise — moderate-to-severe patients increasingly start advanced oral or biologic therapy directly. Basis: AAD-NPF guidelines of care."

# --- glossary (key terms) ---
GLOSSARY=[
 ("PASI","Psoriasis Area and Severity Index — composite 0–72 score of erythema, induration and scaling weighted by body-region area."),
 ("PASI 90 / 100","Share of patients reaching ≥90% / 100% improvement in PASI from baseline — the modern efficacy bar (PASI 75 was the older standard)."),
 ("BSA","Body Surface Area involved (%); ≥10% (or special sites) marks moderate-to-severe disease."),
 ("DLQI","Dermatology Life Quality Index (0–30) — patient-reported quality-of-life impact; 0/1 means no effect on life."),
 ("IL-23","Dendritic-cell cytokine (p19 + p40 subunits) that sustains pathogenic Th17 cells — the most disease-specific target."),
 ("IL-17A / IL-17F","Th17 effector cytokines acting on keratinocytes; blocking them gives the fastest, deepest skin clearance."),
 ("Th17 cell","IL-23-dependent T-helper subset that produces IL-17 and IL-22."),
 ("TYK2","Intracellular pseudokinase that transduces IL-23 signalling; oral allosteric inhibition (deucravacitinib) avoids the JAK boxed warning."),
 ("JAK–STAT","Kinase→transcription-factor relay beneath cytokine receptors; STAT3 switches on the Th17 programme."),
 ("RORγt","Master transcription factor of Th17 identity; an emerging small-molecule target."),
 ("Biologic","Engineered protein (usually a monoclonal antibody) that neutralises a specific cytokine or receptor; injectable."),
 ("Biosimilar","Highly similar copy of an off-patent biologic; launches drive steep price competition (Humira, Stelara)."),
 ("p19 / p40","IL-23-specific (p19) vs IL-12/23-shared (p40) subunits; selective p19 blockade proved more effective than p40."),
 ("NMA","Network meta-analysis — pools many trials to rank therapies never tested head-to-head (e.g. Armstrong 2020)."),
 ("Drug survival","Real-world persistence: how long patients stay on a therapy before switching/stopping — a durability proxy."),
 ("PsA","Psoriatic arthritis — inflammatory joint disease developing in ~30% of psoriasis patients."),
 ("NB-UVB","Narrow-band ultraviolet-B phototherapy."),
 ("Loss of exclusivity","Patent expiry that opens a product to generic or biosimilar competition."),
]

# --- landmark pivotal trials (milestones) ---
# (trial, asset, family_key, year, phase, headline result, source_id)
TRIALS=[
 ("ERASURE / FIXTURE","secukinumab","il17",2014,"Ph3","First IL-17A pivotal; PASI 90 ~59%, superior to etanercept.","erasure"),
 ("AMAGINE-1/2/3","brodalumab","il17",2015,"Ph3","IL-17RA blockade; very high clearance; a boxed warning later shaped uptake.","armstrong"),
 ("UNCOVER-1/2/3","ixekizumab","il17",2016,"Ph3","PASI 90 ~68–71% — among the fastest, deepest responders of its era.","uncover"),
 ("VOYAGE 1/2","guselkumab","il23",2017,"Ph3","IL-23 p19; PASI 90 ~73% at wk16, superior to adalimumab.","voyage"),
 ("reSURFACE 1/2","tildrakizumab","il23",2017,"Ph3","IL-23 p19; established q12w dosing; PASI 90 ~35–39%.","armstrong"),
 ("UltIMMa-1/2","risankizumab","il23",2018,"Ph3","PASI 90 ~75%, superior to ustekinumab — set the IL-23 benchmark.","ultimma"),
 ("ECLIPSE","guselkumab","il23",2019,"Ph3","Head-to-head win: guselkumab beat secukinumab on wk-48 PASI 90 (durability).","eclipse"),
 ("BE VIVID / BE READY / BE SURE","bimekizumab","il17",2021,"Ph3","Dual IL-17A/F; PASI 100 ~60% — the deepest-clearance benchmark to date.","bevivid"),
 ("POETYK PSO-1/2","deucravacitinib","kinase",2022,"Ph3","First oral TYK2; PASI 75 ~58% vs apremilast ~35% — opened the oral-targeted era.","poetyk"),
 ("Zasocitinib Ph3 (TAK-279)","zasocitinib","kinase",2025,"Ph3","Next-gen oral TYK2: >50% PASI 90 — raising the oral efficacy bar.","takeda_zaso"),
 ("ICONIC-LEAD","icotrokinra","il23",2025,"Ph3","First oral IL-23R peptide; positioned as a first-line systemic.","iconic"),
]

# --- trials in focus: the most strategically important programmes, with detail (CT.gov-style fields) ---
# granular endpoint/eligibility/site data would be pulled live from ClinicalTrials.gov v2 by NCT id.
TRIALS_FOCUS=[
 {"name":"ICONIC-LEAD","drug":"icotrokinra","fam":"il23","sponsor":"Johnson & Johnson","phase":"Phase 3","status":"Reported → FDA-approved (2026)",
  "endpoints":["IGA 0/1 at Week 16 vs placebo (co-primary)","PASI 90 at Week 16 vs placebo (co-primary)"],
  "readout":"Positive topline (2025): ~65% IGA 0/1 and ~50–65% PASI 90 at Week 16 — first oral to approach injectable IL-23 efficacy.",
  "start":"2023","end":"2025","inclusion":"Adults & adolescents ≥12 y; moderate-to-severe plaque psoriasis; candidate for systemic therapy or phototherapy.",
  "sites":"Global, multi-country (part of the 6-study ICONIC Phase 3 programme)","kols":"Industry-sponsored; site investigators listed on ClinicalTrials.gov",
  "significance":"Category-defining first-line ORAL IL-23R peptide — the pill that rivals a biologic."},
 {"name":"Zasocitinib Phase 3 (TAK-279)","drug":"zasocitinib","fam":"kinase","sponsor":"Takeda","phase":"Phase 3","status":"Positive topline (Dec 2025); filing expected",
  "endpoints":["PASI 90 at Week 16 vs placebo","sPGA 0/1 at Week 16 vs placebo"],
  "readout":">50% PASI 90 and ~30% PASI 100 at Week 16 — best-in-class oral efficacy for a TYK2 inhibitor.",
  "start":"2024","end":"2025","inclusion":"Adults ≥18 y; moderate-to-severe plaque psoriasis (BSA ≥10%, PASI ≥12, sPGA ≥3).",
  "sites":"Global multi-country Phase 3 (two pivotal studies)","kols":"Industry-sponsored; site investigators on ClinicalTrials.gov",
  "significance":"Next-gen oral TYK2 raising the oral bar toward biologic-level clearance."},
 {"name":"ONWARD (ESK-001)","drug":"ESK-001","fam":"kinase","sponsor":"Alumis","phase":"Phase 3","status":"Positive topline (2026)",
  "endpoints":["PASI 75 at Week 16","PASI 90 / sPGA 0/1 at Week 16"],
  "readout":"~74% PASI 75 at Week 16; NDA planned H2 2026 — a competitive oral TYK2.",
  "start":"2024","end":"2026","inclusion":"Adults ≥18 y; moderate-to-severe plaque psoriasis; systemic-therapy candidate.",
  "sites":"Global Phase 3 (ONWARD programme)","kols":"Industry-sponsored; site investigators on ClinicalTrials.gov",
  "significance":"BID oral TYK2 competing on depth and durability with deucravacitinib and zasocitinib."},
 {"name":"BE VIVID / BE RADIANT (bimekizumab)","drug":"bimekizumab","fam":"il17","sponsor":"UCB","phase":"Phase 3 + long-term","status":"Approved; durability data maturing",
  "endpoints":["PASI 100 at Week 16","Maintenance of PASI 100 through Week 48–144"],
  "readout":"~60% PASI 100 at Week 16 with high maintenance — the deepest, most durable clearance to date.",
  "start":"2018","end":"ongoing OLE","inclusion":"Adults ≥18 y; moderate-to-severe plaque psoriasis.",
  "sites":"Global; BE-series pivotal trials + open-label extensions","kols":"Reich, Warren, Gordon (pivotal lead authors)",
  "significance":"Sets the PASI 100 ceiling — the efficacy benchmark competitors are measured against."},
 {"name":"Sonelokimab Phase 2 (M-1095 / MIRA)","drug":"sonelokimab","fam":"il17","sponsor":"MoonLake Immunotherapeutics","phase":"Phase 2","status":"PsO Ph2 positive; sponsor prioritising HS",
  "endpoints":["PASI 90 at Week 12","IGA 0/1 at Week 12"],
  "readout":"~80% PASI 90 in Ph2 with a small IL-17A/F Nanobody; PsO development deprioritised in favour of hidradenitis.",
  "start":"2021","end":"2023","inclusion":"Adults; moderate-to-severe plaque psoriasis.",
  "sites":"Multi-country Phase 2","kols":"Industry-sponsored; investigators on ClinicalTrials.gov",
  "significance":"Nanobody format tests whether a small IL-17A/F protein can match mAbs — a platform bet."},
 {"name":"POETYK PSO long-term extension","drug":"deucravacitinib","fam":"kinase","sponsor":"Bristol Myers Squibb","phase":"Phase 3 LTE","status":"Ongoing (≥4-year data)",
  "endpoints":["Maintenance of PASI 75 / sPGA 0/1 over time","Long-term safety (no JAK-class signal)"],
  "readout":"Durable response and a clean multi-year safety profile — supporting first-oral-TYK2 positioning.",
  "start":"2019","end":"ongoing","inclusion":"POETYK PSO-1/-2 completers; moderate-to-severe plaque psoriasis.",
  "sites":"Global long-term extension","kols":"Armstrong, Warren, Blauvelt (pivotal lead authors)",
  "significance":"Durability + safety are the oral-TYK2 differentiator versus classic JAK inhibitors."},
]
TRIALS_FOCUS_NOTE="The most strategically important programmes. Endpoints, eligibility, sites and dates would be pulled live from ClinicalTrials.gov (API v2) by NCT id; figures here are curated from cited toplines. Named KOLs are pivotal-trial lead authors; industry site investigators are listed on ClinicalTrials.gov."

# --- deeper burden / comorbidity / economics ---
EPI_DEEP={
 "dlqi":"Mean DLQI ~8–12 in moderate-to-severe disease — a large quality-of-life impact, comparable to that of cancer or heart disease.",
 "economic":"US direct + indirect burden estimated >$100B/yr, roughly half from lost work productivity and comorbidity care.",
 "drug_survival":"Real-world persistence is highest for IL-23 inhibitors (~1-yr drug survival ~85–90%) and lowest for TNF inhibitors — a key durability differentiator beyond trial PASI.",
 "comorbid":[("Psoriatic arthritis","~30%"),("Metabolic syndrome","~40%"),("Cardiovascular / MACE","elevated"),("Depression / anxiety","~20%"),("IBD (Crohn's / UC)","elevated")],
 "mortality":"Not directly fatal, but severe psoriasis carries excess cardiovascular mortality — the basis for treat-to-target inflammation control.",
}
# --- market share by mechanism class (directional; branded systemic/biologic market) ---
MARKET_SHARE=[
 ("IL-23 p19","Largest & growing","--s1"),
 ("IL-17A / A-F","Large, stable","--s2"),
 ("TNF (incl. biosimilar)","Large but eroding","--s5"),
 ("IL-12/23 (p40)","Shrinking — biosimilars","--sN"),
 ("Oral advanced (TYK2/PDE4/IL-23R)","Small, fastest-growing","--s3"),
]
MARKET_NOTE="Directional shares of the branded systemic/biologic market — illustrative, not audited. IL-23 & IL-17 lead; oral targeted therapy is the fastest-growing slice."

# --- PASI-90 response kinetics by class (the psoriasis analog of RA Capital's PK curves) ---
PASI_KINETICS={"weeks":[0,4,8,12,16],
 "note":"Class-representative PASI-90 trajectories (NMA / onset-of-action-informed; illustrative). IL-17 acts fastest and deepest; IL-23 p19 climbs more slowly but is durable; oral agents plateau lower.",
 "series":[
  {"label":"IL-17 (A / A-F)","colorVar":"--s2","pts":[0,45,72,80,83]},
  {"label":"IL-23 p19","colorVar":"--s1","pts":[0,12,40,63,75]},
  {"label":"TNF-α","colorVar":"--s5","pts":[0,8,25,40,46]},
  {"label":"Oral TYK2","colorVar":"--s3","pts":[0,10,26,33,36]},
  {"label":"Oral PDE4","colorVar":"--s7","pts":[0,5,12,16,19]},
 ]}

nodes={}; edges=[]
def node(nid,ntype,label,attrs=None,sources=None):
    nodes[nid]={"id":nid,"type":ntype,"label":label,"attrs":attrs or {},"sources":sources or []}; return nid
def edge(t,s,tg,a=None): edges.append({"type":t,"source":s,"target":tg,"attrs":a or {}})

IND=node("ind:plaque-psoriasis","Indication","Plaque psoriasis",{"area":"Immuno-dermatology"})
# family (MoAClass) nodes
for k,(label,col,order) in FAM.items():
    node("moa:"+k,"MoAClass",label,{"family_key":k,"colorVar":col,"order":order,"safety":SAFETY.get(k)})

comp_ids={}
def company(name):
    if not name: return None
    if name in comp_ids: return comp_ids[name]
    return comp_ids.setdefault(name,node("company:"+slug(name),"Company",name,{"type":"company"}))

seg=[node("seg:mild","MarketSegment","Mild (topical-managed)",{"share_pct":80}),
     node("seg:modsev","MarketSegment","Moderate-to-severe (systemic-eligible)",{"share_pct":20})]

# public drug detail (openFDA + ChEMBL, optionally PubChem) from fetch_drug_detail.py, if present
try: DETAIL=json.load(open(os.path.join(HERE,"drug_detail.json"),encoding="utf-8"))
except Exception: DETAIL={}
for d in ROSTER:
    did="drug:"+slug(d["name"])
    attrs={k:d[k] for k in ("brand","sub","route","dose","appr","sales","syr","bios","combo","disc","p75","p90","p100","note","mod") if d.get(k) is not None}
    attrs["highest_phase"]=d["phase"]; attrs["phase_num"]=PHASE_NUM[d["phase"]]
    attrs["modality"]=d["mod"]; attrs["moa_family"]=FAM[d["fam"]][0]; attrs["sub_class"]=d["sub"]
    if d.get("sales"): attrs["annual_sales_usd_m"]=d["sales"]; attrs["sales_year"]=d.get("syr")
    if slug(d["name"]) in DETAIL: attrs["detail"]=DETAIL[slug(d["name"])]
    src=["ot"]
    if d.get("appr"): src.append("fda")
    if d.get("sales"): src.append(COMP_SALES_SRC.get(d["company"],"xtalks"))
    node(did,"Drug",d["name"],attrs,src)
    edge("DEVELOPED_BY",did,company(d["company"]))
    edge("HAS_MECHANISM",did,"moa:"+d["fam"])
    edge("DEVELOPED_IN",did,IND,{"phase":d["phase"],"approved":d["phase"]=="approved"})
    if d.get("target") and re.match(r"^[A-Za-z0-9]+$",d["target"]):
        edge("HITS",did,node("target:"+d["target"],"Target",d["target"],{}))
    mod=d["mod"]; edge("HAS_MODALITY",did,node("modality:"+slug(mod),"Modality",mod,{}))
    # SERVES: systemic/biologic -> mod-sev; topical/conventional -> mild (+ mod-sev for conv)
    if d["fam"] in ("topical","steroid"): edge("SERVES",did,"seg:mild")
    elif d["fam"]=="conv": edge("SERVES",did,"seg:mild"); edge("SERVES",did,"seg:modsev")
    else: edge("SERVES",did,"seg:modsev")

# associated-target scores (live OT)
OT={"IL12B":0.74,"TYK2":0.71,"IL23A":0.64,"TNF":0.61,"PDE4":0.61,"NR3C1":0.60,"VDR":0.60,"IL17A":0.60,"IL17RA":0.58,"IL23R":0.55,"AHR":0.45}
for tid,n in nodes.items():
    if n["type"]=="Target" and n["label"] in OT: n["attrs"]["ot_association_score"]=OT[n["label"]]

# catalysts (dated) -> nodes + HAS_CATALYST edges to the affected drug
for i,(date,event,kind,comp,asset,sig,src) in enumerate(CAT,1):
    cid=node(f"catalyst:c{i}","Catalyst",event,{"date":date,"kind":kind,"significance":sig,"company":comp},[src])
    did="drug:"+slug(asset)
    if did in nodes: edge("HAS_CATALYST",did,cid)

# deals (deal-flow) -> Deal nodes + PARTY_TO (acquirer) + INVOLVES (asset)
for i,(acq,cp,asset,val,date,cat,stg,note) in enumerate(DEALS,1):
    yr=int(str(date)[:4])
    dl=node(f"deal:d{i}","Deal",f"{acq} ← {cp}",{"value":val,"year":yr,"date":date,"category":cat,"stage":stg,"kind":cat,"note":note,"counterparty":cp,"acquirer":acq,"asset":asset})
    a=company(acq)
    if a: edge("PARTY_TO",a,dl,{"role":"acquirer"})
    dr="drug:"+slug(asset)
    if dr in nodes: edge("INVOLVES",dl,dr)

# biology of the cascade -> Biology nodes + cascade edges + bridges to targets/mechanisms
for suf,label,kind,pos,desc in BIO:
    node("bio:"+suf,"Biology",label,{"kind":kind,"pos":pos,"description":desc})
for suf,label,kind,desc in SIGNAL:  # intracellular signalling depth (no schematic pos)
    node("bio:"+suf,"Biology",label,{"kind":kind,"description":desc})
for et,a,b in CASCADE+SIGNAL_EDGES:
    edge(et,"bio:"+a,"bio:"+b)
for sym,bio in TARGET_BIO.items():
    if "target:"+sym in nodes: edge("PART_OF","target:"+sym,"bio:"+bio)
for fk,pos in ANCHOR.items():
    if "moa:"+fk in nodes and "bio:"+pos in nodes: edge("ACTS_ON","moa:"+fk,"bio:"+pos)
EPI.update(EPI_DEEP)

# ---- market-research layer ingested from the therapeutic-area research report ----
# report_data.json is produced by ingest_report.py (the "ingest" seam of the two-skill split:
# a research skill emits the report model; ingest_report.py normalizes it; the atlas renders it).
try: REPORT=json.load(open(os.path.join(HERE,"report_data.json"),encoding="utf-8"))
except Exception: REPORT={}
# bind forecast segments to the atlas family palette so the same class reads the same colour everywhere
SEG_COLOR={"il23":"--s1","il17":"--s2","oral":"--s3","tnf":"--s5","topical":"--s4","total":"--ink2","other":"--s6"}
for _s in REPORT.get("segments",[]): _s["colorVar"]=SEG_COLOR.get(_s.get("key"),"--s6")
if REPORT.get("total"): REPORT["total"]["colorVar"]="--ink"
# psoriasis-attributed franchise total captured across dashboard brands (fixes the all-indication caveat)
_ATTR_TOTAL=round(sum(a.get("attr_val") or 0 for a in REPORT.get("attribution",[])),1)

graph={"meta":{"scope":"indication","focus":"Plaque psoriasis","generated":"2026-07-23","as_of":"July 2026",
    "one_liner":"Chronic IL-23/IL-17-driven skin disease; a mature, biologics-led market — the competitive question has shifted from clearing skin to reaching the patient first, at what net price.",
    "sales_note":"Franchise-sales donut is company-reported FY2025 totals across ALL indications. The dedicated attribution region below estimates the psoriasis-only split. PASI figures are cross-trial (NMA-anchored) unless a head-to-head is noted.",
    "headline_stats":[
      {"label":"Global prevalence (GBD 2021)","value":"43M"},{"label":"US systemic-eligible","value":"~1.6M"},
      {"label":"Global market (2026)","value":"~$32B"},{"label":"Forecast 2031 · base","value":"$46.5B"}]},
    "families":[{"key":k,"label":l,"colorVar":c,"order":o,"anchor":ANCHOR.get(k,"tcell")} for k,(l,c,o) in FAM.items()],
    "epi":EPI,
    "sites":[{"site":s,"prev":p,"note":n} for s,p,n in SITES],
    "deals":[{"acquirer":a,"counterparty":cp,"asset":asset,"value":v,"date":dt,"year":int(str(dt)[:4]),"category":cat,"stage":stg,"note":nt} for a,cp,asset,v,dt,cat,stg,nt in DEALS],
    "soc":[{"tier":t,"label":l,"agents":a,"note":n,"colorVar":c} for t,l,a,n,c in SOC],
    "soc_note":SOC_NOTE,
    "glossary":[{"term":t,"def":d} for t,d in GLOSSARY],
    "trials":[{"trial":tr,"asset":a,"family_key":fk,"year":y,"phase":ph,"result":r,"src":s} for tr,a,fk,y,ph,r,s in TRIALS],
    "trials_focus":TRIALS_FOCUS,
    "trials_focus_note":TRIALS_FOCUS_NOTE,
    "market_share":[{"cls":c,"trend":t,"colorVar":cv} for c,t,cv in MARKET_SHARE],
    "market_note":MARKET_NOTE,
    "pasi_kinetics":PASI_KINETICS,
    "signal_path":[{"from":"bio:"+f,"to":"bio:"+t,"label":l} for f,t,l in SIGNAL_PATH],
    "hierarchy":HIER,
    # ---- ingested market-research layer (from report_data.json via ingest_report.py) ----
    "forecast":{"years":REPORT.get("years",[]),"segments":REPORT.get("segments",[]),
                "total":REPORT.get("total"),"note":REPORT.get("note","")},
    "scenarios":REPORT.get("scenarios",[]),
    "geo":REPORT.get("geo",[]),
    "funnel":REPORT.get("funnel",[]),
    "segmentation":REPORT.get("segmentation",[]),
    "opportunity":REPORT.get("opportunity",[]),
    "payers":REPORT.get("payers",[]),
    "attribution":REPORT.get("attribution",[]),
    "attribution_total":_ATTR_TOTAL,
    "loe":REPORT.get("loe",[]),
    "competitive":REPORT.get("competitive",[]),
    "catalysts_watch":REPORT.get("catalysts_watch",[]),
    "risks":REPORT.get("risks",[]),
    "thesis":REPORT.get("thesis",[]),
    "report_meta":REPORT.get("meta",{}),
    "report_sources":REPORT.get("sources",[]),
    "nodes":list(nodes.values()),"edges":edges,"sources":SOURCES}

# --- validate the mind-map covers every asset exactly once ---
def _leafdrugs(n,acc):
    if n.get("drugs"): acc.extend(n["drugs"])
    for c in n.get("ch",[]): _leafdrugs(c,acc)
_hd=[]; [ _leafdrugs(o,_hd) for o in HIER ]
_roster=[d["name"] for d in ROSTER]
_missing=[n for n in _roster if n not in _hd]
_unknown=[n for n in _hd if n not in _roster]
from collections import Counter as _C
_dupes=[n for n,c in _C(_hd).items() if c>1]
print("hierarchy: %d leaves place %d assets (roster %d) | missing=%s unknown=%s dupes=%s"%(
    sum(1 for _ in _hd), len(set(_hd)), len(_roster), _missing or "none", _unknown or "none", _dupes or "none"))
json.dump(graph,open(os.path.join(HERE,"graph.json"),"w",encoding="utf-8"),indent=2,ensure_ascii=False)
from collections import Counter
print("assets:",len(ROSTER)," nodes:",len(nodes),dict(Counter(n["type"] for n in nodes.values())))
print("phases:",dict(Counter(d["phase"] for d in ROSTER)))
print("families:",dict(Counter(d["fam"] for d in ROSTER)))
