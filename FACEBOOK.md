# Facebook post rules

## Goal
Get people to click through to the full story. Make them curious about the finding without misleading them about it.

## How
- Open with the most surprising true detail, then leave the explanation (how they found it, what it means) for the article.
- Curiosity phrasing is fine ("Astronomers expected a dead star. The data showed something else."), but every claim in the post must be literally true and match the paper.
- Keep it short: 1–2 lines, then the link.

## Image post style (every post)
- Every post is an image post using the story's news card `img/fb/<slug>.jpg` (1080x1350, made by `python tools/make_cards.py`). Caption = the 1–2 line teaser, then the article link. The article's og:image is the same card at 1200x630, so link previews match.
- Card layout, always the same: our logo mark (ringed planet with signal arcs, no background) followed by the "Science Messenger" wordmark (white + sky blue), between two thin brand-blue rules on top, a big white serif headline, one smaller grey teaser line under it, and the story's photo below fading into black. No text label, photo credit or watermark; the logo + name badge is the only branding.
- Card text lives in `tools/stories.json` as `"card": {"title": ..., "sub": ...}`:
  - `title`: max 60 characters, punchy, clickbaity tease of the most surprising true detail (e.g. "Physicists hunted this for 40 years. Now they see it").
  - `sub`: max 90 characters, one line that adds a concrete fact or a hook the article pays off (e.g. "A trial of 1,880 people has an answer, and it comes with a catch").
  - Both must be literally true and delivered by the article; don't copy the source's headline. The Limits below apply to card text too.
- Don't change the layout per post. If a crop hides the subject, set `"focus_y"` (0 = top, 1 = bottom) in the story's `card`. If the photo has text baked in (credits, captions, labels), cut it out with `"crop": [left, top, right, bottom]` (fractions); no credit text may show on a card.

## Schedule
- One post every 4 hours, 24/7: 00:00, 04:00, 08:00, 12:00, 16:00, 20:00 local (UTC+2), which is 6 posts a day.
- Schedule in the Meta Business Suite Planner. Fill the next empty slot and never stack two posts in one slot.
- Start right away: when a new batch of posts is approved, publish the first one immediately (Publish, not Schedule), then schedule the rest one per 4-hour slot after it.
- No gaps: the page should never go more than 4 hours without a post. Keep the queue booked at least 2 days ahead, and when it's about to run out, add new stories and posts.
- Never boost a post (that's a paid ad). Dismiss the Boost pop-up with "Maybe later".

## Limits
- No overstating: don't say "cure", "proves" or "breakthrough" unless the article quotes an expert saying it. Mouse studies are mouse studies.
- No engagement bait like "Comment YES", "Tag a friend" or "Share if you agree". Facebook demotes posts that ask for reactions or shares.
- Draft the posts in fb-queue.md and get approval before scheduling.
