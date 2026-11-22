"""Farlight logo (ringed planet sending signal arcs) and photo cover for Facebook.

Usage:  python tools/make_logo.py
Writes brand/logo-1024.png (profile picture), brand/favicon-{32,180,192,512}.png, favicon.ico
and brand/cover-photo-1640x624.png.

Cover photo: "Earthrise" (Apollo 8, NASA), Wikimedia Commons File:Earth-moon.jpg, public domain.
Source kept in brand/src/earth-moon.jpg.
"""
import os
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "brand")
NAVY = (13, 27, 46); BLUE = (11, 95, 165); SKY = (108, 182, 255); CREAM = (244, 246, 248)
F = "C:/Windows/Fonts/"
SS = 4  # supersampling factor


def logo(size, stars=True, bg=True):
    """bg=False: just the mark on a transparent background (RGBA), used on share cards."""
    S = size * SS
    im = Image.new("RGBA", (S, S), NAVY + (255,) if bg else (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    rnd = random.Random(3)
    for _ in range(60 if stars and bg else 0):
        x, y, r = rnd.random() * S, rnd.random() * S, rnd.choice([1, 1, 2]) * S / 1024 * 2
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, rnd.randint(40, 120)))

    # planet centre sits lower-left; "message" signal arcs radiate to the upper right
    cx, cy, R = S * 0.45, S * 0.55, S * 0.235
    sig = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    g = ImageDraw.Draw(sig)
    for i, (k, a) in enumerate(((0.98, 255), (1.24, 200), (1.50, 150))):
        r = R * k
        g.arc([cx - r, cy - r, cx + r, cy + r], -78, -12, fill=CREAM + (a,), width=max(2, int(S * 0.026)))
    im.alpha_composite(sig)

    # ringed planet: back half of ring, planet, front half of ring
    pr, rx, ry, w = R * 0.50, R * 0.98, R * 0.27, max(2, int(S * 0.03))
    tilt = -18

    def ring(front):
        L = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        ImageDraw.Draw(L).ellipse([cx - rx, cy - ry, cx + rx, cy + ry], outline=CREAM, width=w)
        cut = Image.new("L", (S, S), 0)
        ImageDraw.Draw(cut).rectangle([0, cy if front else 0, S, S if front else cy], fill=255)
        L.putalpha(Image.composite(L.getchannel("A"), Image.new("L", (S, S), 0), cut))
        return L.rotate(tilt, resample=Image.BICUBIC, center=(cx, cy))

    im.alpha_composite(ring(False))
    d = ImageDraw.Draw(im)
    d.ellipse([cx - pr, cy - pr, cx + pr, cy + pr], fill=SKY)
    # simple shading band and a highlight so it reads as a sphere
    d.chord([cx - pr, cy - pr, cx + pr, cy + pr], 20, 160, fill=(84, 160, 238))
    h = pr * 0.22
    d.ellipse([cx - pr * 0.45 - h, cy - pr * 0.45 - h, cx - pr * 0.45 + h, cy - pr * 0.45 + h], fill=(170, 214, 255))
    im.alpha_composite(ring(True))
    im = im.resize((size, size), Image.LANCZOS)
    return im.convert("RGB") if bg else im.crop(im.getbbox())


def cover():
    W, H = 1640, 624
    im = Image.new("RGBA", (W, H), (8, 14, 26, 255))
    # soft navy glow behind the text
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([60, -200, 1300, 820], fill=NAVY + (255,))
    im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(120)))
    rnd = random.Random(11)
    st = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sd = ImageDraw.Draw(st)
    for _ in range(260):
        x, y = rnd.random() * W, rnd.random() * H
        r = rnd.choice([0.7, 0.7, 1, 1.4])
        sd.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, rnd.randint(40, 150)))
    im.alpha_composite(st)

    # thin orbit arc around Earth, a nod to the logo
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(L).ellipse([1245 - 230, 300 - 62, 1245 + 230, 300 + 62], outline=SKY + (120,), width=2)
    im.alpha_composite(L.rotate(14, resample=Image.BICUBIC, center=(1245, 300)))
    # Earth cut from the Earthrise photo (black space around it), placed inside the mobile-safe area
    src = Image.open(os.path.join(OUT, "src", "earth-moon.jpg")).convert("RGB")
    k = src.width / 3000
    ex, ey, er = 1721 * k, 947 * k, 238 * k
    half = er * 1.15
    earth = src.crop((int(ex - half), int(ey - half), int(ex + half), int(ey + half)))
    D = 250
    side = int(D * 1.15)
    earth = earth.resize((side, side), Image.LANCZOS)
    mask = Image.new("L", (side, side), 0)
    ImageDraw.Draw(mask).ellipse([side / 2 - D / 2, side / 2 - D / 2, side / 2 + D / 2, side / 2 + D / 2], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(3))
    # lighten-only so the photo's black sky never covers our stars
    px, py = 1245 - side // 2, 300 - side // 2
    region = im.crop((px, py, px + side, py + side)).convert("RGB")
    lit = Image.composite(Image.fromarray(__import__("numpy").maximum(
        __import__("numpy").asarray(region), __import__("numpy").asarray(earth))), region, mask)
    im.paste(lit, (px, py))


    d = ImageDraw.Draw(im)
    big = ImageFont.truetype(F + "georgiab.ttf", 74)
    ital = ImageFont.truetype(F + "georgiai.ttf", 27)
    sans = ImageFont.truetype(F + "segoeuib.ttf", 19)
    x = 290
    mark = logo(132)
    m = Image.new("L", mark.size, 0); ImageDraw.Draw(m).ellipse([0, 0, *mark.size], fill=255)
    im.paste(mark, (x, 120), m)
    d.text((x, 270), "Far", font=big, fill=CREAM)
    d.text((x + d.textlength("Far", font=big), 270), "light", font=big, fill=SKY)
    d.text((x + 4, 378), "Discoveries worth interrupting your day for.", font=ital, fill=(190, 202, 216))
    cats = "SPACE  ·  HEALTH  ·  EARTH  ·  LIFE  ·  PHYSICS  ·  TECH  ·  MIND"
    d.text((x + 4, 440), cats, font=sans, fill=(170, 186, 204))
    return im.convert("RGB")


def main():
    big = logo(1024)
    big.save(os.path.join(OUT, "logo-1024.png"))
    big.save(os.path.join(OUT, "profile-1024.png"))
    # address-bar icon: tight crop on the bubble so it stays legible at 16-32px, no stars
    icon = logo(2048, stars=False).crop((250, 250, 1798, 1798))
    for n in (32, 180, 192, 512):
        icon.resize((n, n), Image.LANCZOS).save(os.path.join(OUT, f"favicon-{n}.png"))
    icon.resize((256, 256), Image.LANCZOS).save(os.path.join(ROOT, "favicon.ico"), sizes=[(16, 16), (32, 32), (48, 48)])
    cover().save(os.path.join(OUT, "cover-photo-1640x624.png"))
    print("wrote brand/logo-1024.png, profile-1024.png, favicons, cover-photo-1640x624.png")


if __name__ == "__main__":
    main()
