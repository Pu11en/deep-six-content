# Approved Deep Six outro specification

**Drew chose option 2, Educational sign-off. The complete five-second draft is ready for his review. Finished-media approval remains pending.**

> Helping you understand pests. Deep Six Pest Control.

## Approval scope

Drew explicitly chose option 2 from [the three illustrated alternatives](VISUAL-OPTIONS.md), confirming these exact words and the cream paper transition. This is the educational sign-off, not the flashlight idea in an older numbered brainstorm. It is a selected video sign-off, not a claim about an existing company-wide tagline.

He approved one image test up to $0.15, then replied "yes" to an additional $2.00 for image corrections, animation and voice. [Approval record](production/production-approval.json). New production used an estimated $1.136070; the earlier test used $0.058155. These are usage-based estimates, not invoice totals.

**Production order:** finish the outro, obtain Drew's approval of the finished media, then create the missing educational close and join for **Deep Six Fire Ants Full v2** as a separate final output. No fire-ant close or join has been produced here. The original narration chat owns its ten full script adaptations. No publishing or automatic report-back is authorized.

## Exact words and fixed elements

Spoken, exactly once: **Helping you understand pests. Deep Six Pest Control.** Eight words. Use [the plain-text copy](outro-spoken.txt).

On screen: the actual **DEEP SIX PEST CONTROL** logo, with **Helping you understand pests.** below it. No follow, booking or website request.

After Drew approves the media, reuse the same master, recorded voice, wording, logo, mascot movement, layout, duration and transition settings for every episode. Record once and append that identical recording once. Only the lesson and its final useful sentence vary. No pest name, date or episode reference enters the outro.

## Produced visual and audio

The source-ad reaper retains its original black oval eyes, triangular nose, short jaw marks, purple curled hood, gloves, badge and prop orientation. Its paper texture and cream, purple and lime frame connect it to the current lesson videos. The unapproved code-drawn recreation was not used.

The clean logo came from [Deep Six's own website](https://www.deepsixpest.com/wp-content/uploads/2026/02/Header_Logo.png). It and the exact sentence are fixed overlays. The logo source is only 172 x 100 pixels, so local scaling limits its sharpness. It was not generatively redrawn.

The mascot makes a very slight acknowledgement and settles. The source AI video introduced unwanted eye changes after its opening clean frames. The final edit uses only those clean frames, followed by their reverse and a still hold. Its motion is subtler than the original nod target. No talking or jaw animation. The original mascot artwork remains the identity authority; this adaptation awaits finished-outro approval.

Voice: Google `Sulafat`, generated with `gemini-3.8-flash-tts`, warm adult American English direction. Natural speed preserved. The fixed WAV has 0.16 seconds of leading silence removed, a 0.7 dB level reduction, and padding to 4.5 seconds. No music or sound effects. Voice preference remains part of Drew's finished-media review.

## Measured timing

The reusable master is **4.500 seconds**, 135 frames. The complete ending is **5.000 seconds**, 150 frames, including the separate half-second entry. Both MP4s are vertical **1080 x 1920 at 30 fps**, with 48 kHz audio. The mascot source was generated at 720 x 1280; local scaling does not add native detail.

Let T be the last audible teaching word. These timings include the entry; audible boundaries are approximate measurements at a -40 dB silence threshold.

| Time after T | Picture | Sound |
| --- | --- | --- |
| 0.000 to 0.200 s | Hold the final teaching image and caption, 6 frames. | Brief breath after the completed lesson. |
| 0.200 to 0.500 s | Reveal the cream outro with a left-to-right paper wipe, 9 frames. | No overlapping speech. |
| About 0.552 to 2.182 s | Logo, exact message and mascot readable. | Helping you understand pests. |
| About 2.182 to 2.615 s | Very slight mascot acknowledgement settles. | Natural sentence pause. |
| About 2.615 to 3.904 s | Hold the brand composition. | Deep Six Pest Control. |
| About 3.904 to 5.000 s | Readable final hold. | About 1.10 seconds of quiet. |

Mascot motion occupies master seconds 1.4 to 2.2, equivalent to T + 1.9 to T + 2.7. It is still afterward. Relative to the master, audible speech begins around 0.052 seconds and ends around 3.404 seconds. Actual sentence timing replaces the earlier unmeasured target; the voice was not sped up.

## Required lead-in and script presentation

Finish the lesson with a complete useful thought using established facts. Retain an ending that already does this. The closing sentence must stand on its own; no extra bridge sentence is required merely to introduce the brand.

Count existing trailing silence toward the half-second entry. Do not add it twice, cut a word, or hide the teaching caption before its sentence finishes. The standalone review uses a neutral cream outgoing plate. In an approved episode assembly, replace that plate with the episode's actual final teaching image. The master itself contains no lesson footage.

Every complete script shown to Drew must include the hook, full lesson, episode-specific close and the exact eight-word sign-off once as the final spoken paragraph. No placeholder or abbreviated repetition. Keep all editing cues outside the spoken text.

For audio, generate episode-specific speech separately and append the shared 4.5-second recording once. Do not generate a fresh sign-off from each full review script and then append it again. The writing stage can proceed now; freeze this voice/master for reuse only after Drew approves the finished media.

[Transition instructions](TRANSITION-INSTRUCTIONS.md) · [Narration return plan](NARRATION-HANDOFF.md).

## Actual asset paths

Paths are relative to the project root. All listed files exist.

| Asset | Path |
| --- | --- |
| Original mascot identity source | `01-content/brand/fun-fact-friday-spider.png` |
| Video palette | `01-content/animation/brand.json` |
| Accepted still for the motion test | `01-content/outro/assets/hybrid-still-v3.jpg` |
| Clean official logo, source pixels preserved | `01-content/outro/assets/deep-six-logo.png` |
| Fixed logo and screen-text overlay | `01-content/outro/assets/outro-wording-overlay-v1.svg` |
| Raw AI video, partly rejected | `01-content/outro/assets/mascot-motion-source-v1.mp4` |
| Shared recording with final hold | `01-content/outro/assets/outro-audio-v1.wav` |
| Reusable 4.5-second master | `01-content/outro/assets/outro-master-v1.mp4` |
| Caption file for the master | `01-content/outro/assets/outro-master-v1.srt` |
| Five-second review including neutral entry | `01-content/outro/assets/outro-review-v1.mp4` |
| Local assembly and wipe recipe | `01-content/outro/production/assemble-outro-v1.py` |

The identical review copy is on the Windows Desktop as **Deep Six - Reusable Outro v1.mp4**. No player was opened.

## Checks and remaining work

[Production review](production/REVIEW-V1.md) and [measured checks](production/final-checks-v1.json) record full decode, frame counts, exact text inputs, two speech-recognition checks, unclipped WAV, -2.3 dBFS final true peak, source preservation and matching Desktop checksum. Automated speech recognition is not a human voice audition.

1. Drew reviews and approves the finished voice, appearance and subtle movement, or requests a specific revision.
2. After approval, freeze these exact files for reuse. This session then creates the missing fire-ant educational close and assembles a separate final video, checking the actual join and perceived loudness.
3. The original narration chat handles its ten full script adaptations with the same final words and shared audio. Preserve originals. No automatic message to that chat.

Research supports clear attribution and purposeful endings. The selected words, wipe and timing are creative choices. No AEO/GEO ranking benefit or guarantee is claimed. [Research and sources](RESEARCH.md).
