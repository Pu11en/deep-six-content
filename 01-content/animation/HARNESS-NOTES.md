# Notes for the future MP3-to-MP4 harness

**Keep what worked in the approved Opus 5.5 run. Default model for the harness: Opus 5.5 at max effort (Drew, October 19); Sol, then Astra, when Claude credits run out.** Drew approved the hook on the first try and the full video on its second render, unchanged. He wants this style for every video. Opus, GPT-6 Astra and GPT-6 Sol should all run the same method. This file records the method, the evidence and the requirements a harness must keep. The step-by-step recipe is [VIDEO-FLOW.md](VIDEO-FLOW.md).

## What Drew judged

- **Rejected earlier test:** "too little motion, too few scenes, visuals did not explain the narration's specifics, subtitle timing did not match speech." It was one static scene with a slowly walking ant.
- **Hook v1:** "It's really good ... I do like everything about it."
- **Full video v2:** "very, very good ... the design, how it flows, how it does stuff is very, very good." His only issue was the ending, which waits for the outro.

The difference between the rejected and approved versions is the method below, not the art style; both used cut-paper style C.

## The run, in order

Times are wall-clock on October 19, 2026 (Central Time). Each full render took about 17 minutes.

1. **Gather inputs before designing (about 15 minutes):**
   - The approved narration and its science limits.
   - The approved MP3 manifest and its fingerprint.
   - Drew's rejection feedback, quoted.
   - The approved style C frame and the brand palette.
   - `science-notes.md`: ant anatomy, no mound opening, no depths or temperatures.
   - Pacing research, run in parallel by a cheaper helper: the MacBook crawler plus measured cut and motion rates of 12 reference shorts. See `../research/2026-10-19-video-pacing/README.md`.
2. **Measure word timing precisely.** Three offline speech models voted on each word's start time, which was then snapped to measured silences and plosive dips. This fixed the old complaint about captions not matching speech. The method is now `tools/align_words.py`.
3. **Plan before drawing.** One shot list for the whole piece: one visible action per 1 to 3 spoken words, each landing on its word's first frame. The hook had 8 shots and 25 beats in 8.8 s. The full video had 76 shots and 123 beats in 79 s.
4. **Build reusable pieces first.** The kit came before any shot: paper pieces with shadow and grain, the articulated ant, captions and camera. Approved shapes were reused exactly, so the style never drifted. Later, whole sets were built once and reused across many shots: the nest cutaway with weather, the nursery close-up and the yard.
5. **Write shots as data over time.** Each shot sets camera keyframes plus a state for its set, such as brood amounts, water level, weather or rings. New code is needed only for genuinely new actions.
6. **Check your own frames, repeatedly.** Render one still per beat, look at every tile, fix, and repeat. Inspect suspicious tiles at full size. After every kit change, re-render the approved hook's sheet and confirm it is pixel-identical.
7. **Measure motion objectively.** Track the longest nearly still stretch and the share of the picture changing every half second. Full video v1 failed: one second still, 14% change. It was fixed before Drew saw anything; v2 scored 0.33 s and 17%.
8. **Check the encoded file.** Confirm both streams start at zero and have matching lengths. Pull frames from the MP4 on key words and confirm the right picture and highlighted word.
9. **Deliver.** Copy to the Windows Desktop, never opening a player. Add a board entry with a moving preview and the beat sheets.

Durations: the hook took under an hour from first read to MP4; the timing-to-MP4 part took about 20 minutes. The full video took about 65 minutes from Drew's approval to v2, including two renders.

## Problems the self-checks caught

A harness review step should look for each of these.

| Problem seen | Fix |
|---|---|
| Hero ant close-up cluttered by other ants | Keep neighbours out of the close-up window |
| Mound too small; magnifier hidden by captions and front grass | Enlarge; raise key action above y 1250; draw hand-held props last |
| `Path2D.addPath` drew tunnels as one big triangle | Draw tunnels as round-capped strokes; build paths by hand |
| Characters overlapping on one ground line after a pull-back | Space them, or walk them in during the move |
| Ants upside down on slopes | Use `rotation = path angle` and choose facing from direction |
| Empty sky in side views | Zoom until the subject fills most of the frame width |
| Motion blur made paper slides look ghostly | Blur only big zooms and whips; keep paper moves crisp |
| Brood and life cycle too small to read | Close-ups where items fill a third of the frame or more |
| A full lime loop vanished | An arc of exactly 2*PI draws nothing; stop just short |
| Magnifier never appeared | Its state was computed but not passed in; check each beat's named element is visible |
| Gauge overlapping the homeowner | Check props against characters at the beat frame |
| Tunnel ant above a "quiet", mound-less lawn | Hide anything above ground when the mound is off |
| Holds went still for up to 1 s | Keep the camera breathing (`live`) and push through holds |
| Drifting clouds off-screen during their shot | Check drifting props at the shot's actual time |
| Heat tint leaked into the sky | Clip effects to the region they describe |

## Objective checks and targets

| Check | Target | Approved video |
|---|---|---|
| Format | 1080x1920, 30 fps, 9:16 | Pass |
| Audio and video length | Equal, both start at 0 | 79.2 s each |
| Longest nearly still stretch | At most 0.35 s | 0.33 s |
| Picture changing per half second (median) | At least 15% | 17% |
| Hook regression after kit changes | Pixel-identical beat sheet | Pass |

Commands: `node render-shots.mjs <scene.json> --sheet | --at t1,t2 | --check-motion`, then a full render. The reference shorts we liked measured 4 to 62% picture change; the rejected test measured 0.1%.

## Model findings for the harness

- **Drew's verdict after watching:** both Astra clips (the 13-second test and its full-flow first half) are "super bad". Sol's 13-second test is "not bad". Still sheets and motion numbers had misled the agent into ranking Astra first.
- **GPT-6 Astra (Codex, ChatGPT subscription):** made the 13-second section in 9 minutes at xhigh effort with 15 shots. It invented compositions that failed in motion: brood floating in midair over an empty wall, a jumpy camera, near-static weather shots. It also planned 21 seconds (20 shots, 2 segments) and made segment 1.
- **GPT-6 Sol:** made the same section in 8 minutes with 9 shots. It stayed with the proven nest set and read clearly. Currently the better Codex choice.
- **GPT-6.1 Sol:** rejected by Codex on Drew's ChatGPT account on October 19 ("not supported when using Codex with a ChatGPT account"). Its availability through another route is unknown.
- **What made Astra good:** agent mode with a shell and the image viewer, so it could render its own frames and look at them. Earlier one-shot Astra runs had no shell and no image view, and produced the rejected single scene.
- **Usage:** each segment job used about 2 to 4 million input tokens (mostly cached) and 15,000 to 25,000 output tokens. The tests used up the ChatGPT Codex limit on October 19; access was back the same evening. Astra and Sol share that one limit. `KIT-API.md` now replaces reading 2,000 lines of source to cut usage.
- **Claude through Claude Code:** `claude -p --model <model> --output-format json --json-schema <schema>` works with the subscription login, and the result arrives in `structured_output`. Never use `--bare`: it switches to API-key billing. A trivial call counted as about $0.10 of plan usage. Opus runs this same method; it authored the approved video in this session.
- **Effort:** xhigh was enough for Astra. Ultra is untested in agent mode.

## Requirements the harness must keep

1. Agent mode with a shell, file writing and image viewing. The render-and-look loop is the main quality driver.
2. Deterministic local rendering with `--sheet`, `--at` and `--check-motion`, and frames as pure functions of time.
3. The kit and sets as shared building blocks. New topics add new researched drawings in the same style, never restyle old ones.
4. A whole-video plan for continuity, then segments of 6 to 15 seconds made one at a time. Resumable, keeping finished work.
5. Protected approved files. Agents only add new files; a guard restores anything touched. Approved outputs need a pixel regression check.
6. Objective checks are necessary but not sufficient: Astra's rejected clip passed them all. Quality review must watch motion, for example 5-frames-per-second filmstrips compared against the approved video, and Drew's viewing stays the final gate.
7. Model routing across providers. One provider's usage limit blocks all of its models, so the backup must come from the other provider, opt-in where it costs credits.
8. Delivery to the Desktop, never opening a player, plus a board entry.
9. Human gates stay human: only Drew approves.

## Where everything is

- **Method:** `VIDEO-FLOW.md`, `KIT-API.md`, `choreography/director-prompt.md`, `choreography/animator-prompt.md`.
- **Tools:** `tools/align_words.py`, `render-shots.mjs`, `make_video.py`, which is the current proto-harness with prepare, full, segment, render and deliver.
- **Approved reference:** `episodes/D6-6c917b49743b/full/` contains `words.json`, `shot-list.json`, `scene.json`, `renders/full-v2.*` and `progress.md`. The hook is in `episodes/D6-6c917b49743b/hook/`.
- **Reference code:** `scenes/paper-kit.mjs`, `scenes/nest-world.mjs`, `scenes/yard-world.mjs`, `scenes/hook-fire-ant-drought.mjs`, `scenes/d6-6c917b49743b-body.mjs`, `scenes/d6-6c917b49743b-full.mjs`.
- **Model tests:** `episodes/D6-6c917b49743b/model-test/` and `episodes/D6-6c917b49743b/runs/astra-ending/`. Each job folder keeps the exact brief sent, the event log, the final summary and the runner's report.

## Ways to make Astra or Sol do a good job (to test)

1. **Show the target.** Attach frames from the approved video to every run with `codex exec -i`. Astra only read text and code; it never saw what good looks like.
2. **Constrain shot types.** Build shots from the approved video's proven shot types and sets; allow a new composition only when the narration needs one.
3. **Watch, then judge.** Render 5-fps filmstrips and have a separate reviewer model compare them side by side with the approved video's strips, against the problem table.
4. **Pilot first.** Drew approves one 10-second segment before the rest of the video is made.
5. **Best of two.** Make each segment with both Sol and Astra and keep the better one (double usage).
6. **Learn from verdicts.** Save every Drew verdict with its reason; turn repeated failures into rules, as OpenAI advises for AGENTS.md.

## Prompting resources found on October 19

- OpenAI Codex docs: [Prompting](https://developers.openai.com/codex/prompting) and [Best practices](https://developers.openai.com/codex/learn/best-practices). They advise one clear task per run, saying what done looks like, planning first on hard tasks, and a short AGENTS.md grown from observed mistakes.
- OpenAI Cookbook [GPT-4.1 prompting guide](https://developers.openai.com/cookbook/examples/gpt4-1_prompting_guide): official, older, with an agentic prompt pattern that still applies.
- Unverified third-party GPT-6 notes: a [GPT-6 Sol prompting guide](https://promptessor.com/blog/gpt-6-sol-prompting-guide) and a [GPT-6 long-horizon agent guide](https://yage.ai/share/gpt6-long-horizon-agent-guide-en-20261008.html). Check them against OpenAI's own documentation.

## Open questions for harness research

- Which harness framework to build on, and whether Codex and Claude Code should stay the agent runtimes.
- How to share usage limits across several videos, including scheduling and Codex credit purchases (Drew's decision).
- Whether GPT-6.1 Sol becomes reachable, and whether Astra at ultra beats xhigh enough to justify the usage.
- How new pests get researched drawings before their first video.
- The closer and transition into the outro, the outro itself, and music. All are later sessions.
