# Educational hook repos and a "hooks we like" rubric

**Continuation status:** this draft was saved before its helper hit the subscription limit. On October 19, Codex rechecked the pinned marketingskills hook-system and evaluation files and the viral-hooks checklist. The findings below are candidate methods, not a validated hook system. Timing/word-count rules are proposals; the current [writing flow](../video-workflow.md) uses Drew's later hooks-only display, Saturday-night example refresh and approved-script bank.

**No repo is proven for educational hooks. The best feed for the writer is Corey Haines's well-used marketingskills hook system, plus our own short rubric that rests on curiosity and misconception research and on YouTube and Facebook rules against clickbait.**

Researched 19 Oct 2026. Read files only: no installs, no repo code run, no paid calls, no logins. Star counts and dates are from the GitHub API on 19 Oct.

## Short answer to Drew's question

- Nothing found has been tested on educational or pest hooks. Not one repo shows hook-versus-hook results.
- Most-used hook-related repo: [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills), 55,508 stars, MIT. Also [featured by the GitHub Awesome channel](https://youtu.be/Mo5NmLqArFk?t=592).
- Stars are not proof. They show use, not that the hooks work. Compare: [hookmaxxing](https://github.com/yerdaulet-damir/hookmaxxing) (already reviewed) has 5 stars. Its value is its study procedure, not its popularity.
- The best evidence for educational hooks is research, not repos (see "Evidence" below).

## Picks

### 1. coreyhaines31/marketingskills (use two files)

[Repo](https://github.com/coreyhaines31/marketingskills) · MIT · 55,508 stars, 8,217 forks · last push 2026-10-15 · about 1,166 commits · author is a working marketer ([profile](https://github.com/coreyhaines31)) · inspected `365b412152b9542499ca1439426f7fc3cc92bb65`.

Files read:
- [`skills/ad-creative/references/hook-system.md`](https://github.com/coreyhaines31/marketingskills/blob/365b412152b9542499ca1439426f7fc3cc92bb65/skills/ad-creative/references/hook-system.md): a hook has three parts (what we see, what is said, on-screen text) that must not repeat each other. Steps: segment, motivation, format, hook. A table of 13 opening moves with a "watch out" for each. An "on-ramp rule": the next beat must continue the hook's promise. Grounding rules: every hook cites its source, no invented claims.
- [`skills/social/references/short-form-video.md`](https://github.com/coreyhaines31/marketingskills/blob/365b412152b9542499ca1439426f7fc3cc92bb65/skills/social/references/short-form-video.md): a hook library. It labels the contrast group "best for educational content and decisions" (a claim with no data).

Evidence it is good: heavy use and active upkeep. The repo's [evals](https://github.com/coreyhaines31/marketingskills/blob/365b412152b9542499ca1439426f7fc3cc92bb65/skills/social/evals/evals.json) check that the skill follows its own steps, not that hooks perform. Claims only on performance.

How it plugs into Stage 1 (five hooks):
- **Inputs:** one lesson card per hook (source ID, supported facts, the homeowner's worry in plain words, what is visible).
- **Writer uses:** the lesson-to-hook steps (lesson, worry, cartoon scene, hook); the opening-moves table, one different move per hook; the picture-and-line-written-separately idea; the on-ramp rule; the grounding rules.
- **We ignore:** paid-ad funnel and click metrics, competitor naming, posting times, calls to action, SaaS examples, and the "secret", "hack" and "unpopular opinion" hooks.

### 2. Jakeschincariol ig-reel hook cards (cards only, not the scorer)

[Instagram pack](https://github.com/Jakeschincariol/instagram-agent-skill) · MIT · 1,949 stars · pushed 2026-09-13 · 2 commits · inspected `d03c56bb598be770c60b201f94237e5d1a4268a6`. Sister [YouTube pack](https://github.com/Jakeschincariol/youtube-agent-skill) (1,855 stars, 1 commit, `a2feb2104981a375ffd4f87ee04f4f5344ac43c6`). The author has [about 20 similar packs](https://github.com/Jakeschincariol?tab=repositories); several reached thousands of stars within weeks.

File read: [`skills/ig-reel/hooks.json`](https://github.com/Jakeschincariol/instagram-agent-skill/blob/d03c56bb598be770c60b201f94237e5d1a4268a6/skills/ig-reel/hooks.json), 26 cards. Each has a template, example, on-screen line, "best for", and a `trap` (how it gets ruined). Example trap: "Wrong Way, Right Way" fails without "it is not your fault", because "you are doing it wrong" alone makes people leave.

Evidence it is good: popularity only. The README's [fine print](https://github.com/Jakeschincariol/youtube-agent-skill/blob/a2feb2104981a375ffd4f87ee04f4f5344ac43c6/README.md) says its scorer was calibrated on 74 hooks and "barely" separates one creator's hits from misses.

How it plugs in:
- **Writer uses:** 6 to 8 cards that fit homeowners (Wrong Way/Right Way, Verbatim Question, If This Then Watch, Cold Open Demo, Statistic, Permission, Nobody Tells You), plus each card's `trap` line as a check.
- **We ignore:** [`hookscore.py`](https://github.com/Jakeschincariol/youtube-agent-skill/blob/a2feb2104981a375ffd4f87ee04f4f5344ac43c6/skills/yt-script/hookscore.py) as a picker. It is word-pattern matching that rewards "you" early and words like die, dead, lose, risk and cost, which pushes toward fear. Also ignore the creator-voice cards (I Tried It, Receipt, Insider, Flop Record, Cost Confession), Deadline and Superlative.

### 3. artemnovitckii/content-skills, viral-hooks (as a checklist)

[Repo](https://github.com/artemnovitckii/content-skills) · MIT · 107 stars · pushed 2026-06-20 · 2 commits · inspected `1c6e909c975b15d80f6ffcb0e2b60904b7da6656`. File: [`viral-hooks/SKILL.md`](https://github.com/artemnovitckii/content-skills/blob/1c6e909c975b15d80f6ffcb0e2b60904b7da6656/viral-hooks/SKILL.md).

Four ways a hook fails: Delay (topic arrives late), Confusion (needs a re-read), Irrelevance (about the creator, not the viewer), Disinterest (no gap between what the viewer believes and what you say). Small and clear. Evidence is the author's claims only.
- **Writer uses:** the four as a self-check after drafting. Plain words, short sentences, aimed at the homeowner.
- **We ignore:** voice-DNA, LinkedIn/newsletter rows, "viral" framing.

## Seen, not used

- [shixinzhang/tiktok-viral-hooks](https://github.com/shixinzhang/tiktok-viral-hooks): 36 stars, license not stated. A library of other creators' videos with transcripts and a takedown file. Skip: it invites copying.
- [sergebulaev/tiktok-skills](https://github.com/sergebulaev/tiktok-skills): 78 stars. Ten hook formulas, but tied to Apify scraping and publishing code. More plumbing than we need.
- [Hook-Brain](https://github.com/subkap88-coder/Hook-Brain) (36 stars, fMRI-model "brain scores"): predictive claims, no evidence they match audiences. Skip.
- Catalog hits not opened: [charlie947/social-media-skills](https://github.com/charlie947/social-media-skills), [blader/humanizer](https://github.com/blader/humanizer) (may help later with stiff narration, not hooks). About 25 all-git queries; most "hook" hits were software hooks.
- Already reviewed and still the "study real videos" step: viral-outliers and hookmaxxing ([note](hook-research-repos-2026-10-19.md)). The picks above are the "write" step.

## Evidence on what opens educational shorts well

Honest summary: platform guidance is short and generic; research on curiosity and misconceptions is solid but not about shorts or pests.

- Platforms say the first seconds matter, nothing more exact. YouTube: ["Capture attention in the first few seconds"](https://blog.youtube/creator-and-artist-stories/your-guide-to-getting-started-with-youtube-shorts/). Its [hook tips](https://blog.youtube/creator-and-artist-stories/four-tips-to-hook-your-viewers-on/): start with a question, tell them what they will see, cold open. YouTube's metric ["Stayed to watch"](https://support.google.com/youtube/answer/9314355) counts viewers who stay "past the initial seconds". TikTok's [ads guide](https://ads.tiktok.com/resources/help/article/creative-best-practices) says hook in the first 6 seconds and state the proposition in the first 3. That page is for ads.
- Curiosity needs a specific question the person is aware of ([Golman and Loewenstein](https://doi.org/10.1037/dec0000068)). Curiosity improved memory for surprising answers ([Kang et al. 2009](https://doi.org/10.1111/j.1467-9280.2009.02402.x)). Making people guess first raised curiosity ([npj Science of Learning 2019](https://doi.org/10.1038/s41539-019-0056-y)).
- Videos that expose common misconceptions help learning ([Muller and Sharma](https://openjournals.library.sydney.edu.au/IISME/article/view/6345), physics, 1,000+ students).
- Clickbait does not reliably win. In two studies it [did not create more curiosity](https://doi.org/10.1145/3411764.3445753) than plain headlines; plain ones read as more credible. Prior studies are mixed.
- Rules: YouTube bans ["maliciously misleading titles... that do not deliver what was promised"](https://support.google.com/youtube/answer/2801973). Facebook [reduces headlines](https://about.fb.com/news/2017/05/news-feed-fyi-new-updates-to-reduce-clickbait-headlines/) that withhold information or exaggerate.
- Science TikTok: in 1,025 videos, humor, remixing, and social storytelling formats predicted engagement ([Bunquin 2025, dissertation](https://scholarsbank.uoregon.edu/items/482e9c19-7637-43a0-8fdd-cb88e810fa91/full)). In an experiment, casual, funny science clips were rated more curiosity-sparking ([Cacciatore, press summary](https://news.uga.edu/?p=114414)).
- Interesting but off-topic details hurt recall ([Harp and Mayer 1998](https://doi.org/10.1037/0022-0663.90.3.414); abstract seen via search summary, paper not opened).

## Draft rubric: hooks we like (homeowner pest education)

Tags: **[E]** has evidence above. **[P]** our proposal, untested.

### Types that fit (use a different type for each of the five)

1. **Surprising true fact.** One specific fact from the lesson card, plainly stated. [E] curiosity needs a specific question; surprising answers stick (Kang). State where it comes from in the metadata.
2. **Common mistake, without blame.** "Most people {do X}. Here is why it {doesn't work}." Only if the source names the mistake and the reason. [E] misconception research (Muller). [P] add the "not your fault" tone from the Jake card.
3. **Visible problem.** Start from what the homeowner already sees (a trail, a mound), then what it means. [P]
4. **A question the homeowner already has.** Use real wording from the source or its FAQ. [E] YouTube advises starting with a question; guessing first raises curiosity.
5. **Believe versus source says.** Name the common belief, then the source's answer. [E-weak] marketingskills and viral-hooks claim this works for education; no data.

### Avoid

- **Clickbait the source cannot back:** a hook that withholds the point or exaggerates it. [E] YouTube policy, Facebook, CHI 2021 study.
- **Fake urgency:** no deadlines, "before it's too late", "act now". [P] Jake's own Deadline card calls it the fastest way to lose trust.
- **Fear-mongering:** no danger words ("deadly", "destroy") beyond what the source says in its own terms. [P]
- **Copying creators:** no borrowed lines, no "I tried this" persona, no invented stories or numbers. [P] marketingskills says take vocabulary, never a creator's creative.
- **"Best", "secret", "nobody tells you"** unless the source supports it. [P]
- **A joke or shock that is not the lesson.** Humor tied to the lesson is fine. [E-secondary] Harp and Mayer; Bunquin and Cacciatore favor humor.

### Checks (each hook must pass all)

1. **Promise is in the source.** The payoff exists in the lesson card, with fact IDs. [P] YouTube's rule is "deliver what was promised".
2. **Payoff timing.** Topic named in the first 3 seconds of speech; first useful answer by about second 10; the full promise paid before the halfway point. [P] anchored on TikTok's 3 and 6 seconds and the Jake "halfway" note.
3. **Spoken length.** 8 to 15 words, at most 6 seconds read aloud at a normal pace. Read it aloud once. [P]
4. **Cartoon test.** The first picture is one visible action you can say in one sentence. [P] our [viral prompt note](viral-prompt-patterns-2026-10-16.md) found one clear action with a reaction works best.
5. **Plain words, aimed at the homeowner.** Short sentences, "you", no jargon, no re-read. [P] viral-hooks four failures.
6. **Five different types.** At least four of the five hooks use different types above. [P] marketingskills says varied cells beat rewordings.
7. **Original.** Studied videos are for structure only; no copied wording. [P] same as the writing harness.

## Limits

- Nothing here proves a hook works for homeowners. Only our own posts can.
- The research is on MOOCs ([Guo et al.](https://doi.org/10.1145/2556325.2566239) is similar: general video, not shorts), physics, and news headlines. None is on pests or 9:16 cartoons.
- TikTok's timing page is for ads, and its 3-second and 6-second numbers differ. No official YouTube or TikTok page gives a hook length.
- Popular repos may be popular because of promotion. The Jake packs are one- or two-commit releases.
- Test plan: after posting, note the hook type and YouTube's "Stayed to watch" for each Short. Compare only within our own channel, and across at least a few posts per type.
