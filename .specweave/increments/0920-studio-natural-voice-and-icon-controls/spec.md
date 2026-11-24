# 0920 Studio natural voice and icon controls

## Problem
The coordinator reads replies with macOS synthesis that sounds poor to Anton. Voice controls include text actions where compact icons are clearer.

## Scope
Opt-in ElevenLabs synthesis in the desktop main process, using an existing voice; preserve on-device microphone transcription. Accessible icon controls and accurate cloud disclosure. No voice upload or cloning. Anton authorized deployment on 2026-10-14; coordinate with the active release owner. Free local speech is the default; optional ElevenLabs uses each user’s key. Managed paid voice is Coming soon only; no billing/fulfillment implementation.

## Acceptance Criteria
- [x] AC-01: Configured ElevenLabs voice synthesizes replies with bounded network requests and useful errors without exposing credentials; unconfigured calls remain local.
- [x] AC-02: Stop and dismiss use accessible icons; cloud reply processing is disclosed.
- [x] AC-03: Focused tests and production build pass; Anton accepts sound and UI before closure.

## Approach
Owned worktree /Users/antonabyzov/Projects/github/studio-voice-quality, codex/voice-quality from origin/main 4d6e30488. Existing owners on credit recovery and thread resolution remain untouched. Voice sample found in Downloads, account API verified the existing voice Anton Abyzov best voice (0Ki1af67ybTaTu4TNmO8); generated a live preview without uploading or cloning audio. Credentials stay in main-process environment; no keys or personal recordings committed. Check current ElevenLabs documentation. Disk has ~125 MB free after sparse checkout; builds may be blocked.

## Tasks
### T-01 Improve synthesis and call controls
- AC: AC-01, AC-02 | Files: apps/desktop/src/voice/elevenLabsVoice.ts, apps/desktop/src/voice/elevenLabsVoice.test.ts, apps/desktop/src/ipc/methods/voice.ts, apps/web/src/components/studio/VoiceCall.tsx, docs/voice-calls.md | Test: cd /Users/antonabyzov/Projects/github/studio-voice-quality/apps/desktop && /Users/antonabyzov/.nvm/versions/node/v22.20.0/bin/node ../../node_modules/vite-plus/bin/vp test run src/voice/elevenLabsVoice.test.ts src/voice/voice.test.ts

### T-02 Verify production UI and manual acceptance
- AC: AC-03 | Files: reports/voice-quality/ | Test: cd apps/web && node ../../node_modules/vite-plus/bin/vp build

### T-03 Natural local default and private voice preferences
- AC: AC-01, AC-02 | Files: native/voice/main.swift, apps/desktop/src/voice/voicePreferences.ts, apps/desktop/src/voice/voicePreferences.test.ts, apps/desktop/src/voice/VoiceHelper.ts, apps/desktop/src/ipc/methods/voice.ts, apps/desktop/src/ipc/channels.ts, apps/desktop/src/preload.ts, packages/contracts/src/ipc.ts, packages/contracts/src/desktopVoice.ts, apps/web/src/components/studio/VoiceCall.tsx, apps/web/src/components/studio/VoiceSettings.tsx, docs/voice-calls.md | Test: cd /Users/antonabyzov/Projects/github/studio-voice-quality/apps/desktop && /Users/antonabyzov/.nvm/versions/node/v22.20.0/bin/node ../../node_modules/vite-plus/bin/vp test run src/voice/

### T-04 Review and coordinate deployment
- AC: AC-03 | Files: reports/voice-quality/ | Test: git diff --check

### T-05 Keep voice settings usable in short windows
- AC: AC-02 | Files: apps/web/src/components/studio/VoiceSettings.tsx | Test: cd /Users/antonabyzov/Projects/github/studio-voice-quality && PWDEBUG=0 PLAYWRIGHT_HTML_OPEN=never /Users/antonabyzov/.nvm/versions/node/v22.20.0/bin/node reports/voice-quality/check-ui.mjs
