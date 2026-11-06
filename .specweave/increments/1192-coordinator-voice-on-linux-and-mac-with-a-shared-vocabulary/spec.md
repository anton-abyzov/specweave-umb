# Coordinator voice on Linux and Mac with a shared vocabulary

## Problem

Voice calls with the coordinator only work in the Mac app: `apps/desktop/src/preload.ts` exposes the voice bridge only on `darwin`, and transcription and speech run through the Swift helper `native/voice/main.swift` (Apple `SpeechTranscriber`/`SFSpeechRecognizer`, `AVSpeechSynthesizer`). The Linux app shows no voice controls. The user dictates all day through Wispr Flow, which has no Linux version, so Ministorm has no dictation at all. There is also no dictation in the composer on any platform: the phone button starts a spoken call, and the wave button opens voice settings. Neither platform knows the user's vocabulary (product names, tools, people), so these words come out wrong: in a benchmark on Ministorm, `small` without hints wrote "Tori" and "pasta" for "Tauri" and "Postiz".

## Scope

In: spoken calls and push-to-toggle dictation in the coordinator composer on Linux (x64 and arm64 packages; proven on x64) and Mac; free local speech on Linux; a user-editable vocabulary used by both; seeding that vocabulary from the local Wispr Flow dictionary on M4 and copying it to Ministorm as user data; the Linux helper built into the release.

Out: Windows (the engine is portable, but there is no Windows machine here to prove a microphone on, so it stays hidden rather than unproven); dictation in thread composers and on phones; a global dictation hotkey outside the app; Russian spoken replies (Russian dictation works; the first local voice is English); any hosted speech-to-text.

## Acceptance Criteria

- [ ] AC-01: On Linux the desktop bridge exposes voice; `canHostVoiceCall` is true on `darwin` and `linux` and false on `win32`, browsers and phones.
- [ ] AC-02: On Linux a transcription runs locally through a bundled `whisper-cli` with the Whisper `small` q5_1 model; no audio or text leaves the machine, and no network call is made once assets are present.
- [ ] AC-03: Speech assets (model, Piper, voice) download once after the user's consent, from pinned URLs, are rejected on a SHA-256 mismatch, never leave a partial file in place, refuse when the disk lacks room, and report progress to the UI.
- [ ] AC-04: On Linux a reply is spoken for free with Piper when the provider is local, and through the existing server ElevenLabs path when the provider is ElevenLabs.
- [ ] AC-05: The microphone rule is unchanged on every platform: a window gets audio only while it has declared an active call or dictation, for its own origin, after the in-app consent dialog. No flag or code path bypasses it.
- [ ] AC-06: A dictation button in the coordinator composer records until pressed again, inserts each finished phrase into the message box at the cursor without sending it, and stops the microphone when pressed, on navigation and on page exit.
- [ ] AC-07: Vocabulary terms bias recognition (Whisper `--prompt` on Linux; on Mac `contextualStrings` is passed to Apple's engine, whose effect is not guaranteed), and every term and `heard => written` replacement is applied to the transcript, on both platforms.
- [ ] AC-08: Vocabulary is local user data, editable in Voice settings, never sent to a server or into settings sync. Lines that look like secrets (keys, tokens, emails, phone numbers, long random strings) are refused and counted without being echoed back.
- [ ] AC-09: A silent or near-silent recording yields no text: whisper's "Thank you." and "you" on silence and an echoed prompt never reach the message box.
- [ ] AC-10: The Linux AppImage and .deb contain an executable `resources/voice/whisper-cli` built from a pinned whisper.cpp commit with no dependency beyond glibc, and `THIRD_PARTY_NOTICES.md` names whisper.cpp, the Whisper model, Piper and the voice.
- [ ] AC-11: User-facing voice copy names the machine correctly on Linux (no "this Mac", "macOS" or "System Settings"), and a missing microphone on Linux tells the user to plug one in.
- [ ] AC-12: The installed Linux app on Ministorm at the released version transcribes through a real PipeWire source. The physical headset check is listed for the user.

## Approach

Keep the existing bridge and controller; only the engine behind `VOICE_TRANSCRIBE_CHANNEL` and `VOICE_SYNTHESIZE_CHANNEL` differs by platform.

Speech-to-text: whisper.cpp `whisper-cli` with `ggml-small-q5_1.bin` (190 MB), multilingual with `-l auto`. Measured on Ministorm (Ryzen 7 8745H, 8 threads) on a 12.8 s clip: 3.3 s with language detection and 490 MB RSS while running, every vocabulary term right except "Tauri" with detection on, Russian correct. `large-v3-turbo-q5_0` took 7.6 s (14 s with detection) at 825 MB and was no better; `base.en` took 0.8 s but is English only and worse on ordinary words. A process per utterance holds no memory between phrases, which matters on Ministorm. Parakeet and Moonshine were not benchmarked: Whisper's `--prompt` is the vocabulary mechanism proven here, and a search found no equivalent documented for them. Hosted APIs were rejected because they cost money and send audio away.

Text-to-speech on Linux: Piper 2023.11.14-2 with `en_US-lessac-medium`, about 0.4 s for a 5.6 s reply. Downloaded, not bundled, so its GPL `espeak-ng` is not redistributed by us.

Mac keeps Apple's on-device engines and gets `contextualStrings`. Measured on M4 with the same clip, `SpeechAnalyzer` produced identical text with and without them, so on Mac the working part of the vocabulary is the correction pass: casing, joined split forms and `heard => written` lines.

Files: `apps/desktop/src/voice/vocabulary.ts` (parse, secret filter, prompt, correction), `apps/desktop/src/voice/linuxSpeech.ts` (assets, whisper, piper), `apps/desktop/src/ipc/methods/voice.ts`, `apps/desktop/src/preload.ts`, `packages/contracts/src/desktopVoice.ts`, `packages/contracts/src/ipc.ts`, `apps/desktop/src/voice/vocabularyStore.ts`, `packages/client-runtime/src/voice-call/audio.ts`, `native/voice/main.swift`, `apps/web/src/components/studio/VoiceCall.tsx`, `apps/web/src/components/studio/VoiceDictation.tsx`, `apps/web/src/components/studio/VoiceSettings.tsx`, `apps/web/src/components/studio/ProjectWorkspaceSurface.tsx`, `apps/web/src/studio/voiceCallSupport.ts`, `apps/web/src/studio/voiceCallAudio.ts`, `apps/web/src/components/settings/SettingsPanels.tsx`, `scripts/build-desktop-artifact.ts`, `.github/workflows/release-windows-linux.yml`, `THIRD_PARTY_NOTICES.md`.

Risks: real microphones are noisier than the synthesized benchmark, so accuracy needs the user's check; the Ministorm jack is a retailer-documented combo jack whose firmware reports separate headphone and mic pins, so the user's headset is the first real test.

## Decisions

### Asked
- none

### Defaulted (change any before sw-do)
- D-01 Windows → out of this increment; hidden, not half-shown (reversible).
- D-02 Linux speech → local whisper.cpp plus Piper; no paid or hosted default (reversible).
- D-03 Vocabulary location → `<baseDir>/voice/vocabulary.json`, mode 600, per machine.

### Open
- none

## Tasks

### T-01 Vocabulary: parse, filter, prompt, correct
- AC: AC-07, AC-08, AC-09 | Files: repositories/anton-abyzov/specwithcode-dev/apps/desktop/src/voice/vocabulary.ts, repositories/anton-abyzov/specwithcode-dev/apps/desktop/src/voice/vocabulary.test.ts | Test: vp test run apps/desktop/src/voice/vocabulary.test.ts

### T-02 Linux speech engine and assets
- AC: AC-02, AC-03, AC-04 | Files: repositories/anton-abyzov/specwithcode-dev/apps/desktop/src/voice/linuxSpeech.ts, repositories/anton-abyzov/specwithcode-dev/apps/desktop/src/voice/linuxSpeech.test.ts | Test: vp test run apps/desktop/src/voice/linuxSpeech.test.ts

### T-03 Voice IPC, preload and contracts on Linux, vocabulary on Mac
- AC: AC-01, AC-05, AC-07 | Files: repositories/anton-abyzov/specwithcode-dev/apps/desktop/src/voice/vocabularyStore.ts, repositories/anton-abyzov/specwithcode-dev/packages/client-runtime/src/voice-call/audio.ts, repositories/anton-abyzov/specwithcode-dev/apps/desktop/src/ipc/methods/voice.ts, repositories/anton-abyzov/specwithcode-dev/apps/desktop/src/ipc/channels.ts, repositories/anton-abyzov/specwithcode-dev/apps/desktop/src/preload.ts, repositories/anton-abyzov/specwithcode-dev/packages/contracts/src/desktopVoice.ts, repositories/anton-abyzov/specwithcode-dev/packages/contracts/src/ipc.ts, repositories/anton-abyzov/specwithcode-dev/native/voice/main.swift | Test: vp test run apps/desktop/src/voice/voice.test.ts

### T-04 Composer dictation and call UI
- AC: AC-01, AC-06, AC-11 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/VoiceDictation.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/VoiceDictation.test.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/VoiceCall.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/ProjectWorkspaceSurface.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/studio/voiceCallSupport.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/studio/voiceCallAudio.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/settings/SettingsPanels.tsx | Test: vp test run apps/web/src/components/studio/VoiceDictation.test.tsx apps/web/src/components/studio/VoiceCall.test.tsx

### T-05 Vocabulary editor in Voice settings
- AC: AC-08, AC-11 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/VoiceSettings.tsx | Test: vp test run apps/web/src/components/studio/VoiceCall.test.tsx

### T-06 Build whisper-cli into the Linux release
- AC: AC-10 | Files: repositories/anton-abyzov/specwithcode-dev/scripts/build-desktop-artifact.ts, repositories/anton-abyzov/specwithcode-dev/scripts/build-desktop-artifact.test.ts, repositories/anton-abyzov/specwithcode-dev/.github/workflows/release-windows-linux.yml, repositories/anton-abyzov/specwithcode-dev/THIRD_PARTY_NOTICES.md | Test: vp test run scripts/build-desktop-artifact.test.ts

### T-07 Seed the vocabulary from Wispr Flow as local data
- AC: AC-08 | Files: none in the repository; the data lands in the user's voice folder on M4 and Ministorm | Test: count check by a local script, no entries printed

### T-08 Merge, release, installed Linux check
- AC: AC-12 | Files: none | Test: transcription through a PipeWire virtual source in the installed app on Ministorm

### T-09 Verify and close 1192
- AC: AC-12 | Files: none | Test: specweave verify 1192-coordinator-voice-on-linux-and-mac-with-a-shared-vocabulary
