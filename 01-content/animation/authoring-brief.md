# First reusable scene: fire-ant brood

Create an original, polished, code-drawn vertical illustrated science-book frame for Deep Six Pest Control. GPT-6 Astra at ultra effort is the requested author. This is the first visual approval; movement and the full movie follow approval.

## Deliverable and interface

Return a complete JavaScript ES module as the `code` JSON string. It will be saved as `scenes/fire-ant-brood.mjs`. Also return a brief `design_summary` string. Do not return markdown fences.

Export `createScene(config)`, returning `{ draw(ctx, timeSeconds) }`. The draw function paints an entire 1080×1920 canvas, with no file access, network, process execution, or dependencies beyond the provided drawing helpers and @napi-rs/canvas. The caller registers font aliases `D6Serif` (EB Garamond) and `D6Sans` (DejaVu Sans). Set fonts explicitly. The caller handles PNG export.

Use imports from `../vendor/claude-animation/core.mjs`, `textures.mjs`, and/or `colony.mjs`. Their full public source follows this brief. Reuse their useful paper/grain/root primitives; create original fire-ant anatomy and any custom nest geometry needed. No other imports. Do not use the supplied cocoon, leafcutting, fungus or one-node ant design. The selected helper files have an MIT notice retained in the project.

Config provides `width`, `height`, `seed`, `palette` (cream, paper, ink, purple, lime), and `labels` (eyebrow, title, footer, illustrationNote). Read these rather than hardcoding display copy. Width/height are 1080/1920 for this first scene. Make geometry in this reference coordinate space. All drawing must be deterministic for the same config/time. Do not use Date, Math.random, or state that changes between draws. Cache paper/soil/expensive background textures per scene, not per frame. Keep any leg pose or future position motion a pure function of time. The first exported frame is time 4.5 seconds. The same scene should be usable later for a short animation without re-authoring the artwork.

## Art direction

- A beautiful natural-history picture book for adult homeowners: rich soil textures, warm cream paper, elegant dark serif typography, fine ink contours, softly shaded insects, restrained lime/purple brand accents. Natural red-brown worker, dark abdomen, cream larva. Warm and approachable, with no human faces or cartoon eyes on insects.
- One coherent illustrated environment, not a dashboard, boxes, infographic cards or a simplistic chart. Layered irregular earth, a few roots/pebbles and a small dry yard/house hint near the surface. Use deliberate lighting and quiet negative space. Avoid uniform procedural clutter, overpowering hatching, plastic gradients or flat clip-art.
- Tall phone composition. Keep important content 72px from left, 130px from right, 100px from top and 220px from bottom for later platform overlays. The art may bleed to edges. Do not frame the image in fake player controls. The bottom can continue artwork, with only a small illustrative-not-to-scale note.
- Header: small `labels.eyebrow`, then a large editorial serif `labels.title` on two lines if useful, within roughly the upper 340px. The main illustration occupies most of the remaining frame. `labels.footer` should remain legible around y=1640–1700 without overlapping the insect; it is a short explanatory line, not a paragraph.
- HERO: a side/three-quarter view of a worker carrying a curved pale larva gently between its mandibles, clearly touching the jaws. The insect plus legs should read immediately, roughly 500–650px wide. Place it in an enlarged tunnel/chamber cutaway so its feet meet a floor. Give the carrying action visual priority; the larva must look like a young ant grub, not a leaf, stone or round egg. Other chambers and a tiny brood group can support the scene, never compete.
- The nest should feel connected and organic. Broad, softly edged tunnels/chambers are visibly open where they meet. No perfect grid, ladder or uniform rooms. Avoid roots visibly running through empty tunnel space or objects that appear to float. Treat the nest as illustrative rather than a measured structure. Surface is dry ground with no central volcano opening.

## Scientific content and constraints

Approved narration excerpt (do not change it): “Workers move the brood within the nest as conditions change. Picture the nursery shifting between different parts of the structure, rather than every ant staying in one fixed room all season.”

The complete approved narration explains eggs, larvae and pupae; higher positions in cold/wet conditions and cooler/moister positions during hot/dry weather. This frame illustrates worker transport only. Do not invent a precise depth, temperature, chamber count or survival guarantee. No treatment advice. No invented claim labels.

Texas A&M's Imported Fire Ant Model PDF was read: https://research.entomology.tamu.edu/wp-content/uploads/sites/28/2014/03/ENTO_029.pdf — page 1 lists two waist nodes and 10 antenna segments with a two-segmented club. Draw two visible small waist nodes, elbowed antennae with a club, distinct head/thorax/abdomen, and six jointed legs attached to the thorax (three near, three far, with believable overlapping perspective). Mouthparts grasp the larva. No legs sprout from the abdomen. Do not draw a stinger prominently in a calm transport scene. The carried larva is legless and lightly segmented. If any pupae are drawn they must be exposed pale ant shapes, not cocoons; easiest is to show only larvae in this first frame.

Quality before quantity. Supply a complete carefully composed module, not placeholders or promises. Check coordinates, line widths, clipping, leg count and typography logically before returning. Keep the code understandable for later automation and scene reuse.
