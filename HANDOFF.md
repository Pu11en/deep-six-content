# Session handoff: October 20, 2026

**This is a checkpoint of unfinished work. Drew authorized pushing the current project so another session can continue.**

## Resume the approved ensign-wasp narration

- Episode: `D6-01096ba333e3`. Drew approved v6 option 3, exactly 138 words, including hook 4C and the approved Deep Six outro.
- [Approved script](01-content/approved-narrations/D6-01096ba333e3.md) · [Approval and exact-text checks](01-content/mp3-system/narration-approval.json).
- No audio exists for this episode. Chris is next. Prepare one full recording with the same voice through the outro, obtain bounded spending authorization, then record Drew's listening decision.
- Do not start fresh research or ask Drew to choose a script again. Follow [the current narration checkpoint](01-content/mp3-system/NEXT-SESSION.md).
- The writing runtime remains local and ignored. A [portable workflow checkpoint](01-content/harness/checkpoints/2026-10-20-stop/README.md) preserves approvals, source reservations and queue state for a fresh checkout. Never replace newer runtime state with it.

## Work still unfinished

- The ensign-wasp MP3, researched drawings and finished video.
- System design, diagrams and production automation. Preserve the existing drafts and open decisions; this push does not approve or complete them.
- Adding the website URL to the approved outro. Drew withdrew the owner-face idea.
- Cloud portability and an actual cloud render test. Cloud sessions remain possible after setup; [cloud handoff](CLOUD-HANDOFF.md).

After MP3 approval, continue with [the video flow](01-content/animation/VIDEO-FLOW.md), [video checkpoint](01-content/animation/NEXT-SESSION.md), and [approved outro](01-content/outro/APPROVED-OUTRO.md). Preserve the already approved fire-ant video.

The checkpoint includes drafts, editable diagrams, code, research, original assets, review media and approvals. Temporary frame caches, raw CLI logs, job locks and installed dependencies stay local. No files were deleted.

Checks: 100 offline workflow tests passed. The portable state is an exact copy of the current runtime. The approved script remains exactly 138 words. These checks do not mark unfinished design or media work complete.

## Earlier session history

Everything below records earlier work. The October 20 checkpoint above governs continuation and supersedes old instructions to start a fresh trial, discard narration archives or defer this authorized push.

## Video session (approved MP3 to finished video): flow saved and automated

Drew loves the full fire-ant video (Desktop: `Deep Six - Fire Ants Full v2.mp4`) and wants this style for every video. The method is saved in `01-content/animation/VIDEO-FLOW.md` and runs through `make_video.py`. Default model: Opus 5.5 at max effort; GPT-6 Sol, then Astra, when Claude credits run out. Drew rated Sol's test better than Astra's. The ChatGPT Codex usage limit ran out during testing on October 19; access was back the same evening. Everything a future MP3-to-MP4 harness (Opus 5.5, Astra or Sol) needs from that run is in `01-content/animation/HARNESS-NOTES.md`. Videos go to the Desktop only; never open a player. Closer, outro and music are later sessions. Next steps: [video NEXT-SESSION](01-content/animation/NEXT-SESSION.md).

## Latest checkpoint: finish locally; next chat runs the fresh trial

Drew clarified **used means a completed final MP4**. Main/supporting publications, hooks and scripts stay reserved while an episode is underway and cannot be recycled into a new episode. Source approval, script approval and MP3 approval are separate events. Saved alternative hooks do not authorize another video using that source.

Reviewed and built lifecycle guards, crawler request/import checkpoints, active-stage backtracking, source freshness checks, audio authorization/canonical-word checks, duplicate-request receipts and explicit full-MP3 review. [Current review, edge cases and limits](01-content/mp3-system/edge-cases.md) supersedes earlier unfinished-status notes below. Crawler actions, listening QA and Desktop delivery remain agent-operated. No unattended scheduling is enabled.

**Next chat:** follow [NEXT-SESSION.md](01-content/mp3-system/NEXT-SESSION.md). Run `tools/d6 start --fresh`; keep the three queued ant sources and priority. Current next research pest is cockroaches; next voice is Chris. Show each source/hook/script review directly in chat, stop for Drew's choices, then prepare one authorized full MP3 and record listening approval. Start additional trials only when requested. No new run was started in this closure task.

Another active session owns MP3-to-finished-video, excluding the outro. It records final completion with `tools/d6 complete-video ... --final` after verifying the full MP4. Do not infer completion from preview files. This session changed no video assets. Everything is saved locally; no push, cleanup or paid generation.

**Closure proof:** 94 offline tests passed; 66 documentation links resolve. Corrected one legacy source status with a local state backup. Verified all three queued source records and priority, approved scripts and the 78.6-second Tyler MP3 unchanged. [Short review](01-content/mp3-system/review-summary.md) · [Machine-readable proof](01-content/mp3-system/review-proof.json). Shared BOARD.md differs from an earlier fingerprint and was left as found; this task kept board updates disabled.

## Current task: establish start → approved MP3

**Latest layout request:** Drew approved the wording but wanted more boxes and a clearer top-to-bottom flow. Rebuilt the existing start-to-approved-MP3 board with 33 boxes, four choice diamonds and connected retry paths; all 47 text blocks preserved. [Layout research and checks](01-content/research/2026-10-19-flowchart-layout.md). Same board URL; no video or automation changes.

**Session ownership:** Drew has another active session handling **approved MP3 through finished video, excluding the outro**. This session owns source discovery, hooks, narration and approved MP3 only. Do not edit animation/video work or launch another video session. The outro remains a separate discussion. Current focus here: clarify saved-source reuse versus new discovery, the actual crawler request, source-selection criteria and research frequency.

**Current clarification:** updated the existing start-to-MP3 Excalidraw board to plain-language labels and an explicit saved-source bypass. New discovery now shows the prepared request, caller-directed crawler searches/reads, evidence checks, and five source choices. [Source review note](01-content/mp3-system/source-review.md), [criteria and timing](01-content/mp3-system/source-research.md), and [unsent API request example](01-content/mp3-system/source-request.example.json) are saved. Three approved ant sources wait; tawny crazy ants is first. Next discovery pest is cockroaches, which is independent of the next episode. Asked one optional question: keep stocking other pests during separate queue checks, or research only on request/when empty? Pending; no source schedule or crawler adapter was enabled. No research job or media work ran for this clarification.

**Latest update:** Drew confirmed the crawler is ready and requested a repeatable research flow plus **ASCII, top to bottom**, for copying onto his physical whiteboard. [Whiteboard layout](01-content/mp3-system/whiteboard.md) · [Crawler stage procedure](01-content/mp3-system/crawler-flow.md). Current authenticated access passed through MacBook localhost:8766 using existing client `imac-research`; token stayed in memory. Saved fresh capabilities/API contract and access proof under `01-content/research/2026-10-19-crawler-workflow/`. No job or new content generation was started. Current client reports public search/read/evidence tools, no browser/cookies/model calls/paid fallback. Source discovery and supporting science are the main crawler points; depth retries may revisit science, with separate hook-library maintenance and optional voice troubleshooting. The automatic Python writing runner is still on its old subscription-search path; wiring is unfinished. This is a repeatable agent procedure, not a claim of an implemented crawler adapter. The earlier Excalidraw drawing was preserved; the latest requested view is ASCII.

**Drew wants to finish this diagram, every stage’s instructions, review gates and edge cases. The other active session owns video; the Deep Six outro remains separate.** Start with [the short MP3 system note](01-content/mp3-system/README.md) and [new Excalidraw flow](http://localhost:3003/boards/0d05ffd0809f0bbe1220a047).

Completed this task: audited actual code/state, corrected stale writing/audio status, expanded the loaded writing system instructions, documented controller and audio instructions/retry paths, and made a separate current diagram. Existing 56 offline tests passed. Approved script/render words match; the approved MP3 hash matches its manifest. No new research/model/TTS calls, installations, media changes or publishing.

Current truth: source 1 → hook 4 → original narration 2 → Tyler’s full 78.602449-second MP3 are approved. Three ant sources remain queued; next research pest is cockroaches. Voices rotate Tyler → Chris → Liam; Chris is next new narration. Keep the same assigned voice for revisions.

Writing and audio remain separate tools. Unified episode resume, edit/backtracking commands, audio-content QA, enforceable generation authorization, audio review/version handling, Desktop-first delivery and crawler integration are not built. [Audit and limits](01-content/mp3-system/audit.md). The revised writing prompts load on the next writing call; no new live quality trial ran for them.

One optional policy question is pending: may future episodes reuse an already seen/used article? Keep **ask first** as the current rule outside explicitly saved queue items. No permanent audio spending allowance, cron time or narration duration is decided. Continue discussing this flow one useful question at a time; don't ask technical decisions Drew expects us to handle.

The prior motion preview was **rejected**: too little motion, too few scenes, visuals did not explain the narration’s specifics, and subtitle timing did not match speech. C’s illustration style remains selected. Preserve that feedback for the later MP3-to-video session. The old motion review JSON still says pending; it is not approval. No video artifact was edited during this MP3 task.

BOARD.md and both older drawings retain their pre-task hashes. The newly requested diagram is separate. Opened the new Excalidraw board; the short note is the entry point. Do not launch another session until this flow discussion is finished and Drew requests the move.

## Previous position — superseded by the current task

The preview review request below is historical; Drew has since rejected its movement as described above.

**Drew chose C, cut-paper storybook, with “c”. The [10.76-second moving preview](01-content/animation/episodes/D6-6c917b49743b/motion-paper/review.md) is ready for his movement review.** Current candidate: `motion-paper/renders/motion-v2.mp4`, SHA-256 `ea772c18ca5fec3ac3fca72b35ddb181dbf7ea43944eab956e3902dad2f9e5f0`. Its review decision is pending. Save Drew’s explicit feedback; approval must bind to this video fingerprint. Unchosen styles remain available, not disliked.

C’s illustration approval is saved in `style-options/options.json` and `paper/renders/frame-v1.review.json`. Astra ultra authored motion in one subscription request. The ant walks along the ledge with articulated legs and carried larva; antennae tuck for roof clearance. Selected original artwork is preserved. [Motion checks](01-content/animation/episodes/D6-6c917b49743b/motion-paper/motion-checks.json).

Source 1, hook 4, original narration 2 and Tyler’s full 78.6-second MP3 remain approved. This preview uses the original recording at 46.40–57.16 seconds. Cached offline speech recognition matched all 31 excerpt words; no voice regeneration. Videos remain 1080×1920 with the Deep Six ad palette. The v2 MP4 contains 258 frames at 24 fps: 10.75 seconds video and 10.76 seconds audio/container. V1 is preserved after an export frame-count rounding check failed; that was not a style/motion rejection.

Use `npm run motion -- episodes/D6-6c917b49743b/motion-paper/scene.json` from the animation folder to reuse the current video. `tools/open_d6_video.py` now uses native Windows ffplay, titled **Deep Six Video Preview**. It centers the window, confirms foreground focus and sends pause/rewind; Space plays/pauses, Esc closes. Drew could hear but not find the earlier WSLg player, so merely checking that a window exists is insufficient. The same verified MP4 was reopened with the new foreground behavior. The review note was opened once in Zed Preview. No browser needed. The current frame renderer still has historical A as its default; use explicit C/motion paths. Future automatic excerpt timing is not integrated yet.

Next: Drew reviews movement (keep, gentler, more lively, or free feedback). Revise if needed; only after movement approval, plan/build the full video around the approved narration. Full sequence, final captions and scheduled production remain unfinished. No new installs or paid service calls for this test. Cron/publishing remain inactive. Whiteboard, BOARD.md and diagrams remain frozen.

[Production flow](01-content/animation/README.md) · [Progress](01-content/animation/episodes/D6-6c917b49743b/motion-paper/progress.md) · [Completed crawler research](01-content/research/2026-10-19-illustrated-animation/README.md).

## Earlier checkpoints

The sections below preserve earlier session history. The current position above governs continuation.

**Latest task: Tyler’s full original narration is approved; the MacBook crawler access check passed.** Drew said “I love it.” Approved audio: `01-content/audio/D6-6c917b49743b/full-original-tyler-01/original-tyler.mp3` (78.6 seconds). Rotation: Tyler, Chris, Liam; next new narration uses Chris. Assignments persist per approved narration ID, so revisions keep the same voice. Original script wording remains preferred and unchanged.

**Animation direction:** use GPT-6 Astra with ultra effort for animation creation. Drew wants illustrated picture-book-style scenes of bugs, houses and environments, driven by code and the approved narration. The pasted repository suggestions are unverified candidates. The future task is crawler research, any needed planning questions relayed to Drew, then a concrete installation plan for one first trial. No animation model call, installation or render has run.

**Current boundary: check access only; do not start research yet.** SSH to `drewp@100.80.131.62` succeeded. An authenticated GET to `/research/agent/capabilities`, tunneled to MacBook localhost:8766 with the existing `imac-research` client, returned HTTP 200 and `authentication: per_client_bearer`. Existing credentials were used in memory and not copied into files or chat. The temporary tunnel was closed. No legacy port 8600 request. Search reports configured/available but `unprobed_best_effort`; no search was run. This API reports no browser, cookies, model calls or paid fallback. Evidence and limits are in the [progress note](01-content/research/session-continuation-2026-10-19.md#crawler-access-check-and-audio-approval).

**Do not update the whiteboard, BOARD.md or diagrams yet.** `board_updates_enabled` stays false; `writing_enabled` stays true. Source 1, hook 4, original narration 2 and Tyler’s full audio are approved. Keep the source credit outside spoken text. Other source choices remain queued. Never read or copy crawler cookies into this project.

## Start here

- [System design and open decisions](01-content/video-system-design.md)
- [Short workflow](01-content/video-workflow.md)
- [Writing prompts](01-content/writing-harness-prompts.md) — proposed, not validated.
- [Recovered session, test evidence and current progress](01-content/research/session-continuation-2026-10-19.md).
- [Hook library](01-content/hook-library/README.md), [educational hook research](01-content/research/educational-hook-repos-2026-10-19.md), [harness options](01-content/research/writing-harness-options-2026-10-19.md), and [proposed resource criteria](01-content/research/resource-criteria-2026-10-19.md).
- [Pest resources](01-content/pest-resource-library.md), [source-use log](01-content/source-log.md), and [hook research repositories](01-content/research/hook-research-repos-2026-10-19.md).

## Excalidraw

- [System overview](http://localhost:3003/boards/52831f1163e1277b819320fd) — six phases now run **top to bottom**, as requested.
- [Detailed flow](http://localhost:3003/boards/f8724119f563ab46a50243e7).
- Editable drawings and construction notes: [diagrams](01-content/diagrams/README.md). The final `.excalidraw` files contain edits beyond their initial specifications; preserve those edits. Reuse the shared viewer.

## Required writing flow

Drew clarified that asking about narration never skips hook selection. Source 1, hook 4, original narration 2 and its Tyler audio are approved. Three other ant sources remain queued; the next pest-source research remains cockroaches.

1. Research five pest sources and show five short summaries with links, normally one or two sentences each and never more than four. Drew chooses a source or skips for fresh research.
2. Show five hooks for that ONE selected source. Drew chooses one or skips for fresh hooks on the same source. A second selected hook may queue with that same source.
3. Generate five full narrations using the exact selected hook and its source. Drew chooses one or skips for another five.
4. Save each approved narration and end the writing run. No automatic production. Source-review decisions guide research; hook decisions guide writing. Do not infer reasons for a skip or count unchosen options as disliked.
5. Refresh hook examples Saturday nights once scheduling exists. Later, choose a saved script for scene planning, voiceover, animation and export. One production video at a time.

All videos and previews must be **9:16**, with 1080×1920 export and Deep Six colors. The audience is homeowners seeking useful help with pest problems, initially ants/fire ants. The main lesson uses code animation; the reusable outro may use generated images/video.

## Decided since the handoff

**Latest Q1 correction (D17):** choose one of five sources first, then five hooks for that source. This supersedes D10 and the hooks-first D13. The diagrams still show the older flow; use the written workflow and D17 until the drawings are revised.

The interrupted session also decided research at run start, human-step pings and Telegram later (D11–D12). Its unanswered final message corrected the first screen, set weekly Saturday-night hook research, and requested a bank of approved narrations before videos (D13–D15).

Small follow-up, not yet asked: may a source behind an unchosen or skipped hook return in a later batch? Until Drew decides, ask first under the project source rule.

## Next open choices

Exact Saturday-night time and research volume; video length and voice; later Telegram setup, voice/render tools, outro, budget and retries. Manual trials can use the board now. See Q2–Q6 in the design document.

## Constraints and status

- Do not keep rejected narration archives. Discarded scripts were deleted; keep source metadata, process notes, feedback, and current selected work. Old Git history was not rewritten.
- Log factual sources to avoid reusing them across episodes. ANT-S001 remains reserved for the rejected D6-ANT-001 experiment; it is not a fresh source.
- Writer remains Sonnet 5.5 through Drew's Claude Code subscription. The earlier test of `claude-sonnet-5-5` returned structured output successfully in 3,533 ms. Safe mode omitted the global caveman instruction in a separate comparison. The local harness is now built. Live Codex/Astra research and hook writing passed; narration quality still awaits a real selection.
- D16: GPT-6.1 Sol or GPT-6 Astra through Drew's OpenAI ChatGPT subscription via Codex backs up every Claude role, including Sonnet and any Opus work. Claude remains primary. Preserve stage state and human choices when switching. The shared fallback runner is implemented and tested offline. A live probe fell from unavailable Sol 6.1 to successful Astra. Codex/Astra is active now; Claude has no credits.
- Harness and source-criteria research completed. The hook-repo helper failed at the limit after saving its draft. Its main recommendation was rechecked in this continuation; no inspected repo establishes proven pest-education hook performance.
- No cron, production automation, paid API calls, tool installations or publishing automation was started. The local writing harness uses subscription calls.
- Existing diagrams predate source-first review (D17). Do not treat their hooks-first labels as current. Do not take screenshots or repeat fit checks.
- Earlier work through commit `79371a8` was pushed. Commit `b7bca59` and the Q1 update are local only; Drew said not to push yet.

## Evidence automation added

Source research prioritizes depth; an editorial check runs before hooks. Narration now plans whether to reuse evidence, research specific gaps, or pause on a conflict. New supporting facts require independent page/quote validation and stay outside the liked-source queue. Current live planner reused the already collected evidence; five edited narrations await review. All 48 offline tests passed. Supporting research and failure recovery were tested with fixtures; this live round needed no new supporting search. No whiteboard or crawler changes.

Audio display: **D6 Audio Review** is now the confirmed foreground Windows player. Both files have Play controls. Use `tools/open_d6_audio.py` to reopen; audio generation opens it automatically. Local chat links/folder requests were not usable. Do not regenerate audio just to show it.
