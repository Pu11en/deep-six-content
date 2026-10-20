# Outro v1 is ready for Drew's review

**Historical result: Drew rejected this version.** Its separate Sulafat voice and almost still mascot motion must not be used in future episodes. Follow the corrected [current specification](../APPROVED-OUTRO.md).

The five-second MP4 contains the selected line, real website logo, source-ad mascot, paper reveal and a quiet final hold. Finished-media approval is still pending.

## Review files

- [Five-second review](../assets/outro-review-v1.mp4), also copied to `/mnt/c/Users/drewp/Desktop/Deep Six - Reusable Outro v1.mp4`. No player was opened.
- [Reusable 4.5-second master](../assets/outro-master-v1.mp4).
- [Shared 4.5-second recording](../assets/outro-audio-v1.wav), including its final silence.
- [Caption file](../assets/outro-master-v1.srt).

Exact spoken line: **Helping you understand pests. Deep Six Pest Control.** Voice: Google Sulafat. Natural recording speed retained; no music or sound effects.

## What was checked

- Master: 1080 x 1920, 30 fps, 135 frames, 4.500 seconds. Review: 150 frames, 5.000 seconds. Both contain 48 kHz audio.
- Two offline speech recognizers detected the complete line and no extra words. Both spell the spoken company name as `Deep6`; their inferred punctuation differs. These checks do not replace Drew's voice audition.
- Review voice begins around 0.552 seconds and finishes around 3.904 seconds. About 1.10 seconds of quiet hold remains. True peak is -2.3 dBFS; integrated loudness is -17.7 LUFS. Decode check passed; the WAV has no clipped samples.
- Desktop and project review copies have identical SHA-256 hashes. Original brand files, ten narrations and fire-ant MP4 match their initial hashes. The animation session's status note had changed externally earlier; this session did not edit it.

## Brand choices and limits

The source-only third still restored the original pose, face and badge. The second still correction was rejected. Both remain saved for provenance.

The ten-second AI video added blinking and white pupils after its first 32 frames. Those later frames are excluded. The master uses a very subtle acknowledgement from the clean section, followed by the same motion reversed and a still hold. This is quieter movement than the original larger nod target. [Used-motion check](finished-motion-check-v1.png), [full source review](motion-face-contact-v1.jpg), [edit recipe](assembly-v1.json).

The [official website logo](https://www.deepsixpest.com/wp-content/uploads/2026/02/Header_Logo.png) is a genuine transparent 172 x 100 source. It is scaled locally without generative redrawing; its small source size limits sharpness. The mascot video was generated at 720 x 1280 and scaled into the 1080 x 1920 composition. No claim of added native detail.

The review begins on neutral cream. Its half-second entry shows the timing without using the fire-ant lesson. After finished-outro approval, the final teaching frame will supply that outgoing picture.

## Cost and next step

Estimated additional API cost: **$1.136070 of the approved $2.00**. Two image calls, one video call, one voice call. Earlier image test: $0.058155. Estimated project total: **$1.194225**. Usage-based estimates, not an invoice; no credits bought and nothing published.

Receipts: [image correction](image-correction-v2.json), [source-faithful still](image-correction-v3.json), [video](video-generation-v1.json), [voice](voice-generation-v1.json), [final checks](final-checks-v1.json). Rates were checked against [Google pricing](https://ai.google.dev/gemini-api/docs/pricing).

Drew reviews the voice, appearance and movement first. Only after his finished-outro approval may this session produce the missing educational close and assemble a separate final version of **Deep Six Fire Ants Full v2**. The narration chat still owns the ten full script adaptations.
