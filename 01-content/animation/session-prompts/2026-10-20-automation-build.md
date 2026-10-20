# Task: build the MP3-to-MP4 automation

Build the designed automation by growing `01-content/animation/make_video.py`. When Drew approves an MP3, the runner should make the finished video with as little hand work as the fire-ant and ensign-wasp videos needed. Opus 5.5 at max effort.

## Read first

1. `01-content/animation/AUTOMATION-DESIGN.md`: the agreed design and Drew's decisions.
2. `01-content/animation/VIDEO-FLOW.md` and `HARNESS-NOTES.md`: recipe, quality bar, problems the checks caught.
3. `01-content/animation/episodes/D6-01096ba333e3/progress.md`: the ensign-wasp video, made by hand on October 20 and approved by Drew ("yes good i like it").

## Lessons from the ensign-wasp run to build in

The hand-made scripts are in `01-content/animation/episodes/D6-01096ba333e3/full/`. Turn them into runner steps:

- **Outro fit** (`prep-outro.py`): start the approved cream wipe on the first frame after the last lesson word. Shorten only the reaper's opening scan (drop its duplicate frames, then thin scan frames evenly) until the logo settles at or before "Deep". Keep the jump, swing and reveal at designed speed. Hold the settled logo about 1 s after the last word. Fade the top caption before the logo flies into its spot.
- **Exact audio** (`finish.py`): the renderer fades the last 80 ms. Re-mux the approved MP3 unchanged under the picture, padded with silence, and check lag, correlation and level against the MP3.
- **Motion check** (`motion-check.py`): score the lesson separately. The approved outro's logo hold is a designed still and should not fail the video.
- **Key-word frames** (`keyword-frames.py`): one sheet of frames pulled from the MP4 on key words, for checking and for the board.
- **Crash safety:** a computer crash killed a render at frame 1200 of 1472. Run renders detached so a closed chat cannot stop them. On restart, move to the next revision automatically instead of stopping at the leftover partial file.
- **New pests:** the wasp, cockroach, egg case and under-sink drawings were built first in new modules (`scenes/wasp-kit.mjs`, `scenes/home-world.mjs`), checked on beat sheets, then used. Problems caught that could become learned rules: pale eggs in a dark cut-open case looked like teeth; wide room shots made the insects too small; a highlight drawn before the head was hidden under it.
- **Delivery:** Desktop path from PowerShell, copy, checksum match, never open a player. Board with `tools/show`. On approval, `tools/d6 complete-video <id> <mp4> --audio-manifest <manifest> --final`.

## Not this task

- Music has its own session (`01-content/music/`). Leave a clean place in the finish step where a chosen music bed could be mixed later. Do not choose or add music.
- Do not change approved videos, the fire-ant files, the outro assets or the ensign-wasp files.

## Rules

- No paid API calls without Drew's OK. No push.
- One question at a time, as multiple choice, only for real choices. Caveman mode in chat.
- Test on an existing approved episode without overwriting anything. Show Drew proof before calling it done.
