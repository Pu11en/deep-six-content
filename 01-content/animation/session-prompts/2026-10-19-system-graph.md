# Task: design and diagram the whole MP3-to-MP4 video automation

Drew wants to craft the system and graph out the entire automation that turns an approved narration MP3 into a finished Deep Six MP4. This session designs and draws the system; it does not build it yet.

Read these first, in order:
1. `01-content/animation/HARNESS-NOTES.md`: what worked in the approved run, the problems caught, the model findings, the requirements and the open questions.
2. `01-content/animation/VIDEO-FLOW.md`: the current recipe and quality bar.
3. `01-content/animation/NEXT-SESSION.md`: the current state.
4. `01-content/animation/make_video.py` (skim): the current prototype runner, with prepare, full, segment, render and deliver.

Drew's decisions so far:
- Every video keeps the style of the approved fire-ant video: `01-content/animation/episodes/D6-6c917b49743b/full/renders/full-v2.mp4`.
- Default model: Opus 5.5 at max effort. When Claude credits run out, use GPT-6 Sol, then GPT-6 Astra. Drew rated Sol's test better; he called Astra's clips "super bad".
- Automatic checks are not enough. Watching the motion is the quality gate, and only Drew approves.
- Finished videos are copied to Drew's Windows Desktop; never open a player.
- The closer and transition into the outro, the outro itself (video generation with Deep Six branding assets) and music are later pieces. Show them as future boxes.
- Scope starts at an approved MP3. Another session handles getting to that MP3; do not read or change its work. Show its output only as the input.

Deliver an Excalidraw diagram of the whole system, top to bottom. Show every stage, the human review gates, model routing and fallbacks, quality checks, retries and resume, and delivery. Make technical decisions yourself; ask Drew one useful question at a time when a real choice is his.
