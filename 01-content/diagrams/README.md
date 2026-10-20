# Deep Six system in Excalidraw

**Current whole-system canvas:** [animation and full plain-English flow](animation-system.excalidraw). October 19 update: Claude Code with Opus 5.5 for every planned AI role; Astra/Sol tests and future prompting research stay outside the main flow. The approved outro is reused with each episode's voice. Step 1 now names Ultimate Crawler, Parallel search, page reads and the researcher's checks. [Evidence and implementation limits](../research/2026-10-19-whiteboard-research-step.md).

October 20: added **Research: start to checked evidence** to the right of the existing flows. It shows pest-specific saved sources, adaptive discovery, rejection feedback, reuse protection and the second crawler pass after hook selection. Six proposed research rules cover search memory, shortages, evidence quality and recovery. This section ends before narration writing; interface and harness selection are outside its scope. [Current design and limits](../research/2026-10-20-research-design.md) · [Research gaps reviewed](../research/2026-10-20-research-edge-cases.md).

October 20, later: added **Narration: checked evidence to approved script** below the research section. Steps 10 to 16 run from planning the writing to locked approved words, with retry routes back to research (step 8) and hook choice (step 7). It ends at an approved narration ready to become an MP3. [Narration design and limits](../research/2026-10-20-narration-design.md).

October 20, MP3: added **MP3: approved script to approved recording** below narration. Steps 17 to 24 cover voice, read preparation, cost and Drew's yes, one take, a proposed free word check, listening and locked approval. This is Claude's recommended design, not yet approved. [MP3 design](../research/2026-10-20-mp3-design.md).

**Earlier detailed audio scope: start through approved MP3.** [Open the audio flow](http://localhost:3003/boards/0d05ffd0809f0bbe1220a047) · [editable drawing](start-to-approved-mp3.excalidraw) · [stage instructions, retries and proof](../mp3-system/README.md).

The new drawing has three parts: find the lesson, build the explanation, hear and approve it. It includes the source queue, supporting-research loop, exact repeated hook, separate script/audio approvals, voice rotation and spending/recovery stops. Writing is implemented; audio handoff/review are agent-operated. The separate source file preserves both older boards below. Validated JSON, unique IDs, bindings and text dimensions; no screenshots or viewer fit checks.

Latest clarification: replaced technical numbered labels with plain language; added an approved-source route that goes straight to hooks, the explicit request sent before crawler searches, a real cockroach-request example, and source-quality criteria. Research stocking and episode production are separate routes; their scheduling/automatic crawler connection remain unfinished. Another active session owns MP3 through finished video, excluding the outro.

Latest layout: rebuilt the same board as a vertical boxed flow, keeping all 47 text blocks unchanged. Current drawing: 120 elements, including 33 boxes, four choice diamonds and 36 connectors. The middle column carries the process; examples, retry instructions and review details sit in side boxes. [Research and checks](../research/2026-10-19-flowchart-layout.md).

Later policy update: six labels now reflect fresh research for the next trial, the preserved queue, saved hooks as alternatives, connected crawler request/import, and source consumption only at finished MP4. The boxed layout and all connections remain unchanged. [Current review](../mp3-system/review-summary.md).

## Earlier drawings — historical

**These two drawings predate source-first review (D17).** They remain preserved. Use the new MP3 flow for the current task; later video and outro design is out of scope.

- [Main flow — research, choices, and production](http://localhost:3003/boards/f8724119f563ab46a50243e7) · [drawing file](video-system.excalidraw)
- [Overview — top-to-bottom stages](http://localhost:3003/boards/52831f1163e1277b819320fd) · [drawing file](system-overview.excalidraw)

The main flow includes background research, both five-choice skip loops, the saved second-hook queue, evidence carried internally into narration, a bank of approved scripts, and later production with a reusable outro. Only one writing batch and one production video proceed at a time. Every video stays 9:16 in Deep Six colors.

Yellow notes show open decisions. Production steps are proposals; the local writing harness is built and unattended scheduling stays off. Sonnet 5.5 passed the earlier subscription test. Hook research is planned for Saturday nights; exact time and production tools remain open.

## Editing and checks

The overview now runs top to bottom: phases are rows, roles are columns. Its spec records the vertical layout; preserve that orientation when editing or rebuilding.

Use the same two drawing files for future chat edits; the open boards follow saved changes. The JSON spec files and component drawings are construction inputs; the linked final drawings include the added source arrows, queue, outro, and hand-off labels.

October 19: checked valid JSON, unique element IDs, reciprocal bindings, text bounds, and required flow relationships. Corrected a queue label overlap and added explicit one-video, brand-color and model-status notes. Opened each board once through the shared helper. No screenshots or repeated viewer fit checks.

October 19 layout update: stacked all six overview stages vertically and rerouted the existing hand-offs. Preserved the same file, board URL, 140 elements, and 13 connections.

October 19 decision update: both drawings now show Q1 as decided (five lessons, one source per hook). Only those two note texts and the overview marker color changed.

October 19 continuation: corrected the first screen to five hooks only and removed the topic-direction task. Pest research runs per writing run; the hook library refreshes Saturday nights. Approved scripts are saved, and the production handoff is dashed and labeled as later work. These edits preserve the existing layout and element IDs. The older construction specs/component drawings are not current; use the two final drawings above.

[Design log and open questions](../video-system-design.md) · [Working flow](../video-workflow.md)
