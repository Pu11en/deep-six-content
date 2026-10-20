# Task: one canvas for the whole Deep Six system, then a clean system that runs

Drew, 20 Oct 2026, in his words: "establish the entire system and create a new diagram. The one canvas we have, leave that, but make a new canvas, and this one will have the final zero to video, even with the music that we did, like everything included. After we established that, then we build it, then we clean out everything and delete everything that's junk. We're left with the system itself, so we have a clean system that runs. We might have to add some stuff, because if we look at the flow we might need to add some stuff."

## Order of work

1. **Inventory, read only.** Read the files below. List every working piece, how it is run, and every gap. Facts in a working note, not on the board.
2. **New canvas.** Excalidraw, following the Excalidraw entry in `/home/drewp/main-projects/zed-setup/ON-REQUEST-SKILLS.md` and `EXCALIDRAW-WORKFLOW.md` beside it. Build it from a builder script with layout checks, like `01-content/diagrams/animation-system.build.py`, so no screenshots are needed. Leave `animation-system.excalidraw` and its builder unchanged.
   - Cover zero to finished video: pest and source research, hooks, script, approvals, MP3 (voice, spending OK, listening approval), the video runner, music, the client-preview watermark, Desktop delivery, Drew's verdict, records (sources used, learned rules).
   - Mark each box built, partly built or missing.
3. **Drew reviews the canvas** and adds what is missing.
4. **Build the gaps Drew picks.** Known gaps on 20 Oct:
   - Music and the watermark run by hand after a video is approved; the runner does not call them.
   - The MP3 side does not hand an approved MP3 to `make_video.py start` by itself.
   - The runner's planner, animator, new-drawings maker and triage roles have never run for real.
   - Open choice: how hard the AI reviewer works. A whole-video review took 14 minutes of Opus at max effort.
5. **Clean-up.** List the junk with sizes: old tests, superseded drafts, unused previews, duplicate renders, old diagrams. Drew approves the list before anything is deleted. Keep approved videos, approved audio, approvals and source logs. Commit before and after. No push without Drew's OK.
   - Also decide where big media should live. The repo is about 2.2 GB, and GitHub warned on 20 Oct about music preview MP4s over 50 MB (72 MB each). Options: keep only finals in git, or use Git LFS.

## Read first

- `HANDOFF.md` (top section) and `CLAUDE.md`.
- Writing and MP3: `01-content/mp3-system/README.md`, `flow-and-recovery.md`, `edge-cases.md`; the command is `tools/d6`.
- Video: `01-content/animation/AUTOMATION-DESIGN.md`, `AUTOMATION-BUILD.md`, `VIDEO-FLOW.md`; the runner is `make_video.py`.
- Outro: `01-content/outro/APPROVED-OUTRO.md`.
- Music: `01-content/music/APPROVED-MUSIC.md` (approved bed and the exact mix command).
- Watermark: `01-content/watermark/README.md`.
- Existing canvases: `01-content/diagrams/README.md`.

## State on 20 Oct

- Approved and finished: the fire-ant video and the ensign-wasp video, each also with the approved Warm Ambient music.
- The video runner is built and was tested by re-making the ensign-wasp video byte for byte. Its test copy on the Desktop, `Deep Six - Runner Test Ensign Wasp v1.mp4`, duplicates the approved video and can go in the clean-up.
- Model ladder (Drew, 20 Oct): Opus 5.5, then GPT-6 Sol, then GPT-6 Astra.
- Everything is committed locally (commit `90dda56` and the one after it). Nothing is pushed.

## Rules

- Follow `CLAUDE.md` and Drew's global rules: caveman voice in chat, one question at a time as multiple choice, no paid calls without his OK, no push, ask before deleting anything.
