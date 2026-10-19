# How the best repos write video prompts (research, 2026-10-16)

**Takeaway:** The repos agree. A clear action is a short chain of physical beats: setup, trigger, one visible action, a visible reaction, a visible end state. Weak prompts name a mood or a result ("scared", "the door opens"). Strong prompts say who does what, in what order, with what contact, and what the viewer sees at the end. Our owner is right that this is skill, and there are published methods for it. Read only the files named below. Budget 5-10 generations per clip you keep (ai-shortfilm-prompts cheatsheet: 2-3 rerolls for easy shots, 20+ for hard ones).

Method: `gh search repos/code` plus web, about 35 queries. I cloned and read the files listed. No generation was run. Counts and dates are from the GitHub API on 2026-10-16.

## Rules that repeat across repos

- **One clear action per shot, one camera move.** Sora cookbook, Rylaispirit, Seedance 2.5 notes (Square-Zero), Veo guide.
- **Write actions as numbered or timed beats, not "walks across the room".** Sora cookbook ("takes four steps to the window, pauses, pulls the curtain in the final second"), Rylaispirit (`0-4s`/`4-10s` blocks, 3-5 beats max per 10s), ai-shortfilm-prompts, Veo (`[00:00-00:02]`), stickman-video-director (`[0-3s] [3-7s] [7-10s]`).
- **Do not overload.** An 11-item list yields 4-5 items; 9 scenes in 18s drops scenes (Rylaispirit). Shorter clips obey better; two 4s clips beat one 8s clip (Sora cookbook).
- **Start state, one action, end state.** drama-skills ("start, single action, end"; the action needs trigger, contact, landing). Square-Zero Seedance 2.5 ("End on [specific final image]").
- **Name cause and effect and the visible result.** Square-Zero Seedance 2.0 ("call out cause and effect"), Rylaispirit ("at 4s the second door swings fully open" beats "the door opens"), drama-skills.
- **Use common, whole-body actions. Avoid fine ones.** drama-skills `generability.md`: safe = walk in, sit, turn, hand over, push door. Risky = precise interception, two-hand 4-step chains, micro-expressions, "no X" actions. Test: can someone mime your sentence without explanation?
- **Turn feelings into visible acts.** drama-skills: "suddenly realises" becomes "brow furrows hard, turns toward the door". Rylaispirit: emotion as an ordered chain of beats plus an explicit ban ("tears stay in her eyes and never fall, no crying, no smiling") or the model overacts.
- **Comedy is staged: setup, escalation, payoff, with room to breathe.** stickman Style 3 ("setup, escalation, ironic payoff"; a deadpan 0.5-2s reaction can be the payoff). MiniMax shot spec: hook types (`visual-joke`, `reversal`, `callback`), "anticipation, squash-and-stretch, overshoot, follow-through", comedic silhouettes.
- **Restraint at the end.** ai-shortfilm-prompts: no effects pile-up at the close ("Just {subject} {action}...").
- **Freeze the character with a full written anchor and repeat it in every clip.** stickman ("never 'same character'; repeat the FULL description"), ai-shortfilm-prompts (2 distinguishing marks), Rylaispirit, MiniMax (character cards), Sora cookbook.
- **Track props.** stickman: say where each prop starts, who hands it over, where it ends; no spawning objects. MiniMax: spatial anchors, screen positions and facing for each character.
- **Image-to-video: do not redescribe the image.** Prompt motion, camera, performance, audio only. Square-Zero (global rule), MiniMax I2VA ("first-frame anchor, action onset, continuous development, result"), Sora cookbook.
- **Concrete nouns, no praise words** ("cinematic", "stunning", "epic"). ai-shortfilm-prompts Rule 1, MiniMax tips.
- **Say what you want, not what to avoid.** Veo guide, Rylaispirit 8.10, drama-skills (negatives only where needed, and positive states first).
- **Cartoon styles: lock the medium once, repeat it per shot.** MiniMax ("animation medium, line and shape language... active across every shot"), Rylaispirit 8.8 (style drifts when a new subject appears). Keep text out of the clip; add titles in editing.
- **Counter-view:** vibe-creating-skill says drop camera/lens numbers and describe the one visual anchor, one action, one tone. This helps for emotion, hurts for precise gags.

## Per-repo entries (ranked by usefulness for us)

1. **openai/openai-cookbook**, `examples/sora/sora2_prompting_guide.ipynb`. https://github.com/openai/openai-cookbook. 76,652 stars, MIT, pushed 2026-10-16. Official Sora 2 guide: prompt anatomy, weak vs strong, an Actions-list template, a 2D/3D robot example with dialogue and comedic beats. Verdict: **best single read** for action beats and short clips. Not Veo-specific.
2. **kaomei/stickman-video-director**. https://github.com/kaomei/stickman-video-director. 2,190 stars, MIT, pushed 2026-10-16. Skill for 2D stick-figure cartoon prompts: 10s clips, three timed beats, character-anchor rules, prop ownership, a "dark comedy" mode (`references/prehistoric-dark-comedy.md`), cast cards, negatives. Closest to our use case (flat 2D cartoon, educational, comedy). Verdict: **strong; copy the structure**. Written for Gemini Omni Flash. Not tested by me.
3. **zenstory-ai/drama-skills** (`short-drama-video-prompts`). https://github.com/zenstory-ai/drama-skills. 2,965 stars, MIT, pushed 2026-10-15. Chinese. Start-action-end rules, action budget, `generability.md` (which actions models can do), continuation between clips. Photoreal drama, not cartoon. Verdict: **best "will the model do this action" checklist**.
4. **MiniMax-AI/MiniMax-H3** (`skills/`). https://github.com/MiniMax-AI/MiniMax-H3. 10,052 stars, no license file found, pushed 2026-08-15. Official vendor skills: `h3-prompt-writing` (T2V/I2V/first-last-frame formats, camera as motion + amplitude + speed), `3d-animation-short-generator` (six-column shot table, per-second directives, hook types, self-check gate). Verdict: **best for storyboard discipline**. Skill assumes MiniMax Hub.
5. **jnMetaCode/ai-shortfilm-prompts**. https://github.com/jnMetaCode/ai-shortfilm-prompts. 475 stars, MIT, pushed 2026-10-12. Five-stage template, seven hard rules, 25+ genre templates (claymation, talking-animal vlog, micro-drama). Verdict: **good templates; aimed at photoreal cinematic**. Its camera/lens advice does not suit cartoons.
6. **Rylaispirit/cinematic-video-prompt-skill**. https://github.com/Rylaispirit/cinematic-video-prompt-skill. 152 stars, MIT, pushed 2026-09-27. Vocabulary tables plus section 8, "real lessons from comparing ~1100 prompts with 65 results". Vietnamese/English. Verdict: **section 8 is the gold; the rest is a glossary**.
7. **Square-Zero-Labs/video-prompting-skill**. https://github.com/Square-Zero-Labs/video-prompting-skill. 185 stars, Apache-2.0, pushed 2026-08-25. A per-model guide router (Veo 3, Seedance, Wan, LTX, MiniMax) plus a character-sheet workflow. Verdict: **useful for model-specific syntax**. Check each guide's source first.
8. **songguoxs/seedance-prompt-skill**. https://github.com/songguoxs/seedance-prompt-skill. 2,927 stars, no license, pushed 2026-02-12. Chinese Seedance 2.0 recipes (@reference system, extension, one-take). Only skimmed. Verdict: model-specific; older.
9. **Alisa0808/vibe-creating-skill**. https://github.com/Alisa0808/vibe-creating-skill. 150 stars, NOASSERTION (LICENSE file present), pushed 2026-06-17. Rewrites prompts toward emotion/visual anchor; has "absurd skit" examples. Verdict: **counterpoint, use sparingly**.
10. **zhouwei713/seedance-prompt**. https://github.com/zhouwei713/seedance-prompt. 328 stars, MIT, pushed 2026-08-04. Anti-AI-look checklist for photoreal handheld footage. Verdict: **skip for cartoons**.

Not repos but useful: [Google Cloud Veo 3.1 guide](https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-veo-3-1). Formula `[Cinematography] + [Subject] + [Action] + [Context] + [Style & Ambiance]`; no cartoon examples.
Noted but unread: `kaomei/hand-drawn-video-prompts` (267 stars, MIT, 2D doodle style). Awesome lists (`songguoxs/awesome-video-prompts`, 589 stars) have lots of prompts but almost no method.

## Verbatim example prompts

**A. Cartoon character, comedic beats (Sora cookbook, Example 1; middle paragraphs cut)**
```text
Style: Hand-painted 2D/3D hybrid animation with soft brush textures, warm tungsten lighting, and a tactile, stop-motion feel. [...]
At the center, a small round robot sits on a wooden bench, its dented body patched with mismatched plates and old paint layers. Its large glowing eyes flicker pale blue as it fiddles nervously with a humming light bulb. [...]
Actions:
- The robot taps the bulb; sparks crackle.
- It flinches, dropping the bulb, eyes widening.
- The bulb tumbles in slow motion; it catches it just in time.
- A puff of steam escapes its chest — relief and pride.
- Robot says quietly: "Almost lost it… but I got it!"
```

**B. 2D cartoon, action tied to narration (stickman-video-director `examples.md`)**
```text
[0–3s] (VO: "When you hit a wall, you assume you lack talent."): Zeke takes an ambitious leap upward from the grid floor, but hits his head with a comedic "BONK!" against an invisible, transparent glass ceiling overhead. [...]
[3–7s] (VO: "But skill is rarely the ceiling."): Zeke lands on his feet, rubs his red beanie thoughtfully, and reaches his black stick hand upward to touch the glass. He discovers the glass has no frame or pillars—it simply floats in mid-air.
```

**C. Image-to-video (Sora cookbook, prompts used with a starting image)**
```text
The fridge door opens. A cute, chubby purple monster comes out of it.
She turns around and smiles, then slowly walks out of the frame.
```
Weak vs strong, same guide: `Actor walks across the room.` becomes `Actor takes four steps to the window, pauses, and pulls the curtain in the final second.`

**D. Clear action chain (Seedance 2.0 official prompt, via Square-Zero)**
```text
Single continuous cinematic shot, no music. From outside the glass window, the dim camera slowly pushes inward into a pizza shop. A bearded white male employee is baking pizza. He removes the pizza from the oven with a metal tray, places it into a red takeaway box, closes the lid, then hands it to a customer with a warm smile. Final shot: over-the-shoulder perspective.
```

**E. Event needs time, place, result (Rylaispirit section 8.10)**
```text
at 4s the second door on the left swings fully open, revealing pitch darkness
```

## What to do next (suggested)

1. Rewrite our reaper prompts as beats: setup, trigger, action, reaction, end state, using A and B as templates.
2. Run each action through the drama-skills test: can someone mime it? Replace "realises" with a visible act.
3. Write one frozen character-anchor paragraph for the chibi reaper; paste it in every clip (stickman rule).
4. Budget 5-10 generations per kept clip.
