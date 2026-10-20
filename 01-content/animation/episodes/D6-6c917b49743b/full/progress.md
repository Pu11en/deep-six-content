# Full video progress

**Full video v2 is done and on Drew's Desktop as `Deep Six - Fire Ants Full v2.mp4`; review pending.** It covers the whole 78.6-second approved narration plus a 0.6-second end hold, in cut-paper style C. Drew approved hook v1 on October 19 ("It's really good ... I do like everything about it") and asked for the full video made the same way.

## What it shows

- 0 to 9 s: the approved hook, unchanged. Its frames are pixel-identical to hook v1.
- 9 to 16 s: a nest cutaway; busy chambers; workers walking outside on the surface; a nursery deep underground.
- 16 to 27 s: eggs, larvae and pupae up close; a lime loop names them "brood"; an egg hatches, the larva grows, flips into a pupa, then a pale adult that darkens and walks out.
- 27 to 46 s: why conditions matter. Cold and wet: rain, brood carried up into the mound, sunbeam warming it, deep soil flooding. Hot and dry: big sun, cracked mound, cool moist deep chambers, brood carried down.
- 46 to 58 s: workers carrying brood; a lime picture frame hops around the nest as the nursery moves; one pinned room gets a purple X.
- 58 to 68 s: back in the yard: the mound does not show where the brood is; the busy colony is covered and the surface looks quiet.
- 68 to 79 s: a homeowner, a missing mound, a magnifier x-ray, a gauge with no reading, question marks over the colony and its young.

## How it was made

Same flow as the hook: word times (`words.json`), director shot list (`shot-list.json`, 76 shots, 123 beats), animator code, beat-sheet self-checks.

- Code: `scenes/d6-6c917b49743b-full.mjs` joins the hook module and `scenes/d6-6c917b49743b-body.mjs`.
- New sets: `scenes/nest-world.mjs` (cutaway with weather, water, heat, brood, ants) and `scenes/yard-world.mjs` (yard, homeowner, bubble, gauge, magnifier).
- New kit pieces in `scenes/paper-kit.mjs`: eggs, larvae (the approved style C larva), pupae, brood piles, ants carrying brood, pale newly emerged adults. The default ant is unchanged.
- Word times: words 0 to 28 reuse the hook's checked times; the rest are the median of three offline speech models, snapped to measured silences. All 211 words aligned.

Author: Opus 5.5 at max effort in this Claude Code session. No paid calls, no new audio, no installs.

## Self-check fixes before the full render

- Brood and life-cycle close-ups were too small; items now fill the frame and rest on the nursery floor.
- The surface-workers shot now features large ants walking on the lawn.
- A full lime loop vanished in this canvas library at exactly one turn; it now stops just short.
- The magnifier was missing in the homeowner shot; the gauge overlapped the homeowner; a tunnel ant poked above the quiet lawn. All fixed.

## Checks (`renders/full-v2.json`)

| Check | v2 |
|---|---|
| Size and rate | 1080x1920, 30 fps, 2,376 frames |
| Video, audio, container | 79.2 s each; both streams start at 0 |
| Longest near-still stretch | 0.33 s |
| Picture changing each half second (median) | 17% |
| Render time | 17 minutes |

- Video SHA-256 `c7ff2561764537bf68eef8b57a62ac3c5399e382f90baeec183e4620c825aa06`. Desktop copy verified by hash (`desktop-copy.json`). No player was opened.
- The hook section is bit-identical to approved hook v1 (decoded frames at 3.3 s and 6.64 s match exactly).
- Frames taken from the MP4 on "brood", "hatch", "waterlogged", "fixed", "ants" and "developing" each show that word's picture with the word highlighted.
- v1 was never shown to Drew. The agent's own check found holds still for up to 1 second and picture change at 14%, so v2 keeps the camera moving through every hold, adds drifting dust and clouds, and a scratching hand. `renders/full-v1.review.json` is marked superseded.

## Limits

- Word times are machine-aligned, not checked by ear.
- Brood piles in wide nest shots are small; close-ups carry the detail.
- Illustrative only: no depths, temperatures or nest map.
