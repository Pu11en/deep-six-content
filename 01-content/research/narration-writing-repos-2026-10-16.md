# Repos for automated narration writing

**Best fit for Deep Six: Sterling Chin's spoken-writing method plus KLV's example-driven editing pass.** This recommendation is based on inspected instructions and code, not a test of their generated narration.

## Shortlist

### REPO-W001 — SterlingChin/video-production-skills

[Repository](https://github.com/SterlingChin/video-production-skills) · [writing instructions inspected](https://github.com/SterlingChin/video-production-skills/blob/7c06790e9bc1d83662b749b2fa09e62fe8c2b1ef/skills/video-scriptwriter/SKILL.md)

Strongest match for the voice problem. Develops a focused story, drafts for speech, revises against a spoken read, and separately checks the ending and factual accuracy. Its voice profile records approved and rejected examples. The narration checklist catches breathless clauses, repetition, and competing endings.

Automation level: instructions an AI writing agent can follow, plus a counting/timing helper. A genuine spoken-read check still requires a recording or observed read. Reviewed as research; no skill installed or invoked.

Also inspected `references/narration-checklist.md` and `references/voice-profile-template.md` beneath the same scriptwriter folder. Revision `7c06790e9bc1d83662b749b2fa09e62fe8c2b1ef`.

### REPO-W002 — klv-ai/voiceover

[Repository](https://github.com/klv-ai/voiceover) · [automatic editing code inspected](https://github.com/klv-ai/voiceover/blob/50dc7a75e245dd508ca5b6aec4ceb7d6cfbec203/narrate/lab/polish_script.py)

Best reusable automation pattern. Selects relevant before/after examples of a narrator's edits, provides surrounding lines, and proposes revisions. Treats already edited lines conservatively. Additional code checks some unwanted changes, including new numbers and certain word substitutions.

Key locations: `SYSTEM`, `pick_examples`, `prompt_for`, and `judge`. These checks are limited heuristics, not comprehensive fact checking. Designed for recorded product walkthroughs; adapting the editing method to pest education is our proposal. Revision `50dc7a75e245dd508ca5b6aec4ceb7d6cfbec203`.

### REPO-W003 — trinh-56/youtube-script-writer

[Repository](https://github.com/trinh-56/youtube-script-writer) · [editing prompts inspected](https://github.com/trinh-56/youtube-script-writer/blob/6cf06ac11af9d82bd74c19ce92d355421cca59e2/app/backend/prompts.py)

A local writing app with separate angle, revision, and packaging stages. The revision prompt preserves the author's argument and requests explanations of meaningful paragraph edits. Supporting craft notes discuss varied rhythm and cause-and-effect transitions.

Useful as an editing workflow reference. Its movie-review/vlog assumptions and longer YouTube formulas need adaptation for brief homeowner advice. Also inspected `script-generator/SKILLS.md`. Revision `6cf06ac11af9d82bd74c19ce92d355421cca59e2`.

## Other candidates checked

- [Ghost Creator](https://github.com/HunterisLive-1/ghost-creator): has a real script critic. However, the inspected [pipeline](https://github.com/HunterisLive-1/ghost-creator/blob/4bb92f30cea295151e4bbca1a0529b89448c8f01/graph/pipeline.py) routes the critic to human review; its script node does not consume critic feedback. Do not describe this revision as a verified autonomous critique-and-rewrite loop based on its README diagram.
- [ldhiman's video creator](https://github.com/ldhiman/Agentic-AI-Based-Video-Creater): inspected writer and critic code. Primarily requests short frame-based scripts and evaluates hook, visuals, and coherence. Less specific about natural spoken language.
- [web3-claw/yt-agent](https://github.com/web3-claw/yt-agent): keeps voice examples and rejected ideas, but the inspected script structure targets much longer videos.
- [skindhu's narration guide](https://github.com/skindhu/skind-skills/blob/main/skills/educational-video-creator/references/script-and-narration.md): useful audience and rhythm guidance; structured educational examples rather than evidence of successful automatic revisions.

## Proposed use

Keep the approved ant hook and ANT-S001 facts. Draft one connected explanation, then apply a separate editor pass informed by specific approved/rejected wording. Check every revised factual claim against the article. Judge the actual wording and spoken delivery before accepting it.

## Progress and limits

- Research completed October 16, 2026. Three shortlisted writing references logged separately from pest-content sources.
- Read actual source files and repository metadata; no software installed or executed, no paid calls, no publication.
- No new narration drafted. Existing trial prompt remains an experiment; the current ant narration remains rejected and hook 14 remains selected.
- Next useful test: apply the writing/editing method to that hook. No output-quality or audience-performance claims have been verified.
