# Tasks: Fix skill version default + emission

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started
- `[x]`: Completed
- All paths relative to `repositories/anton-abyzov/vskill/`

---

## Phase 1 — RED (failing tests first)

### T-001: RED — buildSkillMd default-version tests
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02 | **Status**: [x] completed
**File**: `src/eval-server/__tests__/skill-emitter-default-version.test.ts` (NEW)

**Test Plan (Given/When/Then)**:
- **Given** a minimal `BuildSkillMdInput` with `name`, `description`, `layout` and **no `version`**, **When** `buildSkillMdForTest` is invoked, **Then** the returned string contains `version: "1.0.0"` inside the `---` frontmatter block (AC-US2-01).
- **Given** the same input but with `version: ""` (empty string), **When** `buildSkillMdForTest` is invoked, **Then** the output still contains `version: "1.0.0"` (AC-US2-01 edge case).
- **Given** the same input with `version: "2.3.4"`, **When** `buildSkillMdForTest` is invoked, **Then** the output contains `version: "2.3.4"` and not `"1.0.0"` (AC-US2-02).

Initial state: tests fail because current `buildSkillMd` emits no `version:` line when `data.version` is missing/empty.

---

### T-002: RED — save-draft route version-default tests [P]
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03 | **Status**: [x] completed
**File**: `src/eval-server/__tests__/skill-create-routes-save-draft.test.ts` (NEW)

**Test Plan (Given/When/Then)**:
- **Given** a POST to `/api/skills/save-draft` with no `version` field for a non-existent skill, **When** the handler runs, **Then** `SKILL.md` is written with `version: "1.0.0"` in the frontmatter (AC-US1-01).
- **Given** a POST with `version: "3.1.4"`, **When** the handler runs, **Then** `SKILL.md` contains `version: "3.1.4"` (AC-US1-02).
- **Given** an existing draft on disk with `version: "1.2.7"` and a re-save POST with no `version` field, **When** the handler runs, **Then** the new `SKILL.md` preserves `version: "1.2.7"` rather than downgrading to `"1.0.0"` (AC-US1-03).

Use the existing `createMockHandlers` / direct-handler invocation pattern from `skill-update-flow.test.ts:146`. Mock filesystem with `tmpdir()` per test.

Initial state: tests fail because save-draft (`skill-create-routes.ts:1286`) calls `buildSkillMd(body)` with no version, and current emitter omits the line.

---

### T-003: RED — checkDistFreshness helper tests [P]
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04 | **Status**: [x] completed
**File**: `src/eval-server/__tests__/check-dist-freshness.test.ts` (NEW)

**Test Plan (Given/When/Then)**:
- **Given** a tmpdir with `src/eval-server/x.ts` (mtime = now) and `dist/eval-server/x.js` (mtime = now - 60s), **When** `checkDistFreshness(tmpdir)` runs, **Then** it returns `{ stale: true, details: <non-empty> }` (AC-US3-01, AC-US3-02).
- **Given** a tmpdir where dist is newer than src, **When** `checkDistFreshness` runs, **Then** it returns `{ stale: false }` (AC-US3-03).
- **Given** a tmpdir with no `dist/` directory, **When** `checkDistFreshness` runs, **Then** it returns `{ stale: false }` (AC-US3-03).
- **Given** an unreadable path (chmod 000 or non-existent root), **When** `checkDistFreshness` runs, **Then** it returns `{ stale: false }` and never throws (AC-US3-04).

Initial state: helper file doesn't exist — import fails.

---

## Phase 2 — GREEN (minimum implementation)

### T-004: GREEN — buildSkillMd unconditional version + fixtures
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04 | **Status**: [x] completed
**Files**:
- `src/eval-server/skill-create-routes.ts` (lines 239–244)
- `src/eval-server/__tests__/fixtures/skill-emitter-before.md`
- `src/eval-server/__tests__/fixtures/skill-emitter-after.md`

**Implementation**:
1. Replace lines 239–244 of `skill-create-routes.ts` with:
   ```ts
   const version = data.version?.trim() || "1.0.0";
   lines.push(`version: "${version}"`);
   ```
2. Remove the obsolete "golden-file fixtures" comment block.
3. Add `version: "1.0.0"` line to both fixture files (after `name:` if present, else after the opening `---`).
4. Run `npx vitest run src/eval-server/__tests__/skill-emitter-roundtrip.test.ts src/eval-server/__tests__/skill-emitter-spec-compliance.test.ts src/eval-server/__tests__/skill-emitter-default-version.test.ts` — all green.

**Test gate**: T-001 tests pass; existing roundtrip + spec-compliance tests still pass (AC-US2-04).

---

### T-005: GREEN — save-draft resolves version
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03 | **Status**: [x] completed
**File**: `src/eval-server/skill-create-routes.ts` (around line 1286, inside the save-draft handler)

**Implementation**:
1. Before the `buildSkillMd(body)` call at line 1286, insert:
   ```ts
   let resolvedVersion: string;
   if (body.version?.trim()) {
     resolvedVersion = body.version.trim();
   } else if (existsSync(skillMdPath)) {
     resolvedVersion = extractFrontmatterVersion(readFileSync(skillMdPath, "utf-8")) ?? "1.0.0";
   } else {
     resolvedVersion = "1.0.0";
   }
   ```
2. Change `buildSkillMd(body)` → `buildSkillMd({ ...body, version: resolvedVersion })`.
3. Note: `extractFrontmatterVersion` is already imported at the top of the file (line 18). `existsSync`/`readFileSync` are already in use elsewhere in the file.

**Test gate**: T-002 tests pass.

---

### T-006: GREEN — checkDistFreshness helper + eval-server wiring
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04 | **Status**: [x] completed
**Files**:
- `src/eval-server/check-dist-freshness.ts` (NEW)
- `src/eval-server/eval-server.ts` (around line 148)

**Implementation**:
1. Create `check-dist-freshness.ts` exporting `checkDistFreshness(rootDir: string): { stale: boolean; details?: string }`.
   - Walk `src/eval-server/` and `src/utils/`, take newest mtime → `srcMtime`.
   - Walk `dist/eval-server/` and `dist/utils/`, take newest mtime → `distMtime`.
   - If either dir is missing → return `{ stale: false }`.
   - If `srcMtime > distMtime + 1s` (1s tolerance for filesystem precision) → return `{ stale: true, details: ... }`.
   - All errors caught → `{ stale: false }`.
2. In `eval-server.ts:148`, after the port-bind callback fires, call `checkDistFreshness(rootDir)` and if stale, prepend a yellow warning line to the existing banner.
   - Use ANSI yellow `\x1b[33m...\x1b[0m` (codebase already uses ANSI elsewhere).

**Test gate**: T-003 tests pass; manual: edit a `src/` file, restart eval-server, observe banner warning.

---

## Phase 3 — REFACTOR + Verify

### T-007: REFACTOR — extract version-resolution helper (optional, skipped)
**User Story**: US-001, US-002 | **Status**: [x] skipped
**File**: `src/eval-server/skill-create-routes.ts`

**Decision**: Skipped. The create-route and save-draft routes diverge by intent:
- create + update mode + existing → `bumpPatch` (each save = new release)
- save-draft + existing → preserve (each save = iteration on same draft)
- both + no existing → default `"1.0.0"`
- both + explicit body.version → use it

Three paths × two routes = no clean dedup signal. The 6-line block per route is more readable than a generic helper that has to encode the differing semantics.

---

### T-008: VERIFY — full test suite + manual smoke
**Status**: [x] completed

**Test Plan**:
1. `npx vitest run src/eval-server/__tests__/skill-emitter-default-version.test.ts`
2. `npx vitest run src/eval-server/__tests__/skill-create-routes-save-draft.test.ts`
3. `npx vitest run src/eval-server/__tests__/check-dist-freshness.test.ts`
4. `npx vitest run src/eval-server/__tests__/skill-emitter-roundtrip.test.ts`
5. `npx vitest run src/eval-server/__tests__/skill-emitter-spec-compliance.test.ts`
6. `npx vitest run src/eval-server/__tests__/skill-update-flow.test.ts` (regression — create route still asserts `version: "1.0.0"`)
7. `npm run build` — full TypeScript compilation succeeds
8. Manual smoke (documented in spec.md verification section): rebuild → restart studio → create new skill via AI flow → assert `SKILL.md` has `version: "1.0.0"` → AI Edit → assert bump to `1.0.1` → simulate stale dist by `touch src/eval-server/eval-server.ts` then restart → assert yellow stale-dist banner appears.

---

## Dependencies

- T-001, T-002, T-003 are independent — can run in parallel.
- T-004 depends on T-001 (RED before GREEN).
- T-005 depends on T-002.
- T-006 depends on T-003.
- T-007 depends on T-004 + T-005.
- T-008 depends on all of T-004 through T-006 (T-007 optional).
