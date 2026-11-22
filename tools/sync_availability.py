#!/usr/bin/env python3
"""Sync the shop's "Available now" / "Rented" label from the public CCStorage rental page.

Finds the shop by its CCStorage unit-type id and reads whether its button says "Rent Now"
or "Join Waiting List". Updates shop.status in site-config.json only when it was read.

Exit codes:
  0  read the shop (prints changed=true/false to $GITHUB_OUTPUT when set)
  2  could not read it: nothing is changed, the site keeps its last label

Runs plain HTTP first, then a headless browser (playwright) when that is installed.
"""
import html
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "site-config.json"
UA = "Mozilla/5.0 (compatible; MidwayVenturesSiteSync/1.0)"


def fetch_plain(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def fetch_rendered(url):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return None
    with sync_playwright() as p:
        b = p.chromium.launch()
        page = b.new_page(user_agent=UA)
        page.goto(url, wait_until="networkidle", timeout=60000)
        out = page.content()
        b.close()
        return out


def status_for(page_html, type_id):
    for m in re.finditer(r"<a\b[^>]*storage_unit_type_id=" + re.escape(type_id) + r"[^>]*>(.*?)</a>",
                         page_html, re.S | re.I):
        text = " ".join(html.unescape(re.sub(r"<[^>]+>", " ", m.group(1))).split()).lower()
        if "waiting list" in text or "waitlist" in text:
            return "waitlist"
        if "rent now" in text or text == "rent":
            return "rent"
    return None


def main():
    cfg = json.loads(CONFIG.read_text())
    url, tid = cfg["rentUrl"], cfg["shop"]["ccstorageTypeId"]
    new, how = None, "plain"
    try:
        new = status_for(fetch_plain(url), tid)
    except Exception as e:
        print(f"plain fetch failed: {e}", file=sys.stderr)
    if new is None:
        page = fetch_rendered(url)
        if page:
            how, new = "browser", status_for(page, tid)
    if new is None:
        print("COULD NOT READ the shop's status. Keeping the last label; nothing changed.")
        return 2
    old = cfg["shop"]["status"]
    changed = old != new
    print(f"read via {how}: {new}" + (f" (was {old})" if changed else " (no change)"))
    if changed:
        text = CONFIG.read_text()
        text, n = re.subn(r'"status": "(rent|waitlist)"', f'"status": "{new}"', text, count=1)
        if n != 1:
            print("status field not found in site-config.json; not writing.")
            return 2
        CONFIG.write_text(text)
    gh_out = os.environ.get("GITHUB_OUTPUT")
    if gh_out:
        with open(gh_out, "a") as f:
            f.write(f"changed={'true' if changed else 'false'}\n")
            f.write(f"summary=shop {old} -> {new}\n" if changed else "summary=none\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
