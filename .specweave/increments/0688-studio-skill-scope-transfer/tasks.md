---
increment: 0688-studio-skill-scope-transfer
title: "Studio Skill Scope Transfer — Task List"
type: feature
status: planned
test_mode: TDD
---

# Tasks — Increment 0688: Studio Skill Scope Transfer

## Foundations

### T-001: Lift copyPluginFiltered to shared module
**User Story**: prereq (no US) | **Satisfies ACs**: (supports all copy operations) | **Status**: [x] completed
**Test Plan**:
  - Given: `copyPluginFiltered` is defined at `src/commands/add.ts:690`
  - When: it is extracted to `src/shared/copy-plugin-filtered.ts` and re-exported from `add.ts`
  - Then: `add.ts` import resolves from shared path; all existing `add`-command tests still pass; `src/studio/lib/scope-transfer.ts` can import the same function without circular dependency
**Files**: `src/shared/copy-plugin-filtered.ts` (new), `src/commands/add.ts` (updated import + re-export)

---

### T-002: Define shared server-side types (StudioOp, Provenance, TransferEvent)
**User Story**: prereq (no US) | **Satisfies ACs**: AC-US4-01, AC-US1-04 | **Status**: [x] completed
**Test Plan**:
  - Given: no shared type file exists for scope-transfer domain on the server
  - When: `src/studio/studio-types.ts` is created with `StudioOp`, `Provenance`, `TransferEvent` types exactly matching the shapes in plan.md §5
  - Then: TypeScript compiler accepts all imports in new route and lib files without `any` usage; existing studio type imports are unaffected
**Files**: `src/studio/studio-types.ts` (new)

---

## US-001: Promote INSTALLED/GLOBAL skill to OWN

### T-003: [TDD-RED] Unit tests for scope-transfer lib (copy + collision guard)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03, AC-US1-04 | **Status**: [x] completed
**Test Plan**:
  - Given: `src/studio/lib/scope-transfer.ts` does not exist
  - When: unit tests are written for `transfer()` covering: happy-path file copy into dest dir, collision detection when dest exists without `overwrite`, collision bypass with `overwrite=true`, and `.vskill-meta.json` being excluded when copying OWN → INSTALLED
  - Then: all tests fail (red) with module-not-found or assertion errors; tmp-dir fixtures used, no real fs mutation
**Files**: `src/studio/lib/__tests__/scope-transfer.test.ts` (new)

### T-004: [TDD-GREEN] Implement scope-transfer lib
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03, AC-US1-04 | **Status**: [x] completed
**Test Plan**:
  - Given: red tests from T-003 exist
  - When: `src/studio/lib/scope-transfer.ts` is implemented with `transfer()`, `CollisionError`, path resolution for OWN/INSTALLED/GLOBAL scopes, and `copyPluginFiltered` imported from `src/shared/copy-plugin-filtered.ts`
  - Then: all T-003 unit tests pass; TypeScript compiles cleanly; `.vskill-meta.json` is never included in copies going out of OWN scope
**Files**: `src/studio/lib/scope-transfer.ts` (new)

### T-005: [TDD-RED] Unit tests for provenance lib (read/write/remove)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04, AC-US3-03, AC-US3-04 | **Status**: [x] completed
**Test Plan**:
  - Given: `src/studio/lib/provenance.ts` does not exist
  - When: tests are written for `writeProvenance`, `readProvenance`, `removeProvenance` covering: write creates valid `.vskill-meta.json` with correct shape, read returns `Provenance` on valid file, read returns `null` on ENOENT without throwing, read returns `null` on JSON parse error without throwing, remove deletes the file
  - Then: all tests fail; tmp-dir fixtures used
**Files**: `src/studio/lib/__tests__/provenance.test.ts` (new)

### T-006: [TDD-GREEN] Implement provenance lib
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04, AC-US3-03, AC-US3-04 | **Status**: [x] completed
**Test Plan**:
  - Given: red tests from T-005 exist
  - When: `src/studio/lib/provenance.ts` is implemented using `writeFileSync` + `JSON.stringify` for write, best-effort `readFileSync` + `JSON.parse` returning `null` on any error (logs to stderr at debug level), `unlinkSync` for remove
  - Then: all T-005 tests pass
**Files**: `src/studio/lib/provenance.ts` (new)

### T-007: [TDD-RED] Integration tests for promote route SSE event sequence
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-03, AC-US1-04 | **Status**: [x] completed
**Test Plan**:
  - Given: `src/studio/routes/promote.ts` does not exist
  - When: integration tests are written asserting: exact SSE event sequence `started → copied → indexed → done`; 409 response with `{ok:false,code:"collision",path}` when dest exists without `?overwrite=true`; `.vskill-meta.json` written to dest dir after copy; SSE uses `initSSE`/`sendSSE` from `sse-helpers.ts` (not raw writes)
  - Then: all tests fail; server started on dynamic port with tmp-dir workspace fixture
**Files**: `src/studio/routes/__tests__/promote.integration.test.ts` (new)

### T-008: [TDD-GREEN] Implement promote route
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-03, AC-US1-04 | **Status**: [x] completed
**Test Plan**:
  - Given: red integration tests from T-007 exist; T-004 and T-006 libs are passing
  - When: `src/studio/routes/promote.ts` is implemented: `POST /api/skills/:plugin/:skill/promote`, calls `transfer()` + `writeProvenance()` + `appendOp()`, streams `started → copied → indexed → done` via `initSSE`/`sendSSE`/`sendSSEDone`, writes provenance sidecar after copy, appends op to log before emitting `done`
  - Then: all T-007 integration tests pass
**Files**: `src/studio/routes/promote.ts` (new)

---

## US-002: Test-install OWN skill into INSTALLED or GLOBAL

### T-009: [TDD-RED] Integration tests for test-install route
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04 | **Status**: [x] completed
**Test Plan**:
  - Given: `src/studio/routes/test-install.ts` does not exist
  - When: integration tests are written asserting: SSE sequence `started → copied → indexed → done`; default dest is INSTALLED (`.claude/skills/<name>/`); `?dest=global` targets `~/.claude/skills/<name>/` (resolved from a test homedir fixture); `.vskill-meta.json` is NOT present in the copied destination; 409 on collision without `?overwrite=true`; no duplicate copy logic — same `copyPluginFiltered` from shared module
  - Then: all tests fail
**Files**: `src/studio/routes/__tests__/test-install.integration.test.ts` (new)

### T-010: [TDD-GREEN] Implement test-install route
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04 | **Status**: [x] completed
**Test Plan**:
  - Given: red tests from T-009 exist
  - When: `src/studio/routes/test-install.ts` is implemented using `transfer()` from scope-transfer lib with `fromScope:"own"`, resolving `toScope` from `?dest` query param (defaults to `"installed"`, uses `"global"` if `?dest=global`), appending op to log, emitting correct SSE sequence
  - Then: all T-009 integration tests pass
**Files**: `src/studio/routes/test-install.ts` (new)

---

## US-003: Undo / Revert with persistent provenance chip

### T-011: [TDD-RED] Integration tests for revert route
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-03, AC-US3-04 | **Status**: [x] completed
**Test Plan**:
  - Given: `src/studio/routes/revert.ts` does not exist
  - When: integration tests are written asserting: SSE sequence `started → deleted → indexed → done`; OWN dir is physically deleted after done; original `promote` op is NOT removed from log (append-only — a new `revert` op is appended instead); 400 returned with `{code:"no-provenance"}` when `.vskill-meta.json` is absent, with no filesystem changes
  - Then: all tests fail
**Files**: `src/studio/routes/__tests__/revert.integration.test.ts` (new)

### T-012: [TDD-GREEN] Implement revert route
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-03, AC-US3-04 | **Status**: [x] completed
**Test Plan**:
  - Given: red tests from T-011 exist; T-006 provenance lib passes
  - When: `src/studio/routes/revert.ts` is implemented: reads provenance via `readProvenance()`, returns 400 `{ok:false,code:"no-provenance"}` if absent (no fs change), deletes OWN dir with `fs.rm(dir, {recursive:true})`, appends `promote-reverted` op to log, emits `started → deleted → indexed → done` SSE sequence
  - Then: all T-011 tests pass
**Files**: `src/studio/routes/revert.ts` (new)

---

## US-004: Ops log + OpsDrawer + StatusBar chip

### T-013: [TDD-RED] Unit tests for ops-log lib (atomic append + subscribe + listOps + tombstone)
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01 | **Status**: [x] completed
**Test Plan**:
  - Given: `src/studio/lib/ops-log.ts` does not exist
  - When: unit tests are written covering: `appendOp` writes exactly one newline-terminated JSON line; 10 concurrent `appendOp` calls produce 10 parseable lines with no interleaving; `listOps` returns ops newest-first filtered by `before` timestamp; `deleteOp` appends tombstone line, and `listOps` excludes tombstoned ids; `subscribe` callback fires on each `appendOp`; tmp-dir fixture overrides log path via env var
  - Then: all tests fail
**Files**: `src/studio/lib/__tests__/ops-log.test.ts` (new)

### T-014: [TDD-GREEN] Implement ops-log lib
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01 | **Status**: [x] completed
**Test Plan**:
  - Given: red tests from T-013 exist
  - When: `src/studio/lib/ops-log.ts` is implemented using `O_APPEND | O_WRONLY | O_CREAT` open flags (POSIX atomic for writes under 4 KiB), in-process `EventEmitter` for subscribers, `listOps` reads file line-by-line filtering tombstones and applying pagination, directory auto-created on first write, log path configurable via `VSKILL_OPS_LOG_PATH` env var (default `~/.vskill/studio-ops.jsonl`)
  - Then: all T-013 tests pass including the concurrent-write test
**Files**: `src/studio/lib/ops-log.ts` (new)

### T-015: [TDD-RED] Integration tests for ops routes (list + SSE stream + delete)
**User Story**: US-004 | **Satisfies ACs**: AC-US4-04, AC-US4-05 | **Status**: [x] completed
**Test Plan**:
  - Given: `src/studio/routes/ops.ts` does not exist
  - When: integration tests written asserting: `GET /api/studio/ops?limit=5` returns at most 5 ops newest-first as JSON; `GET /api/studio/ops?before=<ts>&limit=5` returns ops with `ts < before`; `GET /api/studio/ops/stream` emits SSE `op` events when `appendOp` is called from a concurrent producer during the test; `DELETE /api/studio/ops/:id` tombstones op and subsequent list excludes it; heartbeat `event: heartbeat` sent every 3s on stream
  - Then: all tests fail
**Files**: `src/studio/routes/__tests__/ops.integration.test.ts` (new)

### T-016: [TDD-GREEN] Implement ops routes
**User Story**: US-004 | **Satisfies ACs**: AC-US4-04, AC-US4-05 | **Status**: [x] completed
**Test Plan**:
  - Given: red tests from T-015 exist; T-014 ops-log lib passes
  - When: `src/studio/routes/ops.ts` is implemented: `GET /api/studio/ops` returns paginated JSON from `listOps()`; `GET /api/studio/ops/stream` is a long-lived SSE using `subscribe()` + heartbeat from `sse-helpers.ts`; `DELETE /api/studio/ops/:id` calls `deleteOp()`; routes exported as `registerOpsRoutes`
  - Then: all T-015 integration tests pass
**Files**: `src/studio/routes/ops.ts` (new)

### T-017: Register all new routes in eval-server
**User Story**: US-001, US-002, US-003, US-004 | **Satisfies ACs**: (enables all route ACs) | **Status**: [x] completed
**Test Plan**:
  - Given: promote, test-install, revert, and ops route files exist but are not wired into the server
  - When: `src/studio/routes/index.ts` exports `registerScopeTransferRoutes(router, root)` aggregating all four route registrations; `src/eval-server/eval-server.ts` calls `registerScopeTransferRoutes` alongside existing `registerSkillCreateRoutes(...)` at lines 42-53
  - Then: `curl -X POST http://localhost:<port>/api/skills/p/s/promote` reaches the promote handler; `GET /api/studio/ops` returns JSON; existing routes are unaffected; TypeScript compiles cleanly
**Files**: `src/studio/routes/index.ts` (update), `src/eval-server/eval-server.ts` (update)

---

## Client — Types and API layer

### T-018: Extend client types and API client functions
**User Story**: US-001, US-002, US-003, US-004 | **Satisfies ACs**: AC-US1-01, AC-US1-04, AC-US4-01 | **Status**: [x] completed
**Test Plan**:
  - Given: client `types.ts` and `api.ts` have no scope-transfer types or API functions
  - When: `src/eval-ui/src/types.ts` is extended with `StudioOp`, `Provenance`, `TransferEvent` (mirroring server types from plan.md §5); `SkillInfo` gains `provenance?: Provenance | null`; `src/eval-ui/src/api.ts` gains `promoteSkill`, `testInstallSkill`, `revertSkill`, `listStudioOps` typed client functions
  - Then: TypeScript compiles with no `any` casts introduced; existing imports from `types.ts` are unaffected
**Files**: `src/eval-ui/src/types.ts` (update), `src/eval-ui/src/api.ts` (update)

---

## Client — FLIP motion + useScopeTransfer hook

### T-019: Implement FLIP motion lib and useScopeTransfer hook
**User Story**: US-001, US-002, US-003 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-05, AC-US2-03, AC-US3-01, AC-US3-05 | **Status**: [x] completed
**Test Plan**:
  - Given: no FLIP lib or scope-transfer hook exists on the client
  - When: `src/eval-ui/src/lib/flip.ts` is implemented (~40 lines, WAAPI, `captureRect`/`runFlip`, early-returns when `prefers-reduced-motion: reduce`); `src/eval-ui/src/lib/use-scope-transfer.ts` wraps `useSSE` with `promote`, `testInstall`, `revert` functions: captures rect before SSE, calls `refresh()` on done, defers `runFlip` via `requestAnimationFrame`, calls `toast` with 5s duration and "Undo" action for promote
  - Then: vitest jsdom unit test: when `matchMedia` mocked to return `reduce`, `runFlip` returns without calling `el.animate`; hook unit test: after SSE done, `toast` called with `action.label === "Undo"` and `durationMs === 5000`
**Files**: `src/eval-ui/src/lib/flip.ts` (new), `src/eval-ui/src/lib/use-scope-transfer.ts` (new)

---

## Client — OpsDrawer + useStudioOps hook

### T-020: Implement useStudioOps hook and OpsDrawer component
**User Story**: US-004 | **Satisfies ACs**: AC-US4-02, AC-US4-03, AC-US4-04, AC-US4-05, AC-US4-06 | **Status**: [x] completed
**Test Plan**:
  - Given: no OpsDrawer or ops hook exists on the client
  - When: `src/eval-ui/src/hooks/use-studio-ops.ts` fetches initial 50 ops on mount, subscribes to `GET /api/studio/ops/stream` via native `EventSource`, live-prepends new `op` events to state, exposes `loadMore` that fetches `?before=<last-op-ts>`; `src/eval-ui/src/components/OpsDrawer.tsx` renders a Virtuoso virtualized list (newest first) with expandable rows showing timestamp, source/dest paths, raw op JSON, `role="dialog"` `aria-modal="false"`, focus trap when open, Esc closes and returns focus to chip
  - Then: jsdom test: `EventSource` mock emits one `op` event, component re-renders with new row at top of list; `loadMore` sends `?before=<ts>` request; Esc key dispatch closes drawer
**Files**: `src/eval-ui/src/hooks/use-studio-ops.ts` (new), `src/eval-ui/src/components/OpsDrawer.tsx` (new)

---

## Client — SkillRow, ContextMenu, PromotedFromChip, StatusBar wiring

### T-021: Extend SkillRow with data-skill-id attribute and PromotedFromChip
**User Story**: US-001, US-003 | **Satisfies ACs**: AC-US1-01, AC-US3-02, AC-US3-03 | **Status**: [ ] pending
**Test Plan**:
  - Given: `SkillRow` renders without `data-skill-id` and no provenance chip
  - When: `data-skill-id="${plugin}/${skill}"` is added to the root element of `SkillRow`; `<PromotedFromChip>` component is created rendering source scope label + Revert `<button aria-label="Revert <skill> to <fromScope>">` when `skill.provenance` is present; chip is not rendered when `provenance == null`; Revert button dispatches the `revert` action from `useScopeTransfer`
  - Then: RTL test: row element has correct `data-skill-id`; chip renders for skill with `provenance` set; chip absent when `provenance` is null; Revert button has correct `aria-label`
**Files**: `src/eval-ui/src/components/SkillRow.tsx` (update), `src/eval-ui/src/components/PromotedFromChip.tsx` (new)

### T-022: Extend ContextMenu with promote / test-install / revert items
**User Story**: US-001, US-002, US-003 | **Satisfies ACs**: AC-US1-01, AC-US1-05, AC-US2-01, AC-US3-01 | **Status**: [ ] pending
**Test Plan**:
  - Given: `ContextMenu.tsx` `ContextMenuAction` union and `itemsForSkill` lack scope-transfer actions
  - When: `"promote" | "test-install" | "revert"` added to `ContextMenuAction`; `itemsForSkill` conditionally adds "Promote to OWN" for installed/global skills; "Test-install to .claude/" for own skills; "Revert to INSTALLED" for own skills with provenance only (not shown when `provenance == null`)
  - Then: RTL test: INSTALLED skill menu contains "Promote to OWN"; OWN skill without provenance does NOT contain "Revert"; OWN skill with provenance contains "Revert"; pressing Enter on "Promote to OWN" calls `onAction` with `"promote"`; existing menu items and keyboard navigation unaffected
**Files**: `src/eval-ui/src/components/ContextMenu.tsx` (update)

### T-023: Wire OpsCountChip into StatusBar and OpsDrawer into StudioLayout
**User Story**: US-004 | **Satisfies ACs**: AC-US4-02, AC-US4-06 | **Status**: [ ] pending
**Test Plan**:
  - Given: `StatusBar` has no ops chip; `StudioLayout` RightPanel variant enum does not include `"ops"`
  - When: `<OpsCountChip>` component is created with `role="button"`, `aria-expanded`, `aria-controls="ops-drawer"`, showing session op count from `useStudioOps().ops.length`; mounted in `StatusBar`; `StudioLayout` adds `"ops"` to its RightPanel variant enum and renders `<OpsDrawer>` when variant is `"ops"`; Esc on open drawer closes and returns focus to chip
  - Then: RTL test: clicking OpsCountChip sets `aria-expanded="true"` and renders OpsDrawer; pressing Esc closes drawer and moves focus back to chip; count increments when a new op is live-prepended
**Files**: `src/eval-ui/src/components/OpsCountChip.tsx` (new), `src/eval-ui/src/components/StatusBar.tsx` (update), `src/eval-ui/src/components/StudioLayout.tsx` (update)

---

## Scanner enrichment

### T-024: Enrich skill-scanner with provenance sidecar read
**User Story**: US-001, US-003 | **Satisfies ACs**: AC-US1-04, AC-US3-02, AC-US3-03 | **Status**: [ ] pending
**Test Plan**:
  - Given: skill-scanner returns `SkillInfo` objects without a `provenance` field
  - When: scanner is updated to call `readProvenance(skillDir)` for each skill where `scope === "own"` and attach the result (or `null`) as `SkillInfo.provenance`; a missing or malformed `.vskill-meta.json` must not throw or abort the scan
  - Then: unit test with tmp-dir: scan of OWN dir with valid sidecar returns `{provenance: {promotedFrom:…}}`; scan of OWN dir with no sidecar returns `{provenance: null}`; scan of OWN dir with corrupt JSON returns `{provenance: null}` without throwing
**Files**: `src/eval-server/skill-scanner.ts` (update)

---

## Docs

### T-025: Document studio-ops.jsonl log in README / studio help
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01 | **Status**: [x] completed
**Test Plan**:
  - Given: `~/.vskill/studio-ops.jsonl` is introduced with no user-facing documentation
  - When: a note is added to the vskill studio README (or `src/eval-server/help.ts` if that file provides studio inline help) explaining: file location (`~/.vskill/studio-ops.jsonl`), `StudioOp` schema summary, that log rotation is manual (`mv ~/.vskill/studio-ops.jsonl ~/.vskill/studio-ops.jsonl.bak`), and that lines with `tombstone:true` are soft-deletes visible only in the raw file
  - Then: note is findable without grepping source; no code changes required
**Files**: `repositories/anton-abyzov/vskill/README.md` or `src/eval-server/help.ts` (update, whichever provides studio help)

---

## End-to-end

### T-026: E2E — promote → FLIP → toast Undo → revert
**User Story**: US-001, US-003 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-05, AC-US3-01, AC-US3-05 | **Status**: [x] completed (scaffolded; green pending backend+frontend integration)
**Test Plan**:
  - Given: vskill studio running with a test workspace containing one INSTALLED skill and one OWN skill (without provenance)
  - When: Playwright test right-clicks the INSTALLED skill row → clicks "Promote to OWN" → waits for `done` SSE → asserts row appears in OWN section → toast appears with "Undo" button → clicks "Undo" within 5s → asserts skill is removed from OWN section; keyboard-only sub-path: Tab to INSTALLED row → open context menu via keyboard → Enter on "Promote to OWN" → same assertions; `prefers-reduced-motion: reduce` sub-path: promote completes instantly with no `.animate()` call observed
  - Then: all three sub-paths pass; `npx playwright test e2e/scope-transfer.spec.ts` exits 0
**Files**: `repositories/anton-abyzov/vskill/e2e/scope-transfer.spec.ts` (new)

### T-027: E2E — OpsDrawer live-update and keyboard accessibility
**User Story**: US-004, US-001 | **Satisfies ACs**: AC-US1-02, AC-US4-02, AC-US4-03, AC-US4-04, AC-US4-06 | **Status**: [x] completed (scaffolded; green pending backend+frontend integration)
**Test Plan**:
  - Given: vskill studio running; ops log has at least one existing op from a prior promote
  - When: Playwright test clicks OpsCountChip → asserts OpsDrawer opens showing existing op rows → triggers a second promote via context menu → asserts new op row live-prepends at top without page refresh → presses Esc → asserts drawer closes and focus returns to OpsCountChip; also verifies `aria-expanded` toggles correctly; for reduced-motion path, Playwright context has `reducedMotion: "reduce"` option set and promote produces no animation class on the landed row
  - Then: all assertions pass; `npx playwright test e2e/scope-transfer.spec.ts` exits 0
**Files**: `repositories/anton-abyzov/vskill/e2e/scope-transfer.spec.ts` (update from T-026)
