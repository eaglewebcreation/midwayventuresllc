#!/usr/bin/env python3
"""Make the web logo files, favicons and the link-preview image from /assets/source.

The logo is Eagle Web Creation's vector rebuild of the Midway Ventures LLC logo
(three green bands + M, wordmark outlined). Source files are never modified.

    python3 tools/build_images.py      (needs Pillow and cairosvg)
"""
import io
import re
from pathlib import Path

import cairosvg
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "source"
OUT = ROOT / "public" / "assets" / "img"
PUB = ROOT / "public"
OUT.mkdir(parents=True, exist_ok=True)

DEEP = (13, 33, 15)


def clean(svg):
    """Drop the embedded metadata block so the files stay small."""
    svg = re.sub(r"<metadata>.*?</metadata>", "", svg, flags=re.S)
    svg = svg.replace(' xmlns:c2pa="http://c2pa.org/manifest"', "")
    return svg.strip() + "\n"


def logos():
    logo = clean((SRC / "midway-ventures-logo.svg").read_text())
    icon = clean((SRC / "midway-ventures-icon.svg").read_text())
    (OUT / "logo.svg").write_text(logo)
    (OUT / "logo-mark.svg").write_text(icon)
    # On dark backgrounds the charcoal M and wordmark turn white; the bands keep their greens.
    (OUT / "logo-white.svg").write_text(logo.replace('fill="#202020"', 'fill="#ffffff"'))
    (OUT / "logo-mark-white.svg").write_text(icon.replace('fill="#202020"', 'fill="#ffffff"'))
    return logo, icon


def svg_png(svg_text, w):
    data = cairosvg.svg2png(bytestring=svg_text.encode(), output_width=w)
    return Image.open(io.BytesIO(data)).convert("RGBA")


def square(icon, size, pad=0.1, bg=(255, 255, 255, 255)):
    inner = round(size * (1 - 2 * pad))
    mark = svg_png(icon, inner * 2)
    mark.thumbnail((inner, inner), Image.LANCZOS)
    canvas = Image.new("RGBA", (size, size), bg)
    canvas.alpha_composite(mark, ((size - mark.width) // 2, (size - mark.height) // 2))
    return canvas


def icons(icon):
    for size, name in [(16, "favicon-16x16.png"), (32, "favicon-32x32.png"), (180, "apple-touch-icon.png"),
                       (192, "android-chrome-192x192.png"), (512, "android-chrome-512x512.png")]:
        pad = 0.04 if size <= 32 else 0.12
        square(icon, size, pad).convert("RGB").save(PUB / name, optimize=True)
    square(icon, 48, 0.04).save(PUB / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])
    lg = svg_png((OUT / "logo.svg").read_text(), 1280)
    flat = Image.new("RGB", lg.size, (255, 255, 255))
    flat.paste(lg, mask=lg.split()[3])
    flat.thumbnail((640, 640))
    flat.save(OUT / "logo-640.png", optimize=True)


def share_image():
    """1200x630 link preview: the logo on white over a deep-green band with the shop's size."""
    W, H = 1200, 630
    im = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(im)
    # three slanted bands down the left edge, echoing the logo
    greens = [(15, 60, 15), (24, 97, 24), (34, 139, 34)]
    for i, g in enumerate(greens):
        x = i * 46
        d.polygon([(x + 60, 0), (x + 106, 0), (x + 46, 410), (x, 410)], fill=g)
    lg = svg_png((OUT / "logo.svg").read_text(), 1900)
    lg.thumbnail((940, 400), Image.LANCZOS)
    im.paste(lg, (190, 150), lg)
    d.rectangle([0, 410, W, H], fill=DEEP)
    for i, g in enumerate(greens):
        d.rectangle([0, 410 + i * 4, W, 410 + i * 4 + 4], fill=g)
    big = ImageFont.truetype("/usr/share/fonts/opentype/inter/InterDisplay-Black.otf", 62)
    small = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-SemiBold.otf", 32)
    d.text((70, 458), "Heated shop for rent", font=big, fill=(255, 255, 255))
    d.text((72, 545), "36 x 45 ft  ·  16 ft ceiling  ·  bathroom + office", font=small, fill=(196, 226, 190))
    im.save(OUT / "share-1200x630.jpg", "JPEG", quality=86, optimize=True, progressive=True)


if __name__ == "__main__":
    logo, icon = logos()
    icons(icon)
    share_image()
    print("images built")
