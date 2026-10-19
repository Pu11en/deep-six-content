# Content flow: repos and prices (2026-10-16)

**Takeaway:** Use AI only for still art (the mascot and backgrounds). Do all motion and all text in code (HyperFrames). That avoids warped text and extra limbs, and it costs about $1-3 per 30 s video. No repo found covers the whole flow. Build a small custom skill from parts. Stars, license and last push were read from the GitHub API on 2026-10-16.

## Recommended flow

1. **Lock the mascot once.** Make one clean reference sheet (front, side, 3/4, 6 expressions, flat colors) with `gemini-3-pro-image`. Human approves it. Save it in `01-content/brand/`.
2. **Storyboard first (text only, free).** Opus writes a shot list: script, on-screen text, which pose per shot. Human approves before any image is made.
3. **Poses with Nano Banana 2.1.** Use the reference sheet as input every call, never an earlier output (drift builds up). Ask for a flat or green background so it cuts out cleanly. Make 3 candidates per pose.
4. **Auto check, then human check.** Opus views each image against a rubric (hood color, 2 arms, scythe shape, no stray text, lime/purple palette). It writes a contact-sheet Markdown file the operator opens in Zed Markdown Preview. The operator ticks keep/reject.
5. **Assemble in HyperFrames.** Approved cut-outs become layers. GSAP does bounce, blink and pan. All text is real HTML text in the brand font. TTS voice from Gemini.
6. **Check the render.** Opus pulls frames and checks text spelling and framing. Human watches the final.
7. **Only if needed:** one Veo 3.1 Lite image-to-video clip for a hero shot, starting from an approved pose.

**Cost per 30 s video (Google price page, fetched today):**
- Code-motion flow: about 25 images at 1K ($0.034 each) = ~$0.85. Add the sheet ($0.134) and TTS (under $0.01). **Total about $1-2.**
- With Veo: 4 clips x 8 s = 32 s. Lite 720p at $0.05/s = $1.60. Fast 720p at $0.10/s = $3.20. Double it for retries. **Total about $4-8.**
- Batch API halves image prices (not Veo).

## Verified prices (ai.google.dev/gemini-api/docs/pricing)
- Veo 3.1 per second, audio included: Lite $0.05 (720p) / $0.08 (1080p). Fast $0.10 / $0.12 / $0.30 (4K). Standard $0.40 / $0.40 / $0.60.
- Images: Nano Banana 2.1 $0.0336 (1K), $0.0504 (2K). 3.1 Flash Image $0.067 (1K). 3 Pro Image $0.134 (1K/2K). Flash Lite Image $0.0336.
- Veo docs: Lite and Fast both do image-to-video, 4/6/8 s, 9:16. Reference images (up to 3) only on non-Lite. Lite cannot extend clips. Both in Preview.
- Image docs: up to 5 character references on Nano Banana 2.1; Pro does not take character references (it takes 6 object and 3 style references). All outputs carry a SynthID watermark.
- Gemini 2.5 Flash Image shuts down 2026-10-02 (already gone).

## Repos

**Workspaces and skills**
- [juliandickie/creators-studio](https://github.com/juliandickie/creators-studio): 3 stars, MIT, pushed 2026-10-16. Brand presets, asset registry, storyboard, mandatory REVIEW-SHEET.md approval before costly clips, cost ledger. Closest match to our flow, but tiny and uses Kling/Veo. Verdict: copy its ideas, test before trusting.
- [AgriciDaniel/banana-claude](https://github.com/AgriciDaniel/banana-claude): 1106 stars, MIT, 2026-10-16. Gemini creative-director skill, cost estimate before each call, local typesetting for exact text. Weak on consistency. Verdict: best Gemini image skill to start from.
- [harshkedia177/image-gen-plugin](https://github.com/harshkedia177/image-gen-plugin): 5 stars, no license, 2026-08-03. Self-review loop (0-3 rounds) plus 360-degree character sheets and identity lock. Verdict: copy the loop idea; no license means do not copy code.
- [kingbootoshi/nano-banana-2-skill](https://github.com/kingbootoshi/nano-banana-2-skill): 418 stars, MIT, 2026-04-02. CLI with green-screen cut-out (FFmpeg + ImageMagick), multi-reference, cost log. Verdict: good for cut-out pieces.
- [LottieFiles/motion-design-skill](https://github.com/LottieFiles/motion-design-skill): 2258 stars, MIT, 2026-05-18. Timing, easing and Disney-principle rules for agents. Verdict: cheap add-on to make motion feel good.
- [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes): 65201 stars, Apache-2.0, 2026-10-16. HTML to video, GSAP and Lottie, live-reload browser preview, lint, 21 skills, TTS and captions. CPU-only rendering not confirmed. Verdict: main engine.
- [remotion-dev/remotion](https://github.com/remotion-dev/remotion): 64564 stars, custom license, 2026-10-16. Free for individuals and companies up to 3 employees; larger needs a paid license. Verdict: backup; HyperFrames is simpler.
- [Vincentwei1021/video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft): 12181 stars, Apache-2.0, 2026-10-16. Remotion shot recipes for product videos. Unverified fit. Verdict: skim only.

**Animating the mascot**
- [nolangz/pixel2motion](https://github.com/nolangz/pixel2motion): 2432 stars, MIT, 2026-08-21. Raster logo to clean SVG with named parts plus CSS motion. Needs only Python, Chrome, Playwright (no API key). Examples are simple marks. Unverified for a detailed chibi.
- [visioncortex/vtracer](https://github.com/visioncortex/vtracer): 7313 stars, MIT, 2026-10-12. Raster to SVG. Works on flat colors; loses detail on shaded art.
- [zluckyhou/living-logo](https://github.com/zluckyhou/living-logo): 1 star, MIT, 2026-09-04. Builds an SVG-rig mascot from text only. Cannot use our existing art. Verdict: shows the pattern only.
- [QwenLM/Qwen-Image-Layered](https://github.com/QwenLM/Qwen-Image-Layered): 2139 stars, Apache-2.0. Splits images into layers but needs a GPU. Verdict: skip.

**Quality control and gallery**
- No ready image-QC skill was found (verified gap). Build one: Opus (vision) scores each image against a rubric and returns JSON `{score, pass, issues}`, best of 3.
- [seochan99/JudgeActs](https://github.com/seochan99/JudgeActs): 0 stars, MIT. Finds small VLM judges pick the first image about half the time. Verdict: shuffle order and keep the human as final judge.
- [konglingbukong/gpt-image-studio](https://github.com/konglingbukong/gpt-image-studio): 1 star, MIT, 2026-10-16. Local live web gallery at 127.0.0.1:8765, cost tracking, `sh start.sh` for Linux. OpenAI only, no approve button. Verdict: pattern only.
- Zed Markdown Preview on a contact-sheet `.md` with relative image links. Not tested here (unverified); it fits the operator's current setup.

## Caveats
- Verified: prices, docs, repo stats. Unverified: Lite quality on cartoon mascots, pixel2motion on a detailed mascot, CPU-only HyperFrames render speed.
- Prices are Preview-tier and may change.
- Reference-sheet tips (re-anchor to the original, name each reference's role) come from third-party blogs, not Google.
