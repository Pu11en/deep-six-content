# What we ask the crawler to find

**Find a useful lesson a pest professional could explain to a homeowner. Use approved sources already in the queue before repeating discovery for an episode.** This defines the source-discovery part of the flow; it does not start research.

## Two different reasons to start

| Request | What happens |
|---|---|
| Continue unfinished work | Resume the saved source, hook, script or audio review. Do not restart discovery. |
| Make the next episode | Use the first approved queued source, unless Drew requests another. If no priority is clear, show the saved choices. Check that the material remains usable, then make hooks. |
| Find new source choices | Prepare a research request for the next pest needing sources, then use the crawler. This can fill tomorrow’s queue while an episode uses today’s saved source. |
| No usable approved sources remain | Research five new choices and wait for Drew’s selection. |
| Drew rejects all five new sources | Save the actual feedback and research fresh candidates for the same pest. |
| Every pest has at least three stocked sources | Stop routine stocking research until inventory is needed. An explicit request can set a different scope. |

**Current queue:** three ant sources are approved and waiting. First is *Tawny Crazy Ants: A Texas-Size Problem*, followed by household-ant identification and fire-ant biology. **Next source-discovery pest:** cockroaches. The next discovery pest and the next episode’s pest can differ.

**Research frequency:** no daily/weekly source schedule has been chosen or activated. Recommended finished automation: separate queue checks start discovery only when a pest needs approved sources; they never rerun source discovery merely because another episode starts. The question of continued stocking versus waiting until requested/empty is with Drew. Three stocked sources is the inventory target; it is not a clock schedule or permission to approve sources automatically.

## The actual request — next stocking round example

> Find five distinct educational sources about cockroaches for homeowners around New Braunfels and Central Texas.
>
> Each source must support one clear lesson a knowledgeable pest professional could explain to a homeowner. Prioritize useful, less-obvious biology, behavior or identification. Explain what happens, why it happens, and what that helps a homeowner understand or do. Avoid five versions of the same lesson.
>
> Prefer original university/extension research and clear expert education. Read the relevant original material. Identify the species, location, supporting facts and limitations. The main source must support a truthful hook on its own; deeper supporting science can be added after the hook is chosen.
>
> Use our existing source history and liked queue to exclude repeated publications. Keep the topics varied within cockroaches. Do not assume unchosen sources were disliked, or that earlier interest in ants means we should research ants again.
>
> Return five original links, each with a one- or two-sentence preview explaining what the episode would teach. Keep the evidence, dates, source locations, useful facts and uncertainties attached internally. If fewer than five qualify, report the shortage. Do not invent a fifth or write the hooks yet.

Before sending, the agent attaches the **current** pest, region, queue counts, reserved URLs/publications, source-specific feedback, allowed retrieval methods, desired output and research bounds. The queue counts choose the next research pest; queued articles are not automatically sent as evidence for a different pest.

[Concrete planning-request example](source-request.example.json) contains the current fields and exclusions. It is a draft API payload, not a submitted or approved crawler job. Regenerate its changing queue/history fields before actual use.

## What makes a source worth showing

These are editorial criteria, not a guarantee of viewer interest or numerical proof of quality.

| Criterion | Pass looks like | Reject or investigate |
|---|---|---|
| **Useful to a homeowner** | Changes how someone understands a pest sign, identifies a problem, or makes a sensible prevention decision. | Trivia with no useful meaning, or material aimed only at technicians without a homeowner lesson. |
| **Teaches something beyond the obvious** | A specific behavior, mechanism, life stage, identification distinction or misconception worth explaining. | Generic “keep your home clean” advice with no explanation. Do not manufacture surprise or claim nobody knows it. |
| **Enough substance for narration** | The main source supports a clear lesson and an honest hook. There is enough explanation to develop, or specific deeper questions for later science research. | A catchy headline, thin listicle, or claim whose promised answer is absent. |
| **Credible and checkable** | Identifiable expertise, original evidence or a clear professional demonstration; the actual passage/segment supports the lesson. | Search snippets, AI summaries, votes or confidence presented as proof. Corroborate broader factual claims from creator content. |
| **Relevant here** | Species and conditions apply to Central Texas, with limitations preserved. | Treating an out-of-state measurement as a Texas result, or using an irrelevant species without explanation. A source need not be written in Texas to explain shared biology. |
| **Distinct from the other options** | A different publication and a meaningfully different lesson. | Mirrors, recycled articles, already reserved publications without permission, or five variations on the same point. |
| **Honest context** | Dates, uncertainty and what was actually accessed are recorded. | Outdated treatment claims, missing context, fabricated causal claims or pretending a video was watched. |

Prefer concrete, explainable subjects that will later be easy to illustrate, but do not plan video scenes during this source step. Scientific depth means explaining accurately; jargon and citation count do not make a weak lesson strong. No permanent word count or required number of facts is being imposed.

Keep the current content scope: identification, behavior and practical nonchemical prevention. Chemical recipes, dosing, medical advice and product-specific recommendations stay outside this source-writing trial. A teaching article containing treatment sections can still contribute a valid biology lesson if the used section and limits are clear.

## How the search actually happens

1. **The writing/research agent prepares the request.** It reads the queue/history and uses the criteria above. The crawler does not invent our editorial goals.
2. **The agent creates a crawler plan.** It sends the written goal, questions, exclusions and bounded output through the planning API. It records real task authorization before starting that plan.
3. **The agent gives the crawler specific searches.** Possible cockroach discovery queries include `site:citybugs.tamu.edu cockroaches biology behavior`, `site:extensionentomology.tamu.edu cockroaches identification`, and `site:npic.orst.edu cockroaches hiding moisture`. These are example queries, not claims that results have been found or read.
4. **The crawler returns search leads.** The agent chooses promising original pages and requests crawler reads. This authenticated crawler route is caller-driven; it does not autonomously run another research model.
5. **The crawler returns the original material and access details.** The agent checks the lesson against the criteria, records brief evidence and assesses limits. Existing independent page/quote checks remain part of admitting cards to the writing system.
6. **The agent builds the five choices.** Normally one or two sentences per choice; maximum four. Links and lesson previews are shown to Drew. He approves what goes in the queue.

The proposed starting bound remains four searches and twenty page reads. Those are ceilings, not targets or guaranteed coverage. Reuse already gathered eligible evidence within the same request; stop honestly if the bounds are insufficient.

## Which source types are eligible

University/extension publications are the current supported path. Educational pest-professional articles, demonstrations and videos remain desirable source categories; they are not excluded just because a pest company created them. They still need identifiable expertise and checked support for the claims we use.

Reddit or other social questions can reveal what homeowners misunderstand. A question or anecdote alone does not validate a biological claim. Social/video candidates require verified retrieval of the relevant content and supporting evidence before becoming selectable source cards.

The authenticated client currently reports public search/read access, no browser or cookies. The existing writing validator also restricts accepted domains. Therefore broad creator/social ingestion needs an adapter and verification; this document does not silently enable it. The older [criteria research note](../research/resource-criteria-2026-10-19.md) proposed a blanket ban on company/social sources; that proposal does not override Drew’s broader educational-source goal or these current distinctions.

## After a source is picked

The hook writer uses only that main source’s supported lesson. After a hook is selected, the agent sends a **different** crawler request: the exact hook, current facts and specific missing scientific explanations. That supporting research does not change source priority, fill the liked-source queue, or require finding five new main sources.

## Status

The configured runner now emits a bounded crawler request and waits for `import-research`. The session agent performs crawler actions and saves evidence; import independently checks pages and binds the result to its request. No new discovery ran in this review. Next trial: `start --fresh`, leaving the old queue intact. Main/supporting publications stay reserved to their episode until a finished MP4 marks them permanently used. Automatic scheduling remains off.
