# Cartoon reference update — October 16, 2026

Found two confirmed vertical character cartoons and one stronger ant-specific code example that is widescreen. Shortlist: [cartoon animation links](../cartoon-animation-links.md). Added to the top of BOARD.md; the earlier list remains below it.

## Verified references

| Reference | Published | Media dimensions / duration | Evidence and limits |
|---|---|---|---|
| [Snack cartoon — jackfriks](https://x.com/jackfriks/status/2103525576912855363) | 2026-09-25 | 1080 × 1920 / 35.266 s | Creator credits Opus 5.5. Metadata saved; sampled frames inspected from the public gallery preview. No source code inspected for this short; creator’s effort/time claims not independently verified. Comedy, not an educational lesson. |
| [Mailbox cartoon — jackfriks](https://x.com/jackfriks/status/2103132260589338762) | 2026-09-24 | 1080 × 1920 / 19.5 s | Creator explicitly says supplied app assets were used. Original poster inspected. Promo, not an educational lesson. No proof that its artwork was code-drawn. |
| [Ant colony — hanifproduktif](https://x.com/hanifproduktif/status/2102742924148830211) | 2026-09-23 | 1920 × 1080 / 32 s | Original post metadata, repository README, source header and render constants agree. Source imports Node canvas and ant/colony drawing libraries. Creator’s contact sheet inspected. Widescreen: style-only extra, not a qualifying vertical video. |

All three posts fall within September 16–October 16, 2026. Media metadata was retrieved through the public FXTwitter mirror of the original posts. Full X MP4 downloads returned HTTP 403; no claim that full videos were watched. Visual selection uses inspected posters/preview frames, repository contact sheet, creator statements, and linked catalog descriptions.

## Evidence

- [Candidate metadata](2026-10-16-cartoon-animation-candidates.json): mailbox, Wordfeel, paper-cut home, and other candidates.
- [Snack cartoon metadata](2026-10-16-cartoon-animation-evidence/dont-tell-her-metadata.json); [public preview](https://raw.githubusercontent.com/theolundqvist/frontier-games/main/media/dont-tell-her/preview.webp); [gallery description](https://github.com/theolundqvist/frontier-games).
- [Ant metadata](2026-10-16-cartoon-animation-evidence/ant-colony-metadata.json); [source excerpt](2026-10-16-cartoon-animation-evidence/ant-colony-source-excerpt.txt); [complete source](https://github.com/buildwithhanif/claude-animation-skill/blob/main/examples/ant-colony/film.mjs); [creator contact sheet](https://raw.githubusercontent.com/buildwithhanif/claude-animation-skill/main/docs/colony-contact.jpg).
- [Discovery collection](https://easyveo.com/claude-opus-5-5-prompts). Used to find originals, not as sole evidence of production method.

## Excluded from the shortlist

- Wordfeel: vertical, but mixes sitcom footage with animation; weaker match to a fully cartoon scene.
- Paper-cut home: vertical, but less like the expressive animal cartoons requested.
- Photosynthesis, dinosaur, pelican and bug cartoons: widescreen. Ant colony was retained as a clearly marked extra because its published code and subject are directly relevant.
- Cartoon workflow guide: a tutorial, with an embedded widescreen sample despite vertical instructions.

## Scope

No video made, software installed, money spent, or factual narration source added. These are reusable visual references only. The ant colony illustrates leafcutters; it does not establish facts about fire ants or other household ants. D6-ANT-001 still uses ANT-S001. All Deep Six previews and final exports remain 9:16.

## Production-method clarification

Drew reiterated that references should use the same code animation method: JavaScript, TypeScript, or equivalent. Updated the visible shortlist to distinguish the ant example’s published JavaScript from the two vertical cartoons’ unverified implementation. The mailbox example uses supplied artwork. Code origin is now an explicit selection requirement; no fully verified example in this shortlist satisfies both code provenance and native 9:16. The ant example is only a widescreen style reference.
