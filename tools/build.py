"""Builds the Farlight static site from tools/stories.json.

Usage:  python tools/build.py
Writes index.html, one page per category, news/<slug>.html and credits.html.
Image sizes come from tools/image_meta.json (refresh with tools/fetch_image_meta.py).
"""
import hashlib
import html
import json
import os
import sys
import urllib.parse
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORIES = json.load(open(os.path.join(ROOT, "tools", "stories.json"), encoding="utf-8"))
META_PATH = os.path.join(ROOT, "tools", "image_meta.json")
IMG_META = json.load(open(META_PATH, encoding="utf-8")) if os.path.exists(META_PATH) else {}

CATS = [
    ("index", "Home"), ("space", "Space"), ("health", "Health"), ("earth", "Earth & Climate"),
    ("life", "Life"), ("physics", "Physics"), ("tech", "Tech"), ("mind", "Mind"),
]
CATNAME = dict(CATS)
SITE = "Farlight"
# GoatCounter site code (the "xyz" in https://xyz.goatcounter.com). Empty = no tracking script.
GOATCOUNTER = "sciencemessenger"
YEAR = date.today().year

# Wikimedia only serves thumbnails at these standard widths; anything else is rejected.
THUMB_WIDTHS = [330, 500, 960, 1280, 1920, 2560]
HERO_W = 2560    # largest copy made, for full-width photos on big / high-DPI screens
HERO_CAP = 1920  # widest a full-width photo is ever drawn (CSS px); plain dark band fills the sides

e = html.escape


def by_date(items):
    return sorted(items, key=lambda s: s["date"], reverse=True)


def fmt_date(iso):
    d = date.fromisoformat(iso)
    return d.strftime("%B %d, %Y").replace(" 0", " ")


def short_place(loc):
    """'Lehi, Utah to Jurupa Valley, California, USA' -> 'Lehi → Jurupa Valley'."""
    sides = loc.split(" to ")
    if len(sides) > 1:
        return " → ".join(side.split(",")[0].strip() for side in sides)
    parts = [p.strip() for p in loc.split(",")]
    return parts[0] if len(parts) == 1 else f"{parts[0]}, {parts[-1]}"


# ---------- Images ----------

def _commons_name(img):
    return img["file"].split(":", 1)[1].replace(" ", "_")


def _thumb(img, width):
    """Direct upload.wikimedia.org URL (no Special:FilePath redirect hops)."""
    name = _commons_name(img)
    h = hashlib.md5(name.encode("utf-8")).hexdigest()
    q = urllib.parse.quote(name)
    orig_w = IMG_META[img["file"]][0]
    if width >= orig_w:
        return f"https://upload.wikimedia.org/wikipedia/commons/{h[0]}/{h[:2]}/{q}"
    return f"https://upload.wikimedia.org/wikipedia/commons/thumb/{h[0]}/{h[:2]}/{q}/{width}px-{q}"


# RULE: every image is self-hosted under img/ (tools/fetch_images.py downloads them).
# Never hotlink upload.wikimedia.org: Facebook's crawler gets 403 there, so link previews lose
# their picture, and hotlinks can be rate-limited or disappear. The build fails on a missing file.

def img_key(img):
    """Stable local filename stem for a Commons file (plus its crop, if any)."""
    k = img["file"] + (repr([round(f, 4) for f in img["crop"]]) if img.get("crop") else "")
    return hashlib.md5(k.encode("utf-8")).hexdigest()[:12]


def img_size(img):
    """Pixel size of the self-hosted image: the original minus the optional "crop"
    [left, top, right, bottom] fractions (used to cut labels and text out of infographics)."""
    ow, oh = IMG_META[img["file"]]
    if img.get("crop"):
        l, t, r, b = img["crop"]
        ow, oh = round(r * ow) - round(l * ow), round(b * oh) - round(t * oh)
    return ow, oh


def local_widths(img, max_w=HERO_W):
    ow = img_size(img)[0]
    widths = [w for w in THUMB_WIDTHS if w < ow and w <= max_w] or [ow]
    if max_w >= ow and ow not in widths:
        widths.append(ow)
    return widths


def local_src(img, width):
    """Path (relative to the site root) of the self-hosted copy at this width."""
    return f"img/{img_key(img)}-{width}.jpg"


def require_local(path):
    if not os.path.exists(os.path.join(ROOT, path)):
        sys.exit(f"Missing self-hosted image {path}: run tools/fetch_image_meta.py, then tools/fetch_images.py")
    return path


# RULE: only public-domain or CC0 images (nothing that needs attribution, nothing copyrighted).
ALLOWED_LICENSES = {"Public domain", "CC0", "CC0 1.0"}


def check_license(img):
    if img["license"] not in ALLOWED_LICENSES:
        sys.exit(f"{img['file']} is {img['license']}: only public domain or CC0 images are allowed")


def img_tag(img, sizes, max_w=1280, eager=False, prefix="", cap=0):
    """<img> with srcset, intrinsic width/height (stops layout shift) and lazy loading."""
    check_license(img)
    alt = e(img["alt"])
    load = ' fetchpriority="high"' if eager else ' loading="lazy" decoding="async"'
    if img["file"] not in IMG_META:
        sys.exit(f"No size data for {img['file']}: run tools/fetch_image_meta.py, then tools/fetch_images.py")
    ow, oh = img_size(img)
    widths = local_widths(img, max_w)
    srcset = ", ".join(f"{prefix}{require_local(local_src(img, w))} {w}w" for w in widths)
    w = widths[-1]
    hgt = round(oh * w / ow)
    styles = [f"object-position:{e(img['focus'])}"] if img.get("focus") else []
    if cap and ow < cap:  # never stretch a small photo past its own width (that is what looks blurry)
        styles.append(f"max-width:{ow}px")
    style = f' style="{";".join(styles)}"' if styles else ""
    return (f'<img src="{prefix}{local_src(img, w)}" srcset="{srcset}" sizes="{sizes}" '
            f'width="{w}" height="{hgt}" alt="{alt}"{style}{load}>')


def wide_img(img, eager=False, prefix=""):
    """Full-width photo band: the photo is drawn at most HERO_CAP px wide (or its own width),
    in a fixed shape set by CSS, centred on a plain dark band (no blurred backdrop)."""
    main = img_tag(img, f"(min-width: {HERO_CAP}px) {HERO_CAP}px, 100vw", HERO_W,
                   eager=eager, prefix=prefix, cap=HERO_CAP)
    return f'<span class="wide">{main}</span>'


def credit(img):
    lic = e(img["license"])
    if img.get("license_url"):
        lic = f'<a href="{e(img["license_url"])}" rel="license noopener" target="_blank">{lic}</a>'
    file_page = "https://commons.wikimedia.org/wiki/" + img["file"].replace(" ", "_")
    return (f'Photo: <a href="{e(file_page)}" target="_blank" rel="noopener">{e(img["author"])}</a>'
            f' via Wikimedia Commons, {lic}. Illustrative image.')


# ---------- Page shell ----------

THEME_BOOT = ("<script>try{var t=localStorage.getItem('theme');"
              "if(t)document.documentElement.dataset.theme=t}catch(e){}</script>")


def asset_version(path):
    """Short content hash so browsers re-fetch CSS/JS after every change (Pages caches 10 min)."""
    with open(os.path.join(ROOT, path), "rb") as f:
        return hashlib.md5(f.read()).hexdigest()[:8]


def analytics():
    if not GOATCOUNTER:
        return ""
    return (f'\n  <script data-goatcounter="https://{GOATCOUNTER}.goatcounter.com/count" '
            'async src="https://gc.zgo.at/count.js"></script>')


def page(title, active, body, prefix="", desc="", og=""):
    nav = "\n".join(
        f'          <li><a href="{prefix}{s}.html"{" class=\"active\" aria-current=\"page\"" if s == active else ""}>{n}</a></li>'
        for s, n in CATS)
    foot = "".join(f'<a href="{prefix}{s}.html">{n}</a>' for s, n in CATS[1:])
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{e(title)}</title>
  <meta name="description" content="{e(desc or 'Science news you can trust, explained in plain words and linked to the original research.')}">{og}
  <link rel="icon" href="{prefix}favicon.ico" sizes="any">
  <link rel="icon" type="image/png" sizes="32x32" href="{prefix}brand/favicon-32.png">
  <link rel="icon" type="image/png" sizes="192x192" href="{prefix}brand/favicon-192.png">
  <link rel="apple-touch-icon" href="{prefix}brand/favicon-180.png">
  {THEME_BOOT}
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Playfair+Display:ital,wght@0,700;0,900;1,400&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{prefix}css/style.css?v={asset_version('css/style.css')}">
  <script src="{prefix}js/site.js?v={asset_version('js/site.js')}" defer></script>
  <script src="{prefix}js/bg-fx.js?v={asset_version('js/bg-fx.js')}" defer></script>{analytics()}
</head>
<body id="top">
  <header class="sitehead">
    <div class="sitehead-inner">
      <a href="{prefix}index.html" class="brand" aria-label="{SITE} home"><img src="{prefix}brand/mark-136.png" alt="" width="34" height="34">Far<span>light</span><small>News</small></a>
      <nav class="catnav" aria-label="Categories">
        <ul>
{nav}
        </ul>
      </nav>
      <button class="theme-toggle" type="button" aria-label="Toggle dark mode" title="Toggle dark mode">
        <svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path fill="currentColor" d="M12 3a9 9 0 1 0 9 9c0-.46-.04-.92-.1-1.36a5.39 5.39 0 0 1-4.4 2.26 5.4 5.4 0 0 1-3.14-9.8C12.92 3.04 12.46 3 12 3z"/></svg>
      </button>
    </div>
  </header>
  <main class="wrap">
{body}
  </main>
  <footer class="footer">
    <div class="wrap">
      <div class="footer-brand">
        <a href="{prefix}index.html" class="brand"><img src="{prefix}brand/mark-136.png" alt="" width="34" height="34" loading="lazy">Far<span>light</span><small>News</small></a>
        <p>Discoveries worth interrupting your day for.</p>
      </div>
      <nav aria-label="Footer">{foot}<a href="{prefix}credits.html">Image credits</a></nav>
      <span>© {YEAR} {SITE}. Every story links to the original research and reporting.</span>
    </div>
  </footer>
  <a class="to-top" href="#top" aria-label="Back to top">↑</a>
</body>
</html>
"""


# ---------- Building blocks ----------

def meta(s, short=True):
    place = "" if short else f' · {e(s["location"])}'
    return (f'<div class="meta"><time datetime="{s["date"]}">{fmt_date(s["date"])}</time>'
            f'{place} · {s["read"]} min read</div>')


def tag(s, prefix):
    return f'<a class="tag" href="{prefix}{s["cat"]}.html">{CATNAME[s["cat"]]}</a>'


def card(s, prefix=""):
    """Whole card is one link (the headline's ::after covers it); the tag stays separately clickable."""
    href = f'{prefix}news/{s["slug"]}.html'
    return f"""      <article class="card">
        <div class="thumb">{img_tag(s['img'], "(max-width: 640px) 100vw, (max-width: 960px) 50vw, 420px", 960, prefix=prefix)}</div>
        <div class="card-body">
          {tag(s, prefix)}
          <h3><a class="card-link" href="{href}">{e(s['headline'])}</a></h3>
          {meta(s)}
          <p>{e(s['dek'])}</p>
        </div>
      </article>"""


def mini(s, prefix=""):
    return f"""        <article class="card mini">
          <div class="thumb">{img_tag(s['img'], "120px", 330, prefix=prefix)}</div>
          <div>
            {tag(s, prefix)}
            <h3><a class="card-link" href="{prefix}news/{s['slug']}.html">{e(s['headline'])}</a></h3>
          </div>
        </article>"""


def lead(main, side, prefix="", hl="h1", side_title="Also new"):
    """Full-bleed photo, headline block underneath, short list of other stories beside it."""
    href = f'{prefix}news/{main["slug"]}.html'
    aside = (f'      <aside class="hero-side">\n        <h2 class="side-title">{e(side_title)}</h2>\n'
             + "\n".join(mini(o, prefix) for o in side) + "\n      </aside>") if side else ""
    return f"""    <section class="hero">
      <a class="bleed hero-media" href="{href}" tabindex="-1" aria-hidden="true">{wide_img(main['img'], eager=True, prefix=prefix)}</a>
      <div class="hero-grid{'' if side else ' solo'}">
        <article class="card hero-main">
          {tag(main, prefix)}
          <{hl}><a class="card-link" href="{href}">{e(main['headline'])}</a></{hl}>
          <p class="hero-dek">{e(main['dek'])}</p>
          {meta(main)}
        </article>
{aside}
      </div>
    </section>
"""


def feature(s, prefix=""):
    """Full-bleed photo with the headline in a box overlapping its lower edge."""
    href = f'{prefix}news/{s["slug"]}.html'
    return f"""    <section class="bleed feature">
      <a class="feature-media" href="{href}" tabindex="-1" aria-hidden="true">{wide_img(s['img'], prefix=prefix)}</a>
      <article class="card feature-box">
        {tag(s, prefix)}
        <h2><a class="card-link" href="{href}">{e(s['headline'])}</a></h2>
        <p>{e(s['dek'])}</p>
        {meta(s)}
      </article>
    </section>
"""


FB_URL = "https://www.facebook.com/profile.php?id=61596428352922"


def rail(prefix=""):
    topics = "".join(
        f'<li><a href="{prefix}{slug}.html">{e(name)}<span>{sum(1 for s in STORIES if s["cat"] == slug)}</span></a></li>'
        for slug, name in CATS[1:])
    return f"""      <aside class="rail">
        <div class="rail-box">
          <h2>Follow {SITE}</h2>
          <p>New discoveries every few hours, explained in plain words.</p>
          <a class="btn" href="{FB_URL}" target="_blank" rel="noopener">Follow on Facebook →</a>
        </div>
        <div class="rail-box">
          <h2>How we work</h2>
          <p>We only cover findings reported by at least two independent sources, and every story links to the original research.</p>
        </div>
        <div class="rail-box">
          <h2>Topics</h2>
          <ul class="topics">{topics}</ul>
        </div>
      </aside>"""


def feed(items, prefix="", cls=""):
    cards = [card(s, prefix) for s in items]
    return f'    <section class="feed{" " + cls if cls else ""}">\n' + "\n".join(cards) + "\n    </section>\n"


def feed_with_rail(items, prefix=""):
    cards = "\n".join(card(s, prefix) for s in items)
    return (f'    <div class="with-rail">\n      <section class="feed feed-2">\n{cards}\n      </section>\n'
            f'{rail(prefix)}\n    </div>\n')


def head(title, sub, level="h2"):
    return f'    <div class="section-head"><{level}>{e(title)}</{level}><p>{sub}</p></div>\n'


def figure(img, cls="", prefix="../"):
    hero = cls == "hero"
    sizes = "(max-width: 860px) 100vw, 760px" if hero else "(max-width: 720px) 100vw, 680px"
    return f"""      <figure class="figure {cls}">
        {img_tag(img, sizes, 1280, eager=hero, prefix=prefix)}
      </figure>"""


def pager(s):
    i = STORIES.index(s)
    prev_s = STORIES[i - 1] if i > 0 else None
    next_s = STORIES[i + 1] if i + 1 < len(STORIES) else None
    cell = lambda o, label, cls: (
        f'<a class="pager-{cls}" href="{o["slug"]}.html"><span>{label}</span>{e(o["headline"])}</a>'
        if o else '<span></span>')
    return (f'      <nav class="pager" aria-label="More stories">{cell(prev_s, "← Previous story", "prev")}'
            f'{cell(next_s, "Next story →", "next")}</nav>')


SITE_URL = "https://farlightnews.github.io"
# Wikimedia robot policy: identify the client with a contact URL or downloads get 429-blocked.
USER_AGENT = f"FarlightBot/1.0 ({SITE_URL}) python-urllib"


def og_tags(s):
    """Open Graph tags so Facebook link posts show the headline, dek and picture."""
    img = s["img"]
    og = require_local(f"img/og/{s['slug']}.jpg")  # 1200x630 news-style card from tools/make_cards.py
    src = f"{SITE_URL}/{og}?v={asset_version(og)}"
    tags = [("og:type", "article"), ("og:site_name", SITE), ("og:title", s["headline"]),
            ("og:description", s["dek"]), ("og:url", f"{SITE_URL}/news/{s['slug']}.html"),
            ("og:image", src), ("og:image:width", "1200"), ("og:image:height", "630"),
            ("og:image:alt", img["alt"])]
    out = "".join(f'\n  <meta property="{k}" content="{e(v)}">' for k, v in tags)
    return out + '\n  <meta name="twitter:card" content="summary_large_image">'


def article_page(s):
    parts = []
    for block in s["body"]:
        if isinstance(block, str):
            parts.append(f"        <p>{e(block)}</p>")
        elif "quote" in block:
            parts.append(f'        <blockquote class="pullquote">{e(block["quote"])}</blockquote>')
        elif "h2" in block:
            parts.append(f"        <h2>{e(block['h2'])}</h2>")
        elif "img2" in block and s.get("img2"):
            parts.append(figure(s["img2"]))
    sources = "".join(
        f'<li><a href="{e(src["url"])}" target="_blank" rel="noopener">{e(src["name"])}</a></li>'
        for src in s["sources"])
    same = by_date(o for o in STORIES if o["slug"] != s["slug"] and o["cat"] == s["cat"])
    rest = by_date(o for o in STORIES if o["slug"] != s["slug"] and o["cat"] != s["cat"])
    more = (same + rest)[:6]
    more_title = f"More {CATNAME[s['cat']]}" if same else "More science"
    hero_img = s["img"]
    body = f"""    <article class="article">
      <figure class="bleed article-hero">
        {wide_img(hero_img, eager=True, prefix="../")}
      </figure>
      <header class="article-head">
        {tag(s, '../')}
        <h1>{e(s['headline'])}</h1>
        <p class="dek">{e(s['dek'])}</p>
        <div class="byline">By <b>{SITE} Staff</b> · <time datetime="{s['date']}">{fmt_date(s['date'])}</time> · {e(s['location'])} · {s['read']} min read</div>
      </header>
      <div class="article-body">
{chr(10).join(parts)}
      </div>
      <aside class="sources">
        <h2>Original reporting</h2>
        <ul>{sources}</ul>
      </aside>
      <p class="disclaimer">Written in our own words from the research and reporting linked above. If we get something wrong, we fix it and note the correction here.</p>
{pager(s)}
    </article>
{head(more_title, '<a href="../index.html">All stories →</a>')}{feed(more, '../')}"""
    return page(f"{s['headline']} — {SITE}", s["cat"], body, "../", s["dek"], og_tags(s))


def build():
    os.makedirs(os.path.join(ROOT, "news"), exist_ok=True)
    missing = {img["file"] for s in STORIES for img in (s["img"], s.get("img2")) if img} - set(IMG_META)
    if missing:
        print(f"warning: {len(missing)} images lack cached sizes; run tools/fetch_image_meta.py")
    out = {}

    # Homepage: curated top story and three side stories, then everything else newest first.
    body = lead(STORIES[0], STORIES[1:4])
    rest = by_date(STORIES[4:])
    body += head("Latest", f"{len(STORIES)} stories, newest first")
    body += feed_with_rail(rest[:6])
    if len(rest) > 6:
        body += feature(rest[6])
    if len(rest) > 7:
        body += head("More stories", "") + feed(rest[7:])
    out["index.html"] = page(SITE, "index", body)

    # Category pages: only that category's stories, then a clearly separate "elsewhere" block.
    for slug, name in CATS[1:]:
        mine = by_date(s for s in STORIES if s["cat"] == slug)
        others = by_date(s for s in STORIES if s["cat"] != slug)
        count = f"{len(mine)} {'story' if len(mine) == 1 else 'stories'}"
        if mine:
            body = f'    <div class="cat-title"><h1>{e(name)}</h1><p>{count}</p></div>\n'
            side = mine[1:4] if len(mine) >= 3 else []
            body += lead(mine[0], side, hl="h2", side_title=f"More {name}")
            rest = mine[1 + len(side):]
            if rest:
                body += head(f"More {name}", "") + feed(rest)
        else:
            body = head(name, "0 stories", "h1")
            body += ('    <p class="empty">No stories in '
                     f'{e(name)} yet. Check back soon.</p>\n')
        body += head("Elsewhere on " + SITE, '<a href="index.html">All stories →</a>') + feed(others[:6])
        out[f"{slug}.html"] = page(f"{name} — {SITE}", slug, body)

    # Article pages.
    for s in STORIES:
        out[f"news/{s['slug']}.html"] = article_page(s)

    # Credits.
    rows = []
    for s in STORIES:
        for img in filter(None, [s["img"], s.get("img2")]):
            rows.append(f'      <li><a href="news/{s["slug"]}.html">{e(s["headline"])}</a> — {credit(img)}</li>')
    hero_img = s["img"]
    body = f"""    <article class="article">
      <figure class="bleed article-hero">
        {wide_img(hero_img, eager=True, prefix="../")}
      </figure>
      <header class="article-head"><h1>Image credits</h1>
        <p class="dek">Every photo on {SITE} comes from Wikimedia Commons under a public-domain or Creative Commons licence. Photos are illustrative and were not taken at the events described.</p>
      </header>
      <div class="sources"><ul>
{chr(10).join(rows)}
      </ul></div>
    </article>
"""
    out["credits.html"] = page(f"Image credits — {SITE}", "", body)

    for name, text in out.items():
        with open(os.path.join(ROOT, name), "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
    print(f"Wrote {len(out)} pages")


if __name__ == "__main__":
    build()
