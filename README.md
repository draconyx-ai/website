# draconyx.ai

The Draconyx website.

- `content.py`: every word on the site, the single source for `index.html`, `index.md`, `llms.txt`, the
  opinions page `/what-models-think/` (verbatim quotes from AI models' answers on the spec; `OPINIONS`) and the
  changelog page `/changelog/` (`CHANGELOG`, see below).
- `build.py`: renders them into `dist/` (git-ignored). No external requests at runtime: no web fonts, trackers or
  scripts from other sites. The one script, the signup form's ALTCHA widget, is served from the site itself (see
  "Signup form" below).
- `assets/`: the logo and its resized versions; `assets/github/` holds the organization avatars; `favicon.ico`
  (16, 32, 48 px) and `apple-touch-icon.png` (180 px, opaque), which `build.py` copies to the site root.
- `assets/models/`: the logos of the models quoted on the opinions page, one SVG per `OPINIONS` id, from
  [Lobe Icons](https://github.com/lobehub/lobe-icons) (MIT, licence file alongside). `build.py` inlines them.
- `assets/share-1200x630.png`: the image link previews show (`og:image`, `twitter:image`), copied to `dist/assets/`.
- `assets/altcha/`: the ALTCHA widget of the signup form (MIT, licence file alongside), copied to `dist/assets/altcha/`.
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

## Signup form

The "Stay tuned" form (`signup()` in `build.py`, on every page) posts `l` (the list UUID), `email`, `nonce` and
`altcha` straight to listmonk's `https://lists.draconyx.ai/subscription/form`, the "Draconyx updates" list (double
opt-in). listmonk refuses a sign-up that fails either of two bot checks:

- **CAPTCHA.** listmonk's Settings, Security, CAPTCHA is set to ALTCHA (complexity 300000): proof of work, issued and
  checked by listmonk itself, no third party, no cookies. A post without a valid solution is refused ("Invalid
  CAPTCHA"), and a challenge expires 5 minutes after it is issued. It is a speed bump, not a wall: it stops bots that
  post the form without running its JavaScript, but a bot built to solve ALTCHA pays well under a second of CPU per
  sign-up. listmonk v6.2.0 also checks reuse by comparing the solution's exact text, so a re-encoded copy of one
  solution (a trailing newline, re-spaced JSON) passes again until the challenge expires: a listmonk bug to report
  upstream. There is no rate limit on sign-ups. On the page, the ALTCHA widget
  (`assets/altcha/altcha-2.3.0.js`: `dist/altcha.umd.cjs` of the npm package `altcha@2.3.0`, sha256
  `0f557a9f535a15acbe0fc7abb4fe896502a6d4c27de1c4145cfa001d0d2be099`, byte-identical to the `altcha.umd.js` that
  listmonk v6.2.0 serves) fetches the challenge from `/altcha-challenge` on draconyx.ai, solves it in a web worker when
  the form is sent (`auto="onsubmit"`) and adds the solution to the form as `altcha`. It sets no cookies, stores
  nothing in the browser and sends nothing anywhere else. The box ticks by itself, with no picture puzzle, so a line
  under it (`SIGNUP_CHECK` in `content.py`) says why; that line is hidden if the widget does not load. Without
  JavaScript the form cannot pass the check (a `<noscript>` note says so). Upgrading the widget: take the same file from the version listmonk ships, and keep the
  file name's version in step (`ALTCHA_JS` in `build.py`).
- **Honeypot.** listmonk's own `nonce` field, which a person never fills; listmonk refuses a post that fills it. It
  sits off-screen with CSS (`.hp`), inside `aria-hidden="true"`, with `tabindex="-1"` and `autocomplete="off"`, and is
  never `type="hidden"`, which bots skip.

Caddy, in the `draconyx.ai` and `lists.draconyx.ai` site blocks of `/etc/caddy/Caddyfile` on the `mail` host:

    # draconyx.ai: the challenge, from the Draconyx listmonk (port 9001), on the site's own origin
    handle /altcha-challenge {
    	header Cache-Control "no-store"
    	rewrite * /api/public/captcha/altcha
    	reverse_proxy 127.0.0.1:9001
    }

    # lists.draconyx.ai: listmonk's JSON subscription API checks neither the CAPTCHA nor the honeypot
    respond /api/public/subscription* 404

listmonk's own page, `https://lists.draconyx.ai/subscription/form` (linked from `index.md` and `llms.txt`), renders the
same CAPTCHA and honeypot itself.

listmonk v6.2.0 has no automatic removal of unconfirmed subscriptions: its Maintenance page deletes them by hand
("Unconfirmed subscriptions", older than a date).

## Contact

No page prints the contact address, where harvesters would collect it. The "email us" links (in "Get in early", the
privacy note, `index.md` and `llms.txt`) go to https://draconyx.ai/contact, which Caddy answers with a redirect to a
`mailto:` link, as `contactus.php` does on www.programmazione.it; the browser then opens the visitor's mail client. The
rule, in the `draconyx.ai` site block (the address is written there, and only there; this repository is public, so it
is not repeated here):

    redir /contact mailto:<the contact address> 302

`CONTACT_URL` and `CONTACT_LINK` in `content.py` set the link and the words linked; `grep -r "info@draconyx" dist/`
must find nothing.

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
