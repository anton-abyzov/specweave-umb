# 1243 Support multiple interface languages at install and first run

## Problem
Users must be able to choose their interface language during first run and read the desktop app comfortably in Russian. Existing source already has nine locales, device-local persistence, a welcome-wizard selector and an Appearance selector. Validate and repair gaps rather than build a second localization system. Increment 1038 concerns syntax highlighting, not interface localization.

## Scope
In: existing desktop first-run language choice, later settings changes, website language parity, Russian translation quality and responsive layout. Audit installer-specific language behavior and document platform boundaries. Out: translating user content, agent responses, or provider output; releasing independently of the single dispatcher.

## Acceptance Criteria
- [ ] AC-01: Record current upstream T3 localization evidence at an exact commit and compare website and app locale inventories.
- [ ] AC-02: First run offers native language names, follows the supported system language by default, and persists explicit selection across restart; Settings can change it later.
- [ ] AC-03: Russian welcome, navigation, chat controls and settings use natural translations without clipped actionable labels at 800 and 1440 pixel widths, including light and dark themes.
- [ ] AC-04: Existing locales continue working with English fallback for missing keys and unchanged user content.
- [ ] AC-05: Exact-head Sonnet 5.5 review and required CI pass, changes merge under the project protocol, and the single release dispatcher receives the merge receipt and manual acceptance steps.

## Approach
Reuse apps/web/src/i18n/locale.ts, messages, phrases, components/settings/LanguageSelect.tsx, LanguageSettingRow.tsx and components/onboarding/WelcomeWizard.tsx. Compare website sources before choosing shared terminology. Inspect actual installer packaging before promising an installer language dialog on each platform. Capture headless screenshots and assertions to reports; headless true, PWDEBUG=0, PLAYWRIGHT_HTML_OPEN=never, HTML reporter open never. Do not access statev2.sqlite files.

## Decisions
### Defaulted
- First run is the cross-platform language-selection entry point; preserve the existing device-local preference.
- Reuse nine existing locales: en, ru, es, zh-CN, ja, pt-BR, ko, de, fr; reconcile against the website before changes.
### Open
- Implementation requires an authorized checkout. The shared app checkout remains on fix/chrome-open-no-window, owned by the Chrome recovery worker, with untracked content. Use worktrees is off. No branch switch or separate checkout is authorized; stop before implementation per the request.

## Tasks
### T-01 Audit current localization and website parity
- AC: AC-01 | Files: reports/localization-audit.md | Test: verify cited source commits and locale inventories

### T-02 Repair first-run language and Russian presentation gaps
- AC: AC-02, AC-03, AC-04 | Files: apps/web/src/i18n/, apps/web/src/components/settings/LanguageSelect.tsx, apps/web/src/components/settings/LanguageSettingRow.tsx, apps/web/src/components/onboarding/WelcomeWizard.tsx | Test: pnpm test; pnpm typecheck; headless first-run persistence and Russian layout checks

### T-03 Review, merge and dispatch delivery
- AC: AC-05 | Files: reports/review.md, reports/validation.md | Test: exact-head Sonnet 5.5 SHIP review and direct required CI readback

### T-04 Verify and close 1243
- AC: AC-01, AC-02, AC-03, AC-04, AC-05 | Files: reports/closure.md | Test: specweave verify 1243; fresh-context review; specweave complete 1243

## Manual acceptance after release
On a fresh profile choose Русский in the welcome screen, complete setup, restart, and confirm Russian remains selected. Resize to 800 and 1440 pixels; inspect sidebar, chat composer, settings and dialogs in both themes. Switch to English and System in Appearance and confirm the interface updates without changing conversations.

## Initial evidence
On November 5, 2026 the installed and npm stable SpecWeave versions both report 3.1.21. App checkout HEAD is 9aeef97f42. WelcomeWizard.tsx imports LanguageSelect and renders it at line 310. Upstream T3 main tree at faf9d7354ce78523e3844d341319d0ebe5a5799d is untruncated and has no paths matching i18n, locales, LanguageSelect or language-settings. This is preliminary evidence, not a complete source audit proving absence.
