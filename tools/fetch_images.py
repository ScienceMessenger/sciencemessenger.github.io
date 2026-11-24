"""Downloads every story image into img/ so the site never hotlinks Wikimedia.

Usage:  python tools/fetch_images.py [--force]
Run after tools/fetch_image_meta.py and before tools/build.py.

Rule: all images are self-hosted. Facebook's crawler gets 403 from upload.wikimedia.org,
and hotlinked images can vanish or be rate-limited. build.py refuses to build if a file is missing.

For each Commons image it saves img/<key>-<width>.jpg at every srcset width build.py uses
(key = build.img_key). An optional "crop" on the image is applied first. Share cards (img/og, img/fb) are made afterwards by tools/make_cards.py.
Existing files are skipped unless --force is given.
"""
import io
import os
import sys
import time
import urllib.error
import urllib.request

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build  # noqa: E402

IMG_DIR = os.path.join(build.ROOT, "img")


def fetch(url):
    """Polite download: pauses between files and backs off on 429 (Wikimedia rate limit)."""
    req = urllib.request.Request(url, headers={"User-Agent": build.USER_AGENT})
    for attempt in range(30):
        time.sleep(1.5)
        try:
            data = urllib.request.urlopen(req, timeout=60).read()
            break
        except urllib.error.HTTPError as err:
            if err.code != 429 or attempt == 29:
                raise
            wait = int(err.headers.get("Retry-After") or 0) or 30 * (attempt + 1)
            print(f"rate limited, waiting {wait}s")
            time.sleep(wait)
    im = Image.open(io.BytesIO(data))
    if im.mode.startswith("I"):  # 16-bit greyscale PNG: scale down to 8 bits, or everything clips to white
        im = im.convert("I").point(lambda v: v * (1 / 256)).convert("L")
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        bg = Image.new("RGB", im.size, (255, 255, 255))
        bg.paste(im, mask=im.split()[-1])
        return bg
    return im.convert("RGB")


def save(im, path):
    im.save(path, "JPEG", quality=84, optimize=True, progressive=True)
    print("saved", os.path.relpath(path, build.ROOT))


def resize(im, w):
    return im if im.width == w else im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)


def main():
    force = "--force" in sys.argv
    os.makedirs(IMG_DIR, exist_ok=True)
    missing = {img["file"] for s in build.STORIES for img in (s["img"], s.get("img2")) if img} - set(build.IMG_META)
    if missing:
        sys.exit("Run tools/fetch_image_meta.py first; no size data for: " + ", ".join(sorted(missing)))

    seen = {}  # file -> (img, largest width needed): lead photos can run full width, in-article ones can't
    for s in build.STORIES:
        for img, max_w in ((s.get("img2"), 1280), (s["img"], build.HERO_W)):
            if img:
                seen[img["file"]] = (img, max(max_w, seen.get(img["file"], (None, 0))[1]))

    for file, (img, max_w) in seen.items():
        widths = build.local_widths(img, max_w)
        paths = {w: os.path.join(build.ROOT, build.local_src(img, w)) for w in widths}
        todo = [p for p in paths.values() if force or not os.path.exists(p)]
        if not todo:
            continue
        if img["file"].lower().endswith(".svg"):  # PIL can't read SVG: take Commons' PNG render
            url = build._thumb(img, 10**9).replace("/commons/", "/commons/thumb/", 1)
            src = fetch(f"{url}/{max_w if max_w < 2000 else 1600}px-{url.rsplit('/', 1)[1]}.png")
        else:
            src = fetch(build._thumb(img, 10**9))  # original file: thumbnail renders are rate-limited much harder
        if img.get("crop"):  # [left, top, right, bottom] fractions: cut labels/text out of infographics
            l, t, r, b = img["crop"]
            src = src.crop((round(l * src.width), round(t * src.height),
                            round(r * src.width), round(b * src.height)))
        for w, p in paths.items():
            if p in todo:
                save(resize(src, w), p)


if __name__ == "__main__":
    main()
