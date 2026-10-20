# Free music for Deep Six shorts: research note, 20 Oct 2026

**Decision, 20 Oct 2026: Drew approved Test H, Warm Ambient, for both finished videos. See [APPROVED-MUSIC.md](APPROVED-MUSIC.md).**

**Takeaway:** Famous songs are out. A few free sources allow business use on all 4 apps from one pre-mixed file. Platform libraries do not travel between apps.

## Decisions so far (Drew, 20 Oct 2026)

- These shorts are organic posts, not ads. Neighborhood-targeted Facebook ads are a separate later job.
- Music must be free, and the agent gets it without Drew doing music work (Drew, 20 Oct).
- Copyrighted hit songs: not used. Reasons below.

## Why hit songs are out

- Posts from a company account count as commercial use. A court found Bang Energy's social posts with song clips commercial and not fair use. [Copyright Office summary](https://www.copyright.gov/fair-use/summaries/Sony-Music-Entmt-v-Vital-Pharms-Inc-21-22825-CIV-SD-Fla-2022.pdf)
- TikTok's in-app library did not protect Bang. [Nixon Peabody](https://nixonpeabody.com/insights/articles/2022/07/20/tiktok-song-library-does-not-shelter-brands-and-influencers-from-copyright-infringement)
- Warner sought up to $150,000 per song. [GDN report](https://www.gdnonline.com/Details/1142856/Warner-Music-sues-Bang-Energy-in-latest-TikTok-advertising-lawsuit)
- Business accounts on TikTok are limited to the Commercial Music Library. [Social Media Today](https://www.socialmediatoday.com/news/tiktok-changes-rules-on-music-usage-by-businesses/577734/)
- Music is mixed into the same audio track as the narrator. A mute for detected music would silence the narrator too.

## Free sources that can work on all 4 apps

| Source | Business use | Credit needed | Catch |
| --- | --- | --- | --- |
| Pixabay Music | Yes, per its content license | No | Mixed quality. Some tracks get false YouTube claims; keep the license file and dispute. |
| Mixkit | Yes. License read 20 Oct: commercial, social media posts and online ads allowed | No | Smaller library. No remixing into music-only tracks, no Content ID registration, no scripted mass downloads. [License copy](library/mixkit/LICENSE-mixkit-stock-music-free.txt) |
| Creative Commons BY tracks (Kevin MacLeod, YouTube Audio Library CC tracks, Free Music Archive CC BY) | Yes | Yes, in every post | Credit line each post. Kevin MacLeod tracks are very recognizable. Never use "NC" tracks. |
| Original track made in FL Studio | Yes, Deep Six owns it | No | Someone has to make it. Bundled FL sounds are royalty-free for commercial productions. |
| AI music through KIE | Unverified | Unverified | Uses already-bought credits, so still spending. Ownership rules unclear. |

Sources: [Pixabay license summary](https://pixabay.com/service/license-summary/) (free use, no attribution, user must check third-party rights) · [HeyGen on clearing Pixabay claims](https://help.heygen.com/en/articles/8986144-how-to-remove-your-content-id-claim-in-youtube) · [YouTube Audio Library help](https://support.google.com/youtube/answer/3376882) (CC tracks need credit; YouTube gives no guidance on off-platform use) · [Incompetech licenses](https://incompetech.com/music/royalty-free/licenses/) · [Image-Line knowledge base](https://support.image-line.com/action/knowledgebase?ans=717)

## Free sources that do not fit

- **Uppbeat free plan:** individuals only. Business use needs a paid plan. [Uppbeat help center](https://fastly-f.uppbeat.io/help-center)
- **StreamBeats:** aimed at streamers. No clear business license found.
- **Each app's own library:** TikTok and Meta libraries are cleared on their own app only. They do not travel to the other apps. Standard YouTube Audio Library tracks: off-YouTube use is unclear. [Osborne Clarke](https://www.osborneclarke.com/insights/use-music-social-media-platforms-what-businesses-and-creators-need-know-about-usage)
- **Later, for Meta-only ads:** Meta Sound Collection is described as cleared for commercial use on Facebook and Instagram. Secondary sources only; read Meta's terms before use.

## Still open

- Learning effect of music under narration, loudness and ducking, signature track or per-pest mood, music under the outro. Not researched yet.
- Local measurement: the approved fire-ant final measures -25.5 LUFS integrated, -3.2 dBFS true peak, mono. Typical platform level is near -14 LUFS (to verify).

## Tests made, 20 Oct 2026 (free, no paid calls)

- Pixabay blocks scripted downloads (HTTP 403). Mixkit allows direct downloads.
- 8 Mixkit tracks downloaded to `library/mixkit/` with [track list](library/mixkit/tracks.json). Offline speech check found no sung lyrics in the 4 checked.
- Three previews under the approved fire-ant final, on Drew's Desktop as `Deep Six - Music Test A/B/C`:

| Test | Track | Why picked |
| --- | --- | --- |
| A Curious Cello | "The Snail", Eugenio Mininni (Mixkit 602) | Plucked, curious, storybook feel |
| B Chill Lo-Fi | "Sweet September", Arulo (Mixkit 282) | Least energy in the voice range of all 8 |
| C Bright Pop | "Pop Track 03", Lily J (Mixkit 729) | Upbeat, positive |

- Mix: [tools/mix_preview.py](tools/mix_preview.py). Narration untouched. Music evened out, set 15 LU under the narration, ducked by the voice (sidechain, ratio 3), faded out over the last 1.2 s. Picture stream copied. [Mix log](previews/mix-log.jsonl).
- Checked: 88.1 s out, 1080x1920 H.264 copied, AAC stereo. Music measures about -38 to -42 dB RMS in pauses versus about -27 dB RMS for speech.
- Louder set A2, B2, C2 (Drew said "idk"; agent chose Zack D. levels): narration alone raised to -14 LUFS by two-pass loudnorm, music 10 LU under, ducking threshold tied to the voice level, limiter, true peak -1.1 to -1.6. Result -14.9 LUFS. On the Desktop as `Deep Six - Music Test A2/B2/C2 (louder)`. [Mix log](previews/mix-log-v2.jsonl). [Zack D. comparison](zack-d-films-reference.md).
- **Drew rejected all six tests (A, B, C, A2, B2, C2) on 20 Oct: "i dont any of them".** Curious cello, chill lo-fi and bright pop are out as styles.
- **Drew chose direction 1, tense and mysterious like Zack D. (20 Oct).** Six more Mixkit tracks downloaded one at a time and checked. "Fallen (Asper)" (565) and "A Voice from The Past" (548) dropped: the speech checker heard words or humming in them. Likely false alarms, but not worth the risk under a narrator.

| Test | Track | Feel | Quiet moments vs speech |
| --- | --- | --- | --- |
| D Dark Pulse | "Torn Threads", Ahjay Stelino (Mixkit 73) | Eerie electronic, about 72 bpm | -15.3 dB |
| E Mystery Piano | "Pianinni", Alejandro Magana (Mixkit 165) | Mysterious piano over a beat, about 81 bpm | -14.7 dB |
| F Stealth Guitar | "Vertigo", Eugenio Mininni (Mixkit 597) | Investigation guitar, about 63 bpm, dynamic so set 8 LU under | -16.2 dB |

  All three: -14.8 to -14.9 LUFS, true peak -1.1 to -1.6, 88.1 s, picture bit-identical to the approved video. On the Desktop as `Deep Six - Music Test D/E/F`. [Mix log](previews/mix-log-tense.jsonl). [Full tense catalog, 143 tracks](library/mixkit/catalog-tense.json).
- **Drew rejected D, E and F on 20 Oct: "they all sound weird".** Six tracks rejected in total. The agent cannot hear audio and picks by tags and measurements only.
- Possible mix causes to rule out before more picks: the voice ducking pumps the music up in every short pause (release 500 ms, pauses 0.3 to 0.6 s); the slow leveler can lift quiet passages up to 20 dB; the voice loudness step may run in dynamic mode. Possible style cause: suspense music over a cute cut-paper look.
- Not yet decided: music level, music under the outro, one signature track or a mood per pest, and final loudness. The finished fire-ant mix is about -25.5 LUFS, quieter than typical platform level.

## Custom AI music, made locally (20 Oct 2026)

- Drew: stock songs sound cheap, and the music "isn't stable, it sounds random".
- Measured: the old ducking roughly doubled the music's quick level jumps (Mixkit 73: 34 to 82; Mixkit 165: 55 to 105). New mixes use `--steady`: one constant music level, no leveler, no ducking.
- Generator: ACE-Step 1.5, installed at `/home/drewp/tools/ACE-Step-1.5`, outside the repo. MIT license; the model card says generated music may be used commercially. Runs on the RTX 4060 laptop GPU, 8 GB, with memory saving on. Free; no paid calls. [Model card](https://huggingface.co/ACE-Step/Ace-Step1.5) · [GitHub](https://github.com/ace-step/ACE-Step-1.5)
- Purely AI-made music likely has no copyright owner, so others could reuse it. It also cannot go into Content ID.
- Prompts: [steady suspense](prompts/2026-10-20-steady-suspense.json). Tools: [ace_generate.py](tools/ace_generate.py), [score_steadiness.py](tools/score_steadiness.py).
- Rejected stock tracks scored 3.3 to 9.7 dB on 3 s level spread. Two steady ones were still rejected, so steadiness alone does not decide.
- First 3 of 8 generated: steady-pulse seed 1000 passed (2.7 dB spread, 15.6 dB voice room, no speech). Seed 1018 (11.8 dB, 6 section changes) and mystery-piano seed 1002 (16.1 dB) failed.
- Test G: steady-pulse seed 1000, `--steady --under 12 --target -14 --tp -2`, under both approved videos. Fire ants: -14.7 LUFS, true peak -1.6. Wasp: -14.2 LUFS, true peak -1.6. Pictures bit-identical. Wasp source: `animation/episodes/D6-01096ba333e3/full/renders/ensign-wasp-v3-final.mp4` (approved, 49.07 s, -23.9 LUFS).

- **Drew rejected Test G on 20 Oct: "no" to "right kind of music?".** Seven tracks rejected so far. Drew on G: "it sounds annoying". The agent cannot hear audio, so picking blind is not converging. Next: get a reference from Drew.

- Drew on G, asked what is annoying: "1", the sound itself (ticking, beat). Stopped the drum-heavy batch after 4 of 8.
- Beatless batch: [prompts](prompts/2026-10-20-smooth-no-beat.json). Writing "no drums" did not stop drums: the warm-strings take scored 0.53 percussive, as high as Test G. Next prompts should describe only wanted sounds and never name drums.
- New checks in the scorer: percussive ratio (median-filter split; pure pad 0.001, pure tick 0.39, Test G 0.51) and sharp hits per second. The regular-pulse number is unreliable: a pure pad scored 0.94.
- Passed: ambient-warm seed 1002 (percussive 0.14, 3 s spread 6.8 dB, voice room 21.1 dB; fades out by about 84 s) and orchestral-wonder seed 1003 (percussive 0.03, but spread 11.7 dB with dips at 54 s and 66 s, so mixed with the slow leveler and no ducking).
- Tests H (Warm Ambient) and I (Soft Orchestra), under both videos: -14.2 to -14.7 LUFS, true peak -1.4 to -1.8, pictures bit-identical. Desktop: `Deep Six - Music Test H/I - Wasp` and `- Fire Ants`. [Mix log](previews/mix-log-smooth.jsonl).

## How it plugs into the video flow (draft)

Music is one last step after the other session's finished MP4: finished MP4 plus chosen track in, new MP4 out. Picture and narration stay untouched, so no file of the MP3-to-MP4 flow changes.
