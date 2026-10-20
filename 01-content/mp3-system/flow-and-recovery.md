# Start-to-MP3 operating instructions

**The controller preserves choices; the writers explain the lesson; Drew approves the source, hook, words and recording.** This specifies the intended complete flow. Labels distinguish working code from agent-operated steps and future work.

**Latest research routing:** Drew confirmed the crawler is ready. [Crawler procedure](crawler-flow.md) governs new agent-operated research at source discovery, supporting science and depth retries. The configured runner now saves crawler requests and waits for validated imports. The session agent performs the crawler actions; direct network dispatch is not unattended. [ASCII whiteboard](whiteboard.md).

**Queue clarification:** [the source-selection specification](source-research.md) distinguishes “make the next episode from an approved source” from “research new choices for the queue.” The diagram’s saved-source route describes intended controller behavior; the CLI’s bare `start` starts a crawler request. The next trial explicitly uses `start --fresh`, keeping queued items and their priority. Research frequency is a pending editorial choice, not an active timer.

## Authority and boundaries

Latest explicit user decisions govern. This flow supersedes older hooks-first drawings and instructions that put voice generation after animation. Its output is an approved MP3 and its evidence package. It does not start video, captions, an outro, publishing, another session or another episode.

One active writing review at a time. Deterministic steps—saving choices, checking IDs, queues, hashes, locks and rotation—belong to the controller, not an extra creative model. Use models for finding evidence, assessing it and writing. Subscription fallback changes the worker, never the chosen source, hook or approvals.

The agent must distinguish four events: **source selected; hook selected; script approved; audio approved.** Liking a voice sample is a voice preference, not approval of a full recording. Liking a source is not approval of its hook. These events need their own records.

## 01 · Start and recover

**Owner:** controller + session agent. **Today:** writing entry and locks exist; unified audio resume is manual.

1. Read the current state, current review ID, approved scripts, source queue, source-use log, voice assignments and pending audio manifests. Never dump credentials or rejected scripts into logs.
2. If a human review is waiting, show that same review. If a generation failed, report the failed stage and resume from its saved checkpoint. Do not launch a fresh episode over unfinished work.
3. If an approved script awaits audio, offer/prepare that next stage; do not interpret `current: null` in the writing state as proof all episode work is complete.
4. Respect holds. `writing_enabled` gates hook/narration work; `board_updates_enabled: false` leaves BOARD.md alone. The new diagram is separately authorized by Drew’s diagram request.
5. For a new run, honor an explicitly selected queued source or queued second hook. Otherwise start source research for the next pest needing inventory. Bare `tools/d6 start` researches; it does **not** automatically consume `next_source_id`.
6. Create the run ID and prompt fingerprint; save before the expensive work. Acquire the writing lock before mutating state. On a duplicate trigger, return existing status.

**Future cron:** same entry checks, deduplicated scheduled trigger, then stop at the first human review. No timer or notification transport is active. Do not invent a schedule or spending allowance.

## 02 · Select the pest and research five sources

**Owner:** source researcher + independent validator. **Today:** public article/PDF path works.

1. Count distinct liked sources with `queued`, `in_use` or `awaiting_video` status per pest. Presented, skipped and completed sources do not fill the inventory target.
2. At three or more, advance research to the next understocked pest. Keep a fourth or fifth liked source. Wrap around; if all pest groups are stocked, stop new research until inventory is used.
3. Current working order: ants, cockroaches, termites, mosquitoes, rodents, spiders, scorpions, bed bugs, fleas and ticks, stinging insects, wildlife. This is an implementation default, not Drew’s final ranking. Preserve actual species separately from broad pest group.
4. Load source-specific preferences and reserved publications. Look for a useful homeowner lesson, interesting biology, a mechanism and honest limits. Five distinct sources should offer distinct lessons.
5. Use crawler stage R1 to search and read the actual pages. The current main-source allowlist is in `harness/config.json`. Return up to ten candidates internally so five can survive checks. The configured runner pauses at `waiting_research`; the agent uses the crawler and imports its checked result.
6. For each candidate record original URL, publisher/title/date, species, region, short lesson, limits and one to four facts with brief exact evidence. Total quoted evidence per publication is at most 25 words. Date unknown means `undated`, not invented.
7. Independently fetch the original page/PDF; check redirects/domains, quoted passage, common duplicates and source reservations. Failed access is not proof. Do not fill a short batch with guesses or search snippets.
8. Require five valid cards before display. Save IDs, fact IDs, check times and source-use reservations, then assign a new review ID.

**Readability:** show 1–5 directly in chat, each original link plus normally one or two sentences, never more than four/600 characters. Explain what the viewer would learn. No hook writing at this screen.

**Crawler boundary:** authenticated access is verified and Drew has resumed crawler use. Follow the repeatable agent-operated procedure now. The automatic writing-runner adapter must still return the same evidence fields and pass validation. The current authenticated client reports no browser/cookies; YouTube transcripts/demonstrations, Reddit, Facebook, X and unrestricted creator ingestion remain unimplemented or unverified in this flow. An inaccessible video is not “watched.” Social popularity is not scientific evidence. Credentials stay with their owner.

## 03 · Review and queue sources

**Owner:** Drew decides; controller records. **Today:** implemented.

- Pick one: save interest, choose it, mark it `in_use`, continue to depth check/hooks.
- Like several: save every liked number. `--first` sets which to use first; `save-sources` itself makes no model call and ends that research run. Then the agent explicitly starts the selected queued source when continuation is requested.
- Like several without priority: current code puts the first listed item first. If spoken intent is ambiguous, ask one short multiple-choice question before starting writing.
- Reject all: save the comment, reserve the shown sources against immediate repetition, research five fresh ones for that same pest. A source rejection is not hook feedback.
- Save for later/stop: preserve queue and review state. No automatic writing or paid audio.
- An unmentioned option is neutral, not disliked. Record the user’s actual reason, or leave it unknown.

**Never reuse a completed episode’s main/supporting publications, hook or script for another episode.** They are reserved while writing/audio/video is underway, and become used only at final MP4 completion. Shown publications stay excluded from fresh shortlists. An unchosen option remains neutral feedback. Keep all history.

## 04 · Check the chosen lesson; write hooks

**Owner:** depth assessor → hook writer → controller. **Today:** implemented.

1. Give the assessor the selected main source only and relevant preferences. Ask whether the source supports a substantial educational lesson and an honest opening; record one to five questions a narration could answer.
2. If shallow or unsupported, pause with the specific problem. Keep the selection on record. Offer a better source or narrower lesson for Drew to choose; never quietly replace the article. Use `revise sources` to return to discovery or `revise hooks` for a new opening. These preserve history and invalidate downstream active review IDs.
3. Load hook patterns and explicit hook feedback. Examples guide opening structure only. An empty library means provisional patterns, not proven performance.
4. Write exactly five distinct spoken hooks from the selected main source. Record source ID, supporting fact IDs and promised payoff internally.
5. Check count, duplicate wording, allowed fact IDs, chosen source and spoken formatting. Agent/editorial review checks actual meaning; fact IDs alone cannot prove it.
6. Show five numbered hooks in chat. Put context/source credit outside spoken text. Wait.

## 05 · Choose the hook

**Owner:** Drew + controller. **Today:** implemented.

Pick one and lock its exact text. A second explicitly saved hook is queued with the same source, not merged into the current hook. Rejecting all hooks makes five new hooks for the same source. Do not restart source research or change pest inventory on a hook retry.

A saved second hook is an alternative tied to its source. It cannot start a second episode while that publication belongs to an approved script or finished video. Keep the saved item as history. An otherwise eligible saved hook carries source reservation/pest metadata and rechecks old source evidence before narration.

## 06 · Plan and collect supporting science

**Owner:** evidence planner → targeted researcher → validator. **Today:** implemented, with editorial limits.

1. Read the exact selected hook, main facts, existing supporting facts and narration feedback.
2. Choose `reuse`, `research` or `blocked`. First narration without supporting evidence should research explanatory questions. Wording-only changes normally reuse checked facts. Missing mechanisms, depth or useful findings request targeted research.
3. Use crawler stage R2 to find up to four supporting publications per round from the separate configured support domains. Prefer original research/university extension. Record evidence, species, location and limits. Supporting publications deepen this lesson; they do not enter the liked-source queue or rotate pests. The runner emits a separate support request and waits for its checked import; crawler actions remain agent-operated.
4. Independently check every returned card. No acceptable evidence, a failed returned card or unresolved necessary question pauses writing. Preserve the main source/hook. Never treat an API success as scientific validation.
5. Save completed evidence before asking for narration so a writer failure does not repeat research.
6. For out-of-state studies distinguish general biology from local measurements. Do not present an Oklahoma or Mississippi result as Texas evidence; don't erase a material limitation simply to make speech smoother.
7. If evidence contradicts the hook, stop and explain. A replacement hook needs a new human selection. Do not quietly soften or rewrite the locked hook.

Every narration rejection returns through this assessment. More sources are useful only when they answer a real gap. The number of citations is not the quality goal.

## 07 · Draft, edit and display full narrations

**Owner:** narration writer, separate editor call and controller. **Today:** implemented; Drew still judges whether the writing works.

1. Supply [the active narration brief](../narration-style.md), the exact hook, checked facts and limits, current request, latest narration feedback and approved style examples. Exclude old contradictory batch requests.
2. Write five complete alternatives by default, or one focused narration through `revise narrations --count 1`. Every first paragraph is the exact hook. Keep one coherent lesson per version.
3. Have a separate editing call fix flow, repetition, unexplained terms, source credits, unsupported claims and the ending. Permit one editing pass. Unresolved problems stop presentation.
4. Check exact opening, requested count, duplicates, known fact IDs, forbidden wording and the exact approved final paragraph: “Helping you understand pests. Deep Six Pest Control.”
5. Record writing and editing calls, change notes and review status. These checks do not prove factual correctness or audience performance. Drew's explicit choice remains required.
6. Show each entire script in chat. Keep citations and production cues outside spoken text. No fixed duration is established; word-based estimates are not measured audio duration.

## 08 · Choose or revise narration

**Owner:** Drew + controller. **Today:** core choice/skip implemented.

Pick one → save exact words, hook, source, supporting evidence, fact IDs, approval time, model and prompt fingerprint. Mark its queued source `awaiting_video`; preserve the source history and earlier approved scripts. Only a recorded finished MP4 changes it to `used`. Advance next queued source priority. Writing state now ends; audio is the next agent-operated stage.

Reject all → remove current rejected bodies from the active review, retain concise feedback/settings/IDs/evidence, reassess research needs, and produce replacements at the current count using the same hook and main source. Do not copy rejected narration bodies into decision logs. Preserve archives Drew explicitly requested, including the ten original ensign-wasp narrations.

“Use 2 but change this sentence” is an edit request, not approval of unreviewed words. Show the edited complete script for approval. A factual change may require evidence; a hook change returns to hook review. Automatic targeted-edit/reapproval commands are not built yet.

## 09 · Prepare the approved script for audio

**Owner:** audio preparation agent + deterministic voice reservation. **Today:** manual specification; reusable helper supports rotation.

Follow [audio instructions](audio-instructions.md). Preserve the approved spoken words. Keep a clean approved text and a separate render text for supported delivery controls. This episode proved a natural original script worked better than an automatic “AI voice” rewrite.

Reserve Tyler → Chris → Liam once per narration ID. Retries/revisions of that same episode keep the assignment. The helper advances the rotation at reservation before generation, not at listening approval. A cancelled episode can therefore consume a rotation slot; preserve that assignment instead of silently rolling back shared state. This is current behavior, not a separately chosen cancellation policy.

Use hook-only auditions when changing an unwanted voice/delivery; include a short problem phrase when the pronunciation issue is outside the hook. Auditioning is a separate bounded authorization, not permission for full scripts in all voices.

## 10 · Authorize, generate and check the MP3

**Owner:** session agent authorizes scope from Drew’s request; audio tool executes. **Today:** separate tool, not wired into writing approval.

1. Identify approved script/version, assigned voice, render text, model/settings, requested number of outputs and destination. Check existing complete results first.
2. Confirm explicit authorization covers this generation. Script selection alone does not grant unlimited paid calls. Future standing budgets require Drew’s decision. No top-ups or plan changes.
3. Read the existing key securely from the environment. Never put it in prompts, manifests, command arguments or logs. Missing login is a precise blocker, not permission to search secrets broadly.
4. Check available credits and the applicable billing assumptions. The existing helper’s character estimate applies to its verified trial setup, not every model/voice. Recheck current provider details before changing those assumptions.
5. Lock the audio job. Check text hashes, file existence and prior request state. Checkpoint `request_started` before the request. Do not overwrite results or silently retry interrupted billing.
6. Save received bytes, request ID and audio hash; probe MP3 format/duration, then mark complete. A valid codec is not proof of correct pronunciation or factual speech.
7. Agent checks narration identity and listening defects before presentation. If a check cannot be performed, say so. Do not invent an ASR/listening pass; no automated audio-content QA currently exists.

## 11 · Present, listen, repair

**Owner:** session agent + Drew. **Today:** player helper works; review recording is manual.

Show which script/voice this is and its measured duration. Open a review only when requested/authorized. Under the current browser rule, default to a clearly named MP3 copy on the Windows Desktop with its exact path; verify the copy hash. The helper prints file paths and does not launch a browser. The agent still makes and verifies the Windows Desktop copy.

Never regenerate because the file is hard to find. Reopen the existing authorized player or copy the existing MP3. No autoplay surprises. “The file exists” is not evidence Drew can see the player.

Classify the feedback: script/content → step 08 (and 06 if needed); pronunciation → corrected pronunciation handling and a short authorized test; flat delivery → hook audition with the same voice first; disliked voice → alternative hook auditions. Keep the clean script and existing approved choices unless Drew changes them. Re-render the full version only within authorization after the needed adjustment is agreed.

## 12 · Approve and freeze the output

**Owner:** Drew approves; agent records. **Today:** done manually for the first episode.

Only explicit approval moves the audio to `audio_approved`. Bind the decision to the exact audio SHA-256, script identity, voice, settings, variant and time. Preserve the full approved script, main/supporting evidence and their limits, render text, generation record, MP3 and feedback. A later change makes a new candidate; it does not inherit approval.

Stop. The approved package becomes input to a later MP3-to-video session. Do not start video or an outro from this completion event.

## Recovery table

| Event | Required action | Preserve / limit |
|---|---|---|
| Silence, old number, duplicate click | Wait, or reject stale review ID; show current choices | Never infer a choice; no extra generation |
| Unclear “4” with multiple active displays | Identify the intended review before acting | No guessed source/script/audio approval |
| Model quota/login/network failure | Try configured subscription fallback once per route; otherwise pause | Same stage, selections and evidence; no paid API fallback |
| Invalid model JSON or wrong hook/fact IDs | Pause stage; correct/retry deliberately | Do not shop through models until one passes |
| Two writers or duplicate cron trigger | Lock/deduplicate; report active run | No competing choices or paid calls |
| Research finds fewer than five | Report shortage and failed checks; retry eligible sources | No fabricated fifth source |
| Source is inaccessible or has changed materially | Stop affected claim; find checked support or ask about source/hook revision | Prior choices remain historical; cached evidence is not a new live read |
| Contradiction or unsupported hook | Explain conflict; get a new hook/source decision if needed | No quiet rewrite |
| “More scientific” | Assess specific missing mechanisms/findings; research those | Do not add jargon or citations merely for count |
| “Sounds too formal” | Rewrite from existing adequate facts | Keep the exact selected hook unless Drew changes it |
| New preference contradicts old preference | Use newer explicit comment; keep decision history | Don’t invent a universal rule from one skip |
| Source queue empty / every pest stocked | Research next understocked pest / stop new research | Queued sources remain available for writing |
| Lost runtime state with existing history | Stop and restore actual state | Never recreate empty state over history |
| Display/export failed after saved choice | Rebuild derived display without model call | State is authoritative; board hold still applies |
| Audio exists with matching hashes | Deliver it again | No second bill |
| Audio text/file changed after completion | Stop; prepare a new reviewed version | Do not overwrite or inherit approval |
| Timeout, HTTP error, `request_started` | Reconcile provider history before any retry | An error may still have consumed credits |
| Bytes received but validation failed | Inspect saved bytes/recover existing result first | No blind generation retry |
| Insufficient credits / unclear pricing | Pause with the exact missing authorization or information | No top-up, subscription change or substitute paid provider |
| Wrong pronunciation/tone/voice | Follow step 11’s targeted audio path | Same chosen source/hook/script unless explicitly revised |
| User cannot find audio | Deliver the existing file visibly | This is a presentation failure, not a voice-generation failure |
| User stops midway or starts a new chat | Save current checkpoint and concise progress | Resume only remaining work; no fresh approval assumed |

## Preference memory and output contracts

Keep source choices, hook choices, narration comments and audio preferences distinguishable. Research receives the latest 12 source decisions. Hook writing receives recent hook decisions and non-source feedback. Narration planning, writing and editing receive the selected hook, consolidated style brief where applicable, current request/preferences, latest narration feedback, approved outro and the last two approved script examples. Older contradictory batch requests stay out of narration context. All existing decision records persist locally; these preferences are context, not model retraining.

Current model contracts include `CARD`, `DEPTH`, `EVIDENCE_PLAN`, `SUPPORT`, `HOOKS` and the count-aware `narration_schema()` in `tools/d6_harness.py`. Editing adds `changes` and `unresolved` fields. Match those schemas; do not add undocumented JSON fields to live calls. Actual writing states include `generating`, `waiting_research`, `waiting_sources`, `waiting_hooks`, `waiting_narrations`, `error`, then approved-script storage. Audio has its own per-variant `prepared → request_started → received → complete` and review-level `waiting_audio_review → audio_approved` records. A unified episode status is a future integration, not an existing state machine.

Checks match quoted words and known fact IDs. They do not automatically validate every paraphrase or inference. Claim-by-claim editorial review and human listening remain necessary. Saved preferences provide context; they do not retrain model weights or guarantee each batch improves.

## Final-MP4 receipt — owned by the video session

After the other session finishes and verifies the full video, it runs `tools/d6 complete-video EPISODE_ID FINAL_MP4 --audio-manifest APPROVED_AUDIO_MANIFEST --final`. This reads the MP4; it does not render, alter or publish it. The command verifies episode/script/audio identity, video and audio streams, duration and file hash, then saves the completion receipt under the writing lock. Identical completion is idempotent; a different claimed final file pauses for review. Only this event marks sources used. Full semantic synchronization is the video operator’s responsibility.

[Current edge-case review](edge-cases.md) governs the newer safeguards. Start-to-MP3 work stops after recording the full-audio approval.
