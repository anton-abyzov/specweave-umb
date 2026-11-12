# Simplified unified settings and model selection

Design increment. No implementation starts until the investigation thread into the silent Devin/Wonder model switch reports its root cause (see Dependency). This spec extends increment 1284, it does not redo it.

## Problem

Anton, November 10 to 12, 2026, in order: (1) Limits by account must scroll and every usage surface must name provider logo, plan and account email with a one-click link to that provider's usage page; (2) the settings concept itself is too verbose, analyze deeply; (3) General settings are huge, long scroll, unclear, the expanded bunch of models when you expand something needs rethinking; (4) why does it choose a Devin model by default when Claude Code subscription was set explicitly; (5) screenshot review: "it doesn't seem really customizable"; (6) investigate why the coordinator showed Claude Code AA provider while Devin was actually selected, then silently landed on Wonder 1.0.

Evidence from this review (code in `repositories/anton-abyzov/specwithcode-dev`, screenshot `/Users/antonabyzov/.specwithcode/m4/userdata/attachments/project-coordinator-1332065e-795b-4f98-91c4-f114917e53f6-6de5f4d3-4a42-493f-aa6e-07333de58582.png`):

- **Screenshot (Providers, Adversarial review).** One uncollapsed "Reviewer order" card lists 3 primary models plus 9 indented "Same model on Cursor / Copilot Enterprise / Copilot personal / Devin" rows, each with a full-width text status badge ("Usage unknown", "Full until Mon 7:00 PM", "Billing unknown"). Customization is only up arrow, down arrow, remove, "Add model". No drag, no collapse, no hide, no grouping. Three stacked sections above and below it repeat 2 to 3 line descriptions. This is the "not really customizable" and "bunch of models" complaint, verbatim in pixels.
- **General is one 1,356-line panel.** `GeneralSettingsPanel` starts at [SettingsPanels.tsx](/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/settings/SettingsPanels.tsx:2295) in a 3,881-line file. Between lines 2295 and 3650 there are 40 `SettingsRow` elements and 40 `description=` props: every row carries prose. Sections: Organization, Behavior, Projects & threads, Confirmations, Text generation, About, Diagnostics, Assistant, plus Team rules and Project defaults stacked on top. Nothing collapses; search is the only shortcut.
- **Providers stacks six model-policy sections under the account list.** [ProviderSettingsPanel.tsx](/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/settings/ProviderSettingsPanel.tsx:1425) appends Model tiers (`ModelLanesSettings.tsx`, 437 lines), Regular and frontier models (179 lines), Adversarial review (356 lines), Decision model (185 lines), Usage sources and Advanced, all in one scroll on top of the provider cards.
- **Model choice has at least eight separate controls/stores.** App default `defaultModelSelection` + `defaultModelProviders` ([settings.ts](/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specwithcode-dev/packages/contracts/src/settings.ts:1661)), project coordinator `coordinatorModelSelection` and "Recommended model for threads" ([ProjectWorkspaceSettings.tsx](/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/ProjectWorkspaceSettings.tsx:559)), per-thread composer picker, worker lanes `modelLanes` (settings.ts:1701), fallback order, reviewer order, decision model, `textGenerationModelSelection`. Each renders differently, so "which provider and account am I on" has a different answer per surface. That fragmentation is what made a Devin default under a Claude Code label possible to miss.
- **Orders already share one list component but it prints everything.** `ModelOrderList` in [FallbackOrderList.tsx](/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/settings/FallbackOrderList.tsx:129) renders alternates always expanded (lines 242 to 274) and status as text badges (lines 112 to 121). The fix is collapsing and icon status in this one component, not a new list per order.

1284 already owns and partly shipped: one-line picker rows with provider logos and status icons (AC-01 to AC-04), smart search (AC-05 to AC-08), the Models popover (AC-09, AC-10), coordinator effort cap (AC-11), machine color (AC-12 to AC-18), Limits scroll (AC-19) and the shared account header with usage links (AC-20 to AC-26). Ledger shows T-01 to T-10 done; T-11 to T-16 (usage surfaces) are the remaining 1284 work. This increment consumes those pieces; duplicating them is out of scope.

## Scope

In:

- General page: keep / move / collapse / delete per the table in Approach; descriptions become one short line or an info tooltip; Advanced collapsed by default.
- A new Settings > Models page holding every model choice; Providers keeps only accounts, auth, enable, usage sources and limits.
- One model-choice control and one order list used by coordinator, new threads, this thread, workers, fallback, reviewer, decision and text generation.
- Order lists become customizable: drag, collapse alternates, hide without deleting, pin, reset.
- Inheritance made visible: App default, then Project (follow or own), then Thread (follow or own); the resolved provider and account show on the composer chip; an explicit user choice is never silently replaced.
- Migration of existing saved settings with no provider rewritten.

Out:

- Anything 1284 already specifies (picker rows, search, popover internals, effort cap values, machine color, account header, usage links). Finish 1284 T-11 to T-16 first.
- The root-cause fix for the Devin default. That is the investigation thread's output; this plan states the guardrails its fix must satisfy (AC-10, AC-11) and blocks on it.
- iPhone settings; release work.

## Acceptance Criteria

- [ ] AC-01: Settings > General opens showing at most 14 rows without scrolling on a desktop window: Organization (2), Behavior (5), Projects & threads (4), plus pinned rows. Every other current General row is under a collapsed "Advanced" disclosure, on its owning page (Models, Assistant, About), or deleted as a duplicate. Section collapse state persists per machine.
- [ ] AC-02: No General row prints a description longer than one line of 90 characters. Longer explanations live in an info-icon tooltip. The strings "Combine matching repositories across environments." style prose paragraphs are gone from the resting page.
- [ ] AC-03: Settings search still finds a collapsed or moved setting and opens its disclosure/page scrolled to it. Existing `searchableSetting` ids do not change, so old links and search terms keep working.
- [ ] AC-04: A new Settings > Models page contains exactly these groups, in this order: Defaults (Coordinator, New threads, Text generation, Decision model), Workers (Everyday lane, Hardest lane), Fallback order, Review (on/off, depth, Reviewer order), Advanced (Regular and frontier models, health-check interval). Providers page ends after Usage sources; no model-policy section remains on it.
- [ ] AC-05: Every model choice on the Models page, in the Models popover (1284 AC-09) and in Project settings is the same control: provider logo, model name, account tag when a provider has 2 or more accounts (1284 AC-23), status icon (1284 AC-02). Clicking any of them opens the same picker, titled for what it sets (1284 AC-10). No surface renders its own model dropdown.
- [ ] AC-06: Fallback, reviewer and both worker lanes use the one `ModelOrderList`. "Same model on X" alternates render collapsed as one chip, "+3 accounts", expanding in place. Default is collapsed, remembered per list. Status is the 1284 status icon with tooltip, not a text badge.
- [ ] AC-07: An order is customizable without deleting: drag handle (with keyboard up/down kept for accessibility), collapse/expand all, per-entry disable (greyed, kept in place, skipped at runtime, shown as disabled in the picker), Add via the AC-05 picker with search, and "Reset to default order" with one-step undo. Screenshot complaint cases all pass: reorder 3 primaries with 9 alternates by drag, hide the Devin alternate, re-enable it, undo a reset.
- [ ] AC-08: Each Defaults row shows its source: "App default", "Project: follow app", "Project: own choice", "This thread: follow project", "This thread: own choice". A project/thread control offers exactly two modes, Follow and Own; Own reveals the AC-05 control. This is the one place follow-vs-own is edited; Project settings and the popover read and write the same record (1284 D-05).
- [ ] AC-09: The composer chip and the Models popover header show the resolved identity as one line: provider logo, model, account tag, and, when inherited, "via Project" or "via App" in the tooltip with the full chain (for example "Muse Code · Opus 5.5 · Max · via App default"). The usage line under the message box uses the same line (extends 1284 AC-23, AC-25).
- [ ] AC-10: An explicit user model choice outranks every default, lane and fallback. Fallback may engage only on a reported limit or unavailable provider, and when it does the thread shows the 1284 AC-24 banner naming the provider and account it left and the one it joined, with one-click "Back to my choice" when the original recovers. Silent substitution fails this AC.
- [ ] AC-11: Guardrail test from the incident: set coordinator explicitly to a Claude Code subscription model, make that provider report a limit, send. Expected: either it runs on the explicit choice, or it stops with the AC-24 banner naming Claude Code. It never runs on Devin (or any other provider) while the chip still shows Claude Code. This test is written against the investigation thread's root-cause fix and must pass before this increment's T-06 starts.
- [ ] AC-12: Migration: on first open after upgrade, existing `defaultModelSelection`, `coordinatorModelSelection`, project thread model, `modelLanes`, fallback and reviewer orders load unchanged (byte-identical selections, same provider instance ids). A normalizer may add the follow/own flag only where a value is absent (absent means Follow). No migration writes a different provider or model; a migration unit test with a Devin-first fallback fixture and a Claude Code explicit coordinator fixture proves both survive untouched.
- [ ] AC-13: Usage consistency stays as 1284 AC-19 to AC-26 specifies and is verified on the new Models page too: Limits by account scrolls, every account header is logo, plan, email, external-link icon to the provider usage page, one dashed-ring "not reported" state, no "Usage not read" / "Billing unknown" text anywhere including Models.
- [ ] AC-14: Headless fixture (headless: true) renders General (resting, Advanced open, search-hit), Settings > Models, each order list collapsed and expanded, and the follow/own control in both modes, light and dark at 390px and desktop; screenshots saved, axe reports no contrast or name violations, and no page requires more than one scroll length at desktop to reach its last group heading via the in-page index.

## Approach

### General page: keep, move, collapse, delete

| Current (SettingsPanels.tsx) | Decision | Where it lands |
|---|---|---|
| Organization: project grouping, project order | Keep, 1-line labels | General, visible |
| Behavior: notifications, input-needed alerts, in-app notifications, keep awake, time format, send shortcut | Keep, merge the 3 notification rows into 1 row with 2 sub-toggles in its popover | General, visible |
| Projects & threads core (working shelf, auto-resume limits) | Keep working shelf; move limit resume/snooze pair to Models Advanced (it is model-limit policy) | Split |
| Confirmations (granular) | Collapse | General > Advanced |
| Response streaming, background activity, voice/dictation detail | Collapse | General > Advanced |
| Text generation model | Move | Models > Defaults |
| Assistant section | Move | Assistant page (already in sidebar) |
| About, Diagnostics | Move | About page / General footer link row |
| Team rules, Project defaults headers stacked on General | Keep but as link rows, not full sections | General top, one line each |
| Every `description=` paragraph | Delete or shrink to 90 chars; rest to info tooltip | All rows |

Customization exposed on General itself: pin any row to a "Pinned" group at top (star on hover, persisted locally), collapse per section, and density stays as-is. That answers "not customizable" for settings without a settings-for-settings page.

### Models page and unification

Extract the five sections at ProviderSettingsPanel.tsx:1425 to 1459 plus Text generation into the Models page (AC-04). Providers keeps accounts/auth/usage. All choices route through one `ModelChoiceField` component built on 1284's picker and popover plumbing; `ModelOrderList` (FallbackOrderList.tsx:129) gains alternate-collapsing, drag and disable, and lanes/reviewer/fallback all consume it (AC-05 to AC-07). Follow/own is one shared `FollowOrOwnModel` control reading the project store (AC-08); resolution chain renders via 1284's account header so provider, plan and email agree everywhere (AC-09, AC-13).

### Dependency (hard gate)

The investigation thread ("why Devin was default under a Claude Code label, then Wonder 1.0") must land its root cause and fix first. Its finding decides where AC-11's guard lives (selection resolution, availability ranking, or fallback engagement). T-01 to T-05 (extraction, collapsing, order customization) do not depend on it and may proceed in parallel; T-06 (follow/own resolution and the AC-10/AC-11 guardrails) is blocked until the investigation reports. If the investigation finds the cause in code this spec planned to move, the move in T-01 rebases on its fix, not the other way round.

### Proposed implementation increments (after this design is accepted)

1. **1310 (this one)** design, then T-01 to T-07 below as its tasks.
2. No separate increments needed unless the investigation's fix is large; if it is, it ships as its own increment and 1310 T-06 references it as a dependency.

### Rejected

- One mega "Advanced" page for everything removed from General: hides model policy next to diagnostics; Models deserves its own page because every incident above is a model-choice incident.
- Deleting worker lanes/fallback/reviewer as "too much": the power is wanted (Anton reorders reviewers); the fault is presentation and duplication, not existence.
- A second simplified picker for settings: two pickers drift; 1284 already unified the picker, this reuses it.
- Rewriting saved settings into a new schema: migration risk with zero user benefit; AC-12 keeps the stores.

Risks: ProviderSettingsPanel.tsx is 1,552 lines and SettingsPanels.tsx 3,881; extraction must be mechanical (move, no behavior change) in T-01 so review stays readable. Alternate-collapsing changes screenshot fixtures from 1284; rerun its verify script.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01: New top-level Settings > Models page instead of keeping model policy on Providers → model choice is the recurring complaint; Providers returns to accounts only. Reversible: it is navigation, stores unchanged.
- D-02: Alternates collapsed by default ("+N accounts" chip) → directly answers the screenshot; one click expands, state remembered.
- D-03: Follow/own is binary (Follow or Own) with no third "suggested" mode → the incident came from ambiguous precedence; two modes are explainable in one tooltip.
- D-04: General keeps at most 14 resting rows; everything else collapses or moves, nothing functional is deleted → simplification is organization, not feature removal.
- D-05: Migration adds flags only where absent and never rewrites a selection → explicit choices outrank defaults, including the migrator.
### Open
- Which exact rows count as the 14 resting General rows if Anton wants different ones pinned by default; pinning (AC-01) makes this per-user, so it does not block.

## Tasks

### T-01 Extract model-policy sections from Providers into Settings > Models (mechanical move)
- AC: AC-04 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/settings/ProviderSettingsPanel.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/settings/ModelSettingsPanel.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/settings/SettingsPanels.tsx | Test: cd repositories/anton-abyzov/specwithcode-dev && pnpm vitest run apps/web/src/components/settings/ProviderSettingsPanel apps/web/src/components/settings/ModelLanesSettings.test.tsx apps/web/src/components/settings/AdversarialReviewSettings.test.tsx

### T-02 General trim: collapse Advanced, move sections, shrink descriptions, pinning
- AC: AC-01, AC-02, AC-03 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/settings/SettingsPanels.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/settings/settingsSearchModel.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/projectSettingsSearch.logic.ts | Test: cd repositories/anton-abyzov/specwithcode-dev && pnpm vitest run apps/web/src/components/settings/settingsSearchModel.test.ts apps/web/src/components/studio/projectSettingsSearch.logic.test.ts

### T-03 One ModelChoiceField everywhere (Defaults, popover, project settings)
- AC: AC-05, AC-09 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/chat/ModelChoiceField.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/shell/ProjectModelsPopover.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/ProjectWorkspaceSettings.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/settings/DecisionModelSettings.tsx | Test: cd repositories/anton-abyzov/specwithcode-dev && pnpm vitest run apps/web/src/components/chat apps/web/src/components/studio/shell/ProjectModelsPopover.test.tsx

### T-04 ModelOrderList: collapsed alternates, status icons, drag, disable, reset with undo
- AC: AC-06, AC-07 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/settings/FallbackOrderList.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/settings/FallbackOrderList.test.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/settings/ModelLanesSettings.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/settings/AdversarialReviewSettings.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/settings/MachineFallbackSettings.tsx | Test: cd repositories/anton-abyzov/specwithcode-dev && pnpm vitest run apps/web/src/components/settings/FallbackOrderList.test.ts apps/web/src/components/settings/ModelLanesSettings.test.tsx apps/web/src/components/settings/AdversarialReviewSettings.test.tsx

### T-05 Migration: follow/own flags only where absent, selections byte-identical
- AC: AC-12 | Files: repositories/anton-abyzov/specwithcode-dev/packages/contracts/src/settings.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/project/ProjectSettingsNormalizer.ts | Test: cd repositories/anton-abyzov/specwithcode-dev && pnpm vitest run apps/server/src/project packages/contracts

### T-06 Follow/own resolution, inheritance chain display, no-silent-switch guard (BLOCKED on investigation root cause)
- AC: AC-08, AC-10, AC-11 | Files: repositories/anton-abyzov/specwithcode-dev/packages/shared/src/coordinatorDefault.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/chat/FallbackStatusCard.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/shell/CoordinatorModelPicker.tsx | Test: cd repositories/anton-abyzov/specwithcode-dev && pnpm vitest run packages/shared/src/coordinatorDefault.test.ts apps/web/src/components/studio/shell/CoordinatorModelPicker.test.tsx

### T-07 Headless fixture: General, Models, orders, follow/own, before and after
- AC: AC-13, AC-14 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/tests/picker-calm/fixture.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/tests/picker-calm/verify-settings.mjs | Test: cd repositories/anton-abyzov/specwithcode-dev && node apps/web/tests/picker-calm/verify-settings.mjs (headless: true; light and dark, 390px and desktop; axe clean)
