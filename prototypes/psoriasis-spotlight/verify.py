#!/usr/bin/env python3
"""Headless verification of the psoriasis atlas: JS errors, schematic clicks, 2-hop, network, path-finding."""
import glob, os, sys, json
from playwright.sync_api import sync_playwright

H = os.path.dirname(os.path.abspath(__file__))
URL = "file://" + os.path.join(H, "index.html")
EXE = sorted(glob.glob("/opt/pw-browsers/chromium*/chrome-linux/chrome"))[-1]
errors = []

def shot(page, name):
    page.screenshot(path=os.path.join(H, name))
    print("  screenshot:", name)

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=EXE, args=["--no-sandbox"])
    pg = b.new_page(viewport={"width": 1680, "height": 1000}, device_scale_factor=2)
    pg.on("console", lambda m: errors.append("console." + m.type + ": " + m.text) if m.type in ("error", "warning") else None)
    pg.on("pageerror", lambda e: errors.append("pageerror: " + str(e)))
    pg.goto(URL, wait_until="networkidle")
    pg.wait_for_timeout(600)

    # 1) poster loads, counts
    counts = pg.evaluate("({nodes:G.nodes.length, bio:G.nodes.filter(n=>n.type=='Biology').length, edges:G.edges.length, wires:document.querySelectorAll('#wires path').length, blocks:document.querySelectorAll('.block').length})")
    print("1) poster:", counts)
    shot(pg, "preview_poster.png")

    # 2) click a Biology cell (dendritic cell) -> modal shows scientific description
    pg.evaluate("openModal('bio:dc')")
    pg.wait_for_timeout(400)
    dc = pg.evaluate("({on:document.getElementById('backdrop').classList.contains('on'), title:document.querySelector('.mhead h2')?.textContent, tt:document.querySelector('.mhead .tt')?.textContent, desc:(document.querySelector('.minfo .desc')?.textContent||'').slice(0,70), neigh:document.querySelectorAll('.gholder svg g').length})")
    print("2) dendritic-cell modal:", dc)
    shot(pg, "preview_bio_cell.png")

    # 3) 2-hop toggle in the modal
    pg.evaluate("""document.querySelectorAll('.gtools .gt').forEach(b=>{if(b.textContent.includes('2-hop'))b.click();})""")
    pg.wait_for_timeout(400)
    hop = pg.evaluate("({groups:document.querySelectorAll('.gholder svg g').length, edges:document.querySelectorAll('.gholder svg line').length})")
    print("3) 2-hop expanded:", hop)
    shot(pg, "preview_2hop.png")

    # 4) close, open a drug modal (risankizumab) and check biology reachability in its info
    pg.evaluate("document.getElementById('backdrop').classList.remove('on')")
    pg.evaluate("openModal('bio:il23')")
    pg.wait_for_timeout(300)
    il23 = pg.evaluate("({title:document.querySelector('.mhead h2')?.textContent, drugs:(document.querySelector('.minfo .desc')?.textContent||'').includes('Engaged by')})")
    print("4) IL-23 cytokine modal engaged-by:", il23)
    pg.evaluate("document.getElementById('backdrop').classList.remove('on')")

    # 5) network view: toggle + expand a node
    pg.evaluate("setView('network','moa:il23')")
    pg.wait_for_timeout(500)
    net0 = pg.evaluate("({nodes:netNodes.length, links:netLinks.length, view:VIEW})")
    pg.evaluate("expand(netNodes[1] && netNodes[1].id)")
    pg.wait_for_timeout(1400)  # let the sim settle
    net1 = pg.evaluate("({nodes:netNodes.length, links:netLinks.length, svgnodes:document.querySelectorAll('#net g').length})")
    print("5) network seed:", net0, "after expand:", net1)
    shot(pg, "preview_network.png")

    # 6) path-finding: risankizumab -> keratinocyte
    pg.evaluate("setView('poster')")
    pg.fill("#pin1", "risankizumab")
    pg.fill("#pin2", "keratinocyte")
    pg.click("#ptrace")
    pg.wait_for_timeout(1400)
    path = pg.evaluate("({view:VIEW, ribbon:(document.getElementById('ribbon').textContent||'').slice(0,160), hl:netNodes.filter(n=>hlNodes.has(n.id)).length, links:netLinks.filter(l=>l.hl).length})")
    print("6) path risankizumab->keratinocyte:", path)
    shot(pg, "preview_path.png")

    # 7) another path: secukinumab -> dendritic cell
    pg.evaluate("setView('poster')")
    pg.fill("#pin1", "secukinumab")
    pg.fill("#pin2", "Dendritic cell")
    pg.click("#ptrace")
    pg.wait_for_timeout(1200)
    path2 = pg.evaluate("({ribbon:(document.getElementById('ribbon').textContent||'').slice(0,180)})")
    print("7) path secukinumab->dendritic:", path2)

    b.close()

print("\n=== JS errors/warnings:", len(errors), "===")
for e in errors[:40]:
    print("  ", e)
sys.exit(1 if any("pageerror" in e or "console.error" in e for e in errors) else 0)
