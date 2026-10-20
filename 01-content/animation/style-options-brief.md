# Three genuinely different visual directions

Drew wants THREE ADDITIONAL first illustrations with vastly different visual styles, to compare before animation. Existing option A is a warm natural-history book illustration: tan earth, fine outlined realistic-ish ant, small house above, serif title in a purple header. Do not merely recolor that picture. Design three new scenes with distinct composition, shapes, textures, lighting and typography. All must be authored in reusable JavaScript drawing code, not image generation.

Return ONLY a complete JavaScript ES module (no markdown, explanation or tools). It will be saved as `scenes/fire-ant-style-options.mjs`. Export `createScene(config)` returning `{draw(ctx, timeSeconds)}`. `config.style` selects `cartoon`, `paper`, or `miniature`. These correspond to choices B, C and D. One source file, three genuinely different art directions. Aim for roughly 450–800 purposeful lines total; avoid excessive boilerplate. All illustration geometry must be original for these directions.

## Runtime contract

- Node, @napi-rs/canvas 0.1.65. Canvas2D API supports gradients, Path2D SVG strings, clipping, compositing, ellipses, bezier paths, shadows and text. You may import `createCanvas`, `Path2D`, `GlobalFonts` from `@napi-rs/canvas` (fonts are already registered; no registration needed here).
- Optional existing helper imports: `../vendor/claude-animation/core.mjs` exports `createCanvas`, `Path2D`, `rng(seed)` returning a deterministic random function, `grainCanvas(size, amount, seed)` returning a canvas, `ellipse(ctx,x,y,rx,ry,rotation=0)` creating a path, `line(ctx,points,width,color)`, `smooth(ctx,points,closed=true)` creating a path, and `lerp(a,b,k)`. `../vendor/claude-animation/textures.mjs` exports `fibrePaper(width,height,color)` returning an opaque paper canvas. Only use these documented APIs if importing helpers. Nothing else is installed.
- No filesystem, network, subprocesses, Date or Math.random. No external assets, model calls, dependencies or imagined APIs. Output source is inspected and rendered later by the caller.
- Fonts: aliases `D6Serif` (EB Garamond regular) and `D6Sans` (DejaVu Sans regular). Normal font styling; do not rely on unavailable fonts or emoji. Thick lettering can use strokes. Make text readable and deliberate.
- `config` contains `width:1080`, `height:1920`, integer `seed`, `palette:{cream,paper,ink,purple,lime}`, and `labels:{eyebrow,title,footer,illustrationNote}`. Use supplied labels verbatim, wrapping as needed. Do not invent other copy. Draw the whole frame. Scale from reference coordinates 1080×1920 to config dimensions. Do not write files.
- `createScene` may cache expensive static textures. Drawing must be deterministic and order-independent for the same time/config. `draw` should reset its transform/state and restore state afterwards. Keep the design in sensible component functions so motion can later be added without changing the art direction. A still is enough now; walking is NOT required in this task.

## Same lesson and branding across all three

One large fire-ant worker carrying a pale curved larva gently in its mandibles, inside an illustrative underground nest. A small domestic surface/house cue can anchor the homeowner setting. Emphasize the ant and transport action, not a generic landscape. Use a different perspective and nest arrangement in each style. The worker should occupy roughly 500–700px width with anatomy legible in a phone frame. Subject and larva should touch the ground/jaws appropriately, not float.

Supplied labels:
- eyebrow: DEEP SIX / FIRE ANT FIELD NOTES
- title: The nursery moves.
- footer: Workers carry their young as nest conditions change.
- illustrationNote: Illustrative cutaway · not to scale

Deep Six ad colors MUST be obvious in every design: lime `#A9D554`, purple `#3A3148`, near-black `#1E1B22`, cream `#F0DDB2`, warm white `#F6EFE2`. Use the supplied palette for these. You may add natural red-brown insect/earth tones and highlight/shadow variations. Do not make the ant purple or green. Integrate branding into each art direction; do not repeat one identical purple header/footer template three times. Large headline and clear brand name. Main content inside ~75px left/right, 100px top, 220px bottom; decorative art may bleed. Leave breathing room. This is a visual style audition, not a dashboard or UI mockup.

## B — Bold animated cartoon

Vivid TV-animation / illustrated ad aesthetic. Strong clean silhouettes, thick near-black outlines, bold rounded type and clearly separated cel-shaded colors. Expressive shape language and an appealing reddish worker, but no human nose, mouth, hands or upright two-legged pose. A lively three-quarter composition with a large worker walking along an earthy tunnel ledge, carrying its larva. Rich but controlled greens/purples in branded framing and surface details. Large insect, layered background, warm light, a few deliberate motion-like graphic accents. Avoid tiny spindly line drawings or beige textbook layout. The art should have the punch of a polished animated explainer thumbnail.

## C — Layered cut-paper storybook

Handmade construction-paper diorama: irregular cut edges, stacked flat silhouettes, fibrous paper textures, visible layered drop shadows, overlapping roots/grass/soil bands. No black outline around every shape, no glossy plastic gradients. Use a diagonal or curved slice of earth and a large worker built from layered red-brown paper pieces with cream larva, jointed paper-strip legs and two clearly separate waist nodes. Purple and lime paper foliage/title ribbons make the brand clear. The tiny house and landscape feel physically cut out. Elegant paper label typography and tactile depth. Clearly different from both ink illustration and cel animation.

## D — Cinematic clay-style miniature

A warm, softly lit miniature diorama with rounded sculptural forms and a slight three-quarter/isometric perspective. Code-drawn illusion of volume using convincing multi-stop gradients, contact shadows, occlusion and highlights; not an actual 3D engine. The earth is a substantial cutaway mound or block with thick rounded tunnel walls, seen as a physical model. A red-brown worker with softly rounded head/thorax, two sculpted waist beads, dark oval abdomen, six attached articulated legs, and pale curled larva takes center stage. Hint at a tiny house atop the earth. Purple studio backdrop or deep-purple shadow region, lime branded title/accents, warm directional lighting. Gloss is restrained; aim for crafted clay rather than chrome spheres. No flat sepia diagram, no neon sci-fi scene, and no collections of floating circles.

## Biological constraints for every style

- Six legs attached to the thorax (three near/three far); head, thorax and abdomen distinct; TWO visible small waist nodes between thorax and abdomen.
- Elbowed antennae, ideally a small club at the end; no antennae emerging from abdomen. Small stylized eyes are fine; don't add human facial features.
- Carried larva is pale, lightly segmented, curved and legless. It must visibly meet the jaws. No cocoons, leaf-carrying or fungus garden.
- Nest entry is not a central volcano hole on the mound. Side tunnels are fine. Nest shape/scale is illustrative. No numeric depth or temperature claims.
- Do not change the approved narration. These are three alternatives for the same excerpt and only their artwork varies.

Compose each frame carefully. Check label bounds, text contrast, insect limb origins, the two waist nodes, larva contact, floors and overlapping layers logically before returning the complete source. The caller will render and visually inspect all three.
