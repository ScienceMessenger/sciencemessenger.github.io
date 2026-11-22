# Facebook post rules

## Goal
Get people to click through to the full story. Make them curious about the finding without misleading them about it.

## How
- Open with the most surprising true detail, then leave the explanation (how they found it, what it means) for the article.
- Curiosity phrasing is fine ("Astronomers expected a dead star. The data showed something else."), but every claim in the post must be literally true and match the paper.
- Keep it short: 1–2 lines, then the link.

## Image post style (every post)
- Every post shows the story's news card. Two ways, both fine:
  - **Link post (default, works in the built-in browser):** caption = the 1–2 line teaser + article link. Facebook uses the article's og:image, which is the card at 1200x630 (`img/og/<slug>.jpg`). In the Business Suite composer, type the caption and link, then click the link (chain) icon so the preview attaches; check the preview shows the card before scheduling.
  - **Photo post:** upload `img/fb/<slug>.jpg` (1080x1350) with the same caption. Needs a real file upload (Claude in Chrome's file upload, or by hand); the built-in browser cannot attach files.
- After changing a card, re-scrape the article URL in Facebook's Sharing Debugger ("Scrape Again") before posting. Posts already created keep the preview they were made with; to change one, re-create it and delete the old one.
- Card layout, always the same: our logo mark (ringed planet with signal arcs, no background) followed by the "Farlight" wordmark ("Far" white + "light" sky blue), between two thin brand-blue rules on top, a big white serif headline, one smaller grey teaser line under it, and the story's photo below fading into black. No text label, photo credit or watermark; the logo + name badge is the only branding.
- Card text lives in `tools/stories.json` as `"card": {"title": ..., "sub": ...}`:
  - `title`: max 60 characters, punchy, clickbaity tease of the most surprising true detail (e.g. "Physicists hunted this for 40 years. Now they see it").
  - `sub`: max 90 characters, one line that adds a concrete fact or a hook the article pays off (e.g. "A trial of 1,880 people has an answer, and it comes with a catch").
  - Both must be literally true and delivered by the article; don't copy the source's headline. The Limits below apply to card text too.
- Don't change the layout per post. If a crop hides the subject, set `"focus_y"` (0 = top, 1 = bottom) in the story's `card`. If the photo has text baked in (credits, captions, labels), cut it out with `"crop": [left, top, right, bottom]` (fractions); no credit text may show on a card.

## Schedule
- Audience is American, so slots are set in US Eastern time. **3 posts a day**, every day:
  - Morning **9:00 AM ET** (6 AM PT) = **16:00** local (UTC+2)
  - Lunch **1:00 PM ET** (10 AM PT) = **20:00** local
  - Evening **9:00 PM ET** (6 PM PT) = **04:00** local, the next calendar day
- These conversions hold while the US is on EST (until 14 Mar 2027). When daylight saving changes on either side, recompute local times so the ET times stay fixed.
- Schedule in the Meta Business Suite Planner. Fill the next empty slot and never stack two posts in one slot.
- When a new batch of posts is approved, schedule it into the next free slots. Don't publish outside these three slots.
- Keep the queue booked at least 2 days ahead (6 posts), and when it's about to run out, add new stories and posts.
- Once the page has followers, check Insights in Meta Business Suite ("when your audience is online") and shift the slots to match.
- Never boost a post (that's a paid ad). Dismiss the Boost pop-up with "Maybe later".

## Limits
- No overstating: don't say "cure", "proves" or "breakthrough" unless the article quotes an expert saying it. Mouse studies are mouse studies.
- No engagement bait like "Comment YES", "Tag a friend" or "Share if you agree". Facebook demotes posts that ask for reactions or shares.
- Draft the posts in fb-queue.md and get approval before scheduling.
