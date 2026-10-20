# Flow-design handoff

**Drew accepted the start-to-checked-evidence design. The full adaptive research loop still needs implementation and a live trial.**

- Current canvas: [animation-system.excalidraw](../diagrams/animation-system.excalidraw), built by [animation-system.build.py](../diagrams/animation-system.build.py).
- Main AI flow uses Claude Code / Opus 5.5. Astra/Sol experiments stay separate. The outro is approved.
- Research uses saved sources by pest, adaptive discovery, reuse checks, hook selection and a second crawler pass for supporting evidence.
- Rejection alone is enough. Claude chooses another strategy without asking Drew to explain.
- Narration design added below research: steps 10 to 16, ending at an approved script ready for the MP3. [Narration design](2026-10-20-narration-design.md). Interface and harness selection stay outside the design scope.
- MP3 design added: steps 17 to 24, Claude's recommendation, awaiting Drew's review. [MP3 design](2026-10-20-mp3-design.md).
- Session split: this session designs the system only. Another session runs the approved wasp narration, Chris MP3 through MP4; Drew gave it the go-ahead. Do not generate audio or video here.
- Continue refining one section at a time.

[Decisions](2026-10-20-research-design.md) · [Research edge cases](2026-10-20-research-edge-cases.md) · [Latest checks](2026-10-20-research-edge-checks.json).

Validation: eight earlier focused workflow tests passed; the latest drawing has zero structural errors or warnings. No runtime changes, new research job, generation or publishing ran. Drew requested a local commit; a later session will handle pushing.

## Review, 20 Oct

The drawing now covers start to approved MP3 (steps 1 to 24). It is a complete design, not a complete automation. Design-only so far: the adaptive research loop, Opus as writer, the free word check at the MP3 stage, one resume screen, targeted script edits, a standing spending cap and how a run gets triggered. None has had a live trial.

Next: when the other session finishes the wasp MP4, critique its MP3-to-MP4 flow against the real result. Then build the missing pieces and run the next episode end to end as the live test. A separate music session started 20 Oct from [its brief](../music/START-SESSION.md).
