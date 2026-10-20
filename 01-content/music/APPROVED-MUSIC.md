# Approved music: Warm Ambient (20 Oct 2026)

**Drew picked Test H, Warm Ambient, for both finished videos: "1 on both is closer ... for now, that's fine." Future episodes should aim for better music; this is the current default, not the final sound.**

## The track

- File: [library/ace-step/2026-10-20-smooth-no-beat/ambient-warm-seed1002.wav](library/ace-step/2026-10-20-smooth-no-beat/ambient-warm-seed1002.wav), 95 s, 48 kHz stereo. SHA-256 `8a7d0ccce92850652aaaa49b4be4d488034665f0842e25832d22771afebe77fd`.
- Made free on this PC with ACE-Step 1.5 (MIT license; model card: generated music may be used commercially). Prompt "ambient-warm" in [prompts/2026-10-20-smooth-no-beat.json](prompts/2026-10-20-smooth-no-beat.json), seed 1002. Settings in its [generation log](library/ace-step/2026-10-20-smooth-no-beat/generation-log.json).
- Sound: warm low drone, slow soft pads, faint shimmer. No beat. Percussive share 0.14, 3 s level spread 6.8 dB.
- Limits: it fades out by about 84 s, so a video longer than about 84 s has a quiet end card. The mixer refuses videos longer than 95 s; looping is not built. Purely AI-made music likely has no copyright owner, so others could reuse it, and it cannot go into Content ID.

## What Drew rejected, so future picks avoid it

Stock tracks from Mixkit (cheap, "weird", "random"), anything with a beat or ticking ("annoying"), and music that ducks under the voice and swells in pauses. Details: [free-music-sources.md](free-music-sources.md).

## Mix settings

Narration alone raised to -14 LUFS (two-pass loudnorm). Music at one constant level 12 LU under the narration: no ducking, no leveler. Limiter at -2 dBFS. Fade-out over the last 1.2 s. Picture stream copied untouched.

## Approved finals

| Video | Clean final with music | SHA-256 | Loudness |
| --- | --- | --- | --- |
| Fire ants, 88.10 s | [previews/fire-ants-music-H-warm-ambient.mp4](previews/fire-ants-music-H-warm-ambient.mp4) | 317759c3f314a6839553998f61823f4a2fd165262d8761e639bbf1540f2e2294 | -14.7 LUFS, true peak -1.6 |
| Ensign wasp, 49.07 s | [previews/ensign-wasp-music-H-warm-ambient.mp4](previews/ensign-wasp-music-H-warm-ambient.mp4) | 07ce2c45c8c42f8ea6a9d93ac65a31a9da93b69323c3bc765a74ac123f71a706 | -14.3 LUFS, true peak -1.7 |

Sources: `outro/assets/deep-six-fire-ants-full-v2-with-outro.mp4` and `animation/episodes/D6-01096ba333e3/full/renders/ensign-wasp-v3-final.mp4`. Their pictures are bit-identical in the music versions. Desktop: `Deep Six - Fire Ants - FINAL clean.mp4` and `Deep Six - Ensign Wasp - FINAL clean.mp4`. Watermarked client copies: [../watermark/README.md](../watermark/README.md).

## How it plugs into the video flow

Music is one step after the MP3-to-MP4 flow has its approved, finished MP4 (with outro). It changes no file of that flow.

1. Take the approved finished MP4.
2. Add music and set loudness:
   ```
   python3 01-content/music/tools/mix_preview.py FINISHED.mp4 \
     01-content/music/library/ace-step/2026-10-20-smooth-no-beat/ambient-warm-seed1002.wav \
     FINAL-WITH-MUSIC.mp4 --under 12 --target -14 --tp -2.0 --steady
   ```
3. Check: same duration as the input, picture stream identical, about -14.5 LUFS, true peak under -1.
4. For the client preview, watermark the music version: `01-content/watermark/watermark.sh FINAL-WITH-MUSIC.mp4 PREVIEW.mp4`.
5. Copy both to Drew's Desktop. Never open a player.

Making new music: [tools/ace_generate.py](tools/ace_generate.py) (ACE-Step installed at `/home/drewp/tools/ACE-Step-1.5`, outside the repo) and [tools/score_steadiness.py](tools/score_steadiness.py). Describe only the wanted sounds; writing "no drums" produced drums.
