# First production test

**Historical concept record:** Drew later rejected v1's separate voice and near-still motion. The current requirement is each video's own narrator plus clear character action, with Opus 5.5 directing the replacement. See [current specification](../APPROVED-OUTRO.md).

The wording and transition are ready. Drew approved one hybrid mascot image test, up to US $0.15, with "ok yes" on 19 October 2026. This covers one request only. Voice, animation and further generation remain outside that spending approval.

**Result:** the test returned [a JPEG draft](../assets/hybrid-still-v1.jpg), at an estimated $0.058155. [Visual review](IMAGE-TEST-REVIEW.md) found identity corrections needed before animation. The single authorized request is used. [The next plan](NEXT-PRODUCTION.md) covers the proposed remaining work and budget.

## Prepared request

- Provider and model: Google Gemini API, `gemini-nano-banana-2.1`. The project-specific credential passed a read-only check and the model appeared in the catalog; generation itself is untested.
- Prompt: [still-prompt.txt](still-prompt.txt).
- Reference images: the original Deep Six ad and the existing final-render opening frame sheet, both inspected in this session. Their exact paths are in the prompt.
- Requested output: one portrait 9:16 image at the model's 2K setting. Actual output: `01-content/outro/assets/hybrid-still-v1.jpg`, 1536 x 2752. Preserve its actual JPEG format; enforce exact video dimensions at assembly.
- Purpose: check the original mascot's identity in the video's paper style before attempting motion.
- Approved request ceiling: **US $0.15 for this one image test**. No automatic retry, video generation, voice generation, purchase of credits or publishing is included.

Google's checked Standard rate is $0.0504 for one 2K output image, plus input and other token charges. The 15-cent ceiling leaves room for those charges; it is a limit, not a claim that the call costs exactly 15 cents. Verify the rate and bound the request before sending it. If the requested settings cannot fit the ceiling, stop before the call. [Published pricing](https://ai.google.dev/gemini-api/docs/pricing), checked 19 October 2026.

## After the image

Compare the face, hood, badge, proportions and paper treatment with the supplied references. Save the result and a short check note in this directory. Do not silently approve a different mascot because the output looks polished.

The existing image helper also writes to the shared board and a separate experiment log. This session's explicit instructions keep its files under `01-content/outro/` and its discussion in chat. Honor those instructions when executing the eventual request; do not use the helper unchanged in a way that modifies another session's presentation.

Once the still is suitable, prepare the exact video and voice calls with their current costs before requesting further spending approval. The approved target is a 4.5-second master plus the reusable 0.5-second entry described in [the specification](../APPROVED-OUTRO.md).

## Drew's review order

Produce the reusable outro first and show it to Drew. Only after he approves the finished outro should this session write and produce the missing educational close for **Deep Six - Fire Ants Full v2**, then assemble a new final video. Keep the existing `full-v2.mp4` unchanged. The ten narration adaptations remain with the original narration chat. No automatic report-back.
