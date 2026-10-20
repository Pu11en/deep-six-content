# Video session: next steps

**The fire-ant video is done and Drew loves it. The flow that made it is saved. Default model: Opus 5.5 at max effort; Sol, then Astra, only when Claude credits run out.**

## State on October 19

- **One canvas for the whole animation system** (Drew, October 19): [board](http://localhost:3003/boards/268ae6e3f42cd1f87ff6d7b2), [drawing](../diagrams/animation-system.excalidraw). It shows the standard, the history, the MP3-to-MP4 automation design and the reference. Keep it the single animation canvas and edit it through its builder. Drew chose a pilot clip only on risky runs, and picks each video's start (now, tonight or later) when its MP3 is approved. Decisions and gaps: [AUTOMATION-DESIGN.md](AUTOMATION-DESIGN.md).
- Final video: `episodes/D6-6c917b49743b/full/renders/full-v2.mp4` (79.2 s, 9:16). Desktop: `Deep Six - Fire Ants Full v2.mp4`. Drew: "the video is very, very good"; keep this style for every video. Its only weak point is the ending (see below).
- The recipe: [VIDEO-FLOW.md](VIDEO-FLOW.md). Prompts: [choreography](choreography/README.md). Timing tool: `tools/align_words.py`. Runner: `make_video.py`.
- **For the future harness (Opus 5.5, Astra or Sol):** [HARNESS-NOTES.md](HARNESS-NOTES.md) records what worked in the approved run, every problem the self-checks caught, the model test numbers and the requirements to keep. Drew plans to research harness options before building it.
- Model test: Astra and Sol each made the same 13-second section from scratch. **Drew watched them: Astra's clips are "super bad"; Sol's Test 3 is "not bad".** Automatic checks passed both, so watching is the real test. See HARNESS-NOTES.md for ways to make Codex runs reliable. Desktop: `Deep Six - Model Test 1 Opus.mp4`, `2 Astra`, `3 Sol`, and `4 Astra Full Flow (first half)`. Details in VIDEO-FLOW.md.
- The Codex usage limit ran out during the October 19 tests; Drew's access was back the same evening. Astra and Sol share one limit. Astra's end-to-end run stopped after its first segment; finishing it is optional (`episodes/D6-6c917b49743b/runs/astra-ending/resume-command.txt`).
- Claude Sonnet can run the same jobs with `--backup sonnet` (Claude plan credits, opt-in). It was wired and probed with one tiny request, not run on a full segment.
- Drew watches videos from his Windows Desktop. Copy each MP4 there; never open a player.

## Handoff from the canvas session (October 19)

- **Done:** the canvas has the technical flow, plus a plain-words flow from the first source search to the finished video, with options and what-ifs beside every step. Change it only through `../diagrams/animation-system.build.py`, then re-run it; its checks replace screenshots.
- **Drew decided:** a pilot clip only on risky runs. He picks each video's start (now, tonight at 11 PM, or later) when its MP3 is approved.
- **Next:** build the automation by growing `make_video.py`, starting from the gaps in [AUTOMATION-DESIGN.md](AUTOMATION-DESIGN.md). Nothing new is built yet.
- The writing side's notes were read for the plain flow and never changed.

## Make the next video

```
cd 01-content/animation
python3 make_video.py prepare --episode <id> --manifest ../audio/<id>/<run>/comparison.json
python3 make_video.py full --episode <id> --run <id>-opus --desktop-name "Deep Six - <title>.mp4"
```

`full` plans the whole video, splits it into segments, has the agent make and check each segment, joins them, renders and copies the MP4 to the Desktop. Opus is the default; if it is unavailable the run falls back to Sol. Use `--model sol` or `--model astra` to choose a Codex model. Opus through this runner has only been probed, not run on a full job; this session's video was made by Opus directly. A new pest (for example cockroaches) needs new researched drawings first; the director lists them under `new_assets`.

## Later sessions (Drew's plan)

1. **Closer and transition**: a short transition line and picture that lead into the outro. Decide after the outro exists.
2. **Outro**: made separately with video generation and the Deep Six branding assets.
3. **Music**: separate.

## Known limits

- Word times are machine-aligned and checked against the waveform, not by ear.
- A full 79-second render takes about 17 minutes; agent steps take about 9 minutes per segment at xhigh effort.
- GPT-6.1 Sol is not available to Codex on Drew's ChatGPT account; GPT-6 Sol is.
