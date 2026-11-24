# Dictation shortcut in every composer with global dictation settings

## Problem

Dictation (`apps/web/src/components/studio/VoiceDictation.tsx`) starts and stops only by clicking the mic button, and only the project coordinator composer has it. Thread composers (`ChatComposer.tsx`) have no dictation at all. There is no keyboard shortcut, so Linux users (whisper.cpp path) and Mac users have to reach for the mouse. The language comes from the OS on macOS and is always auto-detected on Linux, and there is no way to pin it or choose press-to-toggle versus hold-to-talk.

## Scope

In: a `composer.dictation.toggle` keybinding command with a default, rebindable in Settings > Keybindings; the shortcut and mic button in the coordinator composer and every thread composer (including new-thread drafts); global dictation settings (language, mode) in the app's client settings, one value for every project and thread; Linux whisper honours a chosen language.

Out: a speech engine for Windows desktop or plain browsers (the shortcut there shows that dictation needs the app on macOS or Linux); mobile apps.

## Acceptance Criteria

- [ ] AC-01: `composer.dictation.toggle` exists with default `mod+shift+d` (`when: "!terminalFocus"`), so Cmd+Shift+D on macOS and Ctrl+Shift+D on Linux and Windows; it shows as "Composer: Start or Stop Dictation" in Settings > Keybindings and can be rebound there.
- [ ] AC-02: In the coordinator composer the shortcut starts dictation and pressing it again stops it, the same as the mic button.
- [ ] AC-03: Every thread composer (existing thread and new-thread draft) has the mic button and dictation bar, and the shortcut toggles dictation there; phrases land at the caret, unsent.
- [ ] AC-04: Dictation language (System or a chosen language) and mode (Toggle or Hold to talk) are stored once in the app's client settings (`dictationLanguage`, `dictationMode`, shared by every window), are not project-overridable, and apply in every project and thread.
- [ ] AC-05: In Hold mode, holding the shortcut dictates and releasing it stops.
- [ ] AC-06: On Linux, a chosen language is passed to whisper (`-l <code>`); with System it stays `auto`.
- [ ] AC-07: Where dictation is unavailable (Windows desktop, web), the shortcut does nothing harmful and leaves the browser default suppressed only when dictation can run.

## Approach

1. Contracts and shared: add the command to `STATIC_KEYBINDING_COMMANDS`, the default to `DEFAULT_KEYBINDINGS`, `dictationLanguage` and `dictationMode` to `ClientSettingsSchema` and its patch, `pinLanguage` to `DesktopVoiceTranscribeInputSchema`.
2. `useVoiceDictation` takes an `insert` target, reads the global language, and exposes a `useDictationShortcut` hook for keydown/keyup (toggle or hold).
3. Coordinator: wire the shortcut in `ProjectWorkspaceSurface.tsx`.
4. Thread composer: mount the hook, button and bar in `ChatComposer.tsx`, inserting through `applyPromptReplacement`.
5. Settings: dictation language and mode rows beside the voice-calls switch, with the current shortcut shown and a link to Keybindings; keybinding label override.
6. Desktop: Linux `transcribe` takes a language.

Decision: the hotkey stays in the keybindings file (already global for the app); language and mode join the client settings beside `voiceCallsAllowed`, because speech runs on the device being spoken into. Rejected: server `settings.voice`, which is per connected environment and would give one desktop different languages per machine.

Risk: Chrome binds Cmd/Ctrl+Shift+D to "bookmark all tabs"; the handler calls `preventDefault` only when dictation is available.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 default chord → `mod+shift+d`, free outside the terminal (reversible in Settings > Keybindings)
- D-02 mode values → Toggle (default) and Hold to talk
- D-03 storage → client settings, not project-scoped
### Open
- none

## Tasks

### T-01 Contracts, defaults and settings schema
- AC: AC-01, AC-04 | Files: packages/contracts/src/keybindings.ts, packages/shared/src/keybindings.ts, packages/contracts/src/settings.ts, packages/contracts/src/desktopVoice.ts, packages/contracts/src/ipc.ts | Test: node node_modules/vite-plus/bin/vp test run packages/contracts/src/keybindings.test.ts packages/shared/src/keybindings.test.ts

### T-02 Shortcut in coordinator and thread composers
- AC: AC-02, AC-03, AC-05, AC-07 | Files: apps/web/src/components/studio/VoiceDictation.tsx, apps/web/src/components/studio/dictationShortcut.ts, apps/web/src/components/studio/VoiceCall.tsx, apps/web/src/components/studio/ProjectWorkspaceSurface.tsx, apps/web/src/components/chat/ChatComposer.tsx | Test: cd apps/web && node ../../node_modules/vite-plus/bin/vp test run --project unit src/components/studio/VoiceDictation.test.tsx src/components/studio/dictationShortcut.test.tsx

### T-03 Settings rows and keybinding label
- AC: AC-01, AC-04 | Files: apps/web/src/components/settings/DictationSettings.tsx, apps/web/src/components/settings/SettingsPanels.tsx, apps/web/src/components/settings/settingsSearch.ts, apps/web/src/components/settings/KeybindingsSettings.logic.ts | Test: cd apps/web && node ../../node_modules/vite-plus/bin/vp test run --project unit src/components/settings/KeybindingsSettings.logic.test.ts src/components/settings/settingsSearch.test.ts

### T-04 Linux whisper language
- AC: AC-06 | Files: apps/desktop/src/voice/linuxSpeech.ts, apps/desktop/src/ipc/methods/voice.ts | Test: cd apps/desktop && node ../../node_modules/vite-plus/bin/vp test run src/voice/linuxSpeech.test.ts

### T-05 Headless coordinator and thread checks, Linux CI
- AC: AC-02, AC-03, AC-05 | Files: apps/web/tests/dictation-shortcut/ | Test: headless verify.mjs run plus the ubuntu-24.04 PR Gate (web) job

### T-06 Verify and close 1261
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07 | Files: none | Test: specweave verify 1261
