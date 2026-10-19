# Hook research repo findings

Best fit: adapt **viral-outliers** to find real short videos, then use **hookmaxxing**'s video study protocol to record what each opening says and shows. Neither covers the full pest-control workflow. After research, draft five distinct original hooks from the authoritative pest article; after selection, write five narration options that preserve the chosen hook and cite that same article.

## Recommended sources

### 1. [w-avw/instagram-viral-reels-research-claude-skill](https://github.com/w-avw/instagram-viral-reels-research-claude-skill/tree/a6d84757dd9518a4db348f733fdd17555c19e1a4/skills/viral-outliers)

Inspected revision: `a6d84757dd9518a4db348f733fdd17555c19e1a4` (`master`).

- Primary workflow: [`skills/viral-outliers/SKILL.md`](https://github.com/w-avw/instagram-viral-reels-research-claude-skill/blob/a6d84757dd9518a4db348f733fdd17555c19e1a4/skills/viral-outliers/SKILL.md). It says not to script without watching/listening; asks for both audio transcript and visual frames; stores verbal, written, and visual hook, literal transcript, source link, metrics, and timestamps. It separates source format from the user's original version and warns against inventing claims.
- Executable fetcher: [`scripts/getreel.sh`](https://github.com/w-avw/instagram-viral-reels-research-claude-skill/blob/a6d84757dd9518a4db348f733fdd17555c19e1a4/scripts/getreel.sh). Given a Reel shortcode, it reads metadata, downloads MP4, extracts six frames/contact sheet, makes WAV, and prints metrics. Requires OpenCLI + connected Chrome extension, `curl`, `ffmpeg`, and Python 3. Transcript step uses `faster-whisper` in the skill; local CPU transcription, no paid API disclosed. Its discovery instructions call `agent-reach`/OpenCLI and an Instagram logged-in Chrome session. Repo README says agent-reach web search, Reddit, and YouTube subtitle paths work without login; Instagram needs the OpenCLI session. No dollar cost stated.
- Evidence limits: discovery is tied to undocumented/private Instagram endpoints and logged-in sessions; endpoints, thresholds, and access can break. It uses hard cutoffs (700k views and 5× follower count) and presents them as method rules, not validated predictors. Those thresholds may exclude useful educational or local pest videos. Metrics are snapshots, and skill itself notes share counter changed in 2025. Treat as candidate-finding aid, retain direct links, and verify each video manually.

### 2. [yerdaulet-damir/hookmaxxing](https://github.com/yerdaulet-damir/hookmaxxing/tree/16faf862a683616ba0d8b36bf44013b93280385c/skills/write-scroll-stopping-hooks)

Inspected revision: `16faf862a683616ba0d8b36bf44013b93280385c` (`main`).

- Most useful research file: [`references/video-study-protocol.md`](https://github.com/yerdaulet-damir/hookmaxxing/blob/16faf862a683616ba0d8b36bf44013b93280385c/skills/write-scroll-stopping-hooks/references/video-study-protocol.md). It requires canonical URL, metadata, video/captions, timestamped frames; inspect exact spoken argument and first five seconds; label notes as **Source claim**, **Observed**, **Inference**, or **Verified subline**. It says performance claims stay creator claims unless independently checked, and says not to claim a video was watched from transcript alone.
- [`SKILL.md`](https://github.com/yerdaulet-damir/hookmaxxing/blob/16faf862a683616ba0d8b36bf44013b93280385c/skills/write-scroll-stopping-hooks/SKILL.md) is useful later: write from body truth, require visible proof and exact payoff, generate candidate families, curate five, and reject unsupported claims. The core is an agent instruction, not a video-discovery tool. Repo also has executable local `hook_bank.py` and `lint_copy.py`, but neither finds nor inspects videos. No external service or price required for this research protocol.
- Evidence limits: protocols and source studies are authored guidance, not proof that techniques reliably improve reach. Use for disciplined notes and truthful hook checks; do not infer effectiveness from examples alone.

## Other repos checked

- [Ootto-AI/claude-content-skills](https://github.com/Ootto-AI/claude-content-skills): `skills/reel-analyzer/SKILL.md` gives a useful prompt for exact 1–3s spoken/on-screen hook, timed beats, pacing, and visuals. But its instructions expect user to supply a found reel or frames/transcript. The separate `agent-reach` routes discovery and downloads, but Instagram is not clearly a supported source in its stated zero-config channels. Better as a teardown prompt than the end-to-end finder.
- [gAmUssA/watch-skill](https://github.com/gAmUssA/watch-skill): `SKILL.md` and `scripts/hook.py`, `frames.py`, `report.py` inspect a supplied video, including dense first-ten-second frames and word-level transcript. It cannot find candidate videos. Requires `yt-dlp`, `ffmpeg`, `whisper.cpp`, and downloads a ~550 MB local model; local transcript avoids API cost, while optional Groq/OpenAI transcription costs per use. More setup than needed for this stage.

## Practical recommendation and limits

Use viral-outliers for Instagram discovery/fetch only if current session access works; adapt beyond Instagram with links from YouTube/TikTok/Shorts or user-provided candidates. For every candidate, keep URL, creator, date, visible metrics, exact opening transcript with timestamp, opening-frame description, and source-vs-observation labels. Select openings as structural inspiration, never copy lines. Keep pest facts grounded in a separate authoritative article; video performance does not validate pest-control claims. Neither repo implements the staged choice flow (five hooks → user selects → five narrations preserving exact hook and source), so enforce that in the local workflow prompt/template.
