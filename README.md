# draconyx.ai

The Draconyx website.

- `content.py`: every word on the page, the single source for `index.html`, `index.md` and `llms.txt`.
- `build.py`: renders them into `dist/` (git-ignored). No external requests at runtime: no web fonts,
  scripts or trackers.
- `assets/`: the logo and its resized versions; `assets/github/` holds the organization avatars.
- `research-features-versus.json`: the evidence behind every cell of the comparison table.

Build and preview:

    python3 build.py
    python3 -m http.server 8765 --directory dist

Deploy (the site is served by Caddy from `/var/www/draconyx.ai` on the `mail` host):

    rsync -a --delete dist/ mail:/tmp/draconyx-site/
    ssh mail 'sudo rsync -a --delete /tmp/draconyx-site/ /var/www/draconyx.ai/ && sudo chown -R caddy:caddy /var/www/draconyx.ai && rm -rf /tmp/draconyx-site'

draconyx.org and the www hosts redirect to https://draconyx.ai.
