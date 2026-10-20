**First try at the hook: 8.8 seconds, 8 shots, a new action every quarter to half second.**

![Hook preview](board-previews/hook-v1-1792450977.gif)

[Play it with sound](01-content/animation/episodes/D6-6c917b49743b/hook/renders/hook-v1.mp4)

**Every phrase gets its own picture, timed to the word:**

- **"A fire ant"**: a big worker walks across the screen.
- **"colony"**: the camera pulls back to dozens of ants.
- **"doesn't always have"**: a mound pops up, then squashes flat.
- **"a mound you can see"**: a dashed outline marks it; a magnifier shows ants still underground.
- **"In a drought"**: the sun drops in and the grass turns straw.
- **"the ground itself"**: cracks race across dry soil.
- **"can be too hard"**: the ant bites the ground. Clank.
- **"and dry"**: dust blows and the last drop dries up.
- **"for them to build one"**: a dashed mound appears and falls apart. The colony is still below.

![One still per beat](01-content/animation/episodes/D6-6c917b49743b/hook/renders/hook-v1-beats.png)

**How the agent makes it**

1. Measure when each word is said.
2. Director prompt: one picture per phrase, landing on its word.
3. Animator prompt: turn those shots into drawing code.
4. Check a still of every beat before you see it.
