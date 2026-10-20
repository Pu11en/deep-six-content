# Runner Test Ensign Wasp video (d6-01096ba333e3-replay): Stopped

**Step: deliver.**

- Episode D6-01096ba333e3; MP3 `../audio/D6-01096ba333e3/full-chris-01/ensign-wasp-chris.mp3` (48.4 s); start: later, recorded 2026-10-20T04:08.
- Segments: seg01 0.0-44.1 s done by claude-opus-5-5.
- Render video v1: failed (stopped near frame 601 of 1472 (crash test: worker and render killed on purpose)).
- Render video v2: done.
- Delivered v1: Desktop `Deep Six - Runner Test Ensign Wasp v1.mp4`, checksum verified, no player opened. Made by: seg01 claude-opus-5-5.
- File checks: lesson still 0.233 s, change 22%, outro difference 1.83, audio pass.
- Whole-video reviewer: 1 note(s) sent back. Checked all 9 filmstrips plus 54 single-frame renders. In every frame checked, the caption highlights the word being said. Every planned beat shows on its word. Motion, holds and cuts are fine. Wasp, larva, pupa, cockroach and egg-case anatomy matches science-notes.md. The episode limits are kept: only the American cockroach is shown, no treatment advice, and no wasp-means-infestation link. The ending is right: the last teaching picture stays readable through 'roaches.' (44.13 s), then the cream wipe plays, and the logo lands at 46.87 s, before 'Deep' at 46.91 s. One fix: the egg cases are too small on 'look for egg cases' (I2). Small things left alone: the flashlight hand sits below the caption, and the pennant is clipped at the right edge for a few frames near 6.0 s. Context: replay-compare.json says this render is frame-for-frame identical to the approved ensign-wasp-v3-final.mp4, so the I2 shot is also in the version Drew approved, and Drew may choose to keep it.

Commands (from `01-content/animation`):

    python3 make_video.py status --run d6-01096ba333e3-replay
