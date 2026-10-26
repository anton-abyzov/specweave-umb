# Thread chip tooltip tells a usage pre-switch from a limit stop

## Problem

Found October 26, 2026 by the post-merge interaction review of #830 (1041 T-11), `/Users/antonabyzov/.specwithcode/m4/evidence/design-create-reuse-1041/header-chip-hover/post-merge-main/interaction-review.md`.

1. **Pre-switch reads as a limit stop.** #822 (1075) added `modelIdentity.preswitched`: the server moves an idle thread off a model that nears its usage limit and moves it back by itself. The header and row chips now show the fallback glyph for such a thread, and `ThreadModelBadge` ignores the flag, so the tooltip says "Opus 5.5 hit its usage limit. Open the thread to switch back." and the accessible name says "(usage limit)". The composer in the same pane says "Opus 5.5 neared its usage limit…". Repro: `preswitch-repro.log` in the same folder.
2. **The open thread's header points nowhere.** Every fallback tooltip ends with "Open the thread to switch back.", including the header chip of the thread already open, where the way back is the composer's "Back to …" button.

## Scope

In: the fallback copy in `ModelStateTag.tsx` for a pre-switched thread and for the open thread's header; `ThreadModelBadge` passing both facts; the same reason in the sidebar chat row and the composer chip's accessible name (found by the fresh review); unit tests; the headless header fixture; PR, exact-head CI, review, merge and release through the existing release owner.

Out: pre-switch policy and its composer tooltip and banner copy (1075); fallback policy and model-lane rules (1032, 1039, 1003); ChatComposer pending-question, attachment and send-routing paths (1042); whether a pre-switched thread's return is blocked, which the shell does not carry.

## Acceptance Criteria

- [ ] AC-01: For a thread whose shell identity is `preswitched`, the header chip, row chips, sidebar chat row and composer chip's accessible name say "{pick} neared its usage limit, so this thread moved before its next turn." in the tooltip and "(near its usage limit)" in the tip and accessible name, never "hit its usage limit". A launch fallback still reads "no room at launch".
- [ ] AC-02: The open thread's header chip tooltip leaves out "Open the thread to switch back."; row chips keep it for every fallback kind, including a pre-switch.
- [ ] AC-03: Reviewed PR with exact-head CI, merge commit, the release the release owner chooses, and the installed bundle check on that release.

## Approach

- `apps/web/src/components/chat/ModelStateTag.tsx`: the fallback `ModelState` gains `preswitched` and `inOpenThread`; `fallbackModelState` passes them; `modelStateText` picks the reason and leaves out the "open the thread" hint in the open thread. The pre-switch sentence is the first clause of 1075's own `preswitchFallbackDetail` copy, so no new wording is invented; the "goes back on its own" clause is left out because the shell cannot tell whether the return is blocked.
- `apps/web/src/components/studio/shell/ModelBadge.tsx`: `ThreadModelBadge` passes `identity.preswitched` and `header`. `fallbackReason` in `ModelStateTag.tsx` gives the reason words to `StudioSidebar.tsx`, which built its own string, and `ChatComposer.tsx` passes the same flag to `fallbackModelState`.
- Tests: `ModelStateTag.test.tsx`, `ModelBadge.test.tsx`; `apps/web/tests/thread-header-chip` gains `?scenario=preswitch` and checks that the header tooltip never says "Open the thread".

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Separate increment with parent 1041, so 1041 can close on 1.0.95 → yes (reversible).
- D-02 Reuse 1075's clause instead of new pre-switch copy → yes.
### Open
- none

## Tasks

### T-01 Pre-switch and open-thread fallback copy in the thread chips
- AC: AC-01, AC-02 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/fix-1041-model-controls/apps/web/src/components/chat/ModelStateTag.tsx, /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/fix-1041-model-controls/apps/web/src/components/chat/ModelStateTag.test.tsx, /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/fix-1041-model-controls/apps/web/src/components/studio/shell/ModelBadge.tsx, /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/fix-1041-model-controls/apps/web/src/components/studio/shell/ModelBadge.test.tsx, /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/fix-1041-model-controls/apps/web/src/components/studio/shell/StudioSidebar.tsx, /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/fix-1041-model-controls/apps/web/src/components/studio/shell/StudioSidebar.test.tsx, /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/fix-1041-model-controls/apps/web/src/components/chat/ChatComposer.tsx, /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/fix-1041-model-controls/apps/web/tests/thread-header-chip, /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/fix-1041-model-controls/apps/web/tests/thread-row-meta/model-unit.mjs, /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/fix-1041-model-controls/apps/web/tests/thread-row-meta/verify.mjs | Test: vp test run apps/web/src/components/chat/ModelStateTag.test.tsx apps/web/src/components/studio/shell/ModelBadge.test.tsx apps/web/src/components/studio/shell/rowModelFit.test.ts apps/web/src/components/studio/shell/StudioSidebar.test.tsx; headless thread-header-chip and thread-row-meta fixtures
- Branch `fix/header-chip-preswitch-tip` from `origin/main` `b0934915d5`.

### T-02 PR, exact-head CI, review, merge and release
- AC: AC-03 | Files: /Users/antonabyzov/.specwithcode/m4/evidence/design-create-reuse-1041/header-chip-hover/preswitch-tip | Test: gh pr checks on the exact head; merge commit; released version readback; installed bundle check

### T-03 Verify and close 1088
- AC: AC-03 | Files: /Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1088-thread-chip-tooltip-tells-a-usage-pre-switch-from-a-limit-stop/ledger.jsonl | Test: specweave verify 1088; fresh-context review; specweave complete 1088
