#!/usr/bin/env python3
"""Regenerate assets/share-1200x630.png, the image link previews show (og:image and twitter:image in build.py).

    python3 make_share.py

The card is the home page's hero in miniature: the logo on the page's cream, the headline from content.py and the
address. It is 1200x630 and opaque (some apps show transparency as black). Rendering uses headless Google Chrome on
macOS, as make_icons.py does; the rest is standard library. Run it when the logo, the headline or the colours change:
the output is committed and build.py copies it into dist/assets/.
"""
import html
import os
import pathlib
import shutil
import struct
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build  # noqa: E402
import content as C  # noqa: E402

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
ASSETS = os.path.join(build.HERE, "assets")
OUT = os.path.join(ASSETS, "share-1200x630.png")
WIDTH, HEIGHT = 1200, 630
# The page's colours, as in build.CSS: --bg, --fg, --olive, --ember2.
BG, FG, OLIVE, EMBER = "#f6efdf", "#1c1a14", "#5b6b25", "#e8501f"


def page():
    logo = pathlib.Path(ASSETS, "logo-1200.webp").as_uri()
    headline = html.escape(C.HERO["headline"])
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
html,body{{margin:0;width:{WIDTH}px;height:{HEIGHT}px;overflow:hidden;background:{BG}}}
body{{position:relative;display:flex;align-items:center;gap:28px;padding:0 64px 0 36px;box-sizing:border-box;
 background:radial-gradient(1100px 520px at 30% 112%,color-mix(in srgb,{OLIVE} 30%,transparent),transparent 70%),
 radial-gradient(700px 360px at 92% 0%,color-mix(in srgb,{EMBER} 16%,transparent),transparent 70%),{BG}}}
body::after{{content:"";position:absolute;inset:auto 0 0 0;height:70px;
 background:repeating-linear-gradient(0deg,transparent 0 13px,color-mix(in srgb,{OLIVE} 14%,transparent) 13px 15px);
 -webkit-mask:linear-gradient(transparent,#000);mask:linear-gradient(transparent,#000)}}
img{{flex:none;width:600px;height:400px;filter:drop-shadow(0 14px 22px rgba(40,30,10,.18))}}
.t{{position:relative;z-index:1}}
h1{{margin:0 0 30px;color:{FG};font:650 66px/1.08 ui-serif,"New York","Iowan Old Style",Georgia,serif;letter-spacing:-.012em}}
p{{margin:0;color:{OLIVE};font:800 40px/1 -apple-system,BlinkMacSystemFont,"Helvetica Neue",Arial,sans-serif;letter-spacing:.01em}}
</style></head><body><img src="{logo}" alt=""><div class="t"><h1>{headline}</h1><p>draconyx.ai</p></div></body></html>"""


def main():
    assert os.path.isfile(os.path.join(ASSETS, "logo-1200.webp")), "assets/logo-1200.webp is missing"
    with tempfile.TemporaryDirectory() as tmp:
        src, png = os.path.join(tmp, "share.html"), os.path.join(tmp, "share.png")
        with open(src, "w", encoding="utf-8") as f:
            f.write(page())
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                        "--force-device-scale-factor=1", f"--window-size={WIDTH},{HEIGHT}",
                        f"--screenshot={png}", pathlib.Path(src).as_uri()], check=True, capture_output=True)
        with open(png, "rb") as f:
            w, h = struct.unpack(">II", f.read(24)[16:24])
        assert (w, h) == (WIDTH, HEIGHT), f"the render is {w}x{h}, expected {WIDTH}x{HEIGHT}"
        shutil.copyfile(png, OUT)
    print(f"wrote assets/share-1200x630.png ({w}x{h})")


if __name__ == "__main__":
    main()
