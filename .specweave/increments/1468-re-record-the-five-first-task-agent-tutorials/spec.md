# Re-record the five first-task agent tutorials

## Problem

spec-weave.com has no "Run your first task" video for Claude Code, Codex, OpenCode, Grok or Antigravity. On October 28, 2026, specweave PR #2183 (`30fb88566e3101160811518a1d9398fc368247ee`) took the five down because they showed an old interface and used audio the owner rejected. Their entries moved to `planned` and `/tutorials/specwithcode-{claude-code,codex,opencode,grok,antigravity}/` now redirect. PR #2188 (`4ecad300869f1f232c6f7e62b858130a14d84e59`, October 29) saved the unfinished re-record: a Codex edit with Whisper word timings, plus shot lists for the other three. Increment 1109 also built five replacement media families, but they sit unmerged on branch `feat/landing-tutorial-refresh` (`f77b6f273`). They were never listened to (1109 T-04 block, October 28, 2026: "AC-04 actual listening remains unproven: host audio input is unsupported."), and the interface has changed since.

This increment takes over 1109's tutorial half (its AC-04 and the tutorial part of AC-05). 1109's landing half shipped in specweave PR #2181 (`51fc50a9`).

## Scope

In: five tutorials, one for each agent, recorded on the current app; the narration voice proven and the guard from 1109 (refuse to reuse a wrong-voice cache) kept; captions; R2 hosting (#2189); `docs-site/src/data/tutorials.json` moved back from `planned` to `tutorials`; the redirects removed. Reuse what is still current from #2188 and from `feat/landing-tutorial-refresh`, and drop the rest.

Out: landing page changes (1109), other tutorials, social posts, new provider spend beyond the narration.

## Acceptance Criteria

- [ ] AC-01: Each of the five tutorials follows the current first-task flow in the latest released app. Every shot is real app capture from that release, and a script records which steps it shows.
- [ ] AC-02: Narration uses only the canonical voice, with a request receipt for each clip. Generation refuses an unknown voice or a stale cache instead of reusing old audio.
- [ ] AC-03: Every video decodes, has captions that match the words, and meets the loudness target. Every video plays in a headless docs build.
- [ ] AC-04: The owner has watched and listened to all five and accepted them. Their words and the date are recorded in this spec. No agent can stand in for this check.
- [ ] AC-05: The five pages are live on spec-weave.com, the `planned` entries and redirects are gone, and the public media bytes match the delivered files.

## Approach

1. Inventory: list what #2188 and `feat/landing-tutorial-refresh` contain, and which shots still match the current app.
2. Record each agent's flow on the current release, headless where possible. Write one script per agent.
3. Narrate with the voice-provenance guard, then add captions and run the loudness check.
4. Owner review: send all five for watching and listening, and record the answer.
5. Open one specweave PR, upload to R2, deploy, and check the public pages and bytes.

Risk: the app interface moves quickly; record close to delivery.

## Decisions

### Asked
- D-01: Split 1109's tutorials into this increment → yes (owner, November 24, 2026: "yes, do what's recommended", on the board triage recommendation to close 1109's landing half on #2181 and move the tutorials to a new increment).
### Defaulted (change any before sw-do)
- D-02: Re-record on the current app instead of shipping the October media from `feat/landing-tutorial-refresh` as it is. That media shows the 1.0.105-era interface.
- D-03: Priority P2. Nothing is broken, the pages are only missing.
### Open
- none

## Tasks

### T-01 Inventory saved re-record work
- AC: AC-01 | Files: repositories/anton-abyzov/specweave/video/tutorials | Test: inventory report in this increment's reports/ listing every reusable and dropped asset from #2188 and `f77b6f273`

### T-02 Record and script the five current flows
- AC: AC-01 | Files: repositories/anton-abyzov/specweave/video/tutorials | Test: capture provenance file naming the app version per shot
- **Dependencies**: T-01

### T-03 Narrate, caption and check the media
- AC: AC-02, AC-03 | Files: repositories/anton-abyzov/specweave/video/tutorials | Test: voice preflight rejects a wrong voice and a stale cache; full decode, caption and loudness check; `npm --prefix repositories/anton-abyzov/specweave/docs-site run build`
- **Dependencies**: T-02

### T-04 Owner watches and listens
- AC: AC-04 | Files: .specweave/increments/1468-re-record-the-five-first-task-agent-tutorials/spec.md | Test: the owner's words, quoted with date, under Decisions
- **Dependencies**: T-03

### T-05 Publish and verify the public pages
- AC: AC-05 | Files: repositories/anton-abyzov/specweave/docs-site/src/data/tutorials.json | Test: merged PR, deploy run green, public page and R2 byte checks
- **Dependencies**: T-04

### T-06 Verify and close 1468
- AC: AC-01, AC-02, AC-03, AC-04, AC-05 | Files: none | Test: `specweave verify 1468-re-record-the-five-first-task-agent-tutorials`
