#!/usr/bin/env python3
"""Tell the IndexNow search engines (Bing, Yandex, Seznam, Naver, Yep and the others) that the sitemap's
URLs changed. Run it after a deploy:

    python3 indexnow.py             # checks the live key file, then submits every sitemap URL
    python3 indexnow.py --dry-run   # prints what it would submit

The URLs come from the live https://draconyx.ai/sitemap.xml, so what is submitted is what is deployed.
api.indexnow.org shares each submission with every participating engine. 200 and 202 mean accepted
(202: key validation pending); 403 means the key file is not live or does not match; 422 means a URL
is not on this host; 429 means too many requests. Only submit after a real change.
"""
import json
import os
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(__file__))
from build import INDEXNOW_KEY, SITE  # noqa: E402

ENDPOINT = "https://api.indexnow.org/indexnow"
UA = "draconyx-indexnow/1 (+https://draconyx.ai)"


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8")


def main():
    dry = "--dry-run" in sys.argv[1:]
    key_url = f"{SITE}/{INDEXNOW_KEY}.txt"
    try:
        live_key = get(key_url).strip()
    except urllib.error.HTTPError as err:
        live_key = f"HTTP {err.code}"
    if live_key != INDEXNOW_KEY:
        sys.exit(f"{key_url} does not hold the key ({live_key[:40]}): deploy first")
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls = [loc.text.strip() for loc in ET.fromstring(get(f"{SITE}/sitemap.xml")).findall("s:url/s:loc", ns)]
    if not urls:
        sys.exit("the live sitemap lists no URLs")
    host = SITE.split("://", 1)[1]
    body = {"host": host, "key": INDEXNOW_KEY, "keyLocation": key_url, "urlList": urls}
    print("submitting", len(urls), "URL(s):", ", ".join(urls))
    if dry:
        print(json.dumps(body, indent=2))
        return
    req = urllib.request.Request(ENDPOINT, data=json.dumps(body).encode(), method="POST",
                                 headers={"Content-Type": "application/json; charset=utf-8", "User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            code, text = r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as err:
        code, text = err.code, err.read().decode("utf-8", "replace")
    print("IndexNow response:", code, text.strip())
    sys.exit(0 if code in (200, 202) else 1)


if __name__ == "__main__":
    main()
