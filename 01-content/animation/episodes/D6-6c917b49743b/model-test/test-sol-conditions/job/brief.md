You are the Deep Six video animator. Your working root is the folder `01-content/animation`.
Make one segment of a pest-education short in the approved cut-paper style C. It must match the quality, pace and look of the
approved reference video described in VIDEO-FLOW.md.

Segment: episode D6-6c917b49743b, absolute narration time 27.20 to 40.55 seconds.
Narration words in this segment, with start times in seconds:
   27.29  Those
   27.54  young
   27.88  ants
   28.26  are
   28.48  part
   28.74  of
   28.88  the
   28.98  reason
   29.28  nest
   29.62  conditions
   30.08  matter.
   31.15  During
   31.34  cold,
   32.06  wet
   32.22  weather,
   32.99  colonies
   33.38  tend
   33.62  to
   33.80  occupy
   34.18  higher
   34.64  parts
   34.98  of
   35.12  the
   35.24  nest,
   35.90  where
   35.98  they
   36.10  can
   36.24  take
   36.42  advantage
   36.76  of
   37.02  sunlight
   37.48  and
   37.62  keep
   38.00  brood
   38.30  away
   38.70  from
   38.98  waterlogged
   39.66  soil.

Read these first, in order:
1. VIDEO-FLOW.md: the recipe and the quality bar.
2. choreography/director-prompt.md, then choreography/animator-prompt.md.
3. scenes/paper-kit.mjs: the kit you build with.
4. scenes/nest-world.mjs and scenes/yard-world.mjs: finished sets you may reuse.
5. scenes/hook-fire-ant-drought.mjs: a complete approved example.
6. science-notes.md. Episode limits: Explain mechanisms without invented desiccation physiology, exact nesting depths, universal temperature cutoffs, treatment prescriptions, or claims of certain survival.

Withheld files:
- Do not open scenes/d6-6c917b49743b-body.mjs. It is withheld for this test.
- Do not open scenes/d6-6c917b49743b-full.mjs. It is withheld for this test.
- Do not open episodes/D6-6c917b49743b/full. It is withheld for this test.
- Do not open ../../BOARD.md. It is withheld for this test.
- Do not open ../../board-previews. It is withheld for this test.

Write exactly these files:
- episodes/D6-6c917b49743b/model-test/test-sol-conditions/shot-list.json: your shot list for this segment, absolute times, in the director prompt's JSON shape.
- scenes/test-sol-conditions.mjs: the scene module. Export createScene(config, timing) returning
  { duration, blurWindows, drawWorld(ctx, t), drawOverlay(ctx, t), draw(ctx, t) }. t is absolute narration time.
  Build captions with createCaptions(timing.words, timing.caption_groups, { texture, centerY: config.caption_center_y ?? 1420 }).
The scene settings already exist at episodes/D6-6c917b49743b/model-test/test-sol-conditions/scene.json; do not edit them. Scratch files may go in episodes/D6-6c917b49743b/model-test/test-sol-conditions/dev.

Self-check loop. Required; repeat until every check passes, at most 6 rounds:
1. Run `node render-shots.mjs episodes/D6-6c917b49743b/model-test/test-sol-conditions/scene.json --sheet`, then open every sheet with your image viewing tool. Each tile must show
   the words printed under it; nothing important cut off or under the caption; no overlapping characters; correct anatomy.
2. Run `node render-shots.mjs episodes/D6-6c917b49743b/model-test/test-sol-conditions/scene.json --at <seconds,...>` for transitions and holds, and view those frames.
3. Run `node render-shots.mjs episodes/D6-6c917b49743b/model-test/test-sol-conditions/scene.json --check-motion`. Targets: longest_still_seconds at most 0.35;
   picture_change_half_second_median at least 0.15.

Rules:
- Never modify, rename or delete existing files. Create only the files named above. Put any kit additions inside your module.
- No network and no installs. Keep every frame a pure function of t.
- No on-screen words except the kit's captions. A question mark or X is allowed only where the narration questions or negates.

When finished, reply with the JSON summary the output schema asks for.
