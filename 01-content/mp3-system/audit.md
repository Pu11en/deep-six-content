# Earlier start-to-MP3 design audit — October 19, 2026

**Historical checkpoint.** The later [edge-case review and implemented fixes](edge-cases.md) supersede the statuses and pending reuse question below. Kept for history.

**The writing flow and audio generator exist. Connecting them into one reliable, reviewable automation is still unfinished.** This audit read the local code, saved state, approved script, audio manifests and prior decisions. It did not make live research/model/TTS calls.

**Later crawler update:** Drew confirmed the crawler is ready. Authenticated capabilities and API-schema reads passed; [the new procedure and access proof](../research/2026-10-19-crawler-workflow/README.md) supersede the earlier “deferred” instruction. No research job ran during that update. Automatic writing-runner integration remains a gap.

## What is real today

| Part | Evidence / practical limit |
|---|---|
| Source → hook → narration review | [Controller](../../tools/d6_harness.py): five-choice schemas, review IDs, saved decisions, exact-hook check, locks and retry checkpoints. Agent shows choices in chat. |
| Scientific support | `check_depth`, `prepare_evidence`, and [page validator](../../tools/d6_sources.py). Separate support domains, short checked quotes and preserved limits. Quote matches do not prove every inference. |
| Source stock and pest rotation | Liked queued/in-use sources count toward three. Current approved source is used; three ant sources remain queued; next research pest is cockroaches. |
| Preferences | Source decisions separate from hook decisions. Last 12 hook decisions and last 12 combined non-source feedback notes feed writing; last two approved scripts provide style examples. No model retraining. |
| Model fallback | [Runner](../../tools/d6_models.py), subscription authentication only. Current config Codex/Astra; Claude primary route can be restored when usable. Prior Sol 6.1 probe failed; availability is not newly tested here. |
| Voice rotation / MP3 generation | [Audio tool](../../tools/d6_audio.py) and [voice assignments](../audio/voice-rotation.json): one assignment per narration, no blind billing retry, hashes, file checks, measured duration. |
| Listening review | First MP3 explicitly approved in its manifest. User-facing display and recording approval are agent-operated. Player opens Edge automatically; it does not satisfy a Desktop-first default yet. |

## Gaps to implement later

1. **One episode record through audio approval.** Writing currently ends at approved script; audio state is separate. Resume must find either kind of unfinished work.
2. **Human review commands for edits and backtracking.** No general source/hook revision, approved-script versioning, full-audio approval/rejection or approval invalidation workflow exists.
3. **Audio preflight and content checks.** The helper does not enforce recorded authorization, compare to the approved canonical script, check spoken words/pronunciation, or cover all voice/model pricing rules. The agent must do these checks today.
4. **Reliable delivery.** Default to a named Desktop MP3 without opening a browser. Reuse existing artifacts when opening fails. The current generation CLI automatically launches Edge.
5. **Structured audio feedback and claim mapping.** Voice preferences are saved, but the writing runner does not load a structured audio feedback history. Script fact IDs are not sentence-by-sentence factual proof.
6. **Crawler/platform adapters and freshness.** Current writing research is subscription search + allowed public pages/PDFs. No general social/video ingestion or scheduled revalidation of queued cards.
7. **Scheduling, notifications and standing spending limits.** Not enabled or decided. Cron must preserve human gates and resume state; it cannot supply consent.

None of these integrations were built during this documentation task. Updated writing prompts are loaded by the existing runner, but no new live generation was run to evaluate their quality.

## Checks run

- `python3 -m unittest discover -s tests -q` → **56 tests passed**, 2.920 seconds. Offline fixtures; no network, model or paid voice calls. These cover existing behavior, not every proposed rule above.
- Saved approved script equals render text after removing delivery directions and normalizing whitespace: **true**.
- Approved MP3 manifest: `audio_approved`; full recording **78.602449 seconds**, **1,258,100 bytes**. File SHA-256 independently matched the recorded hash:
  `a3e6c21969ad5432b39f784210925212b1d54b6ad896d7954a80e5579140be33`.
- New Excalidraw: **76 elements**; JSON, unique IDs, reciprocal bindings, text dimensions and referenced elements checked. Shared viewer serves the saved drawing; helper confirmed a separate board opened. **23 local links** in the instruction pack resolve. No screenshots or viewer fit checks.
- Prior BOARD.md and both older diagram fingerprints preserved. No existing media changed, no new audio/video, no installation, push or spending.

## Authoritative artifacts

- [Approved narration](../approved-narrations/D6-6c917b49743b.md)
- [Full MP3 generation and explicit approval](../audio/D6-6c917b49743b/full-original-tyler-01/comparison.json)
- [Source queue](../source-queue.md)
- `01-content/harness/runtime/state.json` — ignored local state; do not replace with an empty file. Contains authoritative decisions and transient drafts; never dump it into chat.
- [Writing instructions](../writing-harness-prompts.md), [controller instructions](flow-and-recovery.md), [audio instructions](audio-instructions.md)

## Progress

Current task: settle this start-to-MP3 design before a new session. The article reuse question is pending; current rule remains ask first outside already saved queue items. The prior animation motion was rejected; its C illustration style remains selected. That feedback is preserved in the handoff, and no animation work belongs in this task.
