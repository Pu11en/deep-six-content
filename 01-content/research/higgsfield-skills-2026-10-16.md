# Open-source Higgsfield skills (research, 16 Oct 2026)

Takeaway: the best video-prompting craft found so far. Two repos matter: Higgsfield's official skills (has a narrated mascot explainer skill, our exact format) and OSideMedia's prompt skill (Higgsfield's open-sourced lessons from a 95-minute AI feature film, "Hell Grind"). Both MIT. Read only; nothing installed. Stars/license/push from GitHub API.

## Repos

- higgsfield-ai/skills: 1,307 stars, MIT, pushed 2026-09-26. Official. `higgsfield-video-explainer` (narrated cartoon explainer from 10 s blocks, mascot mode), brandkit, soul-id (character identity), thumbnails. Needs Higgsfield CLI/account to run; prompt rules are portable.
- OSideMedia/higgsfield-ai-prompt-skill: 749 stars, MIT, pushed 2026-09-27. 35 sub-skills. Best: higgsfield-acting, higgsfield-seedance/FAILURE-MODES.md, HELL-GRIND.md, higgsfield-shotlist-director, higgsfield-scene-engine.
- machina-exm/film-studio-skills: 153 stars, no license, pushed 2026-08-14. Asset passports, stress-test (test character with cheap stills before video), 15-block shot prompt. Ideas only.
- Others seen, not read: beshuaxian/higgsfield-seedance2-jineng (973, Chinese, no license), AKCodez/higgsfield-claude-skills (437), rediumvex/ai-video-generator-claude (420, MIT, marketing templates), cth9191/motion-design (250), robonuggets/higgsfield-skill (68), wide-trace/open-higgsfield (4,377, an app, not prompts).

## Rules worth adopting

Official explainer skill (higgsfield-video-explainer/references/prompts.md):
- Video is built from 10 s blocks. Each block = one narration line (20-24 words, about 8-9 s) + one clip with ONE clear action that matches that line.
- Voice takes are made first, clips second, then assembled.
- One style-key image attached to every clip + one identical STYLE descriptor pasted in every clip prompt.
- Clip audio is ambient only; characters never speak or lip-sync. Narrator carries all words.
- Mascot mode: block 1 greets by gesture, mouth closed; last block waves a sign-off.
- Block format: STYLE REFERENCE / SCENE (one clear action) / MOTION (camera + animation) / AUDIO (no voice) / NEGATIVE.

Acting skill (OSideMedia, from Higgsfield's feature film):
- Acting is behavior under pressure: objective (a verb), obstacle, tactic. Never write the emotion.
- States, not transitions: models fail processes that reverse direction (reach in, pull out, wind up) and nail states ("mid-throw, arm extended"). Start complex action already in progress; the approach is a separate shot.
- The reaction is worth more than the action: after every event, show the face of whoever saw it.
- Eyes need a task (look at something specific). Dead eyes = the number one AI tell.

Failure modes (FAILURE-MODES.md), each matched what we saw in test 1:
- Action-reversal fill: a short action finishes early and the model plays it back in reverse to fill time. Fix: chain 2-3 same-direction actions, or give a held end state.
- Truncated action: the cut lands before the result. Fix: price shots by what must FINISH, and state the end state.
- Keyframe forces invention: if the prompt needs an object the start image doesn't show, the model invents it in a wrong place (our second magnifying glass). Fix: everything the shot needs must be in the keyframe.
- Mimed manipulation: hands move, object doesn't change. Fix: write the mechanism and the object's visible change.
- Multi-motion camera overload: one camera move only.
- Walking is the hardest stunt: avoid long walks; feet glide.

Shotlist director: no 3 cuts in a row with the same shot size and camera move; one longer hero hold per sequence; cut durations must add up to the runtime.
Film-studio stress-test: before any video, test the mascot with cheap stills in every angle, shot size and lighting the film needs.
