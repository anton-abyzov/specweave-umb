---
increment: 0786-studio-disk-truth-fixes
---

# Tasks: Studio UI/Disk-State Truth Fixes

## US-001: Create skill with same name as one just deleted

### T-001: Verify leftover new-test folder cleanup
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [x] completed
**Test Plan**: Given TestLab/hi-anton project → When listing `hi-anton/skills/` → Then `new-test/` is absent (remove if present as part of this step).

---

### T-002: [TDD RED] vitest cases for usePendingDeletion.flushKey
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04 | **Status**: [x] completed
**TDD**: RED
**File**: `repositories/anton-abyzov/vskill/src/eval-ui/src/hooks/__tests__/usePendingDeletion.test.ts`
**Test Plan**:
- Given a pending entry exists for `"plugin/skill"` → When `flushKey("plugin/skill")` is called → Then `apiCall` is invoked once and `isPending("plugin/skill")` returns false.
- Given two pending entries `"p/a"` and `"p/b"` → When `flushKey("p/a")` is called → Then `"p/b"` entry is still pending.
- Given no entry for `"p/missing"` → When `flushKey("p/missing")` is called → Then returns a resolved promise and `apiCall` is NOT invoked (idempotent on missing key).
- Given `flushKey("p/a")` is called while an in-flight commit is ongoing → Then subsequent awaited call resolves cleanly.

---

### T-003: [TDD GREEN] Implement flushKey in usePendingDeletion.ts
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04 | **Status**: [x] completed
**TDD**: GREEN
**File**: `repositories/anton-abyzov/vskill/src/eval-ui/src/hooks/usePendingDeletion.ts`
**Test Plan**: Add `flushKey(skillKey: string): Promise<void>` to `UsePendingDeletionReturn` interface (near lines 29-34). Implement after `flushPending` (near line 109): look up `entriesRef.current.get(skillKey)`; if absent return `Promise.resolve()`; else clear `entry.timeoutId` then `await commit(entry)`. Export `flushKey` in returned object at line 162. All T-002 cases pass.

---

### T-004: Expose flushKey + isPending in StudioContext for pendingDeletion and pendingUninstall
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04 | **Status**: [x] completed
**Files**: `repositories/anton-abyzov/vskill/src/eval-ui/src/StudioContext.tsx`, `repositories/anton-abyzov/vskill/src/eval-ui/src/App.tsx`
**Test Plan**: Given `useStudio()` is called from a child → When provider mounts with pendingDeletion/pendingUninstall hook instances from App.tsx (prop-passthrough approach) → Then `studio.pendingDeletion.flushKey`, `studio.pendingDeletion.isPending`, `studio.pendingUninstall.flushKey`, and `studio.pendingUninstall.isPending` are all functions. StudioContextValue gains 4 new fields; App.tsx forwards them into `<StudioProvider>`.

---

### T-005: [TDD RED] Integration test — pending delete is flushed before useCreateSkill's api.createSkill
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-04 | **Status**: [x] completed
**TDD**: RED
**File**: `repositories/anton-abyzov/vskill/src/eval-ui/src/hooks/__tests__/useCreateSkill.flush.test.ts`
**Test Plan**: Given a `flushPendingForSkillName` mock with a deferred promise → When `handleCreate` is invoked → Then `flushPendingForSkillName` is awaited BEFORE `api.createSkill` runs. Strict call-ordering assertion via shared `callOrder` array. Three cases: happy-path ordering, flush-rejects-skips-create, undefined-flush-still-creates (legacy/no-flush mode). Added during 0786 closure to address code-review F-002 gap.

---

### T-006: [TDD GREEN] Wire flushKey into useCreateSkill submit path
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-03, AC-US1-05 | **Status**: [x] completed
**TDD**: GREEN
**File**: `repositories/anton-abyzov/vskill/src/eval-ui/src/hooks/useCreateSkill.ts`
**Test Plan**: At start of `handleCreate` (around line 631, before `setCreating(true)`): compute `skillKey = \`${effectivePlugin || ""}/${toKebab(name)}\`` (matches server's layout resolution in skill-create-routes.ts:1259-1280). Read `pendingDeletion.flushKey/isPending` and `pendingUninstall.flushKey/isPending` from `useStudio()`. If `pendingDeletion.isPending(skillKey)` → await `pendingDeletion.flushKey(skillKey)`. Same for `pendingUninstall`. Existing 409 `skill-already-exists` recovery branch (lines 648-662) kept verbatim. T-005 cases pass.

---

### T-007: e2e smoke — delete then immediate re-create same name succeeds without 10s wait
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03 | **Status**: [x] completed
**Test Plan**: Manual via `vskill studio` against TestLab/hi-anton. Given Studio is open → When create skill `xtest`, immediately delete it, immediately create `xtest` again → Then second create succeeds without 409 error. Confirm `hi-anton/skills/xtest/` exists after re-create and no deleted folder lingers. Also verify that creating a skill with a completely different name still leaves Undo timer firing after 10s as before.

---

## US-002: Skill-creator and skill-builder install detection ignores marketplace catalog

### T-008: [TDD RED] Revise AC-US2-03 test in skill-creator-detection.test.ts — flip expectation to false
**User Story**: US-002 | **Satisfies ACs**: AC-US2-04 | **Status**: [x] completed
**TDD**: RED
**File**: `repositories/anton-abyzov/vskill/src/utils/__tests__/skill-creator-detection.test.ts`
**Test Plan**: Given existing test around line 100 asserting marketplace-only returns `true` → When test description is updated to "AC-US2-04 (0786): marketplace-only does NOT count as installed — catalog presence is availability, not installation" and assertion flipped to `false` → Then test fails RED (implementation still has the marketplace branch).

---

### T-009: [TDD RED] Add marketplace-only test case to skill-builder-detection.test.ts
**User Story**: US-002 | **Satisfies ACs**: AC-US2-05 | **Status**: [x] completed
**TDD**: RED
**File**: `repositories/anton-abyzov/vskill/src/utils/__tests__/skill-builder-detection.test.ts`
**Test Plan**: Given `~/.claude/plugins/marketplaces/<mkt>/plugins/skill-builder/SKILL.md` exists in tmp HOME with nothing in `pluginCacheDir` → When `isSkillBuilderInstalled()` and `findSkillBuilderPath()` are called → Then both return `false`/`null`. Test fails RED because implementation still checks marketplace dir.

---

### T-010: [TDD GREEN] Drop pluginMarketplaceDir branch from isSkillCreatorInstalled and findSkillCreatorPath
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-04 | **Status**: [x] completed
**TDD**: GREEN
**File**: `repositories/anton-abyzov/vskill/src/utils/skill-creator-detection.ts`
**Test Plan**: Delete `if (agent.pluginMarketplaceDir)` block from `isSkillCreatorInstalled` (lines 61-75) and parallel block from `findSkillCreatorPath` (lines 125-141). Update JSDoc (lines 10-22) to drop step 4b and note marketplace catalog is NOT installation. T-008 case turns GREEN.

---

### T-011: [TDD GREEN] Drop pluginMarketplaceDir branch from isSkillBuilderInstalled and findSkillBuilderPath
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03, AC-US2-05 | **Status**: [x] completed
**TDD**: GREEN
**File**: `repositories/anton-abyzov/vskill/src/utils/skill-builder-detection.ts`
**Test Plan**: Delete `if (agent.pluginMarketplaceDir)` block from `isSkillBuilderInstalled` (lines 69-73). Update JSDoc (lines 21-32) removing "or marketplace dir" mention. Keep `findInPluginTree` helper (lines 79-96) — preserved but no longer invoked with the marketplace root. T-009 case turns GREEN.

---

### T-012: Sharpen agents-registry.ts doc comment — marketplace = available, NOT installed
**User Story**: US-002 | **Satisfies ACs**: AC-US2-06 | **Status**: [x] completed
**File**: `repositories/anton-abyzov/vskill/src/agents/agents-registry.ts`
**Test Plan**: Given `pluginMarketplaceDir` JSDoc at lines 63-66 → When updated to: "Marketplace dir is the catalog of *available* plugins — NEVER use this for installed-status detection. Installed plugins live under `pluginCacheDir`. This field exists so future UI can offer 'Install from marketplace' affordances based on catalog presence." → Then the invariant is unmistakable. No code change required.

---

### T-013: Integration smoke for /api/studio/detect-engines and /api/skill-creator-status
**User Story**: US-002 | **Satisfies ACs**: AC-US2-06, AC-US2-07 | **Status**: [x] completed
**Test Plan**: Manual via `vskill studio` with nothing in `~/.claude/plugins/cache/`. Given Studio is running → When GET /api/studio/detect-engines and GET /api/skill-creator-status are called → Then both return `installed: false`. Engine Selector shows "Install" affordance (not "installed") for both engines. Also run `vitest run` on detection test files to confirm all green.

---

## US-003: Uninstall action gated by skill provenance

### T-014: Verify or add provenance field to SkillInfo type
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02 | **Status**: [x] completed
**File**: `repositories/anton-abyzov/vskill/src/eval-ui/src/types.ts`
**Test Plan**: Given `SkillInfo` shape in types.ts → When checking for `provenance` field near line 134 → Then either note "already present" or add `provenance?: "installed" | "source-authored"` after the existing `origin` field with a comment that it is server-derived from lockfile presence.

---

### T-015: Server-side provenance derivation in GET /api/skills skill-list endpoint
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02 | **Status**: [x] completed
**File**: `repositories/anton-abyzov/vskill/src/eval-server/api-routes.ts`
**Test Plan**: Given skill-list handler (lines 1940-2061) → When updated to read lockfile once before `enriched.map` (`const lock = readLockfile(root); const installedKeys = new Set(Object.keys(lock?.skills ?? {}))`) and add `provenance: installedKeys.has(s.skill) ? "installed" : "source-authored"` inside the map → Then each skill in the response carries correct provenance. Single lockfile read per request; O(1) lookup per skill.

---

### T-016: [TDD RED] vitest case for uninstall handler — not-in-lockfile returns 422 not-installed
**User Story**: US-003 | **Satisfies ACs**: AC-US3-03 | **Status**: [x] completed
**TDD**: RED
**File**: `repositories/anton-abyzov/vskill/src/eval-server/__tests__/api-routes.uninstall.test.ts` (or extend nearest existing test)
**Test Plan**: Given POST /api/skills/:plugin/:skill/uninstall for a skill NOT present in the lockfile → When request is made → Then response status is 422 and body contains `{ code: "not-installed" }`. Test fails RED because current implementation lacks this guard.

---

### T-017: [TDD GREEN] Harden POST /api/skills/:plugin/:skill/uninstall with lockfile-first check
**User Story**: US-003 | **Satisfies ACs**: AC-US3-03, AC-US3-06 | **Status**: [x] completed
**TDD**: GREEN
**File**: `repositories/anton-abyzov/vskill/src/eval-server/api-routes.ts`
**Test Plan**: After path-traversal guard (lines 2685-2690): call `readLockfile(root)` → if skill key absent → return `sendJson(res, { error: "<skill> is not installed", code: "not-installed" }, 422, req); return;`. Existing lockfile-write-failed (500) and trash-failed (500) blocks remain for genuine post-check failures. Dangling 404 fallback (line 2731) kept as defensive guard. Update JSDoc (lines 2666-2674) to document lockfile-first check and 422 contract. T-016 case turns GREEN; confirm real-install uninstall path still works (AC-US3-06).

---

### T-018: DetailHeader.tsx — gate Uninstall/Delete button on skill.provenance
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01 | **Status**: [x] completed
**File**: `repositories/anton-abyzov/vskill/src/eval-ui/src/components/DetailHeader.tsx`
**Test Plan**: Given DetailHeader around line 229 → When updated to show "Delete" when `skill.provenance === "source-authored"` and "Uninstall" when `skill.provenance === "installed"`, with fallback to `origin === "source"` when `provenance` is undefined (legacy) → Then: component test with `provenance: "installed"` → Uninstall present, Delete absent; with `provenance: "source-authored"` → Delete present, Uninstall absent; with `provenance: undefined` → falls back to origin-based rule.

---

### T-019: App.tsx pendingUninstall onFailure — branch on err.details.code === "not-installed"
**User Story**: US-003 | **Satisfies ACs**: AC-US3-04 | **Status**: [x] completed
**File**: `repositories/anton-abyzov/vskill/src/eval-ui/src/App.tsx`
**Test Plan**: Given `pendingUninstall` `onFailure` handler (around line 402) → When `err instanceof ApiError && err.details?.code === "not-installed"` → Then toast reads `"<skill> is a source-authored skill — use Delete instead"` (severity `info`, `durationMs: 4000`) with no Retry action. Any other error falls through to existing generic toast + Retry. Add `import { ApiError } from "./api"` if not already present.

---

### T-020: e2e smoke — hi-anton shows Delete not Uninstall; Delete flow works; real install shows Uninstall
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-04, AC-US3-05, AC-US3-06 | **Status**: [x] completed
**Test Plan**: Manual via `vskill studio`. Given Studio open on TestLab/hi-anton → When hi-anton skill detail page is viewed → Then only "Delete" is shown (not "Uninstall"). Click Delete → source-skill trash flow runs cleanly with 10s Undo. Also: `vskill install <marketplace-skill>` → open that skill in Studio → "Uninstall" is shown → click Uninstall → lockfile entry and on-disk dir are both removed.

---

## Cross-cutting

### T-021: Run full vitest suite — confirm no regressions
**User Story**: US-001, US-002, US-003 | **Satisfies ACs**: AC-US1-01, AC-US2-01, AC-US3-01 | **Status**: [x] completed
**Test Plan**: Given all implementation tasks complete → When `vitest run` is executed in `repositories/anton-abyzov/vskill/` → Then suite passes green with no regressions. Coverage target: 90%.

---

### T-022: Manual verification checklist for all three USs
**User Story**: US-001, US-002, US-003 | **Satisfies ACs**: AC-US1-01, AC-US2-06, AC-US3-01 | **Status**: [x] completed
**Notes**: Cross-cutting sign-off — covered by T-007 (US-001), T-013 (US-002), T-020 (US-003). All three must pass before closure.
**Test Plan**: Given T-007, T-013, and T-020 are individually verified → When reviewed together → Then all three US behaviors confirmed working against live vskill Studio with no observed regressions.
