# Source choices and learning from feedback

**Choose the educational source before its hook. Keep source taste, hook taste and narration feedback separate. Crawler integration waits until Drew says the other agent's update is ready.**

## Current flow

1. Research five distinct sources. Display each with its original link and a short description of what it teaches: normally one or two sentences, never more than four.
2. Drew picks one or skips the shortlist. Retain the five summaries, decision and any stated reason.
3. Write five different hooks for the chosen source. Skipping these hooks keeps that source.
4. Choose a hook, review five full narrations and save the approved script. Production still waits for a separate request.

Research receives the latest twelve source decisions and source-specific comments. Writing receives hook decisions and writing feedback. All decisions remain saved locally between sessions and model changes. A pick is a provisional positive signal. Unchosen items are not automatically disliked; a skip without explanation does not establish why. Explicit comments and later corrections guide the next round most closely. Evidence checks remain independent of taste.

## Repositories checked

| Reference | What it offers | Decision for Deep Six |
|---|---|---|
| [LangMem](https://github.com/langchain-ai/langmem) and its [prompt optimization API](https://langchain-ai.github.io/langmem/reference/prompt_optimization/) | Persistent memory primitives and prompt refinement using conversation history with optional feedback. The documented setup uses model-provider APIs. | A useful reference for separating saved preferences from prompt improvements. Our current need is met by local decision records supplied to the subscription runner. No installation or automated prompt optimizer added. |
| [GPT Researcher](https://github.com/assafelovic/gpt-researcher) | Research planning, collection, source tracking and report generation. Its README also offers a Claude skill; the documented quickstart uses model/search API keys. | Useful research-workflow reference, but a larger report-writing system than this shortlist needs. The inspected documentation does not establish a ready-made system for learning Drew's article taste. No package or skill installed. |

My recommendation is to collect real source choices first and keep this small. Later, compare whether Drew needs fewer source skips and whether the stated feedback is followed. A memory system does not itself prove better recommendations; current tests verify delivery of preferences, not audience results or subjective quality. No claim is made that these two repositories exhaust all options.

## Crawler findings — integration deferred

Read the local [crawler README](../../../deep-six-factory/ultimate-crawler/README.md), [goal](../../../deep-six-factory/ultimate-crawler/GOAL.md), [handoff](../../../deep-six-factory/ultimate-crawler/docs/HANDOFF.md) and [caller guide](../../../deep-six-factory/ultimate-crawler/docs/FOR-VERTICAL-BUILDERS.md). The saved notes distinguish the working fetch/feed service from its unfinished research planner.

Read-only requests to `GET /health` and `GET /openapi.json` reached the MacBook on October 19 and reported version `beb4bc0`. The exposed routes include `/fetch` and `/search`; no research-job route was listed. The local implementation describes `/search` as paid Jina search and `/fetch` as a tiered retrieval service with a tier cap. These observations describe that version, not the other agent's unfinished update.

Drew then asked this session to leave crawler improvements to the other agent and wait for notification. No crawler code, configuration, deployment or jobs were changed or started. The content runner continues using its existing subscription search and direct source verification. Recheck the interface when Drew says the crawler is ready; do not assume the current routes remain its final contract.

Articles and PDFs work in the current source validator. YouTube can be a future educational source when readable transcript evidence and creator credibility can be checked. Video/transcript ingestion is not implemented here, and a title or description alone is not enough evidence for its lesson.

## Checks

The source-first flow passes 32 offline tests. They cover the source review stop, one-source hook generation, separate source/hook feedback after restart, skip behavior, source preservation on failure, stale choices, maximum summary length and migration of the existing pending batch without inventing a rejection. Live writing quality still requires Drew's selections.
