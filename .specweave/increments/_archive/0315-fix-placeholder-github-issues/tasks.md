# Tasks: Fix Placeholder GitHub Issue Creation

## Phase 1: TypeScript Guard

### T-001: Add placeholder skip to parseUserStories()
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03 | **Status**: [x] completed
**Test**: Given spec.md with `### US-001: [Story Title] (P1)` → When parseUserStories() runs → Then returns empty array (placeholder skipped)

**File**: `src/sync/external-issue-auto-creator.ts` (line ~340)

After `const title = match[2].trim();` add:
```typescript
// Skip template placeholders (matches github-feature-sync.ts:502)
if (title === '[Story Title]' || /^\[.+\]$/.test(title)) continue;
```

---

### T-002: Add unit tests for placeholder skip
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04 | **Status**: [x] completed
**Test**: Given test spec with mixed real/placeholder titles → When parseUserStories() runs → Then only real titles returned

**File**: `tests/unit/sync/external-issue-auto-creator.test.ts`

Add tests:
- `[Story Title]` exact match is skipped
- `[Some Placeholder]` bracket-only pattern is skipped
- `Queue Search & Filtering (P1)` real title passes through
- Mixed spec with both placeholders and real titles returns only real ones

---

## Phase 2: Bash Guards

### T-003: Add template guard to github-auto-create-handler.sh
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-04 | **Status**: [x] completed
**Test**: Given spec.md containing `[Story Title]` → When handler runs → Then exits with log "Skipping: spec.md still contains [Story Title]"

**File**: `plugins/specweave-github/hooks/github-auto-create-handler.sh`

Changes:
1. After line 51, add: `grep -q '\[Story Title\]' "$SPEC_PATH" && { log "Skipping: template markers found"; exit 0; }`
2. Increase debounce sleep from 10 to 30 (lines 116, 122)

---

### T-004: Fix dispatcher path resolution and add template guard
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02, AC-US2-03, AC-US2-04 | **Status**: [x] completed
**Test**: Given umbrella repo where `${PROJECT_ROOT}/plugins/specweave-github/...` doesn't exist → When dispatcher runs → Then resolves handler via fallback relative path

**File**: `plugins/specweave/hooks/v2/handlers/universal-auto-create-dispatcher.sh`

Changes:
1. Add template guard before dispatch (grep `[Story Title]`)
2. Add fallback path resolution for github handler
3. Increase debounce sleep from 10 to 30

---

## Phase 3: Cleanup

### T-005: Close 11 placeholder issues
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02 | **Status**: [x] completed
**Test**: Given issues #1238-#1248 open → When cleanup runs → Then all 11 issues closed with explanatory comment
