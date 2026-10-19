# Session handoff — October 19, 2026

The video system design is saved. Drew will open a new chat with Claude Opus 5.5 to continue. No narration is approved or active.

## Start here

- [System design and open decisions](01-content/video-system-design.md)
- [Short workflow](01-content/video-workflow.md)
- [Writing prompts](01-content/writing-harness-prompts.md) — proposed, not validated.
- [Pest resources](01-content/pest-resource-library.md), [source-use log](01-content/source-log.md), and [hook research repositories](01-content/research/hook-research-repos-2026-10-19.md).

## Excalidraw

- [System overview](http://localhost:3003/boards/52831f1163e1277b819320fd) — six phases now run **top to bottom**, as requested.
- [Detailed flow](http://localhost:3003/boards/f8724119f563ab46a50243e7).
- Editable drawings and construction notes: [diagrams](01-content/diagrams/README.md). The final `.excalidraw` files contain edits beyond their initial specifications; preserve those edits. Reuse the shared viewer.

## Agreed flow

1. Scheduled pest-resource research and social-media hook research feed a writing harness.
2. Generate exactly five hooks. Drew chooses one or skips all five for another batch. A second choice may queue for a later video; only one video is active at a time.
3. Generate five full narrations using the exact selected hook and its same factual source. Drew chooses one or skips for another five.
4. Proposed next steps: scene plan → voiceover and measured timing → JavaScript/TypeScript cartoon animation → captions and sound → reusable branded outro → final human review → export.

All videos and previews must be **9:16**, with 1080×1920 export and Deep Six colors. The audience is homeowners seeking useful help with pest problems, initially ants/fire ants. The main lesson uses code animation; the reusable outro may use generated images/video.

## Resume with the unanswered choice

**Q1:** Should the five hook choices cover five different lessons/sources, or be five openings for one article? Five different lessons was recommended so a second queued choice can stay unique. Drew has not answered. Keep the selected factual source attached through narration.

Other open choices: research schedule and volume, video length and voice, review interface, voice/render tools, outro, budget and retries. See Q1–Q6 in the design document.

## Constraints and status

- Do not keep rejected narration archives. Discarded scripts were deleted; keep source metadata, process notes, feedback, and current selected work. Old Git history was not rewritten.
- Log factual sources to avoid reusing them across episodes. ANT-S001 remains reserved for the rejected D6-ANT-001 experiment; it is not a fresh source.
- Drew previously proposed Sonnet 5.5 for the writing harness. Its actual provider/model ID is unverified. Opus 5.5 is the requested next chat agent, not a confirmed change to that harness.
- No cron, production automation, paid calls, tool installations, or publishing automation was started.
- Diagram JSON, bindings, downward overview arrows, and whitespace checks passed. Both boards were opened; do not take screenshots or repeat fit checks.
- This closing save is local. Earlier work through commit `79371a8` was pushed; this session's drawing/handoff checkpoint has not been pushed.
