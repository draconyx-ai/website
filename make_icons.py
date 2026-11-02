#!/usr/bin/env python3
"""Regenerate the raster icons in assets/ from the favicon design in build.py (CLAW_PATHS and the FAVICON_* colours).

    python3 make_icons.py

Writes assets/favicon.ico (16, 32 and 48 px, PNG-compressed entries) and assets/apple-touch-icon.png (180x180,
opaque: iOS fills transparency with black and rounds the corners itself). Rendering uses headless Google Chrome
(the vector is rasterised at each size, not scaled down); the ICO container is written with the standard library.
Run it only when the design changes: the outputs are committed and build.py copies them into dist/.
"""
import os
import struct
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build  # noqa: E402

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
ASSETS = os.path.join(build.HERE, "assets")
ICO_SIZES = (16, 32, 48)
APPLE_SIZE = 180


def svg(size, square=False):
    """The favicon at `size` px. `square` is the full-bleed variant for the Apple touch icon."""
    rx = 0 if square else 14
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 64 64">'
            f'<rect width="64" height="64" rx="{rx}" fill="{build.FAVICON_CREAM}"/>'
            f'<g fill="{build.FAVICON_OLIVE}">{build.CLAW_PATHS}</g></svg>')


def render(markup, size, out):
    """Screenshot `markup` (an <svg>) at exactly size x size px with a transparent page background."""
    with tempfile.TemporaryDirectory() as tmp:
        page = os.path.join(tmp, "icon.html")
        with open(page, "w", encoding="utf-8") as f:
            f.write(f'<!doctype html><body style="margin:0;background:transparent">{markup}')
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                        "--force-device-scale-factor=1", "--default-background-color=00000000",
                        f"--window-size={size},{size}", f"--screenshot={out}", f"file://{page}"],
                       check=True, capture_output=True)
    with open(out, "rb") as f:
        data = f.read()
    w, h = struct.unpack(">II", data[16:24])
    assert (w, h) == (size, size), f"{out} is {w}x{h}, expected {size}x{size}"
    return data


def write_ico(path, pngs):
    """ICO container holding PNG images (supported since Windows Vista and by every browser)."""
    header = struct.pack("<HHH", 0, 1, len(pngs))
    offset = 6 + 16 * len(pngs)
    entries, blobs = b"", b""
    for size, data in pngs:
        entries += struct.pack("<BBBBHHII", size, size, 0, 0, 1, 32, len(data), offset + len(blobs))
        blobs += data
    with open(path, "wb") as f:
        f.write(header + entries + blobs)


def main():
    with tempfile.TemporaryDirectory() as tmp:
        pngs = [(s, render(svg(s), s, os.path.join(tmp, f"{s}.png"))) for s in ICO_SIZES]
        apple = render(svg(APPLE_SIZE, square=True), APPLE_SIZE, os.path.join(tmp, "apple.png"))
    write_ico(os.path.join(ASSETS, "favicon.ico"), pngs)
    with open(os.path.join(ASSETS, "apple-touch-icon.png"), "wb") as f:
        f.write(apple)
    print("wrote assets/favicon.ico and assets/apple-touch-icon.png")


if __name__ == "__main__":
    main()
