# Deep Six video system — design log

**Design in progress.** This records Drew’s October 19 whiteboard and the proposed missing production steps. No cron, model calls, voiceover, animation, or publishing automation has been set up.

## Goal and people

Make useful, entertaining pest-control education for homeowners, published as vertical shorts on YouTube, Facebook, and TikTok. Drew chooses the hook and narration. One selected hook leads to one video. Proposed success check: each finished video teaches a source-supported homeowner lesson and passes Drew’s review; audience performance is not yet measured.

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
| D05 | Drew sees the entire script for each numbered option, including the repeated hook. Skip all five produces another five; selecting one advances the video. |
| D06 | Requested writer: Sonnet, described by Drew as Sonnet 5.5. Exact available provider model ID remains unverified and unconfigured. |
| D07 | Main cartoon animation uses code, such as JavaScript or TypeScript. All produced videos and previews are 9:16 and use Deep Six colors. |
| D08 | The branded outro may use AI image/video generation and will probably be reused. This is separate from the code animation method for the lesson. |
| D09 | No narration archives. Keep the current choices and chosen script; on skip or replacement, discard rejected script text. Keep prompts, source IDs, decision IDs, checks, and concise feedback without retaining rejected narration bodies. |

## Proposed phases

Research → choose hook → choose narration → plan scenes and voice → animate and assemble → review and export.

These are a working design, not an implemented automation. Research can refresh independently. A cron tick must not replace a batch Drew is reviewing. Skip is an explicit user action, not an unattended retry loop.

## Step cards

### R1 — Pest-resource research

- Trigger: scheduled run; cadence open (Q2).
- Input: pest/topic scope, [resource library](pest-resource-library.md), source-use log.
- Action: find and read useful homeowner articles; produce evidence cards.
- Done by: research harness; retrieval tools unchosen.
- Output: original URL, publisher/dates, species/region, homeowner problem, facts with locations, limits and use status.
- Stored: resource library and source metadata; no duplicate full article copies needed.
- Time / volume: Q2; no schedule active.
- Can fail by: inaccessible page, unsupported claim, duplicate source/lesson, outdated guidance, wrong region/species.
- On failure: flag and exclude that candidate; show a shortage if too few supported lessons remain.
- Human hand-off / visible: Drew sees a source link and plain lesson description with a hook choice.

### R2 — Social-hook research

- Trigger: scheduled run, independent of R1; cadence open (Q2).
- Input: educational short-video niches, supplied creators/links, previously studied videos.
- Action: find real examples; inspect opening audio, on-screen text and action; describe the opening pattern.
- Done by: research harness. [Repository investigation](research/hook-research-repos-2026-10-19.md) identifies candidates; nothing installed.
- Output: video URL, creator, date, platform, opening timestamp and short transcript excerpt, visual observation, pattern, observed metrics/date, evidence limits.
- Stored: hook-study cards and links. Full downloaded video/transcript retention is not required for the writing prompt.
- Time / volume: Q2. Start with relevant education and homeowner-help examples; broaden niches for storytelling patterns.
- Can fail by: blocked media, missing opening speech, unavailable metrics, unsuitable topic, unsupported performance explanation.
- On failure: mark what could not be observed; do not call a transcript-only study a watched video. Use another candidate if the opening is unavailable.
- Human hand-off / visible: optional original video link behind each generated hook; pattern analysis stays separate from pest facts.

### W1 — Five hook choices

- Trigger: both research inputs ready and no current hook batch awaiting review; or Drew presses Skip.
- Input: verified lesson cards, relevant hook-study patterns, brand/audience brief, previous rejection reasons. Source grouping is Q1.
- Action: write five distinct, truthful opening choices; check each promise against its assigned lesson.
- Done by: writing harness using Drew’s requested Sonnet model, once configured.
- Output: exactly five numbered hooks, each bound to its lesson/source and pattern references.
- Stored: current batch, IDs, source assignments, selection and concise feedback. No new narration written yet.
- Time / volume: five per explicit batch; one pending batch per review stage proposed.
- Can fail by: unsupported promise, duplicate angle, wrong count, missing source, inadequate research, model failure.
- On failure: repair a malformed batch before display; persistent failure becomes a visible error, not automatic selection. Retry limit remains Q6.
- Human hand-off / visible: choose one, optionally save a second for later, or Skip all five. No choice means wait.

### W2 — Five full narrations

- Trigger: Drew selects one hook, or skips the current narration batch.
- Input: exact chosen hook, its original factual resource and fact card, pattern notes, audience/voice instructions, feedback. Target length is Q3.
- Action: write five meaningfully different explanations with the exact same opening and source; check every factual claim.
- Done by: the same writing harness and requested Sonnet model.
- Output: five numbered full scripts, each printing the entire selected hook first. All five fulfill the same promised lesson.
- Stored: current review batch only; retain the selected script, delete rejected script text when the batch is replaced or a choice is made. Keep source/decision metadata and feedback.
- Time / volume: exactly five per requested batch; wait indefinitely for the human selection rather than infer consent.
- Can fail by: altered hook, new unsupported facts, five near-identical paraphrases, unnatural wording, advice without context, wrong count.
- On failure: repair before display; Skip creates a new batch with the same hook/resource. A factual problem with the selected hook is raised explicitly, not silently changed.
- Human hand-off / visible: read five complete scripts; choose one or Skip all five. Review interface is Q4; the current board is only a manual display.

### P1 — Scene plan and timed voiceover (proposed)

- Trigger: selected narration.
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

Log use as soon as a factual draft uses a source, against its episode/lesson. Keep sources, queued lessons and published lessons distinguishable. A skipped draft does not become a published episode. ANT-S001 remains logged for the rejected experiment. Q1 must settle whether a second saved hook shares its source with the first and how that fits the earlier no-repeat rule.

Queue changes, selections and skips need stable IDs so a repeated click or cron run cannot generate duplicate work. One active episode proceeds at a time. A saved second hook waits until explicitly chosen for the next run.

## Open questions

- **Q1 — asked:** Five hook options from five different lessons/sources, or five openings for one article? This affects the second-hook queue and unique-source rule.
- Q2 — later: research cadence, topic breadth, target output volume and maximum pending backlog.
- Q3 — later: target video length and narration tone/example.
- Q4 — later: where Drew reviews and clicks Choose / Save for later / Skip; no interface built yet.
- Q5 — later: voice, renderer and production model; exact Sonnet provider ID; outro text/length and existing approved assets.
- Q6 — later: budget, automatic retry cap, and where failures are shown. No paid calls or cron activation now.

## Problems to show in the eventual diagram

1. Saved second hooks can repeat a source/lesson unless Q1 defines the rule.
2. Scheduled runs can overwrite pending review or pile up work; preserve the current batch and cap the queue.
3. An attention-grabbing hook can promise a fact the article cannot support; check before showing choices.
4. Five narration options can become superficial rewrites; require meaningful differences while preserving hook and facts.
5. Reusing a pretty cartoon does not prove a code-only production route; inspect actual source code or record that provenance is unverified.

## Change log

- 2026-10-19: transcribed the whiteboard decisions; added proposed production steps; asked Q1. Read the named System Blueprint skill and interview guide. Research-only comparison of hook repos completed. Deleted narration files and board copies; no new archive created. Diagram remains in the interview stage while Q1 and production choices are open.
