#!/usr/bin/env python3
"""polish_atlas.py — the layout POLISH harness (input side of the LLM polish pass).

Renders a built atlas headless and emits a machine-readable layout manifest + a screenshot that a
polish agent reasons over. The agent returns layout overrides (region-id → {x,y,w}) written to
`<atlas>.overrides.json`; re-running build_atlas.py applies them (see the OVERRIDES hook in the
template). This is the "LLM polish" half of the deterministic-engine + LLM-polish layout design:
the deterministic engine (layoutAdapt) sizes and flows; the agent fills the residual, context-
dependent blank space a rule can't judge.

    python polish_atlas.py runs/<slug>/atlas.json --html atlas.html \
           --manifest runs/<slug>/layout_manifest.json --shot runs/<slug>/layout.png

Manifest: { canvas:{w,h}, fill_ratio, regions:[{id,x,y,w,h}], blanks:[{x,y,w,h,area_pct}] }.
Stdlib + Playwright only. No LLM is invoked here — this produces the agent's inputs.
"""
import argparse, glob, json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))

MANIFEST_JS = r"""(()=>{
  const CWv=CANVAS.offsetWidth, CHv=(ADAPT_CH||CANVAS.offsetHeight);
  const named=[...CANVAS.querySelectorAll('[data-region]')];
  const regions=named.map(n=>({id:n.getAttribute('data-region'),
    x:n.offsetLeft, y:n.offsetTop, w:n.offsetWidth, h:n.offsetHeight}));
  // occupancy grid over the whole canvas (coarse), then find the N largest empty rectangles
  const boxes=[...CANVAS.querySelectorAll('.panel,.hnode,.node,.mast,.maphead,.clusterlabel,.secband')].map(n=>{
    let x=n.offsetLeft,y=n.offsetTop,w=n.offsetWidth,h=n.offsetHeight;
    if(n.classList.contains('hnode'))y-=h/2; return [x,y,w,h];});
  let area=0; boxes.forEach(([x,y,w,h])=>area+=w*h);
  const fill=+(area/(CWv*CHv)).toFixed(3);
  const GX=48, cell=CWv/GX, rows=Math.ceil(CHv/cell);
  const grid=Array.from({length:rows},()=>new Array(GX).fill(0));
  boxes.forEach(([x,y,w,h])=>{const c0=Math.max(0,(x/cell)|0),c1=Math.min(GX-1,((x+w)/cell)|0),
    r0=Math.max(0,(y/cell)|0),r1=Math.min(rows-1,((y+h)/cell)|0);
    for(let r=r0;r<=r1;r++)for(let c=c0;c<=c1;c++)grid[r][c]=1;});
  function largest(g){let best=[0,0,0,0,0];const hist=new Array(GX).fill(0);
    for(let r=0;r<g.length;r++){for(let c=0;c<GX;c++)hist[c]=g[r][c]?0:hist[c]+1;
      const st=[];for(let c=0;c<=GX;c++){const hgt=c<GX?hist[c]:0;let start=c;
        while(st.length&&st[st.length-1][1]>=hgt){const[si,sh]=st.pop();const a=sh*(c-si);
          if(a>best[0])best=[a,si,r-sh+1,c-si,sh];start=si;}st.push([start,hgt]);}}
    return best;}
  const blanks=[];
  for(let k=0;k<3;k++){const[a,c,r,cw,ch]=largest(grid);if(a< (GX*rows*0.02))break;
    blanks.push({x:Math.round(c*cell),y:Math.round(r*cell),w:Math.round(cw*cell),h:Math.round(ch*cell),
      area_pct:Math.round(a/(GX*rows)*100)});
    for(let rr=r;rr<r+ch;rr++)for(let cc=c;cc<c+cw;cc++)grid[rr][cc]=1;}  // mask & find next
  return {canvas:{w:CWv,h:CHv}, fill_ratio:fill, regions, blanks};
})()"""


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("atlas")
    ap.add_argument("--html", help="built HTML (else built on the fly)")
    ap.add_argument("--manifest", help="write the layout manifest JSON here")
    ap.add_argument("--shot", help="write a full-poster screenshot here")
    args = ap.parse_args()

    html = args.html
    tmp = None
    if not html:
        html = tmp = os.path.join(os.path.dirname(os.path.abspath(args.atlas)), "_polish_build.html")
        subprocess.run([sys.executable, os.path.join(HERE, "build_atlas.py"), args.atlas, "--out", html],
                       capture_output=True, text=True)

    from playwright.sync_api import sync_playwright
    exe = sorted(glob.glob("/opt/pw-browsers/chromium*/chrome-linux/chrome"))[-1]
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=exe, args=["--no-sandbox"])
        pg = b.new_page(viewport={"width": 1680, "height": 1050}, device_scale_factor=1)
        pg.goto("file://" + os.path.abspath(html), wait_until="networkidle")
        pg.wait_for_timeout(700)
        manifest = pg.evaluate(MANIFEST_JS)
        if args.shot:
            # frame the whole poster (not just the top) so the agent sees all blank space
            pg.evaluate("(()=>{const vw=innerWidth,vh=innerHeight;sc=Math.min((vw-20)/CW,(vh-20)/(ADAPT_CH||CH));"
                        "tx=Math.round((vw-CW*sc)/2);ty=10;apply();})()")
            pg.wait_for_timeout(200)
            pg.screenshot(path=args.shot)
        b.close()

    if args.manifest:
        json.dump(manifest, open(args.manifest, "w"), indent=1)
    if tmp and os.path.exists(tmp):
        os.remove(tmp)
    print("canvas %dx%d | fill %.0f%% | %d regions | blanks: %s" % (
        manifest["canvas"]["w"], manifest["canvas"]["h"], manifest["fill_ratio"] * 100,
        len(manifest["regions"]), [f"{b['w']}x{b['h']}@({b['x']},{b['y']}) {b['area_pct']}%" for b in manifest["blanks"]]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
