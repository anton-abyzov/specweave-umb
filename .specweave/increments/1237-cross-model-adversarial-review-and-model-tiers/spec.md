# Cross-model adversarial review and model tiers

## Problem

The owner routinely has a second model family (usually Codex GPT-6.1 Sol) adversarially review work another family (usually Claude) built. Today that is manual: open a thread, pick a model, paste a prompt. Nothing in SpecWithCode knows which model wrote the work, so nothing stops a Claude thread from being "reviewed" by Claude through GitHub Copilot. The only review affordance is the PR "Review with" menu (`ReviewWithMenu.tsx`), which lists every ready provider with no family rule, no fallback chain and no automatic trigger. Model tiers exist only as cross-provider lanes ("Everyday work"/"Hardest work", `modelLanes`) and hardcoded regex tiers (`TIER_RULES`), so there is no per-provider "regular vs frontier" model the engine can pick from, and Claude threads default to Fable 5.1 (frontier) for routine work.

## Scope

In (specwithcode-dev):
- Manual "Adversarial review" on a thread (thread menu, command palette) that starts a review thread on a different model family, on the same checkout.
- An `adversarial-review` skill (`.agents/skills/adversarial-review/SKILL.md`) and a self-contained reviewer prompt built by the server, so review works even where the skill is not installed.
- Per-project setting: auto adversarial review when a feature completes (default off).
- Configurable reviewer order, resolved through the existing fallback walker (`describeFallbackOrder`) with a different-family rule; same model on another provider (GitHub Copilot) is tried right after each entry.
- Per-provider model tiers (regular, frontier) with built-in defaults, editable in Settings; review and worker launches use regular unless frontier is asked for or the task lane is "complex".

Out: changing the app-wide default model for new chats; cross-machine reviewers; posting review findings to GitHub; mobile and iOS UI (they ignore the new keys).

## Acceptance Criteria

- [ ] AC-01: Settings decode `adversarialReview` (`autoOnFeatureComplete` false, `reviewers` [], `tier` "regular") and `modelTiers` ({}) from `{}`; both are project-scoped and round-trip through patch and project overrides.
- [ ] AC-02: `tierModelFor` returns a provider's regular or frontier model from user overrides, else built-in defaults (Claude Opus 5.5 / Fable 5.1, Codex GPT-6.1 Sol / GPT-6 Astra, Muse Wonder 1.0 / Wonder Full 1.0), else the same model a provider serves under another name (Copilot), and never a model the provider does not list; frontier falls back to regular.
- [ ] AC-03: `resolveReviewer` walks the reviewer order (explicit list, else the regular-tier default chain Codex, Copilot, Muse, others) through `describeFallbackOrder`, inserts the same model on other providers after each entry, skips entries of the author's model family, the author's instance and unavailable or excluded entries, and reports each skipped entry with its reason.
- [ ] AC-04: A user can start an adversarial review from the thread menu or the command palette; the server resolves the reviewer, launches a new thread on the source thread's checkout with the reviewer prompt, and the UI says which model reviews or why none can.
- [ ] AC-05: With `autoOnFeatureComplete` on, when a thread's run completes and its linked increment has every task done or skipped, exactly one review thread starts for that increment; it never fires for review threads, wake turns, or with the setting off.
- [ ] AC-06: `studio_thread_launch` and `delegate_task` accept `tier: "regular" | "frontier"`; with a provider but no model they launch on that provider's tier model, and a "complex" task lane defaults to frontier.
- [ ] AC-07: Settings show an "Adversarial review" section (auto switch, depth, reviewer order) and a per-provider "Model tiers" editor for regular and frontier models.
- [ ] AC-08: `.agents/skills/adversarial-review/SKILL.md` exists, is discovered as a skill, and the reviewer prompt points to it when installed; findings use severity, `path:line` and never rubber-stamp.

## Approach

Design (half page):

**Data model.** New `packages/contracts/src/adversarialReview.ts`:
`AdversarialReviewSettings = { autoOnFeatureComplete: boolean (false), reviewers: ModelSelection[] (max 8, []), tier: "regular" | "frontier" ("regular") }` and
`ProviderModelTiers = Record<instanceIdOrDriverKind, { regular?: string; frontier?: string }>` (`{}`), plus `DEFAULT_PROVIDER_MODEL_TIERS` keyed by driver kind (claudeAgent, codex, muse). Both are `ServerSettings` keys with decoding defaults, listed in `PROJECT_SCOPED_SERVER_SETTING_KEYS`, `ProjectSettingsOverrides` and `ServerSettingsPatch`, and replaced whole on patch (arrays must be clearable), like `modelLanes`.

**Where settings live.** Environment `settings.json` with per-project overrides, resolved by `resolveProjectSettings` (no migration: sparse write strips defaults). The auto switch is meant to be set per project; reviewer order and tiers inherit from the environment.

**Reviewer chain via fallbacks.** `packages/shared/src/adversarialReview.ts` exports `reviewerChain` and `resolveReviewer`. The chain is the explicit `reviewers` list, else the regular (or frontier) tier model of every enabled provider ordered by family (OpenAI, Meta, Google, xAI, other, Claude). Each entry is followed by the same model on other providers (`sameModelOn`), which is the "Sol via Copilot" step. The chain is passed as `providerLimitFallbackModels` to the existing `describeFallbackOrder`, with the author's instance as `currentInstanceId` and the project's `providerLimitExcludedModels`, so availability, sign-in, usage, per-token and exclusion rules are the fallback system's own. Entries whose `modelFamily` equals the author's (by model, so Claude via Copilot is still Claude) are skipped. First entry with no reason wins; else the first "unverified" one (a provider whose usage is unknown, e.g. Copilot). No parallel fallback system: the walker, reasons and labels (`ORDER_NOTES`) are reused.

**Tiers.** `packages/shared/src/modelTiers.ts` gains `tierModelFor(provider, tier, tiers)`: user override for the instance, then for the driver, then built-in default, verified against the provider's model list with `sameModelOn`; frontier falls back to regular. Launch tools take an optional `tier`; lane "complex" means frontier, everything else regular. The app-wide default model is not changed here (follow-up).

**Server.** `apps/server/src/review/AdversarialReviewService.ts`: `start({threadId, reviewer?, tier?, trigger})` reads the source thread (model, worktree, branch, increment), resolves the reviewer, builds the prompt (`adversarialReviewPrompt.ts`) and calls `ThreadMessageIntake.launchThread` with `existing_worktree`/`root` on the same checkout and a deterministic `commandId`. New RPC `orchestration.startAdversarialReview`. `AdversarialReviewReactor` (modeled on `PromptSuggestionReactor`/`ThreadFinishActionService`) listens for `run.updated` completed, applies the same eligibility filters, reads `readThreadIncrementProgress`, and starts one review per increment (`commandId = adversarial-review:<project>:<increment>`). Review threads launch without an increment link, so they can never trigger another review.

**UI touchpoints.** Thread action menu item "Adversarial review" (header and sidebar share `threadActionMenu.logic.ts`), a command-palette action, and a toast with the chosen reviewer or the skip reasons. Settings: `AdversarialReviewSettings.tsx` (switch, depth select, reviewer order via `FallbackOrderList` + `ProviderModelPicker`) in project settings and Providers; `ProviderModelTiersSettings.tsx` beside "Model tiers".

Rejected: a separate reviewer fallback resolver (duplicates availability rules); a third model lane "frontier" (every `MODEL_LANES` consumer hardcodes two lanes); relying on the skill alone (the app ships no skills, so a missing skill must not break review).

Risks: Codex/Copilot slugs change (tiers verified against live model lists, user-editable); auto review spending quota (off by default, one per increment).

## Decisions

### Asked
- none (owner brief covers the choices; coordinator relay 2026-11-04)
### Defaulted (change any before sw-do)
- D-01 Frontier defaults: Claude Fable 5.1, Codex GPT-6 Astra, Muse Wonder Full 1.0 → editable in Settings.
- D-02 "Feature completes" = a thread run completes and its linked increment has all tasks done or skipped → reversible.
- D-03 Review thread runs on the same checkout, same runtime mode as the source thread, and is told not to edit files.
### Open
- none

## Tasks

### T-01 Settings schema for review and model tiers
- AC: AC-01 | Files: packages/contracts/src/adversarialReview.ts, packages/contracts/src/adversarialReview.test.ts, packages/contracts/src/settings.ts, packages/contracts/src/index.ts, packages/shared/src/serverSettings.ts, apps/web/src/components/settings/projectOverrideRows.ts | Test: node node_modules/vite-plus/bin/vp test run packages/contracts/src/adversarialReview.test.ts

### T-02 Tier resolver and reviewer chain on the fallback walker
- AC: AC-02, AC-03 | Files: packages/shared/src/modelTiers.ts, packages/shared/src/adversarialReview.ts, packages/shared/src/adversarialReview.test.ts, packages/shared/package.json | Test: node node_modules/vite-plus/bin/vp test run packages/shared/src/adversarialReview.test.ts

### T-03 Review service, prompt and RPC
- AC: AC-04, AC-08 | Files: apps/server/src/review/AdversarialReviewService.ts, apps/server/src/review/adversarialReviewPrompt.ts, apps/server/src/review/AdversarialReviewService.test.ts, packages/contracts/src/orchestrationV2.ts, packages/contracts/src/rpc.ts, apps/server/src/ws.ts, apps/server/src/server.ts | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/review/AdversarialReviewService.test.ts

### T-04 Auto review when a feature completes
- AC: AC-05 | Files: apps/server/src/review/AdversarialReviewReactor.ts, apps/server/src/review/AdversarialReviewReactor.test.ts, apps/server/src/server.ts | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/review/AdversarialReviewReactor.test.ts

### T-05 Tier on worker launch tools
- AC: AC-06 | Files: apps/server/src/mcp/toolkits/project/tools.ts, apps/server/src/mcp/toolkits/project/handlers.ts, packages/contracts/src/orchestratorMcp.ts, apps/server/src/mcp/OrchestratorMcpService.ts | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/mcp

### T-06 Settings UI
- AC: AC-07 | Files: apps/web/src/components/settings/AdversarialReviewSettings.tsx, apps/web/src/components/settings/ProviderModelTiersSettings.tsx, apps/web/src/components/settings/AdversarialReviewSettings.test.tsx, apps/web/src/components/settings/ProviderSettingsPanel.tsx, apps/web/src/components/settings/ProjectDefaultsSettings.tsx | Test: node node_modules/vite-plus/bin/vp test run apps/web/src/components/settings/AdversarialReviewSettings.test.tsx

### T-07 Manual trigger in thread menu and command palette
- AC: AC-04 | Files: apps/web/src/components/threadActionMenu.logic.ts, apps/web/src/hooks/useThreadActionMenu.ts, apps/web/src/components/CommandPalette.tsx, packages/client-runtime/src/operations/commands.ts | Test: node node_modules/vite-plus/bin/vp test run apps/web/src/components/threadActionMenu.logic.test.ts

### T-08 adversarial-review skill and docs
- AC: AC-08 | Files: .agents/skills/adversarial-review/SKILL.md, docs/studio/adversarial-review.md, CHANGELOG.md | Test: test -f .agents/skills/adversarial-review/SKILL.md && grep -q "name: adversarial-review" .agents/skills/adversarial-review/SKILL.md

### T-09 Verify and close 1237
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08 | Files: none | Test: bash scripts/studio-verify/typecheck-gate.sh
