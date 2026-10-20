# Where the first five hooks came from

**Five source-backed drafts are waiting for Drew. Astra researched the pest facts and wrote the hooks through the ChatGPT subscription. This batch used general writing patterns; it did not use a library of studied video openings.**

## What actually ran

1. The local writing runner started with the configured topic: useful ant and fire-ant lessons for Central Texas homeowners. Drew did not need to pick a research topic first.
2. A research call to `gpt-6-astra` had live web search enabled. Its instructions requested up to ten candidate publications, opening the original pages, from Texas A&M, Oregon State's National Pesticide Information Center, or EPA. It requested distinct lessons, regional relevance, limitations and short supporting quotations. Previously used publications were excluded.
3. The runner fetched the returned pages separately. It checked allowed publisher addresses, duplicate publications and whether the short quotations appeared in the page text. Five source cards passed; no rejection was recorded. The saved record does not establish how many other pages the model considered.
4. A second Astra call received those five cards and the project's writing instructions. Web search was disabled for this writing call. The hook-example library, approved narration examples and stored feedback were empty.
5. The writer was instructed to produce exactly five spoken openings, one per source, and connect each to a supported answer. With no studied examples, it could use a visible problem, honest question, surprising supported fact or supported misconception correction. These were provisional writing choices, not proven performance formulas.
6. The runner checked that there were five distinct choices, each tied to a different supplied source and valid fact references. It placed their wording on the board and stopped for Drew's choice. No narration was generated or approved.

## The five drafts and their evidence

The writing-pattern labels below are my reading of the finished drafts. The run did not save a pattern label for each hook.

| # | Exact hook | Factual source and supporting idea | Writing pattern |
|---|---|---|---|
| 1 | That mound has no hole in the middle. Where would the ants get in? Fire ants can use tunnels underground. | [Texas A&M: identifying fire ants](https://fireant.tamu.edu/manage/how-can-i-tell-if-i-have-fire-ants/) describes a mound without a central entrance and underground travel tunnels. | Visible puzzle, then an explanation. |
| 2 | Carpenter ants in your wood? They aren't eating it. Here in Texas, they often move into spaces that are already there. | [Texas A&M: carpenter ants around homes](https://citybugs.tamu.edu/factsheets/household/ants-house/ent-2001/) distinguishes nesting from wood consumption and describes southern species using existing spaces. | Correct a misconception. |
| 3 | Found a winged insect inside? Before you call it a termite, look at its waist. | [Texas A&M: swarming insects indoors](https://citybugs.tamu.edu/factsheets/landscape/ants/ent-2012/) explains the body features that distinguish winged ants from termites. | Familiar worry, then a useful clue. |
| 4 | Those Texas leaf-cutting ants carrying off your leaves are stocking an underground fungus garden. The fungus is their food. | [Texas A&M: Texas leaf cutting ant](https://citybugs.tamu.edu/factsheets/landscape/ants/ent-1002/) explains how collected vegetation supports the fungus the ants eat. | Explain a surprising behavior. |
| 5 | An ant trail across your counter has a chemical signal you can't see. Soapy water can wipe that away. | [NPIC at Oregon State: ants](https://npic.orst.edu/pest/ant.html) recommends soapy water to remove the trail's pheromone signal. | Invisible cause, then a practical action. |

The source cards preserve limits for the eventual narrations: mound shape alone cannot confirm species; carpenter ants can still cause damage; one winged insect cannot diagnose an infestation; leaf damage alone cannot identify leaf-cutting ants; cleaning a trail does not prove the colony is gone. These limits come from the linked publications or the conservative scope recorded in the source cards.

## Where the hook-writing method came from

The wording is newly generated. The runner used our [writing instructions](../writing-harness-prompts.md), not a downloaded hook-writing application or copied creator script. Earlier [repository research](../research/educational-hook-repos-2026-10-19.md) informed the prompt design, but those repositories were not loaded as runtime tools or video evidence.

The planned [hook library](../hook-library/README.md) will supply specific examples from original creator videos or readable transcripts. Each example should record the opening, its structure, where the explanation answers it, available performance information and what could not be observed. A transcript can support wording analysis; it cannot establish visual pacing or audio delivery. Views alone do not prove a hook caused success.

For this batch: **zero studied video examples, zero measured hook-performance comparisons and zero approved narration examples were supplied.** The four general structures above came from our prompt. The hooks are drafts to judge, not evidence-backed predictions of what will perform best.

## Proof and limits

- Run: `D6-2d2a1eb6b091`; review: `review-5d6441acd2e3`; current state: `waiting_hooks`.
- October 19, 2026, Chicago time: run began **12:24:35 p.m.**; research call finished **12:25:35**; source checks recorded **12:25:36**; hook call finished **12:25:54**.
- Both recorded model calls succeeded with `gpt-6-astra` through Codex. No Claude model or paid API key was used for this batch.
- Five source cards and five hooks are retained in the local runtime state. The [source log](../source-log.md) records the publications. I reopened all five original pages during this explanation to check their support again; that was a later audit, not the original search.
- The original exact search queries and browsing sequence were **not retained**. This is an account of the saved inputs, outputs, instructions and checks, not a complete search transcript. The first run also lacks a saved full prompt snapshot for each call.
- Quote matching verifies that evidence text exists on the page. Fact references verify which source a hook cites. Neither automatically proves every paraphrase, measures audience appeal or substitutes for reviewing the actual wording.

Next: Drew chooses one of the five hooks, or skips the batch. A choice triggers five complete narrations using that exact opening and its source. The current batch stays unchanged while its process is explained.
