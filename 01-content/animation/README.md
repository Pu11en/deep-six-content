# Illustrated video production

**Current: [hook v1](episodes/D6-6c917b49743b/hook/progress.md) animates the first 8.8 seconds of the approved narration, one picture per phrase, in cut-paper style C. It awaits Drew's review.** The earlier single-scene motion test was rejected for too little motion. [How narration becomes animation](choreography/README.md): word timing, a director prompt, an animator prompt and a beat-sheet self-check.

## The review flow

Approved narration → scene settings → rendered frame → Drew approves the look → audio timing → short moving preview → Drew approves movement → full video → final review.

Each candidate has its own image, input fingerprints and review record. Approval must refer to that candidate's fingerprint. A changed drawing requires a new candidate and review. A technical check passing is not Drew's approval.

Save Drew's stated visual feedback in that review record and carry it into the next authoring brief. Do not invent a reason for rejection or treat unchosen options as disliked. A requested art direction is not yet an approved rendered style.

## Reusable now

- A scene configuration controls the episode, dimensions, text, palette, seed and approved audio reference.
- New episodes use `"brand_profile": "brand.json"` to load the palette from Drew's Deep Six ad. The original scene uses a branding overlay; the three alternatives draw that palette directly into their own layouts. The reference image and profile are fingerprinted with each render.
- The renderer checks the audio approval and fingerprint, then draws locally without model or voice-service calls.
- Matching inputs reuse the saved frame. Changed inputs require a new revision; reviewed files are not overwritten.
- The drawing modules accept a time value. The three alternatives currently draw stills; actual movement must be implemented after style selection.
- Pinned drawing helpers, fonts, notices and the dependency lockfile travel with the project. No global plugin was installed.

## Run the current frame

Dependencies are already installed. Reuse B with `npm run frame -- episodes/D6-6c917b49743b/style-options/cartoon/scene.json`; substitute `paper` or `miniature` for the other new options.

Only if dependencies are absent, use `npm ci --ignore-scripts --no-audit --no-fund`. The renderer supports the registered `fire-ant-brood` and `fire-ant-style-options` modules at 1080×1920. Historical A outputs are preserved; rerendering them with changed renderer inputs requires a new revision. The historical default frame config remains A; C is selected in the comparison record. The moving test has a separate config.

## Still to build after review

Measured narration timing, the short video encoder, motion review, the full scene sequence, captions and connections to the writing harness. No cron, publishing or automatic approvals are active. Different pests will need appropriate researched drawing modules; changing a label cannot create a new species.

[Authoring brief](authoring-brief.md) · [Scientific drawing limits](science-notes.md) · [Research comparison](../research/2026-10-19-illustrated-animation/findings.md)

## Cut-paper motion test

Use `npm run motion -- episodes/D6-6c917b49743b/motion-paper/scene.json` to reuse the completed preview. The renderer verifies C’s approval, the existing audio and brand fingerprints, then makes a 1080×1920 H.264/AAC MP4 locally. Matching completed outputs are reused; changed inputs require a new revision. It never generates speech or calls a paid service.

Drew watches videos from his Windows Desktop. Copy each MP4 there and do not open a player (Drew, 19 Oct 2026). `tools/open_d6_video.py` is retired for review use.
