# MP3-to-MP4 automation: build note (20 Oct 2026)

**The designed automation is built into `make_video.py`. An approved MP3 now becomes a finished, checked video on the Desktop with no hand work, except Drew's gates.** Design: [AUTOMATION-DESIGN.md](AUTOMATION-DESIGN.md). How to run it: [VIDEO-FLOW.md](VIDEO-FLOW.md#run-it).

## What was built

- `make_video.py`: start choice (now, tonight at 11 PM, later), one background worker, ledger and status note per run, model ladder with pause and resume, Director, Asset maker, Animator, Reviewer and Triage roles, pilot gate, verdicts and learned rules.
- `video_finish.py`: the ensign-wasp hand scripts as reusable steps: outro fit, exact audio, motion check, outro check, key-word frames, filmstrips, crash-safe render helpers, Desktop copy.
- `scenes/outro.mjs`: the approved outro for any runner-made video.
- `learned-rules.md` and `problems-seen.json`: two rules already learned (small subjects too small; marks hidden under later drawings). The egg-case "teeth" problem waits for a second sighting.
- `tests/test_make_video.py` (offline) and `tests/replay_wasp.py` (end to end on the approved ensign-wasp episode).
- `KIT-API.md` now lists the wasp, cockroach, egg-case and under-sink drawings, so the next cockroach video reuses them.

## Proof

Test run on the approved ensign-wasp episode, in its own folder ([status](episodes/D6-01096ba333e3/runs/d6-01096ba333e3-replay/STATUS.md), [comparison](episodes/D6-01096ba333e3/runs/d6-01096ba333e3-replay/replay-compare.json)). The Director and Animator outputs were the approved hand-made ones; every later step was the runner's own.

| Check | Result |
|---|---|
| Offline tests (fake models, temporary folders) | 25 of 25 pass |
| Outro fit against the hand-made plan | Same 148-frame plan; 9 frames trimmed; logo lands 46.867 s, "Deep" 46.91 s; 1 s hold |
| Runner's picture render against the approved one | Byte-identical |
| Runner's finished MP4 against the one Drew approved | Byte-identical: all 1472 frames and every audio sample |
| Audio against the approved MP3 | Lag 0 ms, correlation 0.99997, level -0.01 dB |
| Lesson motion (outro hold excluded) | Longest still 0.233 s, change 22% (targets 0.35 s, 15%) |
| Outro frames against the approved animation | Mean difference 1.83 of 255 (limit 6) |
| Crash test 1: runner killed mid-render | The render kept going; `status` restarted the runner, which waited for it |
| Crash test 2: runner and render killed at frame 601 | On restart, v1 was marked failed and v2 rendered by itself past the leftover partial file |
| Approved hook check (runs after every Animator try) | Beat sheets pixel-identical |
| Desktop copy | `Deep Six - Runner Test Ensign Wasp v1.mp4`, checksum match, no player opened |
| Whole-video Reviewer, one real Opus call | 14 min, 72,000 output tokens, 5.2 million cached input tokens; read all strips and rendered 54 close-ups |

**The Reviewer sent back one note on the video Drew approved:** the egg cases are small in the dim under-sink shot at 41.9 s ("look for egg cases"). It applied the learned "small subjects" rule. So real runs may spend a fix round on things Drew would accept. The test run then had its review step marked done by hand, so delivery could be tested, and was stopped afterwards.

## Limits

- The Director, Animator, Asset maker and Triage roles were not run for real in this build: a full video needs hours of Opus usage. The Claude call path did run for real (the Reviewer), the Codex path ran on October 19 with Astra and Sol, and the new logic around the roles is covered by the offline tests with fake models. The first real episode is their real test.
- Usage-limit messages from Claude and Codex are matched by pattern. A new wording would show as "unavailable" and still move down the ladder.
- "Tonight" needs the computer on at 11 PM. After a restart, `make_video.py status` restarts the worker.
- Outro fit trims at most half the reaper's scan. A narrator who reaches "Deep" sooner than that parks the video with a plain reason.
- Music: not added. `audio_graph` in `video_finish.py` is the marked place for a bed.
- The guard restores any protected file changed during an AI job, including hand edits made at the same time. Edit runner files only while no video job runs.
- One Reviewer pass on a whole video used about 14 minutes of Opus at max effort. A four-segment video gets five Reviewer passes.
- Settled 20 Oct: Drew kept the ladder (Opus, then Sol, then Astra). The canvas now shows it; the runner already did.
