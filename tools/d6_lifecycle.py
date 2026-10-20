"""Publication reservations and explicit final-video completion, without rendering."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import subprocess

from d6_sources import normalized, publication_key, source_url


def publication_record(card):
    return {
        "source_id": card.get("source_id", card.get("id", "")),
        "urls": sorted({source_url(u) for u in card.get("urls", [card.get("url", "")]) if u}),
        "publication_key": card.get("publication_key") or publication_key(card),
        "page_digest": card.get("page_digest"),
        "lesson": card.get("lesson", ""),
        "title": card["title"],
    }


def episode_sources(episode):
    source = episode["source"]
    return [source] + episode.get("supporting_sources", []) + source.get("supporting_references", [])


def reservations(state):
    # Historical field name: used_sources also contains shown-but-unchosen cards.
    records = list(state.get("used_sources", []))
    for episode in state.get("approved", []):
        records.extend(publication_record(c) for c in episode_sources(episode))
    current = state.get("current") or {}
    records.extend(publication_record(c) for c in current.get("supporting_cards", []))
    return records


def same_publication(a, b):
    a, b = publication_record(a), publication_record(b)
    return bool(set(a["urls"]) & set(b["urls"]) or
                a["publication_key"] == b["publication_key"] or
                (a["page_digest"] and a["page_digest"] == b["page_digest"]))


def source_owner(state, card):
    for episode in state.get("approved", []):
        if any(same_publication(card, c) for c in episode_sources(episode)):
            return episode["id"]
    return None


def final_video_receipt(root, episode, mp4, audio_manifest, final=False):
    """Caller must explicitly designate a finished video. Previews never auto-complete."""
    from d6_audio import AudioError, verify_approved_audio

    if not final:
        raise ValueError("Declare the finished MP4 with --final; previews do not consume sources.")
    root = Path(root).resolve()
    path = Path(mp4).resolve()
    if path.suffix.lower() != ".mp4" or not path.is_file():
        raise ValueError("A completed local MP4 file is required.")
    try:
        audio = verify_approved_audio(audio_manifest)
    except AudioError as error:
        raise ValueError(str(error)) from None
    if audio["approved_narration_id"] != episode["id"]:
        raise ValueError("The approved audio belongs to another episode.")
    script_hash = hashlib.sha256(" ".join(episode["text"].split()).encode()).hexdigest()
    if audio["script_sha256"] != script_hash:
        raise ValueError("The audio does not match this episode's saved approved script.")
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)],
            capture_output=True, text=True, timeout=30)
    except subprocess.SubprocessError:
        raise ValueError("The final MP4 check timed out or failed.") from None
    if result.returncode:
        raise ValueError("The final MP4 could not be read.")
    probe = json.loads(result.stdout)
    streams = probe.get("streams", [])
    if not any(s.get("codec_type") == "video" and not s.get("disposition", {}).get("attached_pic") for s in streams):
        raise ValueError("The MP4 has no video stream.")
    if not any(s.get("codec_type") == "audio" for s in streams):
        raise ValueError("The MP4 has no audio stream.")
    duration = float(probe.get("format", {}).get("duration", 0))
    if not math.isfinite(duration) or duration < max(1, audio["duration_seconds"] - 2):
        raise ValueError("The MP4 is shorter than the approved narration; a preview cannot complete it.")
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return {"episode_id": episode["id"], "mp4_path": str(path), "mp4_sha256": digest.hexdigest(),
            "duration_seconds": duration, "audio": audio,
            "sources": [publication_record(c) for c in episode_sources(episode)],
            "hook_sha256": hashlib.sha256(normalized(episode["hook"]).encode()).hexdigest(),
            "script_sha256": hashlib.sha256(normalized(episode["text"]).encode()).hexdigest(),
            "declared_final": True}
