# First outro draft produced

**Historical v1 plan, now rejected by Drew.** Use [the corrected requirements](../APPROVED-OUTRO.md) and Opus 5.5 replacement direction. This plan does not authorize a replacement media call.

Drew approved **up to US $2.00 additional API spend** for image corrections, animation and voice by replying "yes" to that exact budget question. The six-cent first test is separate. See [approval record](production-approval.json).

Drew selected option 2, Educational sign-off, after reviewing the three layouts. That confirms the concept in [APPROVED-OUTRO.md](../APPROVED-OUTRO.md); the separate $2.00 production budget is now approved.

## Concrete work

1. Correct the first still using [this prompt](still-correction-prompt.txt), the original ad and the generated draft. Keep a versioned output. Compare identity before animating.
2. Prepare the real logo from the original source artwork. Preserve exact lettering and shapes. Never replace it with a newly invented wordmark. The logo remains a stable overlay outside the AI video.
3. Generate a single mascot animation with Google `gemini-omni-1.1-flash`, using the checked still as its first frame and [this motion prompt](video-prompt.txt). Request 9:16 at 720p. A 10-second source costs about $1.0136 in output video tokens; input and any other tokens are extra. Assemble a 4.5-second master at 1080 x 1920, 30 fps. Upscaling does not add native detail. Verify duration rather than claiming the provider has a precise 4.5-second setting.
4. Record the exact sign-off with Google `gemini-3.8-flash-tts`, prebuilt voice `Sulafat`, and [this direction](voice-prompt.txt). Sulafat is listed as warm. This is a proposed production voice, subject to Drew's finished-outro review. Do not clone a person or regenerate the episode's lesson.
5. Composite the real logo and exact screen wording. Match the five-second ending specification, including its separate half-second entry. Check actual spoken timing, pronunciation, image consistency, frame size, audio clipping and final hold.
6. Save the outro here and copy the review MP4 to Drew's Windows Desktop without opening a player. Obtain his approval of the finished outro before writing or producing the missing close for the fire-ant video.

## Budget controls

- At most three additional image calls, capped at $0.15 each, including any necessary correction or faithful source preparation.
- At most one video call, capped at $1.25 including inputs and other tokens. Recheck support and token limits before calling. A failed or unusable result does not authorize a second video call.
- At most two short voice calls, capped at $0.05 each, allowing a timing correction if needed.
- Maximum allocated total: $1.80; approved overall ceiling: $2.00. Record usage and estimates after each call. Do not buy credits, publish, or exceed the ceiling. A ceiling is not a completion guarantee if generation fails.
- Before every call, calculate a conservative token bound that fits its allowance. The image preflight counter understated image inputs in test one, so allow for the provider's published input-image allocation and the observed usage. If a safe bound cannot be established, do not send that call.

## Current evidence

[Google pricing](https://ai.google.dev/gemini-api/docs/pricing), checked 19 October 2026: Nano Banana 2.1 is $0.0504 per 2K output plus inputs/text/thinking; Omni 720p uses 5,792 tokens per second at $17.50 per million; Flash TTS audio is $9 per million tokens through 31 December 2026, with 25 audio tokens per second. These are Standard rates and exclude taxes or account-specific adjustments.

[Omni guide](https://ai.google.dev/gemini-api/docs/omni): supports image-conditioned portrait video; 1080p output is upscaled. Its current API does not accept audio references for matching a voice, so use separate TTS. [Voice guide](https://ai.google.dev/gemini-api/docs/speech-generation): lists Sulafat as warm.

Production is complete for review within the approved limits. See [the result and checks](REVIEW-V1.md). Versioned receipts record two additional image calls, one video call and one voice call; estimated additional cost is $1.136070. The steps above are the pre-production plan; REVIEW-V1.md records the actual edit and limits. Original MP4, brand references and narration scripts stay unchanged.
