# Research run record

**The approved crawler research is finished; the first render remains a future task.** Findings are recommendations with evidence and explicit gaps.

## Approval and scope

Drew asked for project reading, a small public-source scout, one multiple-choice question at a time, then a plan for approval. The project, approved script/audio and earlier animation findings were read. Preliminary scouting inspected official/public repository pages. Drew selected **A: illustrated science book**, then answered **yes** to the four-step research plan.

That approval authorized research and research files, with no installations, application changes or spending. The crawler planning snapshot records the agreed goal, constraints and this approval. [Approved plan](approved-plan.json).

## Crawler and login

- Machine: **MacBook / Ultimate Crawler**, reached through SSH as `drewp@100.80.131.62`.
- API: a temporary local loopback SSH tunnel to **MacBook localhost:8766**. Legacy port 8600 was not used.
- Client ID used: **`imac-research`**.
- Login source: the already provisioned entry in **`/Users/drewp/ultimate-crawler-agent/config/clients.json` on the MacBook**. It was read over SSH into process memory. No new client was created, and no token was printed or written into these artifacts.
- Authenticated `/research/agent/capabilities` succeeded before the run and during each resumed batch. [Capabilities](capabilities.json).
- This API is **caller-driven**. The crawler fetched sources, stored evidence and enforced revision/budget checks. Codex chose searches, read context, assessed quote support and wrote the recommendation. The crawler did not run an independent research model.
- The free public search backend was `parallel_public`. Browser access, cookies and paid fallback were disabled. No source-site login was used.

The planning session was created, approved to reflect Drew’s yes, explicitly started, and opened as an agent-driven research job. Every action was submitted with its expected revision and an idempotency key. Each batch closed its temporary SSH tunnel.

## Exact run evidence

Job ID: **`9ea3ef8e-6014-4411-88f5-7dc963a27358`**.

| Measure | Result |
|---|---:|
| Crawler searches | 3 |
| Page attempts | 30 |
| Saved page snapshots | 29 |
| Quoted evidence records | 20 |
| Separate caller support assessments | 20 |
| Total crawler actions | 79 |
| Crawler model calls | 0 |
| Active crawler execution time | 52.83 seconds |

Active time excludes reading, deciding and writing between calls; it is not total task time. Operator-selected ceilings were 4 searches, 30 pages, 80 actions and 900 active seconds. The API schema requires a model-call ceiling of at least 1, but this mode made **0** calls.

The job state is `finished`, reason `caller_finalized`; the crawler result outcome is **`partial`**. All four research questions have coverage notes. This means a bounded, best-effort answer with documented limits, not exhaustive proof or a successfully tested video system. [Final result](result.json) · [Job state](job.json) · [Queries, source index and errors](sources.md).

## Checks and limits

All 29 saved source texts matched the crawler’s recorded SHA-256. All 20 quoted spans exist exactly in their respective snapshots; each was followed by a separate support assessment. These assessments are the caller’s judgments, not independent fact-checking or a second model review.

Two successful fetches landed on generic homepages and were excluded from substantive evidence. One guessed Texas A&M URL returned 404; the correct biology page was subsequently read. Four snapshots were truncated: HyperFrames README, the ant demo source, the ant repository commit response, and Motion Canvas flow documentation. Claims use only the retrieved portions.

The crawler discovered a Texas A&M fire-ant model PDF through search, but did not read the PDF. Its two-node anatomy excerpt remains a research lead, not a checked source passage. Anidoodle’s stated example duration differs between its README and source header; the actual imported duration was not executed.

Read-only local checks identified existing Node, npm, FFmpeg and FFprobe, missing project-resolvable drawing/rendering packages, and Astra ultra in the existing model cache. One **already saved creator contact sheet** was viewed for visual context. No new screenshots, render, full-video playback, benchmark or installation was performed.

All new files from this task are contained in this research folder. Existing tracked files and the approved MP3 are checked in [verification.json](verification.json). The request did not authorize implementation, and none ran.

## Files for continuation

- [Short recommendation](README.md)
- [Detailed findings and open questions](findings.md)
- [Future trial setup](first-trial-plan.md)
- [Sources and excluded reads](sources.md)
- `sources/*.json`: fetched public text, URL, timestamp, truncation marker and hash.
- `actions/*`: action requests and receipts, without authentication headers.
- `crawler_client.py`: research helper used for this run; credential values are never embedded.

No app workflow, voice rotation, source queue, whiteboard or diagram was updated.
