# Ranked model tiers for everyday and hardest work

## Problem

On November 3, 2026 the project coordinator moved from Claude Code Opus 5.5 to Copilot Enterprise Opus 5.5. The move was correct: the Claude weekly window reached 95% used, the idle pre-switch fired at the default `providerLimitSwitchAtPercent` of 95, Codex (fallback entry 2) was at 100%, and the same model on another provider ("Also served by") took the thread. The user still could not tell this from the settings. A model choice is spread over five overlapping places: Recommended model, Also served by, Fallback order, Only these models and Model lanes (Complex/Routine). Lanes pick a worker's first model but do nothing when it runs out, so a user who ranked "Opus 5.5, then GPT-6 Astra" for hard work had to rank them again in Fallback order. The user asked for ranked lists per kind of work: everyday tasks, and the hardest tasks.

## Scope

In: rename the lanes "Everyday work" and "Hardest work", show Everyday first, and make the two ranked tiers the limit fallback chain when no Fallback order is set, with the thread's own tier first and the same model on other providers before the next rank. "Only these models" applies to tiers. Out: new settings or contract fields, a migration, removing Fallback order, and any change to spending rules.

## Acceptance Criteria

- [ ] AC-01: With an empty Fallback order and tiers set, a limited thread continues on its own tier's ranked models, best first, trying the same model on other enabled providers before the next rank, then the other tier.
- [ ] AC-02: A non-empty Fallback order still wins over tiers, and empty tiers leave today's behavior unchanged.
- [ ] AC-03: "Only these models" stops at the tier chain when tiers are the chain, and the settings row shows when tiers are set.
- [ ] AC-04: Tiers never give spending consent: per-token and Gemini entries from tiers are marked per-token and never auto-picked.
- [ ] AC-05: Settings show "Everyday work" above "Hardest work", Fallback order reads "Uses your model tiers" when it follows them, and the routing chip says "Tiers · Hardest" or "Tiers · Everyday".

## Approach

New `packages/shared/src/modelTiers.ts` holds the tier labels, `tierOfModel`, `tierFallbackOrder` and `effectiveFallbackOrder`. `resolveProviderFallback` and `describeFallbackOrder` in `providerFallback.ts` read the effective order instead of the raw Fallback order, so every server caller gets tiers with no change. The web settings relabel the lanes, show the tier status on Fallback order and the "Only these models" toggle. Rejected: a third "Fallback" tier (it would keep three lists), and replacing Fallback order outright (breaks saved settings).

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Tiers are the fallback chain only when Fallback order is empty (reversible).
- D-02 The same model on other providers comes before the next rank, and the thread's own model leads (reversible).
- D-03 Tiers never give spending consent; paid entries are skipped as today (reversible).
### Open
- none

## Tasks

### T-01 Tier fallback chain in the resolver
- AC: AC-01, AC-02, AC-03, AC-04 | Files: packages/shared/src/modelTiers.ts, packages/shared/src/modelTiers.test.ts, packages/shared/src/providerFallback.ts, packages/shared/src/modelLanes.ts | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/model-tiers/packages/shared && npx vp test run src/modelTiers.test.ts src/providerFallback.test.ts src/modelLanes.test.ts

### T-02 Settings and chip wording
- AC: AC-03, AC-05 | Files: apps/web/src/components/settings/ModelLanesSettings.tsx, apps/web/src/components/settings/ProviderLimitSettings.tsx, apps/web/src/components/settings/ProviderSettingsPanel.tsx, apps/web/src/components/settings/projectOverrideRows.ts, apps/web/src/components/studio/shell/RoutingDecisionChip.tsx, apps/web/src/components/ChatView.tsx | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/model-tiers/apps/web && npx vp test run src/components/settings/ProviderLimitSettings.test.tsx src/components/settings/ModelLanesSettings.test.tsx src/components/studio/shell/RoutingDecisionChip.test.tsx

### T-03 Server regression
- AC: AC-02 | Files: none | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/model-tiers/apps/server && npx vp test run src/orchestration-v2/ProviderFallback src/orchestration-v2/limitFallbackReturn src/project/WorkerLaunchRoom.test.ts src/mcp/OrchestratorMcpTaskRouting.test.ts

### T-04 Report on today's behavior
- AC: AC-01 | Files: /Users/antonabyzov/.specwithcode/m4/evidence/model-tiers-2026-11-03/report.html | Test: manual, report renders headless

### T-05 Ship
- AC: AC-05 | Files: none | Test: PR merged to main, release installed, Settings shows the tiers in the installed app

### T-06 Verify and close 1194
- AC: AC-01, AC-02, AC-03, AC-04, AC-05 | Files: none | Test: specweave verify 1194
