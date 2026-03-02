# Tasks: JIRA Sync Plugin Critical Fixes (0403)

---

## Phase 1: Foundation (Critical)

### T-001: Create canonical metadata path module
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [x] completed
**Test**: Given a new shared module `metadata-paths.ts` -> When imported -> Then it exports `CANONICAL_JIRA_KEY_PATH` = `"external_sync.jira.issueKey"` and helper functions `readIssueKey()` / `writeIssueKey()`

### T-002: Unify metadata reads across all plugin files
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-03 | **Status**: [x] completed
**Test**: Given `enhanced-jira-sync.js`, `post-task-completion.sh`, and `jira-spec-commit-sync.ts` -> When they read JIRA issue keys -> Then all three use `readIssueKey()` which checks `.external_sync.jira.issueKey` first, falls back to `.jira.issue` and `.jira.issueKey`

### T-003: Remove SPEC-001 placeholder return
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04 | **Status**: [x] completed
**Test**: Given `enhanced-jira-sync.js:64` -> When no real JIRA key exists in metadata -> Then the function returns `null` (not the placeholder string `"SPEC-001"`)

### T-004: Create JIRA deployment detection module
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02 | **Status**: [x] completed
**Test**: Given a JIRA instance URL -> When `detectDeploymentType()` calls `/rest/api/2/serverInfo` -> Then it returns `{ type: "server", apiVersion: "2" }` for Server/DC or `{ type: "cloud", apiVersion: "3" }` for Cloud

### T-005: Replace hardcoded /rest/api/3 in all files
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03 | **Status**: [x] completed
**Test**: Given `jira-spec-sync.ts`, `jira-epic-sync.ts`, `jira-status-sync.ts`, and `jira-multi-project-sync.ts` -> When building API URLs -> Then all use `apiUrl(instance, path)` from the shared client (zero hardcoded `/rest/api/3` strings remain)

### T-006: Remove self-hosted hard-block from SKILL.md
**User Story**: US-002 | **Satisfies ACs**: AC-US2-04 | **Status**: [x] completed
**Test**: Given `jira-resource-validator/SKILL.md:62-66` -> When a self-hosted JIRA URL is validated -> Then validation passes (hard-block language removed, replaced with "Cloud and Server/DC supported")

---

## Phase 2: Content and Field Compatibility (High)

### T-007: Create content format adapter module
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-05 | **Status**: [x] completed
**Test**: Given markdown/wiki content and API version "3" -> When `toDescription(content, "3")` is called -> Then it returns a valid ADF document object; Given API version "2" -> Then it returns wiki markup string

### T-008: Fix epic and spec description format
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02, AC-US3-03 | **Status**: [x] completed
**Test**: Given `jira-epic-sync.ts:277` and `jira-spec-sync.ts:369` -> When sending descriptions to JIRA Cloud (v3) -> Then the body contains ADF format (not raw wiki markup)

### T-009: Fix status sync comment format
**User Story**: US-003 | **Satisfies ACs**: AC-US3-04 | **Status**: [x] completed
**Test**: Given `jira-status-sync.ts:137` adding a comment -> When targeting JIRA Cloud (v3) -> Then comment body is ADF `{ type: "doc", content: [...] }` (not plain text string)

### T-010: Implement dynamic Epic Link field discovery
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-03, AC-US4-04 | **Status**: [x] completed
**Test**: Given a JIRA instance with Epic Link on `customfield_10025` -> When `discoverEpicLinkField()` queries `/rest/api/*/field` -> Then it returns `"customfield_10025"` and caches the result for subsequent calls

### T-011: Detect Next-gen vs Classic project style
**User Story**: US-004 | **Satisfies ACs**: AC-US4-02 | **Status**: [x] completed
**Test**: Given a Next-gen project -> When `detectProjectStyle()` is called -> Then it returns `"next-gen"` and epic linking uses the `parent` field; Given a Classic project -> Then it returns `"classic"` and uses the discovered custom field ID

### T-012: Update spec-sync and multi-project-sync for dynamic fields
**User Story**: US-004 | **Satisfies ACs**: AC-US4-02, AC-US4-03 | **Status**: [x] completed
**Test**: Given `jira-spec-sync.ts:542` and `jira-multi-project-sync.ts:258` -> When linking an issue to an epic -> Then neither file contains `customfield_10014` and both use the dynamically discovered field or `parent` based on project style

---

## Phase 3: Resilience (High)

### T-013: Implement paginated JQL search
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-04 | **Status**: [x] completed
**Test**: Given a JQL query returning 150 issues (server page size 50) -> When `searchAllIssues()` is called -> Then it makes 3 paginated requests and returns all 150 issues

### T-014: Add rate-limit retry with exponential backoff
**User Story**: US-005 | **Satisfies ACs**: AC-US5-02, AC-US5-03 | **Status**: [x] completed
**Test**: Given a JIRA API call returning HTTP 429 with `Retry-After: 2` -> When the retry wrapper handles it -> Then it waits 2 seconds and retries; after 3 consecutive 429s -> Then it throws with a rate-limit error

### T-015: Apply pagination to hierarchical sync search
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01 | **Status**: [x] completed
**Test**: Given `jira-hierarchical-sync.ts:225` searching for issues -> When results exceed the page size -> Then all results are returned via the paginated search utility (no 50/100 item cap)

### T-016: Replace silent conflict auto-resolve with configurable strategy
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01, AC-US6-02, AC-US6-03 | **Status**: [x] completed
**Test**: Given a sync conflict between local and remote values with default config -> When conflict is detected in `jira-spec-sync.ts:447-462` -> Then sync halts, user is notified with both values, and no silent overwrite occurs

### T-017: Write conflict report file on detection
**User Story**: US-006 | **Satisfies ACs**: AC-US6-04 | **Status**: [x] completed
**Test**: Given a detected sync conflict -> When strategy is `manual` -> Then a `conflict-report.json` is written containing field name, local value, remote value, and timestamp

---

## Phase 4: Medium Priority Fixes

### T-018: Fix false REPARENTED events in reorganization detector
**User Story**: US-007 | **Satisfies ACs**: AC-US7-01, AC-US7-03 | **Status**: [x] completed
**Test**: Given an issue update that changes only `summary` (not `parent` or Epic Link) -> When the reorganization detector processes the webhook -> Then no REPARENTED event is emitted

### T-019: Implement real reorganization handler (replace stub)
**User Story**: US-007 | **Satisfies ACs**: AC-US7-02 | **Status**: [x] completed
**Test**: Given a real REPARENTED event (parent changed from Epic-A to Epic-B) -> When the handler executes -> Then local hierarchy metadata is updated to reflect the new parent

### T-020: Remove hardcoded FS- prefix in epic sync
**User Story**: US-008 | **Satisfies ACs**: AC-US8-01 | **Status**: [x] completed
**Test**: Given a project with key `MYPROJ` -> When `jira-epic-sync.ts` generates epic references -> Then it uses `MYPROJ-` prefix (not hardcoded `FS-`)

### T-021: Defer epic creation until after story classification
**User Story**: US-008 | **Satisfies ACs**: AC-US8-02 | **Status**: [x] completed
**Test**: Given 5 JIRA projects but stories only classified into 2 -> When multi-project sync runs -> Then epics are created only for those 2 projects (not all 5)

### T-022: Fix duplicate detector returning success on failure
**User Story**: US-008 | **Satisfies ACs**: AC-US8-03 | **Status**: [x] completed
**Test**: Given `jira-duplicate-detector.ts:122-130` encountering a verification failure -> When the function returns -> Then `success` is `false` and `error` contains the failure reason

### T-023: Fix ESM compatibility in refresh-cache script
**User Story**: US-008 | **Satisfies ACs**: AC-US8-04 | **Status**: [x] completed
**Test**: Given `scripts/refresh-cache.ts` running as ESM -> When the entry point check executes -> Then it uses `import.meta.url` comparison (not `require.main === module`) and does not throw ReferenceError

---

## Dependencies

```
T-001 -> T-002, T-003 (metadata module needed first)
T-004 -> T-005, T-006 (deployment detection needed before replacing hardcoded paths)
T-004 -> T-007 (format adapter needs API version detection)
T-007 -> T-008, T-009 (format adapter needed before fixing individual files)
T-010 -> T-011, T-012 (field discovery needed before project style detection)
T-013 -> T-015 (pagination utility needed before applying to hierarchical sync)
T-014 -> T-013 (rate limiting wraps the HTTP layer used by pagination)
T-018, T-019 (independent of each other, both in reorganization-detector.ts)
T-020, T-021, T-022, T-023 (all independent, can be parallelized)
```
