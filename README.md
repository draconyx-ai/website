# draconyx.ai

The Draconyx website.

- `content.py`: every word on the site, the single source for `index.html`, `index.md`, `llms.txt` and the
  opinions page `/what-models-think/` (verbatim quotes from AI models' answers on the spec; `OPINIONS`).
- `build.py`: renders them into `dist/` (git-ignored). No external requests at runtime: no web fonts,
  scripts or trackers.
- `assets/`: the logo and its resized versions; `assets/github/` holds the organization avatars; `favicon.ico`
  (16, 32, 48 px) and `apple-touch-icon.png` (180 px, opaque), which `build.py` copies to the site root.
- `assets/models/`: the logos of the models quoted on the opinions page, one SVG per `OPINIONS` id, from
  [Lobe Icons](https://github.com/lobehub/lobe-icons) (MIT, licence file alongside). `build.py` inlines them.
- `make_icons.py`: regenerates those two icons (see below).
- `research-features-versus.json`: the evidence behind every cell of the comparison table.
- `indexnow.py`: after a deploy, submits the live sitemap's URLs to IndexNow.

Build and preview:

    python3 build.py
    python3 -m http.server 8765 --directory dist

Icons: `favicon.svg` is written by `build.py` (olive claws on the page's cream, from `CLAW_PATHS` and the `FAVICON_*`
colours). The ICO and the Apple touch icon are rasters of the same design, committed in `assets/`. Regenerate them only
when the design changes (needs Google Chrome on macOS; the rest is standard library):

    python3 make_icons.py

Deploy (the site is served by Caddy from `/var/www/draconyx.ai` on the `mail` host):

    rsync -a --delete dist/ mail:/tmp/draconyx-site/
    ssh mail 'sudo rsync -a --delete /tmp/draconyx-site/ /var/www/draconyx.ai/ && sudo chown -R caddy:caddy /var/www/draconyx.ai && rm -rf /tmp/draconyx-site'

After a deploy that changes the pages, tell the IndexNow search engines (Bing, Yandex, Seznam, Naver, Yep and
the others; Google does not take part):

    python3 indexnow.py

draconyx.org and the www hosts redirect to https://draconyx.ai.

## Search engines

`build.py` writes `robots.txt`, `sitemap.xml` (the canonical pages in `PAGES`, with the date of the last commit to
the sources as `lastmod`) and the IndexNow key file `/<INDEXNOW_KEY>.txt`. The webmaster consoles' ownership
proofs go in `VERIFY_META` (meta tags) or `VERIFY_FILES` (files at the site root) in `build.py`. Keep them: if a
token disappears from the live site, the console drops the verification.
