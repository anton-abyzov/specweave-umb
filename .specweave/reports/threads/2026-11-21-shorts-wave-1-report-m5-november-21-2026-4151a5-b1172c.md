---
title: "Shorts wave 1 report (M5, November 21, 2026)"
thread: "mcp:7f490574-3d01-45f4-b8ee-1dfa6b1c98fd"
threadTitle: "Livestream shorts factory"
savedAt: "2026-11-21T06:11:25.342Z"
---

# Shorts wave 1 report (M5, November 21, 2026)

## Outcome

Six clips re-cut in the stacked layout, privacy-scanned, uploaded and scheduled on Postiz: 39 posts created (create calls only). Every post's preview page holds the expected media file, and the API list shows each planned channel and time exactly once. X and TikTok wait for m4 (12 rows in `/Users/anton/.specwithcode/m5/scratch/2026-11-21-shorts-factory/handoff/blotato-queue.json`). Captions are hand-checked but not unslop-passed: the skill accepts user invocation only.

Full schedule table with post IDs and preview links: `/Users/anton/.specwithcode/m5/scratch/2026-11-21-shorts-factory/reports/schedule-wave1.md`

## Clips

| Clip | Source | Length | Title bar | Shots, longest | Words/min | Loudness, peak | Silence ratio |
|---|---|---|---|---|---|---|---|
| `g02-ai-gta` | stream 2 | 17.6 s | AI BUILT ME A GTA | 16, 1.28 s | 150 | -13.9 LUFS, -1.5 dBFS | 0.092 |
| `c07-touch` | stream 1 | 13.9 s | STEVE JOBS SAID NEVER | 12, 1.40 s | 147 | -14.1, -1.5 | 0.137 |
| `s02-pass` | stream 1 | 12.7 s | AI BUILT THIS PASS | 11, 1.23 s | 151 | -13.8, -1.5 | 0.213 |
| `g05-ai-play` | stream 2 | 7.4 s | CLAUDE TRIED TO PLAY GTA 6 | 6, 1.33 s | 171 | -14.3, -1.4 | 0.0 |
| `s03-limit` | stream 1 | 13.8 s | CLAUDE HIT ITS LIMIT | 13, 1.38 s | 157 | -14.2, -1.5 | 0.0 |
| `s05-os` | stream 1 | 12.1 s | AI BUILT ME AN "OS". SORT OF. | 11, 1.23 s | 178 | -14.3, -1.5 | 0.158 |

First spoken word is at 0.0 s in all six. Silence ratio is `silencedetect` at -35 dB, 0.3 s, so it counts the 0.3 s pause floor; the playbook's 0.03 target is not met on four clips.

Held: `g01-plane` (20.1 s, three seaplane crashes, 57 words a minute, no AI in the picture). Wave 2 started: `s10-duo` (13.6 s, folding iPhone), rendered and scanned, not uploaded.

Hook B openings rendered and kept, not posted: `c07-touch-b`, `g02-ai-gta-b`, `s02-pass-b` (their captions still need the word corrections the A versions got).

## Checks

- Privacy: OCR of every frame at 4 fps, full 1080x1920 (`privacy/v2/<clip>.ocr.txt`). One fix: a LAN address in the browser bar of `s05-os`, cropped out and rescanned. Final scans: no email, local path, code or token. Whisper text of each cut has no spoken email or code. `s03-limit` shows the public address `https://claude.ai/settings/usage?from=cc_cli_limit_message` in the limit card; it carries no account data.
- Music: YAMNet audio tags, not a listen (`privacy/v2/music-final.txt`). `c07-touch` had the macOS setup soundtrack under the touch (0.59 to 0.80); the reaction shot was dropped and a gate added, final maximum 0.08. GTA clips score 0.02 and 0.01. `g01-plane` peaks at 0.33 on the "wasted" sting.
- Honesty: no stream-1 clip names Gemini, uses "vs" or "winner", or shows the join or copy working. "First time in history" is cut from `c07-touch`. Labels "44 MIN EARLIER" and "6 MIN LATER" match the source times.
- Census: `reports/gta-census.md`. 0 usable AI orders, no vote overlay, no chat replay.

## Not met

- Frame-0 text over 7 words on `s03-limit` and `s02-pass` (UI and render text in the picture).
- Opening frames: only `c07-touch` shows three subjects in the first 3 s. `g02-ai-gta`, `s02-pass` and `s03-limit` hold one shot with punch-ins; `g05-ai-play` and `s05-os` show two.
- Titles: three title bars and YouTube titles open with "AI built" (`g02-ai-gta`, `s02-pass`, `s05-os`), against the no-shared-wording rule.
- YouTube private-first upload for the GTA clips (playbook section 10) was not done; Postiz posts are public at fire time.
- `analyze.py` from the video-pipeline skill was not run; the numbers above come from `scripts/cut2.py` and ffmpeg.
- Discord: not scheduled (needs the live Short link and a channel). Personal Facebook: no such channel in Postiz. No GTA clip on LinkedIn or brand accounts. Only `s03-limit` went to the brand accounts; `s02-pass` and `s05-os` do not show the product clearly.
- 1:1 and 16:9 versions were not re-made; the playbook table asks for the 9:16 master on every platform used here.

## For m4 to act on (the creator cannot edit queued posts)

- Unslop: the first two posts to fire are YouTube AI Power on November 21, 1:00 PM EST (`cmwq05xii00asourw7wi4o4c3`) and Instagram @aabyzov on November 21, 6:00 PM EST (`cmwq0684q00atourwsswzmabp`).
- `c07-touch` audio: the gate that removes the macOS setup music was never heard by a person and can pump under speech. Listen before November 22, 10:00 AM EST.
- Russian title bars, captions and post text were not checked by Anton. First Russian post: Instagram @antonaipower, November 22, 2:00 PM EST.

## Wave 2 position

Cut so far: 8 clips (6 scheduled, `g01-plane` held, `s10-duo` ready). Review 1 survivors not yet cut: 3 (shootout), 26 (boat), 32 (128 GB and GTA still lags), plus three reviewer ideas (title-versus-reality, a solo roast of the AI-built game, a freeze montage). The first three have no AI in the picture. Reaching 15 needs a ruling on first-time-player GTA clips, or reviving killed candidates with no review batch left.
