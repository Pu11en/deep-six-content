# Viral prompt patterns (2026-10-16)

**Takeaway:** Winning prompts give viewers one clear want, one obstacle, and a physical payoff. They write it as timed beats, and each beat is one visible action with a reaction. Our clips failed because the action had no clear cause and effect.

Method: read the Opus 5.5 repo, pulled real view counts from X for 689 of its 703 posts, then read the top Seedance, Veo and Grok prompt collections. Views are from the X post, so they also reflect each author's audience. They do not measure prompt quality alone.

## What winning prompts have in common

- **One-sentence premise a stranger gets instantly.** "A cat burglar sneaks a salmon, a dog chases, the dog wrecks the kitchen." If you cannot say it in one line, the clip will be confusing.
- **A want, an obstacle, a payoff.** Sneak, get caught, escape. Try, fail, scold, deadpan stare.
- **Timed beats, 1.5 to 3 seconds each.** Every beat is one action a viewer can see: "He hops onto the drone and slaps the propeller."
- **Each beat has a reaction.** Pupils dilate, tail goes rigid, a hat lands on the dog's head. Reactions make the joke readable.
- **A button ending.** A deadpan hold, a salute, a loop back to frame one, or "Cut to black".
- **Character defined once, with props.** "Chubby orange tabby, tiny black turtleneck, ski mask on forehead." Then only call it "the cat".
- **Style named at the top, repeated at the bottom.** "2D hand-drawn, slapstick" or "Pixar quality".
- **Camera is plain.** Wide, medium, close-up, whip-pan, locked wide. No fancy moves.
- **Bans list.** Strong prompts say what must not happen (no cuts, no particle bursts, no template look).
- **Sound that matches the action**, written as a line: ticks, clank, alarm, laugh.
- **Short prompts also win** when the premise is a clear emotional arc (see Luffy, 7.2M views).

## Part A: awesome-opus5-5-videos

Repo: https://github.com/yihui-dev/awesome-opus5-5-videos. 5,463 stars, MIT, last push 2026-10-13. The data file has no view counts, so I fetched them from X.

Honest limit: 703 entries split into 369 motion graphics, 117 3D, 116 explainers, 101 interactive. Almost none are character comedy. They are mostly UI, product launches and data explainers, so use them for structure and pacing only.

What the top ones do:
- **Beat grid.** "120 BPM, 54 beats, something happens on every beat." Nothing sits still.
- **Chain, no cuts.** "Every scene is made out of the previous one: nothing fades, blurs or cuts." Objects morph into the next scene, so the viewer always follows cause and effect.
- **Loops.** "The last frame is the first frame." The ending hands back to the start.
- **Story as arrows.** One line of cause-then-effect, e.g. "a dot grid ripples and resolves into a pixel mascot -> a square tunnel flies at the camera".
- **Character as a state machine.** Idle, charge, cast, recover. Each state names what the body does.
- **Self-check.** "Render one frame per beat before the full render. Fix anything off the grid, cramped or hard to read."
- **Short beats the long ones.** The top 20M-view entry is a brief with a clear emotional job (visualize song lyrics). The 3.78M entry is two sentences.

### Five quotes

**1. Portland bus (3.78M views, 20.6K likes)** https://x.com/milos_gis/status/2103751211040317580
> Create a video of Portland, OR's bus service on a random Tuesday! Showcase Portland's different neighborhoods at a high level and then zoom in on specific routes in each quadrant (absorbing North Portland into NE and South Portland into SW for brevity). Use a light theme. Slow down the speed of the bus animation when zoomed in, without increasing the total duration too much so the viewer can appreciate some of the landscape and streets it travels through in a given loop.

Lesson: wide view, then zoom to detail, with a pacing rule (slow down when zoomed in).

**2. Pixel wizard casting a spell (458K views, 2.6K likes)** https://x.com/majidmanzarpour/status/2102476258948927543 (condensed)
> Looping state machine: IDLE (2-frame bob, beard sway) -> CHARGE (staff raises, gem flickers, sparks spiral inward) -> CAST (bright burst, projectile fires across the scene, 1-2 pixel screen shake) -> RECOVER (settle back). ... Minimal background... Character silhouette must read clearly.

Lesson: the best character prompt in the set. Anticipation, action, recovery. The silhouette must read.

**3. One-shape UI morph (1.17M views, 8.4K likes)** https://x.com/twoclipping/status/2103273003555402193 (condensed)
> One shape, never cut: every state is the same element morphing... A cursor drives every change with real clicks and drags... The last frame is the first frame, so it loops. Banned: bouncy easing, particle bursts, glows, dead time... 120 BPM, 7 bars, something happens on every beat. Button -> loader -> check -> dynamic island -> music player ... -> toast -> back to the button.

Lesson: one continuous thing that changes, a banned list, and arrows for the order.

**4. "Claude Pop" music video (20.1M views, 16.3K likes)** https://x.com/anabology/status/2103534482930491441 (condensed from a very long brief)
> Think and feel very deeply about what is the best way to visually represent all of the lyrics on screen... a pop protagonist that represents you... a few backup dancers and some supporting characters... I wouldn't fit too heavily to Pixar. I think it's kind of slop... Think critically about what is relevant here and what would be fun, and also perform well on Twitter as far as an aesthetic.

Lesson: it names a protagonist and supporting cast, ties every scene to the lyrics, and rejects the generic look. Reach also came from a huge audience.

**5. Stickman vs. the battery drain (only 280 views, but the best story template found)** https://x.com/byaiden_vu/status/2104846080722755862
> A stickman lives inside a phone battery icon and fights against power loss. The red battery-drain line is the villain... he's asleep on top of the fully charged battery bars and dodges the red drain line at the last moment... on each cycle he survives it a different way: he jumps over the descending red level, rides the drain line like a rodeo bull as it drops, and ducks flat inside one battery bar... Finally he pries the charging bolt symbol off the center of the battery and jams the drain line with it... he takes a nap... until the low-battery alarm goes off... the battery instantly rewinds back to full, and he ends up asleep on top again, so it loops.

Lesson: hero, villain, three escalating tries, a clever solution, a loop. Low views, so treat as a structure model, not proof.

## Part B: public prompt collections

| Repo | Stars | License | Last push | Notes |
|---|---|---|---|---|
| https://github.com/ZeroLu/awesome-seedance | 2,720 | MIT | 2026-10-16 | Seedance 2.0 prompts from X, with source links |
| https://github.com/songguoxs/awesome-video-prompts | 589 | none stated | 2025-10-18 | Veo 3/3.1, Kling, Hailuo; many JSON prompts |
| https://github.com/renoise-ai/awesome-seedance-prompts | 8 | CC-BY-4.0 | 2026-10-16 | Large Seedance set, tagged (Meme & Comedy, Hand-drawn, Anime 2D) |
| https://github.com/YouMind-OpenLab/awesome-grok-imagine-prompts | 56 | other | 2026-10-16 | Grok Imagine; many are one-liners |
| https://github.com/ZeroLu/awesome-seedance-2.5 | 138 | MIT | 2026-10-16 | Seedance 2.5 community cases |

No Sora or Kling collection worth using (Sora lists are old; the Kling one has 0 stars).

Shared structure:
- **Timestamp blocks.** `[0s-1.5s]`, `0-5s:`, `Shot 01 (0:00-0:02)`. Total length stated up front (15 s is common).
- **Header line** with style and character, then beats, then a closing style tag line.
- **JSON prompts (Veo style)** use keys like `shot`, `subject`, `scene`, `cinematography`, `audio`, `dialogue`. Good for control, but the funniest ones are plain prose with beats.
- **Dialogue in quotes** with who says it.
- **Audio line** (BGM, effects).
- **Comedy tags:** "slapstick", "deadpan", "chaotic comedy".

Caveat: these are video-model prompts, not code, but the beat writing carries over. The renoise tags are the repo's own. Views come from X.

### Five quotes (character action)

**1. Cat burglar (24K views)** https://x.com/Dheepanratnam/status/2037197120957010336 (Seedance, condensed)
> A chubby orange tabby cat with enormous green eyes, wearing a tiny black turtleneck and a miniature ski mask pushed up on his forehead, sneaks across a moonlit kitchen counter toward an unguarded salmon fillet... High budget 3D animation, Pixar quality lighting and fur rendering.
> [11s-13s] The chairs collapse. The dog crashes through a tower of pots and pans... A colander lands on the dog's head like a helmet. He sits in the wreckage, tail still wagging.

**2. Pigeon dogfight (44K views)** https://x.com/Dheepanratnam/status/2037229062624620939 (condensed)
> [3s-5s] The seagull dive bombs from above, screeching. The pigeon barrel rolls the drone to dodge. His cheeks flap in the G forces. A feather pops off. He watches it float away, annoyed.
> [13s-15s] ...The seagull limps past in the background, missing feathers. The pigeon doesn't even look. Cut to black.

**3. Girl vs. giant wolf, 2D painterly (34K views)** https://x.com/GlitterPixely/status/2071288855462858976 (condensed)
> 3.2-4.2: The girl reaches higher, overconfident, one knee sliding into the fur. She pauses proudly for half a beat.
> 5.2-6.4: She scrambles to recover: arms windmill, one leg kicks, hair flips forward. She slides down the wolf's cheek instead of teleporting.
> 7.4-8.4: Hold the upside-down pose for comedy. The wolf blinks once, unimpressed.
> 14.0-15.0: Final deadpan hold. The girl freezes mid-rant beside the huge bored face.

Best match for us: a small character acts out try, fail, anger, deadpan, each second named.

**4. Coatimundi donut heist, 2D hand-drawn (48K views)** https://x.com/AmControo/status/2077389944016801958
> Style: 2D hand-drawn animation, vibrant and clean color palette, fluid comedic character design, expressive motion, slapstick atmosphere.
> 0-5s: A coatimundi crawls from under a table in a bustling donut shop and sneaks through the legs of patrons toward the counter.
> 5-10s: The coatimundi leaps onto the counter, grabs a large pink-frosted donut, and makes eye contact with a surprised police officer who drops his own pastry.
> 10-15s: The coatimundi weaves through the crowded shop toward the exit while the officer clumsily stumbles and crashes into a table.

Only three beats and still clear: sneak, steal, escape.

**5. Mirror glitch (212K views) and Luffy one-liner (7.2M views)** https://x.com/johnAGI168/status/2020788951678607813 and https://x.com/KingBootoshi/status/2021349878232907790
> [00:06-00:11] Shot 2: BUG appears (The Glitch)... the "reflection" in the mirror doesn't move! ... staying for a full 2 seconds, before suddenly panicking and "fast-forwarding" to catch up... [00:11-00:15] Shot 3: Comedic callback (The Punchline)... The frame freezes on the protagonist's confused face.
> Luffy coding on a Macbook on the Thousand Sunny, RAGING, then throwing it overboard.

The mirror prompt labels its own beats: Normalcy, Glitch, Punchline. The Luffy line works because it has a built-in escalation: coding, rage, throw.

## For Deep Six

Write the video as one line first ("mascot wants X, pest does Y, mascot fixes it by Z"). Then 5 to 8 beats of 1.5 to 3 seconds, each with one visible action and one reaction, labelled setup, escalation, reversal, button. Define the mascot once, add a bans line, end on a deadpan hold or a loop.

Sources: the repos and X posts linked above; fxtwitter API for views (read-only). Nothing installed or generated.
