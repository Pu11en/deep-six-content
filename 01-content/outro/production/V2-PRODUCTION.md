> Executed: v2 is generated and ready for Drew's review. See [finished production record](REVIEW-V2.md) and [current specification](../APPROVED-OUTRO.md). The sections below record the earlier prepared plan and proposal.

# Opus 5.5 replacement: magnifier launch

**Opus 5.5 wrote the replacement concept and exact prompts. Production is prepared; the replacement media has not been generated or approved.**

[Final Opus direction](OPUS-V2-REUSABLE.md) · [Model proof](opus-v2-revision-receipt.json) · [First successful creative pass](opus-v2-focused-receipt.json).

## What Drew will see

The lesson picture clears to cream paper. The reaper crouches behind a paper fold, looks up, then springs upright with a robe flare. Its magnifier swings from low to high in a wide arc. The real Deep Six logo appears inside the moving lens, emerges when the lens stops, and lands above the mascot as the narrator says the company name. The robe and arm settle while the readable logo holds.

About five to six seconds including entry, fitted to the actual narration. No ants, anthill, soil or episode-specific backdrop. No extra CTA.

Exact speech: **Helping you understand pests. Deep Six Pest Control.** On-screen: that first sentence during the action, followed by the actual **DEEP SIX PEST CONTROL** logo as it lands. No generated logo lettering.

## Audio scope correction

The animation master contains **no narration**. Future videos generate the entire narration, including the sign-off, in the episode's chosen voice. Timing follows that recording.

**For this already-produced fire-ant video, preserve the existing Tyler recording and full-v2 MP4.** Generate only a Tyler sign-off audition for the replacement-outro review, using [the verified voice settings](fire-ant-voice-reference.json). This is a review track for this episode, not a universal outro voice asset.

This overrides the sentence in the raw Opus draft that says to generate the full fire-ant narration for the review. Regenerating its approved lesson is unnecessary. The raw model response remains unchanged for provenance. The missing educational closer and final join still come only after Drew approves the replacement outro.

## Prepared generation inputs

- Reference A: `01-content/brand/fun-fact-friday-spider.png`, original character identity.
- Reference B: `01-content/outro/assets/v2-paper-style-reference.png`, actual paper texture/edge extracted from the approved video. [Provenance](v2-style-reference.json).
- First-frame prompt: [v2-start-frame-prompt.txt](v2-start-frame-prompt.txt), exact Opus text.
- Last-frame prompt: [v2-end-frame-prompt.txt](v2-end-frame-prompt.txt), exact Opus text. Supply the accepted first frame as the edit reference.
- Video prompt: [v2-video-prompt.txt](v2-video-prompt.txt), exact Opus text. Upload the accepted first and last frames in that order and prefix `[# Sources <FIRST_FRAME>@Image1 <LAST_FRAME>@Image2]`.

Image route: Google `gemini-nano-banana-2.1`, portrait 2K, one result per request. Video route: `gemini-omni-1.1-flash`, portrait 720p. Perform the major action in the first four seconds, then hold. [Google documents the first/last-frame role tags](https://ai.google.dev/gemini-api/docs/omni). Provider timing is a target, not a guarantee; inspect the actual clip before editing. Output resolution is checked and reported before conforming to 1080 x 1920 at 30 fps.

Save first/end artwork as new versioned files. Reject a wrong face, badge, hand assignment or weak pose before using paid video generation. If the allowed image calls do not yield usable reference art, stop before spending the video allowance.

## Logo and animation assembly

Use actual source pixels for the logo. Compare any larger ad crop with the clean official website file. If the logo shapes or lettering differ, keep the genuine official file; do not generatively redraw it. Choose a readable landed size and report any remaining source softness honestly. A higher-resolution real logo remains desirable, but no external request has been sent.

Track the lens rim. Show the logo within its circular matte during the end of the swing, then release it only when the lens stops. Move it to the upper brand area with one small settle. Have it landed by the narrator's first word of **Deep Six Pest Control**. Keep the face, hands, chest badge and logo inside the useful portrait area.

Retain a meaningful body rise and arm swing. The camera may support the movement but cannot substitute for character animation. Reject drift rather than replacing the shot with a mostly frozen poster. Adjust the entry and settled hold for voice timing; do not speed up the speech or character.

Planned outputs, **not yet created**:

- `01-content/outro/assets/outro-animation-v2.mp4`: reusable animation with real logo and no narration.
- `01-content/outro/assets/outro-animation-clean-v2.mp4`: checked text-free animation for assembly flexibility.
- `01-content/outro/assets/fire-ant-tyler-signoff-review-v2.wav`: this episode's review speech only.
- `01-content/outro/assets/outro-review-fire-ant-v2.mp4`: the new outro with Tyler for Drew's review, copied to Desktop without opening a player.
- Timing metadata identifying the lens stop, logo landing and flexible hold, plus source/identity/audio checks.

## Budget awaiting approval

Proposed change: raise the production cap from **$2.00 to $3.00**. Already estimated in this phase: **$1.136070**. The earlier $0.058155 image test remains separate.

| Replacement work | Maximum calls | Maximum reserved cost |
| --- | ---: | ---: |
| Beginning and ending reference images | 2 | $0.30 combined |
| One new source video | 1 | $1.25 |
| Tyler sign-off review | 1 | $0.10 |
| Total new work | 4 | **$1.65** |

Maximum estimated/reserved production total after this work: **$2.786070**, below the proposed $3.00 cap. No automatic retries, credit top-ups, plan changes or publication. Verify the voice provider's actual availability and cost before its request. Failed generations do not authorize extra calls. [Machine-readable proposal](v2-budget-proposal.json).

Conservative Google bounds must include image inputs, prompt text and output/thinking limits. At current Standard rates, a ten-second 720p Omni source uses $1.0136 of video output tokens, plus input/thinking. A 2K Nano Banana image uses $0.0504 of image output tokens plus other usage. [Google pricing](https://ai.google.dev/gemini-api/docs/pricing), checked 19 October 2026. These are planning estimates, not invoice totals or success guarantees.

Opus ran through the existing Claude subscription login with API-key routing disabled. Its CLI cost-equivalent metadata is not an additional media API charge. No replacement media request has been submitted.
