"""News-style share cards for every story (the house style for all Facebook image posts).

Usage:  python tools/make_cards.py
Run after tools/fetch_images.py and before tools/build.py.

Writes, per story:
  img/fb/<slug>.jpg  1080x1350 (4:5) picture for Facebook image posts
  img/og/<slug>.jpg  1200x630 (1.91:1) og:image, same style, for link previews

Layout: thin blue rules with the Science Messenger mark (ringed planet with signal arcs) and "Science Messenger" wordmark on top, a big serif headline, a short grey
teaser line under it, and the story's hero photo below fading into black.
Text comes from the story's "card": {"title": ..., "sub": ...} in tools/stories.json.
No photo credit or watermark goes on the card; the mark is the only branding.
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build  # noqa: E402
import make_logo  # noqa: E402

F = "C:/Windows/Fonts/"
SERIF = F + "georgiab.ttf"
SANS = F + "segoeui.ttf"
BG = (6, 8, 12)
RULE = (11, 95, 165)  # brand blue
SKY = (108, 182, 255)
WHITE = (250, 250, 250)
GREY = (205, 210, 216)

TITLE_MAX, SUB_MAX = 60, 90  # characters: keep cards short


def font(path, size):
    return ImageFont.truetype(path, int(size))


def wrap(d, text, fnt, width):
    lines, cur = [], ""
    for word in text.split():
        trial = f"{cur} {word}".strip()
        if d.textlength(trial, font=fnt) <= width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    return lines + [cur] if cur else lines


def fit(d, text, path, width, start, smallest, max_lines):
    """Largest font size (from start down) at which text fits in max_lines."""
    size = start
    while True:
        fnt = font(path, size)
        lines = wrap(d, text, fnt, width)
        if len(lines) <= max_lines or size <= smallest:
            # balance: narrowest width that keeps the same line count (no one-word last line)
            w = width
            while w > width * 0.6 and len(wrap(d, text, fnt, w - 10)) == len(lines):
                w -= 10
            return fnt, wrap(d, text, fnt, w)
        size -= 2


def cover(im, w, h, focus_y=0.5):
    scale = max(w / im.width, h / im.height)
    im = im.resize((round(im.width * scale), round(im.height * scale)), Image.LANCZOS)
    left = (im.width - w) // 2
    top = round((im.height - h) * focus_y)
    return im.crop((left, top, left + w, top + h))


def fade(w, h, length, side):
    """Alpha mask: 0 (transparent photo) at the given edge, 255 after `length` px."""
    m = Image.new("L", (w, h), 255)
    d = ImageDraw.Draw(m)
    for i in range(length):
        a = round(255 * (i / length) ** 1.6)
        if side == "top":
            d.line([(0, i), (w, i)], fill=a)
        else:  # left
            d.line([(i, 0), (i, h)], fill=a)
    return m


_MARK = {}


def label(card, d, cx, y, W, margin, scale=1.0):
    """Rule — logo mark + "Science Messenger" wordmark — rule, centred on cx. Returns the bottom edge."""
    h = round(84 * scale)
    if h not in _MARK:
        m = make_logo.logo(512, bg=False)
        _MARK[h] = m.resize((round(m.width * h / m.height), h), Image.LANCZOS)
    mark = _MARK[h]
    wf = font(SERIF, 40 * scale)
    w1, w2 = d.textlength("Science", font=wf), d.textlength("Messenger", font=wf)
    inner = 14 * scale
    gw = mark.width + inner + w1 + w2  # whole badge width
    x0 = cx - gw / 2
    gap = 24 * scale
    lw = max(2, round(3 * scale))
    d.line([(margin, y), (x0 - gap, y)], fill=RULE, width=lw)
    d.line([(x0 + gw + gap, y), (W - margin, y)], fill=RULE, width=lw)
    card.paste(mark, (round(x0), round(y - h / 2)), mark)
    tx = x0 + mark.width + inner
    ty = y - h * 0.06  # optical centre: the bubble's tail pulls the mark down
    d.text((tx, ty), "Science", font=wf, fill=WHITE, anchor="lm")
    d.text((tx + w1, ty), "Messenger", font=wf, fill=SKY, anchor="lm")
    return y + h / 2


def portrait(photo, title, sub, focus_y):
    W, H, M = 1080, 1350, 70
    card = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(card)
    y = label(card, d, W / 2, 110, W, M) + 60
    tf, tl = fit(d, title, SERIF, W - 2 * M, 76, 54, 3)
    lh = tf.size * 1.12
    for line in tl:
        d.text((W / 2, y), line, font=tf, fill=WHITE, anchor="ma")
        y += lh
    y += 14
    sf, sl = fit(d, sub, SANS, W - 2 * M - 40, 36, 30, 2)
    for line in sl:
        d.text((W / 2, y), line, font=sf, fill=GREY, anchor="ma")
        y += sf.size * 1.3
    top = round(y + 10)
    ph = H - top
    pic = cover(photo, W, ph, focus_y)
    card.paste(pic, (0, top), fade(W, ph, min(260, ph // 2), "top"))
    return card


def landscape(photo, title, sub, focus_y):
    W, H, M = 1200, 630, 56
    card = Image.new("RGB", (W, H), BG)
    pw = 640
    pic = cover(photo, pw, H, focus_y)
    card.paste(pic, (W - pw, 0), fade(pw, H, 240, "left"))
    d = ImageDraw.Draw(card)
    col = W - pw + 60  # text column overlaps the faded photo edge
    cx = col / 2
    label(card, d, cx, 70, col, M, 0.7)
    tf, tl = fit(d, title, SERIF, col - 2 * M, 58, 40, 4)
    sf, sl = fit(d, sub, SANS, col - 2 * M, 28, 24, 3)
    block = len(tl) * tf.size * 1.12 + 16 + len(sl) * sf.size * 1.3
    y = 120 + (H - 120 - block) / 2
    for line in tl:
        d.text((cx, y), line, font=tf, fill=WHITE, anchor="ma")
        y += tf.size * 1.12
    y += 16
    for line in sl:
        d.text((cx, y), line, font=sf, fill=GREY, anchor="ma")
        y += sf.size * 1.3
    return card


def main():
    for sub_dir in ("fb", "og"):
        os.makedirs(os.path.join(build.ROOT, "img", sub_dir), exist_ok=True)
    for s in build.STORIES:
        c = s.get("card") or {}
        if not c.get("title") or not c.get("sub"):
            sys.exit(f"{s['slug']}: add \"card\": {{\"title\", \"sub\"}} to tools/stories.json")
        if len(c["title"]) > TITLE_MAX or len(c["sub"]) > SUB_MAX:
            sys.exit(f"{s['slug']}: card title max {TITLE_MAX} chars, sub max {SUB_MAX}")
        img = s["img"]
        build.check_license(img)
        src = build.require_local(build.local_src(img, build.local_widths(img)[-1]))
        photo = Image.open(os.path.join(build.ROOT, src)).convert("RGB")
        if c.get("crop"):  # [left, top, right, bottom] as fractions: cut out text baked into a photo
            l, t, r, b = c["crop"]
            photo = photo.crop((round(l * photo.width), round(t * photo.height),
                                round(r * photo.width), round(b * photo.height)))
        fy = c.get("focus_y", 0.4)
        for name, fn in (("fb", portrait), ("og", landscape)):
            out = os.path.join(build.ROOT, "img", name, s["slug"] + ".jpg")
            fn(photo, c["title"], c["sub"], fy).save(out, "JPEG", quality=88, optimize=True, progressive=True)
            print("saved", os.path.relpath(out, build.ROOT))


if __name__ == "__main__":
    main()
