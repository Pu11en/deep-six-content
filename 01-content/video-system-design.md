# Deep Six video system — design log

**Current task: establish the whole flow from start through an approved MP3.** [Current diagram, stage instructions and implementation gaps](mp3-system/README.md) supersede historical stage placement below. Source 1, hook 4, original narration 2 and Tyler’s MP3 are approved. Video and the branded outro are separate later work. No cron is active.

[Earlier Excalidraw drawings](diagrams/README.md) retain historical layouts. Use the new start-to-approved-MP3 drawing for this scope. The decision log below preserves the earlier design history.

## Goal and people

Make useful, entertaining pest-control education for homeowners, published as vertical shorts on YouTube, Facebook, and TikTok. Drew chooses the source, hook and narration. One selected hook leads to one video. Proposed success check: each finished video teaches a source-supported homeowner lesson and passes Drew’s review; audience performance is not yet measured.

## What exists today

Article and video research, a source-use log, narration-method research, brand assets, and a content board. Earlier narration attempts were rejected. Drew requested deletion of all narration archives; the six narration files and five script copies on the board were removed. The previous pushed Git commit still contains its history; no history rewrite was requested.

The two vertical cartoon examples have unverified code provenance. The ant example has published JavaScript, but its original layout is widescreen. No final renderer or approved finished cartoon exists yet.

## Decisions from Drew

| ID | Decision |
|---|---|
| D01 | Scheduled research has two inputs: pest-control resources and researched social-media hooks. |
| D02 | The writing harness produces exactly five hook choices. Skip all five means another five; a human chooses. |
| D03 | A second chosen hook can be queued for a later run. Only one hook proceeds into the current video. |
| D04 | The next writing round produces exactly five complete narrations, each beginning with the same selected hook and using the same selected factual resource. |
| D05 | Drew sees the entire script for each numbered option, including the repeated hook. Skip all five produces another five; selecting one saves the approved narration (D15). |
| D06 | Writer: Sonnet 5.5, run through Drew's Claude Code subscription (Max plan, claude.ai login) rather than a paid API key. Test on October 19: `claude -p --model claude-sonnet-5-5 --json-schema ...` returned the requested structured answer. Claude Code also used Haiku 4.5 for a small background step. The local harness now exists; Codex is active while Claude is out of credits. |
| D07 | Main cartoon animation uses code, such as JavaScript or TypeScript. All produced videos and previews are 9:16 and use Deep Six colors. |
| D08 | The branded outro may use AI image/video generation and will probably be reused. This is separate from the code animation method for the lesson. |
| D09 | No rejected narration archives. Keep current choices and all approved scripts (D15); on skip or replacement, discard rejected script text. Keep prompts, source IDs, decision IDs, checks, and concise feedback without retaining rejected narration bodies. |
| D10 | Historical, superseded by D17: five hooks previously used five separate sources. |
| D11 | Pest-resource research runs when a flow run starts. Hook-example research has a separate weekly refresh (D14). Cron activation comes later. |
| D12 | At every human step, the system pings Drew and waits. Later, pings and choices will go through a Telegram agent. |
| D13 | Historical, superseded by D17: the first review previously contained only five hooks. |
| D14 | Refresh the educational hook-example library on Saturday nights. Exact time and collection volume remain open; no timer is enabled. A writing run uses the latest reviewed library. |
| D15 | Test the hook-to-narration flow several times and save each selected narration for future videos. Approval ends that writing run; it does not start production. Approved scripts may accumulate while only one writing batch and one video are active at a time. |
| D16 | Claude remains primary. Every Claude role, including Sonnet writing and any Opus/research/planning/animation role, can fall back to GPT-6.1 Sol or GPT-6 Astra through Drew's OpenAI ChatGPT subscription via Codex. This applies across the system, not only to narration. The shared fallback runner is built. Astra passed a live subscription test; Sol 6.1 was unavailable in this CLI/account. Codex/Astra is active while Claude is out of credits. |
| D17 | Show five educational sources first, with links and normally one or two sentences each, maximum four. Drew chooses one; all five hook options then use that source. Source skip means fresh research; hook skip means fresh openings for the same source. This supersedes D10/D13. |
| D18 | Learn from source and hook choices separately. Save the shown options, decision and optional reason; supply recent source preferences to research and hook preferences to writing. Comments guide the next batch most; do not invent reasons or assume unchosen options are disliked. |
| D19 | Another agent is improving the MacBook crawler. Defer crawler integration and changes until Drew says it is ready. Existing subscription search and direct source checks continue. |

## Model fallback

When Claude is unavailable or reaches its subscription limit, the controller can continue the affected stage through Codex using either OpenAI backup in D16. Keep the same stage instructions, facts, selected hook, saved state and human-review rules. A model change must not repeat completed work or approve a choice. Record which model produced each batch; stop and report if both subscription routes are unavailable. Paid API use still requires separate approval.

## Proposed phases

Now: research → choose from five source summaries → choose from five hooks for that source → choose from five full narrations → save the approved script → repeat when requested.

Later: choose a saved script → plan scenes and voice → animate and assemble → review and export.

The local research/writing/selection/save loop is implemented; production remains a working design. Research can refresh independently. A cron tick must not replace a batch Drew is reviewing. Skip is an explicit user action, not an unattended retry loop.

## Step cards

### R1 — Pest-resource research

- Trigger: start of a flow run (D11). A cron job will start runs later.
- Input: pest/topic scope, [resource library](pest-resource-library.md), source-use log and recent source-review preferences.
- Action: find and read useful homeowner articles; produce evidence cards.
- Done by: the subscription research runner and independent page/PDF checks. Crawler integration is deferred under D19.
- Output: original URL, publisher/dates, species/region, homeowner problem, facts with locations, limits and use status.
- Stored: resource library and source metadata; no duplicate full article copies needed.
- Time / volume: Q2; no schedule active.
- Can fail by: inaccessible page, unsupported claim, duplicate source/lesson, outdated guidance, wrong region/species.
- On failure: flag and exclude that candidate; show a shortage if too few supported lessons remain.
- Human hand-off / visible: five source links and short lesson summaries, at most four sentences each (D17). Drew picks one or skips for fresh research. The choice is required before hooks are generated.

### R2 — Social-hook research

- Trigger: Saturday-night library refresh (D14). Until scheduling exists, refresh manually. If the library is empty for a trial, seed it during preparation rather than waiting for Saturday.
- Input: educational short-video niches, supplied creators/links, previously studied videos.
- Action: find real examples; inspect opening audio, on-screen text and action; describe the opening pattern.
- Done by: research harness. [Repository investigation](research/hook-research-repos-2026-10-19.md) identifies candidates; nothing installed.
- Output: video URL, creator, date, platform, opening timestamp and short transcript excerpt, visual observation, pattern, observed metrics/date, evidence limits.
- Stored: reviewed hook-study cards and links in the [hook library](hook-library/README.md). Keep useful examples across refreshes; do not replace the library merely because a week passed.
- Time / volume: Saturday nights; exact time and collection volume remain Q2. Start with relevant education and homeowner-help examples; broaden niches for storytelling patterns.
- Can fail by: blocked media, missing opening speech, unavailable metrics, unsuitable topic, unsupported performance explanation.
- On failure: mark what could not be observed; do not call a transcript-only study a watched video. Use another candidate if the opening is unavailable.
- Human hand-off / visible: none in the normal choice screen. Links, observed performance and pattern analysis stay internal. Views alone do not establish that an opening caused good performance.

### W1 — Five hook choices

- Trigger: Drew selects one source, or skips the current hook choices.
- Input: the selected source's verified facts, relevant hook studies, brand/audience brief and recent hook preferences.
- Action: write five distinct, truthful opening choices for the same source; check each promise against its lesson.
- Done by: the local writing harness, currently using Codex/Astra under D16.
- Output: exactly five numbered hooks, each bound to its lesson/source and pattern references.
- Stored: current batch, IDs, source assignments, selection and concise feedback. No new narration written yet.
- Time / volume: five per explicit batch; one pending batch per review stage proposed.
- Can fail by: unsupported promise, duplicate angle, switching away from the selected source, wrong count, missing source, inadequate research, model failure.
- On failure: repair a malformed batch before display; persistent failure becomes a visible error, not automatic selection. Retry limit remains Q6.
- Human hand-off / visible: Drew sees five numbered spoken hooks after source selection. Choose one, optionally save a second with the same source, or skip for new hooks using that source. No choice means wait.

### W2 — Five full narrations

- Trigger: Drew selects one hook, or skips the current narration batch.
- Input: exact chosen hook, its original factual resource and fact card, pattern notes, audience/voice instructions, feedback. Target length is Q3.
- Action: write five meaningfully different explanations with the exact same opening and source; check every factual claim.
- Done by: the same local harness and shared provider runner (D16).
- Output: five numbered full scripts, each printing the entire selected hook first. All five fulfill the same promised lesson.
- Stored: current review batch plus all approved scripts. Save each selection with its exact hook, source IDs, factual limits, prompt version and approval date in an approved-narration bank (D15). Delete rejected script text when replaced or selected; keep concise feedback. Approved work from earlier runs is not a rejected archive.
- Time / volume: exactly five per requested batch; wait indefinitely for the human selection rather than infer consent.
- Can fail by: altered hook, new unsupported facts, five near-identical paraphrases, unnatural wording, advice without context, wrong count.
- On failure: repair before display; Skip creates a new batch with the same hook/resource. A factual problem with the selected hook is raised explicitly, not silently changed.
- Human hand-off / visible: Drew gets a ping (D12), then reads five complete scripts. Choose one or Skip all five. Save the selected script and end the writing run. The current board is a manual display; Telegram comes later.

### P1 — Scene plan and timed voiceover (proposed)

- Trigger: Drew requests production of one saved, approved narration. Narration approval alone does not start production.
- Input: chosen script, factual card, brand palette, cartoon reference, 9:16 requirement.
- Action: map each spoken beat to visible character action; record which facts the picture must demonstrate. Generate/read the voiceover, then lock scene timings to the actual audio.
- Done by: scene-planning harness and voice tool; Q5.
- Output: scene plan, reusable character/asset requirements, voice audio and measured timings.
- Stored: current selected script, scene plan, approved assets and audio settings.
- Time / volume: one episode; duration/voice/tool still Q3/Q5.
- Can fail by: a scene contradicting the facts, weak visual explanation, awkward delivery, timing mismatch.
- On failure: revise the affected plan/audio; script changes return to Drew’s narration choice rather than silently replacing it.
- Human hand-off / visible: proposed compact storyboard/voice preview before full rendering.

### P2 — Code animation (proposed)

- Trigger: ready scene plan and voice timings.
- Input: approved script, timed scenes, brand/character assets.
- Action: draw and animate character actions in JavaScript/TypeScript or equivalent; render a vertical preview.
- Done by: animation harness; renderer and model Q5.
- Output / stored: code, assets, 9:16 preview and render settings for the current episode.
- Time / volume: one current episode; measured after the first test.
- Can fail by: render error, unreadable text, factual visual error, poor character movement, wrong dimensions or sync.
- On failure: repair that scene/render; show the error after a bounded retry count (Q6).
- Human hand-off / visible: proposed preview check; no paid generation authorized by this design.

### P3 — Assembly, reusable outro, final review (proposed)

- Trigger: acceptable animation and a chosen outro asset.
- Input: lesson animation, voice audio, captions/sound, approved Deep Six outro.
- Action: assemble and check the full vertical short; attach the same approved outro when appropriate.
- Done by: editing/render harness; Drew reviews the result. Outro art/video harness is a separate one-time setup or deliberate replacement.
- Output / stored: 1080 × 1920 final file, selected source IDs, captions, outro version and review status.
- Time / volume: one video per selected hook. Outro length and wording remain Q5.
- Can fail by: caption/sound errors, brand mismatch, wrong outro version, unsupported claim, export failure.
- On failure: return to the affected production step and recheck the output.
- Human hand-off / visible: final video ready for Drew. Publishing remains a separate action requiring authorization.

## Source and queue rules

Pest facts come from the selected resource. Social research supplies opening techniques and pacing; it cannot establish pest-control facts. Every hook carries a source/lesson link, which remains attached through narration and production.

Log sources when their shortlist is presented, against its run/lesson, to avoid repetitive shortlists. Older records were logged at hook drafting. Keep shown sources, chosen sources, queued hooks and published lessons distinguishable. A skipped source or draft is not a published episode. ANT-S001 remains reserved for the rejected experiment. Under D17, five hooks share the selected source; a saved second hook retains that source too.

Queue changes, selections and skips need stable IDs so a repeated click or cron run cannot generate duplicate work. One writing batch and one production episode proceed at a time. The approved-narration bank can hold several scripts. A saved second hook waits until explicitly chosen for the next run.

## Open questions

- **Q1 — revised (D17):** five different sources first, then five hooks for one selected source. Previously shown sources remain reserved to avoid repeats; hook retries and explicitly queued hooks keep their source.
- Q2 — partly answered (D11, D14): pest research at flow start; social-hook research Saturday nights. Still open: exact Saturday time, collection volume, topic breadth and pending backlog cap. Cron later.
- Q3 — later: target video length and narration tone/example.
- Q4 — partly answered (D12, D17): source summaries first, then hooks, then full scripts. Show choices directly in chat and on the board, and wait at each choice. Telegram later.
- Q5 — later: voice, renderer and production model; outro text/length and existing approved assets.
- Q6 — later: budget, automatic retry cap, and where failures are shown. No paid calls or cron activation now.

## Problems to show in the eventual diagram

1. Source selection must happen before hooks. Hook retries and queued hooks keep the selected source; source skips request a fresh shortlist.
2. Scheduled runs can overwrite pending review or pile up work; preserve the current batch and cap the queue.
3. An attention-grabbing hook can promise a fact the article cannot support; check before showing choices.
4. Five narration options can become superficial rewrites; require meaningful differences while preserving hook and facts.
5. Reusing a pretty cartoon does not prove a code-only production route; inspect actual source code or record that provenance is unverified.

## Change log

- 2026-10-19: transcribed the whiteboard decisions; added proposed production steps; asked Q1. Read the named System Blueprint skill and interview guide. Research-only comparison of hook repos completed. Deleted narration files and board copies; no new archive created. Diagram remains in the interview stage while Q1 and production choices are open.
- 2026-10-19: Drew requested Excalidraw now. Created and opened a main flow plus a service overview, with open choices labeled rather than assumed. Added the source-to-narration arrow, both skip loops, second-hook queue, production continuation, and reusable outro. Content audit and JSON/binding checks completed; no screenshot or viewer fit checks.

- 2026-10-19: Drew requested a top-to-bottom system overview. Reflowed the same drawing into six stage rows, with roles in columns and chronological arrows pointing down; no process decisions changed.

- 2026-10-19: Drew answered Q1: five hooks cover five different lessons, each from its own source (D10). Updated the step cards, writing prompts, and both diagram notes. Drew chose not to push yet.

- 2026-10-19: Drew set research to run at flow start (cron later) and asked for a ping at each human step, with Telegram later (D11, D12). Writer runs on Drew's Claude Code subscription (D06). Research started on harness options, hook repos and source criteria.

- 2026-10-19 continuation: recovered the unanswered 12:06 p.m. Chicago message from session `1271d6d6-bf63-4e4a-a9fc-55aa4dcc42eb`. Added hooks-only first screen, Saturday-night hook-library refresh and saved approved narrations before production (D13–D15). The hook-repo helper failed at the subscription limit after saving its research draft; recommendations remain untested. [Continuation evidence](research/session-continuation-2026-10-19.md).

- 2026-10-19: Drew designated GPT-6.1 Sol or GPT-6 Astra through the OpenAI ChatGPT subscription as backup for every Claude role (D16). This records routing intent; no model calls or automated fallback were started.

- 2026-10-19 build: implemented the local writing harness and shared subscription fallback. Live Astra research and hook writing passed with five source cards; review `review-5d6441acd2e3` awaits Drew. Timers, Telegram and production remain off.
