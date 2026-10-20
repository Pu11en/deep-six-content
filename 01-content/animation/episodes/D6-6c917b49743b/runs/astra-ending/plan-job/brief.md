You are the Deep Six video director. Your working root is the folder `01-content/animation`.
Plan a whole pest-education short for episode D6-6c917b49743b, narration time 57.60 to 78.60 seconds, in the approved
cut-paper style C. Match the pace and quality bar in VIDEO-FLOW.md. You plan pictures; you do not write scene code.

Narration words with their index in words.json and start time in seconds:
  [149]  57.69  So
  [150]  57.82  the
  [151]  57.96  nest
  [152]  58.18  you
  [153]  58.36  see
  [154]  58.56  above
  [155]  58.84  ground
  [156]  59.47  doesn't
  [157]  59.78  show
  [158]  60.02  you
  [159]  60.22  where
  [160]  60.48  the
  [161]  60.66  developing
  [162]  61.08  ants
  [163]  61.42  are
  [164]  61.58  being
  [165]  61.74  kept.
  [166]  62.73  The
  [167]  62.84  colony's
  [168]  63.32  internal
  [169]  63.76  activity
  [170]  64.26  can
  [171]  64.62  continue
  [172]  65.06  out
  [173]  65.36  of
  [174]  65.52  sight
  [175]  65.82  while
  [176]  66.10  the
  [177]  66.26  surface
  [178]  66.64  looks
  [179]  66.92  quiet.
  [180]  68.11  For
  [181]  68.20  a
  [182]  68.32  homeowner,
  [183]  69.01  that
  [184]  69.24  changes
  [185]  69.68  what
  [186]  69.94  a
  [187]  70.02  missing
  [188]  70.30  mound
  [189]  70.58  means.
  [190]  71.64  You're
  [191]  71.80  losing
  [192]  72.06  a
  [193]  72.34  visible
  [194]  72.74  clue
  [195]  73.12  about
  [196]  73.38  the
  [197]  73.56  nest,
  [198]  74.25  not
  [199]  74.48  getting
  [200]  74.74  a
  [201]  74.90  direct
  [202]  75.22  measurement
  [203]  75.64  of
  [204]  75.90  the
  [205]  76.04  colony's
  [206]  76.46  condition
  [207]  77.14  or
  [208]  77.30  its
  [209]  77.50  developing
  [210]  77.98  young.

Read these first: VIDEO-FLOW.md, choreography/director-prompt.md, scenes/paper-kit.mjs (what the kit already draws),
scenes/nest-world.mjs and scenes/yard-world.mjs (finished sets), science-notes.md. Episode limits: Explain mechanisms without invented desiccation physiology, exact nesting depths, universal temperature cutoffs, treatment prescriptions, or claims of certain survival.

Withheld files:
- Do not open scenes/d6-6c917b49743b-body.mjs. It is withheld for this run.
- Do not open scenes/d6-6c917b49743b-full.mjs. It is withheld for this run.
- Do not open episodes/D6-6c917b49743b/full. It is withheld for this run.
- Do not open episodes/D6-6c917b49743b/model-test. It is withheld for this run.
- Do not open ../../BOARD.md. It is withheld for this run.
- Do not open ../../board-previews. It is withheld for this run.

Write exactly these three files:
1. episodes/D6-6c917b49743b/runs/astra-ending/shot-list.json: every shot, in the director prompt's JSON shape, with absolute times. Every phrase gets a visible action
   landing on its word. Add a top-level "new_assets" list naming any drawing the kit and sets do not have yet.
2. episodes/D6-6c917b49743b/runs/astra-ending/segments.json: a JSON list of {"name", "start", "end"} segments named astra-ending-seg01, astra-ending-seg02 and so on. They must be
   contiguous, cover 57.60 to 78.60 exactly, cut only in pauses between sentences, and last 6 to 15 seconds each.
3. episodes/D6-6c917b49743b/runs/astra-ending/caption-groups.json: a JSON list of caption groups; each group is a list of word indexes from the list above. Cover every word once,
   in order, one to four words per group, broken at natural phrases.

Never modify existing files. When finished, reply with the JSON summary the output schema asks for.
