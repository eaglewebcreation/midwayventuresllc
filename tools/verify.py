#!/usr/bin/env python3
"""Checks the built site: town-page overlap (<25%), title/description lengths, internal links, placeholders.

    python3 tools/verify.py
"""
import html
import itertools
import re
import sys
from pathlib import Path

PUB = Path(__file__).resolve().parent.parent / "public"
TOWNS = sorted(p.parent.name for p in PUB.glob("heated-shop-*-wy/index.html"))
N = 5  # words per shingle


def main_text(path):
    s = (PUB / path).read_text()
    m = re.search(r"<main[^>]*>(.*)</main>", s, re.S)
    t = re.sub(r"<!--.*?-->", " ", m.group(1), flags=re.S)
    t = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", t, flags=re.S)
    t = html.unescape(re.sub(r"<[^>]+>", " ", t)).lower()
    return re.findall(r"[a-z0-9$.,']+", t)


def shingles(words):
    return {" ".join(words[i:i + N]) for i in range(len(words) - N + 1)}


ok = True
sh = {t: shingles(main_text(f"{t}/index.html")) for t in TOWNS}
worst = 0
print("Town page overlap (share of page A's 5-word phrases that also appear on page B):")
for a, b in itertools.permutations(TOWNS, 2):
    r = len(sh[a] & sh[b]) / len(sh[a])
    worst = max(worst, r)
    if r >= 0.25:
        ok = False
        print(f"  FAIL {a} vs {b}: {r:.0%}")
for t in TOWNS:
    m = max(len(sh[t] & sh[o]) / len(sh[t]) for o in TOWNS if o != t)
    print(f"  {t:22s} {len(main_text(t + '/index.html')):4d} words, max overlap {m:.0%}")
print(f"  worst pair: {worst:.0%} (limit 25%)")

files = sorted(PUB.rglob("*.html"))
for f in files:
    s = f.read_text()
    title = html.unescape(re.search(r"<title>(.*?)</title>", s).group(1))
    desc = html.unescape(re.search(r'<meta name="description" content="(.*?)"', s).group(1))
    if len(title) > 60 or len(desc) > 155:
        ok = False
        print("  LENGTH", f.relative_to(PUB), len(title), len(desc))
    if s.count("<h1") != 1:
        ok = False
        print("  H1 count", f.relative_to(PUB), s.count("<h1"))
    for href in re.findall(r'href="(/[^"#?]*)', s):
        target = PUB / href.lstrip("/")
        if not (target.is_file() or (target / "index.html").is_file()):
            ok = False
            print("  BROKEN", f.relative_to(PUB), href)
    for src in re.findall(r'(?:src|srcset)="(/[^" ?]+)', s):
        if not (PUB / src.lstrip("/")).is_file():
            ok = False
            print("  MISSING", f.relative_to(PUB), src)
    for bad in ("climate-controlled", "climate controlled", "gated", "camera", "surveillance"):
        for m in re.finditer(bad, s, re.I):
            ctx = s[max(0, m.start() - 60):m.end() + 40]
            print("  WORD", bad, f.relative_to(PUB), "...", re.sub(r"\s+", " ", ctx))
ph = sum(f.read_text().count('class="tbd"') for f in files)
print(f"{len(files)} pages checked, {ph} visible placeholders")
sys.exit(0 if ok else 1)
