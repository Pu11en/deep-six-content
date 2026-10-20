Claude Code cloud sessions can handle the planned work after a portability pass. End-to-end cloud rendering is not tested. Drew has now authorized a checkpoint push; [the main handoff](HANDOFF.md) is the continuation entry point.

## Pre-push review on October 20, 2026

- GitHub repository `Pu11en/deep-six-content` is public. Before this checkpoint, local `main` was two commits ahead and the remote lacked the animation, outro and audio folders.
- Before exclusions, about 968 MiB of tracked and unignored local files existed. The checkpoint retains project work and media while excluding temporary frame caches, raw CLI logs and job locks.
- [Narration D6-01096ba333e3](01-content/approved-narrations/D6-01096ba333e3.md) is approved: v6 option 3, 138 words. [Approval receipt](01-content/mp3-system/narration-approval.json). No episode audio exists. Chris is next.
- `.gitignore` excludes the writing harness runtime. A [portable checkpoint](01-content/harness/checkpoints/2026-10-20-stop/README.md) preserves saved approvals and queue state for a fresh checkout.

## Next session: prepare the cloud move

1. Start from the pushed checkpoint and preserve narration, source, voice and audio decisions. This turn's push is authorized; later publishing still follows Drew's approval rule.
2. Prepare Node, Python, FFmpeg and speech-alignment dependencies. Replace assumptions about local Claude/Codex logins, MacBook crawler access and Windows Desktop delivery.
3. Use separate task branches for diagrams/system design, the website URL overlay, and the ensign-wasp video. Coordinate shared files and production state.
4. Keep the approved outro. Add only the requested website URL overlay; the owner-face idea was withdrawn.
5. Generate one authorized Chris recording, obtain listening approval, create researched wasp drawings, then build the video. ElevenLabs usage is separate from Claude credits.

## Platform limits

Cloud sessions do not inherit this Zed conversation or machine-only tools. Saved diagram files can travel; the local live board needs separate handling. Rendering needs a cloud smoke test. [Environment documentation](https://code.claude.com/docs/en/cloud-environments).

Independent cloud sessions are supported and share account limits. Exact promotional eligibility and expiry remain unverified. [Cloud documentation](https://code.claude.com/docs/en/claude-code-on-the-web).

Progress: readiness review complete; the authorized checkpoint push is being prepared. Cloud setup remains unfinished.
