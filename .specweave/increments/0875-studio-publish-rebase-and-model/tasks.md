---
id: 0875-studio-publish-rebase-and-model
totalTasks: 6
completedTasks: 6
testMode: TDD
---

# Tasks: Studio Publish — Rebase, Default Model, Subdir skillPath

All tasks implemented TDD (RED → GREEN proven in commit history), committed, and
released to production (desktop 1.0.58 + 1.0.59).

## US-001: Auto-reconcile a non-fast-forward publish push

### T-001: Auto-reconcile non-fast-forward push (pull --rebase --autostash + retry)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed
**File**: `src/eval-server/git-routes.ts` (makePostGitPublishHandler, isNonFastForward)
**Test Plan (BDD)**: Given a `git push` that fails with a non-fast-forward marker
(`non-fast-forward` / `[rejected]` / `fetch first` / `Updates were rejected`)
→ When the publish handler runs → Then it runs `git pull --rebase --autostash origin
<branch>`, retries `git push`, and on a clean rebase returns success with
`reconciled: true`.
**Test**: `src/eval-server/__tests__/git-routes.test.ts` (17 passing)

### T-002: Structured conflict response on rebase conflict (+ rebase --abort, detached-HEAD skip)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-03 | **Status**: [x] completed
**File**: `src/eval-server/git-routes.ts` (parseConflictFilesFromPull),
`src/eval-ui/src/components/PublishDrawer.tsx` (inline conflict + reconciled note)
**Test Plan (BDD)**: Given a rebase that conflicts → When the handler runs → Then it
collects conflicted paths (`git diff --diff-filter=U`, stdout-parse fallback), runs
`git rebase --abort`, and returns HTTP 200 `{ success:false, conflict:true,
reason:"rebase_conflict", conflictedFiles, error }`; non-conflict rebase failures
(network/auth/autostash) return `reason:"rebase_failed"` with no files and a
reason-aware message + abort-failure warning. The drawer renders the conflicted
files inline (not the generic toast), uses reason-aware toast framing, and appends
"(reconciled with remote)" on the reconciled-success path. Detached HEAD
(branch == "HEAD") is skipped; the retry push after a clean rebase is timeout-guarded.
Hardening: all publish git spawns run with `GIT_TERMINAL_PROMPT=0` (fail fast on
credential prompts in the headless server context); a mid-rebase pre-flight guard
returns HTTP 409 `reason:"mid_rebase"` if a prior reconcile left the tree mid-rebase,
so we never commit onto an interrupted-rebase tree.
**Test**: `src/eval-server/__tests__/git-routes.test.ts` (22 — incl. rebase_failed,
abort-failure, detached-HEAD, retry-timeout, mid_rebase guard) +
`src/eval-ui/src/components/__tests__/PublishDrawer.test.tsx`
(conflict-inline, rebase_failed toast, reconciled-note — passing)

## US-002: Generate-with-AI uses and displays the studio's selected default model

### T-003: Resolve active model from useAgentCatalog and use it for commit-message generation
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02 | **Status**: [x] completed
**File**: `src/eval-ui/src/components/PublishDrawer.tsx`, `src/eval-ui/src/api.ts`
**Test Plan (BDD)**: Given the studio has an active default model selected in the
header picker → When the user clicks "Generate with AI" → Then PublishDrawer passes
the active provider/model (from `useAgentCatalog`) to `api.gitCommitMessage`,
preferring it over the config props; when the catalog has not loaded it falls back to
the config props.
**Test**: `src/eval-ui/src/components/__tests__/PublishDrawerActiveModel.test.tsx` (4 passing)

### T-004: Display which model writes the commit message (AI mode)
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03 | **Status**: [x] completed
**File**: `src/eval-ui/src/components/PublishDrawer.tsx`
**Test Plan (BDD)**: Given AI mode is active → When the drawer renders → Then it shows
"Using <displayName>" with `data-testid="publish-ai-model"`.
**Test**: `src/eval-ui/src/components/__tests__/PublishDrawerActiveModel.test.tsx` (passing)

## US-003: Publish from the Edit tab sends skillPath for subdir skills

### T-005: Resolve and forward repo-relative skillPath from EditorPanel
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01 | **Status**: [x] completed
**File**: `src/eval-ui/src/pages/workspace/EditorPanel.tsx`
**Test Plan (BDD)**: Given a skill that lives under `skills/<name>/` → When the user
publishes from the Edit tab → Then EditorPanel resolves the active skill's `skillPath`
from `useStudio().state.skills` (matching plugin + skill) and forwards it to
PublishButton, so the registry finds `skills/<name>/SKILL.md`.
**Test**: `src/eval-ui/src/pages/workspace/__tests__/EditorPanel.publishSkillPath.test.tsx` (4 passing)

### T-006: Preserve root-level publish when skillPath is unresolvable
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02 | **Status**: [x] completed
**File**: `src/eval-ui/src/pages/workspace/EditorPanel.tsx`
**Test Plan (BDD)**: Given a root-level skill (or one not found in studio state)
→ When the user publishes → Then `skillPath` is `undefined` and the existing
root-level publish behavior is preserved (no regression).
**Test**: `src/eval-ui/src/pages/workspace/__tests__/EditorPanel.publishSkillPath.test.tsx` (passing)
