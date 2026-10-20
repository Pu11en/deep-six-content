# Hook animation progress

**Hook v1 is rendered and waiting for Drew's review.** It animates the first 8.8 seconds of Tyler's approved narration in the approved cut-paper style (C).

- Video: `renders/hook-v1.mp4`, SHA-256 `d6611e727b66ba33d79098eb15e2b55cac3a7a2b61cbe5364d632970fcdc227c`. Desktop copy: `C:\Users\drewp\Desktop\Deep Six - Hook v1.mp4`.
- Review record: `renders/hook-v1.review.json` (decision pending). Approval must name this fingerprint.
- Board: entry "Hook animation v1: fire ants in a drought" with a moving preview and the beat sheet.

## What changed from the rejected motion test

| Rejected test | Hook v1 |
|---|---|
| One scene, one slow walking ant | 8 shots, a new action every 0.2 to 0.5 seconds |
| Visuals did not explain specifics | One picture per phrase, landing on its word |
| Static footer text, not synced | Word-by-word captions from measured word times |

## How it was made

1. Word times: median of three offline Whisper models, snapped to measured silences and plosive dips. `words.json`.
2. Director step: `shot-list.json`, following `../../../choreography/director-prompt.md`.
3. Animator step: `scenes/hook-fire-ant-drought.mjs` on the shared kit `scenes/paper-kit.mjs`, following `../../../choreography/animator-prompt.md`.
4. Self-check: beat contact sheets, full-size frame checks, then the full render with `render-shots.mjs`.

Author: Opus 5.5 at max effort, in this Claude Code session. No paid API calls, no new voice generation, no installs. One open-licensed font (Inter Display Black) was copied from the system fonts for captions.

## Checks (`renders/hook-v1.json`)

1080x1920, 30 fps, 264 frames. Video, audio and container are each 8.8 seconds. The longest stretch without visible change is 0.13 seconds. Render time 142 seconds.

ffmpeg scene detection finds 3 hard cuts (1.17, 4.2, 5.9 s). The other shot changes are paper slides, whips and camera moves, which that detector does not count.

## Limits

- Word times are machine-aligned and waveform-checked, not checked by a person listening.
- The Windows player opened twice but Windows kept it behind other windows, so it was closed. Drew can play the Desktop copy.
- The prompts have been followed by this author only; a fresh agent has not run them cold yet.
