# Task: make the ensign-wasp video (approved MP3 to finished MP4)

Make this video yourself with Opus 5.5 at max effort, the same way the approved fire-ant video was made. Drew's bar: as good as `Deep Six - Fire Ants Full v2` on his Desktop. The script and MP3 are approved. Do not change the words or the audio.

## What is ready

- Episode `D6-01096ba333e3`. Approved script, limits and sources: `01-content/approved-narrations/D6-01096ba333e3.md`.
- Approved MP3 (Chris, 48.35 s): `01-content/audio/D6-01096ba333e3/full-chris-01/ensign-wasp-chris.mp3`. Check it with `python3 tools/d6_audio.py 01-content/audio/D6-01096ba333e3/full-chris-01/comparison.json --action verify`.
- Word timing is done: `01-content/animation/episodes/D6-01096ba333e3/full/words.json`. All 138 words matched; 48 caption groups.

## Read first, in order

1. `01-content/animation/VIDEO-FLOW.md`: recipe and quality bar.
2. `01-content/animation/HARNESS-NOTES.md`: what worked and what the checks caught.
3. `01-content/animation/KIT-API.md`, `choreography/director-prompt.md`, `choreography/animator-prompt.md`, `science-notes.md`.
4. `01-content/outro/APPROVED-OUTRO.md` and `01-content/outro/TRANSITION-INSTRUCTIONS.md`.

## New pest: build researched drawings first

The kit has no wasp, cockroach, egg case or indoor set. Check anatomy against the approved sources (UF/IFAS IN319 on Evania appendigaster; the TAMU City Bugs articles), then draw in cut-paper style C:

- Ensign wasp: small, black, flag-like abdomen on a thin stalk held high and bobbing, long hind legs.
- American cockroach and its egg case: dark brown, purse-shaped, ridged seam.
- Egg-case cutaway: a dozen or more eggs in rows; the young wasp with pointed, toothed jaws; the adult cutting a small round hole and leaving.
- A home set: cracks and small gaps, warm damp places such as under a sink.

Add new modules; do not change the fire-ant files. Add the anatomy facts and links to `science-notes.md`. Keep the script's limits: a wasp sighting is a clue, not proof of an infestation; not every cockroach species; no treatment advice.

## Outro

Chris says the sign-off inside this MP3. Lesson ends at 44.13 s, "Helping" starts at 44.61 s, "Deep" at 46.91 s, last word ends at 48.06 s.

- Use the approved outro animation, `01-content/outro/assets/outro-animation-v2.mp4` (silent), with its cream-paper wipe.
- The logo must land at or before "Deep". Chris reaches "Deep" about 0.25 s sooner than the approved template. Trim only opening scan time. Keep the jump, swing and reveal at designed speed.
- Hold the settled logo about 1 s after the last word.

## Output and delivery

- 1080x1920, 9:16, 30 fps. Audio is the approved MP3, unchanged. Run the checks in VIDEO-FLOW step 5.
- Copy the final MP4 to Drew's Windows Desktop as `Deep Six - Ensign Wasp v1.mp4`. Never open a video player.
- Put it on BOARD.md with `tools/show` (moving preview). Open nothing else in Zed.
- Keep a short progress note at `01-content/animation/episodes/D6-01096ba333e3/progress.md`.
- After Drew approves the final MP4, record it: `tools/d6 complete-video D6-01096ba333e3 <mp4> --audio-manifest 01-content/audio/D6-01096ba333e3/full-chris-01/comparison.json --final`.

## Rules

- No paid API calls without Drew's OK. No push.
- Ask Drew only for real choices, as multiple choice.
