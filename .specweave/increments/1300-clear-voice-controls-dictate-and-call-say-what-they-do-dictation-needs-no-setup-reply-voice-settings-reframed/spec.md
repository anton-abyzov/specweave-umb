# Clear voice controls: Dictate and Call say what they do, dictation needs no setup, reply voice settings reframed

## Problem

Anton, November 11, 2026, with a screenshot of the coordinator composer's `+`, microphone and phone icons: "We must tell it clearly, and maybe this configuration for 11Labs should be somehow rethought so that it's only for pronunciation, right? It's not clear what it's doing. Dictate: one icon is for dictation, and two others are for calls and setup. On how to respond to it, think hard on how to improve this UI/UX."

What the code does today (`specwithcode-dev`, `origin/main` at `6ae32d8603`):

| Control | What it does | Where |
|---|---|---|
| Microphone | Dictation. Speech becomes text on the device and lands in the message box, unsent. Tip: "Dictate into the message (⇧⌘D)". | `apps/web/src/components/studio/VoiceDictation.tsx:380` |
| Phone | Voice call with the coordinator. Each thing said is sent as a message; the answer is read aloud. Tip: "Call the coordinator and talk". | `apps/web/src/components/studio/VoiceCall.tsx:481` |
| Waveform | Opens a "Voice" dialog. Tip: "Voice settings". | `apps/web/src/components/studio/VoiceSettings.tsx:230` |

What ElevenLabs controls: only the voice that reads a call's answers aloud. `speakReply` (`VoiceCall.tsx:101`) sends the answer text to the server's `voice.synthesize`, which calls ElevenLabs text-to-speech (`apps/server/src/voice/elevenLabsVoice.ts:33`). Speech-to-text never uses it: dictation and calls both transcribe on the device (Apple speech on Mac, whisper.cpp on Linux). The default voice is the free local one.

Why it is unclear:

- **Three bare icons, short tips.** Nothing shows which is which until hover. The waveform, which other apps use for "voice conversation", is the settings button here. The phone reads as telephony.
- **Dictation asks for a setup it does not need.** The first press opens "Allow voice?" (`VoiceCall.tsx:426`): two paragraphs about calls, ElevenLabs credits and AI provider billing, with the button "Allow and dictate". Dictation is free, on-device and sends nothing. The same `voiceCallsAllowed` flag gates it (`VoiceDictation.tsx:337`), and the Settings switch for it is labelled "Voice calls with the coordinator".
- **The Voice dialog does not say what it is for.** Its lead is "Speak naturally, without a speech subscription." It never says the voice is used only in calls. It mixes the reply voice (text-to-speech, calls only) with "Your vocabulary" (speech recognition, dictation and calls). The ElevenLabs voice cannot be tested there; "Preview" plays only the local voice. It ends with a "Managed premium voice · Coming soon" card for something that does not exist.
- **The call button can be dead.** With ElevenLabs chosen but no key or voice ID, the phone is disabled and the reason lives only in its tooltip (`VoiceCall.tsx:250`, `:497`).
- **No choice of how it answers.** A call always reads the answer aloud. There is no way to talk and get text back.
- **Settings are in three places.** The dialog behind the waveform, and three rows in Settings > General (`SettingsPanels.tsx:2604`, `DictationSettings.tsx`).

## Scope

In: the web and desktop app (`apps/web`, `packages/client-runtime`, `packages/contracts`) on macOS and Linux, where voice exists today. Named Dictate and Call controls with explanatory tips. Dictation with no in-app setup. A Call card with a one-line explanation and the answer choice. A Settings > Voice page that replaces the Voice dialog and the General rows. An answer mode (text only, voice and text, voice). A pronunciation list. A headless fixture with light and dark captures.

Out: voice on Windows, browsers and phones (still no controls). Calls in thread composers. Reading typed-chat replies aloud. A new speech engine, new languages or streaming speech. The desktop microphone gate (`apps/desktop/src/voice/voicePermission.ts`). ElevenLabs model, speed and voice-library browsing. Mobile and iOS apps.

## Acceptance Criteria

- [ ] AC-01: The coordinator composer shows two voice controls after Attach: Dictate (microphone) and Call (phone). Each shows its icon and name when the foot row has room and the icon alone otherwise; the names fold before any other chip in the row folds. The waveform "Voice settings" button is gone from the composer.
- [ ] AC-02: Hover or keyboard focus on either control shows a tip with its name, one sentence on what happens, and for Dictate the shortcut and "On this Mac · free · no setup" ("on this computer" on Linux). The thread composer's microphone shows the same Dictate tip. Accessible names are "Dictate", "Stop dictating", "Call the coordinator" and "End call".
- [ ] AC-03: On macOS a first press of Dictate, or its shortcut, shows no in-app dialog: macOS asks for its own permissions once, then the strip says "Listening" and words land in the message box unsent. This holds whatever `voiceCallsAllowed` is, with no ElevenLabs key, and with ElevenLabs selected but incomplete. A refused permission shows the existing strip with "Open microphone settings".
- [ ] AC-04: On Linux, Dictate shows one dialog only while speech files still need downloading. It names the size, the sources and that dictation works offline afterwards, and says nothing about calls, ElevenLabs or billing. Once the files are present no dialog appears.
- [ ] AC-05: Pressing Call opens a card anchored to the button, with the title "Call the coordinator", one sentence ("Talk hands-free. What you say is sent as a message."), the answer choice, the reply voice in use, and "Start call" focused. Enter starts the call, Escape closes the card, and the microphone opens only after Start call. The card states that speech becomes text on the device; it mentions ElevenLabs and its cost only when ElevenLabs is the reply voice and the answer mode uses voice.
- [ ] AC-06: The answer choice has three modes, saved as `settings.voice.replyMode` with "Voice and text" as the default. Text only: the answer appears in the chat, nothing is synthesized and ElevenLabs is never contacted. Voice and text: today's behavior, a spoken version of up to 700 characters with the full answer in the chat. Voice: the whole answer is read aloud in sentence-bounded parts, up to 6,000 characters, and stopping or speaking over it cancels the remaining parts. In every mode the answer is in the chat.
- [ ] AC-07: Call is never a disabled button with the reason hidden in a tip. When a call cannot start, the card says why and offers the fix: for ElevenLabs without a key or voice ID, "Finish setup" and "Use this Mac's voice"; with Text only selected that state does not block the call.
- [ ] AC-08: Settings has a Voice page with three sections named by what they do: Dictation (language, shortcut mode, words to recognize), Calls with the coordinator (the answer choice) and Reply voice. The three General rows and the Voice dialog are gone, and Settings search for "dictation", "voice", "call", "microphone" and "ElevenLabs" opens the Voice page at the right row.
- [ ] AC-09: The Reply voice section says it reads answers aloud in a call and is not used for dictation or for understanding speech. It offers the device's free voice (voice, pace, Preview) and ElevenLabs (own key, voice ID). "Save and test" saves the ElevenLabs settings and plays one sentence in that voice, or shows the server's exact reason when it fails. A saved key is never displayed. The "Managed premium voice" card is removed.
- [ ] AC-10: A "Say it like this" list of `written => spoken` lines changes how those words are read aloud by either voice, matching whole words without regard to case. It never changes the text in the chat or what dictation writes.
- [ ] AC-11: A headless fixture renders the composer controls (wide and narrow), both tips, the dictation strip, the Call card (ready and ElevenLabs incomplete) and the Voice page in light and dark, with no clipped or overflowing element, every control reachable by keyboard, and no contrast or accessible-name violation in an axe run. Captures are saved to this increment's `reports/`.

## Approach

Mockups (static HTML, not app code) and headless captures are in `reports/mockups/`, each as `-light.png` and `-dark.png`:

- Before and after in one image: `reports/mockups/compare-light.png`, `reports/mockups/compare-dark.png`
- Before: `before-composer`, `before-first-use` (the "Allow voice?" dialog), `before-settings` (the Voice dialog)
- After: `after-composer`, `after-narrow` (icons only, Call tip), `after-dictating`, `after-call-card`, `after-call-blocked`, `after-settings`
- Source: `reports/mockups/mockup.html` (`?view=<name>&theme=light|dark`), captured with `reports/mockups/shoot.mjs`, which fails on any clipped element.

Order of work:

1. **Engine** (`packages/contracts/src/settings.ts`, `packages/client-runtime/src/voice-call/`). `VoiceSettings` gains `replyMode` (`"text" | "both" | "voice"`, default `"both"`) and `pronunciation` (text, at most 200 lines). `speakableText` takes the replacements and a mode; the controller skips synthesis for `"text"` and loops over parts for `"voice"`. A server too old to know the keys drops them, so the page reports "Update the SpecWithCode service" as the dialog does today for `provider`.
2. **Dictation without the dialog** (`VoiceDictation.tsx`). `start()` stops reading `voiceCallsAllowed` and opens the dialog only when `setupBytes > 0`. `VoiceConsentDialog` becomes the Linux download dialog.
3. **Composer controls** (new `VoiceControls.tsx`: the tip, the labelled button, the Call card). `VoiceCallButton` opens the card instead of starting or showing consent; `unavailableReason` moves from the tooltip into the card. `ProjectWorkspaceSurface.tsx` and `ChatComposer.tsx` get wiring only.
4. **Settings > Voice** (new route and `VoiceSettingsPanel.tsx`). The dialog's fields move there under the three headings; `DictationSettings` moves from General. The one-time legacy import that runs when the dialog mounts (`VoiceSettings.tsx:25`) moves to `apps/web/src/studio/legacyVoiceImport.ts`, run from `useVoiceCall`.
5. **Fixture and docs** (`apps/web/tests/voice-ux/`, `docs/voice-calls.md`). The two existing fixtures that mock the dialog and consent are updated.

Overlap with other open increments:

- **1284** (calm model picker) lists `ChatComposer.tsx`, `ProjectWorkspaceSurface.tsx`, `CoordinatorComposer.tsx`, `shell/shell.css` and `contracts/settings.ts`. It reshapes the same foot row: chips become icons, the machine chip and color are added (its AC-13, AC-15, AC-17). This increment follows its rule of "icon plus short label when there is room" and makes the voice names the first thing to fold, so its fold order holds. Conflicts are likely in `ProjectWorkspaceSurface.tsx` around the composer `meta` block (`:1886`). Styles here stay in `shell/voice.css`, not `shell.css`.
- **1294** (recommend Full access) lists `ChatComposer.tsx`, `contracts/settings.ts` and `i18n/messages/en.ts`. Its `ChatComposer.tsx` change is in `ComposerFooterModeControls` (`:1303`); this one touches the dictation block (`:4236-4273`, `:7199-7208`, `:8096-8125`), so the hunks do not meet. Both add keys to `settings.ts` in different structs (it: client settings; this: `VoiceSettings` at `:1248`). This increment adds no keys to the nine message files, because voice copy is not translated today.
- Whichever lands second rebases. Suggested order: 1294 (small), then this, then 1284's composer tasks (T-06, T-07), since 1284 restyles the whole row.

Rejected: one voice button with a menu (hides Call behind a click and still needs explaining); swapping the phone for the waveform icon (the call strip, "Hang up" and docs all use the phone); keeping the dialog and only rewriting its copy (settings would stay in three places); a per-message "read aloud" button (new feature, not this problem).

Risks: removing the in-app dialog changes what 1192 AC-05 promised (see D-01). On Linux there is no system prompt, so the press on a named button is the only question asked. "Voice" mode sends more text to ElevenLabs than today; the card and the page say so.

## Decisions

### Asked
- none (the owner's message set the direction; the choices below are defaults he can change before work starts)

### Defaulted (change any before sw-do)
- D-01 Pressing Dictate is the consent. The in-app "Allow voice?" dialog no longer appears for dictation; macOS still asks for its own permissions, and Linux asks only before a download. This amends 1192 AC-05 ("after the in-app consent dialog"). The desktop rule that a window gets the microphone only while a call or dictation is declared stays as is. Alternative: keep a two-line dialog once (reversible).
- D-02 The Call card opens on every press of Call, and Enter starts. It is where the one-line explanation, the answer choice and the voice are always visible, and it stops a stray click from opening the microphone. Alternative: skip the card after the first call (reversible).
- D-03 "Voice" means the whole answer is read aloud; the chat keeps the text in every mode, because it is the record handoffs and other machines read. Alternative: two modes only, Text only and Voice and text (reversible).
- D-04 "Only for pronunciation" is read as: ElevenLabs is only the voice that speaks answers, and the page should say so. The "Say it like this" list is a small addition on top; drop AC-10 if it is not wanted (reversible).
- D-05 Voice settings become a Settings > Voice page and the waveform button leaves the composer. The card links to the page (reversible).
- D-06 The "Managed premium voice · Coming soon" card is removed until there is something to buy (reversible).
- D-07 The phone icon and the word "Call" stay, since the call strip and "Hang up" already use them (reversible).
- D-08 The answer mode and the pronunciation list are stored in the server's `settings.voice`, one value per machine for every project, like the rest of the reply voice. Dictation language and mode stay client settings (reversible).
- D-09 `voiceCallsAllowed` is no longer read. The key stays in the schema so older clients still decode settings (reversible).

### Open
- none

## Tasks

### T-01 Answer mode and pronunciation in the call engine
- AC: AC-06, AC-10 | Files: repositories/anton-abyzov/specwithcode-dev/packages/contracts/src/settings.ts, repositories/anton-abyzov/specwithcode-dev/packages/client-runtime/src/voice-call/speakableText.ts, repositories/anton-abyzov/specwithcode-dev/packages/client-runtime/src/voice-call/controller.ts, repositories/anton-abyzov/specwithcode-dev/packages/client-runtime/src/voice-call/index.ts, repositories/anton-abyzov/specwithcode-dev/packages/client-runtime/src/voice-call/voiceCall.test.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/serverSettings.test.ts | Test: cd repositories/anton-abyzov/specwithcode-dev && node node_modules/vite-plus/bin/vp test run packages/client-runtime/src/voice-call/voiceCall.test.ts apps/server/src/serverSettings.test.ts

### T-02 Dictation starts without the in-app dialog
- AC: AC-03, AC-04 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/VoiceDictation.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/VoiceDictation.test.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/dictationShortcut.test.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/VoiceCall.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/chat/ChatComposer.tsx | Test: cd repositories/anton-abyzov/specwithcode-dev && node node_modules/vite-plus/bin/vp test run apps/web/src/components/studio/VoiceDictation.test.tsx apps/web/src/components/studio/dictationShortcut.test.tsx

### T-03 Named Dictate and Call controls, tips and the Call card
- AC: AC-01, AC-02, AC-05, AC-07 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/VoiceControls.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/VoiceControls.test.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/VoiceCall.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/VoiceCall.test.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/VoiceDictation.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/ProjectWorkspaceSurface.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/shell/voice.css, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/chat/ChatComposer.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/studio/legacyVoiceImport.ts | Test: cd repositories/anton-abyzov/specwithcode-dev && node node_modules/vite-plus/bin/vp test run apps/web/src/components/studio/VoiceControls.test.tsx apps/web/src/components/studio/VoiceCall.test.tsx

### T-04 Settings > Voice page
- AC: AC-08, AC-09, AC-10 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/src/routes/settings.voice.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/routeTree.gen.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/settings/VoiceSettingsPanel.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/settings/VoiceSettingsPanel.test.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/settings/DictationSettings.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/settings/SettingsPanels.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/settings/settingsSearch.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/settings/SettingsSidebarNav.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/VoiceSettings.tsx, repositories/anton-abyzov/specwithcode-dev/docs/voice-calls.md | Test: cd repositories/anton-abyzov/specwithcode-dev && node node_modules/vite-plus/bin/vp test run apps/web/src/components/settings/VoiceSettingsPanel.test.tsx apps/web/src/components/settings/settingsNavGroups.test.ts

### T-05 Headless fixture, light and dark captures
- AC: AC-11 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/tests/voice-ux/index.html, repositories/anton-abyzov/specwithcode-dev/apps/web/tests/voice-ux/main.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/tests/voice-ux/mocks.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/tests/voice-ux/vite.config.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/tests/voice-ux/verify.mjs, repositories/anton-abyzov/specwithcode-dev/apps/web/tests/coordinator-call-readiness/mocks.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/tests/coordinator-call-readiness/verify.mjs, repositories/anton-abyzov/specwithcode-dev/apps/web/tests/dictation-shortcut/mocks.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/tests/dictation-shortcut/verify.mjs, repositories/anton-abyzov/specwithcode-dev/AGENTS.md | Test: cd repositories/anton-abyzov/specwithcode-dev && node node_modules/vite-plus/bin/vp build --config apps/web/tests/voice-ux/vite.config.ts && node apps/web/tests/voice-ux/verify.mjs ../../../.specweave/increments/1300-clear-voice-controls-dictate-and-call-say-what-they-do-dictation-needs-no-setup-reply-voice-settings-reframed/reports/fixture

### T-06 Verify and close 1300
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08, AC-09, AC-10, AC-11 | Files: .specweave/increments/1300-clear-voice-controls-dictate-and-call-say-what-they-do-dictation-needs-no-setup-reply-voice-settings-reframed/spec.md | Test: cd repositories/anton-abyzov/specwithcode-dev && node node_modules/typescript/bin/tsc --noEmit --project apps/web/tsconfig.json && cd apps/web && node ../../node_modules/vite-plus/bin/vp build
