#!/usr/bin/env python3
"""Build the nothingdown.com website.

Reads site.json and data/offers.json, writes a complete static site to public/.
Standard library only, so it runs on Netlify's default build image:
    python3 build.py
"""
import datetime as dt
import html
import json
import os
import re
import shutil
from collections import OrderedDict

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "public")

try:
    import sharecards as SC  # needs Pillow; falls back to the static image without it
except Exception as _e:  # pragma: no cover
    SC = None
    print(f"Share images skipped ({_e}); using static og-image.png")

SITE = json.load(open(os.path.join(ROOT, "site.json"), encoding="utf-8"))
DATA = json.load(open(os.path.join(ROOT, "data", "offers.json"), encoding="utf-8"))
BASE_URL = SITE["url"].rstrip("/")
NAME = SITE["name"]
TAGLINE = SITE["tagline"]

META = DATA.get("meta") or {}
REFRESHED = META.get("lastRefreshed") or dt.date.today().isoformat()
REF_DATE = dt.date.fromisoformat(REFRESHED)
MONTH = REF_DATE.strftime("%B %Y")
REF_HUMAN = REF_DATE.strftime("%B %-d, %Y")
REF_DAY = REF_DATE.strftime("%A, %B %-d, %Y")  # e.g. Saturday, October 17, 2026

# Drop offers whose published end date has passed.
OFFERS = [o for o in DATA.get("offers", []) if not o.get("expires") or o["expires"] >= REFRESHED]

CATEGORIES = OrderedDict([
    ("Car lease", {
        "slug": "car-leases", "nav": "Car leases",
        "title": f"$0 Down Car Lease Deals, {MONTH}",
        "h1": f"$0 down car lease deals for {MONTH}",
        "intro": "Leases with nothing due at signing or no down payment, from Toyota, Honda, Hyundai, Kia, Mazda and more. Payments exclude tax, title and dealer fees and usually need top-tier credit.",
        "desc": f"Every current $0-down and $0-due-at-signing car lease for {MONTH}, with monthly payments, terms and the fine print. Updated every morning.",
    }),
    ("Car financing", {
        "slug": "car-financing", "nav": "Car loans",
        "title": f"Zero Down Car Financing, {MONTH}",
        "h1": f"Zero down car financing for {MONTH}",
        "intro": "Auto loans that let you finance the full price with no down payment. Most 0% APR dealer offers still expect money down, so only true zero-down loans are listed.",
        "desc": f"Auto loans with 100% financing and no down payment for {MONTH}. Rates, terms and who qualifies, checked every morning.",
    }),
    ("Home loan", {
        "slug": "home-loans", "nav": "Home loans",
        "title": f"0% Down Home Loans, {MONTH}",
        "h1": f"0% down home loans for {MONTH}",
        "intro": "Mortgages you can get with no down payment: VA and USDA loans, credit-union programs and doctor loans. Closing costs and funding fees may still apply.",
        "desc": "Zero-down mortgage programs in one list: VA, USDA, Navy Federal, physician loans and more, with fees and eligibility explained. Updated daily.",
    }),
    ("Phone", {
        "slug": "phones", "nav": "Phones",
        "title": f"$0 Down Phone Deals, {MONTH}",
        "h1": f"$0 down and free phone deals for {MONTH}",
        "intro": "Carrier deals at AT&T, T-Mobile, Verizon and Metro where the phone costs nothing up front. Most are paid back through 36 months of bill credits, and sales tax may be due at purchase.",
        "desc": f"Free and $0-down phone deals from AT&T, T-Mobile, Verizon and Metro for {MONTH}, with trade-in and plan requirements spelled out.",
    }),
    ("Home improvement", {
        "slug": "home-improvement", "nav": "Solar & home",
        "title": f"$0 Down Solar and Home Improvement Financing, {MONTH}",
        "h1": f"$0 down solar and home improvement for {MONTH}",
        "intro": "Solar, HVAC and other home upgrades you can start with nothing paid up front, through loans, leases or power purchase agreements.",
        "desc": "Zero-down solar loans, leases and home improvement financing, with the trade-offs explained. Updated every morning.",
    }),
])

FAQ = [
    ("What does $0 down actually mean?",
     "It means no down payment toward the price. You may still owe other money at signing, such as a first monthly payment, taxes, registration or fees. Each offer here shows what is due up front, and the “Only $0 due at signing” filter shows offers where nothing at all is due."),
    ("What is the difference between $0 down and $0 due at signing on a lease?",
     "A $0-down lease skips the cap cost reduction but usually still asks for the first payment and fees at signing. A $0-due-at-signing lease rolls everything into the monthly payment, so you pay nothing when you drive away, though the monthly payment is a little higher."),
    ("Who qualifies for a zero-down home loan?",
     "VA loans are for eligible service members, veterans and some surviving spouses. USDA loans are for moderate-income buyers in eligible rural and suburban areas. Credit unions such as Navy Federal and some banks’ doctor loans offer their own 0% down programs."),
    ("Are free phone deals really free?",
     "The phone is paid off with monthly bill credits, usually over 36 months, and most deals need a new line, a trade-in or a premium unlimited plan. If you leave early, the remaining phone balance comes due."),
    ("How often is this list updated?",
     "Every morning. New offers are added, changed terms are updated, and offers that have ended or can no longer be confirmed are removed."),
]

REQ_HIDE = {
    "military": ["military", "veteran"],
    "trade": ["trade-in"],
    "newline": ["new line", "switch"],
    "special": ["military", "veteran", "rural", "member", "doctor", "dentist", "attorney", "physician"],
}


def esc(s):
    return html.escape("" if s is None else str(s), quote=True)


def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", str(s).lower()).strip("-")


def fmt_date(d):
    try:
        return dt.date.fromisoformat(d).strftime("%b %-d, %Y")
    except Exception:
        return d or ""


def abs_url(path):
    return BASE_URL + path


def price_text(o):
    m = o.get("monthly")
    if isinstance(m, (int, float)):
        if m == 0 and o.get("priceLabel"):
            return o["priceLabel"]
        return f"${m:,.0f}/mo"
    return o.get("priceLabel") or "See terms"


def months_in(term):
    m = re.search(r"(\d+)\s*(?:-|to)?\s*month", str(term or ""))
    return int(m.group(1)) if m else None


def total_cost(o):
    """Approximate total of payments for leases with a fixed monthly payment and term."""
    m, n = o.get("monthly"), months_in(o.get("term"))
    if o.get("category") == "Car lease" and isinstance(m, (int, float)) and m > 0 and n:
        return round(m * n)
    return None


def offer_path(o):
    return f"/offer/{o['id']}/"


ICON_HEART = '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path d="M12 20.5s-7.5-4.6-9.3-9.2C1.4 8 3.4 4.5 7 4.5c2.1 0 3.6 1.2 5 3 1.4-1.8 2.9-3 5-3 3.6 0 5.6 3.5 4.3 6.8-1.8 4.6-9.3 9.2-9.3 9.2z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/></svg>'
ICON_SHARE = '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path d="M12 15V3m0 0L7.5 7.5M12 3l4.5 4.5M5 12v7a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-7" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>'


def actions_html(o, src_html=""):
    t = esc(o.get("title"))
    return (f'<div class="acts">'
            f'<button type="button" class="act save" data-id="{esc(o["id"])}" aria-pressed="false" aria-label="Save {t}">{ICON_HEART}<span class="act-l">Save</span></button>'
            f'<button type="button" class="act share" data-url="{offer_path(o)}" data-title="{t}" aria-label="Share {t}">{ICON_SHARE}<span class="act-l">Share</span></button>'
            f'{src_html}</div>')


def offer_flags(o):
    reqs = [r.lower() for r in (o.get("requirements") or [])]
    flags = []
    for key, words in REQ_HIDE.items():
        if any(w in r for r in reqs for w in words):
            flags.append(key)
    return " ".join(flags)


def offer_html(o, heading="h3"):
    reqs = o.get("requirements") or []
    hay = " ".join(str(x) for x in [o.get("title"), o.get("provider"), o.get("category"), o.get("summary"),
                                    o.get("dueAtSigning"), o.get("term"), " ".join(reqs), o.get("region")]).lower()
    monthly = o.get("monthly")
    tags = []
    if o.get("added") == REFRESHED:
        tags.append('<span class="tag new">New today</span>')
    if o.get("expires"):
        tags.append(f'<span class="tag exp">Ends {esc(fmt_date(o["expires"]))}</span>')
    for r in reqs:
        tags.append(f'<span class="tag req">{esc(r)}</span>')
    if o.get("term"):
        tags.append(f'<span class="tag">{esc(o["term"])}</span>')
    if o.get("region") and o.get("region") != "National":
        tags.append(f'<span class="tag">{esc(o["region"])}</span>')
    src = ""
    if str(o.get("sourceUrl", "")).startswith("https://"):
        src = (f'<a class="src" href="{esc(o["sourceUrl"])}" target="_blank" rel="nofollow noopener noreferrer">'
               f'{esc(o.get("source") or "Source")}<span aria-hidden="true"> ↗</span></a>')
    zero = bool(o.get("zeroDueAtSigning"))
    total = total_cost(o)
    return f'''<article class="offer" id="{esc(o["id"])}"
  data-cat="{esc(o.get("category"))}" data-provider="{esc(o.get("provider"))}"
  data-monthly="{esc(monthly if isinstance(monthly, (int, float)) else "")}" data-zero="{1 if zero else 0}"
  data-flags="{esc(offer_flags(o))}" data-added="{esc(o.get("added"))}" data-expires="{esc(o.get("expires"))}"
  data-title="{esc(o.get("title"))}" data-text="{esc(hay)}" data-id="{esc(o["id"])}" data-total="{total if total else ""}">
  <div class="o-head">
    <{heading} class="o-title"><a href="{offer_path(o)}">{esc(o.get("title"))}</a></{heading}>
    <p class="meta"><span class="cat">{esc(o.get("category"))}</span><span>{esc(o.get("provider"))}</span><span class="chk-date">Checked {esc(fmt_date(o.get("verified")))}</span></p>
  </div>
  <div class="price"><span class="mo">{esc(price_text(o))}</span><span class="das{" zero" if zero else ""}">{esc(o.get("dueAtSigning") or "$0 down")}</span>{f'<span class="tot">≈ ${total:,} over {months_in(o.get("term"))} mo</span>' if total else ""}</div>
  <p class="summary">{esc(o.get("summary"))}</p>
  <div class="tags">{"".join(tags)}</div>
  {actions_html(o, src)}
</article>'''


def sort_offers(offers):
    def key(o):
        m = o.get("monthly")
        return (0 if isinstance(m, (int, float)) and m > 0 else 1, m if isinstance(m, (int, float)) else 0, o.get("title", ""))
    return sorted(offers, key=key)


def offer_jsonld(offers, page_url, name):
    items = []
    for i, o in enumerate(offers, 1):
        offer = {
            "@type": "Offer",
            "name": o.get("title"),
            "description": o.get("summary"),
            "url": f"{page_url}#{o['id']}",
            "category": o.get("category"),
            "seller": {"@type": "Organization", "name": o.get("provider")},
        }
        m = o.get("monthly")
        if isinstance(m, (int, float)) and m > 0:
            offer["priceSpecification"] = {
                "@type": "UnitPriceSpecification", "price": m, "priceCurrency": "USD",
                "unitText": "MONTH", "referenceQuantity": {"@type": "QuantitativeValue", "value": 1, "unitCode": "MON"}}
        if o.get("expires"):
            offer["validThrough"] = o["expires"]
        items.append({"@type": "ListItem", "position": i, "item": offer})
    return {"@context": "https://schema.org", "@type": "ItemList", "name": name, "numberOfItems": len(items),
            "itemListOrder": "https://schema.org/ItemListUnordered", "itemListElement": items}


def breadcrumb_jsonld(crumbs):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [{"@type": "ListItem", "position": i, "name": n, "item": abs_url(p)}
                                for i, (n, p) in enumerate(crumbs, 1)]}


CSS = open(os.path.join(ROOT, "src", "site.css"), encoding="utf-8").read()
JS = open(os.path.join(ROOT, "src", "site.js"), encoding="utf-8").read()


def counts_by_cat():
    c = {}
    for o in OFFERS:
        c[o["category"]] = c.get(o["category"], 0) + 1
    return c


def brand_pages():
    groups = {}
    for o in OFFERS:
        groups.setdefault(o["provider"], []).append(o)
    return {p: v for p, v in groups.items() if len(v) >= 2}


BRANDS = brand_pages()


def brand_path(p):
    return f"/deals/{slugify(p)}/"


def cat_nav(active):
    """active: a category name, "home" for the homepage, or None for pages outside the category list."""
    cnt = counts_by_cat()
    links = [("/", "All deals", len(OFFERS), active == "home", "all")]
    for cat, c in CATEGORIES.items():
        if cnt.get(cat):
            links.append((f"/{c['slug']}/", c["nav"], cnt[cat], active == cat, cat))
    current = ' aria-current="page"'
    return "".join(
        f'<a class="chip" data-cat="{esc(dc)}" href="{p}"{current if cur else ""}>{esc(label)} <span class="n">{n}</span></a>'
        for p, label, n, cur, dc in links)


def footer():
    brands = "".join(f'<li><a href="{brand_path(p)}">{esc(p)}</a></li>' for p in sorted(BRANDS))
    cats = "".join(f'<li><a href="/{c["slug"]}/">{esc(c["nav"])}</a></li>' for cat, c in CATEGORIES.items() if counts_by_cat().get(cat))
    year = REF_DATE.year
    return f'''<footer class="site-footer">
  <div class="wrap foot-grid">
    <div class="foot-brand">
      <a class="logo" href="/"><span class="logo-mark" aria-hidden="true">$0</span><span>{esc(NAME)}</span></a>
      <p>{esc(TAGLINE)}. Offers are gathered from manufacturer, carrier, lender and deal-tracking sites. Confirm terms with the provider before you commit.</p>
      <p class="fine">Some links may earn us a commission at no cost to you. <a href="/about/#disclosure">How we make money</a>.</p>
    </div>
    <nav aria-label="Categories"><h2 class="foot-h">Categories</h2><ul>{cats}</ul></nav>
    <nav aria-label="Brands"><h2 class="foot-h">Brands</h2><ul class="cols">{brands}</ul></nav>
    <nav aria-label="Guides"><h2 class="foot-h">Guides</h2><ul>{"".join(f'<li><a href="{guide_path(x["slug"])}">{esc(x["nav"])}</a></li>' for x in [G.HUB] + G.GUIDES)}</ul></nav>
    <nav aria-label="Site"><h2 class="foot-h">Site</h2><ul><li><a href="/about/">About</a></li><li><a href="/about/#disclosure">Affiliate disclosure</a></li><li><a href="/sitemap.xml">Sitemap</a></li></ul></nav>
  </div>
  <p class="wrap copy">© {year} {esc(NAME)}. Updated {esc(REF_HUMAN)}.</p>
</footer>'''


def card_path(path):
    key = path.strip("/").replace("/", "-") or "home"
    return f"/og/{key}.png"


def make_card(path, kind, **kw):
    """Draw the page's share image; return its URL path (or the static fallback)."""
    if SC is None:
        return "/og-image.png"
    url = card_path(path)
    try:
        out = os.path.join(OUT, url.lstrip("/"))
        if kind == "offer":
            SC.offer_card(out, updated=fmt_date(REFRESHED), **kw)
        else:
            SC.page_card(out, updated=fmt_date(REFRESHED), **kw)
        return url
    except Exception as e:
        print(f"Share image failed for {path}: {e}")
        return "/og-image.png"


ALL_COLORS = [(37, 99, 235), (14, 116, 144), (21, 128, 61), (147, 51, 234), (180, 83, 9)]


def clamp(text, limit=155):
    text = re.sub(r"\s+", " ", text or "").strip()
    if len(text) <= limit:
        return text
    cut = text[:limit]
    end = max(cut.rfind(". "), cut.rfind("; "))
    if end > limit * 0.6:
        return cut[:end + 1]
    return cut[:cut.rfind(" ")].rstrip(",;:—-") + "…"


def head(title, desc, path, jsonld, noindex=False, og_image="/og-image.png"):
    url = abs_url(path)
    # Keep titles inside Google's ~60-character display: drop the site-name suffix when it doesn't fit.
    if " | " in title and len(title) > 60:
        title = title.split(" | ")[0]
    desc = clamp(desc)
    # Link previews (iMessage, Facebook, X, Slack...) always lead with the site name.
    page = title.split(" | ")[0].strip()
    og_title = f"{NAME}: {TAGLINE}" if path == "/" else (page if page.startswith(NAME) else f"{NAME}: {page}")
    ld = "".join('<script type="application/ld+json">' + json.dumps(j, ensure_ascii=False).replace("</", "<\\/") + "</script>"
                 for j in jsonld)
    robots = '<meta name="robots" content="noindex">' if noindex else '<meta name="robots" content="index, follow, max-image-preview:large">'
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
{robots}
<link rel="canonical" href="{esc(url)}">
<meta name="theme-color" content="#fff0e6" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#0f1619" media="(prefers-color-scheme: dark)">
<meta name="color-scheme" content="light dark">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{esc(NAME)}">
<meta property="og:title" content="{esc(og_title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{esc(url)}">
<meta property="og:image" content="{esc(abs_url(og_image))}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{esc(og_title)}">
<meta property="og:locale" content="en_US">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(og_title)}">
<meta name="twitter:description" content="{esc(desc)}">
<meta name="twitter:image" content="{esc(abs_url(og_image))}">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Familjen+Grotesk:wght@600;700&family=IBM+Plex+Mono:wght@500&family=IBM+Plex+Sans:wght@400;600&display=swap">
<style>{CSS}</style>
{ld}
</head>'''


def site_header():
    return f'''<a class="skip" href="#offers">Skip to offers</a>
<header class="topbar">
  <div class="wrap topbar-in">
    <a class="logo" href="/" aria-label="{esc(NAME)} home"><span class="logo-mark" aria-hidden="true">$0</span><span>{esc(NAME)}</span></a>
    <nav class="topnav" aria-label="Main"><button type="button" class="topnav-btn" data-open-match>What can I get?</button><a href="/guides/best-nothing-down-deals/">Guides</a><a href="/?saved=1#offers" class="saved-link">Saved<span class="sbadge" data-saved-count hidden></span></a></nav>
    <span class="updated"><span class="dot" aria-hidden="true"></span><span class="long">Updated&nbsp;</span>{esc(REF_DATE.strftime("%b %-d"))}</span>
  </div>
</header>'''


def filters_rail():
    providers = sorted({o["provider"] for o in OFFERS})
    opts = "".join(f'<option value="{esc(p)}">{esc(p)}</option>' for p in providers)
    return f'''<aside class="rail" id="filters" aria-label="Filters" tabindex="-1">
  <div class="rail-head"><h2 class="rail-title">Filters</h2><button type="button" class="icon-btn" id="closeFilters" aria-label="Close filters">✕</button></div>
  <div class="rail-body">
    <div class="field m-only">
      <label class="label" for="sortM">Sort by</label>
      <select id="sortM">
        <option value="monthly">Lowest monthly</option>
        <option value="total">Lowest total cost</option>
        <option value="newest">Newest</option>
        <option value="ending">Ending soonest</option>
        <option value="az">Name A–Z</option>
      </select>
    </div>
    <fieldset class="field m-only"><legend class="label">Show</legend>
      <label class="chk"><input type="checkbox" id="savedM"> Only my saved offers</label>
      <label class="chk" id="sinceMWrap" hidden><input type="checkbox" id="sinceM"> <span id="sinceMLabel">New since my last visit</span></label>
    </fieldset>
    <div class="field">
      <label class="label" for="provider">Brand or provider</label>
      <select id="provider"><option value="">All</option>{opts}</select>
    </div>
    <fieldset class="field"><legend class="label">Cash at signing</legend>
      <label class="chk"><input type="checkbox" id="onlyZeroDas"> Only $0 due at signing</label>
    </fieldset>
    <fieldset class="field"><legend class="label">Hide offers that need</legend>
      <label class="chk"><input type="checkbox" id="noTrade"> A trade-in</label>
      <label class="chk"><input type="checkbox" id="noNewLine"> A new line or switching carriers</label>
      <label class="chk"><input type="checkbox" id="noSpecial"> Military, membership, profession or rural address</label>
    </fieldset>
    <fieldset class="field"><legend class="label">Monthly payment</legend>
      <div class="row2">
        <label class="sr" for="minMo">Minimum monthly payment</label><input id="minMo" type="number" inputmode="numeric" min="0" step="10" placeholder="Min $">
        <label class="sr" for="maxMo">Maximum monthly payment</label><input id="maxMo" type="number" inputmode="numeric" min="0" step="10" placeholder="Max $">
      </div>
    </fieldset>
    <fieldset class="field"><legend class="label">Freshness</legend>
      <label class="chk"><input type="checkbox" id="onlyNew"> Added today</label>
      <label class="chk"><input type="checkbox" id="hasExpiry"> Has a published end date</label>
    </fieldset>
  </div>
  <div class="rail-foot">
    <button class="btn-ghost" id="reset" type="button">Clear filters</button>
    <button class="btn-primary" id="applyFilters" type="button"><span id="applyCount">Show offers</span></button>
  </div>
</aside>'''


def faq_html():
    items = "".join(f'<details class="faq-item"><summary>{esc(q)}</summary><p>{esc(a)}</p></details>' for q, a in FAQ)
    return f'<section class="faq wrap" aria-labelledby="faq-h"><h2 id="faq-h">Zero-down questions, answered</h2>{items}</section>'


def faq_jsonld():
    return {"@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]}


def guide_link(cat):
    g = GUIDE_FOR_CAT.get(cat) if cat else None
    if not g:
        return guides_section(heading="Learn before you sign")
    return (f'<section class="wrap guide-teaser"><a class="teaser" href="{guide_path(g["slug"])}">'
            f'<span class="label">Guide</span><span class="teaser-t">{esc(fill(g["h1"]))}</span>'
            f'<span class="gcard-d">{esc(fill(g["desc"]))}</span><span class="gcard-go">Read the guide →</span></a></section>')


def listing_page(path, title, desc, eyebrow, h1, intro, offers, active_cat, crumbs, with_faq=False, extra_ld=None, h1_html=None):
    offers = sort_offers(offers)
    url = abs_url(path)
    ld = [offer_jsonld(offers, url, h1)]
    if crumbs:
        ld.append(breadcrumb_jsonld(crumbs))
    if with_faq:
        ld.append(faq_jsonld())
    ld += extra_ld or []
    crumb_html = ""
    if crumbs and len(crumbs) > 1:
        crumb_html = '<nav class="crumbs" aria-label="Breadcrumb"><ol>' + "".join(
            (f'<li><a href="{p}">{esc(n)}</a></li>' if i < len(crumbs) - 1 else f'<li aria-current="page">{esc(n)}</li>')
            for i, (n, p) in enumerate(crumbs)) + "</ol></nav>"
    n_zero = sum(1 for o in offers if o.get("zeroDueAtSigning"))
    n_new = sum(1 for o in offers if o.get("added") == REFRESHED)
    stats = (f'<ul class="stats" aria-label="Summary"><li><b>{len(offers)}</b> offers</li>'
             f'<li><b>{n_zero}</b> with $0 due at signing</li><li><b>{n_new}</b> new today</li></ul>')
    body = f'''<body>
{site_header()}
<main id="main">
  <section class="hero wrap">
    {crumb_html}
    <p class="eyebrow">{esc(eyebrow)}</p>
    <h1>{h1_html or esc(h1)}</h1>
    <p class="lede">{esc(intro)}</p>
    {stats}
    <div class="hero-cta"><button type="button" class="btn-primary" data-open-match>What can I get? <span class="cta-sub">3 quick questions</span></button><a class="btn-ghost" href="#alerts">Get deal alerts</a></div>
  </section>
  <nav class="cats wrap" aria-label="Deal categories"><div class="chips">{cat_nav(active_cat)}</div></nav>
  <div class="toolbar-wrap">
    <div class="wrap toolbar" role="search">
      <label class="sr" for="q">Search offers</label>
      <input id="q" type="search" placeholder="Search “Honda”, “VA loan”, “trade-in”" autocomplete="off" enterkeyhint="search">
      <button type="button" class="filters-btn" id="openFilters" aria-controls="filters" aria-expanded="false">Filters<span class="badge" id="filterBadge" hidden></span></button>
      <label class="sr" for="sort">Sort offers</label>
      <select id="sort" class="sort-select">
        <option value="monthly">Lowest monthly</option>
        <option value="newest">Newest</option>
        <option value="total">Lowest total cost</option>
        <option value="ending">Ending soonest</option>
        <option value="az">Name A–Z</option>
      </select>
    </div>
    <div class="wrap pills" role="group" aria-label="Quick filters">
      <button type="button" class="pill" data-pill="zero" aria-pressed="false">Nothing at signing</button>
      <button type="button" class="pill" data-pill="notrade" aria-pressed="false">No trade-in</button>
      <button type="button" class="pill" data-pill="nonewline" aria-pressed="false">No new line</button>
      <button type="button" class="pill" data-pill="u350" aria-pressed="false">Under $350/mo</button>
      <button type="button" class="pill" data-pill="new" aria-pressed="false">New today</button>
      <button type="button" class="pill" data-pill="saved" aria-pressed="false">♥ Saved</button>
      <button type="button" class="pill pill-hot" data-pill="since" aria-pressed="false" hidden></button>
    </div>
  </div>
  <div class="layout wrap">
    {filters_rail()}
    <section class="results" id="offers" aria-labelledby="offers-h">
      <div class="bar"><h2 id="offers-h" class="count"><span id="count">{len(offers)} offers</span></h2></div>
      <div class="list" id="list">
        {"".join(offer_html(o) for o in offers)}
        <div class="empty" id="empty" hidden><strong>No offers match these filters</strong><span class="empty-msg">Loosen a filter or clear them to see every offer.</span><button type="button" class="btn-ghost" id="emptyReset">Clear filters</button></div>
      </div>
      <p class="fine">Lease payments exclude tax, title and dealer fees and usually need top-tier credit. “$0 down” can still mean a first payment, taxes or fees at signing; the price column shows what is due. Offers change often, so confirm with the provider.</p>
    </section>
  </div>
  {faq_html() if with_faq else ""}
  {guides_section() if with_faq else guide_link(active_cat)}
  {alerts_form(active_cat if active_cat in CATEGORIES else None)}
</main>
{footer()}
<div class="scrim" id="scrim" hidden></div>
{chrome()}
</body>
</html>'''
    n_all = len(offers)
    if path == "/":
        img = make_card(path, "page", eyebrow=f"Today’s deals · {REF_DATE.strftime('%A')}", headline=TAGLINE,
                        sub=f"{n_all} offers today · {n_zero} with nothing due at signing", colors=ALL_COLORS)
    else:
        accent = SC.CAT_COLORS.get(active_cat) if SC and active_cat in CATEGORIES else None
        img = make_card(path, "page", eyebrow=eyebrow.split(" · ")[0], headline=h1,
                        sub=f"{n_all} live {'offer' if n_all == 1 else 'offers'} · {n_zero} with nothing due at signing",
                        colors=[accent] if accent else ALL_COLORS, accent=accent)
    return head(title, desc, path, ld, og_image=img) + "\n" + body


# ---------------------------------------------------------------- guides
import guides as G

GUIDE_BY_SLUG = {g["slug"]: g for g in G.GUIDES}
GUIDE_FOR_CAT = {g["category"]: g for g in G.GUIDES}


def guide_path(slug):
    return f"/guides/{slug}/"


class _Safe(dict):
    def __missing__(self, k):
        return "{" + k + "}"


def guide_context():
    cnt = counts_by_cat()
    leases0 = sorted([o for o in OFFERS if o["category"] == "Car lease" and o.get("zeroDueAtSigning")
                      and isinstance(o.get("monthly"), (int, float)) and o["monthly"] > 0], key=lambda o: o["monthly"])
    lowest = f"{leases0[0]['title']} at ${leases0[0]['monthly']:,.0f}/mo" if leases0 else "latest lease offers"
    return _Safe(month=MONTH, today=REF_DAY, short=fmt_date(REFRESHED), n_all=len(OFFERS), n_lease=cnt.get("Car lease", 0),
                 n_lease_zero=len(leases0), n_finance=cnt.get("Car financing", 0), n_home=cnt.get("Home loan", 0),
                 n_phone=cnt.get("Phone", 0), n_solar=cnt.get("Home improvement", 0), lowest_lease=lowest)


CTX = None


def fill(text):
    return text.format_map(CTX)


def inline(text):
    """Escape, then allow **bold** and [text](/internal-path) links."""
    s = esc(fill(text))
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"\[([^\]]+)\]\((/[^)\s]*)\)", r'<a href="\2">\1</a>', s)
    return s


def mini_offer(o):
    zero = bool(o.get("zeroDueAtSigning"))
    return (f'<li class="mini" data-cat="{esc(o["category"])}"><a href="/{CATEGORIES[o["category"]]["slug"]}/#{esc(o["id"])}">'
            f'<span class="mini-title">{esc(o["title"])}</span>'
            f'<span class="mini-price">{esc(price_text(o))}</span>'
            f'<span class="mini-das{" zero" if zero else ""}">{esc(o.get("dueAtSigning") or "$0 down")}</span></a></li>')


def offers_block(cat, limit, zero_only):
    offers = [o for o in OFFERS if o["category"] == cat and (o.get("zeroDueAtSigning") or not zero_only)]
    offers = sort_offers(offers)[:limit]
    if not offers:
        return ""
    c = CATEGORIES[cat]
    total = counts_by_cat().get(cat, 0)
    label = "with nothing due at signing" if zero_only else "available now"
    return (f'<section class="live" aria-label="Today’s offers"><div class="live-head"><p class="live-kicker">'
            f'<span class="dot" aria-hidden="true"></span>Live {esc(fmt_date(REFRESHED))}</p>'
            f'<h2 class="live-h">Today’s best {esc(c["nav"].lower())} {label}</h2></div>'
            f'<ul class="mini-list">{"".join(mini_offer(o) for o in offers)}</ul>'
            f'<a class="btn-primary live-cta" href="/{c["slug"]}/">See all {total} {esc(c["nav"].lower())} with filters</a></section>')


def render_blocks(blocks):
    out, toc = [], []
    for b in blocks:
        t = b[0]
        if t == "p":
            out.append(f"<p>{inline(b[1])}</p>")
        elif t == "h2":
            out.append(f'<h2 id="{esc(b[1])}">{inline(b[2])}</h2>')
            toc.append((b[1], fill(b[2])))
        elif t == "h3":
            out.append(f"<h3>{inline(b[1])}</h3>")
        elif t in ("ul", "ol"):
            out.append(f"<{t}>" + "".join(f"<li>{inline(x)}</li>" for x in b[1]) + f"</{t}>")
        elif t == "table":
            _, cap, heads, rows = b
            th = "".join(f'<th scope="col">{inline(h)}</th>' for h in heads)
            trs = "".join("<tr>" + "".join((f'<th scope="row">{inline(c)}</th>' if i == 0 else f"<td>{inline(c)}</td>")
                                           for i, c in enumerate(r)) + "</tr>" for r in rows)
            out.append(f'<div class="table-scroll" tabindex="0" role="region" aria-label="{esc(fill(cap))}"><table>'
                       f"<caption>{inline(cap)}</caption><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table></div>")
        elif t == "callout":
            out.append(f'<aside class="callout"><p class="callout-t">{inline(b[1])}</p><p>{inline(b[2])}</p></aside>')
        elif t == "offers":
            out.append(offers_block(b[1], b[2], b[3]))
        elif t == "steps":
            out.append('<ol class="steps">' + "".join(f"<li><strong>{inline(a)}</strong><span>{inline(c)}</span></li>"
                                                      for a, c in b[1]) + "</ol>")
        elif t == "ranked":
            out.append(ranked_html())
    return "\n".join(out), toc


def ranked_html():
    cnt = counts_by_cat()
    items = []
    for i, r in enumerate(G.RANKED, 1):
        g = GUIDE_BY_SLUG.get(r["guide"])
        live = cnt.get(r["category"], 0)
        cslug = CATEGORIES[r["category"]]["slug"]
        items.append(f'''<li class="rank" id="rank-{i}" data-cat="{esc(r["category"])}">
  <div class="rank-head"><span class="rank-n">{i}</span><h3>{esc(r["name"])}</h3></div>
  <dl class="rank-dl"><dt>Best for</dt><dd>{esc(r["best_for"])}</dd><dt>Why it’s good</dt><dd>{esc(r["why"])}</dd><dt>Watch out for</dt><dd>{esc(r["watch"])}</dd></dl>
  <p class="rank-links">{f'<a href="{guide_path(g["slug"])}">Read the guide</a>' if g else ""}<a href="/{cslug}/">See {live} live {"offer" if live == 1 else "offers"}</a></p>
</li>''')
    return '<ol class="ranked">' + "".join(items) + "</ol>"


def guide_card(g):
    return (f'<li class="gcard"><a href="{guide_path(g["slug"])}"><span class="gcard-t">{esc(fill(g["h1"]))}</span>'
            f'<span class="gcard-d">{esc(fill(g["desc"]))}</span><span class="gcard-go">Read the guide →</span></a></li>')


def guides_section(exclude=None, heading="Guides to zero-down deals"):
    cards = [guide_card(g) for g in [HUB_G] + G.GUIDES if g["slug"] != exclude]
    return f'<section class="guides wrap" aria-labelledby="guides-h"><h2 id="guides-h">{esc(heading)}</h2><ul class="gcards">{"".join(cards)}</ul></section>'


HUB_G = dict(G.HUB, h1=G.HUB["h1"])


def article_page(g, blocks, faq, related, is_hub=False):
    path = guide_path(g["slug"])
    title = fill(g["title"])
    desc = fill(g["desc"])
    h1 = fill(g["h1"])
    content, toc = render_blocks(blocks)
    crumbs = [("Home", "/"), ("Guides", guide_path(G.HUB["slug"])), (h1, path)] if not is_hub else [("Home", "/"), ("Guides", path)]
    article_ld = {"@context": "https://schema.org", "@type": "Article", "headline": h1[:110], "description": desc,
                  "datePublished": "2026-10-17", "dateModified": REFRESHED, "mainEntityOfPage": abs_url(path),
                  "image": abs_url("/og-image.png"),
                  "author": {"@type": "Organization", "name": NAME, "url": BASE_URL + "/"},
                  "publisher": {"@type": "Organization", "name": NAME, "logo": {"@type": "ImageObject", "url": abs_url("/apple-touch-icon.png")}}}
    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage",
              "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": fill(a)}} for q, a in faq]}
    toc_html = ""
    if len(toc) >= 3:
        toc_html = '<nav class="toc" aria-label="On this page"><p class="label">On this page</p><ol>' + "".join(
            f'<li><a href="#{esc(a)}">{esc(t)}</a></li>' for a, t in toc) + ('<li><a href="#faq-h">Questions</a></li>' if faq else "") + "</ol></nav>"
    crumb_html = '<nav class="crumbs" aria-label="Breadcrumb"><ol>' + "".join(
        (f'<li><a href="{p}">{esc(n)}</a></li>' if i < len(crumbs) - 1 else f'<li aria-current="page">{esc(n if len(n) < 40 else n[:38] + "…")}</li>')
        for i, (n, p) in enumerate(crumbs)) + "</ol></nav>"
    faq_html_ = ""
    if faq:
        faq_html_ = '<section class="faq" aria-labelledby="faq-h"><h2 id="faq-h">Questions people ask</h2>' + "".join(
            f'<details class="faq-item"><summary>{esc(q)}</summary><p>{esc(fill(a))}</p></details>' for q, a in faq) + "</section>"
    cat = g.get("category")
    cta = ""
    if cat and counts_by_cat().get(cat):
        c = CATEGORIES[cat]
        cta = (f'<aside class="endcta"><p class="endcta-t">See every {esc(c["nav"].lower())} offer, checked this morning</p>'
               f'<p>Filter by brand, payment and what you’re willing to do, like skipping trade-ins or new lines.</p>'
               f'<a class="btn-primary" href="/{c["slug"]}/">Browse {counts_by_cat()[cat]} {esc(c["nav"].lower())} offers</a></aside>')
    else:
        cta = (f'<aside class="endcta"><p class="endcta-t">See all {len(OFFERS)} zero-down offers, checked this morning</p>'
               f'<p>Search and filter car leases, home loans, phones and solar in one place.</p>'
               f'<a class="btn-primary" href="/">Browse today’s deals</a></aside>')
    rel = [GUIDE_BY_SLUG.get(s) or (HUB_G if s == G.HUB["slug"] else None) for s in related]
    rel_html = ""
    if any(rel):
        rel_html = '<section class="related" aria-labelledby="rel-h"><h2 id="rel-h">Keep reading</h2><ul class="gcards">' + "".join(
            guide_card(r) for r in rel if r) + "</ul></section>"
    body = f'''<body>
{site_header()}
<main id="main">
  <article class="article wrap">
    <header class="a-head">
      {crumb_html}
      <p class="eyebrow">{esc(fill(g["eyebrow"]))}</p>
      <h1>{esc(h1)}</h1>
      <p class="lede">{inline(g["intro"])}</p>
    </header>
    <div class="a-grid">
      <div class="a-body">
        {content}
        {faq_html_}
        {cta}
      </div>
      {f'<aside class="a-side">{toc_html}</aside>' if toc_html else ""}
    </div>
  </article>
  <div class="wrap">{rel_html}</div>
  {alerts_form(g.get("category"))}
</main>
{footer()}
{chrome()}
</body>
</html>'''
    accent = SC.CAT_COLORS.get(cat) if SC and cat else None
    img = make_card(path, "page", eyebrow="Guide", headline=h1, sub=f"Updated {fmt_date(REFRESHED)} with today’s live offers",
                    colors=[accent] if accent else ALL_COLORS, accent=accent)
    return head(title + f" | {NAME}", desc, path, [article_ld, faq_ld, breadcrumb_jsonld(crumbs)], og_image=img) + "\n" + body


# ---------------------------------------------------------------- shared page chrome
ICON_DEALS = '<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><path d="M4 6h16M4 12h16M4 18h10" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>'
ICON_MATCH = '<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><path d="M12 3l2.6 5.6 6.1.7-4.5 4.2 1.2 6L12 16.6 6.6 19.5l1.2-6L3.3 9.3l6.1-.7z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/></svg>'
ICON_GUIDE = '<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H20v15H6.5A2.5 2.5 0 0 0 4 20.5zM4 20.5A2.5 2.5 0 0 0 6.5 23H20v-5" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/></svg>'


def quiz_html():
    return '''<div class="sheet" id="match" role="dialog" aria-modal="true" aria-labelledby="match-h" hidden>
  <div class="sheet-in" tabindex="-1">
    <div class="sheet-head">
      <h2 id="match-h">What can I get?</h2>
      <button type="button" class="icon-btn" data-close-match aria-label="Close">✕</button>
    </div>
    <div class="quiz-progress" aria-hidden="true"><span id="qbar"></span></div>
    <div class="quiz" id="quiz" aria-live="polite"></div>
  </div>
</div>'''


def bottom_bar():
    return f'''<nav class="bottombar" aria-label="Quick links">
  <a href="/" data-tab="deals">{ICON_DEALS}<span>Deals</span></a>
  <button type="button" data-open-match data-tab="match">{ICON_MATCH}<span>Match me</span></button>
  <a href="/?saved=1#offers" data-tab="saved">{ICON_HEART}<span>Saved</span><span class="sbadge" data-saved-count hidden></span></a>
  <a href="{guide_path(G.HUB["slug"])}" data-tab="guides">{ICON_GUIDE}<span>Guides</span></a>
</nav>'''


def chrome():
    return f'''{quiz_html()}
{bottom_bar()}
<div class="toast" id="toast" role="status" aria-live="polite" hidden></div>
<script>{JS}</script>'''


def alerts_form(cat=None):
    labels = [(c, CATEGORIES[c]["nav"]) for c in CATEGORIES if counts_by_cat().get(c) or c in ("Car financing", "Home improvement")]
    boxes = "".join(
        f'<label class="chk"><input type="checkbox" name="interests" value="{esc(lbl)}"{" checked" if c == cat else ""}> {esc(lbl)}</label>'
        for c, lbl in labels)
    return f'''<section class="alerts wrap" id="alerts" aria-labelledby="alerts-h">
  <div class="alerts-in">
    <div class="alerts-copy">
      <p class="eyebrow">Deal alerts</p>
      <h2 id="alerts-h">Get new $0-down deals before they’re gone</h2>
      <p>Tell us what you’re shopping for and we’ll email you when a matching zero-down offer appears. Only deal alerts, nothing else.</p>
    </div>
    <form class="alerts-form" name="deal-alerts" method="POST" action="/thanks/" data-netlify="true" netlify-honeypot="bot-field">
      <input type="hidden" name="form-name" value="deal-alerts">
      <p class="hp"><label>Leave this empty <input name="bot-field" tabindex="-1" autocomplete="off"></label></p>
      <label class="label" for="alert-email">Email</label>
      <input id="alert-email" type="email" name="email" required autocomplete="email" inputmode="email" placeholder="you@example.com">
      <fieldset class="field"><legend class="label">I’m shopping for</legend><div class="alert-boxes">{boxes}</div></fieldset>
      <label class="label" for="alert-brand">Brands or models (optional)</label>
      <input id="alert-brand" type="text" name="brands" placeholder="e.g. Honda CR-V, iPhone, VA loan" autocomplete="off">
      <fieldset class="field"><legend class="label">How often</legend><div class="radios">
        <label class="chk"><input type="radio" name="frequency" value="Daily" checked> As they appear</label>
        <label class="chk"><input type="radio" name="frequency" value="Weekly"> Weekly roundup</label></div></fieldset>
      <button type="submit" class="btn-primary">Get deal alerts</button>
    </form>
  </div>
</section>'''


CATEGORY_NOTES = {
    "Car lease": [
        "Payments shown exclude tax, title, registration and dealer fees.",
        "Advertised lease terms usually need top-tier credit, often around 700 or higher.",
        "Check the yearly mileage allowance and the per-mile charge for going over.",
        "Ask for the selling price, money factor, residual and total due at signing in writing.",
    ],
    "Car financing": [
        "Financing the full price means you may owe more than the car is worth for a while; gap coverage helps.",
        "A shorter loan term builds equity faster.",
        "Get preapproved before you visit the dealer.",
        "Compare the APR and total interest, not just the monthly payment; a longer term lowers the payment but costs more.",
    ],
    "Home loan": [
        "Zero down still leaves closing costs, often 2% to 5% of the price; a seller credit can cover some of them.",
        "Compare the APR and any funding or origination fee, not just the rate.",
        "Keep savings for repairs, since you start with little equity.",
    ],
    "Phone": [
        "Bill credits usually run 36 months; leaving early ends the credits and the remaining balance comes due.",
        "Compare the required plan’s price with the plan you would choose anyway.",
        "Sales tax on the full price and an activation fee may be due at purchase.",
    ],
    "Home improvement": [
        "Leases and power purchase agreements often rise 1% to 3% a year; ask for the total over the contract.",
        "On a lease or PPA, the company keeps the incentives; on a loan, you do.",
        "Ask how a transfer works if you sell your home.",
    ],
}


def similar_offers(o, n=5):
    same = [x for x in OFFERS if x["category"] == o["category"] and x["id"] != o["id"]]
    m = o.get("monthly")
    if isinstance(m, (int, float)) and m > 0:
        same.sort(key=lambda x: abs((x.get("monthly") or 10 ** 6) - m))
    else:
        same.sort(key=lambda x: (x["provider"] != o["provider"], x["title"]))
    return same[:n]


def offer_page(o):
    path = offer_path(o)
    cat = CATEGORIES[o["category"]]
    price = price_text(o)
    das = o.get("dueAtSigning") or "$0 down"
    total = total_cost(o)
    kind = {"Car lease": " $0 Down Lease", "Phone": " Deal"}.get(o["category"], "")
    if o["category"] == "Car lease" and isinstance(o.get("monthly"), (int, float)) and o["monthly"] > 0:
        tail = "$0 Due at Signing" if o.get("zeroDueAtSigning") else "$0 Down"
        title = f"{o['title']} Lease: {price}, {tail}"
        if len(title) > 60:
            title = f"{re.sub(r'^20[0-9][0-9] ', '', o['title'])} Lease: {price}, {tail}"
    elif o["category"] == "Phone":
        title = f"{o['title']}: {price}"
    else:
        title = f"{o['title']}: {das}"
        if len(title) > 60 and "," in das:
            title = f"{o['title']}: {das.split(',')[0]}"
    desc = f"{o['title']}: {price}, {das}. {o.get('summary') or ''}"
    crumbs = [("Home", "/"), (cat["nav"], f"/{cat['slug']}/"), (o["title"], path)]
    offer_ld = {"@context": "https://schema.org", "@type": "Offer", "name": o["title"], "description": o.get("summary"),
                "url": abs_url(path), "category": o["category"], "seller": {"@type": "Organization", "name": o["provider"]}}
    m = o.get("monthly")
    if isinstance(m, (int, float)) and m > 0:
        offer_ld["priceSpecification"] = {"@type": "UnitPriceSpecification", "price": m, "priceCurrency": "USD", "unitText": "MONTH"}
    if o.get("expires"):
        offer_ld["validThrough"] = o["expires"]
    facts = []
    if total:
        facts.append(("Total of payments", f"≈ ${total:,} over {months_in(o.get('term'))} months"))
    if o.get("term"):
        facts.append(("Term", o["term"]))
    facts.append(("Available in", o.get("region") or "National"))
    if o.get("expires"):
        facts.append(("Ends", fmt_date(o["expires"])))
    facts.append(("Last checked", fmt_date(o.get("verified"))))
    facts_html = "".join(f"<div><dt>{esc(k)}</dt><dd>{esc(v)}</dd></div>" for k, v in facts)
    reqs = o.get("requirements") or []
    reqs_html = ("<h2>What you need</h2><ul class=\"req-list\">" + "".join(f"<li>{esc(r)}</li>" for r in reqs) + "</ul>") if reqs else ""
    notes = "".join(f"<li>{esc(n)}</li>" for n in CATEGORY_NOTES.get(o["category"], []))
    src_btn = ""
    if str(o.get("sourceUrl", "")).startswith("https://"):
        src_btn = (f'<a class="btn-primary" href="{esc(o["sourceUrl"])}" target="_blank" rel="nofollow noopener noreferrer">'
                   f'See the offer at {esc(o.get("source") or "the source")}<span aria-hidden="true"> ↗</span></a>')
    sim = similar_offers(o)
    sim_html = ""
    if sim:
        sim_html = (f'<section class="live" aria-labelledby="sim-h"><h2 class="live-h" id="sim-h">More {esc(cat["nav"].lower())} like this</h2>'
                    f'<ul class="mini-list">{"".join(mini_offer(x) for x in sim)}</ul>'
                    f'<a class="btn-ghost live-cta" href="/{cat["slug"]}/">See all {counts_by_cat()[o["category"]]} {esc(cat["nav"].lower())}</a></section>')
    tags = []
    if o.get("added") == REFRESHED:
        tags.append('<span class="tag new">New today</span>')
    if o.get("zeroDueAtSigning"):
        tags.append('<span class="tag exp">Nothing due at signing</span>')
    crumb_html = '<nav class="crumbs" aria-label="Breadcrumb"><ol>' + "".join(
        (f'<li><a href="{p}">{esc(n)}</a></li>' if i < len(crumbs) - 1 else f'<li aria-current="page">{esc(n)}</li>')
        for i, (n, p) in enumerate(crumbs)) + "</ol></nav>"
    body = f'''<body>
{site_header()}
<main id="main">
  <article class="offer-page wrap" data-cat="{esc(o["category"])}">
    {crumb_html}
    <p class="eyebrow">{esc(o["category"])} · {esc(o["provider"])}</p>
    <h1>{esc(o["title"])}</h1>
    <p class="op-price"><span class="op-mo">{esc(price)}</span><span class="op-das{" zero" if o.get("zeroDueAtSigning") else ""}">{esc(das)}</span></p>
    {f'<div class="tags">{"".join(tags)}</div>' if tags else ""}
    <p class="lede">{esc(o.get("summary"))}</p>
    <div class="op-actions">{src_btn}{actions_html(o)}</div>
    <dl class="facts">{facts_html}</dl>
    <div class="op-body">
      {reqs_html}
      <h2>Before you sign</h2>
      <ul>{notes}</ul>
      <p class="fine">Offers change often and vary by credit and region. Confirm the final terms with {esc(o["provider"])}.</p>
    </div>
    {sim_html}
  </article>
  {guide_link(o["category"])}
  {alerts_form(o["category"])}
</main>
{footer()}
{chrome()}
</body>
</html>'''
    reqs0 = (o.get("requirements") or [None])[0]
    tl = f"≈ ${total:,} total over {months_in(o.get('term'))} months" if total else ""
    money = True
    if isinstance(m, (int, float)) and m > 0:
        big, unit, due_text = f"${m:,.0f}", "/mo", das
    elif o["category"] == "Phone":
        label = o.get("priceLabel") or price
        if label.startswith("$0/mo"):
            big, unit = "$0", "/mo"
        elif label.lower().startswith("free"):
            big, unit = "Free", ""
        else:
            big, unit = label, ""
        due_text = "$0 down"
        tl = "Paid off through 36 monthly bill credits" if "credit" in (label + " " + (o.get("term") or "")).lower() else (reqs0 or "")
    else:
        big, unit = das, ""
        due_text, money = (reqs0 or o.get("priceLabel") or "See terms"), False
    img = make_card(path, "offer", o=o, price_big=big, price_unit=unit, due=due_text, total_line=tl, due_is_money=money)
    return head(f"{title} | {NAME}", desc, path, [offer_ld, breadcrumb_jsonld(crumbs)], og_image=img) + "\n" + body


def thanks_page():
    body = f'''<body>
{site_header()}
<main id="main" class="wrap prose center">
  <p class="eyebrow">You’re on the list</p>
  <h1>Thanks, deal alerts are on the way</h1>
  <p class="lede">We’ll email you when a new zero-down offer matches what you’re shopping for.</p>
  <p><a class="btn-primary" href="/">Back to today’s deals</a></p>
</main>
{footer()}
{chrome()}
</body>
</html>'''
    return head(f"Thanks | {NAME}", "You’re signed up for deal alerts.", "/thanks/", [], noindex=True) + "\n" + body


def write(path, content):
    full = os.path.join(OUT, path.lstrip("/"))
    if full.endswith("/"):
        full = os.path.join(full, "index.html")
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)


def about_page():
    path = "/about/"
    title = f"About {NAME}: How We Find $0-Down Deals"
    desc = f"How {NAME} finds and checks zero-down offers every morning, and how the site makes money."
    body = f'''<body>
{site_header()}
<main id="main" class="wrap prose">
  <nav class="crumbs" aria-label="Breadcrumb"><ol><li><a href="/">Home</a></li><li aria-current="page">About</li></ol></nav>
  <h1>About {esc(NAME)}</h1>
  <p class="lede">{esc(TAGLINE)}. One list of every current offer that asks for no down payment, with the fine print spelled out.</p>
  <h2>How offers are found</h2>
  <p>Every morning we check manufacturer, carrier and lender sites plus trusted deal trackers for offers that explicitly say $0 down, no money down or $0 due at signing. New offers are added, changed terms are updated, and anything that has ended or can no longer be confirmed is removed.</p>
  <h2>What “$0 down” means here</h2>
  <p>We list an offer when no down payment is required. Some still ask for a first payment, taxes or fees at signing, so every listing shows exactly what is due up front. Use the “Only $0 due at signing” filter to see offers where nothing at all is due.</p>
  <h2 id="disclosure">How we make money</h2>
  <p>Some links on this site may be affiliate links. If you sign up or buy through one, we may earn a commission at no extra cost to you. Commissions never decide which offers appear or how they rank; listings are sorted by payment, date or name.</p>
  <h2>What you’ll find here</h2>
  <p>Every listing is a current offer that asks for no down payment, sorted into five kinds of deals: <a href="/car-leases/">car leases</a> with nothing or almost nothing due at signing, <a href="/car-financing/">car loans</a> with 100% financing, <a href="/home-loans/">home loans</a> with 0% down such as VA and USDA loans, <a href="/phones/">phone deals</a> paid off through bill credits, and <a href="/home-improvement/">solar and home upgrades</a> with nothing paid at installation. Each offer has its own page with the price, what is due up front, who qualifies and a link to the source.</p>
  <p>New to zero-down deals? Start with <a href="/guides/best-nothing-down-deals/">the best nothing-down deals, ranked</a>, or answer three quick questions with “What can I get?” to see only the offers that fit you.</p>
  <h2>Before you sign</h2>
  <p>Offers vary by credit, region and dealer, and they change often. Always confirm the final terms with the provider. Nothing here is financial advice.</p>
  <p><a class="btn-primary" href="/">See today’s offers</a></p>
</main>
{footer()}
{chrome()}
</body>
</html>'''
    return head(title, desc, path, [breadcrumb_jsonld([("Home", "/"), ("About", path)])]) + "\n" + body


def not_found_page():
    body = f'''<body>
{site_header()}
<main id="main" class="wrap prose center">
  <p class="eyebrow">404</p>
  <h1>That page has moved or the deal has ended</h1>
  <p class="lede">Offers come and go every day. Today’s list has {len(OFFERS)} current zero-down deals.</p>
  <p><a class="btn-primary" href="/">See today’s offers</a></p>
  <nav class="cats" aria-label="Deal categories"><div class="chips wrapchips">{cat_nav(None)}</div></nav>
</main>
{footer()}
{chrome()}
</body>
</html>'''
    return head(f"Page not found | {NAME}", "This page isn’t available.", "/404.html", [], noindex=True) + "\n" + body


def main():
    global CTX
    CTX = guide_context()
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    static = os.path.join(ROOT, "static")
    for f in os.listdir(static):
        shutil.copy(os.path.join(static, f), os.path.join(OUT, f))

    pages = []
    website_ld = {"@context": "https://schema.org", "@type": "WebSite", "name": NAME, "url": BASE_URL + "/",
                  "description": SITE["description"],
                  "potentialAction": {"@type": "SearchAction",
                                      "target": {"@type": "EntryPoint", "urlTemplate": BASE_URL + "/?q={search_term_string}"},
                                      "query-input": "required name=search_term_string"}}
    org_ld = {"@context": "https://schema.org", "@type": "Organization", "name": NAME, "url": BASE_URL + "/",
              "logo": abs_url("/apple-touch-icon.png")}
    write("/", listing_page(
        "/", f"$0 Down Deals Updated Daily | {NAME}", SITE["description"],
        TAGLINE, f"Nothing-Down Deals for {REF_DAY}",
        "Car leases with nothing due at signing, 0% down home loans, free phones and $0-down solar, all in one list. We check every offer each morning and spell out the fine print.",
        OFFERS, "home", None, with_faq=True, extra_ld=[website_ld, org_ld],
        h1_html=f'Nothing-Down Deals for <time class="date" datetime="{REFRESHED}">{esc(REF_DAY)}</time>'))
    pages.append("/")

    cnt = counts_by_cat()
    for cat, c in CATEGORIES.items():
        if not cnt.get(cat):
            continue
        path = f"/{c['slug']}/"
        offers = [o for o in OFFERS if o["category"] == cat]
        write(path, listing_page(path, f"{c['title']} | {NAME}", c["desc"], f"{c['nav']} · Updated {fmt_date(REFRESHED)}",
                                 c["h1"], c["intro"], offers, cat, [("Home", "/"), (c["nav"], path)]))
        pages.append(path)

    for prov, offers in sorted(BRANDS.items()):
        path = brand_path(prov)
        cats = sorted({o["category"] for o in offers})
        kinds = " and ".join(CATEGORIES[c]["nav"].lower() for c in cats if c in CATEGORIES)
        h1 = f"{prov} $0 down deals for {MONTH}"
        desc = f"Every current {prov} offer with no down payment for {MONTH}: {len(offers)} {kinds} deals with payments, requirements and fine print. Updated daily."
        noun = "offer" if len(offers) == 1 else "offers"
        intro = f"{len(offers)} current {prov} {noun} that need no down payment, covering {kinds}. Checked every morning."
        write(path, listing_page(path, f"{prov} $0 Down Deals, {MONTH} | {NAME}", desc, f"{prov} · Updated {fmt_date(REFRESHED)}",
                                 h1, intro, offers, None, [("Home", "/"), (prov, path)]))
        pages.append(path)

    # Guides: hub + one page per deal type.
    write(guide_path(G.HUB["slug"]), article_page(G.HUB, G.HUB_BLOCKS, G.HUB_FAQ, [g["slug"] for g in G.GUIDES[:3]], is_hub=True))
    pages.append(guide_path(G.HUB["slug"]))
    for g in G.GUIDES:
        if g.get("category") and not counts_by_cat().get(g["category"]):
            continue  # skip a guide whose category has no live offers today
        write(guide_path(g["slug"]), article_page(g, g["blocks"], g["faq"], g.get("related", [])))
        pages.append(guide_path(g["slug"]))

    write("/about/", about_page())
    pages.append("/about/")
    write("/thanks/", thanks_page())
    for o in OFFERS:
        write(offer_path(o), offer_page(o))
        pages.append(offer_path(o))
    write("/404.html", not_found_page())

    # Machine-readable copies of the data.
    write("/offers.json", json.dumps({"meta": {"lastRefreshed": REFRESHED}, "offers": OFFERS}, ensure_ascii=False, indent=1))

    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for p in pages:
        pri = "0.5" if p.startswith("/offer/") else "1.0" if p == "/" else ("0.8" if (p.count("/") == 2 and not p.startswith("/deals") and p != "/about/") or p.startswith("/guides/") else "0.6")
        sm.append(f"<url><loc>{esc(abs_url(p))}</loc><lastmod>{REFRESHED}</lastmod><changefreq>daily</changefreq><priority>{pri}</priority></url>")
    sm.append("</urlset>")
    write("/sitemap.xml", "\n".join(sm) + "\n")
    write("/robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {abs_url('/sitemap.xml')}\n")
    print(f"Built {len(pages)} pages with {len(OFFERS)} offers (refreshed {REFRESHED}) into public/")
    if "YOURDOMAIN" in BASE_URL:
        print("Note: set your real domain in site.json so canonical links and the sitemap point to it.")


if __name__ == "__main__":
    main()
