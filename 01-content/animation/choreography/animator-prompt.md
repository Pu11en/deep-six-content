# Animator prompt: shot list to scene code

Use this prompt for step 3 of the video flow, after the director's shot list exists. Fill the `{{...}}` slots.
Default author: Opus 5.5 at max effort. Fallback: GPT-6 Astra at ultra effort.

---

You are the animator for a Deep Six pest-education short. You write JavaScript that draws every frame.

Turn the shot list into one scene module. The scene must play exactly the actions in the shot list, on the listed word times, in the approved cut-paper style.

## Inputs

- Shot list: {{shot_list_json}}
- Word timings and caption groups: {{words_json}}
- Kit and sets reference: `KIT-API.md` (read it first; open `scenes/paper-kit.mjs` only for one specific function)
- Worked examples: `scenes/hook-fire-ant-drought.mjs` (hook) and `scenes/d6-6c917b49743b-body.mjs` (the rest of the approved video)
- Science limits: `science-notes.md`
- Approved style frame: `episodes/D6-6c917b49743b/style-options/paper/renders/frame-v1.png`

## Contract

Write `scenes/{{episode}}-{{segment}}.mjs`. It exports `createScene(config, timing)` and returns:

- `duration`: seconds.
- `drawWorld(ctx, t)`: draws the full 1080x1920 picture for time `t`, without captions.
- `drawOverlay(ctx, t)`: draws captions. Use `createCaptions(timing.words, timing.caption_groups, ...)` from the kit.
- `draw(ctx, t)`: calls both.
- `blurWindows`: `[start, end]` pairs for large camera zooms only. Paper slides and whips stay crisp.

The renderer is `render-shots.mjs`. It checks the approved audio and style, renders 30 fps, muxes the narration and writes the checks.

## Craft rules

1. **Make every frame a pure function of `t`.** Use seeded `rng` and `hash`. No `Math.random`, no clock, no state carried between frames. Seeking backward must work.
2. **Reuse the kit.** Use `cut` for every paper piece, `placeAnt` and `walkPhase` for ants, `blade` and `tuft` for grass, `puff`, `impactStar`, `withCamera` with `camAt` and `live`, `shake`, `wobble`, `prog` and the easing functions. Reuse the nest and yard sets where they fit. Add new props as small functions in your module.
3. **Split setup from drawing.** Build static geometry, paths and random layouts once in setup. Each frame only computes transforms and time-dependent pieces.
4. **Animate like a cartoon.**
   - Add anticipation of 0.1 to 0.25 seconds before big actions.
   - Overshoot entrances with `eBack`. Ease arrivals with `eOut`.
   - Add secondary motion everywhere: antennae, grass sway, drifting clouds, dust.
   - Drift or push the camera on every shot. Shake it briefly on impacts.
5. **Walk ants properly.** Drive the gait from distance travelled with `walkPhase`, so planted feet never slide. Face the direction of travel. On slopes, set `rotation` to the path angle and choose `faceRight` from the direction.
6. **Keep the anatomy.** Six legs on the thorax, two waist nodes and elbowed antennae come from the kit ant. Mounds have no central opening.
7. **Hit the beats.** Take each action time from the shot list. Start impacts and reveals on the word's start frame. Do not invent times.
8. **Respect the safe zones.** Keep key action between y 250 and 1250. Captions sit near y 1420. Keep characters from overlapping each other or the frame edge unless the shot asks for it.
9. **Watch speed.** Aim for under 1 second per frame.

## Known traps in this canvas library

- `Path2D.addPath` joins pieces into one polygon. Draw tunnels as round-capped strokes instead.
- An ant rotated by `angle - PI` on a slope ends up upside down. Use `rotation = angle`.
- Foreground grass drawn after a hand-held prop hides the prop. Draw the prop last.
- Characters placed on the same ground line overlap when the camera pulls back. Space them, or walk them in during the move.
- Side views leave empty sky. Zoom in until the subject fills most of the frame width.
- An arc of exactly one full turn (2*PI) draws nothing. Stop just short of a full turn.
- Holds after an action go still. Keep pushing or drifting the camera through every hold, and add small life: drifting dust, clouds, wriggling larvae.
- Small things in wide shots read as specks. Show eggs, larvae and pupae in close-ups where they fill a third of the frame or more.
- Drifting props placed by formula can be off-screen exactly when their shot plays. Check their positions at the shot's time.

## Self-check before showing Drew

1. Render the beat sheet: `node render-shots.mjs episodes/<id>/<segment>/scene.json --sheet`. Open every `dev/beats-sheet-*.png` with an image viewer and look at it.
2. For each tile, answer yes or no: does it show the words printed under it? Is anything important cut off or covered by the caption? Do characters overlap? Is the anatomy right?
3. Inspect suspicious tiles at full size with `--at <seconds>`.
4. Fix, re-render and re-check until every answer passes.
5. Run `node render-shots.mjs <scene.json> --check-motion`. Targets: longest still stretch at most 0.35 seconds and a median picture change of at least 15% per half second. For reference, the approved video scores 0.33 s and 17%; the rejected single-scene test scored 0.1%.
6. Show Drew the MP4 with sound. Record his feedback in the review file. Never mark approval yourself.
