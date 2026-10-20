## Recommendation: "Spot It, Launch It" (universal outro)

This is one outro reused for every pest lesson. The lesson's final picture slides away and reveals the reaper crouched behind a layered cream-paper fold, peering through its green lens. It notices us, springs to full height and swings the magnifier up in a wide arc. The genuine Deep Six logo is already visible, magnified, inside the lens. When the lens stops hard, the logo emerges through the glass and lands at full size above the reaper. The magnifier is the "helping you understand" tool, and the last thing it finds is the brand.

The video model never generates the line "Helping you understand pests. Deep Six Pest Control." That line is the last part of each video's complete narration, read in that video's own voice. For Fire Ants Full v2, the voice is Tyler. There is no universal brand-voice file. The fire-ant closer itself remains a later task.

## Beat table

The anchor is the onset of the spoken word "Deep." Total length is 5 to 6s, and the settled hold flexes to fit the actual narration.

| Time | Action | Overlay | Speech |
|---|---|---|---|
| 0.0-0.3 | The lesson's final picture slides down and out, uncovering the crouched reaper behind the paper fold | none | lesson ends |
| 0.3-1.0 | Small lens scan. Head snaps up to the viewer, knees bend, shoulders drop | caption "Helping you understand pests." | "Helping you understand..." |
| 1.0-2.0 | Springs to full height, robe flares, magnifier arcs from low to high-left, flashlight drops to the hip | logo fades in inside the lens matte for the last 0.4s | "...pests." |
| 2.0 | Lens stops hard | logo begins emerging through the glass | pause |
| 2.0-2.5 | Follow-through begins | logo rises to top center, grows to full size, overshoots 3% once, lands | lands at or before "Deep" |
| 2.5-4.0 | Arm settles, head tilts toward the logo, chest lifts | caption removed, logo holds | "Deep Six Pest Control." |
| 4.0-end | Settled hold with slight robe sway | logo stays readable | about 0.8s tail |

The camera stays locked. An optional 3% push-in in post can support the rise but never replaces the body motion.

## Prompts

- **Reference A:** `fun-fact-friday-spider.png`, for character identity only.
- **Reference B:** a crop from a lesson render that shows only cream paper layers and edges, with no pests and no captions. Use it for style and palette only.

**Beginning frame (Nano Banana 2.1, role: first frame)**

> Vertical 9:16 illustration in the exact matte cut-paper style and palette of Reference B: layered paper shapes, soft paper grain, flat color, gentle offset paper shadows, no gloss, no 3D rendering. Colors: cream #F6EFE2, purple #3A3148, lime #A9D554, ink #1E1B22. Character: the reaper mascot from Reference A, identical identity. Curled purple hood with the tip curling toward viewer-right. White skull with solid black oval eyes (no pupils, no highlights), a small triangular nose and short vertical jaw marks exactly as in Reference A. White gloves. Small chest shield reading "D6" with a downward arrow, exactly as in Reference A. The viewer-left glove holds a round black-rimmed magnifier with a green-tinted lens. The viewer-right glove holds a black flashlight. Pose: crouched low, right of center, head lowered, the magnifier held low near the fold and the flashlight pointing down. The bottom 25% of the frame is a layered cream-paper foreground fold that covers the lower robe. There are no animals, insects, soil, plants or scenery. The top 35% is plain cream. Apart from the existing D6 chest shield, no text, logos or words.

**Ending frame (Nano Banana 2.1 edit of the approved beginning frame, role: last frame)**

> Same image, character, style and paper fold. The reaper now stands at full height behind the fold, visible from mid-robe up, right of center. The viewer-left arm reaches up and out, holding the magnifier high at about 35% from the top and 35% from the left, lens facing the viewer and empty. The flashlight hand rests at the hip with the beam pointing down. The head tilts slightly toward the upper-left. The face is unchanged: solid black oval eyes with no pupils or highlights, triangular nose, short jaw marks, mouth closed. The top 30% stays plain cream. Apart from the existing D6 chest shield, no text, logos or words.

**Portrait video (Gemini Omni 1.1 Flash image-to-video, single clip, first frame = beginning frame, last frame = ending frame)**

> Matte cut-paper animation that matches the first frame, locked camera. All action happens in the first 4 seconds, then the final pose holds with only gentle robe sway. First, the crouched reaper sweeps the magnifier slightly, then snaps its head up to look at the viewer, bending its knees and dropping its shoulders. Next, it springs up to full height in one strong motion. The robe flares and the hood tip whips. The viewer-left arm swings the magnifier in a wide continuous arc from low to high upper-left and stops it firmly. The flashlight swings down to the hip. Then follow-through: the arm settles slightly, the head tilts toward the upper-left and the chest lifts proudly. The body and arm must clearly move; do not rely on camera motion. The face stays exactly as in the first frame: solid black eyes with no pupils or highlights, triangular nose, short jaw marks, jaw closed and still, no speaking. Props never change hands. The lens stays empty. The upper third stays plain cream. Apart from the existing D6 chest shield, no text or logos. No particles, sparkles or glossy lighting. No audio or speech.

The beat timing in this prompt is a generation target, not a guarantee. Do not assume an exact-duration option. Use the length the model returns, then trim or extend the hold.

## Compositing and sync

- **Logo source.** This is a source limitation, not a blocker for concept work. Cut the larger logo from the supplied original ad using its existing pixels only, with no redraw, tracing or generative cleanup. Compare it against the genuine official file: letterforms, shapes, colors and proportions. If any of it differs, use the official file. Request the vector or print master from Deep Six in parallel. Choose the landed size for readability and accept honest softness if the source is small. Upscaling adds no detail.
- **Assembly.** Confirm the source clip really is 720x1280. Scale it 1.5x to 1080x1920 and conform to 30fps without motion interpolation. Composite the logo and caption as separate overlays.
- **Reveal.** Track the lens rim and matte the logo inside it at reduced scale, with a light multiply of the green tint. It may be visible during the swing but stays inside the matte. On the stop frame, release it outward through the glass. It rises to top center and grows to its final size over about 0.5s, overshoots once, settles, and then gains a 25% ink shadow.
- **Masters.** After spending approval, export an animation-only reusable master: 1080x1920 at 30fps, no audio, no caption, with the logo animation plus a clean no-logo version, and the lens-stop frame marked. For the Fire Ants review, generate the full narration in Tyler's voice, ending with the sign-off. Place the master so the logo lands at or before "Deep." Trim the entry or extend the settled hold as needed, and never retime speech or character action.

## Reject criteria

1. **Weak motion.** There is no crouch-to-full-height, the magnifier arc is short or hesitant, or the camera does the work instead of the body.
2. **Identity drift.** The eyes gain pupils or highlights, the nose or jaw marks change, the hood flips, props swap hands, the shield changes, or the jaw moves.
3. **Scope or style break.** Pest or ground imagery appears, the model generates any text or logo other than the canonical shield, or there is gloss, 3D shading or particles.
4. **Reveal or sync failure.** The logo leaves the lens or lands before the stop, is not landed by "Deep," is unreadable, differs from the official file, or the speech differs from the exact line or the video's own narration voice.
