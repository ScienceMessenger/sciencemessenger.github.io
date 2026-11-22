# Farlight

Science news in plain words, with every story linked to the original research. Static site served by GitHub Pages at https://farlightnews.github.io.

## How it works
- `tools/stories.json`: every story (headline, dek, body, sources, Wikimedia Commons images). Newest editorial picks go first; the first four fill the homepage lead.
- `python tools/fetch_image_meta.py`: caches image sizes from Commons. Run it after adding stories with new images.
- `python tools/fetch_images.py`: downloads every image into `img/` (all srcset widths). Images are always self-hosted and must be public domain or CC0; `build.py` fails otherwise. Commit `img/`.
- `python tools/make_cards.py`: makes the news-style share cards from each story's `card` text: `img/fb/<slug>.jpg` (1080x1350, for Facebook image posts) and `img/og/<slug>.jpg` (1200x630 og:image). See FACEBOOK.md.
- `python tools/build.py`: writes `index.html`, the category pages, `news/<slug>.html` and `credits.html`.
- `python tools/make_brand.py`: regenerates the logo, favicons and Facebook cover in `brand/`.
- Preview locally with `python -m http.server 5500`.

## Rules
- [SOURCES.md](SOURCES.md): which sources count, how to verify, how to write.
- [FACEBOOK.md](FACEBOOK.md): how and when to post to the Facebook page.
