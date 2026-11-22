"""Farlight logo (white star in a ring with a pale gold dot on it) and photo cover for Facebook.

Usage:  python tools/make_logo.py
Writes brand/logo-1024.png (profile picture), brand/favicon-{32,180,192,512}.png, favicon.ico,
brand/mark-136.png (transparent header mark)
and brand/cover-photo-1640x624.png.

Cover photo: "Earthrise" (Apollo 8, NASA), Wikimedia Commons File:Earth-moon.jpg, public domain.
Source kept in brand/src/earth-moon.jpg.
"""
import os
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "brand")
NAVY = (13, 27, 46); BLUE = (11, 95, 165); SKY = (108, 182, 255); CREAM = (244, 246, 248); WHITE = (255, 255, 255); GOLD = (240, 225, 182)  # pale gold, close to white
BLACK = (6, 6, 8)  # background for the profile icon, favicons and cover
NEWS_RED = (255, 59, 48)  # sharp news red, only for the "NEWS" tag
F = "C:/Windows/Fonts/"
SS = 4  # supersampling factor


def logo(size, stars=True, bg=True, small=False):
    """Corona mark: a white star inside one soft white ring, with a pale gold dot riding on the ring.
    Drawn on a 40-unit grid. bg=False: just the mark on transparent (RGBA), cropped to its bounds,
    used in the site header and on share cards. small=True: heavier rings so favicons stay legible."""
    S = size * SS
    u = S / 40
    im = Image.new("RGBA", (S, S), BLACK + (255,) if bg else (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    rnd = random.Random(3)
    for _ in range(50 if stars and bg else 0):
        x, y, r = rnd.random() * S, rnd.random() * S, rnd.choice([1, 1, 2]) * S / 1024 * 2
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, rnd.randint(30, 90)))

    # one ring and a solid star, scaled up to fill the 40-unit grid
    cx = cy = 20 * u
    w = max(1, round((2.0 if small else 1.15) * u))
    r = 12 * u
    L = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(L).ellipse([cx - r, cy - r, cx + r, cy + r], outline=WHITE + (round(255 * (0.85 if small else 0.6)),), width=w)
    im.alpha_composite(L)
    d = ImageDraw.Draw(im)
    sr = (6.4 if small else 5.7) * u
    d.ellipse([cx - sr, cy - sr, cx + sr, cy + sr], fill=WHITE)
    # pale gold dot riding on the ring, upper right (45 degrees)
    k = 12 * u * 0.7071
    pr = (3.0 if small else 2.4) * u
    d.ellipse([cx + k - pr, cy - k - pr, cx + k + pr, cy - k + pr], fill=GOLD)
    im = im.resize((size, size), Image.LANCZOS)
    return im.convert("RGB") if bg else im.crop(im.getbbox())


def spaced(d, x, cy, word, fnt, track, fill):
    """Draw word in letter-spaced capitals, vertically centred on cy; returns the end x."""
    for c in word:
        d.text((x, cy), c, font=fnt, fill=fill, anchor="lm")
        x += d.textlength(c, font=fnt) + track
    return x - track


def profile(size=1024):
    """Facebook profile picture: the mark with a red "NEWS" tag under it, on black with faint stars."""
    im = Image.new("RGBA", (size, size), BLACK + (255,))
    d = ImageDraw.Draw(im)
    rnd = random.Random(3)
    for _ in range(50):
        x, y, r = rnd.random() * size, rnd.random() * size, rnd.choice([1, 1, 2]) * size / 1024 * 2
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, rnd.randint(30, 90)))
    mark = logo(size * 2, bg=False)
    m = round(size * 0.56)
    mark = mark.resize((m, round(m * mark.height / mark.width)), Image.LANCZOS)
    im.alpha_composite(mark, ((size - m) // 2, round(size * 0.15)))
    fnt = ImageFont.truetype(F + "segoeuib.ttf", round(size * 0.085))
    track = size * 0.03
    w = sum(d.textlength(c, font=fnt) for c in "NEWS") + track * 3
    spaced(d, (size - w) / 2, size * 0.8, "NEWS", fnt, track, NEWS_RED)
    return im.convert("RGB")


def cover():
    W, H = 1640, 624
    im = Image.new("RGBA", (W, H), BLACK + (255,))
    # soft navy glow behind the text
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([60, -200, 1300, 820], fill=(22, 22, 26, 255))
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
    mark = logo(200, bg=False)
    im.alpha_composite(mark, (x - 4, 118))
    d.text((x, 270), "Far", font=big, fill=CREAM)
    d.text((x + d.textlength("Far", font=big), 270), "light", font=big, fill=GOLD)
    # red "NEWS" tag right of the wordmark after a thin divider, like the site header
    wx = x + d.textlength("Far", font=big) + d.textlength("light", font=big) + 22
    cy = 270 + big.getbbox("Far")[3] / 2 + 6
    d.line([(wx, cy - 22), (wx, cy + 22)], fill=(255, 255, 255, 70), width=2)
    spaced(d, wx + 22, cy, "NEWS", ImageFont.truetype(F + "segoeuib.ttf", 24), 7, NEWS_RED)
    d.text((x + 4, 378), "Discoveries worth interrupting your day for.", font=ital, fill=(190, 202, 216))
    cats = "SPACE  ·  HEALTH  ·  EARTH  ·  LIFE  ·  PHYSICS  ·  TECH  ·  MIND"
    d.text((x + 4, 440), cats, font=sans, fill=(170, 186, 204))
    return im.convert("RGB")


def main():
    big = logo(1024)
    big.save(os.path.join(OUT, "logo-1024.png"))
    profile(1024).save(os.path.join(OUT, "profile-1024.png"))
    # address-bar icon: tight crop on the mark, heavier rings so it stays legible at 16-32px, no stars
    icon = logo(2048, stars=False, small=True).crop((230, 230, 1818, 1818))
    for n in (32, 180, 192, 512):
        icon.resize((n, n), Image.LANCZOS).save(os.path.join(OUT, f"favicon-{n}.png"))
    icon.resize((256, 256), Image.LANCZOS).save(os.path.join(ROOT, "favicon.ico"), sizes=[(16, 16), (32, 32), (48, 48)])
    mark = logo(136 * 4, bg=False)
    mark.resize((136, round(136 * mark.height / mark.width)), Image.LANCZOS).save(os.path.join(OUT, "mark-136.png"))
    cover().save(os.path.join(OUT, "cover-photo-1640x624.png"))
    print("wrote brand/logo-1024.png, profile-1024.png, favicons, mark-136.png, cover-photo-1640x624.png")


if __name__ == "__main__":
    main()
