# Future first trial

**Start with one short scene from the approved audio.** This is an installation and production plan; none of these installation or rendering steps ran during research.

## First option: Claude Animation drawing kit

| Item | What to use | Current status |
|---|---|---|
| Author | GPT-6 Astra, ultra effort, through Drew’s existing subscription | Listed in the existing model cache; no new generation tested. |
| Repository | `buildwithhanif/claude-animation-skill` | Public files read only; no clone or installation. |
| Revision to inspect/use | `4ddb8c80fdec96dc9f55d4b9bdee60bde6f0134b` | Head reported by GitHub during the run. Fetched source snapshots and their hashes are saved. |
| Runtime | Node 20+ | Node **22.22.0** and npm **11.19.0** already available. |
| Drawing package | `@napi-rs/canvas`, declared range `^0.1.65` | Not resolvable from this project. Resolved version/native package still needs testing. |
| Encoder | FFmpeg and FFprobe | Both already installed, version **6.1.1**. |
| Audio | Existing `original-tyler.mp3` | Approved, **78.602449 seconds**. Reuse it; no new voice request needed. |
| Fonts | Explicit locally available fonts, with reuse rights checked | Demo points at Claude-specific and macOS paths; choose portable paths for the trial. |

Primary setup evidence: [README](https://github.com/buildwithhanif/claude-animation-skill), [package](https://github.com/buildwithhanif/claude-animation-skill/blob/main/plugins/claude-animation/skills/claude-animation/package.json), [template](https://github.com/buildwithhanif/claude-animation-skill/blob/main/plugins/claude-animation/skills/claude-animation/templates/film-template.mjs). Local evidence: [environment inspection](local-environment.json), [model cache inspection](model-cache-check.json).

When implementation is requested:

1. Put a pinned repository checkout and original trial scene in an isolated experiment folder inside this project. Preserve the MIT notice.
2. Install dependencies only for `plugins/claude-animation/skills/claude-animation/`. Record the resolved dependency versions. No global Claude plugin or IDE extension is necessary to author a local scene from the library.
3. Verify the fire-ant anatomy reference, then make original worker and exposed-pupa drawings. Reuse suitable texture and nest helpers.
4. Author a 1080×1920 composition in Deep Six colors. Use the approved paragraph beginning “Workers move the brood within the nest as conditions change.” Measure the matching MP3 excerpt before setting timing; its timestamps have not been established yet.
5. Show a worker carrying brood toward a cooler, moister part of an illustrative nest. Use one clear action, large visible subjects and restrained labels. Aim for roughly 10–15 seconds, adjusted to the actual spoken excerpt.
6. Render a new trial file locally and combine it with the existing audio excerpt. Keep the approved full MP3 untouched. Check decoding, dimensions, duration, timing and the biological drawings, then show Drew the actual moving preview for review.

The renderer supports dimensions and time, but it does not automatically turn this narration into accurate shot timings, drawings or captions. Those remain the scene-authoring work. Its existing sound helper focuses on synthesized sounds/music; integrating the approved narration still needs explicit handling.

## What should pass before making the full video

- Drew likes the illustrated detail and the movement.
- A viewer can see that workers are relocating young ants; they are not watching unrelated leafcutter activity.
- Pupae, entrance layout and worker anatomy fit fire ants.
- The scene reads clearly in a tall phone frame and matches the spoken excerpt.
- Rendering finishes reliably on this machine with acceptable measured time.

Then extend the same approved visual vocabulary across the whole narration. Align scene changes to measured audio phrases; do not rewrite or regenerate the narration to accommodate an animation shortcut.

## Backup: Anidoodle

Use [Anidoodle](https://github.com/alexgreensh/anidoodle) if the first kit’s illustrated look or drawing controls fail the trial. Observed head: `4db69644b994ae9caf9e20936506954b2f5e4872`.

The inspected engine manifest lists **esbuild 0.25.12**, **Playwright Core 1.63.0** and **TypeScript 5.9.3**, with optional Remotion/React packages. Its documented browser path also needs a compatible Chromium installation and FFmpeg. Evaluate omitting optional Remotion packages and use the Playwright route for the first backup test; this installation has not been executed. Preserve Apache license/notice requirements.

Create the same fire-ant scene and use the same audio excerpt so Drew can compare drawing and motion fairly. The supplied butterfly is a reference, not a finished fire-ant asset. Resolve its README/source timing mismatch before borrowing timing-related assumptions.

No required paid image/video service was identified for either proposed local route. Installation compatibility, transitive terms and actual generation/rendering effort remain untested.
