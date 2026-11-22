"""Profile picture, favicons and Facebook cover for Farlight.

Usage:  python tools/make_brand.py [out_dir]   (default: brand/)
"""
import math
import os
import random
import sys
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "brand")
NAVY = (13, 27, 46); BLUE = (11, 95, 165); SKY = (108, 182, 255)
CREAM = (244, 246, 248); MUTED = (150, 165, 182); RULE = (44, 62, 86)
F = "C:/Windows/Fonts/"
bold = lambda s: ImageFont.truetype(F + "georgiab.ttf", int(s))
ital = lambda s: ImageFont.truetype(F + "georgiai.ttf", int(s))
sans = lambda s: ImageFont.truetype(F + "segoeuib.ttf", int(s))


def stars(d, W, H, n, seed=7, alpha_max=150):
    rnd = random.Random(seed)
    for _ in range(n):
        x, y = rnd.random() * W, rnd.random() * H
        r = rnd.choice([1, 1, 1, 2, 2, 3]) * W / 1640
        a = rnd.randint(40, alpha_max)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, a))


def layer(size):
    L = Image.new("RGBA", size, (0, 0, 0, 0))
    return L, ImageDraw.Draw(L)


def orbit_layer(size, cx, cy, rx, ry, tilt_deg, width, color):
    """Smooth tilted ellipse: drawn axis-aligned on its own layer, then rotated."""
    L, d = layer(size)
    d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], outline=color, width=width)
    return L.rotate(-tilt_deg, resample=Image.BICUBIC, center=(cx, cy))


def point_on(cx, cy, rx, ry, tilt_deg, t_deg):
    t, tilt = math.radians(t_deg), math.radians(tilt_deg)
    x, y = rx * math.cos(t), ry * math.sin(t)
    return cx + x * math.cos(tilt) - y * math.sin(tilt), cy + x * math.sin(tilt) + y * math.cos(tilt)


def profile(S=2048):
    im = Image.new("RGBA", (S, S), NAVY + (255,))
    L, d = layer((S, S)); stars(d, S, S, 70, seed=3, alpha_max=120); im.alpha_composite(L)
    cx, cy = S / 2, S / 2
    rx, ry, tilt = S * .42, S * .13, -20
    back = orbit_layer((S, S), cx, cy, rx, ry, tilt, int(S * .016), SKY + (255,))
    im.alpha_composite(back)
    L, d = layer((S, S))
    d.text((cx, cy + S * .015), "S", font=bold(S * .58), fill=CREAM, anchor="mm")
    im.alpha_composite(L)
    # front half of the orbit passes over the letter
    front = back.copy()
    mask = Image.new("L", (S, S), 0)
    ImageDraw.Draw(mask).rectangle([0, cy, S, S], fill=255)
    mask = mask.rotate(20, center=(cx, cy))
    im.paste(front, (0, 0), Image.composite(front.split()[3], Image.new("L", (S, S), 0), mask))
    px, py = point_on(cx, cy, rx, ry, tilt, 20)
    r = S * .05
    L, d = layer((S, S)); d.ellipse([px - r, py - r, px + r, py + r], fill=SKY); im.alpha_composite(L)
    im = im.convert("RGB")
    m = Image.new("L", (S, S), 0); ImageDraw.Draw(m).ellipse([0, 0, S, S], fill=255)
    pv = Image.new("RGB", (S, S), (36, 37, 38)); pv.paste(im, (0, 0), m)
    pv.resize((512, 512), Image.LANCZOS).save(os.path.join(OUT, "_preview-circle.png"))
    im.resize((1024, 1024), Image.LANCZOS).save(os.path.join(OUT, "profile-1024.png"))
    im.resize((180, 180), Image.LANCZOS).save(os.path.join(OUT, "favicon-180.png"))
    im.resize((32, 32), Image.LANCZOS).save(os.path.join(OUT, "favicon-32.png"))


def cover(K=2):
    W, H = 1640 * K, 624 * K
    im = Image.new("RGBA", (W, H), NAVY + (255,))
    L, sd = layer((W, H)); stars(sd, W, H, 220, alpha_max=130); im.alpha_composite(L)
    cx = W / 2
    im.alpha_composite(orbit_layer((W, H), cx, H * .36, W * .37, H * .17, -5, 2 * K, (108, 182, 255, 90)))
    d = ImageDraw.Draw(im)
    hl = lambda y, x0=0, x1=W, c=RULE: d.rectangle([x0, y * K, x1, y * K + K - 1], fill=c)
    hl(18); hl(58)
    d.text((60 * K, 44 * K), "SCIENCE NEWS", font=sans(15 * K), fill=MUTED, anchor="ls")
    d.text((W - 60 * K, 44 * K), "EST. 2026", font=sans(15 * K), fill=MUTED, anchor="rs")
    d.text((cx, 44 * K), "EVERY STORY LINKS TO THE RESEARCH", font=sans(15 * K), fill=CREAM, anchor="ms")
    mf = bold(112 * K)
    w1 = d.textlength("Far", font=mf); w2 = d.textlength("light", font=mf)
    x = cx - (w1 + w2) / 2; base = 222 * K
    d.text((x, base), "Far", font=mf, fill=CREAM, anchor="ls")
    d.text((x + w1, base), "light", font=mf, fill=SKY, anchor="ls")
    d.rectangle([x, 246 * K, x + w1 + w2, 249 * K], fill=CREAM)
    d.text((cx, 300 * K), "Discoveries worth interrupting your day for.",
           font=ital(25 * K), fill=MUTED, anchor="ms")
    cats = ["SPACE", "HEALTH", "EARTH & CLIMATE", "LIFE", "PHYSICS", "TECH", "MIND"]
    cf = sans(17 * K)
    widths = [d.textlength(c, font=cf) for c in cats]
    gap = 44 * K; total = sum(widths) + gap * (len(cats) - 1)
    px = cx - total / 2; y = 400 * K
    for c, w in zip(cats, widths):
        d.text((px, y), c, font=cf, fill=CREAM, anchor="ls")
        px += w + gap
        if c != cats[-1]:
            r = 3 * K
            d.ellipse([px - gap / 2 - r, y - 7 * K - r, px - gap / 2 + r, y - 7 * K + r], fill=SKY)
    d.rectangle([0, 520 * K, W, 576 * K], fill=BLUE)
    d.text((cx, 548 * K), "Peer-reviewed findings  ·  Plain words  ·  Sources on every page",
           font=sans(21 * K), fill=CREAM, anchor="mm")
    hl(600)
    im = im.convert("RGB").resize((1640, 624), Image.LANCZOS)
    im.save(os.path.join(OUT, "cover-1640x624.png"))
    mw = int(624 * 16 / 9)
    im.crop(((1640 - mw) // 2, 0, (1640 + mw) // 2, 624)).save(os.path.join(OUT, "_preview-mobile.png"))


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    profile(); cover()
    print("brand assets written to", OUT)
