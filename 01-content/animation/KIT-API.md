# Kit reference for scene authors

**Read this instead of the kit's source.** Open a source file only to check one function. All drawing happens at 1080x1920 in world coordinates; `withCamera` maps world to screen.

## `scenes/paper-kit.mjs`

**Constants:** `W`, `H` (1080, 1920). `C` palette: `cream paper ink purple lime limeDark grass grassMid grassDeep straw strawDark strawLight soil soilLight soilPale soilDark soilDeep tunnel tunnelInner crust crack sky hotSkyTop hotSkyLow sun sunHi sunRay sunRay2 water white`.

**Math and time:** `clamp lerp eOut eIn eIO eBack(k, s) eElastic noise1 rng(seed) hash(n)`. `prog(t, a, b)` gives 0..1. `bell(t, t0, d)` rises and falls once. `wobble(t, t0, freq, decay)` gives a damped shake. `shake(t, t0, dur, amp, seed)` returns `[dx, dy]`. `zoomTo(z0, z1, k)`. `mix(colorA, colorB, k)` blends hex or rgb colours and can be nested.

**Paper pieces:** `makeFibres(seed)` returns the paper texture; make it once per scene. `cut(ctx, pathOrSvg, color, texture, depth = 6, { shadow, grain, lift })` draws one paper piece with its shadow and grain; use it for every shape. Paths: `polyPath(points)`, `smoothPath(points, closed)`, `ovalPath(x, y, rx, ry, rot)`, `capsulePath(a, b, r0, r1)`, `bandPath(x0, x1, top, bottom, amp, seed)` (torn-top band), `tornLine`, `tornRect`. `fillScreen(ctx, color, texture)` fills the frame. Do not use `Path2D.addPath`; it joins pieces in this library.

**Camera:** `withCamera(ctx, { x, y, zoom, rot, dx, dy }, draw)` centres world point (x, y). `cam(x, y, zoom)`. `camAt(t, [[t0, cam(...)], [t1, cam(...), ease]])` interpolates keyframes. `live(camera, t)` adds the approved slow breathing sway; wrap every camera in it.

**Fire-ant worker:** `placeAnt(ctx, texture, x, groundY, scale, pose, { faceRight, rotation })`. Feet stand on `groundY`. The ant faces left unless `faceRight`. Pose fields:
- `phase` and `walk` (0..1): use `walkPhase(distanceTravelled, scale)` so planted feet never slide.
- `mand` (0..1 open), `head` (tilt radians), `bob` (lowers the body).
- `antennae: [[proximal, distal], [proximal, distal]]` in radians.
- `carry: 'larva' | 'pupa' | 'egg'`.
- `tint` (0..1): 1 is a pale newly emerged adult.

Scale 1 is about 640 px nose to tail.

**Brood:** `drawEgg(ctx, tex, x, y, r, angle)`. `drawLarva(ctx, tex, x, y, scale, angle, wiggle)` is about 100 x 130 px at scale 1. `drawPupa(ctx, tex, x, y, scale, angle, mature)` is adult-shaped, pale, with folded legs and no cocoon. `createBroodPile(seed)` then `drawBroodPile(ctx, tex, items, x, floorY, size, amount, t)`; amount 0..1 reveals the pile item by item.

**Plants and effects:** `blade(ctx, tex, x, y, height, width, lean, bend, color)`, `tuft(ctx, tex, x, y, size, seed, colors, sway, droop)`, `puff(ctx, tex, x, y, r, color, alpha)`, `impactStar(ctx, tex, x, y, r, popK, fade, rot)`.

**Captions:** `createCaptions(timing.words, timing.caption_groups, { texture, centerY: config.caption_center_y ?? 1420 })` returns `draw(ctx, t)`. Captions are automatic; never draw words yourself.

## `scenes/nest-world.mjs`: nest cutaway set

`createNest(texture)` returns `{ draw(ctx, t, state) }` in world coordinates. The surface line is `SURFACE` = 760. `CHAMBERS` lists `M1 M2 M3` (inside the mound), `U1 U2` (upper), `C1 C2` (middle) and `D1 D2 D3` (deep), each `{ x, y, rx, ry }`. The whole nest fits at `cam(540, 1480, 0.62)`.

State fields, all optional:
- **Mound:** `mound` (0..1; 0 means a flat lawn and nothing above ground), `moundCracks`.
- **Tunnels:** `tunnelsDraw` (0..1 draws tunnels downward).
- **Ants:** `surfaceAnts` (0..1), `surfaceScale`, `traffic` (0..1), `flow` (+1 down, -1 up, 0 both), `carry` (traffic carries brood), `speed`.
- **Chambers:** `brood: { C1: 1 }`, `busy: { C2: 1 }`, `glow: { D1: 0.7 }`, `glowColor: { D1: 'cool' }`, `ring: { C1: k }` (lime ring), `frame: { x, y, w, h, k }` (lime picture frame).
- **Overlays:** `cover` (soil sheet slides over the cutaway), `dimUnder`.
- **Weather:** `cold`, `wind`, `rain`, `rainFall`, `cloudsPart`, `fairClouds`, `sun`, `sunX`, `sunY`, `sunR`, `sunPale`, `beam` (sunbeam onto the mound), `heat`, `heatSoil`, `cool`, `moist` (sparkles), `water` (0..1 floods from below).
- **Extras:** `extra(ctx, t)` draws your own pieces on top.

## `scenes/yard-world.mjs`: backyard set and props

`createYard(texture)` returns `{ outline, drawBack(ctx, t, { mound, trace, dashed }), drawFront(ctx, t, { lens }) }`. The house, fence, lawn and mound spot match the hook. `MOUND` is `{ x: 520, base: 1065, width: 560, height: 265 }`. `lens` is `{ x, y, r, angle, xray(ctx) }`; xray draws inside the magnifier glass.

Props:
- `questionMark(ctx, tex, x, y, size, k)`
- `bigX(ctx, tex, x, y, size, k)`
- `pushpin(ctx, tex, x, y, k)`
- `gauge(ctx, tex, x, groundY, scale, needleAngle, k)`
- `person(ctx, tex, x, groundY, scale, { walk, phase, face, arm: 'down' | 'chin' | 'scratch' | 'hold', look, scratch })` draws a homeowner about 1000 px tall at scale 1.
- `thoughtBubble(ctx, tex, x, y, w, h, k, content)`

## Module contract

```js
export function createScene(config, timing) {
  const texture = makeFibres((config.seed ?? 1) | 0);
  const captions = createCaptions(timing.words, timing.caption_groups, { texture, centerY: config.caption_center_y ?? 1420 });
  const drawWorld = (ctx, t) => { /* t is absolute narration time */ };
  return { duration: config.duration_seconds, blurWindows: [], drawWorld, drawOverlay: captions,
    draw(ctx, t) { drawWorld(ctx, t); captions(ctx, t); } };
}
```

`blurWindows` entries look like `[start, end, samples, shutter]`. Use them only for big zooms and whips.

## `scenes/wasp-kit.mjs`: ensign wasp, American cockroach and egg case (made for D6-01096ba333e3)

Researched pieces in style C; anatomy and sources in `science-notes.md`. Reuse them for any cockroach or wasp episode; do not redraw them.

- **Ensign wasp:** `placeWasp(ctx, texture, x, groundY, scale, pose, { faceRight, rotation })`, about 560 px long at scale 1, faces left. Pose: `phase`, `walk`, `stride`, `flag` (gaster angle; about -1.1 is held high), `antennae`, `wing`, `fold` (0..1 tucks legs and wings, as in the pupa), `tint` (0..1 pale), `bob`. Use `gaitPhase(distance, scale, stride)` so feet never slide.
- **Young wasp:** `drawWaspEgg(ctx, tex, x, y, len, angle, k)`, `drawGrub(ctx, tex, x, y, len, angle, opts)` (pale, legless, segmented), `drawJawFace(ctx, tex, x, y, size, open, teethK, boost, lime)` (head-on, sickle jaws with small teeth).
- **Egg case:** `drawEggCase(ctx, tex, x, y, L, opts)` (purse-shaped, ridged seam; height `CASE_H` x L; exit hole `CASE_HOLE`), `drawCaseCutaway(ctx, tex, x, y, L, state)` with 16 eggs in two rows of eight (`caseEgg(L, i)` gives an egg's place), `drawRoachEgg(...)` (whole 1, empty shell 0), `drawCaseHole`, `drawCaseDisc`, `drawEggCaseTop`.
- **American cockroach:** `placeRoach(ctx, tex, x, groundY, scale, pose, options)` side view, about 860 px at scale 1; `drawRoachTop(ctx, tex, x, y, scale, angle, pose)` from above.
- **Props:** `ensignFlag` (pennant for the word "ensign"), `limeRing(ctx, x, y, rx, ry, k)` (drawn on like a marker), `targetMark`, `flashlightHand`.

## `scenes/home-world.mjs`: home sets (made for D6-01096ba333e3)

- `createSink(texture).draw(ctx, t, { crack, damp, warm, drip, extra })`: the cabinet under a kitchen sink, front view, with a crack, a gap under the back wall, a gap round the drain pipe, a warm supply line, a dripping trap and a damp floor. Named places in `SINK`.
- `createMacro(texture).draw(ctx, t, s)`: the same cabinet floor very close (floor line `MACRO_FLOOR` = 1150), where an egg case lies near a crack.
- `createFloorTop(texture).draw(ctx, t, { crackY })`: the floor seen from above.
- `tracePath(ctx, points, k)` draws a lime outline along a path; `flashlightBeam(ctx, x0, y0, x1, y1, spread, beam, dim)` lights a cone and dims the rest.
- Insects in wide sink shots read as specks: see `learned-rules.md`.

## `scenes/outro.mjs`: the approved Deep Six outro

The runner adds it after the lesson; segment authors never draw it. `createOutro(config, timing)` reads the frame plan written by `video_finish.fit_outro` (cream-paper wipe on the first frame after the last lesson word, logo landed before "Deep", about 1 s hold) and draws the outro's own top caption.
