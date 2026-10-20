# Deep Six video flow: approved MP3 to finished MP4

**This is how the fire-ant video was made. Drew approved its style on October 19, 2026; every new video follows it.** Reference video: `episodes/D6-6c917b49743b/full/renders/full-v2.mp4`. **Default model: Opus 5.5 at max effort (Drew, October 19).** When Claude credits run out, use GPT-6 Sol, then GPT-6 Astra, through Codex.

## The quality bar

1. **One picture per 1 to 3 spoken words.** Each action lands on the first frame of its word.
2. **Fast pacing.** A new shot every 0.7 to 1.5 seconds in the hook and never longer than 2 seconds anywhere. Something new appears about every half second.
3. **Constant motion.** The camera pushes or drifts through every hold. Antennae, grass, dust and clouds keep moving.
4. **Literal first.** Show the exact thing named. Use symbols only for absence or negation: a dashed outline, a purple X, a question mark.
5. **Cut-paper style C.** Every shape is a paper piece (`cut()`), with soft cast shadows and fibre grain. Natural insect and soil colours, plus Deep Six purple `#3A3148`, lime `#A9D554`, cream `#F0DDB2` and paper `#F6EFE2`.
6. **Word-synced captions.** Torn paper strips near y 1420. Lime tape marks the spoken word. One to four words per group.
7. **A few reusable sets.** Use three or four places per video, such as the nest cutaway, the nursery close-up and the backyard. Move the camera inside a set; cut hard on a new sentence or idea.
8. **Science limits.** Correct anatomy. No invented mechanisms, depths, temperatures or treatment advice. See `science-notes.md` and the episode's limits.
9. **Format.** 1080x1920, 9:16, 30 fps. Keep key action between y 250 and 1250; keep the bottom 300 px and right 120 px clear.

Measured on the reference: never still longer than 0.33 s; a median 17% of the picture changes every half second.

## Steps

1. **Word timing (local, free).** Three offline speech models, aligned to the approved script and snapped to silences:
   `python3 tools/align_words.py --manifest ../audio/<id>/<run>/comparison.json --out episodes/<id>/full/words.json`
2. **Director.** Plan every shot and refine the caption groups: [director prompt](choreography/director-prompt.md). Output: `shot-list.json` with absolute times.
3. **Animator, one segment at a time.** Write 8 to 15 seconds per segment: [animator prompt](choreography/animator-prompt.md). The animator checks its own work with the renderer and looks at the images:
   - `node render-shots.mjs <scene.json> --sheet` renders one still per beat.
   - `node render-shots.mjs <scene.json> --at 12.4,13.0` renders single frames.
   - `node render-shots.mjs <scene.json> --check-motion` measures the longest still stretch and the picture change.
4. **Assemble and render.** Join the segments into one module and render the MP4. A full 79-second render takes about 17 minutes.
5. **Check.** Format, matching audio and video length, motion targets, and frames pulled from the MP4 on key words.
6. **Deliver.** Copy the MP4 to Drew's Windows Desktop and never open a player. Add a board entry with a moving preview and the beat sheets.

## Run it

`make_video.py` is the runner (built October 20 from [AUTOMATION-DESIGN.md](AUTOMATION-DESIGN.md)). When Drew approves an MP3, an agent records his start choice with one command; a background worker then makes the video by itself, one video at a time, in the order started.

```
cd 01-content/animation
python3 make_video.py start --episode <id> --manifest ../audio/<id>/<run>/comparison.json --when now|tonight|later
python3 make_video.py status                       # where every video stands; restarts the worker after a crash or reboot
python3 make_video.py verdict --run <run> --decision approve|notes --says "Drew's own words"
python3 make_video.py go --run <run>               # start a "later" video, or retry a parked one
```

What the worker does, in order: verify the MP3 against its approval fingerprint; time every word (reusing `episodes/<id>/full/words.json` when the MP3 matches); the Director plans the lesson, checked by the runner; new drawings for a new pest (Asset maker, then Drew approves); each segment by the Animator, then the runner's checks, then a fresh Reviewer AI watching 5-fps filmstrips beside the approved videos; a pilot clip for Drew only on risky segments; join with the approved outro fitted to the narrator; a detached render; the approved MP3 re-muxed unchanged; file checks; a whole-video Reviewer; Desktop copy and board entry. Each run keeps a ledger (`run.json`) and a plain status note (`STATUS.md`) in `episodes/<id>/runs/<run>/`.

Every AI job tries Opus 5.5 (max), then GPT-6 Sol, then GPT-6 Astra (xhigh) when a model is out of usage or unavailable. A Codex usage limit blocks both Codex models, so the video pauses and resumes by itself at the first reset, starting at Opus again. A quality failure never switches models: the same model retries with notes (Director and Animator twice, a crashed render once), then the video parks with its reason. Drew's notes go through a Triage AI that redoes only the affected segments and re-delivers the next version. A problem seen twice becomes a rule in `learned-rules.md`, which every brief reads. Finishing steps without AI live in `video_finish.py`; offline tests in `tests/`.

**Usage limits.** Astra and Sol share one ChatGPT Codex usage limit, so switching between them does not help once it is used up. On October 19 the tests used it up; Drew's access was back the same evening (an Astra probe passed). A segment used about 2 to 4 million input tokens, mostly cached. The briefs now point agents to `KIT-API.md` instead of the full source, to use less. Claude Sonnet can join the ladder only when asked (`start --ladder opus,sonnet,sol,astra`); it is never automatic.

## Model test, October 19

GPT-6 Astra and GPT-6 Sol each made the same 13-second section from scratch through `make_video.py segment`, at xhigh effort. They could not see the approved version of that section. Both ran the render-and-look loop twice and changed no protected file.

| Model | Time | Shots | Longest still | Picture change |
|---|---|---|---|---|
| Opus 5.5 (approved video) | n/a | 13 | 0.33 s (whole video) | 17% (whole video) |
| GPT-6 Astra | 9 min | 15 | 0 s | 22% |
| GPT-6 Sol | 8 min | 9 | 0 s | 16% |

**Drew watched the clips and judged Astra's "super bad" and Sol's Test 3 "not bad".** My earlier reading, from still sheets and motion numbers, had it the other way round. Astra invented compositions that failed in motion: brood floating in midair over a mostly empty wall, a jumpy camera, near-static weather shots. Sol stayed in the proven nest set and read clearly. Automatic checks passed both, so they cannot be the quality gate; watching the motion is. Prefer Sol until a review step proves otherwise. GPT-6.1 Sol is not available to Codex on a ChatGPT account; GPT-6 Sol is. Results: `episodes/D6-6c917b49743b/model-test/`.

End-to-end test: Astra ran `full` on the last 21 seconds with the approved version withheld. It planned 20 shots in two segments in 7 minutes, then made segment 1 in 13 minutes, which passed every check. Segment 2 stopped when the Codex usage limit ran out. The finished half was joined, rendered and delivered: `episodes/D6-6c917b49743b/runs/astra-ending/`. Finishing it is optional; it would only add a test of joining two segments and resuming, which the first real episode will cover. The saved resume command finishes it.

## Files

- Kit: `scenes/paper-kit.mjs` contains paper pieces, the fire-ant worker, eggs, larvae and pupae, brood piles, carrying, captions, camera and effects.
- Sets: `scenes/nest-world.mjs` (cutaway with weather, water, heat, brood and ants) and `scenes/yard-world.mjs` (yard, homeowner, thought bubble, gauge, magnifier, pushpin, X, question mark).
- Reference modules: `scenes/hook-fire-ant-drought.mjs` (hook), `scenes/d6-6c917b49743b-body.mjs` (everything after it) and `scenes/d6-6c917b49743b-full.mjs` (assembly).
- Renderer: `render-shots.mjs`. Timing: `tools/align_words.py`. Runner: `make_video.py`, finishing steps `video_finish.py`, outro `scenes/outro.mjs`.

## Time conventions

Scene modules, shot lists and captions use absolute narration time, counted from the start of the MP3. A segment's `scene.json` sets `"absolute_time": true` with the segment's start and end, so the renderer draws frames at the real narration times.

## Still to decide in later sessions

- Music. The finish step has a marked place for a music bed (`audio_graph` in `video_finish.py`); the music session decides.
