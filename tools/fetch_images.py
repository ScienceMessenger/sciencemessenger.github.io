"""Downloads every story image into img/ so the site never hotlinks Wikimedia.

Usage:  python tools/fetch_images.py [--force]
Run after tools/fetch_image_meta.py and before tools/build.py.

Rule: all images are self-hosted. Facebook's crawler gets 403 from upload.wikimedia.org,
and hotlinked images can vanish or be rate-limited. build.py refuses to build if a file is missing.

For each Commons image it saves img/<key>-<width>.jpg at every srcset width build.py uses
(key = build.img_key). Share cards (img/og, img/fb) are made afterwards by tools/make_cards.py.
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

    seen = {}
    for s in build.STORIES:
        for img in filter(None, (s["img"], s.get("img2"))):
            seen[img["file"]] = img

    for file, img in seen.items():
        widths = build.local_widths(img)
        paths = {w: os.path.join(build.ROOT, build.local_src(img, w)) for w in widths}
        todo = [p for p in paths.values() if force or not os.path.exists(p)]
        if not todo:
            continue
        src = fetch(build._thumb(img, 10**9))  # original file: thumbnail renders are rate-limited much harder
        for w, p in paths.items():
            if p in todo:
                save(resize(src, w), p)


if __name__ == "__main__":
    main()
