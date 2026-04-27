---
status: completed
---
# Studio IA redesign + cleanup follow-ups (0792)

## Context

Increment 0791 (model-threading + SKILL.md content fix) shipped as vskill 1.0.1. During that investigation a research team identified four leftover items. This increment addresses three of them as code changes; the fourth (regenerating eval assertions) is a manual follow-up documented at the end.

**Source repo:** `repositories/anton-abyzov/vskill/` (umbrella child)
**Distribution:** publish vskill 1.0.2 once all ACs pass.

## Problem

Skill Studio is mid-refactor: a previous engineer demoted History/Leaderboard/Deps from top-level tabs into Run sub-tabs but didn't finish the cut. The seams produce three real defects:

1. **Conceptual confusion** — Tests/Run/Trigger are three top-level tabs that all dispatch evaluation runs but split the user's mental model across "WHAT to test" vs "HOW to run." Every run path writes to one shared history store, but three different surfaces display slices of it with inconsistent labels.
2. **Sub-tab discoverability** — History and Models sub-tabs under Run are clickable in code but visually inert (transparent border, 12px font, no hover). Plus a latent risk: `RightPanel.tsx:783` defaults `onSubChange` to a no-op, so if any render path picks the prop-driven branch over the integrated path, clicks become silent no-ops.
3. **Backend type mismatch** — frontend per-case path sends `{ baseline_only: true }`, backend reads `body?.mode === "baseline"`. Baseline runs from the per-case endpoint silently get recorded as `type: "benchmark"` and use the skill prompt instead of the baseline prompt.

## Goals

- Collapse the 6 top-level tabs (Overview / Edit / Tests / Run / Trigger / Versions) into 4 (Overview / Edit / Run / History) reflecting the user's actual workflow: Authoring → Execution → Evidence.
- Fix sub-tab discoverability and the latent no-op default.
- Fix the baseline payload contract so per-case baseline runs are correctly typed.

## Non-goals

- Regenerating `evals.json` assertions to use regex/substring matching. Documented as a manual follow-up at the end of this spec.
- Changing the eval-server data model (history store schema, BenchmarkResult shape).
- Visual restyling beyond what's needed for the new tab structure.
- Mobile/responsive support beyond what already exists.

## User Stories

### US-001 — Unified IA: 4 tabs replacing 6

**As** a Skill Studio user
**I want** Tests, Run, and Trigger consolidated into a single execution surface and a unified History timeline
**So that** I can clearly distinguish authoring (Edit), execution (Run), and evidence (History) without re-deriving the mental model each session.

**Acceptance criteria:**
- [x] AC-US1-01: The top-level tab bar shows exactly four tabs: Overview, Edit, Run, History (no Tests, no Trigger, no Versions).
- [x] AC-US1-02: Edit tab embeds eval-case authoring (the previous Tests-tab content) as a section within the existing editor surface, accessible without leaving Edit.
- [x] AC-US1-03: Run tab is a single dispatcher with three modes — Benchmark, Activation, A/B — surfaced as inline mode controls, not nested sub-tabs. The previous Trigger-tab content (activation testing) is reachable here.
- [x] AC-US1-04: History tab unifies the previous Run/History sub-tab + Models leaderboard + Versions tab. Models leaderboard is a *view* (filter + grouping) on the unified history; Versions is a *filter chip*.
- [x] AC-US1-05: All previously functional panels (RunPanel, HistoryPanel, LeaderboardPanel, ActivationPanel, VersionHistoryPanel, TestsPanel) continue to render their existing content; only the routing/shell changes.
- [x] AC-US1-06: URL deep-links honored — `?tab=run`, `?tab=history`, `?tab=edit`, `?tab=overview` mount the corresponding tab. Old `?tab=tests` and `?tab=trigger` redirect to `?tab=run`; old `?tab=versions` redirects to `?tab=history&filter=versions`.
- [x] AC-US1-07: No regressions in: model-selector wiring (1.0.1 fix), benchmark recording, activation classification, version listing.

### US-002 — Sub-tab discoverability + latent no-op default

**As** a user clicking around Skill Studio
**I want** every clickable sub-tab to look clickable and never be a silent no-op
**So that** I can trust what the UI shows me.

**Acceptance criteria:**
- [x] AC-US2-01: Inactive sub-tabs render with at least 13px font, a non-transparent bottom border (uses `var(--border-subtle)` or equivalent), and a hover state with `cursor: pointer` plus a background color change.
- [x] AC-US2-02: The no-op default for `onSubChange` in `RightPanel.tsx` is replaced with a `console.warn` that fires (in dev builds) when it's invoked, so silent breakage is observable.
- [x] AC-US2-03: A Playwright test clicks each sub-tab present in the redesigned IA, asserts the URL updates, and asserts the panel mounts.

### US-003 — Baseline payload contract aligned

**As** a developer running per-case baseline tests
**I want** baseline runs to actually use the baseline prompt and be recorded with `type: "baseline"`
**So that** baseline data isn't silently mislabeled as benchmark data.

**Acceptance criteria:**
- [x] AC-US3-01: Frontend `WorkspaceContext.runCase` and `runAll` send `{ mode: "baseline" }` (instead of `{ baseline_only: true }`) when `mode === "baseline"`.
- [x] AC-US3-02: Backend `/api/skills/:plugin/:skill/benchmark/case/:evalId` continues to accept `{ mode: "baseline" }` (no change needed) and the `baseline_only` field is removed from the body type. (Verified: handler body type at api-routes.ts:3050 is `{ mode?, bulk?, provider?, model? }`; zero `baseline_only` references in src/eval-server/ or src/eval/.)
- [x] AC-US3-03: A new vitest case verifies that posting `{ mode: "baseline" }` to the per-case handler results in a recorded entry with `type: "baseline"` (not `"benchmark"`).
- [x] AC-US3-04: Existing benchmark/baseline integration tests still pass.

## Out of scope (manual follow-up for Anton)

**Eval assertion brittleness.** All assertions in `~/Projects/TestLab/hi-anton/skills/hi-anton/evals/evals.json` check exact strings (e.g., "begins with the exact string 'HI Anton'"). LLM phrasing variation will continue to cause flaky pass/fails. Two paths:
- (a) Run "Generate Evals" from the Studio Edit tab once the redesign ships, then review the new assertions for intent fidelity.
- (b) Loosen assertions manually to substring/regex form (e.g., the assertion runner could accept `regex:^HI Anton`).

Path (a) is recommended — Anton owns the eval intent and has API quota; programmatic regen without his explicit ack is a bad pattern.

**Obsoleted Playwright specs migrated in this increment.** During T-021's full-suite run, three pre-existing specs flipped to fail because they asserted against removed IA elements. testing-agent migrated all three in-place during a closure-cleanup pass:
- `e2e/qa-click-audit.spec.ts:85` — now navigates `?tab=history&view=versions` via History tab + Versions view chip. ✓ passing.
- `e2e/qa-click-audit.spec.ts:384` — same migration. ✓ passing.
- `e2e/tests-panel.spec.ts` (all 3 specs) — helper `openEvalCasesDisclosure(page)` clicks `detail-tab-edit`, expands `editor-eval-cases-section`, then specs scope filter/badge/case-list assertions to `[data-testid="editor-eval-cases-body"]`. ✓ all 3 passing.

Net Playwright delta: 81→85 pass, 50→48 fail. Remaining 48 failures are pre-existing environmental (lm-studio-smoke needs local LM Studio, eval-ui.spec.ts:168 load-time budget) — none attributable to 0792.

## Technical notes

- **Source repo:** `repositories/anton-abyzov/vskill/`. Increment file lives at umbrella root (`specweave-umb/.specweave/increments/0792-...`) per umbrella increment-placement rule; `metadata.project = "vskill"` routes context.
- **Release vehicle:** publish vskill 1.0.2 after closure.
- **No public API changes:** `/benchmark/case/:evalId` accepts `{ mode: "baseline" }` already; we're just removing dead `baseline_only` reads from the body type.
- **Existing panel components stay unchanged** as content components. Only `App.tsx`/`RightPanel.tsx`/`SubTabBar.tsx`/route effect change.
