# Deep Six system in Excalidraw

**Current whole-system canvas:** [animation and full plain-English flow](animation-system.excalidraw). October 19 update: Claude Code with Opus 5.5 for every planned AI role; Astra/Sol tests and future prompting research stay outside the main flow. The approved outro is reused with each episode's voice. Step 1 now names Ultimate Crawler, Parallel search, page reads and the researcher's checks. [Evidence and implementation limits](../research/2026-10-19-whiteboard-research-step.md).

October 20: added **Research: start to checked evidence** to the right of the existing flows. It shows pest-specific saved sources, adaptive discovery, rejection feedback, reuse protection and the second crawler pass after hook selection. Six proposed research rules cover search memory, shortages, evidence quality and recovery. This section ends before narration writing; interface and harness selection are outside its scope. [Current design and limits](../research/2026-10-20-research-design.md) · [Research gaps reviewed](../research/2026-10-20-research-edge-cases.md).

**Two views of the same working design are open in the shared Excalidraw workspace.**

- [Main flow — research, choices, and production](http://localhost:3003/boards/f8724119f563ab46a50243e7) · [drawing file](video-system.excalidraw)
- [Overview — top-to-bottom stages](http://localhost:3003/boards/52831f1163e1277b819320fd) · [drawing file](system-overview.excalidraw)

The main flow includes both research inputs, both five-choice skip loops, the saved second-hook queue, the source carried into narration, production steps, and the reusable branded outro. Only one video proceeds at a time. Every video stays 9:16 in Deep Six colors.

Yellow notes show open decisions. Production steps are proposals; no automation is running. The exact Sonnet model, schedule, and production tools remain unconfigured.

## Editing and checks

The overview now runs top to bottom: phases are rows, roles are columns. Its spec records the vertical layout; preserve that orientation when editing or rebuilding.

Use the same two drawing files for future chat edits; the open boards follow saved changes. The JSON spec files and component drawings are construction inputs; the linked final drawings include the added source arrows, queue, outro, and hand-off labels.

October 19: checked valid JSON, unique element IDs, reciprocal bindings, text bounds, and required flow relationships. Corrected a queue label overlap and added explicit one-video, brand-color and model-status notes. Opened each board once through the shared helper. No screenshots or repeated viewer fit checks.

October 19 layout update: stacked all six overview stages vertically and rerouted the existing hand-offs. Preserved the same file, board URL, 140 elements, and 13 connections.

[Design log and open questions](../video-system-design.md) · [Working flow](../video-workflow.md)
