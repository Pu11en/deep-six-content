# Research holes to close

**The main missing piece is a research loop that changes strategy, retains useful leads and knows when evidence is sufficient.**

This review covers starting an episode through delivering checked evidence to the narration writer. It does not choose an interface, harness, research timer or narration method. The rules below are design refinements, not claims of completed automation.

## Main gaps

| Situation | Rule to add or make explicit | Current implementation |
| --- | --- | --- |
| Drew rejects all five | Rejection alone is enough. Claude changes the query, teaching angle or source route using search history, quality and variety. Never require an explanation or invent a rejection reason. | Source feedback reaches the next research request. There is no systematic cross-run record of strategies, results and why each search failed. |
| The familiar source pool runs thin | Search different species names, homeowner questions, credible authors and publishers; follow references to original studies. Revisit promising publication feeds when stock is needed. | Initial discovery uses a narrow domain allowance. Supporting science has a wider one. Source eligibility remains unchanged in code. |
| An article was shown but never chosen | Keep it distinct from rejected and used. Avoid repeated fresh shortlists, while retaining a browsable candidate history. Explicitly liked sources stay in their pest queue. | All shown cards enter the historic `used_sources` exclusion list. The queue is separate, but the history mixes several meanings. |
| A fresh article repeats an old lesson | Compare the teaching claim as well as the publication. Detect mirrors, editions and shared study origins. | URL, publisher/title, exact page text and exact lesson text checks exist. Paraphrased lessons and altered mirrors need editorial judgment. |
| Three good candidates are found, then search stalls | Preserve the three. Try a different bounded route if promising. Otherwise report the shortage and offer the valid choices or pause. | The importer requires exactly five. It records counts on failure, but does not persist the validated partial shortlist as reusable accepted cards. |
| Research keeps returning nothing | Distinguish an unavailable search service, unreadable content, duplicate-heavy results and genuinely thin evidence. Retry only with a reason to expect progress. | Requests are bounded to four searches, twenty reads and 300 active seconds. Limits alone do not choose a better strategy. |
| Several pages agree because they copied one source | Trace the original evidence. Treat copied accounts as one origin, not independent confirmation. | Literal quote checks cannot establish independence or whether an interpretation follows from a passage. |
| The main source cannot support the chosen hook | Catch shallow sources before hooks. If deeper research contradicts a selected hook, return to source/hook review with the reason. A changed hook needs approval. | Depth checks and contradiction stops exist; the diagram previously showed the pause without explaining recovery. |
| A saved source changed, disappeared or is outdated | Hold it for recheck, retain the rest of the queue and explain the next eligible option. Recheck relevant supporting evidence after long pauses too. | Main sources older than 24 hours are re-fetched. Any page-text change stops progress, even if the change is unrelated to the lesson. Supporting freshness remains agent-operated. |
| Drew changes source or hook while work is pending | Invalidate dependent evidence and review IDs. Retain unrelated queues and audit records. Reject results for the older request. | Revision commands and request/run/stage/client checks exist. Interrupted crawler actions still need receipt reconciliation. |
| An episode is abandoned | Keep its publication reservation explicit until the episode is deliberately resumed or cancelled. Cancellation must not silently make a used source reusable. | Reservations exist, but a clear whole-episode cancellation/release policy remains to be specified before automation. |
| “Evidence ready” is vague | Require a supported hook, answers to essential explanatory questions, claim-to-source links, species/region limits and no unresolved essential contradiction. | Evidence planning, quote checks and unresolved-question stops exist. Meaning, causal reasoning and sufficiency still need editorial review. |

## Adaptive search procedure

1. Read the current pest's approved queue, publication/lesson history and relevant feedback.
2. Record the rejection without asking Drew why. Assess observable weaknesses such as repetition, thin evidence, weak local fit or limited source diversity. These are the researcher's assessments, not Drew's stated reasons.
3. Choose a changed route using those assessments and search history. Try mechanisms, original studies, different homeowner questions or new credible publishers. If no weakness is clear, diversify the next batch instead of asking Drew to diagnose it.
4. Give Ultimate Crawler concrete searches and page-read requests. Claude chooses the strategy and assesses the material.
5. Keep each useful candidate and record what was tried. Do not discard a good partial batch when a search or read fails.
6. Continue while there is a promising route within the current research bounds. On repeated no-progress, state the concrete limit and offer the valid choices or pause. Do not require rejection feedback to continue.
7. Save liked sources by pest. After hook selection, run a separate targeted evidence pass. Avoid searching again for answers already adequately checked.

There is no guarantee of unlimited distinct, high-quality sources for every narrow topic. New discoveries can be older, previously unused publications. Broader access and better search improve coverage; they do not justify weaker evidence, invented novelty, repeated used articles or infinite retries.

## Evidence and limits

Reviewed `tools/d6_harness.py` research, source import, freshness, depth, evidence planning and revision behavior; `tools/d6_sources.py` duplicate/quote validation; the existing lifecycle review; and the current canvas. [Prior eight focused checks](2026-10-19-research-audit.json) cover existing behavior, not the proposed adaptive loop.

The canvas now ends at **ready for narration writing**. Drafting happens next; reviewing five narrations happens after drafting. [Current design](2026-10-20-research-design.md) · [Drawing checks](../diagrams/animation-system.checks.json).

Progress: removed interface assumptions from this research section, added six visible research safeguards and explicit retry routes, and preserved the existing larger flows. No live crawler job, source import, model call or runtime change was made.
