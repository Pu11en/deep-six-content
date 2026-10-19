# Deep Six board

Newest on top.

---

### 2026-10-19 11:31 · Your whiteboard — research, choices, production

# Deep Six shorts — working flow

**Two research feeds supply five hooks. You choose one, then get five full scripts using that same hook and factual source.** No automation is running yet.

## 1. Research on a schedule

- **Pest resources:** articles with useful homeowner lessons. Start with [Texas A&M](https://citybugs.tamu.edu/2018/06/14/when-ants-invade/), [NPIC](https://npic.orst.edu/pest/ant.html), and [UC IPM](https://ipm.ucanr.edu/home-and-landscape/ants/). [Resource library](01-content/pest-resource-library.md).
- **Social hooks:** real educational videos, their opening words and visuals, and the pattern worth learning. Keep original links and observed evidence.

Articles supply the facts. Social research supplies ideas for how to open and explain them. Research frequency is still open.

## 2. Choose the writing

1. Writing harness → **five hooks**.
2. You choose one. A second choice waits for a later video. **Skip → another five.**
3. Same writing harness → **five full narrations**, each repeating the exact chosen hook and using its same resource.
4. You choose one. **Skip → another five with that same hook and source.**

Requested writer: Sonnet; exact model/version still needs setup. [Proposed writing instructions](01-content/writing-harness-prompts.md).

## 3. After the chosen narration — proposed

**Scene plan → voiceover and measured timing → code cartoon animation → captions and sound → reusable branded outro → your final review → export.**

Plan the characters’ actions around the lesson. Time the animation to the actual voiceover. Make the outro once, approve it, and reuse it; AI image/video generation can be used for that asset. Every produced preview and final video stays **9:16 in Deep Six colors**.

## Hook-research repos

- [Instagram Viral Reels Research](https://github.com/w-avw/instagram-viral-reels-research-claude-skill): finds candidate reels and combines transcripts with visual frames. Needs Instagram access/setup; its fixed view thresholds would need adapting.
- [Hookmaxxing](https://github.com/yerdaulet-damir/hookmaxxing): useful rules for studying the opening and checking whether a hook’s promise has evidence. It does not discover videos by itself.

[Inspected files and limits](01-content/research/hook-research-repos-2026-10-19.md). Neither repo has been installed or tested here.

## Decisions and records

Keep sources, prompts, chosen work and brief feedback. **No rejected narration archives.** The old script files and board copies have been deleted; earlier Git history still exists.

Open decision: should five hooks cover five separate lessons/sources, or five openings for one article? This affects saving a second hook for the next video.

[Full design log and step cards](01-content/video-system-design.md) · [Source-use log](01-content/source-log.md)


### 2026-10-16 23:18 · Cartoon animation — closer matches

# Cartoons closer to our Deep Six videos

**Required method: AI writes animation code, such as JavaScript or TypeScript. Every Deep Six video must be 9:16 vertical.**

The ant colony below has published JavaScript drawing and animation code. The two vertical cartoons match the look, but their exact implementation is unverified. For ours, the action would show an ant reaching a house while the narration explains the homeowner’s next step.

## 1. Animals sneaking snacks — closest character style

[Watch the cartoon](https://x.com/jackfriks/status/2103525576912855363)

A pig, pug, and duck sneak snacks after the cat goes to bed. Expressive animal characters, rooms, props, and a visual joke.

**35 seconds · 9:16 · September 25, 2026.** The creator credits Opus 5.5; JavaScript/TypeScript implementation is unverified. This is comedy; we would borrow the character acting and scene style for our lesson.

## 2. Mailbox love notes — simple cartoon story

[Watch the cartoon](https://x.com/jackfriks/status/2103132260589338762)

Cute animals, painted scenery, a mailbox, and large captions. A useful reference for one character doing something easy to follow.

**20 seconds · 9:16 · September 24, 2026.** The creator says Opus 5.5 animated supplied app artwork. The exact animation implementation is unverified. This is an app promo; the artwork was already provided.

## Animated ant colony — confirmed JavaScript example; widescreen reference

[Watch the ant animation](https://x.com/hanifproduktif/status/2102742924148830211) · [Published animation code](https://github.com/buildwithhanif/claude-animation-skill/tree/main/examples/ant-colony)

Illustrated ants cut and carry leaves, then the scene follows them underground. The creator published the JavaScript that draws and animates them.

**32 seconds · September 23, 2026. This reference is 16:9 widescreen.** We would need to rebuild the scene layout for **9:16**, which remains required for every Deep Six video.

This is a leafcutter-ant showcase, so it is a visual reference only. Our pest advice still comes from our logged educational source.


### 2026-10-16 22:38 · Educational AI animation — watch links

# Educational AI animation styles

The finished examples we found, with the photon video first.

**All Deep Six videos must be 9:16 vertical.**

## Journey of a Photon — your pick

Playful character, visual jokes, and a journey through space.

[Watch the video](https://x.com/AstroTheWizard/status/2103629247751618782) · [Read the animation prompt](https://github.com/yihui-dev/awesome-opus5-5-videos/blob/main/prompts/astrothewizard-618782.md) · [Alternative watch page](https://skillry.dev/ai-videos/opus-5-5/astrothewizard-618782)

## Chemistry — colorful moving diagrams

Atoms, molecules, and mixtures explained with simple shapes and labels.

[Watch the video and read how it was made](https://www.reddit.com/r/ClaudeAI/comments/1wr268d/a_different_kind_of_opus_55_video_prompt/)

## Recursion — cartoons and visual jokes

One concept explained through several playful animation styles.

[Watch Ethan Mollick’s video](https://x.com/emollick/status/2103688362960019567)

## A tree as an ecosystem — illustrated cutaway

A tree, animals, fungi, and roots shown as a connected environment.

[Watch hunzai’s video](https://x.com/hunzai/status/2103904436141842605)

## Eye evolution — animated science diagrams

Cross-sections, light rays, and labels explain a biological process.

[Watch Çağrı Mert Bakırcı’s video](https://x.com/cagrimbakirci/status/2104011756397842869)

## The Bitter Lesson — educational music video

A lesson told through a song and animated visuals.

[Watch on YouTube](https://www.youtube.com/watch?v=OAwat51S_Sk) · [Creator’s production notes](https://www.oneusefulthing.org/p/the-dot-and-the-swarm)

## How Laya Works — technical explainer

A longer lesson using mathematical animation and narration.

[Watch on YouTube](https://www.youtube.com/watch?v=obR9DYQq3v4) · [Creator’s production notes](https://www.hijoseromero.com/posts/opus-55-made-three-ai-learning-videos)

## More examples and prompts

[Browse the Opus animation collection](https://github.com/yihui-dev/awesome-opus5-5-videos)


### 2026-10-16 20:51 · Trial prompt for natural narration

**Deep Six narration prompt — trial**

Write a short, useful voiceover for Deep Six Pest Control. Your listener is one homeowner dealing with a pest problem.

Use the selected hook and the supplied factual source. If a voice example has been approved, study its rhythm, transitions, and humor. Write fresh wording; get every pest claim from the factual source.

Sound like someone standing beside the homeowner, pointing out what's happening. Use everyday words, contractions, and a mix of short and longer sentences. Let each thought lead into the next.

Keep the selected hook exactly. Develop one useful observation: what's happening, why it matters, and what the homeowner can do. Spend the words on explaining that connection. Stop when the useful point is complete.

Name things the homeowner can see. Replace vague phrases with the actual place, object, or action. Keep the spoken voice warm and direct. Avoid a string of clipped instructions, forced jokes, canned suspense, and a sales ending.

Keep the source's uncertainty and limits. Use only supported facts. Personal experiences and customer stories require real supplied details.

Before returning the draft, check the wording as speech. Rewrite anything that sounds like a brochure, report, or checklist. Remove repeated ideas and lines added only to fill time.

Apply the supplied editing notes to the actual wording. Treat approved examples as the voice target; treat rejected drafts as examples of what needs to change.

Return the narration as short paragraphs. Put the source credit separately, outside the spoken script.


### 2026-10-16 20:11 · More ant hooks — 9 through 18

**More ant hooks**

9. Why do the ants keep showing up in the exact same spot?

10. You cleaned up the food. Did you check for water?

11. That line of ants is leaving you clues.

12. A clean kitchen can still have an ant problem.

13. Before you treat the whole house, find out where the ants are nesting.

14. That branch touching your house? Ants can use it as a bridge.

15. Rain outside. Ants inside. There may be a connection.

16. If the ants ignore your bait, adding more may not solve it.

17. You’ve found the ants. Now find what they’re after.

18. The gap where ants get in isn’t necessarily where they live.

---

Same source: [Managing Household Ant Pests — Texas A&M](https://extensionentomology.tamu.edu/wp-content/uploads/sites/6/2021/03/managing-household-ants.pdf).


### 2026-10-16 20:09 · Ant video — pick the hook first

**Ant video — hook options**

1. You cleaned the kitchen. The ants came back. Now what?

2. Before you wipe up that ant trail, see where it’s going.

3. What if the ants aren’t coming from outside?

4. Killing the ants on your counter might leave their nest untouched.

5. No crumbs. No spills. So why are there ants in your bathroom?

6. Ants walking right past your bait? You might be offering the wrong food.

7. Sometimes an ant problem starts with a plumbing problem.

8. Before you buy another ant treatment, find out which ant you have.

---

Same source: [Managing Household Ant Pests — Texas A&M](https://extensionentomology.tamu.edu/wp-content/uploads/sites/6/2021/03/managing-household-ants.pdf).


### 2026-10-16 15:16 · Scorpion fun fact, AI image, 3 cents

![Scorpion fun fact, AI image, 3 cents](01-content/experiments/2026-10-16-fun-fact-remix/scorpion-uv.png)


### 2026-10-16 14:46 · Reaper drawn in code (right) vs original

![Reaper drawn in code (right) vs original](01-content/brand/code-mascot/compare.png)


### 2026-10-16 14:46 · Original Deep Six post

![Original Deep Six post](01-content/brand/fun-fact-friday-spider.png)
