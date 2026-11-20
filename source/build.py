#!/usr/bin/env python3
"""Build Minotaur Web and Claude variants from one source.

Usage: python3 build.py <version>
Inputs: src/app.html, data.json, icon.svg, vendor/{leaflet.css,topojson-client.min.js,countries-50m.json}
Outputs: build/Minotaur-Web-v<V>.html, build/Minotaur-Claude-v<V>.html, build/seed/*.json
"""
import json, re, sys, pathlib

V = sys.argv[1] if len(sys.argv) > 1 else "0.0"
root = pathlib.Path(__file__).parent
src = (root / "src/app.html").read_text()
data = json.loads((root / "data.json").read_text())
lcss = (root / "vendor/leaflet.css").read_text()
tj = (root / "vendor/topojson-client.min.js").read_text()
topo = (root / "vendor/countries-50m.json").read_text()
SITE = "https://invisory.uk/minotaur/"
DESC = ("Minotaur: ASX, TSX and TSXV gold, silver, copper and rare earth explorers and developers, "
        "with stage, valuation, funding, project maps, drill strikes and news.")


def common(s):
    s = s.replace("/*__LEAFLETCSS__*/\n", lcss).replace("/*__LEAFLETCSS__*/", lcss)
    s = s.replace("/*__TOPOJSON__*/\n", tj).replace("/*__TOPOJSON__*/", tj)
    s = s.replace("/*__WORLD__*/", "const WORLD_TOPO=" + topo)  # src carries the ";" on the next line
    return s


# ---- Web build (invisory.uk): full document, embedded snapshot, icons + link preview in <head>
web = common(src)
web = web.replace("/*__BUILD__*/", 'const BUILD="web";')
web = web.replace("/*__DATA__*/", "const SNAPSHOT=" + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";")
web = web.replace("\n<!--__HEADEXTRA__-->", "").replace("<!--__HEADEXTRA__-->", "")

# Move everything before the app header (title, meta, font links, styles) into <head>
cut = web.index('<header class="top">')
head_part, body_part = web[:cut], web[cut:]
icons = ('<link rel="icon" type="image/png" sizes="32x32" href="favicon-32.png?v=3">'
         '<link rel="icon" type="image/png" sizes="16x16" href="favicon-16.png?v=3">'
         '<link rel="icon" type="image/png" sizes="192x192" href="favicon-192.png?v=3">'
         '<link rel="shortcut icon" href="favicon.ico?v=3">'
         '<link rel="apple-touch-icon" href="apple-touch-icon.png?v=3">'
         '<meta name="apple-mobile-web-app-title" content="Minotaur">'
         '<meta name="theme-color" content="#0E2033">')
og = ('<link rel="canonical" href="' + SITE + '">'
      '<meta property="og:type" content="website"><meta property="og:site_name" content="Invisory">'
      '<meta property="og:title" content="Minotaur — mining juniors tracker">'
      '<meta property="og:description" content="Gold, silver, copper and rare-earth juniors on the ASX, TSX and TSXV: '
      'global project map, stage, P/NPV, funding, drill strikes and news.">'
      '<meta property="og:url" content="' + SITE + '">'
      '<meta property="og:image" content="' + SITE + 'og-image.png?v=3"><meta property="og:image:type" content="image/png">'
      '<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">'
      '<meta property="og:image:alt" content="Minotaur: world map of tracked gold, silver, copper and rare-earth projects">'
      '<meta name="twitter:card" content="summary_large_image">'
      '<meta name="twitter:image" content="' + SITE + 'og-image.png?v=3">')
web = ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
       '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
       '<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}'
       '[hidden]{display:none!important}img{max-width:100%}</style>'
       + icons + og + "\n" + head_part.strip() + "\n</head><body>\n" + body_part.rstrip() + "\n</body></html>\n")

# ---- Claude build: the artifact service adds its own skeleton; data comes from the db store
cl = common(src)
cl = cl.replace("/*__BUILD__*/", 'const BUILD="claude";')
cl = cl.replace("/*__DATA__*/", "const SNAPSHOT=null;")
cl = cl.replace("\n<!--__HEADEXTRA__-->", "").replace("<!--__HEADEXTRA__-->", "")

out = root / "build"; out.mkdir(exist_ok=True)
(out / f"Minotaur-Web-v{V}.html").write_text(web)
(out / f"Minotaur-Claude-v{V}.html").write_text(cl)
seed = out / "seed"; seed.mkdir(exist_ok=True)
for st in data["stocks"]:
    (seed / f"{st['id']}.json").write_text(json.dumps(st, ensure_ascii=False))
for f in (out / f"Minotaur-Web-v{V}.html", out / f"Minotaur-Claude-v{V}.html"):
    print(f.name, f.stat().st_size)
