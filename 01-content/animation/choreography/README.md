# How narration becomes animation

**Two prompts, one kit, one check loop.** The first test, the hook of episode D6-6c917b49743b, used this flow.

1. **Timing.** Three offline speech models give word times. Silences and plosive dips in the waveform correct them. Output: `words.json`.
2. **Director.** [Director prompt](director-prompt.md) turns words and times into a shot list: one visible action per phrase, landing on its word. Output: `shot-list.json`.
3. **Animator.** [Animator prompt](animator-prompt.md) turns the shot list into a scene module built on the shared kit, `scenes/paper-kit.mjs`.
4. **Self-check.** The renderer draws one frame per beat into a contact sheet. The animator fixes mismatches before Drew sees anything.
5. **Drew reviews** the MP4 with sound. Feedback goes into the review file next to the video.

Why two prompts: planning pictures and writing drawing code are different jobs. The shot list is short, readable and easy to change. Code changes stay local to one shot.

Pacing used in the hook: 8 shots in 8.8 seconds, with a new action every 0.2 to 0.5 seconds. Each action lands on the start frame of its word.

Full video (D6-6c917b49743b): 76 shots and 123 timed beats over 79 seconds, built on three reusable sets: the nest cutaway (`scenes/nest-world.mjs`), the nursery close-up and the backyard (`scenes/yard-world.mjs`).

## Run it with Astra or Sol

The whole flow is automated in `make_video.py`; see [VIDEO-FLOW.md](../VIDEO-FLOW.md). Agents read the short kit reference `KIT-API.md` instead of the source.

## Run it by hand

```
cd 01-content/animation
node render-shots.mjs episodes/D6-6c917b49743b/hook/scene.json --sheet      # beat contact sheet
node render-shots.mjs episodes/D6-6c917b49743b/hook/scene.json --at 6.7     # one frame
node render-shots.mjs episodes/D6-6c917b49743b/hook/scene.json              # full MP4 (new revision only)
```

The full render never overwrites an existing revision. Change `revision` in `scene.json` for a new candidate.

## Limits

- Word times are machine-aligned, checked against the waveform, not by a person listening.
- This hook was authored in one session by Opus 5.5 following these rules. A fresh agent has not yet run the prompts cold.
- The kit has one insect, the fire-ant worker. New pests need new, researched drawings.
