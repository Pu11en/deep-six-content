# Deep Six Content: workspace rules for agents

Goal right now: find a flow that makes GOOD content, cheaply. Everything is an experiment. No fixed creative rules. Judge by how it looks. Drew wants NO spending for now (16 Oct 2026): ask before any paid API call.

## Video format

All videos we create for Deep Six must be **9:16 vertical**, including previews and final exports.

## DISPLAY RULES (Drew, 16 Oct 2026). Read first. Overrides the global "open a note in Markdown Preview" rule.

The pane beside chat is for CONTENT only: images, videos, and content text Drew needs (prompts, scripts, captions, post copy).

- Everything goes on `BOARD.md`. Nothing else opens in Zed: no notes, research, plans, specs, code, or separate image tabs.
- Every image or video you make goes on the board right away, without being asked: `tools/show <file> "short caption"`. Videos get a moving preview.
- Content text (a prompt, a script, a caption) goes on the board too, designed for a human: a clear title, short lines, big gaps, the picture next to it. Never walls of text, tables of jargon, or file paths.
- Working notes (research, plans, logs) are fine as agent files. Write them; never display them.
- Open the board only if it is not already open, at most once per chat:
  `python3 /home/drewp/main-projects/zed-setup/scripts/show-in-zed.py BOARD.md`
- Explain things in chat, in short plain words. Never "see the note".
- Side-by-side comparisons (`convert a.png b.png +append compare.png`) go on the board.

## Paid AI keys (ask Drew before any use)

- Key: `DEEPSIX_GOOGLE_API_KEY` in `~/.config/allwork/keys.env`. Load it with
  `set -a; . <(grep '^DEEPSIX_GOOGLE_API_KEY=' ~/.config/allwork/keys.env); set +a`
- Never print the key or copy it into this folder.
- Models on the key (checked 16 Oct 2026): Nano Banana image (gemini-3-pro-image, gemini-3.1-flash-image, gemini-nano-banana-2.1), Veo 3.1 (fast, lite), Gemini TTS.
- KIE (200+ image/video/music/voice models): `DEEPSIX_KIE_API_KEY` in the same file. Same rules. Credits left after 16 Oct tests: 6195.7. KIE agent skills (`npx skills add https://kie.ai`) not installed yet.
- If Drew OKs spending: one test at a time, cheapest model that works. Log every paid call in `01-content/experiments/cost-log.csv` (55 cents spent on 16 Oct).
- Make images with `tools/gen-image <prompt.txt> <out.png> <reference.png...>` (Nano Banana 2.1, about 3 cents each; `ASPECT=9:16` for vertical). It logs cost and puts the image on the board.

## How to prompt for on-brand images

- Read `01-content/brand/style-spec.md`. Attach `01-content/brand/fun-fact-friday-spider.png` as reference.
- Sort every element into PRESERVE (style, mascot, layout), REPLACE (pest, scene, exact text), ADAPT (props). Method from Drew's Dremes pipeline.

## Where things go

- Before drafting each new episode, check `01-content/source-log.md`. Log every factual/content source used, including drafts and fact checks, and the episode’s topic. Do not reuse a content source for another video unless Drew approves. Same-episode revisions may reuse it. Track reusable visual/style references separately.

- `01-content/brand/` brand references and the mascot.
- `01-content/experiments/<date>-<name>/` each content test: prompt, outputs, short note.
- `01-content/research/` research notes.
- `board-previews/` GIF previews made by `tools/show` (created when needed).
