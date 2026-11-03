# draconyx.ai

The Draconyx website.

- `content.py`: every word on the site, the single source for `index.html`, `index.md`, `llms.txt`, the
  opinions page `/what-models-think/` (verbatim quotes from AI models' answers on the spec; `OPINIONS`) and the
  changelog page `/changelog/` (`CHANGELOG`, see below).
- `build.py`: renders them into `dist/` (git-ignored). No external requests at runtime: no web fonts,
  scripts or trackers.
- `assets/`: the logo and its resized versions; `assets/github/` holds the organization avatars; `favicon.ico`
  (16, 32, 48 px) and `apple-touch-icon.png` (180 px, opaque), which `build.py` copies to the site root.
- `assets/models/`: the logos of the models quoted on the opinions page, one SVG per `OPINIONS` id, from
  [Lobe Icons](https://github.com/lobehub/lobe-icons) (MIT, licence file alongside). `build.py` inlines them.
- `assets/share-1200x630.png`: the image link previews show (`og:image`, `twitter:image`), copied to `dist/assets/`.
- `make_icons.py`: regenerates those two icons (see below).
- `make_share.py`: regenerates the share image (see below).
- `research-features-versus.json`: the evidence behind every cell of the comparison table.
- `indexnow.py`: after a deploy, submits the live sitemap's URLs to IndexNow.

Build and preview:

    python3 build.py
    python3 -m http.server 8765 --directory dist

Icons: `favicon.svg` is written by `build.py` (olive claws on the page's cream, from `CLAW_PATHS` and the `FAVICON_*`
colours). The ICO and the Apple touch icon are rasters of the same design, committed in `assets/`. Regenerate them only
when the design changes (needs Google Chrome on macOS; the rest is standard library):

    python3 make_icons.py

Share image: `make_share.py` renders the logo, the headline from `content.py` and the address on the page's cream into
an opaque 1200x630 PNG, with the same Chrome. Regenerate it when the logo, the headline or the colours change:

    python3 make_share.py

Deploy (the site is served by Caddy from `/var/www/draconyx.ai` on the `mail` host):

    rsync -a --delete dist/ mail:/tmp/draconyx-site/
    ssh mail 'sudo rsync -a --delete /tmp/draconyx-site/ /var/www/draconyx.ai/ && sudo chown -R caddy:caddy /var/www/draconyx.ai && rm -rf /tmp/draconyx-site'

After a deploy that changes the pages, tell the IndexNow search engines (Bing, Yandex, Seznam, Naver, Yep and
the others; Google does not take part):

    python3 indexnow.py

draconyx.org and the www hosts redirect to https://draconyx.ai.

## Changelog

`/changelog/` (and `/changelog/index.md`) lists what changed in the language, the spec and the toolchain, newest
first, grouped by month. It is built from `CHANGELOG` in `content.py`: one entry per day that something public-worthy
landed on `main` of the language repository, each with a short factual title and up to eight changes. A change is
`(area, text, evidence)`: the area is one of the tags already in use (Spec, Syntax, Types, Ownership, ...), the text
uses `backticks` for code, and the evidence (commit hashes on the language repository's `main`) is not rendered but
keeps every line auditable. Public wording only: no earlier working title, no internal card, decision, question or
gap numbers, no process, no benchmark results. The page is linked from the top bar, the Status section, the footer,
`index.md` and `llms.txt`, and listed in the sitemap.

## Search engines

`build.py` writes `robots.txt`, `sitemap.xml` (the canonical pages in `PAGES`, with the date of the last commit to
the sources as `lastmod`) and the IndexNow key file `/<INDEXNOW_KEY>.txt`. The webmaster consoles' ownership
proofs go in `VERIFY_META` (meta tags) or `VERIFY_FILES` (files at the site root) in `build.py`. Keep them: if a
token disappears from the live site, the console drops the verification.
