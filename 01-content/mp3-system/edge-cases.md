# Review: start through approved MP3

**Ready for a guided trial with fresh research. Human choices, crawler operation and listening checks remain part of the flow.** This October 19 review supersedes the earlier [design audit](audit.md).

## What “used” means

| State | Meaning | Available for another episode? |
|---|---|---|
| Shown | Candidate appeared in a review; neutral unless Drew gave feedback | Excluded from fresh shortlists to avoid repeated choices |
| Queued | Liked and saved, not started | Yes, when explicitly selected; next trial skips these |
| In progress | Selected for the active writing run | Reserved for that episode |
| Awaiting final MP4 | Script approved; audio/video may still be underway | Reserved for that episode |
| Used | Finished MP4 explicitly recorded and checked | Never reused for another episode |

This applies to the main publication, supporting publications, selected hook and approved script. Same-episode research/writing/audio retries retain their evidence. An alternate saved hook stays saved but cannot start a second episode using an already reserved source. Voices, branding and writing patterns remain reusable as previously requested. Detecting a paraphrased repeat of a lesson still needs editorial judgment.

## Holes reviewed

| Case | Handling now | Limit |
|---|---|---|
| Script approval prematurely consumed source | Source moves to `awaiting_video`; completion receipt alone changes it to `used` | Other video session must record final completion |
| Fresh trial accidentally consumes queued sources | `start --fresh` preserves old queue and priority | New liked choices are added normally |
| Same source through another URL/title | URL, publication identity, page digest and exact lesson checks; supporting sources included in reservations | Renamed or paraphrased mirrors need editorial checks |
| Saved second hook reuses a source | Existing episode ownership blocks it; saved item remains | Alternate hooks are alternatives, not permission for another video |
| Source changed while waiting | Main-source checks older than 24 hours are fetched again; changed/unreadable evidence stops writing | Supporting evidence also needs agent freshness review after a long pause |
| Crawler unavailable or returns too little | Keep request and queue; report missing access, evidence or coverage | No silent ordinary-search fallback; current public-page allowlist still applies |
| Wrong or repeated crawler result | Run/request/stage/client must match; actual job ID and project evidence file required | Provenance fields are operator records, not cryptographic proof of crawling |
| Crash importing sources/support | Atomic checkpoint includes evidence provenance and clears pending request; resume remaining stage | Live crawler mutations still require receipt reconciliation |
| Shallow source, wrong hook, changed direction | `revise sources`, `revise hooks`, or `revise narrations` invalidates downstream active review IDs | Approved-script revisions require a deliberate agent-managed revision; never overwrite approval silently |
| First science step incorrectly chooses reuse | Empty support forces targeted research | Facts and causal claims still need editorial verification |
| Rejected scripts need depth or wording | Reassess evidence; research gaps or retain adequate same-episode facts | More citations alone are not better education |
| Stale or double choice | Review IDs and writing lock reject replay | Writers must use the CLI under its lock |
| Changed words/settings before TTS | Canonical approved words and request fingerprint checked | Pronunciation and model controls still require judgment |
| Duplicate paid audio request | Episode lock, unique outputs and persistent request receipts | Uncertain billing stops for provider-history review |
| Missing authorization/credits | Bounded recorded authorization required before a new request; balance checked | Operator must verify current pricing/model support; authorizing command cannot invent consent |
| File created but process interrupted | Preserve bytes and request state; block another paid request | Recover received files/provider history manually; no blind reset to `prepared` |
| Voice audition mistaken for final approval | Auditions cannot receive full-MP3 approval | Voice preferences are agent-recorded separately |
| Old or altered MP3 approved | Audio decision binds review ID, words, settings and file hash | Legacy first approval is explicitly flagged as legacy |
| User cannot find MP3 | Deliver existing file; generator prints paths and does not open browser | Agent copies to Windows Desktop and compares hashes |
| Preview MP4 mistaken for completed video | Requires `--final`, approved audio, video/audio streams and sufficient duration | The video operator verifies full content and narration synchronization |
| Another session works on video | Shared state lock for completion receipt; video assets untouched here | Keep episode ID and approved audio identity across sessions |

## What was checked

**94 offline tests passed in 4.059 seconds; `git diff --check` passed.** Fixtures cover source/hook/narration gates, both crawler imports, crash recovery, queue preservation, source ownership, migration, final-MP4 receipts, audio authorization, duplicate calls, canonical words and audio approval. No research, model or paid TTS call was made in this review. [Saved proof and preserved-file hashes](review-proof.json).

The approved Tyler MP3 remains 78.602449 seconds with SHA-256 `a3e6c21969ad5432b39f784210925212b1d54b6ad896d7954a80e5579140be33`. The three untouched queued ant sources remain saved; next discovery pest is cockroaches. No new run has started.

## Next builds after real trials

Prioritize fixes exposed by actual trials: a single resume screen joining writing/audio status; formal approved-script revision history; automatic Desktop delivery; crawler action dispatch and recovery; speech-content checks. Cron, broad social/video ingestion and unattended production remain outside the current guided trial. Record observed failures before expanding the system.

[Next-session instructions](NEXT-SESSION.md) · [Crawler procedure and import contract](crawler-flow.md) · [Audio instructions](audio-instructions.md)
