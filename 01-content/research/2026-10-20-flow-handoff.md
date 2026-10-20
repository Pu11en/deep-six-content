# Flow-design handoff

**Drew accepted the start-to-checked-evidence design. The full adaptive research loop still needs implementation and a live trial.**

- Current canvas: [animation-system.excalidraw](../diagrams/animation-system.excalidraw), built by [animation-system.build.py](../diagrams/animation-system.build.py).
- Main AI flow uses Claude Code / Opus 5.5. Astra/Sol experiments stay separate. The outro is approved.
- Research uses saved sources by pest, adaptive discovery, reuse checks, hook selection and a second crawler pass for supporting evidence.
- Rejection alone is enough. Claude chooses another strategy without asking Drew to explain.
- This section ends before narration writing. Interface and harness selection are outside the current design scope.
- The other narration session owns narration improvements. Continue refining one section at a time.

[Decisions](2026-10-20-research-design.md) · [Research edge cases](2026-10-20-research-edge-cases.md) · [Latest checks](2026-10-20-research-edge-checks.json).

Validation: eight earlier focused workflow tests passed; the latest drawing has zero structural errors or warnings. No runtime changes, new research job, generation or publishing ran. Drew requested a local commit; a later session will handle pushing.
