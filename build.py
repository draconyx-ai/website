#!/usr/bin/env python3
"""Build draconyx.ai into dist/ from content.py: index.html, index.md, llms.txt, the opinions page
(what-models-think/index.html and .md, logos inlined from assets/models/), the changelog page
(changelog/index.html and .md), the blog (blog/index.html and .md, blog/feed.xml, and blog/<slug>/index.html and .md
for each post in posts/), the not-found page (404.html), assets (the logo and the share image), favicon.svg,
favicon.ico, apple-touch-icon.png, robots.txt, sitemap.xml, the IndexNow key file and any search-engine verification files.
No external requests at runtime: no web fonts, trackers or scripts from other sites. The one script, the signup form's
ALTCHA widget, is served from the site itself (ALTCHA_JS), and so is the challenge it fetches.

    python3 build.py            # writes dist/
    python3 build.py --drafts   # also builds the posts marked draft: true, to preview them (never deploy this build)
    python3 indexnow.py         # after a deploy: tells IndexNow engines the sitemap URLs changed
"""
import datetime
import html
import json
import os
import re
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(__file__))
import content as C  # noqa: E402

HERE = os.path.dirname(__file__)
OUT = os.path.join(HERE, "dist")
SITE = "https://draconyx.ai"
TITLE = "Draconyx: a programming language for AI coding agents"

# Search engines. The IndexNow key is public by design: it is served as /<key>.txt and proves that
# submissions come from the site's owner (https://www.indexnow.org/documentation).
INDEXNOW_KEY = "7a40ed4c85a90c8eeddb499ccbd8a46b"
# Ownership verification tokens, one <meta> per non-empty value. They are public too (they sit in the page).
VERIFY_META = {
    "google-site-verification": "k8XJduzwzitQAtVzBfwNyRI8RYR3AAJbgtZGccEutw8",  # Google Search Console, HTML tag method
    "msvalidate.01": "AA85F239DE5C1777B1DA35E1AC7A54C4",  # Bing Webmaster Tools, meta tag method
    "yandex-verification": "",        # Yandex Webmaster, meta tag method
    "naver-site-verification": "",    # Naver Search Advisor, HTML tag method
    "seznam-wmt": "",                 # Seznam Webmaster (reporter.seznam.cz/wm), meta tag method
}
# Verification files served at the site root: {filename: exact content}, as each engine's console gives them.
VERIFY_FILES = {}
# The site's name, as search engines should show it: og:site_name on every indexable page, and the WebSite and
# Organization structured data on the home page (structured_data()). Google reads the site name from the home page's
# WebSite markup first (https://developers.google.com/search/docs/appearance/site-names); alternateName is its fallback
# when the bare name is taken (Draconyx is also a dinosaur genus).
SITE_NAME = "Draconyx"
SITE_ALT_NAMES = ["Draconyx programming language", "draconyx.ai"]
# Public profiles of the project, for the Organization's sameAs: only addresses that exist and are public.
SAME_AS = ["https://github.com/draconyx-ai"]
# Pages listed in sitemap.xml and submitted to IndexNow: the canonical HTML pages only. /index.md and
# /llms.txt are alternate formats of the same page, linked from it, and stay crawlable. build_sitemap() adds the blog
# and its published posts after these.
PAGES = ["/", C.OPINIONS_URL, C.CHANGELOG_URL]
MECH_LEDE = "Real mechanisms, each one enforced by the toolchain."
e = html.escape
# The signup form's bot check (README, "Signup form"): the ALTCHA widget, MIT, pinned. It is dist/altcha.umd.cjs of the
# npm package altcha@2.3.0, byte-identical to the altcha.umd.js that listmonk v6.2.0 serves; licence alongside.
ALTCHA_DIR = "assets/altcha"
ALTCHA_JS = f"{ALTCHA_DIR}/altcha-2.3.0.js"

# Three talons: the "claw" in Draconyx.
CLAW_PATHS = ('<path d="M14 54C10 38 14 20 30 8C22 24 22 40 26 54Z"/>'
              '<path d="M28 56C26 40 32 24 48 14C40 30 38 44 40 56Z"/>'
              '<path d="M42 58C42 46 48 36 60 30C54 42 52 50 54 58Z"/>')
CLAW = f'<svg class="claw" viewBox="0 0 64 64" aria-hidden="true" focusable="false">{CLAW_PATHS}</svg>'
# The favicon is the top bar's mark: olive claws (--olive) on the page's cream (--bg).
FAVICON_OLIVE, FAVICON_CREAM = "#5b6b25", "#f6efdf"
FAVICON = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" '
           f'fill="{FAVICON_CREAM}"/><g fill="{FAVICON_OLIVE}">{CLAW_PATHS}</g></svg>')

# The logos of the models quoted on the opinions page: assets/models/<id>.svg, from Lobe Icons (MIT, licence file
# alongside). Inlined, so no page loads anything from another site. They sit on a light tile (.mk),
# so the brand colours stay legible; the monochrome marks draw in currentColor.
MODEL_ICONS = {o["id"]: open(os.path.join(HERE, "assets", "models", o["id"] + ".svg"), encoding="utf-8").read().strip()
               for o in C.OPINIONS}


def model_icon(slug, use):
    """A model's logo, inlined. Gradient ids get the suffix `use`, so one logo can appear twice on a page."""
    svg = re.sub(r'(id="|url\(#)([\w-]+)', rf"\g<1>\g<2>-{use}", MODEL_ICONS[slug])
    return '<span class="mk" aria-hidden="true">' + svg.replace("<svg ", '<svg focusable="false" ', 1) + "</span>"


def quote(text):
    """A verbatim excerpt between typographic quotes; `backticks` set code."""
    return f"“{md(text)}”"


# The language's keywords in the ruled syntax (no def or let; concepts; take; comments start with //).
KEYWORDS = {"concept", "law", "checked", "example", "take", "borrow", "clone", "tainted", "endorse", "trust", "match",
            "type", "any", "if", "else", "for", "in", "return", "when", "otherwise", "fail", "use", "yield", "super", "extend", "const", "proven"}
# A Draconyx line in pieces: a closed """ text (a one-line doc), a """ left open to the end of the line (a doc that
# goes on below, down to the line holding the closing """), a "string", or a // comment to the end of the line.
# Found left to right, so a // inside a string is text.
DRX_TOKENS = re.compile(r'("""[^\n]*?"""|"""[^\n]*$|"(?:[^"\\]|\\.)*"|//.*$)')


def drx_report(text):
    """drx's terminal report in its own style, from the plain text (one block per problem, each line of a block
    starting with ┃): the bar becomes ONE left border, the ERROR badge, the file and line in bold, the code
    highlighted, the ^^^ marks red, `code` in a sentence shown without its backticks in the name colour, the
    reference grey, the recap's count red and bold. Escapes everything."""
    out, block = [], []

    def sentence(line):
        return re.sub(r"`([^`]+)`", r'<span class="d-name">\1</span>', e(line))

    def flush():
        if block:
            out.append('<span class="d-bar">' + "\n".join(x or "<span></span>" for x in block) + "</span>")
            block.clear()

    for line in text.split("\n"):
        if not line.startswith("┃"):
            flush()
            if line.startswith("$ "):
                out.append('<span class="d-prompt">$</span> ' + e(line[2:]))
            else:
                m = re.match(r"(\d+ errors?)(.*)$", line)
                out.append(f'<span class="d-count">{e(m.group(1))}</span>{e(m.group(2))}' if m else e(line))
            continue
        body = line[2:] if line.startswith("┃ ") else line[1:]
        m = re.match(r"ERROR  (.*)$", body)
        if m:
            block.append(f'<span class="d-badge"> ERROR </span>  <span class="d-loc">{e(m.group(1))}</span>')
        elif re.fullmatch(r" +\^+", body):
            block.append(f'<span class="d-marks">{e(body)}</span>')
        elif body.startswith("    "):
            block.append(highlight("draconyx", body))
        elif re.fullmatch(r"\(AX\d{4}\. .*\)", body):
            block.append(f'<span class="d-ref">{e(body)}</span>')
        else:
            block.append(sentence(body))
    flush()
    html_out = ""
    for i, piece in enumerate(out):
        if i and not piece.startswith('<span class="d-bar">') and not out[i - 1].startswith('<span class="d-bar">'):
            html_out += "\n"
        html_out += piece
    return html_out


def highlight(kind, text):
    """Tiny, safe highlighter. Draconyx: // comments, strings, docs (a \"\"\" text above a declaration, on one line
    or from a \"\"\" line down to the closing \"\"\" line, all in the string colour), keywords, AX codes. Shell and
    JSON: # comments, strings, AX codes. Escapes everything."""
    def plain(p):
        p = e(p)
        if kind == "draconyx":
            p = re.sub(r"\b(" + "|".join(sorted(KEYWORDS)) + r")\b", r'<span class="k">\1</span>', p)
        return re.sub(r"\b(AX\d{4})\b", r'<span class="ax">\1</span>', p)

    def note(c):
        return '<span class="c">' + re.sub(r"\b(AX\d{4})\b", r'<span class="ax">\1</span>', e(c)) + "</span>"

    out, in_doc = [], False  # in_doc: inside a Draconyx """ text that a line above opened
    for line in text.split("\n"):
        buf = []
        if in_doc:
            end = line.find('"""')
            if end < 0:
                out.append(f'<span class="s">{e(line)}</span>' if line else "")
                continue
            buf.append(f'<span class="s">{e(line[:end + 3])}</span>')
            line, in_doc = line[end + 3:], False
        if kind == "draconyx":
            for i, p in enumerate(DRX_TOKENS.split(line)):
                if i % 2 == 0:
                    buf.append(plain(p))
                elif p.startswith("//"):
                    buf.append(note(p))
                else:
                    buf.append(f'<span class="s">{e(p)}</span>')
                    in_doc = p.startswith('"""') and (len(p) < 6 or not p.endswith('"""'))
        else:
            code, comment = line, ""
            m = re.search(r"((?:^|\s)#\s.*$)", line)
            if m:
                code, comment = line[: m.start(1)], line[m.start(1):]
            for i, p in enumerate(re.split(r'("(?:[^"\\]|\\.)*")', code)):
                buf.append(f'<span class="s">{e(p)}</span>' if i % 2 else plain(p))
            if comment:
                buf.append(note(comment))
        out.append("".join(buf))
    return "\n".join(out)


def md(text):
    """Escape, then turn `backticks` into <code>."""
    return re.sub(r"`([^`]+)`", r"<code>\1</code>", e(text))


def cites_html(cites):
    return ('<details class="cites"><summary>Spec references</summary><p>'
            + ", ".join(f"<code>{e(c)}</code>" for c in cites) + "</p></details>")


CSS = """
:root{--cut1:polygon(11px 0,46% 1px,calc(100% - 17px) 0,100% 10px,100% calc(100% - 13px),calc(100% - 8px) 100%,58% calc(100% - 1px),15px 100%,0 calc(100% - 9px),0 14px);--cut2:polygon(0 8px,7px 0,62% 0,calc(100% - 13px) 1px,100% 15px,calc(100% - 1px) 64%,100% calc(100% - 7px),calc(100% - 16px) 100%,10px 100%,0 calc(100% - 15px));--cut3:polygon(16px 0,calc(100% - 9px) 0,100% 7px,100% 52%,calc(100% - 1px) calc(100% - 16px),calc(100% - 12px) 100%,6px 100%,0 calc(100% - 6px),1px 40%,0 12px);--cut-s:polygon(6px 0,calc(100% - 10px) 0,100% 7px,100% calc(100% - 5px),calc(100% - 6px) 100%,9px 100%,0 calc(100% - 8px),0 5px);--chip-cut:polygon(4px 0,calc(100% - 6px) 0,100% 5px,100% calc(100% - 3px),calc(100% - 4px) 100%,5px 100%,0 calc(100% - 5px),0 3px);--pebble:polygon(30% 0,74% 5%,100% 36%,94% 78%,62% 100%,20% 95%,0 62%,6% 22%);--bg:#f6efdf;--bg2:#efe4cc;--card:#fffaf0;--fg:#1c1a14;--muted:#5c5545;--line:#ddcfae;
--olive:#5b6b25;--ember:#b63e15;--ember2:#e8501f;--ink:#15130f;
--code-bg:#1d1b15;--code-fg:#efe8d8;--code-c:#9d9583;--code-s:#e9bd7c;--code-k:#f08a5d;--code-ax:#d7e48a;
--chip:#efe2c4;--ok:#45601a;--ok-bg:#e3ead0;--gap:#7d5200;--gap-bg:#f6e3b5;--shadow:#15130f}
html{scroll-padding-top:76px;-webkit-text-size-adjust:100%}*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:17px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,Roboto,"Helvetica Neue",Arial,sans-serif}
a{color:var(--ember)}a:hover{color:var(--ember2)}
a:focus-visible,button:focus-visible,summary:focus-visible,[tabindex]:focus-visible{outline:2px solid var(--ember);outline-offset:3px;border-radius:4px}
.skip{position:absolute;left:-999px}.skip:focus{left:16px;top:16px;background:var(--fg);color:var(--bg);padding:8px 12px;z-index:9}
.vh{position:absolute;width:1px;height:1px;margin:-1px;overflow:hidden;clip-path:inset(50%);white-space:nowrap}
.wrap{max-width:1120px;margin:0 auto;padding-left:16px;padding-right:16px}
header.top{position:sticky;top:0;z-index:5;background:color-mix(in srgb,var(--bg) 86%,transparent);backdrop-filter:blur(10px);border-bottom:1px solid var(--line)}
header.top .wrap{display:flex;align-items:center;justify-content:space-between;height:62px;gap:16px}
.brand{display:flex;align-items:center;gap:10px;color:var(--fg);text-decoration:none;font-weight:800;letter-spacing:.06em;text-transform:uppercase;font-size:17px}
.claw{width:26px;height:26px;fill:var(--olive)}
nav a{display:inline-block;padding:10px 0;color:var(--muted);text-decoration:none;font-size:15px;font-weight:550;margin-left:20px}nav a:hover{color:var(--fg)}
nav{white-space:nowrap}@media (max-width:720px){nav a.opt{display:none}}@media (max-width:480px){nav a.nr{display:none}}@media (max-width:420px){nav a{margin-left:12px;font-size:14px}.brand{font-size:15px}}
.hero{position:relative;overflow:hidden;background:
 radial-gradient(1100px 520px at 50% 108%,color-mix(in srgb,var(--olive) 30%,transparent),transparent 70%),
 radial-gradient(700px 360px at 8% 0%,color-mix(in srgb,var(--ember2) 16%,transparent),transparent 70%),var(--bg)}
.hero::after{content:"";position:absolute;inset:auto 0 0 0;height:90px;background:repeating-linear-gradient(0deg,transparent 0 13px,color-mix(in srgb,var(--olive) 14%,transparent) 13px 15px);-webkit-mask:linear-gradient(transparent,#000);mask:linear-gradient(transparent,#000)}
.hero .wrap{position:relative;z-index:1;text-align:center;padding-top:40px;padding-bottom:80px}
.logo{display:block;width:min(720px,100%);height:auto;margin:0 auto 6px;filter:drop-shadow(0 18px 28px rgba(40,30,10,.18));animation:rise .9s cubic-bezier(.2,.8,.2,1) both}
.eyebrow{display:inline-block;text-transform:uppercase;letter-spacing:.14em;font-size:13px;font-weight:750;color:var(--olive);background:color-mix(in srgb,var(--olive) 12%,transparent);border:1px solid color-mix(in srgb,var(--olive) 30%,transparent);padding:6px 12px;clip-path:var(--chip-cut);margin:8px 0 18px;border:0}
h1,h2,h3{font-family:ui-serif,"New York","Iowan Old Style",Georgia,"Times New Roman",serif;font-weight:650;letter-spacing:-.012em;line-height:1.12}
h1{font-size:clamp(34px,5.6vw,62px);margin:0 auto 20px;max-width:18ch}
.hero .sub{font-size:clamp(17px,2vw,20px);color:var(--muted);max-width:64ch;margin:0 auto 30px}
.btns{display:flex;flex-wrap:wrap;gap:12px;justify-content:center}
.btn{--edge:var(--shadow);--ew:2px;--eb:5px;--cut:var(--cut-s);display:inline-block;padding:14px 22px 17px;color:var(--fg);text-decoration:none;font-weight:700;font-size:15px}
.btn:hover,.btn:focus-visible{--edge:var(--ember);color:var(--fg)}
.btn.primary{--fill:var(--ember2);color:#1a0c05}.btn.primary:hover,.btn.primary:focus-visible{--edge:var(--shadow);--fill:#f2662f;color:#1a0c05}

@keyframes rise{from{opacity:0;transform:translateY(24px) scale(.98)}to{opacity:1;transform:none}}
@media (max-width:720px){.hero .wrap{padding-top:20px;padding-bottom:56px}}
.stats{background:var(--olive);color:#f6f1df}
.stats ul{list-style:none;padding:30px 16px;display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:18px;max-width:1120px;margin:0 auto}
.stats li{text-align:center}.stats b{display:block;font:800 clamp(30px,4vw,44px)/1 ui-serif,Georgia,serif;letter-spacing:-.02em;color:#fff3c9}
.stats span{display:block;font-size:14px;margin-top:6px;opacity:.92}
@media (max-width:820px){.stats ul{grid-template-columns:repeat(2,minmax(0,1fr))}.stats li:last-child{grid-column:1/-1}}
section{padding:80px 0;border-top:1px solid var(--line)}
h2{font-size:clamp(28px,3.8vw,42px);margin:0 0 16px}
.kicker{font:700 13px/1 ui-monospace,SFMono-Regular,Menlo,monospace;letter-spacing:.1em;text-transform:uppercase;color:var(--ember);margin:0 0 12px}
.lede{color:var(--muted);max-width:70ch;margin:0 0 8px}
.prose p{max-width:70ch}
.loop{list-style:none;padding:0;margin:40px 0 0;display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:22px}
.loop li{--edge:var(--shadow);--ew:2px;--eb:6px;padding:24px 20px 24px}
.loop .n{position:absolute;top:-17px;left:16px;width:36px;height:36px;display:grid;place-items:center;font:800 15px/1 system-ui,sans-serif;font-style:normal;color:#fff;background:var(--shadow);clip-path:var(--pebble)}
.loop .n::before{content:"";position:absolute;inset:2px;z-index:-1;background:var(--olive);clip-path:var(--pebble)}.loop .n{isolation:isolate}
.loop .arr{position:absolute;right:-17px;top:50%;width:12px;height:12px;border-top:3px solid var(--ember2);border-right:3px solid var(--ember2);transform:translateY(-50%) rotate(45deg)}
.loop b{display:block;font-size:17px;margin:6px 0 4px}.loop span{font-size:15px;color:var(--muted)}
@media (max-width:860px){.loop{grid-template-columns:minmax(0,1fr);gap:30px}.loop .arr{right:auto;left:50%;top:auto;bottom:-22px;transform:translateX(-50%) rotate(135deg)}}
.vwrap{overflow-x:auto;contain:paint;margin-top:30px;border-radius:2px;border:2px solid var(--shadow);border-bottom-width:6px;background:var(--card)}
table.versus{width:100%;table-layout:fixed;border-collapse:collapse;min-width:@VMIN_MID@px;font-size:14.5px}.versus col.cap{width:220px}@media (max-width:1100px){.versus col.cap{width:180px}}
.versus tbody th{position:sticky;left:0;background:var(--card);z-index:1}
@media (max-width:600px){.versus col.cap{width:150px}.versus tbody th{font-size:13px}table.versus{font-size:13px;min-width:@VMIN_PHONE@px}.versus th,.versus td{padding:10px 4px}}
.versus thead th:first-child{position:sticky;left:0;z-index:2}
.versus th,.versus td{padding:13px 4px;border-bottom:1px solid var(--line);text-align:center}
.versus tbody tr:last-child th,.versus tbody tr:last-child td{border-bottom:0}
.versus thead th{font-size:12.5px;letter-spacing:0;line-height:1.25;padding-left:2px;padding-right:2px;color:var(--muted);font-weight:750;background:var(--bg2)}
.versus tbody th{text-align:left;font-weight:600;padding-left:16px;padding-right:10px}
.versus .us{background:color-mix(in srgb,var(--olive) 14%,transparent)}
.versus thead .us{background:var(--olive);color:#fff}
.m{display:inline-grid;place-items:center;width:28px;height:28px;clip-path:var(--pebble);font-weight:900;font-size:15px}
.m.yes{background:var(--olive);color:#fff}.m.part{background:var(--gap-bg);color:var(--gap)}.m.no{color:var(--muted);opacity:.7}
.vnote{margin-top:14px;max-width:90ch}
details.fine{--cut:var(--cut3);margin-top:16px;padding:15px 19px 17px}
details.fine summary{cursor:pointer;font-weight:700}
details.fine h4{margin:16px 0 6px;font-size:15px}details.fine ul{margin:0;padding-left:20px;font-size:14.5px;color:var(--muted)}
details.fine li{margin:4px 0}
.fgroups{display:grid;gap:34px;margin-top:30px}
.fgroup h3{font-size:clamp(21px,2.4vw,26px);margin:0 0 14px}
.fgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,300px),1fr));gap:16px}
.fcard{padding:19px 19px 19px;display:flex;flex-direction:column;gap:8px}
.fcard:hover{--edge:var(--olive)}
.fcard b{font-size:16.5px;line-height:1.3}.fcard p{margin:0;font-size:15px;color:var(--muted)}
.fcard p code,.fcard b code{background:var(--chip);padding:1px 5px;border-radius:5px}
.fcard .pill{align-self:flex-start}
.pill.spec{color:var(--muted);background:var(--line)}
.reasons{display:grid;grid-template-columns:minmax(0,1fr);gap:26px;margin-top:34px}.reason{min-width:0}
.reason{padding:31px 31px 27px}
.reason:hover{--edge:var(--olive)}
.rhead{display:flex;align-items:center;gap:12px;flex-wrap:wrap}
.num{font:800 15px/1 ui-monospace,SFMono-Regular,Menlo,monospace;color:#fff;background:var(--olive);clip-path:var(--chip-cut);padding:8px 10px}
.pill{font-size:12.5px;font-weight:750;letter-spacing:.04em;text-transform:uppercase;clip-path:var(--chip-cut);padding:5px 10px}
.pill.ships{color:var(--ok);background:var(--ok-bg)}.pill.gaps{color:var(--gap);background:var(--gap-bg)}
h3{font-size:clamp(23px,2.7vw,30px);margin:14px 0 12px}
.rbody{max-width:76ch}.reason p{margin:0 0 14px}
.ships-line{font-size:15px;background:var(--chip);clip-path:var(--cut-s);padding:10px 14px}
.unlike{font-size:15px;color:var(--muted);border-left:3px solid var(--ember2);padding-left:14px}.unlike b{color:var(--fg)}
.reason p code,dd code,.prose code{background:var(--chip);padding:1px 5px;border-radius:5px}.ships-line code{background:var(--card)}
figure{margin:18px 0 0;min-width:0}
pre{margin:0;background:var(--code-bg);color:var(--code-fg);clip-path:var(--cut2);padding:18px 20px;overflow-x:auto;
font:13.5px/1.6 ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,monospace;tab-size:4}
pre .c{color:var(--code-c)}pre .s{color:var(--code-s)}pre .k{color:var(--code-k)}pre .ax{color:var(--code-ax);font-weight:700}
pre .d-bar{display:block;border-left:3px solid #cd3131;padding-left:calc(2ch - 3px)}pre .d-badge{color:#fff;background:#cd3131;font-weight:700}
pre .d-loc,pre .d-count{font-weight:700}pre .d-count,pre .d-marks{color:#cd3131}pre .d-ref,pre .d-prompt{color:#8a8a8a}pre .d-name{color:#afd7ff}
figcaption{font-size:13px;color:var(--muted);margin-top:8px}
code{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:.9em}
.cites{margin-top:10px;font-size:13px;color:var(--muted)}.cites summary{cursor:pointer}.cites code{white-space:nowrap}
.loop li,.fcard,.reason,details.fine,.btn,.opinion,.tcard,.roster a,.entry{position:relative;isolation:isolate}
.loop li::before,.fcard::before,.reason::before,details.fine::before,.btn::before,.opinion::before,.tcard::before,.roster a::before,.entry::before{content:"";position:absolute;inset:0;z-index:-2;background:var(--edge,var(--line));clip-path:var(--cut,var(--cut1));transition:background .2s}
.loop li::after,.fcard::after,.reason::after,details.fine::after,.btn::after,.opinion::after,.tcard::after,.roster a::after,.entry::after{content:"";position:absolute;inset:var(--ew,1px) var(--ew,1px) var(--eb,3px);z-index:-1;background:var(--fill,var(--card));clip-path:var(--cut,var(--cut1));transition:background .2s}
.fcard:nth-child(3n+2),.reason:nth-child(3n+2),.loop li:nth-child(3n+2),.btn:nth-child(2),.opinion:nth-child(3n+2),.tcard:nth-child(3n+2),.entry:nth-child(3n+2){--cut:var(--cut2)}.fcard:nth-child(3n),.reason:nth-child(3n),.loop li:nth-child(3n),.btn:nth-child(3),.opinion:nth-child(3n),.tcard:nth-child(3n),.entry:nth-child(3n){--cut:var(--cut3)}
@media (max-width:600px){.reason{padding:23px 19px 21px}}
:root{--mk-bg:#efe4cc}
.mk{display:inline-grid;place-items:center;flex:none;width:44px;height:44px;background:var(--mk-bg);color:#15130f;clip-path:var(--chip-cut)}
.mk svg{width:62%;height:62%}
.hero.page .wrap{padding-top:56px;padding-bottom:64px}.hero.page h1{max-width:20ch}
.hero:not(.page) h1{max-width:26ch;text-wrap:balance}
.roster{list-style:none;padding:0;margin:0 auto;display:flex;flex-wrap:wrap;gap:12px;justify-content:center;max-width:860px}
.roster a{--cut:var(--chip-cut);--eb:3px;display:flex;align-items:center;gap:10px;padding:6px 16px 9px 7px;color:var(--fg);text-decoration:none;font-weight:700;font-size:15px}
.roster a:hover,.roster a:focus-visible{color:var(--fg);--edge:var(--olive)}.roster .mk{width:34px;height:34px}
.asks{list-style:none;padding:0;margin:26px 0 0;display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:18px 22px}
.asks li{display:flex;gap:12px;align-items:flex-start;font:600 18px/1.35 ui-serif,"New York","Iowan Old Style",Georgia,serif}
@media (max-width:900px){.asks{grid-template-columns:repeat(2,minmax(0,1fr))}}@media (max-width:520px){.asks{grid-template-columns:minmax(0,1fr)}}
.setup .note{margin:24px 0 0;max-width:86ch}
.opinions{display:grid;gap:30px}
.opinion{--edge:var(--shadow);--ew:2px;--eb:6px;padding:32px 34px 30px;scroll-margin-top:80px}
.ohead{display:flex;align-items:center;gap:16px}.ohead .mk{width:60px;height:60px}
.ohead h2{margin:0;font-size:clamp(26px,3vw,34px)}.maker{margin:3px 0 0;font-size:14.5px;color:var(--muted);font-weight:600}
blockquote{margin:0}blockquote p{margin:0}
.pull{margin:24px 0 0;padding:2px 0 2px 22px;border-left:4px solid var(--olive);max-width:48ch;font:600 clamp(21px,2.5vw,28px)/1.3 ui-serif,"New York","Iowan Old Style",Georgia,serif;letter-spacing:-.01em}
.quotes{list-style:none;padding:0;margin:28px 0 0;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:22px 36px}
.qtag{display:block;font:700 12px/1 ui-monospace,SFMono-Regular,Menlo,monospace;letter-spacing:.1em;text-transform:uppercase;color:var(--ember);margin:0 0 8px}
.quotes blockquote{font-size:16px}
.quotes code,.pull code,.tcard code{background:var(--chip);padding:1px 5px;border-radius:5px;font-size:.84em}
@media (max-width:760px){.quotes{grid-template-columns:minmax(0,1fr)}.opinion{padding:24px 19px 24px}.ohead .mk{width:50px;height:50px}}
.credits{margin-top:30px}
.roster.plain a{padding:8px 16px 11px}
.lognote{margin:0 0 34px;max-width:86ch}
.log{display:grid;gap:56px}.month{scroll-margin-top:80px}.month h2{margin:0 0 22px}
.entries{display:grid;gap:22px}
.entry{padding:26px 30px 28px;scroll-margin-top:80px}
.ehead{display:flex;align-items:center;gap:14px}.ehead .num{flex:none;white-space:nowrap}
.ehead h3{margin:0;font-size:clamp(20px,2.3vw,25px)}
.changes{list-style:none;padding:0;margin:18px 0 0;display:grid;gap:12px}
.changes li{display:grid;grid-template-columns:136px minmax(0,1fr);gap:4px 18px;align-items:baseline}
.changes .qtag{margin:0;line-height:1.5}.changes p{margin:0;max-width:78ch;font-size:16px}
.changes code{background:var(--chip);padding:1px 5px;border-radius:5px;font-size:.88em}
@media (max-width:640px){.changes li{grid-template-columns:minmax(0,1fr)}.entry{padding:22px 19px 24px}.ehead{align-items:flex-start;flex-direction:column;gap:10px}}
.tgrid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px;margin-top:30px}
.tcard{margin:0;padding:20px 21px 23px;display:flex;flex-direction:column;gap:14px}
.tcard:hover{--edge:var(--olive)}
.who{display:flex;align-items:center;gap:12px;line-height:1.25}.who a{color:var(--fg);text-decoration:none;font-weight:750}.who a:hover{color:var(--ember)}
.who small{display:block;color:var(--muted);font-size:13.5px;font-weight:600}
.tcard blockquote{font:600 17.5px/1.4 ui-serif,"New York","Iowan Old Style",Georgia,serif}
@media (max-width:900px){.tgrid{grid-template-columns:repeat(2,minmax(0,1fr))}}@media (max-width:600px){.tgrid{grid-template-columns:minmax(0,1fr)}}
.btns.start{justify-content:flex-start;margin-top:30px}
.name{background:linear-gradient(180deg,var(--bg2),var(--bg))}
.namegrid{display:grid;grid-template-columns:minmax(0,.9fr) minmax(0,1.1fr);gap:44px;align-items:center}
.namegrid img{width:100%;height:auto;filter:drop-shadow(0 14px 24px rgba(40,30,10,.16))}
@media (max-width:860px){.namegrid{grid-template-columns:minmax(0,1fr)}.namegrid img{max-width:460px;margin:0 auto}}
.src{font-size:13px;color:var(--muted)}
dl.status{display:grid;grid-template-columns:210px minmax(0,1fr);gap:14px 28px;margin:26px 0 0}
dl.status dt{font-weight:750}dl.status dd{margin:0;color:var(--muted)}
@media (max-width:720px){dl.status{grid-template-columns:minmax(0,1fr)}dl.status dd{margin-bottom:10px}}
.cta{background:var(--ink);color:#f3ecda;border-top:0}
.cta h2,.cta h3{color:#fff3c9}.cta h3{margin-top:38px}.cta .lead{font-size:19px;max-width:60ch}.cta a{color:#ffb08f}.cta a:hover{color:#ffd0bd}.cta .note{color:#c9c0a8}
form.signup{display:flex;flex-wrap:wrap;gap:10px;margin:22px 0 8px}
form.signup input[type=email]{flex:1 1 260px;min-width:0;padding:11px 14px;clip-path:var(--chip-cut);border:1px solid #8c8470;background:#1f1d17;color:#f3ecda;font-family:inherit;font-size:16px}
form.signup button{padding:11px 20px;clip-path:var(--chip-cut);border:0;background:var(--ember2);color:#1a0c05;font-family:inherit;font-size:15px;font-weight:700;cursor:pointer;transition:background .2s}
form.signup button:hover,form.signup button:focus-visible{background:#ff7a45}
form.signup .hp{position:absolute;left:-10000px;top:auto;width:1px;height:1px;overflow:hidden}
form.signup altcha-widget{flex:1 1 100%;font-size:15px;accent-color:#e8501f;--altcha-color-base:#1f1d17;--altcha-color-border:#8c8470;--altcha-color-border-focus:#ffb08f;--altcha-color-text:#f3ecda;--altcha-color-error-text:#ffb08f;--altcha-color-active:#e8501f;--altcha-border-radius:0;--altcha-max-width:320px}
form.signup .altcha{clip-path:var(--chip-cut)}
form.signup .check{flex:1 1 100%;margin:0}
altcha-widget:not(:defined)+.check{display:none}
.note{font-size:14px;color:var(--muted)}
footer{background:var(--ink);color:#bfb69d;border-top:1px solid #2a271f;padding:26px 0 40px;font-size:14px}
footer a{color:#e7dcc0}
footer .wrap{display:flex;flex-wrap:wrap;gap:12px 28px;justify-content:space-between;align-items:center}
footer .claw{fill:#a6b85a;width:22px;height:22px;vertical-align:-5px;margin-right:6px}
footer .privacy{flex:1 1 100%;margin:6px 0 0;font-size:13px;line-height:1.55;max-width:96ch}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}}
"""
# Language columns share the width equally and never shrink below VCOL px (the widest header,
# "Draconyx" in bold, needs about that); below it the table scrolls inside its box instead.
VCOL = 62
CSS = (CSS.replace("@VMIN_MID@", str(180 + VCOL * len(C.VERSUS_LANGS)))
          .replace("@VMIN_PHONE@", str(150 + VCOL * len(C.VERSUS_LANGS))))


# The home page's blog section (latest_posts()): its own few lines of CSS, passed to head() for the home page only, so
# the other pages do not change. The cards are the blog index's (.entry), with the title one level down (h3).
HOME_POSTS = 3
HOME_BLOG_CSS = (".latest{display:grid;gap:22px;max-width:860px;margin-top:30px}.latest .entry:hover{--edge:var(--olive)}"
                 ".latest .ehead h3 a{color:var(--fg);text-decoration:none}.latest .ehead h3 a:hover{color:var(--ember)}"
                 ".latest .psum{margin:14px 0 0;color:var(--muted);max-width:70ch}"
                 ".latest .tags{margin:14px 0 0}")


def latest_posts(posts):
    """Home page section: the newest posts (date, title, summary), each linking to its page, then a link to the blog.
    posts are load_posts()'s, the same the blog's index lists, so drafts appear only in a --drafts preview, marked.
    Nothing at all when there are no posts."""
    if not posts:
        return ""
    cards = []
    for p in posts[:HOME_POSTS]:
        y, m, d = (int(x) for x in p["date"].split("-"))
        draft = '<p class="tags"><span class="pill gaps">Draft</span></p>' if p["draft"] else ""
        cards.append(f'<article class="entry"><div class="ehead">'
                     f'<time class="num" datetime="{p["date"]}">{d} {MONTHS[m - 1][:3]} {y}</time>'
                     f'<h3><a href="{p["url"]}">{e(p["title"])}</a></h3></div>'
                     f'<p class="psum">{md(p["summary"])}</p>{draft}</article>')
    return f"""<section id="blog"><div class="wrap">
<p class="kicker">{e(C.BLOG_HOME_KICKER)}</p>
<h2>{e(C.BLOG_HEADLINE)}</h2>
<p class="lede">{e(C.BLOG_HOME_LEDE)}</p>
<div class="latest">{''.join(cards)}</div>
<div class="btns start"><a class="btn" href="{C.BLOG_URL}">{e(C.BLOG_HOME_ALL)}</a></div>
</div></section>

"""


def build_html(posts=()):
    reasons = []
    for i, r in enumerate(C.REASONS, 1):
        pill = ('<span class="pill ships">Ships today</span>' if r["state"] == "ships"
                else '<span class="pill gaps">Ships, with gaps</span>')
        body = "".join(f"<p>{md(p)}</p>" for p in r["body"])
        fig = ""
        if r["sample"]:
            kind, code, cap = r["sample"]
            fig = (f'<figure><pre tabindex="0" role="region" aria-label="{e(r["title"])}: example"><code>'
                   f'{drx_report(code) if kind == "drx" else highlight(kind, code)}</code></pre>'
                   f'<figcaption>{e(cap)}</figcaption></figure>')
        reasons.append(
            f'<article class="reason" id="{r["id"]}"><div class="rhead"><span class="num">{i:02d}</span>{pill}</div>'
            f'<h3>{e(r["title"])}</h3><div class="rbody">{body}<p class="ships-line">{md(r["ships"])}</p>'
            f'<p class="unlike"><b>Elsewhere:</b> {md(r["unlike"])}</p>{cites_html(r["cites"])}</div>{fig}</article>')

    marks = {"yes": ('<span class="m yes" aria-hidden="true">&#10003;</span>', "built in"),
             "part": ('<span class="m part" aria-hidden="true">&#9680;</span>', "partly or via an add-on"),
             "no": ('<span class="m no" aria-hidden="true">&#10005;</span>', "no")}
    vhead = "".join(f'<th scope="col"{" class=\"us\"" if i == 0 else ""}>{e(l)}</th>' for i, l in enumerate(C.VERSUS_LANGS))
    vrows = "".join(
        "<tr><th scope=\"row\">" + e(row) + "</th>" + "".join(
            f'<td{" class=\"us\"" if i == 0 else ""}>{marks[v][0]}<span class="vh">{marks[v][1]}</span></td>'
            for i, v in enumerate(vals)) + "</tr>" for row, vals in C.VERSUS)
    vnote = ("<details class=\"fine\"><summary>Why \u201cpartly\u201d? The fine print, language by language.</summary>"
             + "".join(f"<h4>{e(l)}</h4><ul>" + "".join(f"<li>{md(n)}</li>" for n in ns) + "</ul>"
                       for l, ns in C.VERSUS_NOTES.items()) + "</details>")
    status_pill = {"ships": '<span class="pill ships">Ships</span>', "partial": '<span class="pill gaps">Partly built</span>',
                   "specified": '<span class="pill spec">In the spec</span>'}
    fgroups = "".join(
        f'<div class="fgroup"><h3>{e(g)}</h3><div class="fgrid">' + "".join(
            f'<div class="fcard">{status_pill[st]}<b>{md(n)}</b><p>{md(pt)}</p></div>' for n, pt, st in items)
        + "</div></div>" for g, items in C.FEATURE_GROUPS)
    stats = "".join(f"<li><b>{e(n)}</b><span>{e(t)}</span></li>" for n, t in C.STATS)
    loop = "".join(f'<li><i class="n" aria-hidden="true">{i}</i><b>{e(t)}</b><span>{e(d)}</span>'
                   + ('<i class="arr" aria-hidden="true"></i>' if i < len(C.LOOP) else "") + "</li>"
                   for i, (t, d) in enumerate(C.LOOP, 1))
    status = "".join(f"<dt>{e(k)}</dt><dd>{md(v)}</dd>" for k, v in C.STATUS)
    spec = f'<a class="btn" href="{e(C.SPEC_PDF)}">Read the spec (PDF)</a>' if C.SPEC_PDF else ""

    description = ("Draconyx is a programming language designed for AI coding agents. Its compiler gives structured "
                   "diagnostics with edits and checks laws by default.")
    return head(TITLE, description, "/", SITE_NAME, f"{C.HERO['headline']} A programming language designed for its AI author.",
                verify=True, css=HOME_BLOG_CSS if posts else "", extra=structured_data(description)) + topbar("/") + f"""<main id="main">
<div class="hero"><div class="wrap">
<img class="logo" src="/assets/logo-1200.webp" srcset="/assets/logo-640.webp 640w, /assets/logo-1200.webp 1200w" sizes="(max-width:760px) 100vw, 720px" width="1200" height="800" alt="Draconyx: a dinosaur mascot above the Draconyx wordmark.">
<p class="eyebrow">{e(C.HERO['eyebrow'])}</p>
<h1>{e(C.HERO['h1'])}</h1>
<p class="sub">{e(C.HERO['subhead'])}</p>
<div class="btns"><a class="btn primary" href="#versus">See it beat the rest</a>{spec}<a class="btn" href="#updates">Get launch updates</a><a class="btn" href="/llms.txt">For AI agents: llms.txt</a></div>
</div></div>

<div class="stats" aria-label="Project in numbers"><ul>{stats}</ul></div>

<section id="problem"><div class="wrap prose">
<p class="kicker">The problem</p>
<h2>Every other language was built for humans</h2>
{''.join(f'<p>{e(p)}</p>' for p in C.PROBLEM)}
{cites_html(C.PROBLEM_CITES)}
</div></section>

<section id="loop"><div class="wrap">
<p class="kicker">The loop</p>
<h2>Built for generate, check, repair</h2>
<p class="lede">A model doesn't read the manual and then write correct code. It iterates, hundreds of times. Draconyx turns every step of that loop into a machine-readable contract.</p>
<ol class="loop">{loop}</ol>
</div></section>

<section id="versus"><div class="wrap">
<p class="kicker">Head to head</p>
<h2>Draconyx vs. the languages your agents write today</h2>
<p class="lede">Built in, not bolted on.</p>
<div class="vwrap" tabindex="0" role="region" aria-label="Comparison table"><table class="versus"><colgroup><col class="cap"></colgroup>
<thead><tr><th scope="col"><span class="vh">Capability</span></th>{vhead}</tr></thead>
<tbody>{vrows}</tbody></table></div>
{vnote}
</div></section>

<section id="why"><div class="wrap">
<p class="kicker">Why Draconyx</p>
<h2>Nine unfair advantages</h2>
<p class="lede">{e(MECH_LEDE)}</p>
<div class="reasons">{''.join(reasons)}</div>
</div></section>

<section id="language"><div class="wrap">
<p class="kicker">The whole language</p>
<h2>Built for agents. Complete for everything else.</h2>
<p class="lede">One language from the type system to the cluster: ownership without a garbage collector, concepts with laws, structured concurrency, remote values, a numerical core. Every card says exactly where it stands.</p>
<div class="fgroups">{fgroups}</div>
</div></section>

{opinions_teaser()}
<section id="name" class="name"><div class="wrap namegrid">
<img src="/assets/logo-640.webp" width="640" height="427" alt="" loading="lazy">
<div class="prose"><p class="kicker">The name</p><h2>Dragon claw, written law</h2>
{''.join(f'<p>{md(p)}</p>' for p in C.NAME)}
<p class="src">Source: <a href="{e(C.NAME_SOURCE[1])}">{e(C.NAME_SOURCE[0])}</a>.</p></div>
</div></section>

<section id="status"><div class="wrap">
<p class="kicker">Status</p>
<h2>Where it stands</h2>
<p class="lede">As of {e(C.AS_OF)}.</p>
<dl class="status">{status}</dl>
<div class="btns start"><a class="btn" href="{C.CHANGELOG_URL}">What changed: the changelog</a></div>
</div></section>

{latest_posts(posts)}{signup()}</main>
""" + footer("/index.md")


# The link-preview image (Open Graph and X/Twitter), made by make_share.py and committed in assets/.
SHARE_IMAGE = "/assets/share-1200x630.png"
SHARE_ALT = f"The Draconyx logo beside the headline: {C.HERO['headline']}"


def structured_data(description):
    """The home page's JSON-LD: the WebSite (the site name) and the Organization behind it (logo, public profiles), with
    the same name and alternate names, as Google asks (https://developers.google.com/search/docs/appearance/
    structured-data/organization). The logo is the 180 px Apple touch icon: opaque, square, above Google's 112 px
    minimum. "</" is escaped so the text cannot close the script element."""
    data = {"@context": "https://schema.org", "@graph": [
        {"@type": "WebSite", "@id": f"{SITE}/#website", "name": SITE_NAME, "alternateName": SITE_ALT_NAMES,
         "url": f"{SITE}/", "inLanguage": "en", "publisher": {"@id": f"{SITE}/#organization"}},
        {"@type": "Organization", "@id": f"{SITE}/#organization", "name": SITE_NAME, "alternateName": SITE_ALT_NAMES,
         "url": f"{SITE}/", "description": description,
         "logo": {"@type": "ImageObject", "url": f"{SITE}/apple-touch-icon.png", "width": 180, "height": 180},
         "sameAs": SAME_AS},
    ]}
    text = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return f'<script type="application/ld+json">{text}</script>\n'


def head(title, description, path, og_title=None, og_description=None, verify=False, noindex=False, css="",
         og_type="website", extra=""):
    """Everything up to the skip link: meta, icons, the Markdown alternate (<path>index.md), the inlined CSS.
    verify adds the webmaster consoles' ownership tags, which only the home page needs. noindex is for the not-found
    page, served at addresses that do not exist: a robots noindex tag instead of the canonical, the Markdown
    alternate and the link-preview tags, which would all name such an address. css is appended to the shared CSS
    for this page only, so the other pages stay as they are. og_type is "article" for a blog post; extra is more
    head tags for this page only (the blog's feed link, a post's date)."""
    verify_meta = "".join(f'<meta name="{e(n)}" content="{e(v)}">\n' for n, v in VERIFY_META.items() if v) if verify else ""
    if noindex:
        page_meta = '<meta name="robots" content="noindex">\n'
    else:
        page_meta = f"""<link rel="alternate" type="text/markdown" href="{path}index.md" title="This page as Markdown">
<link rel="canonical" href="{SITE}{path}">
<meta property="og:site_name" content="{e(SITE_NAME)}">
<meta property="og:title" content="{e(og_title)}">
<meta property="og:description" content="{e(og_description)}">
<meta property="og:url" content="{SITE}{path}">
<meta property="og:type" content="{og_type}">
<meta property="og:image" content="{SITE}{SHARE_IMAGE}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{e(SHARE_ALT)}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(og_title)}">
<meta name="twitter:description" content="{e(og_description)}">
<meta name="twitter:image" content="{SITE}{SHARE_IMAGE}">
"""
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(description)}">
{verify_meta}<meta name="color-scheme" content="only light">
<link rel="icon" href="/favicon.ico" sizes="32x32">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
{page_meta}{extra}<style>{CSS}{css}</style>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
"""


def topbar(path):
    """The sticky top bar. Away from the home page, its section links lead back to it."""
    home = "" if path == "/" else "/"

    def here(url):
        return ' aria-current="page"' if path == url else ""
    return f"""<header class="top"><div class="wrap">
<a class="brand" href="/">{CLAW}<span>Draconyx</span></a>
<nav aria-label="Sections"><a href="{home}#versus">Versus</a><a class="opt" href="{home}#why">Why</a><a class="opt" href="{home}#language">Language</a><a class="opt" href="{home}#name">Name</a><a class="nr" href="{home}#status">Status</a><a class="opt" href="{C.CHANGELOG_URL}"{here(C.CHANGELOG_URL)}>Changelog</a><a href="{C.BLOG_URL}"{here(C.BLOG_URL)}>Blog</a><a class="opt" href="{C.OPINIONS_URL}"{here(C.OPINIONS_URL)}>Reviews</a><a href="/llms.txt">For agents</a></nav>
</div></header>
"""


def contact_html(text):
    """Escape text and link its last CONTACT_LINK phrase to the contact redirect (the address itself is never printed)."""
    head, phrase, tail = e(text).rpartition(e(C.CONTACT_LINK))
    assert phrase, f"{C.CONTACT_LINK!r} missing from {text!r}"
    return f'{head}<a href="{e(C.CONTACT_URL)}" rel="nofollow">{phrase}</a>{tail}'


def contact_md(text):
    """The Markdown twin of contact_html."""
    head, phrase, tail = text.rpartition(C.CONTACT_LINK)
    assert phrase, f"{C.CONTACT_LINK!r} missing from {text!r}"
    return f"{head}[{phrase}]({C.CONTACT_URL}){tail}"


def signup():
    """The closing call to action: the launch-updates form and the way to get in early.

    The form posts to listmonk, which refuses a sign-up without a solved CAPTCHA or with its honeypot filled
    (README, "Signup form"). The honeypot is listmonk's own nonce field, kept out of sight with CSS, not with
    type="hidden" (bots skip those). The ALTCHA widget solves the challenge when the form is sent (auto="onsubmit").
    """
    uuid = C.LISTMONK_LIST_UUID
    if uuid:
        form = (f'<form class="signup" method="post" action="{e(C.LISTMONK_FORM_URL)}">'
                f'<input type="hidden" name="l" value="{e(uuid)}">'
                f'<label class="vh" for="em">Your email address</label>'
                f'<input id="em" type="email" name="email" required placeholder="you@example.com" autocomplete="email">'
                f'<div class="hp" aria-hidden="true"><label for="nonce">{e(C.HONEYPOT_LABEL)}</label>'
                f'<input id="nonce" type="text" name="nonce" value="" tabindex="-1" autocomplete="off"></div>'
                f'<button type="submit">Keep me posted</button>'
                f'<altcha-widget challengeurl="{e(C.ALTCHA_CHALLENGE_URL)}" auto="onsubmit" hidelogo hidefooter>'
                f'</altcha-widget><p class="note check">{e(C.SIGNUP_CHECK)}</p></form>'
                f'<noscript><p class="note">{e(C.SIGNUP_NOSCRIPT)}</p></noscript>'
                f'<p class="note">{e(C.SIGNUP_FINE)}</p>'
                f'<script src="/{ALTCHA_JS}" defer></script>')
    else:
        form = '<p class="note">An update list opens at launch.</p>'
    involved = contact_html(C.INVOLVED)
    return f"""<section id="involved" class="cta"><div class="wrap prose">
<h2 id="updates">{e(C.SIGNUP_TITLE)}</h2>
<p class="lead">{e(C.SIGNUP_LEAD)}</p>
{form}
<h3>Get in early</h3>
<p>{involved}</p>
</div></section>
"""


def footer(md_path):
    """The footer. md_path is the page's Markdown version; None (the not-found page has none) leaves that link out."""
    privacy = contact_html(C.PRIVACY)
    md_link = f' &middot; <a href="{md_path}">This page as Markdown</a>' if md_path else ""
    return f"""<footer><div class="wrap">
<span>{CLAW}Draconyx, a language designed by <a href="https://www.linkedin.com/in/filippofadda/" rel="author">Filippo F. Fadda</a>.</span>
<span><a href="{C.CHANGELOG_URL}">Changelog</a> &middot; <a href="{C.BLOG_URL}">Blog</a>{md_link} &middot; <a href="/llms.txt">llms.txt</a></span>
<p class="privacy" id="privacy"><b>Privacy.</b> {privacy}</p>
</div></footer>
</body>
</html>
"""


def opinions_teaser():
    """Home page section: each model's headline quote, leading to the opinions page."""
    cards = "".join(
        f'<figure class="tcard"><figcaption class="who">{model_icon(o["id"], "t")}<span>'
        f'<a href="{C.OPINIONS_URL}#{o["id"]}">{e(o["name"])}</a><small>{e(o["maker"])}</small></span></figcaption>'
        f'<blockquote><p>{quote(o["headline"])}</p></blockquote></figure>' for o in C.OPINIONS)
    return f"""<section id="reviews"><div class="wrap">
<p class="kicker">Second opinions</p>
<h2>Six AI models read the spec</h2>
<p class="lede">{e(C.OPINIONS_LEDE)}</p>
<div class="tgrid">{cards}</div>
<div class="btns start"><a class="btn" href="{C.OPINIONS_URL}">Read what they said</a></div>
</div></section>
"""


def build_opinions_html():
    """The opinions page: per model, a headline quote and one or two quotes per question."""
    path = C.OPINIONS_URL
    roster = "".join(f'<li><a href="#{o["id"]}">{model_icon(o["id"], "r")}{e(o["name"])}</a></li>' for o in C.OPINIONS)
    asks = "".join(f'<li><span class="num">{i:02d}</span><span>{e(q)}</span></li>'
                   for i, q in enumerate(C.OPINIONS_QUESTIONS, 1))
    cards = []
    for o in C.OPINIONS:
        by = f'By {e(o["maker"])}' + (f' &middot; {e(o["note"])}.' if o.get("note") else "")
        quotes = "".join(f'<li><span class="qtag">{e(t)}</span><blockquote><p>{quote(q)}</p></blockquote></li>'
                         for t, q in o["quotes"])
        cards.append(
            f'<article class="opinion" id="{o["id"]}"><div class="ohead">{model_icon(o["id"], "c")}'
            f'<div><h2>{e(o["name"])}</h2><p class="maker">{by}</p></div></div>'
            f'<blockquote class="pull"><p>{quote(o["headline"])}</p></blockquote>'
            f'<ul class="quotes">{quotes}</ul></article>')
    names = ", ".join(o["name"] for o in C.OPINIONS)
    src_name, src_url = C.OPINIONS_ICONS_SOURCE
    return head(C.OPINIONS_TITLE, f"{C.OPINIONS_LEDE} Verbatim excerpts from {names}.", path,
                C.OPINIONS_TITLE, C.OPINIONS_LEDE) + topbar(path) + f"""<main id="main">
<div class="hero page"><div class="wrap">
<p class="eyebrow">Second opinions</p>
<h1>{e(C.OPINIONS_HEADLINE)}</h1>
<p class="sub">{e(C.OPINIONS_LEDE)}</p>
<ul class="roster">{roster}</ul>
</div></div>

<section id="setup" class="setup"><div class="wrap">
<p class="kicker">The setup</p>
<h2>Same four questions for every model</h2>
<ol class="asks">{asks}</ol>
<p class="note">{e(C.OPINIONS_METHOD)}</p>
</div></section>

<section id="answers"><div class="wrap">
<div class="opinions">{''.join(cards)}</div>
<p class="note credits">{e(C.OPINIONS_CREDITS)} Icons: <a href="{e(src_url)}">{e(src_name)}</a>, MIT License.</p>
</div></section>

{signup()}</main>
""" + footer(path + "index.md")


MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
          "November", "December"]


def long_date(iso):
    """2026-11-02 -> 2 November 2026."""
    y, m, d = (int(x) for x in iso.split("-"))
    return f"{d} {MONTHS[m - 1]} {y}"


def changelog_months():
    """The changelog's entries grouped by month, in the order given (newest first): [(yyyy-mm, "Month yyyy", entries)]."""
    months = []
    for entry in C.CHANGELOG:
        key = entry["date"][:7]
        if not months or months[-1][0] != key:
            y, m = (int(x) for x in key.split("-"))
            months.append((key, f"{MONTHS[m - 1]} {y}", []))
        months[-1][2].append(entry)
    return months


def build_changelog_html():
    """The changelog page: dated entries, newest first, grouped by month; each change tagged with its area."""
    path = C.CHANGELOG_URL
    months = changelog_months()
    jump = "".join(f'<li><a href="#{k}">{e(name)}</a></li>' for k, name, _ in months)
    blocks = []
    for key, name, entries in months:
        arts = []
        for en in entries:
            y, m, d = (int(x) for x in en["date"].split("-"))
            changes = "".join(f'<li><span class="qtag">{e(area)}</span><p>{md(text)}</p></li>'
                              for area, text, _evidence in en["items"])
            arts.append(f'<article class="entry" id="{en["date"]}"><div class="ehead">'
                        f'<time class="num" datetime="{en["date"]}">{d} {MONTHS[m - 1][:3]}</time>'
                        f'<h3>{e(en["title"])}</h3></div><ul class="changes">{changes}</ul></article>')
        blocks.append(f'<div class="month" id="{key}"><h2>{e(name)}</h2><div class="entries">{"".join(arts)}</div></div>')
    return head(C.CHANGELOG_TITLE, f"{C.CHANGELOG_LEDE} Dated, pre-release: no version numbers yet.", path,
                C.CHANGELOG_TITLE, C.CHANGELOG_LEDE) + topbar(path) + f"""<main id="main">
<div class="hero page"><div class="wrap">
<p class="eyebrow">Changelog</p>
<h1>{e(C.CHANGELOG_HEADLINE)}</h1>
<p class="sub">{e(C.CHANGELOG_LEDE)}</p>
<ul class="roster plain" aria-label="Months">{jump}</ul>
</div></div>

<section id="log"><div class="wrap">
<p class="note lognote">{md(C.CHANGELOG_NOTE)}</p>
<div class="log">{''.join(blocks)}</div>
</div></section>

{signup()}</main>
""" + footer(path + "index.md")


def build_changelog_md():
    lines = [f"# {C.CHANGELOG_TITLE}", "", f"> {C.CHANGELOG_LEDE}", "", C.CHANGELOG_NOTE, ""]
    for _key, name, entries in changelog_months():
        lines += [f"## {name}", ""]
        for en in entries:
            lines += [f"### {long_date(en['date'])}: {en['title']}", ""]
            lines += [f"- **{area}:** {text}" for area, text, _evidence in en["items"]] + [""]
    lines += [f"Home: [Draconyx]({SITE}/) · [llms.txt]({SITE}/llms.txt)", ""]
    return "\n".join(lines)


# The blog (README, "Blog"): one Markdown file per post in posts/, rendered at /blog/<slug>/ with a Markdown copy
# (/blog/<slug>/index.md), listed newest first at /blog/ and in the Atom feed /blog/feed.xml. A post's other files
# (images) go in posts/<slug>/ and are copied next to it, hidden files (.DS_Store) left out. Posts marked draft: true are built only with --drafts.
# Markdown and code highlighting use mistune and Pygments (requirements.txt), imported only when the blog is built,
# so indexnow.py, which imports this file, still needs nothing but the standard library.
POSTS_DIR = os.path.join(HERE, "posts")
BLOG_FEED = C.BLOG_URL + "feed.xml"
AUTHOR = ("Filippo F. Fadda", "https://www.linkedin.com/in/filippofadda/")  # as in the footer
POST_KEYS = {"title", "date", "summary", "tags", "draft"}
POST_SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
# Blog pages only, passed to head() like NOT_FOUND_CSS, so the other pages do not change. The reading column, the
# article's own elements, and Pygments' token classes mapped onto the site's code colours. Pygments' classes carry the
# prefix t- (PYGMENTS_PREFIX): bare, its number class "m" would be the comparison table's mark.
BLOG_CSS = (
    ".hero.page .meta{display:flex;flex-wrap:wrap;gap:8px 12px;justify-content:center;align-items:center;margin:0;"
    "color:var(--muted);font-size:15px;font-weight:600}"
    ".hero.page .meta+.feedlink{margin-top:18px}.feedlink{margin:0;font-size:15px;font-weight:600}"
    ".pill.tag{color:var(--olive);background:color-mix(in srgb,var(--olive) 12%,transparent)}"
    ".posts{display:grid;gap:22px;max-width:860px;margin:0 auto}"
    ".posts .entry:hover{--edge:var(--olive)}.ehead h2{margin:0;font-size:clamp(21px,2.4vw,26px)}"
    ".ehead h2 a{color:var(--fg);text-decoration:none}.ehead h2 a:hover{color:var(--ember)}"
    ".entry .psum{margin:14px 0 0;color:var(--muted);max-width:70ch}.entry .tags{display:flex;flex-wrap:wrap;gap:8px;"
    "margin:14px 0 0}"
    ".posts-empty{max-width:860px;margin:0 auto}"
    ".post{max-width:720px;margin:0 auto;font-size:18px;line-height:1.7;overflow-wrap:break-word}"
    ".post>:first-child{margin-top:0}.post>:last-child{margin-bottom:0}"
    ".post h2{font-size:clamp(26px,3.2vw,33px);margin:52px 0 14px;scroll-margin-top:80px}"
    ".post h3{font-size:clamp(21px,2.5vw,25px);margin:38px 0 10px;scroll-margin-top:80px}"
    ".post h4,.post h5,.post h6{font-size:18px;margin:30px 0 8px;scroll-margin-top:80px}"
    ".post p,.post ul,.post ol{margin:0 0 22px}.post ul,.post ol{padding-left:26px}.post li{margin:6px 0}"
    ".post li>ul,.post li>ol,.post li>p{margin:6px 0}.post li::marker{color:var(--olive);font-weight:700}"
    ".post blockquote{margin:30px 0;padding:2px 0 2px 22px;border-left:4px solid var(--olive);"
    "font:500 20px/1.5 ui-serif,\"New York\",\"Iowan Old Style\",Georgia,serif}"
    ".post blockquote p{margin:0 0 12px}.post blockquote>:last-child{margin-bottom:0}"
    ".post a{text-underline-offset:2px}"
    ".post .notice{margin:30px 0;padding:14px 18px 15px;background:var(--gap-bg);clip-path:var(--cut-s);font-size:16px;"
    "line-height:1.55}.post .notice p{margin:0 0 8px}.post .notice>:last-child{margin-bottom:0}"
    ".post .notice strong{color:var(--gap)}.post .notice code{background:var(--card)}"
    ".post .notice+pre{margin-top:-18px}"
    ".post code{background:var(--chip);padding:1px 5px;border-radius:5px;font-size:.86em}"
    ".post pre{margin:30px 0;font-size:14px}.post pre code{background:none;padding:0;border-radius:0;font-size:inherit}"
    ".post img{display:block;max-width:100%;height:auto;margin:30px auto}"
    ".post table{display:block;max-width:100%;overflow-x:auto;border-collapse:collapse;margin:30px 0;font-size:15.5px;"
    "line-height:1.5}"
    ".post th,.post td{padding:9px 14px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}"
    ".post thead th{background:var(--bg2);font-weight:750;border-bottom:2px solid var(--shadow)}"
    ".post hr{border:0;border-top:1px solid var(--line);margin:44px 0}"
    ".post-foot{max-width:720px;margin:48px auto 0;padding-top:20px;border-top:1px solid var(--line);font-size:15px;"
    "font-weight:600}"
    + ",".join(f"pre .t-{c}" for c in "c ch cm cp cpf c1 cs gp".split()) + "{color:var(--code-c)}"
    + ",".join(f"pre .t-{c}" for c in "s sa sb sc dl sd s2 se sh si sx sr s1 ss".split()) + "{color:var(--code-s)}"
    + ",".join(f"pre .t-{c}" for c in "k kc kd kn kp kr kt ow nt".split()) + "{color:var(--code-k)}"
)
PYGMENTS_PREFIX = "t-"


def post_error(path, message):
    sys.exit(f"{os.path.relpath(path, HERE)}: {message}")


def unquote(value):
    """A front-matter value, without the quotes it may be written in."""
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def read_post(path):
    """One post: its front matter checked and parsed, its Markdown body, its slug (the file name)."""
    slug = os.path.basename(path)[:-len(".md")]
    if not POST_SLUG.fullmatch(slug):
        post_error(path, "the file name is the address: lowercase letters, digits and single hyphens, such as "
                         "my-first-post.md")
    with open(path, encoding="utf-8-sig") as f:
        text = f.read().replace("\r\n", "\n")
    m = re.match(r"---\n(.*?)\n---[ \t]*(?:\n|$)", text, re.S)
    if not m:
        post_error(path, "it must start with front matter: a line ---, then title, date and summary, then ---")
    meta = {}
    for line in m.group(1).split("\n"):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        key, sep, value = line.partition(":")
        key = key.strip()
        if not sep or key not in POST_KEYS:
            post_error(path, f"unknown front-matter line {line!r}; the keys are {', '.join(sorted(POST_KEYS))}")
        if key in meta:
            post_error(path, f"{key} is given twice")
        meta[key] = unquote(value.strip())
    for key in ("title", "date", "summary"):
        if not meta.get(key):
            post_error(path, f"the front matter needs a {key}")
    try:
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", meta["date"]):
            raise ValueError
        datetime.date.fromisoformat(meta["date"])
    except ValueError:
        post_error(path, f"date {meta['date']!r} is not a date written YYYY-MM-DD")
    tags = meta.get("tags", "").strip()
    if tags.startswith("[") and tags.endswith("]"):
        tags = tags[1:-1]
    tags = [q2 or q1 or bare.strip() for q1, q2, bare in re.findall(r'\s*(?:"([^"]*)"|\'([^\']*)\'|([^,]+))\s*(?:,|$)', tags)]
    tags = [t for t in tags if t]
    if any('"' in t or "'" in t for t in tags):
        post_error(path, f"tags {meta['tags']!r}: put each tag in quotes whole, or not at all")
    draft = meta.get("draft", "false").lower()
    if draft not in ("true", "false"):
        post_error(path, f"draft is true or false, not {meta['draft']!r}")
    return {"slug": slug, "path": path, "title": meta["title"], "date": meta["date"], "summary": meta["summary"],
            "tags": tags, "draft": draft == "true", "body": text[m.end():].strip("\n") + "\n",
            "url": f"{C.BLOG_URL}{slug}/"}


def load_posts(drafts):
    """The posts to build, newest first (same day: by title). Drafts only when drafts is true."""
    if not os.path.isdir(POSTS_DIR):
        return []
    posts = [read_post(os.path.join(POSTS_DIR, n)) for n in sorted(os.listdir(POSTS_DIR)) if n.endswith(".md")]
    posts = [p for p in posts if drafts or not p["draft"]]
    posts.sort(key=lambda p: p["title"].lower())
    posts.sort(key=lambda p: p["date"], reverse=True)
    for p in posts:
        p["html"] = render_post(p)
    return posts


def render_post(post):
    """A post's Markdown body as HTML. Headings start at ## (the title is the page's h1) and get ids for anchors.
    Code blocks are highlighted here, at build time: ```draconyx with the site's own highlighter, any other language
    Pygments knows with Pygments, both in the site's code colours; a block with no language stays plain. Raw HTML in a
    post is kept as written: posts are the site's own."""
    try:
        import mistune
        import pygments
        from pygments.formatters import HtmlFormatter
        from pygments.lexers import get_lexer_by_name
        from pygments.util import ClassNotFound
    except ImportError:
        sys.exit("the blog needs mistune and Pygments (README, \"Setup\"): python3 -m venv .venv, then "
                 ".venv/bin/python3 -m pip install -r requirements.txt, then build with .venv/bin/python3 build.py")
    seen = {"main", "post", "involved", "updates", "em", "nonce", "privacy"}  # the page's own ids

    class Renderer(mistune.HTMLRenderer):
        def heading(self, text, level, **attrs):
            if level == 1:
                post_error(post["path"], f"heading {text!r} is a level-1 heading: start at ## (the title is the h1)")
            plain = html.unescape(re.sub(r"<[^>]+>", "", text))
            base = re.sub(r"[^a-z0-9]+", "-", plain.lower()).strip("-") or "section"
            hid, n = base, 2
            while hid in seen:
                hid, n = f"{base}-{n}", n + 1
            seen.add(hid)
            return f'<h{level} id="{hid}">{text}</h{level}>\n'

        def block_code(self, code, info=None):
            lang = info.split()[0].lower() if info and info.strip() else ""
            code = code[:-1] if code.endswith("\n") else code
            if lang == "draconyx":
                body = highlight("draconyx", code)
            elif lang:
                try:
                    lexer = get_lexer_by_name(lang)
                except ClassNotFound:
                    post_error(post["path"], f"code block language {lang!r} is not one Pygments knows "
                                             "(use draconyx, or a Pygments name such as python, json, sh or console)")
                body = pygments.highlight(code, lexer, HtmlFormatter(nowrap=True, classprefix=PYGMENTS_PREFIX)).rstrip("\n")
            else:
                body = e(code)
            label = f"Code sample ({e(lang)})" if lang else "Code sample"
            return f'<pre tabindex="0" role="region" aria-label="{label}"><code>{body}</code></pre>\n'

        def block_quote(self, text):
            # GitHub's alert syntax, "> [!WARNING]" on the quote's first line: a notice box, not a quotation. The
            # Markdown copy keeps the syntax, which GitHub and most Markdown viewers show as an alert too.
            m = re.match(r"<p>\[!WARNING\][ \t]*\n?", text)
            if not m:
                return super().block_quote(text)
            body = re.sub(r"^<p>\s*</p>\n?", "", "<p>" + text[m.end():])
            return f'<aside class="notice" role="note">\n{body}</aside>\n'

        def image(self, text, url, title=None):
            return super().image(text, url, title)[:-3] + ' loading="lazy" decoding="async">'

    to_html = mistune.create_markdown(renderer=Renderer(escape=False), plugins=["table", "strikethrough", "url"])
    return to_html(post["body"])


def post_meta(post):
    """The line under a post's title: the date, a draft mark (preview builds only) and the tags."""
    draft = '<span class="pill gaps">Draft</span>' if post["draft"] else ""
    tags = "".join(f'<span class="pill tag">{e(t)}</span>' for t in post["tags"])
    return f'<time datetime="{post["date"]}">{long_date(post["date"])}</time>{draft}{tags}'


def blog_head(title, description, path, og_title, og_description, post=None):
    """head() for the blog's pages: their CSS, the feed link, and for a post its type and date. A draft (built only
    for a preview) is also noindex."""
    extra = f'<link rel="alternate" type="application/atom+xml" href="{BLOG_FEED}" title="{e(C.BLOG_TITLE)}">\n'
    if post:
        extra += f'<meta property="article:published_time" content="{post["date"]}">\n'
        for t in post["tags"]:
            extra += f'<meta property="article:tag" content="{e(t)}">\n'
        if post["draft"]:
            extra += '<meta name="robots" content="noindex">\n'
    return head(title, description, path, og_title, og_description, css=BLOG_CSS,
                og_type="article" if post else "website", extra=extra)


def build_blog_html(posts):
    """The blog's index: every post, newest first, with its date, title, summary and tags."""
    path = C.BLOG_URL
    cards = []
    for p in posts:
        y, m, d = (int(x) for x in p["date"].split("-"))
        draft = '<span class="pill gaps">Draft</span>' if p["draft"] else ""
        tags = "".join(f'<span class="pill tag">{e(t)}</span>' for t in p["tags"])
        tags = f'<p class="tags">{draft}{tags}</p>' if draft or tags else ""
        cards.append(f'<article class="entry"><div class="ehead">'
                     f'<time class="num" datetime="{p["date"]}">{d} {MONTHS[m - 1][:3]} {y}</time>'
                     f'<h2><a href="{p["url"]}">{e(p["title"])}</a></h2></div>'
                     f'<p class="psum">{md(p["summary"])}</p>{tags}</article>')
    listing = (f'<div class="posts">{"".join(cards)}</div>' if cards
               else f'<p class="note posts-empty">{e(C.BLOG_EMPTY)}</p>')
    return blog_head(C.BLOG_TITLE, C.BLOG_LEDE, path, C.BLOG_TITLE, C.BLOG_LEDE) + topbar(path) + f"""<main id="main">
<div class="hero page"><div class="wrap">
<p class="eyebrow">Blog</p>
<h1>{e(C.BLOG_HEADLINE)}</h1>
<p class="sub">{e(C.BLOG_LEDE)}</p>
<p class="feedlink"><a href="{BLOG_FEED}">{e(C.BLOG_FEED_LINK)}</a></p>
</div></div>

<section id="posts"><div class="wrap">
{listing}
</div></section>

{signup()}</main>
""" + footer(path + "index.md")


def build_post_html(post):
    """A post's page: the title, summary and date in the page's hero, then the article in a reading column."""
    path = post["url"]
    return blog_head(f"{post['title']}: {C.BLOG_TITLE}", post["summary"], path, post["title"], post["summary"],
                     post) + topbar(path) + f"""<main id="main">
<div class="hero page"><div class="wrap">
<p class="eyebrow">Blog</p>
<h1>{e(post["title"])}</h1>
<p class="sub">{md(post["summary"])}</p>
<p class="meta">{post_meta(post)}</p>
</div></div>

<section id="post"><div class="wrap">
<article class="post">
{post["html"]}</article>
<p class="post-foot"><a href="{C.BLOG_URL}">{e(C.BLOG_BACK)}</a> &middot; <a href="{BLOG_FEED}">{e(C.BLOG_FEED_LINK)}</a></p>
</div></section>

{signup()}</main>
""" + footer(path + "index.md")


def link_text(text):
    """Text for the [...] of a Markdown link: a bracket in a post's title must not end the link."""
    return re.sub(r"([\\\[\]])", r"\\\1", text)


def build_blog_md(posts):
    lines = [f"# {C.BLOG_TITLE}", "", f"> {C.BLOG_LEDE}", ""]
    lines += [f"- [{link_text(p['title'])}]({SITE}{p['url']}) ({long_date(p['date'])}): {p['summary']} "
              f"([Markdown]({SITE}{p['url']}index.md))" for p in posts] or [C.BLOG_EMPTY]
    lines += ["", f"Feed: [{C.BLOG_FEED_LINK}]({SITE}{BLOG_FEED})", "",
              f"Home: [Draconyx]({SITE}/) · [llms.txt]({SITE}/llms.txt)", ""]
    return "\n".join(lines)


def build_post_md(post):
    """A post as Markdown: the title, summary and date, then the body as written."""
    meta = long_date(post["date"]) + "".join(f" · {t}" for t in post["tags"])
    return "\n".join([f"# {post['title']}", "", f"> {post['summary']}", "", f"_{meta}_", "", post["body"].rstrip("\n"), "",
                      f"Blog: [{C.BLOG_TITLE}]({SITE}{C.BLOG_URL}) · Home: [Draconyx]({SITE}/) · "
                      f"[llms.txt]({SITE}/llms.txt)", ""])


def post_lastmod(post):
    """A post's sitemap date: the last commit to its file (and its folder), or its date if that is later."""
    return max(filter(None, [post["date"], last_modified(os.path.relpath(post["path"], HERE),
                                                         os.path.relpath(post["path"], HERE)[:-len(".md")])]))


def atom_time(day):
    return f"{day}T00:00:00Z"


def build_feed(posts):
    """The Atom feed: every published post, newest first, with its full text. Drafts never go in, even with
    --drafts. xml:base makes the posts' relative links resolve in feed readers."""
    posts = [p for p in posts if not p["draft"]]
    updated = max([post_lastmod(p) for p in posts] or [last_modified() or datetime.date.today().isoformat()])
    entries = "".join(
        f"""<entry>
<title>{e(p["title"])}</title>
<link rel="alternate" type="text/html" href="{SITE}{p["url"]}"/>
<id>{SITE}{p["url"]}</id>
<published>{atom_time(p["date"])}</published>
<updated>{atom_time(post_lastmod(p))}</updated>
<summary>{e(p["summary"])}</summary>
{"".join(f'<category term="{e(t)}"/>' for t in p["tags"])}<content type="html" xml:base="{SITE}{p["url"]}">{e(p["html"])}</content>
</entry>
""" for p in posts)
    return f"""<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom" xml:lang="en">
<title>{e(C.BLOG_TITLE)}</title>
<subtitle>{e(C.BLOG_LEDE)}</subtitle>
<link rel="self" type="application/atom+xml" href="{SITE}{BLOG_FEED}"/>
<link rel="alternate" type="text/html" href="{SITE}{C.BLOG_URL}"/>
<id>{SITE}{C.BLOG_URL}</id>
<updated>{atom_time(updated)}</updated>
<author><name>{e(AUTHOR[0])}</name><uri>{e(AUTHOR[1])}</uri></author>
<icon>{SITE}/apple-touch-icon.png</icon>
{entries}</feed>
"""


def blog_files(posts):
    """{dist path: text} for the blog: its index, its feed and each post, each page with its Markdown copy."""
    base = C.BLOG_URL.strip("/")
    files = {f"{base}/index.html": build_blog_html(posts), f"{base}/index.md": build_blog_md(posts),
             f"{base}/feed.xml": build_feed(posts)}
    for p in posts:
        files[f"{base}/{p['slug']}/index.html"] = build_post_html(p)
        files[f"{base}/{p['slug']}/index.md"] = build_post_md(p)
    return files


def copy_post_assets(posts):
    """A post's own files, posts/<slug>/ (images and the like), go next to its page, dist/blog/<slug>/."""
    for p in posts:
        src = p["path"][:-len(".md")]
        if not os.path.isdir(src):
            continue
        clash = {"index.html", "index.md"} & set(os.listdir(src))
        if clash:
            post_error(src, f"{', '.join(sorted(clash))} would overwrite the post's own page")
        shutil.copytree(src, os.path.join(OUT, C.BLOG_URL.strip("/"), p["slug"]), dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns(".*"))  # no .DS_Store and the like


# The not-found page, written as 404.html. Caddy serves it with status 404 at any address on draconyx.ai that has no
# file (README, "Not found"), at any depth, so every link and asset on it is root-relative. It is not in PAGES, so the
# sitemap and IndexNow leave it out. It fills the window, so a short page ends on the footer, not on blank cream.
NOT_FOUND_FILE = "404.html"
NOT_FOUND_CSS = ("body:has(.nf){display:flex;flex-direction:column;min-height:100vh}"
                 "body:has(.nf) main{flex:1;display:flex;flex-direction:column}"
                 ".hero.nf{flex:1;display:flex;align-items:center}.hero.nf .wrap{width:100%}"
                 ".nf .logo{width:min(360px,100%)}")


def build_not_found_html():
    """The not-found page: the site's top bar and footer, the logo, a heading, one line and the way home. No signup
    form, no Markdown version; noindex."""
    return head(C.NOT_FOUND_TITLE, C.NOT_FOUND_LINE, None, noindex=True, css=NOT_FOUND_CSS) \
        + topbar("/" + NOT_FOUND_FILE) + f"""<main id="main">
<div class="hero page nf"><div class="wrap">
<img class="logo" src="/assets/logo-640.webp" srcset="/assets/logo-640.webp 640w, /assets/logo-1200.webp 1200w" sizes="(max-width:392px) 100vw, 360px" width="640" height="427" alt="Draconyx: a dinosaur mascot above the Draconyx wordmark.">
<h1>{e(C.NOT_FOUND_HEADLINE)}</h1>
<p class="sub">{e(C.NOT_FOUND_LINE)}</p>
<div class="btns"><a class="btn primary" href="/">{e(C.NOT_FOUND_HOME)}</a></div>
</div></div>
</main>
""" + footer(None)


def build_md(posts=()):
    lines = ["# Draconyx", "", f"> {C.HERO['headline']} {C.HERO['subhead']}", "",
             "## Every other language was built for humans", ""]
    lines += [p + "\n" for p in C.PROBLEM]
    lines += [f"Spec references: {', '.join(C.PROBLEM_CITES)}", "", "## Built for generate, check, repair", ""]
    lines += [f"{i}. **{t}.** {d}" for i, (t, d) in enumerate(C.LOOP, 1)]
    lines += ["", "## Draconyx vs. the languages your agents write today", "",
              "| Capability | " + " | ".join(C.VERSUS_LANGS) + " |", "|---|" + "---|" * len(C.VERSUS_LANGS)]
    sym = {"yes": "yes", "part": "partly", "no": "no"}
    lines += ["| " + row + " | " + " | ".join(sym[v] for v in vals) + " |" for row, vals in C.VERSUS]
    lines += ["", "**Why \u201cpartly\u201d:**", ""]
    for l, ns in C.VERSUS_NOTES.items():
        lines += [f"- **{l}:** " + " ".join(ns)]
    lines += ["", "## Nine unfair advantages", "", MECH_LEDE, ""]
    for i, r in enumerate(C.REASONS, 1):
        lines += [f"### {i}. {r['title']}", ""] + [p + "\n" for p in r["body"]]
        lines += [f"**Status:** {r['ships']}", "", f"**Elsewhere:** {r['unlike']}", ""]
        if r["sample"]:
            kind, code, cap = r["sample"]
            lang = {"draconyx": "", "json": "json", "shell": "sh", "drx": "text"}[kind]
            lines += [f"```{lang}", code, "```", f"_{cap}_", ""]
        lines += [f"Spec references: {', '.join(r['cites'])}", ""]
    lines += ["## The whole language", ""]
    names = {"ships": "Ships", "partial": "Partly built", "specified": "In the spec"}
    for g, items in C.FEATURE_GROUPS:
        lines += [f"### {g}", ""] + [f"- **{n}** ({names[st]}): {pt}" for n, pt, st in items] + [""]
    lines += ["## Six AI models read the spec", "", C.OPINIONS_LEDE, ""]
    lines += [f"- **{o['name']}** ({o['maker']}): \u201c{o['headline']}\u201d" for o in C.OPINIONS]
    lines += ["", f"Their answers, question by question: [{C.OPINIONS_HEADLINE}]({SITE}{C.OPINIONS_URL}).", ""]
    lines += ["## Dragon claw, written law", ""] + [p + "\n" for p in C.NAME]
    lines += [f"Source: [{C.NAME_SOURCE[0]}]({C.NAME_SOURCE[1]}).", "", f"## Where it stands (as of {C.AS_OF})", ""]
    lines += [f"- **{k}:** {v}" for k, v in C.STATUS]
    lines += ["", f"What changed, by date: [{C.CHANGELOG_TITLE}]({SITE}{C.CHANGELOG_URL})."]
    if posts:  # the blog section, as on the page: the newest posts (drafts only in a --drafts preview, marked)
        lines += ["", f"## {C.BLOG_HEADLINE}", "", C.BLOG_HOME_LEDE, ""]
        lines += [f"- [{link_text(p['title'])}]({SITE}{p['url']}) ({long_date(p['date'])}"
                  + (", draft" if p["draft"] else "") + f"): {p['summary']}" for p in posts[:HOME_POSTS]]
        lines += ["", f"All posts: [{C.BLOG_TITLE}]({SITE}{C.BLOG_URL})."]
    lines += ["", f"## {C.SIGNUP_TITLE}", "", C.SIGNUP_LEAD, "", f"Subscribe: [{C.LISTMONK_FORM_URL}]({C.LISTMONK_FORM_URL}).", ""]
    lines += ["## Get in early", "", contact_md(C.INVOLVED), ""]
    lines += ["## Privacy", "", contact_md(C.PRIVACY), ""]
    return "\n".join(lines)


def build_opinions_md():
    lines = [f"# {C.OPINIONS_HEADLINE}", "", f"> {C.OPINIONS_LEDE}", "", "The four questions:", ""]
    lines += [f"{i}. {q}" for i, q in enumerate(C.OPINIONS_QUESTIONS, 1)]
    lines += ["", C.OPINIONS_METHOD, ""]
    for o in C.OPINIONS:
        by = f"By {o['maker']}" + (f", {o['note']}" if o.get("note") else "")
        lines += [f"## {o['name']}", "", f"_{by}._", "", f"> \u201c{o['headline']}\u201d", ""]
        lines += [f"- **{t}:** \u201c{q}\u201d" for t, q in o["quotes"]] + [""]
    src_name, src_url = C.OPINIONS_ICONS_SOURCE
    lines += [f"{C.OPINIONS_CREDITS} Icons: [{src_name}]({src_url}), MIT License.", "",
              f"Home: [Draconyx]({SITE}/) \u00b7 [llms.txt]({SITE}/llms.txt)", ""]
    return "\n".join(lines)


def build_llms(posts=()):
    """llms.txt. posts: the blog's published posts, newest first; drafts are never listed."""
    posts = [p for p in posts if not p["draft"]]
    out = ["# Draconyx", "",
           "> A programming language designed for code written by AI models and used by AI agents. "
           f"In development: a {C.STATS[0][0]}-page specification and a working compiler, "
           "public at the first release. Each mechanism below says whether it ships, is partly built or is in the spec.", "",
           f"Status as of {C.AS_OF}: " + " ".join(f"{k}: {v}" for k, v in C.STATUS), "",
           "## Mechanisms", ""]
    for r in C.REASONS:
        out.append(f"- [{r['title']}]({SITE}/#{r['id']}): {r['body'][0]} Status: {r['ships']} "
                   f"Spec references: {', '.join(r['cites'])}")
    names = {"ships": "ships", "partial": "partly built", "specified": "in the spec"}
    out += ["", "## Language", ""]
    for g, items in C.FEATURE_GROUPS:
        out += [f"- [{n}]({SITE}/#language): {pt.removesuffix('.')} ({g}; {names[st]})." for n, pt, st in items]
    out += ["", "## Docs", "", f"- [Full page as Markdown]({SITE}/index.md): every mechanism with samples and status.",
            f"- [Why the name]({SITE}/#name): Draconyx, Draco's written laws and the axones.",
            f"- [{C.OPINIONS_TITLE}]({SITE}{C.OPINIONS_URL}): verbatim excerpts from six AI models asked about the "
            f"spec through a service, without knowing who was asking ([Markdown]({SITE}{C.OPINIONS_URL}index.md)).",
            f"- [{C.CHANGELOG_TITLE}]({SITE}{C.CHANGELOG_URL}): what changed in the language, the spec and the "
            f"toolchain, dated, newest first ([Markdown]({SITE}{C.CHANGELOG_URL}index.md)).",
            f"- [{C.BLOG_TITLE}]({SITE}{C.BLOG_URL}): {C.BLOG_LLMS} ([Markdown]({SITE}{C.BLOG_URL}index.md), "
            f"[Atom feed]({SITE}{BLOG_FEED})).",
            f"- [Email us]({C.CONTACT_URL}): design discussion, collaboration, model training or evaluation.",
            f"- [Launch updates]({C.LISTMONK_FORM_URL}): mailing list for the launch and new features (double opt-in).", ""]
    if posts:
        out += ["## Blog", ""]
        out += [f"- [{link_text(p['title'])}]({SITE}{p['url']}) ({p['date']}): {p['summary'].removesuffix('.')} "
                f"([Markdown]({SITE}{p['url']}index.md))." for p in posts] + [""]
    return "\n".join(out)


def last_modified(*paths):
    """Date of the last commit that touched paths (by default, what the pages are built from), as a W3C date, or None
    outside git or before the first commit to them."""
    try:
        out = subprocess.run(["git", "log", "-1", "--format=%cs", "--", *(paths or ("content.py", "build.py", "assets"))],
                             cwd=HERE or ".", capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None
    return out or None


def build_sitemap(posts=()):
    """The canonical pages in PAGES, then the blog and its published posts (drafts never go in). A post's lastmod is
    post_lastmod(); the blog's is the newest of the sources' and its posts'."""
    mod = last_modified()
    lastmod = f"<lastmod>{mod}</lastmod>" if mod else ""
    urls = "".join(f"<url><loc>{e(SITE + p)}</loc>{lastmod}</url>" for p in PAGES)
    posts = [p for p in posts if not p["draft"]]
    post_mods = [post_lastmod(p) for p in posts]
    blog_mod = max(filter(None, [mod, *post_mods]), default=None)
    urls += f"<url><loc>{e(SITE + C.BLOG_URL)}</loc>" + (f"<lastmod>{blog_mod}</lastmod>" if blog_mod else "") + "</url>"
    urls += "".join(f"<url><loc>{e(SITE + p['url'])}</loc><lastmod>{m}</lastmod></url>" for p, m in zip(posts, post_mods))
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')


def main():
    args = sys.argv[1:]
    if set(args) - {"--drafts"}:
        sys.exit("usage: python3 build.py [--drafts]")
    drafts = "--drafts" in args
    posts = load_posts(drafts)
    # The blog is rebuilt whole, so a post removed or turned back into a draft leaves nothing behind.
    shutil.rmtree(os.path.join(OUT, C.BLOG_URL.strip("/")), ignore_errors=True)
    os.makedirs(os.path.join(OUT, "assets"), exist_ok=True)
    for name in ("logo-1200.webp", "logo-640.webp", os.path.basename(SHARE_IMAGE)):
        shutil.copyfile(os.path.join(HERE, "assets", name), os.path.join(OUT, "assets", name))
    os.makedirs(os.path.join(OUT, ALTCHA_DIR), exist_ok=True)
    for path in (ALTCHA_JS, f"{ALTCHA_DIR}/LICENSE.txt"):
        shutil.copyfile(os.path.join(HERE, path), os.path.join(OUT, path))
    # Browsers and apps ask for these at the site root. Made by make_icons.py, committed in assets/.
    for name in ("favicon.ico", "apple-touch-icon.png"):
        shutil.copyfile(os.path.join(HERE, "assets", name), os.path.join(OUT, name))
    files = {
        "index.html": build_html(posts), "index.md": build_md(posts), "llms.txt": build_llms(posts), "favicon.svg": FAVICON,
        "robots.txt": f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n",
        "sitemap.xml": build_sitemap(posts),
        f"{INDEXNOW_KEY}.txt": INDEXNOW_KEY,
        **VERIFY_FILES,
        C.OPINIONS_URL.strip("/") + "/index.html": build_opinions_html(),
        C.OPINIONS_URL.strip("/") + "/index.md": build_opinions_md(),
        C.CHANGELOG_URL.strip("/") + "/index.html": build_changelog_html(),
        C.CHANGELOG_URL.strip("/") + "/index.md": build_changelog_md(),
        NOT_FOUND_FILE: build_not_found_html(),
        **blog_files(posts),
    }
    copy_post_assets(posts)
    for name, text in files.items():
        os.makedirs(os.path.dirname(os.path.join(OUT, name)), exist_ok=True)
        with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
            f.write(text)
    print("built", ", ".join(f"{n} ({len(t.encode())} B)" for n, t in files.items()))
    shown = [p["slug"] for p in posts if p["draft"]]
    if shown:
        print(f"DRAFTS INCLUDED ({', '.join(shown)}): a preview build, do not deploy this dist/")


if __name__ == "__main__":
    main()
