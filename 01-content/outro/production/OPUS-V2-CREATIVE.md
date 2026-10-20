I viewed both images. The ad's logo looks like an AI-composited reproduction, so check it against the official file before using it (see step 4).

## Recommendation: "Spot It, Launch It"

### 1. Pitch

The reaper crouches at the edge of the anthill, peering at the soil through its green lens. It notices us, snaps its head up and springs to full height in one big motion that flares the robe. The magnifier swings up in a wide arc and stops hard. The Deep Six logo, seen magnified inside the lens, flies out of it and lands as a cut-paper piece above the reaper. The magnifier is the mascot's "helping you understand" tool: it finds things for us, and the last thing it finds is the brand.

### 2. Beat table

The onset of the spoken word "Deep" anchors the lens stop at about 2.4s.

| Time | Camera | Action | Logo / message | Speech |
|---|---|---|---|---|
| 0.0-0.3 | Locked, vertical medium-wide | The lesson's last soil layer slides down out of frame, uncovering the reaper crouched behind a soil ridge with its lens to the ground | Upper third is empty cream | Lesson narration flows on |
| 0.3-1.2 | Locked | One small lens scan. Head snaps up to the viewer, knees bend, shoulders drop | None | "Helping you understand pests." |
| 1.2-2.4 | 3% push-in added in post | Springs to full height, robe flares. Magnifier arm swings from low-left to high-left in one arc. Flashlight hand drops to the hip, beam pointing down | Logo appears inside the lens for the last 0.4s of the swing | Ends on "pests." |
| 2.4 | Locked | Lens stops hard, held high | Logo flies up out of the lens toward top center | "Deep Six" |
| 2.4-3.4 | Locked | Follow-through: arm settles about 5 degrees, head tilts toward the logo, chest lifts | Logo lands with one 3% paper overshoot, then a matte shadow appears | "Pest Control." |
| 3.4-end | Locked | Proud hold, robe sways slightly | Logo stays put | Silent hold until 5.5-6.0s |

### 3. Prompts

**Start still (Nano Banana 2.1).** Reference A is `fun-fact-friday-spider.png`, used for character identity only. Reference B is one cropped soil panel from the Fire Ants render with no caption strip, used for style and palette only. Cropping out the captions keeps the model from copying text.

> Vertical 9:16 illustration in the exact matte cut-paper style and palette of Reference B: layered paper shapes, soft paper grain, flat color, gentle offset paper shadows, no gloss, no 3D rendering. Colors: cream #F6EFE2 background, purple #3A3148, lime #A9D554, ink #1E1B22, warm soil browns. Character: the reaper mascot from Reference A, identical identity. Curled purple hood whose tip curls toward viewer-right. White skull with solid black oval eyes (no pupils, no highlights), a small triangular nose and three short vertical jaw marks. White gloves. Small shield on the chest reading "D6" with a downward arrow, exactly as in Reference A. Viewer-left glove holds a round magnifier with a black rim and a green-tinted lens. Viewer-right glove holds a black flashlight. Pose: crouched low, right of center, head lowered, the magnifier held close to the soil and the flashlight pointing down at it. A cut-paper soil ridge with a small anthill and a few ants fills the bottom 25% of the frame and covers the reaper's lower robe. The top 35% of the frame is plain cream with nothing in it. No text, no logo, no words anywhere.

**Matched end still (Nano Banana 2.1 edit of the approved start still).**

> Same image, same character, same style. The reaper now stands at full height behind the ridge, visible from mid-robe up, right of center. The viewer-left arm reaches up and out so the magnifier is held high at about 35% from the top and 35% from the left, with the lens facing the viewer. The flashlight hand rests at the hip with the beam pointing down. The head tilts slightly up toward the upper-left. The face is unchanged: solid black oval eyes, no pupils, mouth closed. The top 30% of the frame stays empty cream. No text.

**Video (Gemini Omni 1.1 Flash, portrait image-to-video).** First frame is the approved start still. Last frame is the approved end still.

> Matte cut-paper animation that keeps the style of the first frame, locked camera. All action happens within the first 4 seconds, then the end pose holds with only gentle robe sway. 0-1s: the crouched reaper sweeps the magnifier slowly across the soil, then lifts its head sharply to look at the viewer. Its knees bend and its shoulders drop as it gathers energy. 1-2.5s: it springs up to full height in one strong motion. The robe flares outward and the hood tip whips. The viewer-left arm swings the magnifier up in a wide continuous arc from near the soil to high upper-left and stops it firmly. The flashlight swings down to the hip, beam still pointing down. 2.5-4s: follow-through. The arm settles slightly, the head tilts toward the upper-left and the chest lifts proudly. Then hold. The skull face stays exactly as in the first frame: solid black eyes with no pupils, no highlights, no eyebrows, and the jaw closed and still (no speaking). Props stay in the same hands the whole time. The upper third stays plain cream. No text, no logo, no particles, no sparkles, no glossy lighting.

### 4. Compositing and transition

- **Logo source.** First ask Deep Six for the original vector or print master. That is the only real sharpness fix. Until it arrives, cut out the roughly 450px ad logo using the existing pixels only, with no repainting and no tracing. Compare it letter by letter with the official 172x100 file and reject it if anything differs.
- **Scale rule.** Never show the logo above 1:1. Inside the lens it appears at native 1.0. At rest it settles at 0.89 (about 400px wide on the 1080 canvas), so the "magnified" moment never needs upscaling. If a vector arrives, rest it at about 640px.
- **Assembly.** Upscale the Omni 720x1280 clip 1.5x to 1080x1920 at 30fps. This is a format change and adds no detail. Composite the logo on top afterward.
- **Making the swing cause the reveal.** Track the lens rim and use a circular matte so the logo shows only inside the lens, with a light multiply of the lens's green tint. On the frame where the lens stops, release the logo from the matte. It travels up and to the right to top center, eases out over 0.6s, overshoots by 3%, and settles once. Then fade in a 6px ink shadow at 25% opacity.
- **Transition in.** Slide the lesson's final soil layer down out of frame over 6 frames to uncover the outro's first frame. Reference B keeps the palette continuous.
- **Captions.** In the lesson's caption-strip style, place "Helping you understand pests." under the logo zone. Remove the strip when the logo lands, so the logo itself carries "Deep Six Pest Control." There is no other text.
- **Sync.** Using the episode's word timings, slide the clip so the lens stops on the start of the spoken "Deep." Trim the opening crouch or stretch the end hold to fit. Never change the speed of the speech or the character.

### 5. Reject conditions

1. **Weak motion:** the reaper doesn't go from crouch to full height, or the lens doesn't travel at least 40% of the frame height in one committed arc.
2. **Identity drift:** pupils, eye highlights or a changed eye shape; a missing nose or jaw marks; the hood curling toward viewer-left; props swapping hands; a wrong badge; or any jaw movement that reads as speaking.
3. **Style break:** glossy or 3D shading, rendered lighting, particles, or any text or logo generated by the model.
4. **Reveal or sync failure:** the logo appears before the lens stops or isn't attached to the lens, the logo is shown above native scale, or the spoken words differ from "Helping you understand pests. Deep Six Pest Control."
