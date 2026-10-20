# Zack D. Films music: reference check, 20 Oct 2026

**Takeaway:** Zack D. Films uses its own commissioned music, picked by mood per video. Music sits about 9 to 12 dB under the voice, and the videos are very loud overall.

## What they do

- They hired freelance composers for original background music for 30 to 90 second animated shorts on YouTube Shorts, TikTok and Instagram. They kept full ownership and licensing rights, with Content ID tagging. Moods listed: suspenseful, mysterious, quirky, historical, feel-good, fast-paced action. Source: Zack D. Films job post, [recruitee listing](https://zackdfilms.recruitee.com/o/music-composer) (404 on 20 Oct; wording from the search engine's copy).
- So: a music library with a mood per video, not one theme for every episode.

## Measured, 4 shorts posted 19 Oct 2026 (audio only, local analysis)

Method: 50 ms loudness frames, skipping the first and last 0.5 s. "Speech" is the 80th percentile frame. "Quiet moments" is the 15th percentile frame: the gaps between words, where only music and sound effects play. Check: the approved fire-ant video with no music reads -35.5 dB here, so the method does see the music floor. A first method (gaps from speech timing) was wrong: it read -11 dB even on the no-music video, so those numbers were dropped.

| Short | Length | Loudness | Quiet moments vs speech |
| --- | --- | --- | --- |
| Why A Giant T Makes You Look Better | 31 s | -10.0 LUFS | -12.2 dB |
| The Titanic Orphans Reunited With Their Mother | 47 s | -11.1 LUFS | -13.5 dB |
| How Plato's Alarm Clock Worked | 30 s | -10.1 LUFS | -12.4 dB |
| She Kept Getting Flowers From Her Dead Father | 37 s | -13.1 LUFS | -16.2 dB |

Narration starts at 0.00 s in all four. Their quiet moments include sound effects, so their music alone may sit a little lower.

## Compared with Deep Six tests (same method)

| File | Loudness | Quiet moments vs speech |
| --- | --- | --- |
| Approved fire-ant final, no music | -25.5 LUFS (mono) | -35.5 dB |
| Tests A, B, C (voice untouched, music 15 LU under) | about -22.6 LUFS (stereo) | -18.5, -18.3, -16.2 dB |
| Tests A2, B2, C2 (voice raised to -14, music 10 LU under, ducking tied to voice level) | -14.9 LUFS, true peak -1.1 to -1.6 | -16.1, -16.0, -13.9 dB |

- A2, B2 and C2 are in Zack D. range for both loudness and music level. Picture stream is bit-identical to the approved video.
- The audio was downloaded to `/tmp` for measurement only. Nothing from it is reused.
