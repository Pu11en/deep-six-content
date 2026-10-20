# Fast-scene pacing research (19 Oct 2026)

**Short answer:** the fast narrated shorts show a new picture every 0.6 to 2 seconds, and something on screen moves almost all the time. Blog advice ("change something every 3 to 5 seconds") is about 3 to 8 times slower than the fastest examples and cites no data.

## What the measurements say

- **Fastest (Zack D. Films Shorts):** a new shot about every 0.6 to 0.7 s, one shot per 1 to 3 spoken words. A small caption names what is on screen. The narration runs about 3 words per second (YouTube auto-captions: 92 and 84 words in 30 s), so about 2 words per shot. Up to 62% of the picture changes within half a second.
- **Flat cartoon (Kurzgesagt Shorts):** a new prop, label or scene about every 1 to 1.5 s in the hook, then 2 to 4 s per scene with things morphing inside the scene. Closest in look to code-drawn art.
- **Cut paper:** a new paper page about every 2 s with a new paper piece landing about every 0.5 s, or a torn-paper reveal about every 1.2 s.
- **Slow contrast:** the MinuteEarth stick-figure Short holds one static scene for 8 s and about 0% of the picture changes. It matches the problems listed for the rejected test (too little motion, too few scenes). Use it only as "what to avoid".
- **Cut counts mislead.** ffmpeg finds only 0 to 3 hard cuts in 10 s on clips that visibly change picture every second, because they use dissolves, zooms, morphs and camera moves. Count visual beats (new shot, scene, page, prop, label), not cuts.

Medians over the 12 clips below: ffmpeg hard cuts (threshold 0.30) give 1 cut in the first 10 s and an average shot of 8.75 s. By eye, the median is 3 scene changes in the first 8 s, about 2.0 s per scene, and 1.5 s per scene for the six narrated Zack and Kurzgesagt Shorts. Fastest: 0.62 s per scene.

## Targets these numbers suggest for our animation (a reading of the data, not a rule)

- A new scene or shot at least every 2 s; 0.7 to 1.5 s in the fast stretches.
- Something new on screen (word, prop, paper piece, label) about every 0.5 s.
- One picture per 1 to 3 spoken words, and the caption names what is shown.
- Motion in every frame. For flat cartoon or paper looks, about 10 to 20% of the picture changes within 0.5 s; Zack-style camera work reaches 25 to 60%.
- Move to the next scene with a transition that moves (camera push, torn-paper reveal, morph), not a pause.

## Top links, ranked by use to us

"Hard cuts" is ffmpeg scene detection at 0.30 / 0.20 in the first 10 s. "Avg shot" is the first-30-second average from those cuts. "By eye" is counted from the contact sheet. "Picture change" is the median share of the picture that differs 0.5 s later. Found by: **crawler** = MacBook crawler search result; **yt-dlp** = local yt-dlp YouTube search or channel Shorts list.

1. **[What Happens To Bugs When You Mow?](https://www.youtube.com/watch?v=esR-EXzvckw)** — Zack D. Films, YouTube Short, 9:16, 35 s. Found by yt-dlp.
   Hard cuts 1 / 4. Avg shot 15.0 s / 4.3 s. By eye: 12 scene changes in 8 s (0.6 s each). Picture change 62%.
   Borrow: one new picture per 1 to 3 spoken words, held under a second, caption naming it. Bugs are our topic.
2. **[Ants Form A Chain To Raid A Wasp Nest](https://www.youtube.com/watch?v=dxmQDoiHVnc)** — Zack D. Films, Short, 9:16, 30 s. Found by yt-dlp.
   Hard cuts 0 / 0. Avg shot 14.8 s / 9.9 s. By eye: 11 changes in 8 s (0.7 s each). Picture change 25%.
   Borrow: keep one subject (ants) but change the angle on every phrase; caption chunk equals shot.
3. **[The Deadliest Thing in Your Kitchen](https://www.youtube.com/watch?v=2cK8l5Yg5w8)** — Kurzgesagt, Short, 9:16, 67 s. Found by yt-dlp.
   Hard cuts 3 / 3. Avg shot 3.75 s (shortest 0.67 s). By eye: 5 scene changes plus 3 label pops in 8 s, about one beat per second. Picture change 17% (45% in the first 8 s).
   Borrow: a new flat-colour prop or label every 1 to 1.5 s, each with a quick animated transition and a background colour change.
4. **[The Hunt for the Perfect Croissant, Paris 1905 (paper collage)](https://www.youtube.com/watch?v=e7jJn8Iafgg)** — onlyone, YouTube video, 16:9, 60 s. Found by yt-dlp.
   Hard cuts 4 / 6. Avg shot 2.0 s / 1.5 s. By eye: 3 torn-paper page changes (about every 2 s) plus about 12 paper pieces landing in 8 s. Picture change 18.5%.
   Borrow: page-by-page scenes with pieces landing one at a time on each noun; pins, tape, stamps and string as animated connectors. Looks AI-made and has 89 views: use for look and rhythm only.
5. **[Outer Space | Collage Animation](https://www.youtube.com/watch?v=XAm4i1X7L_Y)** — sabstabs, YouTube video, 16:9, 22 s. Found by yt-dlp.
   Hard cuts 12 / 18. Avg shot 1.4 s / 1.0 s. By eye: about 6 changes in 8 s (1.2 s each). Picture change 9% (27% in the first 8 s).
   Borrow: torn-paper reveal as the scene transition; one new collage image about every 1.2 s.
6. **[Queen Ant Clones Another Species](https://www.youtube.com/watch?v=NXhKuMQRAZ4)** — Kurzgesagt, Short, 9:16, 69 s. Found by yt-dlp.
   Hard cuts 0 / 0. Avg shot 10.0 s. By eye: 2 scene changes in 8 s (4.2 s title hook, then about 2 s per scene). Picture change 12%.
   Borrow: a name label pops on with each new animal; about 2 s scenes after a short hook.
7. **[How I Use Codex to Build Vox-Style Explainer Videos](https://www.youtube.com/watch?v=Fjns2RO9t8Q)** — AI for Real Life, Short, 9:16, 44 s. Found by crawler.
   Hard cuts 0 / 2. Avg shot 30.0 s / 5.0 s. By eye: 1 scene change (at 6.5 s) but a paper or label beat every 0.5 to 1.5 s. Picture change 7%.
   Borrow: layered paper planes with parallax and small paper props moving in on every beat; zoom-through transition. Its 6.5 s first scene is too slow for us.
8. **[How Electrical Outlets Work](https://www.youtube.com/watch?v=0BZ1C83I2R4)** — Zack D. Films, Short, 9:16, 24 s, 35M views. Found by yt-dlp.
   Hard cuts 0 / 0. Avg shot 24.0 s / 12.0 s. By eye: 4 scene changes in 8 s. Picture change 54%, the highest of the set.
   Borrow: switch scenes by moving the camera through an object; never hold a still frame.
9. **[Ethan Mollick: recursion video made by Claude Opus 5.5](https://x.com/emollick/status/2103688362960019567)** — X video, 16:9, 75 s. Found through the awesome-opus5-5-videos Explainers list; the crawler read its prompt file.
   Hard cuts 2 / 3. Avg shot 6.0 s / 5.0 s. By eye: 3 scene changes in 8 s, words popping in every 0.25 to 0.5 s. Picture change 9%.
   Borrow: word-by-word text timed to speech; 0.3 s flash cards as punctuation. The post says the prompt asked for "fast moving".
10. **[Can Earth Run Out of Water?](https://www.youtube.com/watch?v=tZ8i1RxGSYM)** — Kurzgesagt, Short, 9:16, 78 s. Found by yt-dlp.
    Hard cuts 2 / 2. Avg shot 6.0 s. By eye: 3 scene changes in 8 s. Picture change 12%.
    Borrow: change a scene in place (colour or size morph) to keep movement without new art. Typical Kurzgesagt pace.
11. **[The Secret of the World's Most Famous Diamond (Paper Cut Animation)](https://www.youtube.com/watch?v=CssQtDTrD90)** — PaperCraft Animations, YouTube video, 16:9, 40 s. Found by yt-dlp.
    Hard cuts 1 / 2. Avg shot 7.5 s / 6.0 s. By eye: no scene change, about 6 big paper motions in 8 s. Picture change 4%.
    Borrow: paper behaviour: slide in from the edge, fold, split, shards falling. Probably AI-generated with 28 views: use for motion ideas only.
12. **[Yes, mosquitoes ARE out to get you.](https://www.youtube.com/watch?v=fUBRGTKInbI)** — MinuteEarth, Short, 9:16, 81 s. Found by yt-dlp.
    Hard cuts 1 / 1. Avg shot 10.0 s. By eye: 0 scene changes, 2 figures drawn in. Picture change 0%.
    Borrow: nothing. This is what to avoid.

Same pest as our episode: [TED-Ed, life of a fire ant](https://www.youtube.com/watch?v=RNdouBNrnM0) (16:9). Its first 30 s are a logo, a quote, then a slow landscape (0.3% picture change). Use for topic facts only, not pacing.

Other clips were measured but not chosen; see `also_measured` in `measurements.json`. The crawler's own ant leads (three YouTube Shorts and an ant animation) turned out to be live-action footage or slow intros, not fast animated explainers.

## Technique notes per clip

The same notes, with more detail, are in `measurements.json` under `technique`. Contact sheets (first 8 s, one frame per 0.5 s) are in `contact-sheets/`, internal reference only.

- Zack Shorts: captions of 1 to 3 words, bottom centre, changing with the speech; each shot shows the named thing; transitions are camera moves and quick dissolves.
- Kurzgesagt Shorts: small centred captions about every 1 s; swipes and zooms instead of hard cuts; a new background colour per scene; name labels pop on.
- Paper clips: pieces land one at a time; torn edges, tape, pins and string; page changes about every 2 s.

## How it was measured

- Download: `yt-dlp -f "worst[height>=360]/worst" --download-sections "*0-30"`, 360p or lower, first 30 s. On 23 of the YouTube clips ffmpeg got HTTP 403 with the default client; the same command with the public `mweb` client (`--extractor-args youtube:player_client=mweb`) worked each time (no login, no cookies).
- Hard cuts: `ffmpeg -i v.mp4 -vf "select='gt(scene,T)',showinfo" -f null -` with T = 0.30 and 0.20, cut times from `pts_time`.
- Picture change: share of pixels whose colour differs by more than 40/255 between frames 0.5 s apart (48 px wide, 10 fps).
- Contact sheets: `fps=2`, 240 px tall, 4x4, first 8 s. Scene changes and element beats were counted by eye and checked on a 0.25 s sheet; read them as plus or minus 1.

## Limits

- ffmpeg counts hard cuts only. Use the by-eye numbers for real scene rate.
- By-eye counts cover the first 8 s only. Only the first 30 s of each video was downloaded, at low resolution; hooks and intros can differ from the rest.
- Audio was not listened to. Narration is confirmed only for the two Zack bug Shorts (auto-captions, about 3 words per second). For other clips it is inferred from burned-in captions or not assessed.
- Views show popularity, not effectiveness. Three of the four paper examples are 16:9, and three look AI-made with small audiences (28 to 1,332 views).
- Blog guidance numbers come from vendor blogs with no cited data (details below).

## Crawler record (MacBook crawler, client `imac-research`)

- Job `05d97f54-c79e-4625-b757-97c9376b0ecc`, status finished. Session `e5439860-a052-4860-b74f-fbb586d23a2d`.
- Used: 6 searches, 20 page attempts, 67 steps, 0 model calls, 45 s active. Ceilings: 6 searches, 30 pages, 900 s, 80 steps. The API rejected steps above 80 (90 was requested), so the ceiling is 80.
- Read 15 pages: the awesome-opus5-5-videos list, two of its prompt files and the Skillry gallery; five explainer skills or guides (one for papercraft); six pacing pages. 17 evidence quotes were saved, each with a caller support check (not independent verification).
- Pacing guidance found: OpusClip's TikTok article says "pattern interrupts every 4 seconds" and its Shorts article says "one cut every 2-4 seconds"; ByteCap says a visual shift every 3 to 5 seconds; a papercraft skill says 2 to 4 s per shot for 15 s videos. None cites a dataset.
- Failed or thin: four YouTube watch or channel pages returned `document_too_large`; github.com returned an access page (the raw README worked but was cut at 24,000 characters, before its Explainers section, so those 16 links were listed from a local copy); one article page held no usable figure.
- Files here: `session.json`, `approved-plan.json`, `request.json`, `job.json`, `actions/` (every request and receipt), `sources/` (page snapshots), `capabilities.json`, `crawler_client.py`.
