#!/usr/bin/env python3
"""Build draconyx.ai into dist/ from content.py: index.html, index.md, llms.txt, assets, favicon.svg,
robots.txt, sitemap.xml. No external requests at runtime: no web fonts, scripts or trackers.

    python3 build.py            # writes dist/
"""
import html
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(__file__))
import content as C  # noqa: E402

HERE = os.path.dirname(__file__)
OUT = os.path.join(HERE, "dist")
SITE = "https://draconyx.ai"
MECH_LEDE = "Real mechanisms in a real compiler. Every sample on this page was run through it."
e = html.escape

# Three talons: the "claw" in Draconyx.
CLAW_PATHS = ('<path d="M14 54C10 38 14 20 30 8C22 24 22 40 26 54Z"/>'
              '<path d="M28 56C26 40 32 24 48 14C40 30 38 44 40 56Z"/>'
              '<path d="M42 58C42 46 48 36 60 30C54 42 52 50 54 58Z"/>')
CLAW = f'<svg class="claw" viewBox="0 0 64 64" aria-hidden="true" focusable="false">{CLAW_PATHS}</svg>'
FAVICON = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" '
           f'fill="#5b6b25"/><g fill="#f4ecd8">{CLAW_PATHS}</g></svg>')

KEYWORDS = {"def", "let", "match", "enum", "capability", "law", "provide", "locally", "in", "example",
            "transfer", "borrow", "tainted", "if", "else", "for", "return", "struct"}


def highlight(kind, text):
    """Tiny, safe highlighter: comments, strings, keywords, AX codes. Escapes everything."""
    out = []
    for line in text.split("\n"):
        code, comment = line, ""
        m = re.search(r"(//.*$)" if kind == "draconyx" else r"((?:^|\s)#\s.*$)", line)
        if m:
            code, comment = line[: m.start(1)], line[m.start(1):]
        parts = re.split(r'("(?:[^"\\]|\\.)*")', code)
        buf = []
        for i, p in enumerate(parts):
            if i % 2 == 1:
                buf.append(f'<span class="s">{e(p)}</span>')
                continue
            p = e(p)
            if kind == "draconyx":
                p = re.sub(r"\b(" + "|".join(sorted(KEYWORDS)) + r")\b", r'<span class="k">\1</span>', p)
            p = re.sub(r"\b(AX\d{4})\b", r'<span class="ax">\1</span>', p)
            buf.append(p)
        if comment:
            c = re.sub(r"\b(AX\d{4})\b", r'<span class="ax">\1</span>', e(comment))
            buf.append(f'<span class="c">{c}</span>')
        out.append("".join(buf))
    return "\n".join(out)


def md(text):
    """Escape, then turn `backticks` into <code>."""
    return re.sub(r"`([^`]+)`", r"<code>\1</code>", e(text))


def cites_html(cites):
    return ('<details class="cites"><summary>Spec references</summary><p>'
            + ", ".join(f"<code>{e(c)}</code>" for c in cites) + "</p></details>")


CSS = """
:root{--bg:#f6efdf;--bg2:#efe4cc;--card:#fffaf0;--fg:#1c1a14;--muted:#5c5545;--line:#ddcfae;
--olive:#5b6b25;--ember:#b63e15;--ember2:#e8501f;--ink:#15130f;
--code-bg:#1d1b15;--code-fg:#efe8d8;--code-c:#9d9583;--code-s:#e9bd7c;--code-k:#f08a5d;--code-ax:#d7e48a;
--chip:#efe2c4;--ok:#45601a;--ok-bg:#e3ead0;--gap:#7d5200;--gap-bg:#f6e3b5;--shadow:#15130f}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#13140f;--bg2:#1a1c14;--card:#1c1e16;--fg:#efe9da;
--muted:#aaa48f;--line:#2f3224;--olive:#a6b85a;--ember:#f07a4f;--ember2:#ff8a5c;--code-bg:#0c0d09;--code-c:#958d7c;
--chip:#272a1e;--ok:#c2d36f;--ok-bg:#262c18;--gap:#f1c56a;--gap-bg:#33290f;--shadow:#000}}
:root[data-theme="dark"]{--bg:#13140f;--bg2:#1a1c14;--card:#1c1e16;--fg:#efe9da;--muted:#aaa48f;--line:#2f3224;--olive:#a6b85a;
--ember:#f07a4f;--ember2:#ff8a5c;--code-bg:#0c0d09;--code-c:#958d7c;--chip:#272a1e;--ok:#c2d36f;--ok-bg:#262c18;
--gap:#f1c56a;--gap-bg:#33290f;--shadow:#000}
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
nav{white-space:nowrap}@media (max-width:720px){nav a.opt{display:none}}@media (max-width:420px){nav a{margin-left:12px;font-size:14px}.brand{font-size:15px}}
.hero{position:relative;overflow:hidden;background:
 radial-gradient(1100px 520px at 50% 108%,color-mix(in srgb,var(--olive) 30%,transparent),transparent 70%),
 radial-gradient(700px 360px at 8% 0%,color-mix(in srgb,var(--ember2) 16%,transparent),transparent 70%),var(--bg)}
.hero::after{content:"";position:absolute;inset:auto 0 0 0;height:90px;background:repeating-linear-gradient(0deg,transparent 0 13px,color-mix(in srgb,var(--olive) 14%,transparent) 13px 15px);-webkit-mask:linear-gradient(transparent,#000);mask:linear-gradient(transparent,#000)}
.hero .wrap{position:relative;z-index:1;text-align:center;padding-top:40px;padding-bottom:80px}
.logo{display:block;width:min(720px,100%);height:auto;margin:0 auto 6px;filter:drop-shadow(0 18px 28px rgba(40,30,10,.18));animation:rise .9s cubic-bezier(.2,.8,.2,1) both}
.eyebrow{display:inline-block;text-transform:uppercase;letter-spacing:.14em;font-size:13px;font-weight:750;color:var(--olive);background:color-mix(in srgb,var(--olive) 12%,transparent);border:1px solid color-mix(in srgb,var(--olive) 30%,transparent);padding:6px 12px;border-radius:999px;margin:8px 0 18px}
h1,h2,h3{font-family:ui-serif,"New York","Iowan Old Style",Georgia,"Times New Roman",serif;font-weight:650;letter-spacing:-.012em;line-height:1.12}
h1{font-size:clamp(34px,5.6vw,62px);margin:0 auto 20px;max-width:18ch}
.hero .sub{font-size:clamp(17px,2vw,20px);color:var(--muted);max-width:64ch;margin:0 auto 30px}
.btns{display:flex;flex-wrap:wrap;gap:12px;justify-content:center}
.btn{display:inline-block;padding:12px 20px;border-radius:999px;border:2px solid var(--shadow);color:var(--fg);text-decoration:none;font-weight:700;font-size:15px;background:var(--card);box-shadow:0 3px 0 var(--shadow);transition:transform .12s,box-shadow .12s}
.btn:hover{transform:translateY(-2px);box-shadow:0 5px 0 var(--shadow);color:var(--fg)}
.btn.primary{background:var(--ember2);color:#1a0c05}.btn.primary:hover{color:#1a0c05}
.btn:focus-visible{border-radius:999px}
@keyframes rise{from{opacity:0;transform:translateY(24px) scale(.98)}to{opacity:1;transform:none}}
@media (max-width:720px){.hero .wrap{padding-top:20px;padding-bottom:56px}}
.stats{background:var(--olive);color:#f6f1df}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]) .stats{background:#2b3315}}
.stats ul{list-style:none;padding:30px 16px;display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:18px;max-width:1120px;margin:0 auto}
.stats li{text-align:center}.stats b{display:block;font:800 clamp(30px,4vw,44px)/1 ui-serif,Georgia,serif;letter-spacing:-.02em;color:#fff3c9}
.stats span{display:block;font-size:14px;margin-top:6px;opacity:.92}
@media (max-width:820px){.stats ul{grid-template-columns:repeat(2,minmax(0,1fr))}.stats li:last-child{grid-column:1/-1}}
section{padding:80px 0;border-top:1px solid var(--line)}
h2{font-size:clamp(28px,3.8vw,42px);margin:0 0 16px}
.kicker{font:700 13px/1 ui-monospace,SFMono-Regular,Menlo,monospace;letter-spacing:.1em;text-transform:uppercase;color:var(--ember);margin:0 0 12px}
.lede{color:var(--muted);max-width:70ch;margin:0 0 8px}
.prose p{max-width:70ch}
.loop{list-style:none;padding:0;margin:40px 0 0;display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:22px;counter-reset:s}
.loop li{position:relative;background:var(--card);border:2px solid var(--shadow);border-radius:18px;padding:22px 18px 18px;box-shadow:0 4px 0 var(--shadow)}
.loop li::before{counter-increment:s;content:counter(s);position:absolute;top:-17px;left:16px;width:34px;height:34px;border-radius:50%;background:var(--olive);color:#fff;font:800 15px/30px system-ui,sans-serif;text-align:center;border:2px solid var(--shadow)}
.loop li:not(:last-child)::after{content:"";position:absolute;right:-17px;top:50%;width:12px;height:12px;border-top:3px solid var(--ember2);border-right:3px solid var(--ember2);transform:translateY(-50%) rotate(45deg)}
.loop b{display:block;font-size:17px;margin:6px 0 4px}.loop span{font-size:15px;color:var(--muted)}
@media (max-width:860px){.loop{grid-template-columns:minmax(0,1fr);gap:30px}.loop li:not(:last-child)::after{right:auto;left:50%;top:auto;bottom:-22px;transform:translateX(-50%) rotate(135deg)}}
.vwrap{overflow-x:auto;contain:paint;margin-top:30px;border-radius:20px;border:2px solid var(--shadow);border-bottom-width:6px;background:var(--card)}
table.versus{width:100%;border-collapse:collapse;min-width:1100px;font-size:14.5px}
.versus tbody th{position:sticky;left:0;background:var(--card);z-index:1;min-width:260px}
@media (max-width:600px){.versus tbody th{min-width:150px;max-width:170px;font-size:13px}table.versus{font-size:13px}.versus th,.versus td{padding:10px 8px}}
.versus thead th:first-child{position:sticky;left:0;z-index:2}
.versus th,.versus td{padding:13px 14px;border-bottom:1px solid var(--line);text-align:center}
.versus tbody tr:last-child th,.versus tbody tr:last-child td{border-bottom:0}
.versus thead th{font-size:14px;letter-spacing:.03em;color:var(--muted);font-weight:750;background:var(--bg2)}
.versus tbody th{text-align:left;font-weight:600;max-width:380px}
.versus .us{background:color-mix(in srgb,var(--olive) 14%,transparent)}
.versus thead .us{background:var(--olive);color:#fff;font-size:15px;letter-spacing:.06em;text-transform:uppercase}
.m{display:inline-grid;place-items:center;width:28px;height:28px;border-radius:50%;font-weight:900;font-size:15px}
.m.yes{background:var(--olive);color:#fff}.m.part{background:var(--gap-bg);color:var(--gap)}.m.no{color:var(--muted);opacity:.7}
.vnote{margin-top:14px;max-width:90ch}
details.fine{margin-top:16px;background:var(--card);border:1px solid var(--line);border-radius:16px;padding:14px 18px}
details.fine summary{cursor:pointer;font-weight:700}
details.fine h4{margin:16px 0 6px;font-size:15px}details.fine ul{margin:0;padding-left:20px;font-size:14.5px;color:var(--muted)}
details.fine li{margin:4px 0}
.fgroups{display:grid;gap:34px;margin-top:30px}
.fgroup h3{font-size:clamp(21px,2.4vw,26px);margin:0 0 14px}
.fgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,300px),1fr));gap:16px}
.fcard{background:var(--card);border:1px solid var(--line);border-radius:18px;padding:18px 18px 16px;display:flex;flex-direction:column;gap:8px;transition:transform .2s,box-shadow .2s}
.fcard:hover{transform:translateY(-2px);box-shadow:0 10px 26px rgba(40,30,10,.09)}
.fcard b{font-size:16.5px;line-height:1.3}.fcard p{margin:0;font-size:15px;color:var(--muted)}
.fcard p code{background:var(--chip);padding:1px 5px;border-radius:5px}
.fcard .pill{align-self:flex-start}
.pill.spec{color:var(--muted);background:var(--bg2);border:1px solid var(--line)}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]) .versus thead .us,:root:not([data-theme="light"]) .m.yes{color:#13140f}}
.reasons{display:grid;grid-template-columns:minmax(0,1fr);gap:26px;margin-top:34px}.reason{min-width:0}
.reason{background:var(--card);border:1px solid var(--line);border-radius:22px;padding:30px 30px 24px;transition:transform .2s,box-shadow .2s}
.reason:hover{transform:translateY(-3px);box-shadow:0 14px 36px rgba(40,30,10,.10)}
.rhead{display:flex;align-items:center;gap:12px;flex-wrap:wrap}
.num{font:800 15px/1 ui-monospace,SFMono-Regular,Menlo,monospace;color:#fff;background:var(--olive);border-radius:10px;padding:8px 10px}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]) .num{color:#13140f}}
.pill{font-size:12.5px;font-weight:750;letter-spacing:.04em;text-transform:uppercase;border-radius:999px;padding:5px 10px}
.pill.ships{color:var(--ok);background:var(--ok-bg)}.pill.gaps{color:var(--gap);background:var(--gap-bg)}
h3{font-size:clamp(23px,2.7vw,30px);margin:14px 0 12px}
.rbody{max-width:76ch}.reason p{margin:0 0 14px}
.ships-line{font-size:15px;background:var(--chip);border-radius:12px;padding:10px 14px}
.unlike{font-size:15px;color:var(--muted);border-left:3px solid var(--ember2);padding-left:14px}.unlike b{color:var(--fg)}
.reason p code,dd code,.prose code{background:var(--chip);padding:1px 5px;border-radius:5px}.ships-line code{background:var(--card)}
figure{margin:18px 0 0;min-width:0}
pre{margin:0;background:var(--code-bg);color:var(--code-fg);border-radius:16px;padding:18px 20px;overflow-x:auto;
font:13.5px/1.6 ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,monospace;tab-size:4}
pre .c{color:var(--code-c)}pre .s{color:var(--code-s)}pre .k{color:var(--code-k)}pre .ax{color:var(--code-ax);font-weight:700}
figcaption{font-size:13px;color:var(--muted);margin-top:8px}
code{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:.9em}
.cites{margin-top:10px;font-size:13px;color:var(--muted)}.cites summary{cursor:pointer}.cites code{white-space:nowrap}
@media (max-width:600px){.reason{padding:22px 18px 18px;border-radius:18px}}
.name{background:linear-gradient(180deg,var(--bg2),var(--bg))}
.namegrid{display:grid;grid-template-columns:minmax(0,.9fr) minmax(0,1.1fr);gap:44px;align-items:center}
.namegrid img{width:100%;height:auto;filter:drop-shadow(0 14px 24px rgba(40,30,10,.16))}
@media (max-width:860px){.namegrid{grid-template-columns:minmax(0,1fr)}.namegrid img{max-width:460px;margin:0 auto}}
.src{font-size:13px;color:var(--muted)}
dl.status{display:grid;grid-template-columns:210px minmax(0,1fr);gap:14px 28px;margin:26px 0 0}
dl.status dt{font-weight:750}dl.status dd{margin:0;color:var(--muted)}
@media (max-width:720px){dl.status{grid-template-columns:minmax(0,1fr)}dl.status dd{margin-bottom:10px}}
.cta{background:var(--ink);color:#f3ecda;border-top:0}
.cta h2{color:#fff3c9}.cta a{color:#ffb08f}.cta a:hover{color:#ffd0bd}.cta .note{color:#c9c0a8}
form.signup{display:flex;flex-wrap:wrap;gap:10px;margin:22px 0 8px}
form.signup input[type=email]{flex:1 1 260px;min-width:0;padding:11px 14px;border-radius:999px;border:1px solid #8c8470;background:#1f1d17;color:#f3ecda;font-family:inherit;font-size:16px}
form.signup button{padding:11px 20px;border-radius:999px;border:0;background:var(--ember2);color:#1a0c05;font-family:inherit;font-size:15px;font-weight:700;cursor:pointer}
.note{font-size:14px;color:var(--muted)}
footer{background:var(--ink);color:#bfb69d;border-top:1px solid #2a271f;padding:26px 0 40px;font-size:14px}
footer a{color:#e7dcc0}
footer .wrap{display:flex;flex-wrap:wrap;gap:12px 28px;justify-content:space-between;align-items:center}
footer .claw{fill:#a6b85a;width:22px;height:22px;vertical-align:-5px;margin-right:6px}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}}
"""


def build_html():
    reasons = []
    for i, r in enumerate(C.REASONS, 1):
        pill = ('<span class="pill ships">Ships today</span>' if r["state"] == "ships"
                else '<span class="pill gaps">Ships, with gaps</span>')
        body = "".join(f"<p>{md(p)}</p>" for p in r["body"])
        fig = ""
        if r["sample"]:
            kind, code, cap = r["sample"]
            fig = (f'<figure><pre tabindex="0" role="region" aria-label="{e(r["title"])}: example"><code>'
                   f'{highlight(kind, code)}</code></pre><figcaption>{e(cap)}</figcaption></figure>')
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
    vnote = ("<details class=\"fine\"><summary>Why \u201cpartly\u201d? The fine print, language by language</summary>"
             + "".join(f"<h4>{e(l)}</h4><ul>" + "".join(f"<li>{md(n)}</li>" for n in ns) + "</ul>"
                       for l, ns in C.VERSUS_NOTES.items()) + "</details>")
    status_pill = {"ships": '<span class="pill ships">Ships</span>', "partial": '<span class="pill gaps">Partly built</span>',
                   "specified": '<span class="pill spec">In the spec</span>'}
    fgroups = "".join(
        f'<div class="fgroup"><h3>{e(g)}</h3><div class="fgrid">' + "".join(
            f'<div class="fcard">{status_pill[st]}<b>{e(n)}</b><p>{md(pt)}</p></div>' for n, pt, st in items)
        + "</div></div>" for g, items in C.FEATURE_GROUPS)
    stats = "".join(f"<li><b>{e(n)}</b><span>{e(t)}</span></li>" for n, t in C.STATS)
    loop = "".join(f"<li><b>{e(t)}</b><span>{e(d)}</span></li>" for t, d in C.LOOP)
    status = "".join(f"<dt>{e(k)}</dt><dd>{md(v)}</dd>" for k, v in C.STATUS)
    uuid = C.LISTMONK_LIST_UUID
    if uuid:
        form = (f'<form class="signup" method="post" action="{e(C.LISTMONK_FORM_URL)}">'
                f'<input type="hidden" name="l" value="{e(uuid)}">'
                f'<label class="vh" for="em">Email for release updates</label>'
                f'<input id="em" type="email" name="email" required placeholder="you@example.com" autocomplete="email">'
                f'<button type="submit">Get updates</button></form>')
    else:
        form = '<p class="note">An update list opens at launch.</p>'
    spec = f'<a class="btn" href="{e(C.SPEC_PDF)}">Read the spec (PDF)</a>' if C.SPEC_PDF else ""
    involved = e(C.INVOLVED).replace(e(C.CONTACT), f'<a href="mailto:{e(C.CONTACT)}">{e(C.CONTACT)}</a>')

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Draconyx</title>
<meta name="description" content="Draconyx is a programming language designed for its AI author: structured diagnostics with edits, writes by definition name, laws checked by default, compile-time authority.">
<meta name="color-scheme" content="light dark">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="alternate" type="text/markdown" href="/index.md" title="This page as Markdown">
<link rel="canonical" href="{SITE}/">
<meta property="og:title" content="Draconyx">
<meta property="og:description" content="{e(C.HERO['headline'])} A programming language designed for its AI author.">
<meta property="og:url" content="{SITE}/">
<meta property="og:type" content="website">
<meta property="og:image" content="{SITE}/assets/logo-1200.webp">
<style>{CSS}</style>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="top"><div class="wrap">
<a class="brand" href="/">{CLAW}<span>Draconyx</span></a>
<nav aria-label="Sections"><a href="#versus">Versus</a><a class="opt" href="#why">Why</a><a class="opt" href="#language">Language</a><a class="opt" href="#name">Name</a><a href="#status">Status</a><a href="/llms.txt">For agents</a></nav>
</div></header>
<main id="main">
<div class="hero"><div class="wrap">
<img class="logo" src="/assets/logo-1200.webp" srcset="/assets/logo-640.webp 640w, /assets/logo-1200.webp 1200w" sizes="(max-width:760px) 100vw, 720px" width="1200" height="800" alt="Draconyx: a dinosaur mascot above the Draconyx wordmark">
<p class="eyebrow">{e(C.HERO['eyebrow'])}</p>
<h1>{e(C.HERO['headline'])}</h1>
<p class="sub">{e(C.HERO['subhead'])}</p>
<div class="btns"><a class="btn primary" href="#versus">See it beat the rest</a>{spec}<a class="btn" href="/llms.txt">For AI agents: llms.txt</a></div>
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
<div class="vwrap" tabindex="0" role="region" aria-label="Comparison table"><table class="versus">
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
<p class="lede">One language from the type system to the cluster: ownership without a garbage collector, capabilities with laws, structured concurrency, remote values, a numerical core. Every card says exactly where it stands.</p>
<div class="fgroups">{fgroups}</div>
</div></section>

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
</div></section>

<section id="involved" class="cta"><div class="wrap prose">
<h2>Get in early</h2>
<p>{involved}</p>
{form}
</div></section>
</main>
<footer><div class="wrap">
<span>{CLAW}Draconyx, a language designed by Filippo Fadda with AI collaborators.</span>
<span><a href="/index.md">This page as Markdown</a> &middot; <a href="/llms.txt">llms.txt</a></span>
</div></footer>
</body>
</html>
"""


def build_md():
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
            lang = {"draconyx": "", "json": "json", "shell": "sh"}[kind]
            lines += [f"```{lang}", code, "```", f"_{cap}_", ""]
        lines += [f"Spec references: {', '.join(r['cites'])}", ""]
    lines += ["## The whole language", ""]
    names = {"ships": "Ships", "partial": "Partly built", "specified": "In the spec"}
    for g, items in C.FEATURE_GROUPS:
        lines += [f"### {g}", ""] + [f"- **{n}** ({names[st]}): {pt}" for n, pt, st in items] + [""]
    lines += ["## Dragon claw, written law", ""] + [p + "\n" for p in C.NAME]
    lines += [f"Source: [{C.NAME_SOURCE[0]}]({C.NAME_SOURCE[1]})", "", f"## Where it stands (as of {C.AS_OF})", ""]
    lines += [f"- **{k}:** {v}" for k, v in C.STATUS]
    lines += ["", "## Get in early", "", C.INVOLVED, ""]
    return "\n".join(lines)


def build_llms():
    out = ["# Draconyx", "",
           "> A programming language designed for code written by AI models and used by AI agents. "
           "Pre-release research project: a 522-page specification and a working compiler, "
           "public at the first release. Each mechanism below states what ships today and what is only specified.", "",
           f"Status as of {C.AS_OF}: " + " ".join(f"{k}: {v}" for k, v in C.STATUS), "",
           "## Mechanisms", ""]
    for r in C.REASONS:
        out.append(f"- [{r['title']}]({SITE}/#{r['id']}): {r['body'][0]} Status: {r['ships']} "
                   f"Spec references: {', '.join(r['cites'])}")
    names = {"ships": "ships", "partial": "partly built", "specified": "in the spec"}
    out += ["", "## Language", ""]
    for g, items in C.FEATURE_GROUPS:
        out += [f"- [{n}]({SITE}/#language): {pt} ({g}; {names[st]})" for n, pt, st in items]
    out += ["", "## Docs", "", f"- [Full page as Markdown]({SITE}/index.md): every mechanism with samples and status",
            f"- [Why the name]({SITE}/#name): Draconyx, Draco's written laws and the axones",
            f"- [Contact](mailto:{C.CONTACT}): design discussion, collaboration, model training or evaluation", ""]
    return "\n".join(out)


def main():
    os.makedirs(os.path.join(OUT, "assets"), exist_ok=True)
    for name in ("logo-1200.webp", "logo-640.webp"):
        shutil.copyfile(os.path.join(HERE, "assets", name), os.path.join(OUT, "assets", name))
    files = {
        "index.html": build_html(), "index.md": build_md(), "llms.txt": build_llms(), "favicon.svg": FAVICON,
        "robots.txt": f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n",
        "sitemap.xml": ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                        f"<url><loc>{SITE}/</loc></url><url><loc>{SITE}/index.md</loc></url><url><loc>{SITE}/llms.txt</loc></url></urlset>\n"),
    }
    for name, text in files.items():
        with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
            f.write(text)
    print("built", ", ".join(f"{n} ({len(t.encode())} B)" for n, t in files.items()))


if __name__ == "__main__":
    main()
