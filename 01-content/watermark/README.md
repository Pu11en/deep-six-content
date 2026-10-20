# The Aldus watermark for client previews

**Takeaway:** Every Deep Six video sent to the client before he pays gets The Aldus logo tiled across the whole frame. Keep the clean copy for final delivery.

- Drew asked for it on 20 Oct 2026 so the client cannot take the video.
- Logo: The Aldus locked mark (blue tile, gold border, cream dolphin and anchor) from `/home/drewp/main-projects/thealdus/site/assets/aldus-icon-512.png`, plus the "The Aldus" wordmark from `aldus-lockup-light.svg` in the same folder. The `brand/logo-final/` folder named in the Aldus notes is not on this machine; the website files were used.
- Look: icon plus wordmark, white with a soft dark shadow, repeated on a -28 degree diagonal over the full 1080x1920 frame at 36% opacity. Reads on both cream and dark scenes.
- Files: [overlay](watermark-1080x1920.png), [tile parts](unit.png), [frame check](frames-check.png).
- Run: `01-content/watermark/watermark.sh IN.mp4 OUT.mp4`. Audio is copied. Picture is re-encoded once (x264 CRF 18), so always watermark from the clean master, never from a watermarked copy.
- Limit: a tiled watermark discourages reuse; it does not make copying impossible.

## Made 20 Oct 2026

| Video | Watermarked file | SHA-256 |
| --- | --- | --- |
| Ensign wasp, 49.07 s | [renders/ensign-wasp-final-music-watermarked.mp4](renders/ensign-wasp-final-music-watermarked.mp4) | c151d1c713a1a8fd8dd90f2261242c7e8dd5dc0ab5815dce6d40f193ba4b85b5 |
| Fire ants, 88.10 s | [renders/fire-ants-final-music-watermarked.mp4](renders/fire-ants-final-music-watermarked.mp4) | 439edaa89346c38d4108a4a067235867ce55c5f9c18c4a6047c8acebf94f1737 |

Desktop: `Deep Six - Ensign Wasp - FINAL watermarked.mp4`, `Deep Six - Fire Ants - FINAL watermarked.mp4`.
