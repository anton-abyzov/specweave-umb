---
increment: 0480-remove-admin-evals-editor
generated_by: sw:test-aware-planner
by_user_story:
  US-001:
    tasks: [T-001, T-002]
    acs: [AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05, AC-US1-06, AC-US1-07, AC-US1-08, AC-US1-09]
---

# Tasks: Remove Admin Evals Editor

## User Story: US-001 - Remove admin evals editor page and API routes

**Linked ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05, AC-US1-06, AC-US1-07, AC-US1-08, AC-US1-09
**Tasks**: 2 total, 2 completed

---

### T-001: Delete evals editor files and remove nav entry

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05, AC-US1-06, AC-US1-07
**Status**: [x] completed

**Test Plan**:
- **Given** the vskill-platform repo at `repositories/anton-abyzov/vskill-platform/`
- **When** all evals-related files and directories are deleted and the nav entry is removed
- **Then** `grep -r "admin/evals\|eval-content" src/` returns no matches

**Implementation**:
1. `cd repositories/anton-abyzov/vskill-platform`
2. `rm -rf src/app/admin/evals/` (satisfies AC-US1-01, AC-US1-06 partial)
3. `rm -rf src/app/api/v1/admin/evals/` (satisfies AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-06 partial)
4. `rm src/lib/github/eval-content.ts` (satisfies AC-US1-05)
5. `rm src/lib/github/__tests__/eval-content.test.ts` (satisfies AC-US1-06)
6. Edit `src/app/admin/layout.tsx` — remove `{ label: "Evals", href: "/admin/evals", icon: "check-circle" }` from `NAV_ITEMS` (satisfies AC-US1-07)
7. Run `grep -r "admin/evals\|eval-content" src/` — must return no matches

---

### T-002: Verify build and test suite pass

**User Story**: US-001
**Satisfies ACs**: AC-US1-08, AC-US1-09
**Status**: [x] completed

**Test Plan**:
- **Given** T-001 complete (all evals editor files deleted, nav entry removed)
- **When** build and test suite are run in `repositories/anton-abyzov/vskill-platform/`
- **Then** `npm run build` exits 0 and `npx vitest run` exits 0 with no failures

**Implementation**:
1. `cd repositories/anton-abyzov/vskill-platform`
2. `npm run build` — must pass with exit 0 (satisfies AC-US1-08)
3. `npx vitest run` — must pass with exit 0, no test referencing deleted code (satisfies AC-US1-09)
