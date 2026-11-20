# Minotaur

Mining-juniors tracker (ASX / TSX / TSXV gold, silver, copper and rare earths), hosted at https://invisory.uk/minotaur/ and as a private Claude artifact.

## What lives here

| Path | What it is |
|---|---|
| `minotaur-data.json` | Live data feed. The scheduled Claude refresh rewrites it; the web page fetches it every time it opens. Do not move or rename it. |
| `site/` | The files that go in `public_html/minotaur/` on GoDaddy, exactly as uploaded: `index.html`, `favicon.ico`, `favicon-16.png`, `favicon-32.png`, `favicon-192.png`, `apple-touch-icon.png`, `og-image.png`. `Minotaur-Claude-v*.html` is the matching Claude-artifact build. |
| `source/src/app.html` | Single source for both builds. |
| `source/build.py` | `python3 build.py <version>` writes `build/Minotaur-Web-v<V>.html` and `build/Minotaur-Claude-v<V>.html`. |
| `source/data.json` | Data snapshot embedded in the web build (the page loads newer data from the feed when available). |
| `source/vendor/` | Leaflet CSS, topojson-client and the world-borders TopoJSON, inlined at build time. |
| `source/tools/` | Icon and link-preview generators and the browser check script (Playwright). |
| `source/screen/` | Top-100 screening scripts and research notes. |
| `source/scheduled-task/` | The prompt the scheduled refresh runs (v2.0: Wednesdays ids 0-9/A-L, Saturdays M-Z, 06:53 London). |
| `archive/` | Earlier uploaded web builds kept as delivered (v1.4, v2.0). |

## Deploying the web version

1. Upload everything in `site/` to `public_html/minotaur/` (keep the file names).
2. Clear the Sucuri cache.

## Version history

- v2.1 (20 Nov 2026): identical app and data to v2.0; restores the browser icon, home-screen icon and link-preview tags that v2.0 dropped from the page header. Source reconstructed from the live page (rebuild verified identical to v2.0's body).
- v2.0 (20 Nov 2026): 100 stocks from the re-run top-100 screen; data refresh split into two runs a week.
- v1.9 (12 Oct 2026): 19 stocks, map front page, sticky filters, favicon files.
