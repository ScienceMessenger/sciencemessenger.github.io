# Story sources

Science Messenger takes its story ideas from the biggest science news pages on Facebook (the **reference pages** below). Facts still have to match the paper or the official release behind each story.

## Two-source rule (hard rule)
- Only use a topic when **at least 2 different reference pages** covered the same finding (same paper, mission or event). One page alone is not enough, however good the story.
- List every reference page that covered it under `sources`, plus the paper (DOI or journal page) or the agency release when there is one.
- Rewrite in our own words. Headlines should make people curious and want to click, but they must stay literally true (see FACEBOOK.md).

## Reference pages (story discovery)
The most-followed science news pages on Facebook, and the sites behind them:
- [ScienceAlert](https://www.sciencealert.com/)
- [IFLScience](https://www.iflscience.com/)
- [SciTechDaily](https://scitechdaily.com/)
- [Phys.org](https://phys.org/) / [Medical Xpress](https://medicalxpress.com/)
- [ScienceDaily](https://www.sciencedaily.com/)
- [Live Science](https://www.livescience.com/)
- [Space.com](https://www.space.com/)
- [New Scientist](https://www.newscientist.com/)
- [Scientific American](https://www.scientificamerican.com/)
- [Popular Science](https://www.popsci.com/)
- [National Geographic](https://www.nationalgeographic.com/science)
- [Smithsonian Magazine](https://www.smithsonianmag.com/category/science-nature/)
- [NASA](https://www.nasa.gov/news/)
- [Nature News](https://www.nature.com/news) and [Science News (AAAS)](https://www.science.org/news)

## Picking topics
Take stories that are both **solid** and **interesting**. If one of the two is missing, skip it.
- **Solid:** covered by at least two reference pages (above), and traceable to a peer-reviewed paper or an official agency release. No preprint-only stories unless they're clearly labeled as not yet peer reviewed.
- **Interesting:** there's a clear "what did they find" hook and a reason the reader should care.
- **Skip:** single-study miracle cures, "X causes cancer" from small or animal-only studies, company press releases with no data, and anything that only appears on tabloids or aggregators.
- **Space first (~75%):** about 3 of every 4 stories in each batch (and 3 of every 4 Facebook posts) should be space news: astronomy, planets, missions, telescopes, rockets, astronauts, asteroids, cosmology. Only interesting, solid ones count; never pad with a weak space story. If there aren't enough good space stories, fill the rest with the best other science rather than lowering the bar. When scheduling, spread the non-space posts out instead of bunching them.
- **Top priority: aliens, life, new physics.** Stories about possible alien life, life's origins or habitable worlds (biosignatures, organics, oceans on moons, life's building blocks in space) and possible new physics (dark energy/matter surprises, broken Standard Model, cosmology tensions) go first whenever they're solid. They still need the two-source rule and must not overstate: "hints of", never "found aliens"; fringe claims (e.g. an asteroid being artificial) are labelled as unsupported or left out.
- **Picture:** a public-domain or CC0 Commons image that shows the subject (the telescope, the animal, the organ, the place).

## Writing rules: accurate, own words, no copyrighted material
- Rewrite every story completely in our own words. Never copy or lightly reword a source's sentences.
- Combine facts from at least 2 reference pages plus the paper or release, and list them all under sources. Link the paper by DOI or journal page when there is one.
- State the limits: sample size, animal vs human, observational vs causal, preprint vs peer reviewed. Name the journal and the lead institution.
- No hype words ("breakthrough", "cure", "miracle", "proves") unless a named expert in the sources says so, and then quote them.
- Quotes: only short ones the sources actually contain, attributed, and at most one or two per story. Paraphrase everything else.
- Images: **public domain or CC0 only** (no CC BY, CC BY-SA or any license that requires attribution, and nothing copyrighted). Use Wikimedia Commons files tagged PD (e.g. PD-USGov/NASA/NOAA, PD-old) or CC0. Never use photos from news sites, journals, social media or agencies outside Commons. No credit text on images or share cards.
- Images are **always self-hosted** under `img/`: run `python tools/fetch_images.py` after `fetch_image_meta.py`. Never hotlink upload.wikimedia.org (Facebook's crawler gets 403, so link posts lose their picture). `build.py` fails if an image is missing or not PD/CC0.
- Headlines and decks are ours. They can pose a question or tease the finding, but they must be literally true and must not overstate the result. Don't reuse the source's headline.

## Legal rules (hard rules)
Everything we publish must be legal to publish. When in doubt, leave it out.
- **Text: facts only, never expression.** Facts and findings can't be copyrighted, but an outlet's wording can. Write every sentence from scratch. No copied or lightly reworded sentences, no translated passages, and don't follow one article's structure paragraph by paragraph. Combine facts from 2+ sources so no story is a rewrite of a single article.
- **Quotes:** at most two short quotes (under 25 words each) per story, only ones the sources really contain, attributed to the speaker and the outlet that published them.
- **Headlines and decks are ours.** Never reuse a source headline.
- **Images: public domain or CC0 only, self-hosted.** Never take images from the reference pages, news sites, journals, Facebook, Google Images or stock sites, even "just as a thumbnail". Use Wikimedia Commons files whose page shows PD or CC0 (check the license tag on the file page, not a search result). NASA/NOAA/USGS imagery on Commons tagged PD-USGov is fine; ESA, ESO and most university images are CC BY and are **not** allowed. No logos or trademarks of other outlets.
- **Link, don't copy.** Sources are credited by name and link under `sources`. Never republish a whole article, figure, chart or table from a source; describe the result in our words.
- **No defamation or false claims.** Every claim must be literally true and supported by the sources. Don't accuse named people of wrongdoing unless an official source states it. No made-up quotes, numbers or experts.
- **Health:** report findings, never give personal medical advice. Say when results are from animals, cells or small studies.
- **Clickbait limit:** curiosity headlines are fine; misleading ones are not (they also break Facebook's rules and EU/UK consumer law on misleading content). The article must deliver what the headline promises.

## Verification (primary material)
Check facts against the paper or agency release behind the story: journals (Nature, Science, Cell, The Lancet, NEJM, PNAS, JAMA, The BMJ, Physical Review Letters, The Astrophysical Journal and others), agencies (NASA, ESA, NOAA, USGS, WHO, CDC, NIH, CERN, ESO), and [EurekAlert!](https://www.eurekalert.org/) for the institution's release. [Retraction Watch](https://retractionwatch.com/) for surprising claims.

## Verification checklist
1. Find the paper or official release and read at least the abstract and methods summary.
2. Confirm the publication date and that it's peer reviewed (or say clearly that it isn't).
3. Check that the numbers in the story match the paper, not just the press release.
4. Look for an independent expert comment in a credible outlet and include their view when there is one.
5. Check Retraction Watch for the authors or the paper if the claim is surprising.
