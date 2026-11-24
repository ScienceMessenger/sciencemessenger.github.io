# ScienceNews rules

Read SOURCES.md before adding stories and FACEBOOK.md before posting.

## Images (hard rules)
- **Public domain or CC0 only.** No CC BY / CC BY-SA or any image that requires attribution, and nothing copyrighted.
  Set `license` in tools/stories.json to exactly `Public domain` or `CC0`; build.py rejects anything else.
  If an image would need attribution, don't use it: find a PD/CC0 one instead.
- **No attribution where none is required.** No "Photo: author / license" captions under images on article pages,
  and no credit text on Facebook cards. PD/CC0 needs none.
- **One extra in-article image, only if it truly fits.** Every story gets a second picture (`"img2"` in tools/stories.json,
  placed with a `{"img2": true}` body block near the middle of the article, between paragraphs). It must show the story's
  actual subject (the object, place, instrument, species or thing discussed), be different from the hero photo, and follow
  all image rules above. If no PD/CC0 image really fits, add nothing: no generic or loosely related filler.
- **Always self-hosted.** Never hotlink upload.wikimedia.org or any other host. Pipeline after editing stories:
  `python tools/fetch_image_meta.py` → `python tools/fetch_images.py` → `python tools/make_cards.py` → `python tools/build.py`, then commit `img/`.

## Facebook image posts (hard rule)
- Every Facebook image post uses the news-card style from `tools/make_cards.py` (`img/fb/<slug>.jpg`): our logo mark + "Farlight" wordmark between thin blue rules on top, then a big spaced red "NEWS" topic tag on its own line between the logo and the headline, big serif headline, one short grey teaser line, story photo below on black.
- Every story needs `"card": {"title", "sub"}` in tools/stories.json: title ≤60 chars, sub ≤90, short and clickbaity but literally true (see FACEBOOK.md).
- No photo credit or watermark text on images or Facebook share cards.

## Sources and legal (hard rules)
- **Space first:** aim for ~75% space stories (and FB posts) when good ones exist; the rest other science. Never pick a dull or weak space story just to hit the ratio (see SOURCES.md).
- Story topics come from the reference pages in SOURCES.md. Use a topic only if **at least 2 different reference pages** covered the same finding.
- Write everything in our own words: facts only, never copied or lightly reworded sentences, max two short attributed quotes, never a source's headline.
- Headlines may tease, but must be literally true and the article must deliver on them. No fake quotes, numbers or experts.
- Never use images from news sites, Facebook, Google or stock sites. Commons PD/CC0 only (ESA/ESO/university images are usually CC BY: not allowed).
