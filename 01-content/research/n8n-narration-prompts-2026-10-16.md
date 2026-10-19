# n8n narration prompt research

**Best lead: provide a real voice example and specific editing notes, then draft from verified facts.** This is a proposed writing method, not a demonstrated improvement in Deep Six scripts.

## What was checked

Read public n8n template pages and the scripting instructions returned by n8n's public template endpoint on October 16, 2026. Inspected prompts directly, rather than relying on template descriptions. No workflows were imported or executed.

## Three useful references

| ID / template | Exact location in workflow | What the prompt actually does | What to adapt |
|---|---|---|---|
| N8N-W001 · [9445: Instagram content repurposing](https://n8n.io/workflows/9445-ai-powered-instagram-content-repurposing-with-openai-gpt-4o-and-perplexity-research/) | `Write New Script` → `parameters.messages.values[1–4].content` | Supplies a rough script, research, practical steps, editing suggestions, and an example input/output pair. Requests restrained, casual language. | Give the writer concrete feedback and an example of the desired voice. The sample contains a product-comparison claim unsupported by its supplied research; do not inherit its claims or compulsory promotional ending. |
| N8N-W002 · [10303: Scripts from trending reels](https://n8n.io/workflows/10303-generate-viral-instagram-scripts-by-analyzing-trending-reels-with-apify-and-gpt-4/) | `AI Agent` → `parameters.options.systemMessage` | Studies a transcript's pacing, tone, dialogue, curiosity, humor, and ending. Requests fresh wording for a different topic. | Learn how an approved example moves between ideas. Keep pest facts separate. Its requested youth-oriented tone and compulsory CTA are not Deep Six requirements. |
| N8N-W003 · [10051: Podcast creation](https://n8n.io/workflows/10051-automate-podcast-creation-with-gpt-claude-and-eleven-labs-text-to-speech/) | `Podcast Script Agent` → `parameters.options.systemMessage`; `Podcast Idea/Topic Agent` → same field | Defines a friendly solo speaker, contractions, an everyday audience, and a specific episode angle. | Define who is speaking to whom. Use natural contractions and a focused lesson. Do not adopt its celebrity references, canned handoff, or instruction to replace unverified details with vague authorities. |

Direct public configuration evidence: [9445](https://api.n8n.io/api/templates/workflows/9445), [10303](https://api.n8n.io/api/templates/workflows/10303), [10051](https://api.n8n.io/api/templates/workflows/10051). Locations above identify the fields inspected; unrelated credentials and workflow settings were not saved.

## Other checks and limits

- [9251, comments to TikTok](https://n8n.io/workflows/9251-turn-tiktok-comments-into-ai-avatar-videos-with-dumpling-ai-gpt-4-and-captionsai/): useful audience-question input, but the script prompt mostly asks for conversational writing without demonstrating it.
- [15328, three-platform scripts](https://n8n.io/workflows/15328-generate-youtube-reels-and-tiktok-scripts-from-one-topic-with-gpt-4o-mini-google-sheets-and-gmail/): explicitly limits the TikTok version to one idea. Its word counts and mandatory engagement endings are template choices.
- [10158, news recap](https://n8n.io/workflows/10158-automated-news-video-generation-with-heygen-ai-apify-and-gpt-41-mini/): includes a voice example and omits introductory and closing boilerplate. A compressed multi-story news format does not suit this ant lesson.
- [12347, audio documentary](https://n8n.io/workflows/12347-generate-audio-documentaries-from-web-articles-with-elevenlabs-and-browseract/): its script prompt hard-codes an unrelated medical story despite the broader article-conversion description. Unsuitable as a general source-to-script prompt.
- [8404, video automation](https://n8n.io/workflows/8404-automate-ai-video-creation-and-multi-platform-publishing-with-gemini-and-creatomate/): emphasizes sensational reveals and a fixed scene formula. Poor fit for Drew's request for natural homeowner education.
- [4658](https://n8n.io/workflows/4658-automate-instagram-content-discovery-and-repurposing-w-apify-gpt-4o-and-perplexity/) contains the same script instructions and example pair as 9445; not independent evidence.

Template availability and creator claims do not establish writing quality, retention, or conversion results. No performance claims were verified. No generated audio was evaluated.

## Application to Deep Six

The rejected narration reads like compressed inspection notes. Concrete edits: replace abstract language such as “contact points” with the physical place the homeowner should look; connect actions to their reasons; vary sentence length. These are our editorial judgments, not findings proven by n8n.

Saved a [trial narration prompt](../experiments/2026-10-16-ant-return-narration/narration-prompt-trial.md). It combines the useful methods with Drew's existing requirements: retain the selected hook, stay within one verified factual source, and give homeowners useful advice. It is an experiment, not a new skill or permanent rule.

## Progress

- Research and trial prompt complete; prompt displayed on the content board.
- Current hook-14 narration was rejected for its voice. Hook remains selected; replacement narration has not been approved or drafted in this research step.
- Writing references logged separately from factual episode sources. ANT-S001 remains the factual source for this episode.
- Next: test the prompt on the selected hook and compare the actual narration. No spending, publishing, or workflow execution.
