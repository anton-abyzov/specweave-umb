<!-- specweave review: reviewer=gemini-4-neon model=gemini-4-neon family=google author=claude depth=standard repo=repositories/anton-abyzov/specwithcode base=ff2180809e8fa6eb10d57dc204e3654de5a57356 head=71258d549d272fa952c169ed2452c0f3d9dc8d2b at=2026-11-20T06:31:53.108Z -->
# Review: 1422 T-08 translated approval prompts (PR #784)
Verdict: ship · risk: low · 3 files · 0 findings
Reviewer context: new session (Gemini 4 Neon on Copilot Enterprise, reviewing GPT-6.2-Astra on Codex)

Reviewed head: `71258d549d272fa952c169ed2452c0f3d9dc8d2b`
Base: `ff2180809e8fa6eb10d57dc204e3654de5a57356`
PR: `anton-abyzov/specwithcode#784`
Worktree: `/Users/antonabyzov/.specwithcode/m4/worktrees/specweave-umb/fix-device-approval-several-devices/repositories/anton-abyzov/specwithcode`

## Summary

No findings. All three locale edits (`de.ts`, `fr.ts`, `ru.ts`) match the current English approval key in `apps/web/src/components/devices/ConnectDeviceViews.tsx:314-318`, fix the semantic direction so the requesting device's app gains access to the approving host `{machine}`, preserve punctuation, full granting scope, the separate machine-agents choice, and `{machine}`.

## Locale Verification

English source (`apps/web/src/components/devices/ConnectDeviceViews.tsx:314-318`):
`Allow lets that device's SpecWithCode app open {machine} and use its chats and the work they start, terminals, files, settings and sign-ins, and approve or remove other devices. Letting another machine's agents run work here is a separate choice.`

- `apps/web/src/i18n/phrases/de.ts:5393-5394`: Replaces `auf diesem Gerät` with `auf dem anfragenden Gerät`. Matches `Allow: "Erlauben"` (`Mit „Erlauben“`), uses valid dative syntax and German typographic quotes, keeps `{machine}` as object of `öffnen`, preserves all listed capabilities (`Chats und die Arbeit, die sie starten, Terminals, Dateien, Einstellungen und Anmeldungen`, `andere Geräte erlauben oder entfernen`), and keeps the separate machine-agents sentence.
- `apps/web/src/i18n/phrases/fr.ts:5401-5402`: Replaces `de cet appareil` with `de l’appareil qui demande l’accès`. Matches `Allow: "Autoriser"` and the prompt's own `demande l’accès` phrasing, keeps typographic apostrophes (`’`), keeps `d’ouvrir {machine}` and `d’y utiliser`, preserves all capabilities and the separate machine-agents choice.
- `apps/web/src/i18n/phrases/ru.ts:5356-5357`: Replaces `«Разрешить» даёт приложению SpecWithCode на этом устройстве открыть {machine}` with `Если нажать «Разрешить», приложение SpecWithCode на устройстве, с которого пришёл запрос, сможет открыть {machine}`. Matches `Allow: "Разрешить"`, uses valid Russian guillemets and clause punctuation, keeps `{machine}` and `там`/`сюда` direction, preserves all capabilities and the separate machine-agents choice.

The remaining five shipped catalogs (`es.ts`, `pt.ts`, `ja.ts`, `ko.ts`, `zh.ts`) already use unambiguous distal/anaphoric demonstratives (`ese`, `desse`, `その`, `그`, `该`).

## Evidence Checked

- `/Users/antonabyzov/.specwithcode/m4/scratch/2026-11-20-1422-approval-translations/focused.log`: 2 test files, 390 tests passed.
- `/Users/antonabyzov/.specwithcode/m4/scratch/2026-11-20-1422-approval-translations/before.log` and `/Users/antonabyzov/.specwithcode/m4/scratch/2026-11-20-1422-approval-translations/after.log`: `render-approval.mjs` failed for `de`, `fr`, `ru` before the commit and passed for all three after, interpolating `Mac-Test` with no literal `{machine}`.
- Independent re-runs at `71258d549d272fa952c169ed2452c0f3d9dc8d2b`:
  - `bun /Users/antonabyzov/.specwithcode/m4/scratch/2026-11-20-1422-approval-translations/render-approval.mjs`: PASS for `de`, `fr`, `ru`.
  - `vp test run --passWithNoTests --project unit src/components/devices/ConnectDeviceViews.test.tsx src/i18n/i18n.test.ts src/i18n/retiredPhrases.test.ts`: 3 test files passed, 393 tests passed.

Read-only review; no repository files edited.
