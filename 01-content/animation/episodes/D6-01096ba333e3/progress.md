# Ensign wasp video (D6-01096ba333e3): progress

**Status: done. Drew approved the final video ("yes good i like it", 2026-10-20). Recorded with `tools/d6 complete-video ... --final`.** Desktop: `Deep Six - Ensign Wasp v1.mp4` (internal file `full/renders/ensign-wasp-v3-final.mp4`).

## Done (October 20, 2026)

- Approved MP3 verified unchanged (Chris, 48.35 s, sha `48b3cd7c…`). Words unchanged.
- Anatomy checked against UF/IFAS IN319, TAMU City Bugs, UF/IFAS EENY-141, UMN Extension and a Lander University page. Facts and limits added to [science notes](../../science-notes.md); sources logged in [source-log.md](../../../source-log.md) under "Drawing anatomy checks".
- New drawings, cut-paper style C, in new modules only (no fire-ant file changed):
  - `scenes/wasp-kit.mjs`: ensign wasp (walk, flag-like abdomen on a stalk, fold for pupa), wasp egg, larva with toothed jaws, jaw close-up, egg case (outside, cut open with 16 eggs, exit hole), American cockroach (side and top views), pennant, lime target, flashlight hand.
  - `scenes/home-world.mjs`: under-sink cabinet (crack, gap under the wall, gap round the drain pipe, warm supply line, dripping trap, damp patch), the floor up close, the floor from above, flashlight beam.
- Director step: [shot list](full/shot-list.json), 36 shots and 96 beats, longest shot 1.94 s. Caption groups refined in `full/words.json` (machine groups kept in `full/words.aligned-groups.json`).
- Animator step: `scenes/d6-01096ba333e3-full.mjs`; beat sheets checked by eye and fixed (eggs looked like teeth, sink shots too wide, jaw highlight hidden).
- Outro: approved `outro-animation-v2.mp4` with its cream wipe over the last teaching frame (starts 44.133 s, after "roaches." ends at 44.13 s). Only the mascot's opening scan is shortened, by 0.30 s (9 frames: the scan's 24-to-30 fps duplicate frames plus two scan frames). Logo settles 46.867 s, before "Deep" at 46.91 s. Settled logo held 1.0 s after the last word. Top caption as in the approved outro. Details: [outro-retime.json](full/outro-retime.json), made by `full/prep-outro.py`.

## Renders

- v1 (`full/renders/ensign-wasp-v1-final.mp4`): all format and audio checks pass; picture change 22%. One 0.37 s still moment at 13.3 s (target 0.35 s). Not delivered.
- v2: fixes from watching v1 filmstrips (closer on the larva at 12.5 to 14.8 s, drift through short holds, egg-case glow, wasp framing at 32 s). Render stopped by a crash; `full-v2.partial.mp4` left as is.
- v3 (`full/renders/ensign-wasp-v3-final.mp4`, delivered as "v1"): same code as v2. Checks:
  - 1080x1920, 30 fps, 1472 frames; video 49.067 s, audio 49.066 s; both start at 0.
  - Audio is the approved MP3 decoded unchanged: lag 0 ms, correlation 0.99997, level change -0.01 dB, then silence. [checks](full/renders/ensign-wasp-v3-final.checks.json)
  - Lesson: longest still 0.23 s, picture change 22% (targets 0.35 s, 15%). The only longer still is the approved outro's logo hold, 47.1 to 49.0 s. [motion](full/renders/ensign-wasp-v3-final.motion.json)
  - Frames pulled on 28 key words show the right picture and highlighted word: [sheet](full/renders/ensign-wasp-v3-keywords.png).
  - Desktop copy verified by checksum; no player opened: [record](full/desktop-copy.json).

## Next

Nothing left for this video. Approval recorded in `full/renders/full-v3.review.json` and in the d6 flow state. No push or publishing.

## Rebuild

```
cd 01-content/animation
python3 episodes/D6-01096ba333e3/full/build-shot-list.py   # shot list and caption groups
python3 episodes/D6-01096ba333e3/full/prep-outro.py        # outro frame cache (1.2 GB, git-ignored)
node render-shots.mjs episodes/D6-01096ba333e3/full/scene.json --sheet
node render-shots.mjs episodes/D6-01096ba333e3/full/scene.json   # new revision in scene.json first
python3 episodes/D6-01096ba333e3/full/finish.py v3     # revision in scene.json; never overwrites
```
