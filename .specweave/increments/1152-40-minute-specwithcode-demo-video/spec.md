# 40-minute SpecWithCode demo video

## Problem

The user wants a 40-45 minute YouTube demo of SpecWithCode built from real recordings on real machines (M4 Max, M1, Ministorm Linux) and the iPhone Duo, with motion-graphics overlays. The earlier session ("Script the SpecWithCode overview video", transcript `~/.claude/projects/-Users-antonabyzov-Projects-github-specweave-umb/f1313591-f231-4f5a-8e26-010a8609cb08.jsonl`) produced only a 7-minute `SCREEN-CUT-v1.mp4`, mostly headless captures on the M4 running 1.0.135, with two live failures on screen (Codex limit, M1 "Native subscription authorization is unverified") and the "abycrash" handle visible. Demos that fail on camera should become fixed bugs, released, then re-recorded.

## Scope

In: recording 40+ minutes of real demos on M4, M1 and Ministorm (desktop screen capture where possible, headless app capture otherwise); fixing app bugs found while recording, through PRs to `anton-abyzov/specwithcode-dev` and a release; a short iPhone Duo unboxing segment from the user's phone videos; HyperFrames motion graphics (titles, chapter cards, callouts, fleet map); a master cut, per-segment clips, timed voice cues and a bug list in `/Volumes/KINGSTON/MediaLibrary/06-PRODUCTIONS/specwithcode-overview-2026-11/`.

Out: publishing anything; generating the user's cloned voice for publication (scratch timing voice only, labelled); deleting the user's threads or data; touching `statev2.sqlite*`; driving the iPhone Duo while the "iPhone Duo adaptation and install" worker owns it.

## Acceptance Criteria

- [ ] AC-01: `renders/MASTER-CUT-v2.mp4` runs 40:00-45:00, 1920x1080 or larger, every scene from a real recording or a motion-graphics card; ffprobe duration recorded in `renders/MASTER-CUT-v2.json`.
- [ ] AC-02: `renders/segments/` holds at least 8 standalone segment clips, each with motion-graphics overlays (chapter card plus at least one callout), listed with durations in `renders/segments/INDEX.md`.
- [ ] AC-03: Footage covers the M4, the M1 and Ministorm, including skills (version change pushed to machines and verified on another machine), cross-machine workers and remote control over SpecWithCode Connect.
- [ ] AC-04: `VOICE-CUES-cut-v2.md` gives master-cut timecodes with lines to read for every scene.
- [ ] AC-05: `BUGS-FOUND-AND-FIXED.md` lists each bug seen on camera, its PR link and merge state, and whether the fixed version was re-recorded.
- [ ] AC-06: A privacy pass (OCR on sampled frames) finds no visible email, token, secret, or the "abycrash" handle in delivered renders; report in `renders/PRIVACY-CHECK-v2.md`.
- [ ] AC-07: An unboxing segment exists from the user's phone videos, or a titled slot with the drop-in path if the videos are unavailable.

## Approach

Continue from the earlier session's assets (script v2, brief, fleet map, recorder scripts recovered into `work/recovered/`). Record per segment with a headless CDP screencast of each machine's app (paired through `specweave-studio pair --json --ttl`) plus real desktop capture with ffmpeg on the M4 where the desktop app itself matters. Track bugs in `work/bugs.jsonl`; fix in a worktree of `specwithcode-dev`, PR, merge per the release protocol, release, update machines, re-record. Motion graphics in HyperFrames (`hyperframes`, `hyperframes-animation`, `motion-graphics`, `hyperframes-best-practices`) rendered as alpha overlays and full-frame cards; assembly with ffmpeg. Risk: release cycles take an hour or more; unfixed bugs are listed as open with the take kept honest.

## Decisions

### Asked
- D-01 Where are the unboxing videos? Asked October 31, 2026 (AirDrop, pair Chrome, or skip with a slot).
### Defaulted (change any before sw-do)
- D-02 Voice: the user records the voice-over over the final cut; an ElevenLabs scratch track ("Anton Abyzov best voice") may be drafted for timing review only, labelled scratch, never published without the user's yes.
- D-03 The "abycrash" handle is blurred.
- D-04 M1 and M3 stay off the Ministorm Connect setup; the M1 still appears through the M4's fleet.
### Open
- none

## Tasks

### T-01 Record M4 desktop and coordinator segments
- AC: AC-01, AC-03 | Files: raw/screen/v2/m4/* | Test: ffprobe each take; contact sheet reviewed

### T-02 Record fleet segments on M1 and Ministorm (Connect, remote workers, skills push, update)
- AC: AC-03 | Files: raw/screen/v2/fleet/* | Test: ffprobe each take; contact sheet reviewed

### T-03 Fix bugs found on camera, release, re-record
- AC: AC-05 | Files: work/bugs.jsonl, BUGS-FOUND-AND-FIXED.md | Test: each fixed bug has a merged PR URL and a re-recorded take

### T-04 Build motion graphics pack
- AC: AC-02 | Files: hyperframes/v2/* | Test: hyperframes render succeeds; frames checked

### T-05 Unboxing segment
- AC: AC-07 | Files: renders/segments/01-unboxing.mp4 | Test: ffprobe; frames checked

### T-06 Assemble master cut, segment clips, voice cues, privacy check
- AC: AC-01, AC-02, AC-04, AC-06 | Files: renders/MASTER-CUT-v2.mp4, renders/segments/*, VOICE-CUES-cut-v2.md, renders/PRIVACY-CHECK-v2.md | Test: ffprobe duration 2400-2700 s; OCR privacy scan clean

### T-07 Verify and close 1152
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07 | Files: .specweave/increments/1152-40-minute-specwithcode-demo-video/* | Test: specweave verify 1152
