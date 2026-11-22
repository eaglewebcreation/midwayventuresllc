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


PHOTO_WIDTHS = (480, 768, 1152)


def shop_photo():
    """Owner's photo of the shop front (door open). 3:4, never cropped; WebP plus JPG fallback per width."""
    src = Image.open(SRC / "shop-front.jpg").convert("RGB")
    for w in PHOTO_WIDTHS:
        h = round(w * src.height / src.width)
        r = src.resize((w, h), Image.LANCZOS)
        r.save(OUT / f"shop-front-{w}.webp", "WEBP", quality=78, method=6)
        r.save(OUT / f"shop-front-{w}.jpg", "JPEG", quality=80, optimize=True, progressive=True)
    return src


def share_image(photo):
    """1200x630 link preview: logo and the shop's size on the left, the whole shop photo on the right."""
    W, H = 1200, 630
    im = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(im)
    pw = round(H * photo.width / photo.height)  # full photo, no crop
    left = W - pw
    # three slanted bands down the left edge, echoing the logo
    greens = [(15, 60, 15), (24, 97, 24), (34, 139, 34)]
    for i, g in enumerate(greens):
        x = i * 40
        d.polygon([(x + 52, 0), (x + 92, 0), (x + 40, 410), (x, 410)], fill=g)
    lg = svg_png((OUT / "logo.svg").read_text(), 1600)
    lg.thumbnail((left - 200, 300), Image.LANCZOS)
    im.paste(lg, (165, 205 - lg.height // 2), lg)
    d.rectangle([0, 410, left, H], fill=DEEP)
    for i, g in enumerate(greens):
        d.rectangle([0, 410 + i * 4, left, 410 + i * 4 + 4], fill=g)
    big = ImageFont.truetype("/usr/share/fonts/opentype/inter/InterDisplay-Black.otf", 56)
    small = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-SemiBold.otf", 25)
    d.text((56, 456), "Heated shop for rent", font=big, fill=(255, 255, 255))
    d.text((58, 540), "36 x 45 ft  ·  16 ft ceiling  ·  bathroom + office", font=small, fill=(196, 226, 190))
    im.paste(photo.resize((pw, H), Image.LANCZOS), (left, 0))
    d.rectangle([left - 4, 0, left - 1, H], fill=greens[2])
    im.save(OUT / "share-1200x630.jpg", "JPEG", quality=86, optimize=True, progressive=True)

if __name__ == "__main__":
    logo, icon = logos()
    icons(icon)
    share_image(shop_photo())
    print("images built")
