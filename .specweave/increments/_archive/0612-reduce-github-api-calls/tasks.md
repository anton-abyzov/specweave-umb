---
increment: 0612-reduce-github-api-calls
---

# Tasks

### T-001: Session label cache
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-03 | **Status**: [x] completed
**Test Plan**:
- Given a label cache utility → When `ensureLabel(repo, label)` is called twice for the same label → Then `gh label create` is called only once
- Given labels cached for repo A → When `ensureLabel(repo B, same-label)` is called → Then `gh label create` is called (no cross-repo leakage)

### T-002: Session milestone cache
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-03 | **Status**: [x] completed
**Test Plan**:
- Given a milestone cache → When `createMilestone()` is called twice with the same title → Then API call happens only once, second returns cached value
- Given milestone cached for feature A → When different feature B milestone is requested → Then API call is made (cache miss)

### T-003: Invert DuplicateDetector Phase 3 guard
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01 | **Status**: [x] completed
**Test Plan**:
- Given default env (no SPECWEAVE_VERIFY_DUPLICATES) → When issue is created → Then Phase 3 verification is SKIPPED
- Given `SPECWEAVE_VERIFY_DUPLICATES=1` → When issue is created → Then Phase 3 verification RUNS
- Given `wasReused=true` → When either env → Then Phase 3 is always skipped (regression)

### T-004: Merge getIssue + getLastComment into GraphQL query
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02 | **Status**: [x] completed
**Test Plan**:
- Given an issue number → When `getIssueWithLastComment(N)` is called → Then returns issue state + labels + last comment body + author in one response
- Given the GraphQL query fails → When fallback is triggered → Then sequential REST calls are used (graceful degradation)

### T-005: skipDuplicateCheck in createEpicIssue
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03 | **Status**: [x] completed
**Test Plan**:
- Given `skipDuplicateCheck: true` → When `createEpicIssue()` is called → Then `searchIssueByTitle()` is NOT called
- Given `skipDuplicateCheck: false` (default) → When `createEpicIssue()` is called → Then `searchIssueByTitle()` IS called (backward compat)

### T-006: AC sync dedup — share issue state
**User Story**: US-002 | **Satisfies ACs**: AC-US2-04 | **Status**: [x] completed
**Test Plan**:
- Given AC checkbox sync runs first → When AC progress sync runs → Then it reuses the issue state from checkbox sync instead of re-fetching
- Given spec.md was already parsed in Step 2 → When Step 5 needs user story IDs → Then it reuses parsed data (no re-read)
