# Local writing flow

**Required flow: choose a source → choose a hook → supporting research → choose a full narration → authorized MP3 → listening approval.** Source 1, hook 4, original narration 2 and Tyler’s full MP3 are approved. Writing and audio are still separate tools. Every narration option repeats the exact selected hook. The runner uses Codex/Astra on Drew’s ChatGPT subscription. Show choices in chat; BOARD.md stays on hold. [Current complete flow and gaps](../mp3-system/README.md).

## Commands for the agent

Current configuration uses the crawler request/import bridge. Next trial: `tools/d6 start --fresh`; leave the old queue untouched. [Exact crawler import contract](../mp3-system/crawler-flow.md).

Run from the project root:

```bash
tools/d6 status
tools/d6 start
tools/d6 save-sources REVIEW_ID 1 2 4 5 --first 1
tools/d6 choose REVIEW_ID 2
tools/d6 choose REVIEW_ID 2 --save 4
tools/d6 choose REVIEW_ID 2 --feedback 'I like the direct question.'
tools/d6 skip REVIEW_ID --feedback 'Make the wording more natural.'
tools/d6 retry
tools/d6 show
tools/d6 start --queued QUEUED_ID
tools/d6 start --source SOURCE_ID
tools/d6 refresh-hooks
```

Use the exact current review ID from `status`; stale choices fail without making another model call. `start` saves a crawler request and pauses; the session agent performs it and imports results. A successful source import stops at five previews (normally one or two sentences, maximum four). `choose` advances source → hooks → narrations → saved script, stopping for a new choice each time. Source skip researches five new sources; hook skip keeps the chosen source; narration skip keeps the chosen hook and source. `--save` queues a second hook with the selected source. `retry` resumes an interrupted stage. `show` repairs the board and approved exports without another call. Give only concise feedback, never a rejected narration body.

**Holds override writing commands:** `writing_enabled: false` makes a source `choose` save that source without generating hooks. Starting queued writing or advancing it is blocked. Drew has now resumed writing, so this flag is true. `board_updates_enabled: false` still prevents even `show` or state saves from updating BOARD.md. Leave drawings untouched until requested.

Narration generation and approval require a selected hook. Show full scripts directly in chat, including the exact hook and approved sign-off. Five options remain the default; `tools/d6 revise narrations --count 1 --feedback "..."` focuses on one, and `--count 5` restores five. Each draft passes through one separate editing call using [the narration brief](../narration-style.md). Unresolved problems or invalid output stop presentation. `review-hooks` recovers an old premature narration batch that has no selected hook: discard those drafts, preserve the chosen source and queue, then generate five hooks and wait. It records no taste preference or hook approval.

`save-sources` saves all liked numbers without a model call; `--first` sets priority. Sources 1, 2, 4 and 5 from the current decision are saved, source 1 first. Source 3 is neutral. Read [the queue](../source-queue.md) or `status`; do not infer likes from silence. `start --source SOURCE_ID` uses that exact saved card without researching it again. An approved narration marks its source `awaiting_video`. A declared, checked finished MP4 alone changes it to `used`. Main/supporting publications, hooks and scripts are never reassigned to another episode.

`pest_rotation` gives the working order, with all ant types grouped as ants by default. `sources_per_pest` is three. Count liked queued/in-use/awaiting-video sources, not merely displayed sources. A fourth liked item is kept. Research moves to the next pest needing inventory; sources with a completed final MP4 stop counting, allowing later replenishment. If all groups are stocked, new research stops. Current next pest: cockroaches. The order and grouping are stated defaults rather than Drew's finalized taxonomy. [Research brief and platform status](../research/research-brief.md).

For the pre-existing five-source hook batch only, `tools/d6 review-sources` backs up the old state under ignored `runtime/migrations/`, reuses its already checked cards and returns to source review. It creates a new review ID, makes no model call and invents no user rejection.

Hook picks and skips retain the five opening texts and the decision. The latest twelve hook reviews are supplied to future hook calls, including after restarting or changing models. Narration calls use the exact selected hook and the focused narration brief instead. Choosing or saving a hook is a provisional positive signal; unchosen hooks are not automatically disliked. A skip without a comment is a weak signal with no assumed reason. Pass Drew's stated reason with `--feedback` on either `choose` or `skip`; do not invent one. Explicit comments guide the writer most. Narration skips stay separate from hook preferences, and rejected narration bodies remain excluded from decision history. This is saved context for the writer, not model retraining or a guarantee of better hooks.

Source reviews separately retain the five titles, links, short summaries, species/region, choice and comments. The latest twelve source decisions and source-specific comments feed future research calls. Hook/narration rejections are excluded from research preferences. A source choice expresses interest; it does not relax evidence checks. All decision records persist locally, while only the most recent twelve of each kind are supplied at once.

## Educational depth and supporting evidence

Main-source research now prioritizes detailed biology, useful mechanisms and research findings, and describes depth in the short source preview. A separate editorial depth assessment runs before hooks and pauses if the main source cannot support a substantive lesson. Hooks use only the main source; wording examples do not supply pest facts.

Before narration, an evidence planner chooses reuse, targeted research, or a pause for conflicting/insufficient evidence. The first narration without supporting evidence requests research. A later skip triggers another assessment: writing feedback can reuse evidence; missing depth requests specific facts. This model judgment is not a deterministic quality guarantee.

Supporting research uses primary/university domains configured separately under `support_domains`. Returned facts must pass the same independent page, quote, publication and domain checks. Missing/unreadable evidence or unresolved conflicts stop writing. New facts retain source IDs and limits, are supplied to narration only, and are exported with approved scripts. Supporting publications do not count as liked queue items or change pest rotation. Completed evidence is checkpointed so retrying a failed writing call does not repeat research.

The current older batch also contains manually checked supporting references with their access methods recorded. Those were gathered before this automation existed; some used web-search full-page excerpts. Future automated supporting facts require independent fetching. Neither quote matching nor the editorial model proves every scientific inference correct.

## Models

`config.json` selects the current route. `tools/d6 provider codex` selects the default Codex route; `tools/d6 provider auto` selects the default Claude-first route with OpenAI fallback. Explicit `role_routes` take precedence for their named stage and can set provider, model, fallback order and effort. Other stages retain the default route. Per-role Claude defaults also remain available under `claude_models`. Every route uses the same subscription-only runner.

The live probe rejected `gpt-6.1-sol` as unavailable in this CLI/account and then succeeded with `gpt-6-astra`. Astra is now first. Sol remains the second configured backup; its availability is not confirmed. A quota, login, network, timeout or unavailable-model failure tries the next route. Invalid content pauses for correction instead of silently generating through every model. Each invocation tries a route at most once.

Narration writing and editing use Astra at high effort, with the existing Sol backup. Other stages keep their earlier routing. The October 20 attempt to test Opus 5.5 stopped at its subscription limit before a draft; no comparison winner was established. [Saved trial records](../mp3-system/narration-refinement/).

Codex is restricted to ChatGPT authentication. Claude must report subscription authentication. API-key/token environment variables are removed from child calls. Writing runs have no web search; research runs have web search. Shell tools, optional plugins and helper agents are disabled for Codex calls. Model calls are ephemeral, and raw model output is not saved as project logs. No shared credentials or global settings are changed.

## Records and recovery

- `runtime/state.json`: atomic current batch, source reservations, liked source queue, next source, rotation cursor, decisions, queued hooks and approved scripts. Ignored by Git because it temporarily contains unchosen narration text. It is the authoritative local state; preserve it between sessions.
- `../source-queue.md`: readable export of queued/in-use sources, first source and next research pest. It contains source metadata, not rejected narration text.
- `../approved-narrations/`: one readable export per approved script, with source, limits, model and prompt version. Rebuilt from state when needed.
- `../source-log.md`: source-use metadata, including unchosen or skipped hooks. Used publications stay unavailable by default.
- `../../BOARD.md`: a replaceable current-choice block above existing board history. Rejected narration bodies are removed on skip/selection, including after a model failure. The board is tracked; never commit or push it while it contains unchosen narration bodies.

One process holds a lock through each generation step. State saves before derived displays; `show` repairs displays after an interrupted write. No human choice is inferred from elapsed time or from a model switch.

## Checks and limits

Run `python3 -m unittest discover -s tests -v`. Tests use temporary fixture projects and make no network/model calls. The first live run researched five different publications, checked their short quoted evidence against separately fetched pages, and produced five hooks with Astra.

Quote matching proves the quoted words occur on the page. It does not prove every paraphrase, regional inference, or proposed hook is correct. Publication URL/title/content checks catch common duplicates, not every renamed mirror or paraphrased repeat. Scripts still need Drew's review. Source facts, timestamps, exact hooks and limits remain attached internally.

The hook library starts empty, so the first batch used explicitly provisional opening patterns. `refresh-hooks` collects text-based candidates and preserves existing examples; it does not claim to watch footage or prove performance. No Saturday timer, Telegram integration, automatic audio handoff, publishing or paid API fallback is enabled. Separate authorized audio generation has been used successfully.

Drew has now confirmed the crawler is ready. [The repeatable crawler procedure](../mp3-system/crawler-flow.md) defines where and how an agent uses it. **The configured CLI emits R1/R2 requests and imports checked results; the session agent performs crawler actions.** Provenance is saved with each import. Unattended network dispatch remains future work. The current validator supports trusted public pages/PDFs; YouTube transcript ingestion is not implemented. [Current access proof](../research/2026-10-19-crawler-workflow/README.md).

[Build proof](build-proof-2026-10-19.md) · [Writing instructions](../writing-harness-prompts.md)

## Audio review

After narration choice, the next requested review is an MP3. The first comparison is historical: Drew preferred the original narration, approved Tyler/Chris/Liam for rotation, then approved the full Tyler recording in `../audio/D6-6c917b49743b/full-original-tyler-01/`. Do not repeat the comparison or rewrite the script automatically. [Current voice and review instructions](../mp3-system/audio-instructions.md).

The original two-file comparison is historical. Verify/deliver existing recordings; new jobs follow the exact authorization and review commands in [audio instructions](../mp3-system/audio-instructions.md). It reads an existing `ELEVENLABS_API_KEY` or `ELEVEN_API_KEY` from the environment; never paste keys into commands or save them. It checks balance, avoids overwriting results, and checkpoints before each billable call. An interrupted request requires provider-history review before retry. Completed runs do not regenerate. No top-up, plan change or automatic video step exists. The balance check assumes this comparison’s verified standard-rate voice/model; it is not a general pricing engine.

Current helper behavior: after generation its CLI prints the saved file paths. **Current display instruction:** the session agent copies the exact MP3 to the Windows Desktop and verifies the hash; browser/player opening requires authorization. Do not regenerate to repair a delivery problem or assume a window check means Drew can find it.

Voice auditions: the audio helper accepts two or three explicitly authorized variants, with per-variant voice IDs and display labels. The completed hook comparison is `../audio/D6-6c917b49743b/hook-voices-01/comparison.json`, using Eleven v4 and three different voices. Drew approved all three, then the full Tyler recording. Delivery tags are render instructions; canonical spoken hook wording remains unchanged. New voice tests use short auditions; the approved rotation does not require repeating auditions on every episode.

Approved voice rotation: `../audio/voice-rotation.json` stores Tyler, Chris and Liam in that order, plus assignments and next index. Full-narration manifests must set `voice_rotation_file` relative to their folder. The helper assigns one voice per approved narration ID under a lock; retries and revisions retain it. The next index advances on first assignment, so even a failed request keeps its assignment rather than reshuffling voices. Auditions do not consume rotation slots. Single-voice full narration is supported alongside two/three-option reviews. Current full narration uses Tyler; Chris is next.

## Recovery and final-video handoff

- `tools/d6 import-research RESULT_JSON`: admit the result for the exact pending crawler request.
- `tools/d6 revise sources|hooks|narrations --feedback 'Drew’s reason'`: return an active run to that review, preserving source history and invalidating downstream choices. Approved-script revisions remain agent-managed; do not silently overwrite saved approval.
- `tools/d6 migrate-lifecycle`: idempotently correct old script-time `used` labels to `awaiting_video`, preserving a local backup.
- `tools/d6 complete-video EPISODE_ID FINAL_MP4 --audio-manifest APPROVED_AUDIO_MANIFEST --final`: the video session records its finished MP4. Requires approved matching audio, valid video/audio streams and sufficient duration. The operator must verify full content and synchronization; a preview is not a final video. The receipt consumes main/supporting sources exactly once.

Do not call completion from this start-to-MP3 session. No MP4 has been declared complete here.

[Edge cases and implementation limits](../mp3-system/edge-cases.md) · [Next-session trial](../mp3-system/NEXT-SESSION.md)
