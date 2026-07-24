#!/usr/bin/env python3
"""qc_atlas.py — quality gate for a built atlas (data accuracy + visual correctness).

The deterministic core of the QC agent. Runs two checks and prints a report; exits non-zero on
any hard failure so it can gate delivery. An LLM-judgment pass (mislabelling, aesthetic balance,
subtle blank space) runs ON TOP of this in the skill workflow by reviewing the screenshot it saves.

    python qc_atlas.py runs/<slug>/atlas.json [--html atlas.html] [--check-links] [--shot qc.png]

DATA QC (offline): re-runs the structural validator, then checks that every nct_id looks like a real
NCT id, every source url is well-formed, and (with --check-links) that external URLs resolve (200).
VISUAL QC (headless Chromium): builds the atlas if --html not given, asserts 0 JS errors, asserts
every region whose data IS present actually rendered (else an honest empty state), measures the
canvas fill-ratio to catch large blank space, and saves a screenshot. Stdlib + Playwright only.
"""
import argparse, glob, json, os, re, subprocess, sys, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
NCT = re.compile(r"^NCT\d{8}$")
URL = re.compile(r"^https?://[^\s]+$")

# data section present in atlas.json  ->  DOM selector that must be non-empty when it is
REGION_SELECTORS = {
    "strategy_map": ".hobj", "moa_landscape": ".hmech", "standard_of_care": ".soctab",
    "glossary": ".gloss2 .g", "biology_graph": ".anchor", "response_kinetics": ".pasi svg",
    "trials_focus": ".tfocus .row",
    "market_research.forecast": ".scchip", "market_research.funnel": ".funnel .stg",
    "market_research.payers": ".payer tr", "market_research.competitive": ".comp .card",
    "market_research.opportunity": ".opp .row",
}


def get(atlas, dotted):
    cur = atlas
    for k in dotted.split("."):
        cur = (cur or {}).get(k) if isinstance(cur, dict) else None
    return cur


def data_qc(atlas, check_links):
    errs, warns = [], []
    # structural validator (reuse the researcher's)
    val = os.path.join(HERE, "..", "..", "disease-atlas", "scripts", "validate_atlas.py")
    if os.path.exists(val):
        r = subprocess.run([sys.executable, val, ARGS.atlas], capture_output=True, text=True)
        if r.returncode == 1:
            errs.append("validate_atlas.py reported errors:\n  " + r.stdout.strip().replace("\n", "\n  "))
    # nct id format
    urls = []
    for a in (get(atlas, "pipeline.assets") or []):
        for n in (a.get("nct_ids") or []):
            if not NCT.match(str(n)):
                errs.append(f"asset {a.get('name')!r} has malformed nct_id {n!r} (want NCT########)")
    for t in (get(atlas, "trials_focus.trials") or []):
        n = t.get("nct_id")
        if n and not NCT.match(str(n)):
            errs.append(f"trials_focus {t.get('name')!r} malformed nct_id {n!r}")
        if n:
            urls.append("https://clinicaltrials.gov/study/" + n)
    # source urls well-formed + collected for link-check
    for s in (atlas.get("sources") or []):
        u = s.get("url")
        if u and not URL.match(u):
            warns.append(f"source {s.get('id')!r} url looks malformed: {u!r}")
        elif u:
            urls.append(u)
    # optional live link resolution
    if check_links:
        for u in sorted(set(urls))[:60]:
            try:
                req = urllib.request.Request(u, method="HEAD", headers={"User-Agent": "atlas-qc"})
                code = urllib.request.urlopen(req, timeout=15).status
                if code >= 400:
                    errs.append(f"dead link ({code}): {u}")
            except Exception as e:
                warns.append(f"link check failed for {u}: {e}")
    return errs, warns, len(urls)


def visual_qc(atlas, html_path, shot):
    from playwright.sync_api import sync_playwright
    errs, warns = [], []
    exe = sorted(glob.glob("/opt/pw-browsers/chromium*/chrome-linux/chrome"))[-1]
    js_errors = []
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=exe, args=["--no-sandbox"])
        pg = b.new_page(viewport={"width": 1680, "height": 1050})
        pg.on("console", lambda m: js_errors.append("console.error: " + m.text) if m.type == "error" else None)
        pg.on("pageerror", lambda e: js_errors.append("pageerror: " + str(e)))
        pg.goto("file://" + os.path.abspath(html_path), wait_until="networkidle")
        pg.wait_for_timeout(700)
        # region presence for every section the data actually carries
        present = {}
        for section, sel in REGION_SELECTORS.items():
            if get(atlas, section):
                present[section] = pg.evaluate("s=>document.querySelectorAll(s).length", sel)
        for section, n in present.items():
            if not n:
                errs.append(f"data section {section!r} present in atlas.json but its region ({REGION_SELECTORS[section]}) rendered EMPTY")
        # fill ratio: content bbox area vs canvas area (catch large blank space)
        fill = pg.evaluate("""(()=>{
          const els=[...CANVAS.querySelectorAll('.panel,.hnode,.node,.mast,.clusterlabel,.secband')];
          if(!els.length) return 1;
          let area=0; els.forEach(n=>{area+=n.offsetWidth*n.offsetHeight;});
          const cw=CANVAS.offsetWidth, ch=(ADAPT_CH||CANVAS.offsetHeight);
          return area/(cw*ch);
        })()""")
        if fill < 0.20:
            warns.append(f"low canvas fill-ratio {fill:.0%} — likely large blank space (adaptive layout should be tuned)")
        js_err = list(js_errors)
        if shot:
            pg.evaluate("fit()"); pg.wait_for_timeout(200)
            pg.screenshot(path=shot)
        b.close()
    if js_err:
        errs.append(f"{len(js_err)} JS error(s): " + "; ".join(js_err[:5]))
    return errs, warns, {"regions_checked": len(REGION_SELECTORS), "fill_ratio": round(fill, 3)}


def main():
    global ARGS
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("atlas")
    ap.add_argument("--html", help="built HTML (else built on the fly)")
    ap.add_argument("--check-links", action="store_true", help="HTTP-check external URLs resolve")
    ap.add_argument("--shot", help="save a screenshot here")
    ARGS = ap.parse_args()
    atlas = json.load(open(ARGS.atlas, encoding="utf-8"))

    html = ARGS.html
    if not html:
        html = os.path.join(os.path.dirname(os.path.abspath(ARGS.atlas)), "_qc_build.html")
        subprocess.run([sys.executable, os.path.join(HERE, "build_atlas.py"), ARGS.atlas, "--out", html],
                       capture_output=True, text=True)

    de, dw, nurls = data_qc(atlas, ARGS.check_links)
    ve, vw, vstats = visual_qc(atlas, html, ARGS.shot)
    errs, warns = de + ve, dw + vw

    print("=== ATLAS QC:", (atlas.get("meta", {}) or {}).get("disease", ARGS.atlas), "===")
    print(f"  data: {nurls} external urls{' (link-checked)' if ARGS.check_links else ''} | "
          f"visual: {vstats['regions_checked']} region types, fill-ratio {vstats['fill_ratio']:.0%}")
    for w in warns:
        print("  WARN:", w)
    for e in errs:
        print("  FAIL:", e)
    print(f"\n{len(errs)} failure(s), {len(warns)} warning(s)")
    if not ARGS.html and os.path.exists(html):
        os.remove(html)
    if errs:
        print("QC FAILED — do not deliver until resolved.")
        return 1
    print("QC PASSED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
