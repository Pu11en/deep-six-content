# Findings: code-drawn illustrated pest videos

**First trial: Claude Animation’s drawing kit. Backup: Anidoodle’s painted illustration approach.** These are recommendations from the evidence below, not tested production systems.

## The project this research serves

Drew chose an illustrated science-book look: detailed bugs, textured scenery and clear underground views for homeowners. The approved lesson explains why a missing fire-ant mound does not prove the colony is gone, and how workers relocate developing ants as conditions change. The original narration and Tyler MP3 are already approved; the MP3 lasts **78.602449 seconds**. All new scenes must be **9:16, 1080×1920**, using the Deep Six palette. Astra with ultra effort is Drew’s requested animation author.

The existing [cartoon references](../../cartoon-animation-links.md) and [code-animation evidence](../code-animation-evidence-2026-10-16.md) informed the search. Their claims were treated as leads. The crawler then retrieved current repositories, actual drawing/rendering code, manifests, licenses and Texas A&M biology pages.

## Six options compared

| Option | What the inspected sources establish | Assessment for this trial |
|---|---|---|
| [Claude Animation](https://github.com/buildwithhanif/claude-animation-skill) | Published ant drawing, nest-building code, texture helpers, film template and local renderer. | **First choice:** directly relevant starting artwork and a small declared dependency list. Species corrections and a new vertical scene are required. |
| [Anidoodle](https://github.com/alexgreensh/anidoodle) | Painted storybook style recipes, a published butterfly example, renderer and package manifest. | **Backup:** promising for a richer painted look. No finished fire-ant scene was verified; more original drawing and browser setup are needed. |
| [Remotion](https://github.com/remotion-dev/remotion) | General code-driven video creation and a substantial component/rendering ecosystem. | Useful future assembly layer. It does not by itself establish the illustrated pest look. The [inspected license](https://github.com/remotion-dev/remotion/blob/main/LICENSE.md) has conditional commercial eligibility. |
| [Motion Canvas](https://github.com/motion-canvas/motion-canvas) | TypeScript vector animation explicitly designed to synchronize with voiceovers. | Strong timing candidate. Our textured ants and environments would still need to be designed. |
| [HyperFrames](https://github.com/heygen-com/hyperframes) | HTML/CSS/media and seekable animation rendered through a browser and FFmpeg. | General alternative renderer. No relevant ready-made fire-ant drawing library was established in the inspected README. |
| [HandDraw](https://github.com/ToBeWin/HandDraw-Skill) | Whiteboard-oriented SVG/text animation with a restricted movement vocabulary; README directs colorful stories to another project. | Lower priority for this selected look. “Hand-drawn” in its name is not evidence of rich illustrated animal scenes. |

These assessments concern fit for this one video. This was not a benchmark of all repositories pasted into chat, and no engine was ruled incapable of richer custom art.

## Why the first choice is concrete

The ant kit has actual functions for drawing an ant and moving its legs, creating paper/soil textures, laying out nest chambers and paths, and drawing eggs and larvae. Its [package manifest](https://github.com/buildwithhanif/claude-animation-skill/blob/main/plugins/claude-animation/skills/claude-animation/package.json) declares one direct dependency: `@napi-rs/canvas`, range `^0.1.65`. The [renderer](https://github.com/buildwithhanif/claude-animation-skill/blob/main/plugins/claude-animation/skills/claude-animation/lib/film.mjs) accepts frame dimensions and a duration, calls drawing code at each frame time, and sends those frames to FFmpeg. These are source-code observations, not a new execution test.

I inspected the project’s existing [creator contact sheet](../2026-10-16-cartoon-animation-evidence/colony-contact.jpg). It shows shaded brown ants, warm paper-like backgrounds, soil textures and nest rooms. That supports the visual direction. It does not prove smooth motion, full-video quality, narration synchronization or scientific correctness.

The [demonstration source](https://github.com/buildwithhanif/claude-animation-skill/blob/main/examples/ant-colony/film.mjs) fixes 1920×1080, 24 fps and 32 seconds. Its opening comments describe a leafcutter story. We need a new scene composition and timing for our narration; changing width and height alone would leave positions designed for a wide image.

The repository has an [MIT license](https://github.com/buildwithhanif/claude-animation-skill/blob/main/LICENSE). Preserve its notice when adapting code. The inspected renderer operates locally and does not require a hosted image/video API. This does not establish that all future services, dependencies or model usage have no cost.

## Scientific corrections before a usable fire-ant scene

1. **Pupae:** the colony module supplies a cocoon drawing. Texas A&M describes fire-ant pupae as exposed, initially pale, adult-shaped developing ants. Build that stage separately instead of using the capsule artwork. [Colony code](https://github.com/buildwithhanif/claude-animation-skill/blob/main/plugins/claude-animation/skills/claude-animation/lib/colony.mjs), [Texas A&M](https://fireant.tamu.edu/learn/fire-ant-identification/).
2. **Nest entrance:** Texas A&M describes underground access and no central mound opening. The example’s dive through a visible central hole must be redesigned for this lesson. [Texas A&M](https://fireant.tamu.edu/manage/how-can-i-tell-if-i-have-fire-ants/).
3. **Species anatomy:** the ant drawing explicitly implements a one-node waist. The crawler found a [Texas A&M model PDF](https://research.entomology.tamu.edu/wp-content/uploads/sites/28/2014/03/ENTO_029.pdf) whose search excerpt describes two nodes, but this PDF was **not read** in the run. Treat it as an unresolved verification lead before designing a fire-ant close-up. [Inspected ant code](https://github.com/buildwithhanif/claude-animation-skill/blob/main/plugins/claude-animation/skills/claude-animation/lib/rigs/ant.mjs).
4. **Lesson content:** create original scenes for the approved brood-relocation explanation. Leaf carrying and fungus gardening belong to the demo’s stated leafcutter story and are outside this approved lesson. A nest cutaway should be clearly illustrative; avoid implying a measured depth, fixed room layout or exact temperature threshold.

These corrections affect pictures. They do not revise the approved hook or narration.

## Why Anidoodle is the backup

Its [README](https://github.com/alexgreensh/anidoodle) describes pencil/watercolor and folk-tale storybook styles. The inspected [example source](https://github.com/alexgreensh/anidoodle/blob/main/skills/anidoodle/example/src/canvas-core/mechanicalLepidoptera.ts) defines a coded film with drawing functions, timeline cues and audio. The [renderer](https://github.com/alexgreensh/anidoodle/blob/main/skills/anidoodle/engine/tools/render.mjs) opens a Playwright adapter and encodes with FFmpeg. The repository carries an [Apache 2.0 license](https://github.com/alexgreensh/anidoodle/blob/main/LICENSE).

Its extra setup is concrete: the [manifest](https://github.com/alexgreensh/anidoodle/blob/main/skills/anidoodle/engine/package.json) declares esbuild, Playwright Core and TypeScript. Remotion/React packages are optional. Prefer the browser route for a future backup trial and resolve optional-package behavior before installing. The compatibility of that installation has not been tested here.

There is a documentation mismatch: the worked-example README says 47 seconds; the source header says 60 seconds, with actual duration computed from imports. The README also reports 49 consecutive identical opening frames. Neither was evaluated live. These are reasons to test a small original scene rather than promise a ready-made long video. [Example notes](https://github.com/alexgreensh/anidoodle/blob/main/skills/anidoodle/example/README.md).

## Remaining unknowns

- Finished quality and rendering speed on this machine, particularly at 1080×1920 for the complete narration.
- Installation of the native canvas dependency, its resolved version and transitive packages.
- Accurate fire-ant close-up anatomy, including the uninspected model PDF above.
- Word/phrase timings in the approved MP3; no forced alignment or new transcription ran.
- Whether the backup’s painted style looks better to Drew, and its actual example duration.
- Remotion license eligibility for a future commercial setup; this was not needed to recommend the MIT first option.
- Astra ultra’s results on this drawing task. The local cache lists that model and effort, but no model generation was run.

The crawler finished its evidence-gathering job with outcome **partial**, meaning best-effort public research with explicit limits. [Method, counts and failures](research-method.md) · [Complete source index](sources.md) · [Future installation and trial plan](first-trial-plan.md).
