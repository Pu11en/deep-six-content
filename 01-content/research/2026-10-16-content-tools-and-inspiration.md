# Content tools + inspiration research (16 Oct 2026)

Question (Drew): what open-source apps, repos and skills give us a better workspace for high-quality educational pest content, starting from what already works, and with a fix for the AI making things up during generation?

Method: All Git catalog (4,328 repos, full keyword sweep of video/image/voice/explainer/fact-check/consistency terms, 551 hits narrowed by hand), web search for repos the catalog misses, GitHub API for stars/license/last push (all pulled 16 Oct), README reads for the top picks, yt-dlp sweep of 8 pest searches (~200 videos) for inspiration. Nothing installed or run. Source review is not a functional test.

## The core finding on "hallucination"

Generation goes wrong in three different places, and each needs a different fix:

1. Wrong facts in the script (wrong bug, wrong treatment, made-up stats). Fix: a claim ledger. Every factual line in a script gets a source (Texas A&M AgriLife Extension, EPA, university entomology) before anything gets made. Erik signs off on pest-specific claims.
2. Wrong visuals (AI bugs with 8 legs that should have 6, a "brown recluse" that is a wolf spider, warped text). For pest education this is the dangerous one: misidentifying a bug is misinformation. Fix: never let an image/video model invent the bug. Use real reference photos (Deep Six job photos, Wikimedia/extension photos with license logged), and render text, labels, diagrams and captions in code (HyperFrames/Remotion), which is exact every time. Use AI generation only for mood b-roll where accuracy doesn't matter, locked to reference images.
3. Drift between shots (look, colors, character change every clip). Fix: a brand kit (colors, fonts, logo, any mascot) + reference-image locking + a review step that compares each shot to the reference before it's accepted.

Tools below are picked to support that setup.

## Recommended core stack (no-face / voiceover + motion graphics)

- HyperFrames — heygen-com/hyperframes. 65k stars, Apache-2.0, pushed 16 Oct. Agent writes HTML/CSS, it renders a deterministic MP4. Text and labels are exact (no AI text warping). Free, no per-render fee. Best base renderer.
  https://github.com/heygen-com/hyperframes
- OpenMontage — calesthio/OpenMontage. 69k stars, AGPL-3.0, pushed 16 Oct. Turns Claude Code into a video production studio: 12 pipelines (explainers, image-based video, character animation), uses HyperFrames or Remotion, FFmpeg, word-level captions, free Piper narration, free stock from Pexels/Wikimedia/NASA/Archive. Works with zero API keys. Strongest single "workspace" candidate. AGPL is fine for internal use.
  https://github.com/calesthio/OpenMontage
- Claim checking — sunxiayi/make-blender-education-video-skill (55 stars, MIT). Small, but its process is exactly the guardrail we want: brief → research + claim ledger → approve one frame → then render → final QA. Copy the process, not necessarily the Blender part.
  https://github.com/sunxiayi/make-blender-education-video-skill
  Simple fact-check skills to adapt: daymade/claude-code-skills (fact-checker), analystacademy/claude-skills (/factcheck with ✅/❌ per claim + "publishable?" rating).
- Voice — Gemini TTS (gemini-3.8-flash-tts, already on Drew's key; pricing not checked) or free local Kokoro (remsky/Kokoro-FastAPI, 5.5k, Apache-2.0) / voicebox (jamiepine/voicebox, 58k, MIT; voice cloning, so Erik's voice is possible with his OK).

## Learn from what works (inspiration tools)

- edenfunf/reelmimic — 3.4k, MIT, pushed 16 Oct. Show it a video you like, it breaks down pacing, shot lengths, transitions, colors, then makes a new original video in that style. Separate agent reviews each shot. Runs on your Claude Code plan. 2D/animated only. Slow (1–3.5 h per 30–60 s). Tested mostly on Windows.
- bradautomates/claude-video (18.7k, MIT) and HUANGCHIHHUNGLeo/claude-real-video (2.2k, MIT) — let Claude watch a YouTube video (frames + transcript) so we can break down exactly why a winner works.
- mvanhorn/last30days-skill (64k, MIT) — researches a topic across Reddit, YouTube, X, web and gives a grounded summary. Good for finding the questions New Braunfels homeowners actually ask.

## Other options (alternatives, not first picks)

- tsensei/OpenReels (216, MIT) — topic in, finished Short out, one command, can run all-Google on one key. Fast, but fully automatic = least control over accuracy.
- aqm857886159/Nomi (577, AGPL) — local AI video workbench with storyboard, references, timeline; Claude Code drives it over MCP. Good if we go heavy on AI-generated footage. Mostly built around Chinese model providers.
- HKUDS/ViMax (12.7k, MIT) — idea → script → storyboard → consistent characters → video; generates 2 candidates per keyframe and auto-picks the most consistent. Built for stories, overkill for tips.
- GenielabsOpenSource/style-consistency-ai (11 stars) — tiny but focused: character-consistency skill with a verify-and-fix loop per generation. Worth reading if we make a mascot.
- vincentsch/explainroo (572, MIT) — free local explainer videos (Kokoro voice + Whisper timing). Vincentwei1021/anything2explainer (2.5k) — topic → narrated motion-graphics explainer.
- masihsultani/whiteboard-animator (240, MIT) — whiteboard hand-drawn reveal videos. Classic educational format.
- Hainrixz/open-carrusel (483, MIT) — Instagram carousel builder with Claude, exports exact IG sizes. OrRon/EpicInfographics (441, MIT) — infographic skill. Carousels/infographics double as cold-email content (step 4).
- browser-use/video-use (29k, MIT) — edit real footage (Erik's phone clips) with Claude: cuts, subtitles.
- Writing quality: blader/humanizer (57k, MIT), petergyang/no-ai-slop (12k, MIT) — strip AI-sounding phrasing from scripts and captions.
- Prompting: nidhinjs/prompt-master (14.5k), YouMind-OpenLab/awesome-nano-banana-pro-prompts (13.6k).
- Grounded research notebooks: MODSetter/SurfSense (16k, open NotebookLM). PleasePrompto/notebooklm-skill is archived; skip it.
- Big lists to browse later: zhuyansen/awesome-claude-video-skills (180 video repos, security-graded).
- Posting (step 2, later): gitroomhq/postiz-app (37k, AGPL) — self-hosted scheduler for YT/FB/IG/TikTok/Reddit.

## Machine limits (checked 16 Oct)

iMac: Intel i5-8500, 8 GB RAM, Radeon Pro 570X 4 GB. No local AI image/video models (ComfyUI, FLUX, LTX, Wan) are realistic here. Code-rendered video (HyperFrames/Remotion + FFmpeg) and light TTS run fine. AI image/video generation has to be cloud. Drew's Gemini key lists Nano Banana image models and Veo 3.1. Veo/image pricing on this key was not checked; nothing is enabled or spent.

## Inspiration: pest content that already works (YouTube, views as of 16 Oct)

- Arrow Pest Service (pest company, ~315k subs): "5 Craziest DIY Fire Ant Killers — Do They Work?" 1.38M; "Baking Soda for Roaches and Ants" 1.08M; "Most Effective Fire Ant Treatment Nobody Talks About" 536k. Format: a pro tests popular DIY myths. Closest model for Deep Six.
- Insider Science "Exterminator And Pest Expert Debunk 15 Pest Myths" 456k; "Why Cockroaches Are So Hard To Kill" 8.6M. TED-Ed same topic 4.3M. "Why" biology explainers are huge.
- Solutions Pest & Lawn "How to Get Rid of German Cockroaches (4 Simple Steps)" 997k; scorpions 148k. Numbered how-to.
- DoMyOwn "Cockroach Inspection — Where Roaches Hide" 223k in 99 s; "Signs of a Cockroach Infestation" 105k in 93 s. Short and simple.
- Local: San Antonio Water System "How to get rid of fire ants naturally" 149k. Central Texas fire ant content performs.
Pattern: myth tests, "why is this bug like this", "signs you have X", "where X hides", Texas-specific pests (fire ants, scorpions, termites). Full list: youtube-pest-sweep-2026-10-16.md (same folder).

## Open questions for Drew

- Who is on camera: Erik, Drew, or nobody (voiceover + graphics)? This picks the stack.
- Can Erik send real job photos/clips? Real footage is the biggest accuracy and trust win.
- Any spend allowed for cloud image/video generation, or free tools only to start?

## Next step

Pick the format, then install OpenMontage + HyperFrames in a sandbox and make one 30–45 s test piece (e.g. "Where scorpions hide in New Braunfels homes") with a claim ledger, to test quality and accuracy before choosing for real.
