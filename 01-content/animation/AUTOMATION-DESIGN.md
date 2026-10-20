# Animation system canvas and automation design

**One canvas now holds the whole animation system: the standard, how we got here, the MP3-to-MP4 automation and the reference material. The automation is designed, not built.** Drew asked on 19 Oct 2026 for one combined canvas instead of separate flow drawings. A plain-words version of the whole process sits on the far right, from the first source search to the finished video, written as a film crew with Drew as producer. Each of its 19 steps has a note with Drew's options and what happens when something goes wrong. Steps 1 to 7 and their notes summarize the writing side's own README and edge-case review; nothing there was changed. Keep both versions.

[Open the board](http://localhost:3003/boards/268ae6e3f42cd1f87ff6d7b2) · [drawing](../diagrams/animation-system.excalidraw) · [builder](../diagrams/animation-system.build.py) · [layout checks](../diagrams/animation-system.checks.json) · [pictures](../diagrams/animation-system-images/)

## Editing it

Change wording or layout in the builder, then run `python3 01-content/diagrams/animation-system.build.py`. It rewrites the drawing atomically and checks it. The open board follows the file. Do not hand-edit the drawing, or the builder goes stale.

The checks replace screenshots, per Drew's rule. They cover unique IDs, two-way bindings, text fitting its shape, overlaps and arrows crossing anything they do not connect. Last run: 611 elements, 0 errors, 0 warnings.

## Technical decisions in the design

- **Runner:** grow `make_video.py`. Claude Code and Codex stay the agent runtimes.
- **Start:** when an MP3 is approved, Drew picks now, tonight or later. Drew chose this on 19 Oct. Tonight means 11 PM. Later waits for his go. He answers in chat, and an agent records it with one command.
- **Queue:** started videos run one at a time, in the order started. The MP3 must match its approval fingerprint.
- **Model ladder:** Opus 5.5 max, then GPT-6 Sol xhigh, then GPT-6 Astra xhigh. A Claude limit moves to Sol. Sol unavailable for a reason other than a limit moves to Astra. A Codex limit blocks both, so the run pauses and resumes at the first reset, starting at Opus again.
- **Quality failures never switch models.** The same model retries with notes.
- **Every AI job** gets a shell, file writing and image viewing, frames from the approved video, and the guard.
- **Reviewer:** a fresh session watches 5-fps filmstrips beside the approved video and checks the 15 known problems. It can send work back; it can never approve.
- **Retries:** Director twice, Animator twice per segment with the best try kept, render crash once. Then the video parks with its reason in a status note. Time limits: AI job 3 h, render 4 h.
- **Pilot clip gate** for risky segments only: the first segment Sol or Astra makes, or the first with new drawings. Drew chose this on 19 Oct.
- **New pests:** an Asset maker draws researched pieces in style C; Drew approves; they join the protected kit. Anatomy sources go in the source log.
- **Drew's notes:** Triage maps each note to a stage and time range. Only affected segments are redone, then the video is re-delivered as the next version.
- **Learning:** every verdict goes to `verdicts.jsonl`. A problem seen twice becomes a rule in `learned-rules.md`, read by every brief.
- **On approval:** the run is locked, the MP3 system is told the episode's sources are used, and the next MP3 starts.
- **Edge-case handling added with the plain flow:** two videos ready at once run one at a time; a Desktop name clash gets the next version number; a copy that fails its hash check is copied again; a restart resumes from the last finished piece; silence never counts as approval.
- **Not adopted:** best of two with Sol and Astra. It doubles usage, and Drew rated Astra "super bad".

## Gaps against today's runner

- Its router tries one model plus one backup. The design needs the three-step ladder, the shared Codex limit and pause-resume.
- Missing pieces: start choice and night start, reviewer, pilot gate, triage, verdict command, waiting and parked ledger states, learned rules, asset maker, final-file checks and the status note.
- Already there: prepare, director plan, segment loop with guard and motion check, join, render, and the Desktop copy with a hash check.

## Open for Drew

- Usage across many videos, including any Codex credit purchase.

## Outside this canvas

- The MP3 system belongs to another session. It appears only as the input.
- The closer, outro and music appear as future boxes.
- `../diagrams/production-flow.excalidraw` is an older video sketch, now outdated. It was left untouched.
