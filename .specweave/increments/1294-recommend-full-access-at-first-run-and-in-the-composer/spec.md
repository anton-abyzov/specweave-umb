# Recommend Full access at first run and in the composer

## Problem

A fresh SpecWithCode install starts every chat in Supervised: the machine setting `defaultRuntimeMode` decodes to `approval-required` (`packages/contracts/src/providerPolicy.ts:32`, `packages/contracts/src/settings.ts:1795`). The agent then stops before each command and file change, and work waits for the person. Nothing during setup says so. The first-run wizard (`apps/web/src/components/onboarding/WelcomeWizard.tsx`) has the steps role, connection, agents and import, and none of them mentions access. The only way to learn about Full access is the small access chip in the composer, the "Switch chat to Full access" action on an approval card after the agent has already stopped, or Settings > General > New threads > Permissions.

Anton, November 11, 2026: "It would be great to recommend to the user that he switch to full access when he starts, because he provides this by default. But we shall somehow highlight it or do onboarding once a user installs it."

Earlier work left the default alone on purpose: 1050 recorded that the product default is a product decision, and 1260 kept `DEFAULT_RUNTIME_MODE` out of scope. PR #1142 made the access chip the last composer control to fold away and tinted it for Full access, but it stays neutral in Supervised, which is the state a new user is in.

## Scope

In: the web and desktop app (`apps/web`). A new Access step in the first-run wizard for a main machine. A one-time highlight on the composer's access chip with a short callout. One shared plain-language explanation of what Full access allows. One click to accept, one click to decline, and the answer remembered. The nine interface languages. A headless fixture with light and dark captures.

Out: changing `DEFAULT_RUNTIME_MODE` or what any access mode does; the mobile and native iOS apps; project overrides and existing chats (an accept never rewrites them); team rules; the approval card's existing "Switch chat to Full access"; the wizard's frame, stage bar, footer and other steps (1297).

## Acceptance Criteria

- [ ] AC-01: On a first run, the wizard shows an Access step after Agents and before Projects, as the Access stage of the bar 1297 defines (Sign in, Your machines, Agents, Access, Projects). The step names Full access as recommended, lists what it allows (run terminal commands, create, change and delete files on this machine, use the network and connected tools), says what still stops (the person's decisions, sign-ins, app approvals such as sending email), and describes Supervised in one sentence.
- [ ] AC-02: "Use Full access" is one click: it saves `defaultRuntimeMode: "full-access"` on every machine being set up, records the answer and moves to Projects. The first new chat after setup starts on Full access with the tinted chip.
- [ ] AC-03: "Keep Supervised" is one click: it changes no access setting, records the answer and moves to Projects. Neither the step nor the composer highlight appears again.
- [ ] AC-04: When no answer is recorded (setup closed early, "Decide later", or an install from before this change) and a new chat would start below Full access, the composer's access chip carries an accent ring and dot, and a callout anchored to it shows the same explanation with "Switch to Full access" and "Keep Supervised". Switching sets this chat and the machine default to Full access and shows a notice with Undo. Keep Supervised, the close button and Escape all decline.
- [ ] AC-05: The answer survives a restart and the recommendation is never shown a second time. It is not shown at all when new chats already start on Full access, when the project has its own permissions setting, when team rules cap access below Full access, when the chat's provider does not offer Full access, on a started chat, or on an older install whose saved first-run role is "joined".
- [ ] AC-06: If saving the setting fails, the step or callout says so, stays open and records no answer.
- [ ] AC-07: The step and the callout pass in light and dark at desktop width and 390 px with no horizontal scroll, are reachable and operable by keyboard with focus starting on the recommended action, and every new string exists in all nine language files.

## Approach

Mockups (static HTML, not app code) and headless captures are in `reports/mockups/`:

- `reports/mockups/first-run-access-step-light.png`, `reports/mockups/first-run-access-step-dark.png`
- `reports/mockups/first-run-access-step-phone-light.png`, `reports/mockups/first-run-access-step-phone-dark.png`
- `reports/mockups/composer-recommendation-light.png`, `reports/mockups/composer-recommendation-dark.png`
- `reports/mockups/composer-after-accept-light.png`, `reports/mockups/composer-after-accept-dark.png`
- Source: `reports/mockups/mockup.html` (`?view=wizard|composer|accepted&theme=light|dark`), captured with `reports/mockups/shoot.mjs`.

How it works today:

- `FirstRunGate` sends a fresh install to `/welcome`; `WelcomeWizard` runs role → connection → agents → import. Since PR #1095, "Decide later" and the close button finish onboarding with nothing chosen.
- A new chat's mode is the composer's choice, else the started chat's stored mode, else the resolved default (`ChatView.tsx:2702`): project override, else the machine's `defaultRuntimeMode`, and for a chat on another machine the main machine's default (`chat/draftRuntimeMode.ts`, PR #1142). Team rules clamp it.
- The chip and its menu are `ComposerFooterModeControls` in `chat/ChatComposer.tsx:1303`; labels and descriptions are in `chat/runtimeModeConfig.ts`.

Changes, in order:

1. Contracts: add client setting `fullAccessRecommendation: null | "accepted" | "declined"` (decoding default `null`) next to `whatYouCanDoDismissed` in `packages/contracts/src/settings.ts`, plus its patch key.
2. Logic: new `apps/web/src/onboarding/accessRecommendation.logic.ts` with one pure function that decides whether to recommend, from the recorded answer, the effective default mode, whether the project has its own `defaultRuntimeMode`, the team rules ceiling, the provider's available modes, and whether the chat has started. New `apps/web/src/onboarding/accessRecommendation.ts` holds the accept and decline actions: accept writes `defaultRuntimeMode` through the existing settings update for each target machine, then records the answer; decline only records it.
3. Shared copy: new `apps/web/src/components/onboarding/FullAccessExplanation.tsx` renders the "what it allows" list once, used by the step and the callout so the two can never drift.
4. Wizard, after 1297 T-09 merges: new `apps/web/src/components/onboarding/AccessStep.tsx`, registered as one entry in the stage list T-09 builds, between Agents and Projects. It uses T-09's shared frame and footer (Back, "Keep Supervised" as the skip action, "Use Full access" as the primary with the Enter label) and adds no frame, bar or footer of its own. `WelcomeWizard.tsx` gains only that entry and the two handlers. The stage is left out of the list when the logic says not to recommend.
5. Composer: new `apps/web/src/components/chat/AccessRecommendation.tsx` (callout and chip accent). `ChatComposer.tsx` and `ChatView.tsx` get wiring only: one prop into `ComposerFooterModeControls` and the accept handler, which reuses `handleRuntimeModeChange("full-access")` for the chat.
6. Strings: `wizard.access.*` keys in `apps/web/src/i18n/messages/{en,de,es,fr,ja,ko,pt,ru,zh}.ts`; the callout uses the same keys.
7. Fixture: `apps/web/tests/access-recommendation/` renders the real step and the real callout with mock settings, and `verify.mjs` captures light and dark at 1100 and 390 px and asserts focus, overflow and both actions.

Rejected: changing `DEFAULT_RUNTIME_MODE` to Full access (silent, and 1050 and 1260 kept it a deliberate choice); a blocking modal after setup (the owner asked for a highlight, and a modal over the first chat reads as an error); storing the answer on the server (a new server setting meets version skew with older workers, and an accept is already visible to every client through `defaultRuntimeMode`); putting the question on the role step (a joined machine takes its access from the main machine's grant).

Risks: recommending Full access to someone who chose Supervised on purpose. Mitigation: asked once, an explicit project setting or team rule suppresses it, and D-03 can turn it off for existing installs. Copy must stay true as modes change; the shared component and a test that compares the listed items against `runtimeModeConfig` guard that.

## Decisions

### Asked
- none (the owner's request fixed the direction: recommend, highlight, onboard once)
### Defaulted (change any before sw-do)
- D-01 The answer is a client setting; an accept also sets the machine default. A decline is therefore remembered per app install, and a second client of the same machine can ask once more (reversible).
- D-02 Accept sets the machine default only. Project permission settings and existing chats are never changed (reversible).
- D-03 Installs from before this change that still default to Supervised see the composer highlight once. Flip to "fresh installs only" by gating on `onboardingCompletedAt` being newer than the release (reversible).
- D-04 The step sits after Agents, so the person has seen which agents will get the access (reversible).
- D-05 Undo on the notice restores the previous default and chat mode and records a decline, so it is not asked again (reversible).
- D-06 The chip accent uses the primary color, not the warning tint; the tint stays the mark of Full access being on (reversible).
- D-07 Order with 1297 (coordinator, November 12, 2026): 1297 T-09 lands first. It splits `WelcomeWizard.tsx` into one file per step with a shared frame and a stage bar built from a list; this increment then adds Access as one stage entry. This replaces 1297's earlier note that 1294 lands first. T-01 and T-03 touch no wizard file and do not depend on T-09; T-02 and T-04 do. The wizard mockup shows the old four-stage bar and the old two-button row; the step's content is what counts, the frame is 1297's.
### Open
- none

## Tasks

### T-01 Answer setting and recommendation logic
- AC: AC-03, AC-05, AC-06 | Files: repositories/anton-abyzov/specwithcode-dev/packages/contracts/src/settings.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/onboarding/accessRecommendation.logic.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/onboarding/accessRecommendation.logic.test.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/onboarding/accessRecommendation.ts | Test: cd repositories/anton-abyzov/specwithcode-dev && node node_modules/vite-plus/bin/vp test run apps/web/src/onboarding/accessRecommendation.logic.test.ts

### T-02 Access step in the first-run wizard (after 1297 T-09 merges)
- AC: AC-01, AC-02, AC-03, AC-06 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/onboarding/AccessStep.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/onboarding/FullAccessExplanation.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/onboarding/WelcomeWizard.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/onboarding/WelcomeWizard.access.test.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/i18n/messages/en.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/i18n/messages/de.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/i18n/messages/es.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/i18n/messages/fr.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/i18n/messages/ja.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/i18n/messages/ko.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/i18n/messages/pt.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/i18n/messages/ru.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/i18n/messages/zh.ts | Test: cd repositories/anton-abyzov/specwithcode-dev && node node_modules/vite-plus/bin/vp test run apps/web/src/components/onboarding/WelcomeWizard.access.test.tsx apps/web/src/components/onboarding/WelcomeWizard.test.tsx

### T-03 Composer highlight and callout
- AC: AC-04, AC-05, AC-06 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/chat/AccessRecommendation.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/chat/AccessRecommendation.test.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/chat/ChatComposer.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/ChatView.tsx | Test: cd repositories/anton-abyzov/specwithcode-dev && node node_modules/vite-plus/bin/vp test run apps/web/src/components/chat/AccessRecommendation.test.tsx apps/web/src/components/chat/unifiedPermissions.test.tsx

### T-04 Headless fixture, light and dark captures
- AC: AC-07 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/tests/access-recommendation/index.html, repositories/anton-abyzov/specwithcode-dev/apps/web/tests/access-recommendation/main.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/tests/access-recommendation/vite.config.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/tests/access-recommendation/verify.mjs, repositories/anton-abyzov/specwithcode-dev/AGENTS.md | Test: cd repositories/anton-abyzov/specwithcode-dev && node node_modules/vite-plus/bin/vp build --config apps/web/tests/access-recommendation/vite.config.ts && node apps/web/tests/access-recommendation/verify.mjs ../../../.specweave/increments/1294-recommend-full-access-at-first-run-and-in-the-composer/reports/fixture

### T-05 Verify and close 1294
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07 | Files: .specweave/increments/1294-recommend-full-access-at-first-run-and-in-the-composer/spec.md | Test: cd repositories/anton-abyzov/specwithcode-dev && node node_modules/typescript/bin/tsc --noEmit --project apps/web/tsconfig.json && cd apps/web && node ../../node_modules/vite-plus/bin/vp build
