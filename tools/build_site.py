#!/usr/bin/env python3
"""Build the static Midway Ventures LLC site into /public.

Plain HTML/CSS/JS, nothing runs on the server. Shared pieces (header with the animated
logo, footer, drawing, schema) and the owner facts in /site-config.json stay consistent
across every page.

    python3 tools/build_site.py
    SITE_URL=https://example.com python3 tools/build_site.py   # build for another host
"""
import datetime
import hashlib
import html
import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PUB = ROOT / "public"
C = json.loads((ROOT / "site-config.json").read_text())
K = C["CONFIRM"]
S = C["shop"]
SITE = (os.environ.get("SITE_URL") or C["siteUrl"]).rstrip("/")
PROD = bool(C.get("prodHost")) and SITE == "https://" + C["prodHost"]
TODAY = datetime.date.today().isoformat()
YEAR = datetime.date.today().year
BIZ_ID = SITE + "/#business"
NAME = C["name"]
PHONE = C["phoneDisplay"]
TEL = "tel:" + C["phoneTel"]
RENT = html.escape(C["rentUrl"], quote=True)
ADDR_LINE = f'{C["street"]}, {C["city"]}, {C["region"]} {C["zip"]}'
DIRECTIONS = ("https://www.google.com/maps/dir/?api=1&amp;destination="
              "1781+US+Highway+310,+Lovell,+WY+82431")
AS_OF = C["pricesAsOf"]
OPEN = S["status"] == "rent"
SQFT = S["w"] * S["d"]
PER_SQFT = round(float(S["rent"].replace(",", "")) / SQFT * 100)  # cents per sq ft per month

PH_TEXT = "[waiting on owner confirmation]"


def ph(todo):
    """Visible placeholder plus an HTML TODO comment that says what is missing."""
    return f'<!-- TODO: confirm with owner: {todo} --><span class="tbd">{PH_TEXT}</span>'


def fact(key, todo):
    v = K.get(key)
    return html.escape(str(v)) if v else ph(todo)


def minify_css(s):
    s = re.sub(r"/\*.*?\*/", "", s, flags=re.S)
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"\s*([{};:,>])\s*", r"\1", s)
    return s.replace(";}", "}").strip()


JS_V = hashlib.sha1((PUB / "assets" / "js" / "site.js").read_bytes()).hexdigest()[:8]
CSS_MIN = minify_css((ROOT / "src" / "site.css").read_text())

ICON = {
    "phone": '<svg aria-hidden="true" viewBox="0 0 24 24" fill="currentColor"><path d="M6.6 10.8a15.1 15.1 0 0 0 6.6 6.6l2.2-2.2a1 1 0 0 1 1-.25 11.4 11.4 0 0 0 3.6.57 1 1 0 0 1 1 1V20a1 1 0 0 1-1 1A17 17 0 0 1 3 4a1 1 0 0 1 1-1h3.5a1 1 0 0 1 1 1c0 1.25.2 2.45.57 3.57a1 1 0 0 1-.25 1z"/></svg>',
    "key": '<svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><circle cx="8" cy="15" r="4"/><path d="M11 12l9-9M16 7l3 3"/></svg>',
    "heat": '<svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M7 20c-1.5-2 1.5-4 0-6s1.5-4 0-6M12 20c-1.5-2 1.5-4 0-6s1.5-4 0-6M17 20c-1.5-2 1.5-4 0-6s1.5-4 0-6"/></svg>',
    "height": '<svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v18M8 7l4-4 4 4M8 17l4 4 4-4M3 3h4M3 21h4"/></svg>',
    "floor": '<svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M2 8l10-5 10 5-10 5z"/><path d="M2 8v8l10 5 10-5V8M12 13v8"/></svg>',
    "bath": '<svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3c3 4 6 7 6 11a6 6 0 0 1-12 0c0-4 3-7 6-11z"/></svg>',
    "office": '<svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><rect x="3" y="4" width="18" height="12" rx="1"/><path d="M8 20h8M12 16v4"/></svg>',
    "camera": '<svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"><path d="M3 8h4l2-3h6l2 3h4v11H3z"/><circle cx="12" cy="13" r="4"/></svg>',
}

# ---------------------------------------------------------------- towns
# drive = fastest Google Maps route from 1781 US Highway 310, read 2026-11-21
# (Powell, Cody, Greybull and Basin were read from the Midway Storage pin next door, 1780 US-310)
TOWNS = [
    {"slug": "lovell", "name": "Lovell", "drive": "4 minutes", "mi": "2.7 miles", "short": "4 min", "road": "US-310"},
    {"slug": "cowley", "name": "Cowley", "drive": "4 minutes", "mi": "3.5 miles", "short": "4 min", "road": "US-310"},
    {"slug": "byron", "name": "Byron", "drive": "5 minutes", "mi": "4.7 miles", "short": "5 min", "road": "US-14A"},
    {"slug": "powell", "name": "Powell", "drive": "22 minutes", "mi": "19.6 miles", "short": "22 min", "road": "US-14A"},
    {"slug": "greybull", "name": "Greybull", "drive": "36 minutes", "mi": "35.2 miles", "short": "36 min", "road": "US-310"},
    {"slug": "basin", "name": "Basin", "drive": "44 minutes", "mi": "42.8 miles", "short": "44 min", "road": "US-16/20 and US-310"},
    {"slug": "cody", "name": "Cody", "drive": "47 minutes", "mi": "43.4 miles", "short": "47 min", "road": "US-14A"},
]
for _t in TOWNS:
    _t["url"] = f'/heated-shop-{_t["slug"]}-wy/'
TOWN = {t["slug"]: t for t in TOWNS}
COUNTY = {"lovell": "Big Horn", "cowley": "Big Horn", "byron": "Big Horn", "greybull": "Big Horn",
          "basin": "Big Horn", "powell": "Park", "cody": "Park"}


def city(t):
    return {"@type": "City", "name": f'{t["name"]}, WY',
            "containedInPlace": {"@type": "AdministrativeArea", "name": f'{COUNTY[t["slug"]]} County, Wyoming'}}


# ---------------------------------------------------------------- the logo (inline so it can animate)
def _logo_paths():
    svg = (PUB / "assets" / "img" / "logo.svg").read_text()
    return re.findall(r'<path fill="([^"]+)" d="([^"]+)"/>', svg)


LOGO = _logo_paths()  # 3 bands, the M, the wordmark


def logo_svg():
    bands = "".join(f'<path fill="{f}" d="{d}"/>' for f, d in LOGO[:3])
    m_fill, m_d = LOGO[3]
    w_fill, w_d = LOGO[4]
    # Order matters: bands, a white cover that slides with the M (so the bands appear behind it
    # like a trail), the name clipped to the right of the M, then the M on top.
    return (f'<svg viewBox="322 -32 2974 428" width="290" height="42" role="img" aria-labelledby="logo-t">'
            f'<title id="logo-t">{NAME}</title>'
            f'<defs><clipPath id="lg-clip"><rect x="1190" y="-40" width="2200" height="480"/></clipPath></defs>'
            f'{bands}<polygon class="lg-cover" points="902,-40 3400,-40 3400,420 748,420"/>'
            f'<g clip-path="url(#lg-clip)"><path class="lg-word" fill="{w_fill}" d="{w_d}"/></g>'
            f'<path class="lg-m" fill="{m_fill}" d="{m_d}"/></svg>')


# ---------------------------------------------------------------- the to-scale drawing
def iso_svg():
    """Isometric line drawing of the 36 x 45 x 16 ft shop, to scale, with a 5 ft 10 in person and
    a full-size pickup for scale. Bathroom and office are not drawn: their layout isn't known."""
    s, c = 7.0, 0.8660254
    ox, oy = 292.0, 142.0
    W, D, H = S["w"], S["d"], S["h"]

    def P(x, y, z=0):
        return (ox + (x - y) * c * s, oy + (x + y) * 0.5 * s - z * s)

    def pts(*ps):
        return " ".join(f"{a:.1f},{b:.1f}" for a, b in (P(*p) for p in ps))

    def path(*ps, close=True):
        xy = [P(*p) for p in ps]
        d = "M" + " L".join(f"{a:.1f} {b:.1f}" for a, b in xy)
        return d + (" Z" if close else "")

    def box(x0, x1, y0, y1, z0, z1):
        top = f'<polygon class="truck-top" points="{pts((x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1))}"/>'
        side = f'<polygon class="truck-side" points="{pts((x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1))}"/>'
        front = f'<polygon class="truck-front" points="{pts((x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1))}"/>'
        return side + front + top

    walls = (f'<polygon class="wall" points="{pts((0, 0, 0), (W, 0, 0), (W, 0, H), (0, 0, H))}"/>'
             f'<polygon class="wall" points="{pts((0, 0, 0), (0, D, 0), (0, D, H), (0, 0, H))}"/>')
    floor = f'<polygon class="floor" points="{pts((0, 0, 0), (W, 0, 0), (W, D, 0), (0, D, 0))}"/>'
    # pickup: about 6.7 ft wide, 19.5 ft long, cab 6.3 ft tall
    tx0, tx1, ty0, ty1 = 7.0, 13.7, 15.0, 34.5
    truck = (f'<g class="truck">{box(tx0, tx1, ty0, ty1, 0.9, 3.9)}{box(tx0 + .2, tx1 - .2, 21.0, 27.5, 3.9, 6.3)}'
             + "".join(f'<ellipse cx="{P(tx1, wy, 1.1)[0]:.1f}" cy="{P(tx1, wy, 1.1)[1]:.1f}" rx="7" ry="9" fill="#2a2e2a" transform="rotate(-30 {P(tx1, wy, 1.1)[0]:.1f} {P(tx1, wy, 1.1)[1]:.1f})"/>'
                       for wy in (18.5, 30.5)) + "</g>")
    px, py = P(27, 40)
    ph_ = 5.83 * s
    person = (f'<g class="person"><rect x="{px - 3.6:.1f}" y="{py - ph_ + 7.5:.1f}" width="7.2" height="{ph_ - 7.5:.1f}" rx="3.2"/>'
              f'<circle cx="{px:.1f}" cy="{py - ph_ + 3.4:.1f}" r="3.6"/></g>')
    hx, hy = P(22, 26)
    heat = '<g class="heat">' + "".join(
        f'<path d="M{hx + dx:.1f} {hy - 6:.1f} c-6 -8 6 -14 0 -22 s6 -14 0 -22"/>' for dx in (-14, 0, 14)) + "</g>"
    edges = (f'<path class="edge draw" pathLength="1" d="{path((0, 0, 0), (W, 0, 0), (W, D, 0), (0, D, 0))}"/>'
             f'<path class="edge draw d2" pathLength="1" d="M{P(0, 0, 0)[0]:.1f} {P(0, 0, 0)[1]:.1f} V{P(0, 0, H)[1]:.1f} M{P(W, 0, 0)[0]:.1f} {P(W, 0, 0)[1]:.1f} V{P(W, 0, H)[1]:.1f} M{P(W, D, 0)[0]:.1f} {P(W, D, 0)[1]:.1f} V{P(W, D, H)[1]:.1f} M{P(0, D, 0)[0]:.1f} {P(0, D, 0)[1]:.1f} V{P(0, D, H)[1]:.1f}"/>'
             f'<path class="edge draw d3" pathLength="1" d="{path((0, 0, H), (W, 0, H), (W, D, H), (0, D, H))}"/>')

    def dim(a, b, label, off, ang):
        (x1, y1), (x2, y2) = P(*a), P(*b)
        mx, my = (x1 + x2) / 2 + off[0], (y1 + y2) / 2 + off[1]
        return (f'<line x1="{x1 + off[0] * .45:.1f}" y1="{y1 + off[1] * .45:.1f}" x2="{x2 + off[0] * .45:.1f}" y2="{y2 + off[1] * .45:.1f}"/>'
                f'<text x="{mx:.1f}" y="{my:.1f}" text-anchor="middle" transform="rotate({ang} {mx:.1f} {my:.1f})">{label}</text>')

    dims = ('<g class="dim">'
            + dim((0, D, 0), (W, D, 0), f"{W} FT WIDE", (-16, 26), 30)
            + dim((W, 0, 0), (W, D, 0), f"{D} FT DEEP", (18, 26), -30)
            + f'<line x1="{P(W, 0, 0)[0] + 12:.1f}" y1="{P(W, 0, 0)[1]:.1f}" x2="{P(W, 0, H)[0] + 12:.1f}" y2="{P(W, 0, H)[1]:.1f}"/>'
            + f'<text x="{P(W, 0, H / 2)[0] + 18:.1f}" y="{P(W, 0, H / 2)[1] + 5:.1f}">{H} FT</text>'
            + "</g>")
    label = (f"Drawing to scale of the Midway Ventures shop: {W} feet wide, {D} feet deep and {H} feet tall inside, "
             "shown next to a full-size pickup and a person about 5 feet 10 inches tall")
    return (f'<svg class="iso" viewBox="0 0 580 470" role="img" aria-label="{label}">'
            f'{walls}{floor}{heat}{truck}{person}{edges}{dims}</svg>')


def status_html(cls=""):
    if OPEN:
        return f'<span class="status status-rent {cls}" data-status>Available now</span>'
    return f'<span class="status status-wait {cls}" data-status>Rented right now</span>'


RENT_LABEL = "Rent the shop" if OPEN else "Join the waitlist"


def sheet():
    return f'''<figure class="sheet">
  <div class="sheet-top"><span class="sheet-title">Shop &middot; {S["w"]} &times; {S["d"]} &times; {S["h"]} ft &middot; heated</span>{status_html()}</div>
  {iso_svg()}
  <figcaption class="sheet-foot">
    <p class="sheet-price"><strong>${S["rent"]}</strong> a month, before card or ACH payment fees</p>
    <p class="sheet-key">Drawn to scale with a full-size pickup<br>and a 5&prime;10&Prime; person</p>
  </figcaption>
</figure>'''


# ---------------------------------------------------------------- shell pieces
NAV = [
    ("/the-shop/", "The Shop"),
    ("/the-shop/#price", "Price"),
    ("/faq/", "FAQ"),
    ("/contact/", "Contact"),
]


def header(current):
    items = []
    for href, label in NAV:
        cur = ' aria-current="page"' if href == current else ""
        items.append(f'<li><a href="{href}"{cur}>{label}</a></li>')
    return f'''<a class="skip-link" href="#main">Skip to content</a>
<header class="site-header">
  <div class="wrap header-inner">
    <a class="brand" href="/" aria-label="{NAME} home">{logo_svg()}</a>
    <nav class="main-nav" id="main-nav" aria-label="Main"><ul>{"".join(items)}</ul></nav>
    <div class="header-actions">
      <a class="btn btn-green btn-rent" href="{RENT}">{RENT_LABEL}</a>
      <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="main-nav"><span class="nav-toggle-bars" aria-hidden="true"></span><span class="nav-label">Menu</span></button>
    </div>
  </div>
</header>'''


def since_line():
    return f"since {html.escape(str(K['sinceYear']))}" if K.get("sinceYear") else "since " + ph("year Midway Ventures started renting the shop")


def footer():
    towns = "".join(f'<li><a href="{t["url"]}">Shop for rent near {t["name"]}</a></li>' for t in TOWNS)
    email = (f'<br><a href="mailto:{html.escape(K["email"])}">{html.escape(K["email"])}</a>' if K.get("email")
             else '<!-- TODO: confirm with owner: email address for the footer -->')
    return f'''<footer class="site-footer">
  <div class="trust"><div class="wrap">{NAME} &middot; <a href="{TEL}">{PHONE}</a> &middot; Renting shop space in the Big Horn Basin {since_line()}</div></div>
  <div class="wrap footer-grid">
    <div>
      <a class="footer-logo" href="/"><img src="/assets/img/logo-white.svg" width="250" height="36" alt="{NAME} logo" loading="lazy"></a>
      <address>
        <p><strong style="color:#fff">{NAME}</strong><br>{C["street"]}<br>{C["city"]}, {C["region"]} {C["zip"]}</p>
        <p><a href="{TEL}">{PHONE}</a>{email}</p>
      </address>
    </div>
    <div>
      <h2>The shop</h2>
      <ul>
        <li><a href="/the-shop/">Size, features &amp; photos</a></li>
        <li><a href="/the-shop/#price">Price &amp; availability</a></li>
        <li><a href="{RENT}">Rent online</a></li>
        <li><a href="/faq/">FAQ</a></li>
        <li><a href="/contact/">Contact &amp; directions</a></li>
      </ul>
    </div>
    <div>
      <h2>Nearby towns</h2>
      <ul>{towns}</ul>
    </div>
  </div>
  <div class="wrap footer-bottom">
    <span>&copy; {YEAR} {NAME}</span>
    <span>Built by <a href="https://eaglewebcreation.com/">Eagle Web Creation</a></span>
  </div>
</footer>
<nav class="mobile-bar" aria-label="Quick actions">
  <a class="mb-call" href="{TEL}">{ICON["phone"]}Call</a>
  <a class="mb-rent" href="{RENT}">{RENT_LABEL}</a>
</nav>'''


def breadcrumbs_html(trail):
    lis = []
    for i, (n, u) in enumerate(trail):
        if i == len(trail) - 1:
            lis.append(f'<li><span aria-current="page">{n}</span></li>')
        else:
            lis.append(f'<li><a href="{u}">{n}</a></li>')
    return f'<nav class="breadcrumbs" aria-label="Breadcrumb"><ol>{"".join(lis)}</ol></nav>'


def page_hero(kicker, h1, intro, trail, mark=""):
    return f'''<section class="page-hero" data-mark="{mark}">
  <div class="wrap">
    {breadcrumbs_html(trail)}
    <span class="kicker">{kicker}</span>
    <h1>{h1}</h1>
    <p>{intro}</p>
  </div>
</section>'''


def cta_band(heading, text, sid="cta"):
    return f'''<section class="cta-band" aria-labelledby="{sid}-h">
  <div class="wrap">
    <h2 id="{sid}-h">{heading}</h2>
    <p>{text}</p>
    <div class="btn-row"><a class="btn btn-green" href="{RENT}">{RENT_LABEL}</a><a class="btn btn-line" href="{TEL}">{ICON["phone"]}Call {PHONE}</a></div>
  </div>
</section>'''


def map_embed():
    q = "1781+US+Highway+310,+Lovell,+WY+82431"
    return f'''<div><div class="map-embed"><iframe src="https://maps.google.com/maps?q={q}&amp;z=13&amp;output=embed" title="Map: {NAME}, {ADDR_LINE}" loading="lazy" referrerpolicy="no-referrer-when-downgrade" allowfullscreen></iframe></div>
<p class="note"><a href="{DIRECTIONS}">Get driving directions to the shop</a></p></div>'''


def faq_html(items, hl="h3"):
    out = ['<div class="faq-list">']
    for q, a, slug in items:
        out.append(f'<details class="faq-item" id="{slug}"><summary><{hl}>{q}</{hl}></summary><div class="faq-a">{a}</div></details>')
    out.append("</div>")
    return "\n".join(out)


def strip_tags(s):
    s = re.sub(r"<!--.*?-->", "", s, flags=re.S)
    s = re.sub(r"<[^>]+>", "", s)
    return html.unescape(re.sub(r"\s+", " ", s)).strip()


def faq_schema(items, url):
    """FAQPage schema that matches the visible answers word for word. Answers still waiting on
    the owner are left out of the schema until they are filled in."""
    return {"@context": "https://schema.org", "@type": "FAQPage", "@id": url + "#faq",
            "mainEntity": [{"@type": "Question", "name": strip_tags(q),
                            "acceptedAnswer": {"@type": "Answer", "text": strip_tags(a)}}
                           for q, a, _ in items if PH_TEXT not in a]}


def breadcrumb_schema(trail):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": html.unescape(n), "item": SITE + u}
                                for i, (n, u) in enumerate(trail)]}


def offer():
    return {"@type": "Offer",
            "name": f'Heated shop space, {S["w"]} x {S["d"]} ft with {S["h"]} ft ceilings, private bathroom and private office',
            "url": C["rentUrl"],
            "availability": "https://schema.org/InStock" if OPEN else "https://schema.org/OutOfStock",
            "priceSpecification": {"@type": "UnitPriceSpecification", "price": float(S["rent"].replace(",", "")),
                                   "priceCurrency": "USD", "unitCode": "MON",
                                   "description": "Base monthly rent before card or ACH payment fees."}}


def business_schema():
    s = {
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        "@id": BIZ_ID,
        "name": NAME,
        "url": SITE + "/",
        "logo": SITE + "/assets/img/logo-640.png",
        "image": SITE + "/assets/img/share-1200x630.jpg",
        "description": f'Rents a heated {S["w"]} x {S["d"]} ft shop with {S["h"]}-foot ceilings, a private bathroom '
                       f'and a private office on US-310 just west of Lovell, Wyoming. Rent online.',
        "telephone": C["phoneTel"],
        "address": {"@type": "PostalAddress", "streetAddress": C["street"], "addressLocality": C["city"],
                    "addressRegion": C["region"], "postalCode": C["zip"], "addressCountry": "US"},
        "hasMap": html.unescape(DIRECTIONS),
        "areaServed": [city(t) for t in TOWNS],
        "priceRange": f'${S["rent"]} per month',
        "currenciesAccepted": "USD",
        "paymentAccepted": "Credit card, debit card, ACH bank draft",
        "amenityFeature": [{"@type": "LocationFeatureSpecification", "name": n, "value": True}
                           for n in ["Heated", "Private bathroom", "Private office", f'{S["h"]} ft ceilings',
                                     "Online rental"]],
        "makesOffer": offer(),
    }
    if K.get("email"):
        s["email"] = K["email"]
    if K.get("sameAs"):
        s["sameAs"] = K["sameAs"]
    return s


def service_schema(url, name, t):
    return {"@context": "https://schema.org", "@type": "Service", "@id": SITE + url + "#service",
            "name": name, "serviceType": "Heated shop space rental", "url": SITE + url,
            "provider": {"@id": BIZ_ID}, "areaServed": city(t), "offers": offer()}


# ---------------------------------------------------------------- page shell
def page(path, title, desc, body, *, current=None, schema=(), noindex=False):
    if len(title) > 60:
        print(f"WARN title {len(title)} chars on {path}: {title}")
    if len(desc) > 155:
        print(f"WARN desc {len(desc)} chars on {path}: {desc}")
    url = SITE + path
    ld = "\n".join(f'<script type="application/ld+json">{json.dumps(s, ensure_ascii=False, separators=(",", ":"))}</script>'
                   for s in [business_schema()] + list(schema))
    # The logo animation plays on the first page of a visit, not on every click.
    boot = ("(function(d){d.className+=' js';try{if(sessionStorage.getItem('mvLogo'))d.className+=' logo-seen';"
            "else sessionStorage.setItem('mvLogo','1')}catch(e){}})(document.documentElement)")
    robots = ('<meta name="robots" content="noindex, nofollow">' if noindex or not PROD
              else '<meta name="robots" content="index, follow, max-image-preview:large">')
    canonical = "" if noindex else f'<link rel="canonical" href="{url}">'
    verif = ""
    if K.get("googleSiteVerification"):
        verif += f'<meta name="google-site-verification" content="{html.escape(K["googleSiteVerification"])}">'
    if K.get("bingSiteVerification"):
        verif += f'<meta name="msvalidate.01" content="{html.escape(K["bingSiteVerification"])}">'
    ga = ""
    if K.get("ga4MeasurementId"):
        g = html.escape(K["ga4MeasurementId"])
        ga = (f'<script async src="https://www.googletagmanager.com/gtag/js?id={g}"></script>'
              f"<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}"
              f"gtag('js',new Date());gtag('config','{g}');</script>")
    og = SITE + "/assets/img/share-1200x630.jpg"
    t, d = html.escape(title), html.escape(desc)
    doc = f'''<!doctype html>
<html lang="en-US">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{t}</title>
<meta name="description" content="{d}">
{robots}
{canonical}
<script>{boot}</script>
<link rel="preload" href="/assets/fonts/archivo-var.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/source-sans-3-var.woff2" as="font" type="font/woff2" crossorigin>
<style>{CSS_MIN}</style>
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<meta name="theme-color" content="#0f3c0f">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{NAME}">
<meta property="og:locale" content="en_US">
<meta property="og:title" content="{t}">
<meta property="og:description" content="{d}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{og}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{NAME} logo: heated shop for rent, 36 by 45 feet with a 16 foot ceiling">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{t}">
<meta name="twitter:description" content="{d}">
<meta name="twitter:image" content="{og}">
<!-- Search Console / Bing: set "googleSiteVerification" / "bingSiteVerification" in site-config.json CONFIRM and rebuild. GA4: set "ga4MeasurementId". -->
{verif}{ga}
{ld}
<script src="/assets/js/site.js?v={JS_V}" defer></script>
</head>
<body>
{header(current)}
<main id="main">
{body}
</main>
{footer()}
</body>
</html>
'''
    doc = re.sub(r"\n{2,}", "\n", doc)
    out = PUB / ("404.html" if path == "/404.html" else "index.html" if path == "/" else path.strip("/") + "/index.html")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc)
    return path


def photo_slot(what):
    return (f'<figure class="photo-slot"><!-- TODO: owner photo: {what} --><div>{ICON["camera"]}'
            f'<strong>[waiting on photos]</strong>{what}</div></figure>')


# ---------------------------------------------------------------- shared blocks
def inside_list(h="h3"):
    office = (f'Its own room with a door, apart from the shop floor. Size: {html.escape(K["officeSize"])}.'
              if K.get("officeSize") else f'Its own room with a door, apart from the shop floor. Size: {ph("office size")}')
    return f'''<ul class="inside">
  <li class="hot"><span class="ic">{ICON["heat"]}</span><div><{h}>Heated</{h}><p>Work through a Wyoming winter without losing feeling in your hands. Paint, glue and gaskets get the warm room they need.</p></div></li>
  <li><span class="ic">{ICON["height"]}</span><div><{h}>{S["h"]}-foot ceilings</{h}><p>Room overhead for lifting, tall racks, or a vehicle with something mounted on top.</p></div></li>
  <li><span class="ic">{ICON["floor"]}</span><div><{h}>{S["w"]} &times; {S["d"]} open floor</{h}><p>{SQFT:,} square feet to lay out the way your work needs it.</p></div></li>
  <li><span class="ic">{ICON["bath"]}</span><div><{h}>Private bathroom</{h}><p>Your own restroom inside the building, so a long day in the shop doesn&rsquo;t mean leaving it.</p></div></li>
  <li><span class="ic">{ICON["office"]}</span><div><{h}>Private office</{h}><p>{office}</p></div></li>
</ul>'''


def price_band(sid="price"):
    status_txt = ("The shop is open to rent right now." if OPEN
                  else "The shop is rented right now. Join the waitlist on the rental page to hear when it opens.")
    return f'''<section class="price-band" id="{sid}" aria-labelledby="{sid}-h">
  <div class="wrap">
    <div>
      <span class="kicker">Price &amp; availability</span>
      <h2 id="{sid}-h">One shop, one simple price</h2>
      <p class="price-big">${S["rent"]}<small>/month</small></p>
      <p class="price-sub">Base rent as of {AS_OF}, about {PER_SQFT}&cent; per square foot. A payment fee is added on the rental page (smaller for ACH).</p>
    </div>
    <div>
      <p>{status_html()}</p>
      <p data-status-text>{status_txt}</p>
    </div>
    <div class="btn-row"><a class="btn btn-line" href="{RENT}">{RENT_LABEL}</a></div>
  </div>
</section>'''


def glance():
    return f'''<ul class="glance">
  <li><b>{S["w"]} &times; {S["d"]} ft</b><span>Open floor</span></li>
  <li><b>{S["h"]} ft</b><span>Ceiling height</span></li>
  <li><b>Heated</b><span>All winter</span></li>
  <li><b>Bath + office</b><span>Both private</span></li>
  <li><b>${S["rent"]}</b><span>Monthly base rent</span></li>
</ul>'''


# ---------------------------------------------------------------- general FAQ
def access_html():
    return fact("accessHours", "when renters can get into the shop (24/7?)")


FAQ = [
    ("How big is the shop?",
     f'<p>The floor is {S["w"]} feet wide and {S["d"]} feet deep, {SQFT:,} square feet in all, with {S["h"]}-foot ceilings inside.</p>', "size"),
    ("Is the shop heated?",
     "<p>Yes. The shop is heated, so it stays usable for work and storage through the winter.</p>", "heated"),
    ("Does the shop have a bathroom and an office?",
     f'<p>Yes, both are private and only for the renter of the shop. Office size: {fact("officeSize", "office size")}</p>', "bath-office"),
    ("How much is the rent?",
     f'<p>${S["rent"]} a month in base rent as of {AS_OF}. The <a href="{RENT}">rental page</a> adds a payment fee: about 1.75% by ACH bank draft or about 4% by card.</p>', "rent"),
    ("How do I rent the shop?",
     f'<p>Open the <a href="{RENT}">online rental page</a> and choose Rent Now, any time of day. If you would rather talk first, call <a href="{TEL}">{PHONE}</a>.</p>', "how-to-rent"),
    ("Is the shop available right now?",
     f'<p>{"It was open to rent at our last check." if OPEN else "It was rented at our last check."} This site checks the rental page every hour, and the <a href="{RENT}">rental page</a> always has the current status.</p>', "available"),
    ("How long do I have to rent for?",
     f'<p>{fact("leaseTerm", "lease term: month to month, or a minimum?")}</p>', "lease"),
    ("When can I get into the shop?",
     f"<p>{access_html()}</p>", "access"),
    ("How big is the overhead door?",
     f'<p>{fact("doorSize", "overhead door width and height, and any walk-in door")}</p>', "door"),
    ("What power does the shop have?",
     f'<p>{fact("power", "electrical service: 110 V outlets, 220 V, amps")}</p>', "power"),
    ("Where is the shop?",
     f'<p>At {ADDR_LINE}, on the highway about 4 minutes west of downtown Lovell. <a href="{DIRECTIONS}">Get directions</a>.</p>', "where"),
]


# ---------------------------------------------------------------- pages
def build_home():
    body = f'''<section class="hero" aria-labelledby="hero-h">
  <div class="wrap hero-grid">
    <div class="hero-copy">
      <span class="kicker">Shop space for rent &middot; US-310</span>
      <h1 id="hero-h">A heated {S["w"]}&nbsp;&times;&nbsp;{S["d"]} shop <span class="accent">with its own bathroom and office</span></h1>
      <p class="hero-sub">{SQFT:,} square feet of open floor under a {S["h"]}-foot ceiling. Room for the trucks, the tools and the project you&rsquo;ve been putting off, and warm enough to work in all winter.</p>
      <div class="btn-row"><a class="btn btn-green" href="{RENT}">{ICON["key"]}{RENT_LABEL}</a><a class="btn btn-line" href="/the-shop/">See the details</a></div>
      <ul class="hero-points"><li>Heated</li><li>{S["h"]} ft ceilings</li><li>Rent online</li></ul>
    </div>
    {sheet()}
  </div>
</section>
<section class="specs" aria-label="The shop at a glance">
  <ul class="wrap">
    <li><strong>{SQFT:,}</strong><span>Square feet</span></li>
    <li><strong>{S["h"]}<em> ft</em></strong><span>Ceiling height</span></li>
    <li class="hot"><strong>Heat<em>ed</em></strong><span>Usable all year</span></li>
    <li><strong>${S["rent"]}</strong><span>Per month, base rent</span></li>
  </ul>
</section>
<section class="section" aria-labelledby="inside-h">
  <div class="wrap split top">
    <div>
      <span class="kicker">What you get</span>
      <h2 id="inside-h">More than four walls and a roof</h2>
      <p class="lead">Most shop rentals are a cold box. This one is set up so you can spend a full day in it.</p>
      {inside_list()}
    </div>
    <div class="photo-pair">
      {photo_slot("The shop from the outside")}
      {photo_slot("Inside the shop")}
    </div>
  </div>
</section>
<section class="section section-paper" aria-labelledby="uses-h">
  <div class="wrap">
    <div class="section-head"><span class="kicker">Who it suits</span><h2 id="uses-h">Built for people who need room to work</h2>
    <p>A few of the ways a heated shop this size gets used. Ask us about yours.</p></div>
    <!-- TODO: confirm with owner: any uses that are not allowed in the shop (businesses open to the public, auto repair for hire, etc.) -->
    <ul class="uses">
      <li><h3>Contractors &amp; trades</h3><p>One warm place for the trailer, tools and material racks, with an office for bids.</p></li>
      <li><h3>Farm &amp; ranch repairs</h3><p>Do the winter work on the equipment without fighting the cold.</p></li>
      <li><h3>Vehicle projects</h3><p>Space for the truck, the engine stand and every part you pull off.</p></li>
      <li><h3>Business stock</h3><p>Inventory and supplies kept dry and above freezing.</p></li>
      <li><h3>Toys &amp; off-season gear</h3><p>Side-by-sides, sleds and trailers stored out of the weather.</p></li>
    </ul>
  </div>
</section>
{price_band()}
<section class="section" aria-labelledby="how-h">
  <div class="wrap">
    <div class="section-head"><span class="kicker">How it works</span><h2 id="how-h">Rent the shop in three steps</h2></div>
    <ol class="steps">
      <li><h3>Look it over</h3><p>Read the <a href="/the-shop/">shop details</a> or call <a href="{TEL}">{PHONE}</a> with questions.</p></li>
      <li><h3>Rent online</h3><p>Choose Rent Now on the <a href="{RENT}">rental page</a> and finish the steps there.</p></li>
      <li><h3>Move in</h3><p>Pay online by ACH or card, then bring in your equipment and get to work.</p></li>
    </ol>
  </div>
</section>
<!-- No customer reviews of Midway Ventures were found on Google or Facebook (Nov 21, 2026). Add real ones here, word for word, once there are some. -->
<section class="section section-paper" aria-labelledby="find-h">
  <div class="wrap split">
    <div>
      <span class="kicker">Find the shop</span>
      <h2 id="find-h">On the highway, a few minutes from town</h2>
      <p><strong>{ADDR_LINE}</strong></p>
      <p>The shop is on US-310 about 4 minutes west of downtown Lovell, close to where US-14A splits off toward Byron and Powell.</p>
      <p><a href="{TEL}">{PHONE}</a></p>
      <div class="btn-row"><a class="btn btn-dark" href="{DIRECTIONS}">Get Directions</a><a class="btn btn-line" href="/contact/">Contact</a></div>
    </div>
    {map_embed()}
  </div>
</section>
{cta_band("Ready for a shop of your own?", f"Heated, {S['h']}-foot ceilings, a private bathroom and office, ${S['rent']} a month in base rent.")}'''
    page("/", "Heated Shop for Rent | Midway Ventures LLC, Lovell WY",
         f'Rent a heated {S["w"]}x{S["d"]} shop with 16-ft ceilings, a private bathroom and a private office. ${S["rent"]}/month base rent. Rent online.',
         body, current="/")


SHOP_FAQ = [FAQ[0], FAQ[2], FAQ[3], FAQ[8], FAQ[9]]


def build_shop():
    trail = [("Home", "/"), ("The Shop", "/the-shop/")]
    office = html.escape(K["officeSize"]) if K.get("officeSize") else ph("office size")
    rows = [
        ("Floor", f'{S["w"]} ft wide &times; {S["d"]} ft deep'),
        ("Floor area", f"{SQFT:,} square feet"),
        ("Ceiling height", f'{S["h"]} ft inside'),
        ("Heat", "Yes, heated" + (f' ({html.escape(K["heatType"])})' if K.get("heatType") else '<!-- TODO: confirm with owner: type of heat -->')),
        ("Bathroom", "Private, inside the shop"),
        ("Office", f"Private, size {office}"),
        ("Overhead door", fact("doorSize", "overhead door size")),
        ("Power", fact("power", "electrical service")),
        ("Access", access_html()),
        ("Lease term", fact("leaseTerm", "lease term")),
        ("Base rent", f'${S["rent"]} a month as of {AS_OF}'),
        ("Address", ADDR_LINE),
    ]
    table = "".join(f'<tr><th scope="row">{a}</th><td>{b}</td></tr>' for a, b in rows)
    body = f'''{page_hero("The shop", f"A heated {S['w']}&nbsp;&times;&nbsp;{S['d']} shop with a bathroom and office", f"Everything we know about the shop at {C['street']}: size, features, price and how to rent it.", trail, mark=f"{S['w']}&times;{S['d']}")}
<section class="section" aria-labelledby="draw-h">
  <div class="wrap split">
    <div>
      <h2 id="draw-h">How big {SQFT:,} square feet really is</h2>
      <p>The drawing is to scale. A full-size pickup takes up a small corner of the floor, and a person standing inside barely reaches a third of the way to the ceiling.</p>
      <p>We haven&rsquo;t drawn the bathroom and office because their exact layout isn&rsquo;t posted yet. Photos are coming.</p>
      <div class="btn-row"><a class="btn btn-green" href="{RENT}">{RENT_LABEL}</a></div>
    </div>
    {sheet()}
  </div>
</section>
<section class="section section-paper" aria-labelledby="spec-h">
  <div class="wrap split top">
    <div>
      <h2 id="spec-h">Shop details</h2>
      <table class="spec-table"><caption class="visually-hidden">Midway Ventures shop specifications</caption><tbody>{table}</tbody></table>
    </div>
    <div>
      <h2 class="h3">What&rsquo;s included</h2>
      {inside_list(h="h3")}
    </div>
  </div>
</section>
<section class="section" aria-labelledby="photos-h">
  <div class="wrap">
    <div class="section-head"><h2 id="photos-h">Photos</h2></div>
    <div class="grid g3">{photo_slot("Outside and the overhead door")}{photo_slot("The shop floor")}{photo_slot("Bathroom and office")}</div>
  </div>
</section>
{price_band()}
<section class="section" aria-labelledby="how-h">
  <div class="wrap narrow">
    <h2 id="how-h">How renting works</h2>
    <ul class="check-list">
      <li>Choose Rent Now on the <a href="{RENT}">rental page</a> and fill in your details there. If the shop is rented, the same page takes a waitlist sign-up.</li>
      <li>Pay by ACH bank draft for the smaller payment fee, or by card.</li>
      <li>Questions before you rent? Call <a href="{TEL}">{PHONE}</a>.</li>
    </ul>
  </div>
</section>
<section class="section section-paper" aria-labelledby="sfaq-h">
  <div class="wrap narrow">
    <h2 id="sfaq-h">Questions about the shop</h2>
    {faq_html(SHOP_FAQ)}
    <p class="mt"><a href="/faq/">More questions and answers</a></p>
  </div>
</section>
{cta_band("Want to see it in person?", "Call to ask about a walk-through, or rent it online now.")}'''
    page("/the-shop/", "Heated 36x45 Shop: Size, Price & Details | Midway Ventures",
         f'Heated 36x45 shop, 1,620 sq ft, 16-ft ceilings, private bathroom and office on US-310 near Lovell, WY. ${S["rent"]}/month base rent.',
         body, current="/the-shop/", schema=[faq_schema(SHOP_FAQ, SITE + "/the-shop/"), breadcrumb_schema(trail)])


def build_contact():
    trail = [("Home", "/"), ("Contact", "/contact/")]
    email = (f'<a href="mailto:{html.escape(K["email"])}">{html.escape(K["email"])}</a>' if K.get("email")
             else ph("email address"))
    body = f'''{page_hero("Contact &amp; directions", f"Contact {NAME}", "Call with questions about the shop, rent it online, or find your way here.", trail, mark="307")}
<section class="section" aria-labelledby="nap-h">
  <div class="wrap split top">
    <div class="nap-card">
      <h2 id="nap-h">{NAME}</h2>
      <dl>
        <dt>Address</dt><dd>{C["street"]}<br>{C["city"]}, {C["region"]} {C["zip"]}</dd>
        <dt>Phone</dt><dd><a href="{TEL}">{PHONE}</a></dd>
        <dt>Email</dt><dd>{email}</dd>
        <dt>Shop access</dt><dd>{access_html()}</dd>
        <dt>Status</dt><dd>{status_html()}</dd>
      </dl>
      <div class="btn-row mt"><a class="btn btn-green" href="{RENT}">{RENT_LABEL}</a><a class="btn btn-line" href="{TEL}">{ICON["phone"]}Call</a></div>
    </div>
    {map_embed()}
  </div>
</section>
<section class="section section-paper" aria-labelledby="dir-h">
  <div class="wrap">
    <h2 id="dir-h">Getting here</h2>
    <div class="grid g3">
      <div><h3>From Lovell</h3><p>Head west out of town on US-310. The shop is about 2.7 miles out, on the highway.</p></div>
      <div><h3>From Powell, Cody or Byron</h3><p>Take US-14A east past Byron. The shop is near where US-14A meets US-310, just before Lovell.</p></div>
      <div><h3>From Greybull or Basin</h3><p>Take US-310 north into Lovell, then keep going west through town for about 2.7 miles.</p></div>
    </div>
    <p class="note mt"><a href="{DIRECTIONS}">Open turn-by-turn directions in Google Maps</a></p>
  </div>
</section>'''
    page("/contact/", "Contact & Directions | Midway Ventures LLC",
         f"Call {NAME} at {PHONE} about the heated shop at {ADDR_LINE}, or rent it online.",
         body, current="/contact/", schema=[breadcrumb_schema(trail)])


def build_faq():
    trail = [("Home", "/"), ("FAQ", "/faq/")]
    towns = "".join(f'<li><a href="{t["url"]}">{t["name"]}, WY<span>{t["drive"]}</span></a></li>' for t in TOWNS)
    body = f'''{page_hero("FAQ", "Shop rental questions, answered", "Size, heat, price, renting and getting here.", trail, mark="FAQ")}
<section class="section" aria-labelledby="faq-h">
  <div class="wrap narrow">
    <h2 id="faq-h" class="visually-hidden">Frequently asked questions</h2>
    {faq_html(FAQ)}
  </div>
</section>
<section class="section section-paper" aria-labelledby="towns-h">
  <div class="wrap">
    <div class="section-head"><h2 id="towns-h">Renting from a nearby town?</h2>
    <p>Drive times to the shop on the fastest route, and what renters from each town tend to use it for.</p></div>
    <ul class="area-links">{towns}</ul>
  </div>
</section>
{cta_band("Didn't see your question?", f"Call {PHONE} and ask, or look over the shop details.")}'''
    page("/faq/", "Shop Rental FAQ | Midway Ventures LLC",
         "Answers about the heated 36x45 shop from Midway Ventures LLC: size, heat, bathroom and office, rent, payment fees and how to rent.",
         body, current="/faq/", schema=[faq_schema(FAQ, SITE + "/faq/"), breadcrumb_schema(trail)])


# ---------------------------------------------------------------- town pages
# Each town gets its own angle, route, story and questions so no two pages share much text.
TOWN_PAGES = {
    "lovell": dict(
        title="Shop Space Near Downtown Lovell, WY | Midway Ventures",
        desc="Heated 36x45 shop for rent 4 minutes from downtown Lovell, WY. 16-ft ceilings, private bathroom and office. Move the business out of the garage.",
        kicker="Shop space in Lovell",
        h1="Shop space for rent in Lovell, Wyoming",
        intro="Outgrown the garage at home? The Midway Ventures shop sits on US-310 about four minutes west of downtown Lovell.",
        route=["Start on Main Street in downtown Lovell", "Head west out of town on US-310", "Look for 1781 US Highway 310, about 2.7 miles out"],
        story_h="Move the business out of the garage",
        story=["Plenty of Lovell businesses start in a garage or the pole barn behind the house. At some point the work needs its own space, and the family wants the garage back. This shop gives you 1,620 square feet without building anything.",
               "Being this close means the shop fits into a normal day. Run out after breakfast, come back for lunch, and still make the kids' game. Four minutes each way is easy to live with.",
               "The private office is somewhere to keep invoices and take calls away from the noise, and the private bathroom means you aren't driving home to use one."],
        faq=[("How far is the shop from downtown Lovell?", "<p>About 4 minutes and 2.7 miles west on US-310, on the fastest Google Maps route.</p>", "lovell-far"),
             ("Is the office separate from the shop floor?", f'<p>Yes, the office is a private room of its own. Size: {fact("officeSize", "office size")}</p>', "lovell-office"),
             ("What does the shop rent for?", f'<p>${S["rent"]} a month in base rent as of {AS_OF}. The rental page adds a payment fee, which is smaller if you pay by ACH.</p>', "lovell-rent")],
        cta=("Your own shop, four minutes from home", "Rent it online, or call with questions first."),
    ),
    "cowley": dict(
        title="Heated Shop Space Near Cowley, WY | Midway Ventures",
        desc="Heated shop for rent about 4 minutes from Cowley, WY. Do winter repairs on farm and ranch equipment in a warm 36x45 building with 16-ft ceilings.",
        kicker="Shop space near Cowley",
        h1="Heated shop space near Cowley, Wyoming",
        intro="Working on equipment in a cold barn in January gets old. The Midway Ventures shop is about four minutes east of Cowley on US-310.",
        route=["Leave Cowley heading east on US-310", "Drive toward Lovell for about 3.5 miles", "Pull in at 1781 US Highway 310"],
        story_h="Winter repairs, done warm",
        story=["Around Cowley, winter is when the swather, the baler and the feed truck get fixed. Doing that in an unheated barn means stiff hands, slow work and parts that won't seal right. A heated building lets the work go at summer speed.",
               "A 36-foot-wide floor and a 16-foot ceiling leave room to walk all the way around a piece of equipment and still have space for the welder and the parts washer.",
               "There's a private bathroom inside, so a long day of repairs doesn't mean trips back to the house."],
        faq=[("How far is the shop from Cowley?", "<p>About 4 minutes and 3.5 miles east on US-310, on the fastest Google Maps route.</p>", "cowley-far"),
             ("How tall is the shop inside?", f'<p>{S["h"]} feet. The overhead door size: {fact("doorSize", "overhead door size")}</p>', "cowley-tall"),
             ("Can I work in the shop through the winter?", "<p>Yes. The building is heated, which is the whole point for winter equipment work.</p>", "cowley-winter")],
        cta=("Get the equipment out of the cold", "A heated shop four minutes from Cowley. Rent it online."),
    ),
    "byron": dict(
        title="Heated Shop for Rent Near Byron, WY | Midway Ventures",
        desc="A heated 36x45 shop about 5 minutes from Byron, WY. Room for a truck restoration, the engine stand and the parts, with a bathroom and office.",
        kicker="Shop space near Byron",
        h1="A heated shop for vehicle projects near Byron, Wyoming",
        intro="The truck you've been meaning to restore deserves better than a carport. This shop is about five minutes from Byron on US-14A.",
        route=["Leave Byron on US-14A toward Lovell", "Stay on the highway about 4.7 miles", "Watch for 1781 US Highway 310"],
        story_h="Room for the project and all its parts",
        story=["Restoring an old pickup or rebuilding a motor takes months, and the parts pile up. At 36 by 45 feet there's room for the vehicle, a bench, the engine stand and shelves of parts without tripping over any of it.",
               "Heat matters most for this kind of work. Paint, body filler and gaskets all want a warm room, and you'll actually go out to the shop on a February evening when it isn't ten degrees inside.",
               "A bathroom to wash up in and an office for receipts and service manuals make it feel like your own place instead of a rented box."],
        faq=[("How long is the drive from Byron?", "<p>About 5 minutes and 4.7 miles on US-14A, on the fastest Google Maps route.</p>", "byron-far"),
             ("How much floor space is there?", f'<p>{SQFT:,} square feet: {S["w"]} feet wide by {S["d"]} feet deep, under a {S["h"]}-foot ceiling.</p>', "byron-floor"),
             ("Is there a place to wash up?", "<p>Yes. The shop has its own private bathroom.</p>", "byron-wash")],
        cta=("Give the project a real shop", "Heated, roomy and five minutes from Byron."),
    ),
    "powell": dict(
        title="Shop Space for Contractors Near Powell, WY | Midway",
        desc="Heated shop space for contractors, 22 minutes from Powell, WY. 1,620 sq ft for trucks, trailers and tools, plus a private office for paperwork.",
        kicker="Shop space near Powell",
        h1="Shop space for contractors near Powell, Wyoming",
        intro="If your crews work up and down the valley, a base between Powell and Lovell keeps the trucks and tools in one warm place. The shop is 22 minutes east of Powell.",
        route=["Leave Powell on US-14A heading east", "Drive through Byron", "Continue toward Lovell to 1781 US Highway 310"],
        story_h="A home base for the crew",
        story=["Contractors around Powell often end up with tools in three pickups, material in a yard and paperwork on the kitchen table. A heated 1,620-square-foot shop puts the tools, the trailer and the material racks under one roof.",
               "The private office is where bids, invoices and job folders can live, with a door you can close when a customer calls.",
               "Mornings start better too. Load out in a warm building instead of scraping frost off the tools, then head to jobs anywhere from Powell to Lovell."],
        faq=[("How far is the shop from Powell?", "<p>About 22 minutes and 19.6 miles east on US-14A, on the fastest Google Maps route.</p>", "powell-far"),
             ("Is there an office for paperwork?", f'<p>Yes, a private office inside the shop. Size: {fact("officeSize", "office size")}</p>', "powell-office"),
             ("How does my business pay the rent?", "<p>Through the online rental page, by ACH bank draft or card. ACH has the smaller payment fee.</p>", "powell-pay")],
        cta=("Set up a base for the crew", "Rent the shop online or call with questions."),
    ),
    "greybull": dict(
        title="Heated Equipment Shop Near Greybull, WY | Midway Ventures",
        desc="Keep work trucks warm and ready in a heated 36x45 shop, 36 minutes from Greybull, WY. 16-ft ceilings, private office and bathroom.",
        kicker="Shop space near Greybull",
        h1="A heated equipment shop near Greybull, Wyoming",
        intro="Diesels that sit outside all night don't like a 20-below morning. A heated building keeps the work trucks ready, 36 minutes north of Greybull.",
        route=["Take US-310 north out of Greybull", "Follow it into Lovell", "Keep going west through town about 2.7 miles"],
        story_h="Keep the fleet warm and ready",
        story=["For trucking, hauling and ag outfits around Greybull, cold starts cost time every winter morning. Parked inside a heated shop, the trucks fire up and the hydraulics move when you need them to.",
               "The 16-foot ceiling and the open floor leave space for vehicles plus a bench and parts shelving along the walls.",
               "The private office gives dispatch and paperwork a quiet corner, and the bathroom saves a trip off site."],
        faq=[("How far is the shop from Greybull?", "<p>About 36 minutes and 35.2 miles north on US-310, on the fastest Google Maps route.</p>", "greybull-far"),
             ("How big is the overhead door?", f'<p>{fact("doorSize", "overhead door size")}</p>', "greybull-door"),
             ("Is the shop open to rent right now?", f'<p>{"It was open at our last check." if OPEN else "It was rented at our last check."} The <a href="{RENT}">rental page</a> always shows the current status.</p>', "greybull-open")],
        cta=("Warm trucks on cold mornings", "Rent the heated shop online."),
    ),
    "basin": dict(
        title="Warehouse & Shop Space Near Basin, WY | Midway Ventures",
        desc="Heated warehouse and shop space 44 minutes from Basin, WY. 1,620 sq ft for inventory and supplies, with a private office. About 77 cents per sq ft.",
        kicker="Shop space near Basin",
        h1="Warehouse and shop space near Basin, Wyoming",
        intro="Running a business out of Basin with nowhere to keep the stock? This heated shop works as a small warehouse with its own office, 44 minutes north.",
        route=["Take US-16/20 north from Basin to Greybull", "Pick up US-310 north to Lovell", "Drive west through town to the shop"],
        story_h="Room for inventory, supplies and records",
        story=["Retail stock, seasonal inventory, building supplies, boxes of records: small businesses in Basin often outgrow the back room before they're ready to buy a building. Renting 1,620 square feet of heated space bridges that gap.",
               "Heat protects what you keep from the deep freezes, which matters for paint, liquids, electronics and anything else that doesn't like the cold.",
               "The private office is a place to work through orders with the stock right outside the door, and the bathroom makes a full day of counting inventory doable."],
        faq=[("How far is the shop from Basin?", "<p>About 44 minutes and 42.8 miles: north on US-16/20 to Greybull, then US-310 to Lovell.</p>", "basin-far"),
             ("What does it work out to per square foot?", f'<p>${S["rent"]} a month for {SQFT:,} square feet is about {PER_SQFT} cents per square foot per month in base rent, before payment fees.</p>', "basin-sqft"),
             ("Will the shop stay above freezing?", f'<p>The shop is heated. Heat type and setting: {fact("heatType", "type of heat and the temperature it holds")}</p>', "basin-freeze")],
        cta=("Give the stock a warm home", "Rent the shop online or call to talk it over."),
    ),
    "cody": dict(
        title="Off-Season Shop Space for Cody, WY | Midway Ventures",
        desc="Heated off-season space for Cody, WY outfitters and owners, 47 minutes east. 36x45 shop, 16-ft ceilings, bathroom and office. Rent online.",
        kicker="Shop space for Cody",
        h1="Off-season shop space for Cody, Wyoming outfits",
        intro="When the tourists and hunters head home, a lot of Cody businesses need a warm place for the gear until spring. The shop is about 47 minutes east.",
        route=["Take US-14A east out of Cody to Powell", "Stay on US-14A through Byron", "Continue toward Lovell to 1781 US Highway 310"],
        story_h="Somewhere warm for the gear between seasons",
        story=["Guides, outfitters and tour operators spend the winter fixing what the summer wore out: rafts, trailers, tack, coolers, side-by-sides. A heated 36 by 45 foot shop holds the whole outfit with room left over to work on it.",
               "Sixteen-foot ceilings help when the gear stacks high, and the floor is open so you can lay it out the way you load it.",
               "Most owners only make the drive a few times a season, so 47 minutes is a fair trade for a heated building with its own bathroom and office."],
        faq=[("How far is the shop from Cody?", "<p>About 47 minutes and 43.4 miles east on US-14A through Powell, on the fastest Google Maps route.</p>", "cody-far"),
             ("Can I rent without coming out first?", f'<p>Yes. You can rent on the <a href="{RENT}">online rental page</a>, and call <a href="{TEL}">{PHONE}</a> with any questions.</p>', "cody-online"),
             ("Is it heated all winter?", "<p>Yes, the shop is heated, so gear and equipment aren't sitting in the cold until spring.</p>", "cody-heat")],
        cta=("Park the outfit somewhere warm", "Set it all up online from Cody."),
    ),
}


def town_page(slug):
    t, d = TOWN[slug], TOWN_PAGES[slug]
    trail = [("Home", "/"), (f'Shop for rent near {t["name"]}', t["url"])]
    route = "".join(f"<li>{r}</li>" for r in d["route"])
    story = "".join(f"<p>{p}</p>" for p in d["story"])
    others = "".join(f'<li><a href="{o["url"]}">{o["name"]}, WY<span>{o["drive"]}</span></a></li>'
                     for o in TOWNS if o["slug"] != slug)
    body = f'''{page_hero(d["kicker"], d["h1"], d["intro"], trail, mark=t["name"].upper())}
<section class="section" aria-labelledby="story-h">
  <div class="wrap split top">
    <div class="prose"><h2 id="story-h">{d["story_h"]}</h2>{story}</div>
    <aside class="drive-card" aria-labelledby="drive-h">
      <h2 id="drive-h" class="h3">The drive from {t["name"]}</h2>
      <p class="big">{t["short"]}</p><p>{t["mi"]} on the fastest route</p>
      <ol class="route">{route}</ol>
      <a class="btn btn-line btn-sm" href="{DIRECTIONS}">Directions</a>
    </aside>
  </div>
</section>
<section class="section section-paper" aria-labelledby="glance-h">
  <div class="wrap">
    <div class="section-head"><h2 id="glance-h">The shop at a glance</h2></div>
    {glance()}
    <p class="note mt">{"Open to rent at our last check." if OPEN else "Rented at our last check; join the waitlist on the rental page."} <a href="/the-shop/">See every detail</a>.</p>
  </div>
</section>
<section class="section" aria-labelledby="q-h">
  <div class="wrap narrow"><h2 id="q-h">{t["name"]} questions</h2>{faq_html(d["faq"])}</div>
</section>
<section class="section section-paper" aria-labelledby="other-h">
  <div class="wrap"><h2 id="other-h" class="h3">Other towns nearby</h2><ul class="area-links">{others}</ul></div>
</section>
{cta_band(d["cta"][0], d["cta"][1])}'''
    page(t["url"], d["title"], d["desc"], body,
         schema=[service_schema(t["url"], f'Heated shop for rent near {t["name"]}, WY', t),
                 faq_schema(d["faq"], SITE + t["url"]), breadcrumb_schema(trail)])


def build_404():
    body = f'''<section class="page-hero notfound" data-mark="404">
  <div class="wrap">
    <span class="kicker">Error 404</span>
    <h1>This page isn&rsquo;t here</h1>
    <p>The link may be old or mistyped. The shop is still here, though.</p>
    <div class="btn-row"><a class="btn btn-green" href="/">Go to the home page</a><a class="btn btn-line" href="{TEL}">{ICON["phone"]}Call {PHONE}</a></div>
  </div>
</section>
<section class="section"><div class="wrap">
  <ul class="link-cards">
    <li><a href="/the-shop/"><strong>The shop</strong>Size, features and photos</a></li>
    <li><a href="/the-shop/#price"><strong>Price &amp; availability</strong>Monthly rent and status</a></li>
    <li><a href="/faq/"><strong>FAQ</strong>Answers about renting</a></li>
    <li><a href="/contact/"><strong>Contact</strong>Phone, address and map</a></li>
    <li><a href="{RENT}"><strong>Rent online</strong>The rental page</a></li>
  </ul>
</div></section>'''
    page("/404.html", f"Page Not Found | {NAME}",
         f"That page isn't here. See the heated shop for rent or call {PHONE}.", body, noindex=True)


PAGES = ["/", "/the-shop/", "/faq/", "/contact/"] + [t["url"] for t in TOWNS]


def build_root_files():
    urls = "\n".join(f"  <url><loc>{SITE}{p}</loc><lastmod>{TODAY}</lastmod></url>" for p in PAGES)
    (PUB / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n'
                                     '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + "\n</urlset>\n")
    if PROD:
        (PUB / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")
    else:
        (PUB / "robots.txt").write_text("# Preview copy. Not for search engines.\nUser-agent: *\nDisallow:\n")
    (PUB / "site.webmanifest").write_text(json.dumps({
        "name": NAME, "short_name": C["shortName"],
        "icons": [{"src": "/android-chrome-192x192.png", "sizes": "192x192", "type": "image/png"},
                  {"src": "/android-chrome-512x512.png", "sizes": "512x512", "type": "image/png"}],
        "theme_color": "#0f3c0f", "background_color": "#ffffff", "display": "browser", "start_url": "/"}, indent=2))
    drives = "\n".join(f'- {t["name"]}, WY: {t["drive"]} ({t["mi"]})' for t in TOWNS)
    pages = "\n".join(f"- {SITE}{p}" for p in PAGES)

    def known(key, label):
        return f"- {label}: {K[key]}" if K.get(key) else f"- {label}: not published yet"
    (PUB / "llms.txt").write_text(f"""# {NAME}

> Rents one heated shop on US-310 just west of Lovell, Wyoming (Big Horn Basin): {S["w"]} x {S["d"]} ft floor ({SQFT:,} sq ft), {S["h"]} ft ceilings, a private bathroom and a private office. Rent online.

## Shop facts (as of {AS_OF})
- Size: {S["w"]} ft wide x {S["d"]} ft deep x {S["h"]} ft tall inside; {SQFT:,} sq ft
- Heated: yes
- Private bathroom: yes
- Private office: yes
- Base rent: ${S["rent"]} per month before payment fees (the rental page adds about 1.75% for ACH or about 4% for card)
- Status at last check: {"open to rent" if OPEN else "rented (waitlist)"}
{known("officeSize", "Office size")}
{known("doorSize", "Overhead door")}
{known("power", "Power")}
{known("accessHours", "Access hours")}
{known("leaseTerm", "Lease term")}

## Business facts
- Name: {NAME}
- Address: {ADDR_LINE}
- Phone: {PHONE}
- Rent online or join a waitlist: {C["rentUrl"]}

## Drive times to the shop (fastest Google Maps route)
{drives}

## Pages
{pages}
""")


def main():
    build_home()
    build_shop()
    build_contact()
    build_faq()
    for t in TOWNS:
        town_page(t["slug"])
    build_404()
    build_root_files()
    print("built", len(PAGES) + 1, "pages into", PUB, "for", SITE, "(indexable)" if PROD else "(noindex)")


if __name__ == "__main__":
    main()
