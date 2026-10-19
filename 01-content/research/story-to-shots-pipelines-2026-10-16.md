# Story to shots: how open pipelines do it (2026-10-16)

## Top takeaway

Every working pipeline does the same thing: **lock the story in words first, then cut it into shots with a hard "one primary action per shot" rule, then run a critic before any pixels.** Our clips failed because we skipped those two gates. We can copy the prompts below (ViMax and VideoClaw are MIT) with small edits for a cartoon reaper.

## Recommended pipeline for us

1. **Fact card.** One fact, the exact voiceover line, one thing the viewer can SEE prove it ("single demo").
2. **Premise writer.** Reaper wants something (motivation), a pest blocks or causes it, result proves the fact. Link beats with "but/therefore", never "and then". Ending first.
3. **Beat sheet.** About one beat per 2-4 s. 15 s = 3-5 shots, 30 s = 6-8 (ViMax default 3-5; MAViS 5 s each). 15 s of VO is about 35-40 words.
4. **Shot writer.** One primary action per shot. Fixed camera count, first frame, last frame, motion line, VO line per shot.
5. **Critic.** Checks motivation, one action, cause then effect, screen direction, positions. Fails send back to step 4 (max 2-4 rounds; MAViS uses 4/2/1).
6. **Animatic gate (Drew approves).** Stills plus VO at real timing. Cheap. Nothing is rendered before this.
7. **Locked mascot sheet** pasted verbatim into every prompt; first-frame image-to-video; VLM picks best of N takes.
8. **Edit.** Cut on motion, match cuts, VO leads the picture.

## Best prompt templates (verbatim, source in brackets)

**Shot-writer rules** [ViMax `agents/storyboard_artist.py`, MIT]
> Each shot must have a clear narrative purpose—such as establishing the setting, showing character relationships, or highlighting reactions.
> When designing a new shot, first consider whether it can be filmed using an existing camera position. Introduce a new one only if the shot size, angle, and focus differ significantly.
> When describing visual elements, it is necessary to indicate the position of the element within the frame. ... Ensure that invisible elements are not included.
> When describing a character, it is necessary to indicate the direction they are facing.
> Each shot requires an independent description without reference to each other.

**First frame / last frame / motion split** [ViMax, same file]
> Ensure the first and last frame descriptions are pure "snapshots," containing no ongoing actions (e.g., "He is about to stand up" is unacceptable; it should be "He is sitting on the chair, leaning slightly forward").
> The last frame description must be logically consistent with the first frame description and the motion description. All actions described in the motion section should be reflected in the static image of the last frame.
> Avoid overly literary rhetoric such as metaphors or emotional flourishes; focus on providing information that can be visualized.
> The first shot must establish the overall scene environment, using the widest possible shot. Use as few camera positions as possible.

**One action per shot** [MAViS paper, arXiv 2508.08487]
> it is advisable to limit each shot to a single, simple action. (Scriptwriter prompt: "Each shot must include only one primary action." "complex actions should be broken into multiple shots." "Do not show the same character in two adjacent shots" unless separated.)

**Video-prompt writer** [Anim-Director `videogen.py`, no license]
> Prompt Structure: ... Subject + Motion + slightly Camera Movement + ,3D animation.
> Assign more common and simple actions to characters, and avoid overly complex or delicate actions or objects.
> Don't add anything that can't be shown on the video screen. For example, the content of spoken words should not be included in the prompt.
> Do not abuse the Camera Movement.

**Critic** [FilmAgent `director_3.txt`, MIT, in HITsz-TMG/VideoClaw]
> Check whether any character has violated the rule that a character can only add one action at a time. ... Check whether any character transitions from a standing state to a sitting state without using "Sit Down" ...
> Assess whether the script flows smoothly ... ensuring there are no abrupt jumps or sudden plot twists that disrupt the flow. If not, first identify the dialogues in the script that lead to this outcome, then provide detailed revision suggestions.

**Reviser/reviewer pair** [MM_StoryAgent `prompts_en.py`, Apache-2.0]
> Review the image description corresponding to the given story content. If the requirements are met, output "Check passed.". If not, provide improvement suggestions.

**Staging continuity checker** [VideoClaw `staging_continuity_zh.txt`, MIT; Chinese, my translation]
> Within one scene, unless an entrance, exit, seat change or walk is stated, each character's relative position, facing and relation to furniture/doors/walls must stay the same. After a stated move, later shots must start from the result ("walks to the door" then character is at the door). Fix only position, facing, gaze, camera and spatial relations; do not change plot or add/remove shots.

**Our critic (my adaptation, not a quote).** Score each shot pass/fail: (1) Why does the reaper do this? Name the cause in the previous shot. (2) Exactly one verb? (3) Does shot N+1 start where N ended? (4) Same left/right facing as the last shot? (5) Does the picture alone show the fact, with sound off? (6) Does the VO line match what is on screen at that second? Return failing shot ids with a rewrite.

## Per-repo entries

| Repo | Stars | License | Last push | Verdict |
|---|---|---|---|---|
| [HKUDS/ViMax](https://github.com/HKUDS/ViMax) | 12.7k | MIT | 2026-09-30 | **Best source.** idea, characters, script, storyboard, first/last-frame split, camera tree, ref-image picker, best-image judge. Defaults to 1 scene, 3-5 shots. Read all prompts. |
| [HITsz-TMG/VideoClaw](https://github.com/HITsz-TMG/VideoClaw) (FilmAgent lives here) | 1.9k | MIT | 2026-08-26 | **Very useful.** Segment plan, shot design, staging-continuity patch pass, plot/dialogue evals, "doctor" prompt rewriter. Prompts partly Chinese. |
| [calesthio/OpenMontage](https://github.com/calesthio/OpenMontage) | 68.9k | AGPL-3.0 | 2026-10-16 | **Ideas only (AGPL).** `skills/creative/storytelling.md`, `video-gen-prompting.md`, animation `scene-director.md`: five-slot prompt (Subject, Subject Motion, Scene, Spatial, Camera), "no mood adjectives, name the visual cause", human gate after each stage. |
| [HITsz-TMG/Anim-Director](https://github.com/HITsz-TMG/Anim-Director) (AniMaker) | 262 | none | 2026-01-07 | Good for cartoons: max 2 characters per clip, 5-8 clips, entry/exit clips, script checker. No license, so adapt ideas only. |
| [X-PLUG/MM_StoryAgent](https://github.com/X-PLUG/MM_StoryAgent) | 309 | Apache-2.0 | 2024-08-23 | Narrated kids storybook; reviser+reviewer per field; images stay static, no plot. Old but clean pattern. |
| [aicontentskills/ai-video-storyboard-skill](https://github.com/aicontentskills/ai-video-storyboard-skill) | 65 | none listed (README says MIT) | 2026-04-09 | Claude skill; shared Visual Theme block, 5 s shots, 40-80 word prompts. Thin on motivation. |
| [hoodini/ai-agents-skills `director`](https://github.com/hoodini/ai-agents-skills) | 288 | none | 2026-07-11 | Claude skill; gated "no pixels before story locked", 13-thumbnail test, editing-theory and consistency chapters. Good reading. |
| [showlab/MovieAgent](https://github.com/showlab/MovieAgent) | 368 | none | 2025-03-26 | Screenwriter-CoT splits synopsis into sub-scripts; skimmed only. Film-scale, not ours. |
| [DuNGEOnmassster/VideoGen-of-Thought](https://github.com/DuNGEOnmassster/VideoGen-of-Thought) | 66 | BSD-3 | 2025-09-22 | Short shot line, then 5-domain detail. Needs GPU stack; only sample outputs read. |
| [lichao-sun/Mora](https://github.com/lichao-sun/Mora) | 1.6k | none | 2024-10-10 | Video-model agents, not story. Not opened. Skip. |
| smixs/visual-skills (521), pexoai/pexo-skills (803, MIT), elementsix-skills (312, MIT) | | | | Found, **not read**. |

**Not found / not usable:** StoryAgent, DreamFactory, AutoStory (papers only, no code found). MAViS (paper only; prompts are in its supplement). n8n faceless-short templates exist (n8n.io workflows 6014, 17408) but are script plus image-prompt per scene with no motivation or critic step. GitHub search was rate limited mid-run, so the sweep is not exhaustive.

## Consistency tricks that recur

- ViMax: one character ID per character, first-frame ref pulled from the nearest earlier shot of the same camera; a VLM judge ranks N candidates on character, space and text match.
- hoodini guide: paste the identity block verbatim, never paraphrase; mascot sheet image beats words.
- Anim-Director: refer to characters by look ("the boy in green") in motion prompts, not by name.
- Cutting trick: match cut on a shared motion hides identity drift between clips.

## Principles (with sources)

- **Staging:** "the presentation of any idea so that it is completely and unmistakably clear" (Thomas and Johnston, *Illusion of Life*, via [Wikipedia](https://en.wikipedia.org/wiki/Twelve_basic_principles_of_animation)). One clear subject per frame.
- **Anticipation:** a preparatory move readies the viewer; give each gag a wind-up shot or pose before the action.
- **Timing, secondary action:** secondary action must support the main action, not compete with it (same source).
- **Cause then effect (Kuleshov):** viewers build meaning from adjacent shots; the original footage is lost and a 1992 replication failed, later studies support it ([Wikipedia](https://en.wikipedia.org/wiki/Kuleshov_effect)). Practical use: show the pest's act, then the reaper's reaction.
- **Screen direction / 180 rule:** keep the axis; a character leaving frame left enters the next shot from the right ([Wikipedia](https://en.wikipedia.org/wiki/180-degree_rule)). (The 30-degree rule was not explained in that source.)
- **Cut on motion, Murch's rule of six (emotion 51%, story 23%, rhythm, eye-trace, 2D, 3D):** secondhand from the hoodini bible, not checked against Murch's book. Treat weights as a heuristic.
- **Explainer pacing (secondhand, OpenMontage notes citing Mayer, Muller, Kurzgesagt):** 150-160 wpm, one new concept per 30-45 s, new visual every 3-5 s (short-form note says 1-3 s). Unverified numbers; test on our own retention.
- **Educational channels (documented):** Kurzgesagt's own [process page](https://kurzgesagt.org/youtube/) says script (about a dozen drafts), then sketching, then "His voiceover provides the timing for the animation team", with no mention of storyboard or animatic. A TED-Ed lesson by [Buzzco](https://buzzco.nyc/?p=366) went script, voiceover, storyboard/animatic (4 days), animation. **Dr. Binocs: nothing documented found.** Lesson: voice is recorded first and picture is timed to it.

## Caveats

- Quotes were copied from the live repos on 2026-10-16. Star counts are as of that day.
- Nobody here proves these critics fix "no motivation". The motivation check in our critic is my design; test it on 3 facts before trusting it.
