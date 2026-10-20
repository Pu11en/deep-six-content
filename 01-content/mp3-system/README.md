# Deep Six: start → approved MP3

**Choose the source, choose the hook, choose the complete narration, then approve the recorded voice.** This is the working design for that whole process. Video and the promotional outro are separate later tasks.

Another active session owns **approved MP3 through finished video**, excluding the outro. This session stops at the approved audio package.

[Open the flow diagram](http://localhost:3003/boards/0d05ffd0809f0bbe1220a047)

**Crawler update:** Drew confirmed it is ready. The current diagram now separates using approved sources from researching new ones. [Exact request, source criteria and research timing](source-research.md) · [repeatable crawler procedure](crawler-flow.md) · [ASCII whiteboard](whiteboard.md).

## The flow

1. **Start or resume.** Remember saved choices and finish the current step. For the next trial, run fresh crawler research and leave the saved queue untouched. Later runs can explicitly select a queued source. On demand works today; cron comes later.
2. **When new choices are needed: send a crawler request.** Specify pest, audience, lesson criteria, source history, feedback and desired output. Gather original material, check evidence, and show five short source previews. Queue stocking is separate from making an episode.
3. **Save your source choices.** Keep every source you like. Use the one you put first. With at least three liked sources stocked for a pest, research the next pest.
4. **Choose one of five hooks.** All five use the chosen main source. Check that it can support the promised lesson.
5. **Crawler: research supporting science.** Fill the selected hook’s specific gaps. Keep the main lesson and hook fixed. Reuse adequate evidence for wording-only retries.
6. **Choose one of five narrations.** Each shows the exact same hook plus the full script. Teach useful, less-obvious facts in natural speech. Keep source credits outside the words spoken.
7. **Prepare the voice.** Keep the approved wording. Rotate Tyler → Chris → Liam. Keep the same voice when revising an episode. Use short hook auditions when a voice or delivery needs testing.
8. **Generate the authorized MP3.** Check the request, existing files and available credits first. New spending needs permission. Never silently repeat an uncertain paid request.
9. **Listen and approve.** Make the file easy to find. Fix pronunciation, tone or content through the right retry path. Save approval against that exact MP3.

At every choice, you can pick, reject, give a reason, or stop. Silence never means approval.

## What already works

The source/hook/narration controller works. Supporting research, saved feedback, source rotation and model fallback exist. A separate audio tool generates MP3s and remembers voice assignments. **This is a guided system with human review gates.** Crawler request/import checkpoints are connected; the session agent performs crawler actions. Audio now enforces bounded authorization, canonical words, duplicate-request protection and explicit listening decisions.

Your first episode already passed every human choice: source 1 → hook 4 → original narration 2 → Tyler → approved MP3, **78.6 seconds**. Three other ant sources remain queued. Next source research: cockroaches. Next new narration voice: Chris.

## Instructions and evidence

- [Detailed steps, state and every identified retry case](flow-and-recovery.md)
- [Writing system instructions](../writing-harness-prompts.md)
- [Voice, MP3 and listening instructions](audio-instructions.md)
- [Edge cases, implemented fixes and remaining limits](edge-cases.md)
- [Next session: fresh research through MP3](NEXT-SESSION.md)
- [Editable Excalidraw flow](../diagrams/start-to-approved-mp3.excalidraw)

## No reuse after a finished MP4

**Used means the final MP4 is complete.** Main and supporting sources stay reserved while the episode is underway. Script/MP3 approval does not consume them. Final completion makes the sources, hook and script unavailable for another episode. Shown-but-unchosen sources remain excluded from fresh shortlists without being treated as disliked.

Working defaults also remain adjustable: pest order, source freshness checks and future audio spending limits. No cron time, automatic spending allowance or fixed narration length has been approved.

## Current task

October 19 closure: reviewed edge cases, built lifecycle/crawler/audio guards, and saved the next-session trial instructions. No new episode, crawler job, model generation or paid audio call ran. All changes stay local; video production belongs to the other session.
