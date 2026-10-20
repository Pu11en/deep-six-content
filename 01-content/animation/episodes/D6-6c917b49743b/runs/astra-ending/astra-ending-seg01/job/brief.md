You are the Deep Six video animator. Your working root is the folder `01-content/animation`.
Make one segment of a pest-education short in the approved cut-paper style C. It must match the quality, pace and look of the
approved reference video described in VIDEO-FLOW.md.

Segment: episode D6-6c917b49743b, absolute narration time 57.60 to 67.80 seconds.
Narration words in this segment, with start times in seconds:
   57.69  So
   57.82  the
   57.96  nest
   58.18  you
   58.36  see
   58.56  above
   58.84  ground
   59.47  doesn't
   59.78  show
   60.02  you
   60.22  where
   60.48  the
   60.66  developing
   61.08  ants
   61.42  are
   61.58  being
   61.74  kept.
   62.73  The
   62.84  colony's
   63.32  internal
   63.76  activity
   64.26  can
   64.62  continue
   65.06  out
   65.36  of
   65.52  sight
   65.82  while
   66.10  the
   66.26  surface
   66.64  looks
   66.92  quiet.

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
- Do not open episodes/D6-6c917b49743b/model-test. It is withheld for this test.
- Do not open ../../BOARD.md. It is withheld for this test.
- Do not open ../../board-previews. It is withheld for this test.

Write exactly these files:
- scenes/astra-ending-seg01.mjs: the scene module. Export createScene(config, timing) returning
  { duration, blurWindows, drawWorld(ctx, t), drawOverlay(ctx, t), draw(ctx, t) }. t is absolute narration time.
  Build captions with createCaptions(timing.words, timing.caption_groups, { texture, centerY: config.caption_center_y ?? 1420 }).
The scene settings already exist at episodes/D6-6c917b49743b/runs/astra-ending/astra-ending-seg01/scene.json; do not edit them. Scratch files may go in episodes/D6-6c917b49743b/runs/astra-ending/astra-ending-seg01/dev.

Self-check loop. Required; repeat until every check passes, at most 6 rounds:
1. Run `node render-shots.mjs episodes/D6-6c917b49743b/runs/astra-ending/astra-ending-seg01/scene.json --sheet`, then open every sheet with your image viewing tool. Each tile must show
   the words printed under it; nothing important cut off or under the caption; no overlapping characters; correct anatomy.
2. Run `node render-shots.mjs episodes/D6-6c917b49743b/runs/astra-ending/astra-ending-seg01/scene.json --at <seconds,...>` for transitions and holds, and view those frames.
3. Run `node render-shots.mjs episodes/D6-6c917b49743b/runs/astra-ending/astra-ending-seg01/scene.json --check-motion`. Targets: longest_still_seconds at most 0.35;
   picture_change_half_second_median at least 0.15.

Rules:
- Never modify, rename or delete existing files. Create only the files named above. Put any kit additions inside your module.
- No network and no installs. Keep every frame a pure function of t.
- No on-screen words except the kit's captions. A question mark or X is allowed only where the narration questions or negates.

When finished, reply with the JSON summary the output schema asks for.

The director already planned this segment. Its shots are in episodes/D6-6c917b49743b/runs/astra-ending/astra-ending-seg01/shot-list.json (copied from the whole-video plan episodes/D6-6c917b49743b/runs/astra-ending/shot-list.json).
Implement those shots faithfully; refine details only to fix problems you see in your checks. Do not rewrite episodes/D6-6c917b49743b/runs/astra-ending/astra-ending-seg01/shot-list.json.
Earlier segments in this video, for continuity: none
