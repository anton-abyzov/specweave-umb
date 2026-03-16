# Tasks: ADO Sync Plugin Critical Fixes

## Task Notation

- `[ ]`: Not started | `[x]`: Completed
- Priority tiers: Phase 1 = Critical (P0), Phase 2 = High (P1), Phase 3 = Medium (P2)

---

## Phase 1: Critical Fixes (P0)

### T-001: Fix post-task-completion hook field path for work item ID
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed

**Description**: `hooks/post-task-completion.sh:99` reads `.ado.item` but the system writes to `.external_sync.ado.workItemId`. This mismatch means auto-sync never finds the work item ID, permanently breaking automatic task-to-ADO propagation.

**Implementation Details**:
- In `post-task-completion.sh`, replace all reads of `.ado.item` with `.external_sync.ado.workItemId`
- Verify the JSON structure written by the sync system matches the read path
- Add a fallback to `.ado.item` for backward compatibility with older metadata files

**Test**: Given a metadata.json with `external_sync.ado.workItemId` set to 12345 -> When post-task-completion hook runs -> Then the hook reads work item ID 12345 and calls ADO API with that ID

**Dependencies**: None

---

### T-002: Add pagination to ado-client-v2 batch fetch
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [x] completed

**Description**: `ado-client-v2.ts:339-373` fetches work items in a single batch call with no pagination. ADO's batch API caps results at 200 items. Queries for >200 items silently fail or return an API error.

**Implementation Details**:
- Implement a pagination loop in the batch fetch method using `$skip` parameter or continuation token
- Accumulate all pages into a single result array before returning
- Respect ADO's 200-item page size limit per request
- Add a safety cap (e.g., 10000 items max) to prevent runaway pagination

**Test**: Given 350 work items matching a query -> When batchGetWorkItems() is called -> Then all 350 items are returned across 2 pages (200 + 150)

**Dependencies**: None

---

### T-003: Fix cross-project WIQL endpoint for FILTERED strategy
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03 | **Status**: [x] completed

**Description**: `ado-hierarchical-sync.ts:368` uses the project-level WIQL endpoint (`{org}/{project}/_apis/wit/wiql`) for the FILTERED strategy even when querying across projects. The project-scoped endpoint silently limits results to that single project, hiding items from other projects.

**Implementation Details**:
- When strategy is FILTERED and query spans multiple projects, use org-level endpoint: `{org}/_apis/wit/wiql`
- When strategy is FILTERED and query is single-project, continue using project-level endpoint
- Detect multi-project by checking if `containers` reference more than one project

**Test**: Given a FILTERED strategy with containers in projects "Alpha" and "Beta" -> When hierarchical sync runs -> Then WIQL query is sent to `{org}/_apis/wit/wiql` (org-level) and results include items from both projects

**Dependencies**: None

---

## Phase 2: High Priority Fixes (P1)

### T-004: Resolve activeProfile vs defaultProfile naming mismatch
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01 | **Status**: [x] completed

**Description**: `ado-profile-resolver.ts:161` references `activeProfile` while `commands/sync.md:96` references `defaultProfile`. This mismatch means profile resolution can fail silently when the field name does not match what was configured.

**Implementation Details**:
- Audit both files to determine which name is canonical
- Standardize on `activeProfile` (the code-side name) as the canonical field
- Update `commands/sync.md` documentation to use `activeProfile`
- Add a migration/fallback: if `defaultProfile` exists but `activeProfile` does not, use `defaultProfile` with a deprecation warning

**Test**: Given a config with `defaultProfile: "my-profile"` and no `activeProfile` -> When profile resolver runs -> Then it resolves to "my-profile" profile and emits a deprecation warning

**Dependencies**: None

---

### T-005: Fix hardcoded $Feature work item type in URL construction
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02 | **Status**: [x] completed

**Description**: `ado-spec-sync.ts:258` hardcodes `$Feature` in the ADO URL instead of using the computed `workItemType` variable. This breaks sync for teams that map specs to Epics, PBIs, or custom work item types.

**Implementation Details**:
- Replace the hardcoded `$Feature` string with the `workItemType` variable already computed in the function scope
- Ensure the variable is URL-encoded if it contains special characters (e.g., `$` prefix)

**Test**: Given workItemType computed as "Epic" -> When ado-spec-sync builds the ADO URL -> Then URL contains `$Epic` (not `$Feature`)

**Dependencies**: None

---

### T-006: Fix testConnection() URL in single-project mode
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03 | **Status**: [x] completed

**Description**: `ado-client-v2.ts:150` `testConnection()` builds a URL that is incorrect in single-project mode, always returning 404. The project segment is missing or malformed when a single project is configured.

**Implementation Details**:
- In single-project mode, include the project name in the test URL: `{org}/{project}/_apis/projects/{project}`
- In org-wide mode, use: `{org}/_apis/projects`
- Add response status checking to provide clear error messages on 401 (bad PAT) vs 404 (bad project/org)

**Test**: Given a single-project config with org "myorg" and project "myproj" -> When testConnection() is called -> Then the request URL is `https://dev.azure.com/myorg/myproj/_apis/projects/myproj?api-version=7.0`

**Dependencies**: None

---

### T-007: Implement org-specific PAT pattern from SKILL.md
**User Story**: US-002 | **Satisfies ACs**: AC-US2-04 | **Status**: [x] completed

**Description**: SKILL.md documents the `AZURE_DEVOPS_PAT_MYORG` environment variable pattern for org-specific PATs, but the code never reads this pattern. Users following the documentation get no org-specific PAT resolution.

**Implementation Details**:
- In the PAT resolution logic, check for `AZURE_DEVOPS_PAT_{ORG_UPPER}` first (org name uppercased, hyphens replaced with underscores)
- Fall back to `AZURE_DEVOPS_PAT` if the org-specific variable is not set
- Then fall back to profile-stored PAT
- Document the resolution order in code comments

**Test**: Given env var `AZURE_DEVOPS_PAT_CONTOSO=secret123` and org name "contoso" -> When PAT is resolved -> Then "secret123" is returned (not the generic AZURE_DEVOPS_PAT)

**Dependencies**: None

---

### T-008: Make conflict resolver process-template-aware
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01 | **Status**: [x] completed

**Description**: `conflict-resolver.ts:88-98` hardcodes Agile process template states (Active, Resolved, Closed). Teams using Scrum (New, Approved, Committed, Done), CMMI (Proposed, Active, Resolved, Closed), or Basic (To Do, Doing, Done) hit incorrect state transitions.

**Implementation Details**:
- Create a state mapping table for each process template: Agile, Scrum, CMMI, Basic
- Read the process template from config/profile or detect it from the project's process
- Use the appropriate state set when resolving conflicts
- Default to Agile for backward compatibility if template is unknown

**Test**: Given a Scrum process template project -> When conflict resolver evaluates state "Committed" -> Then it recognizes "Committed" as an active state (not unknown/invalid)

**Dependencies**: None

---

### T-009: Replace hardcoded 'User Story' work item type in per-US sync
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02 | **Status**: [x] completed

**Description**: `per-us-sync.ts:270` hardcodes `'User Story'` as the work item type. Scrum uses "Product Backlog Item", CMMI uses "Requirement", and Basic uses "Issue". This breaks per-US sync for all non-Agile teams.

**Implementation Details**:
- Read the work item type from the profile or config, keyed by process template
- Provide a default mapping: Agile -> "User Story", Scrum -> "Product Backlog Item", CMMI -> "Requirement", Basic -> "Issue"
- Allow explicit override via profile config field `workItemType`

**Test**: Given a Scrum profile config -> When per-us-sync creates a WIQL query -> Then the query filters by `[System.WorkItemType] = 'Product Backlog Item'` (not 'User Story')

**Dependencies**: T-008 (shares process template detection logic)

---

### T-010: Add HTTP request timeout to hierarchical sync
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01 | **Status**: [x] completed

**Description**: `ado-hierarchical-sync.ts:424-484` makes HTTP requests without any timeout. If ADO is slow or unresponsive, the sync process hangs indefinitely, blocking the entire pipeline.

**Implementation Details**:
- Wrap all `fetch()` calls in hierarchical sync with `AbortController` and a configurable timeout
- Default timeout: 30 seconds per request
- Allow override via config: `ado.requestTimeoutMs`
- On timeout, throw a descriptive error: "ADO request timed out after {N}ms"

**Test**: Given a request timeout of 100ms and a server that never responds -> When hierarchical sync makes an HTTP request -> Then the request aborts after 100ms with a timeout error

**Dependencies**: None

---

### T-011: Fix area path double-prepend of project name
**User Story**: US-003 | **Satisfies ACs**: AC-US3-03 | **Status**: [x] completed

**Description**: `ado-client-v2.ts:459-462` constructs the area path by always prepending the project name. If the configured area path already starts with the project name (e.g., `MyProject\Team A`), the result is `MyProject\MyProject\Team A`, which does not exist.

**Implementation Details**:
- Before prepending the project name, check if the area path already starts with `{project}\` or equals `{project}`
- If it already includes the project prefix, use the area path as-is
- Normalize backslash separators for consistent comparison

**Test**: Given project "MyProject" and area path "MyProject\Team A" -> When area path is constructed -> Then result is "MyProject\Team A" (not "MyProject\MyProject\Team A")

**Dependencies**: None

---

## Phase 3: Medium Priority Fixes (P2)

### T-012: Fix container filter scope to apply per-container
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01 | **Status**: [x] completed

**Description**: `ado-hierarchical-sync.ts:91-97` takes filters from only the first container and applies them globally. If different containers have different filter criteria, all containers except the first have their filters ignored.

**Implementation Details**:
- Iterate over each container and apply its own filters when building the WIQL query for that container
- If containers share a common filter, apply it as a shared base
- Ensure each container's unique filters are scoped to its own query segment

**Test**: Given container A with filter "Area Path = Team1" and container B with filter "Area Path = Team2" -> When sync runs -> Then container A's query filters by Team1 and container B's query filters by Team2

**Dependencies**: None

---

### T-013: Fix duplicate detector returning success on verification failure
**User Story**: US-005 | **Satisfies ACs**: AC-US5-02 | **Status**: [x] completed

**Description**: `ado-duplicate-detector.ts:122-130` returns `{ success: true }` even when verification of a potential duplicate fails. This causes the system to silently skip duplicates that should be flagged or to proceed with creating duplicates.

**Implementation Details**:
- Change the verification failure return to `{ success: false, error: "Verification failed: {reason}" }`
- Ensure callers handle the failure case appropriately
- Add logging for verification failures for debugging

**Test**: Given a duplicate verification that fails (e.g., work item not found) -> When the detector runs -> Then it returns `{ success: false }` with an error message

**Dependencies**: None

---

### T-014: Add conditional update logic to updateAdoFeature
**User Story**: US-005 | **Satisfies ACs**: AC-US5-03 | **Status**: [x] completed

**Description**: `ado-spec-sync.ts:273-303` `updateAdoFeature` replaces title and description unconditionally on every sync. This overwrites manual edits made directly in ADO, causing data loss for teams that edit features in both SpecWeave and ADO.

**Implementation Details**:
- Fetch the current title and description from ADO before updating
- Compare current values with the new values from the spec
- Only include changed fields in the PATCH request
- Log skipped fields for transparency

**Test**: Given an ADO feature with title "Original" and spec title also "Original" -> When updateAdoFeature runs -> Then no PATCH request is sent for the title field

**Dependencies**: None

---

### T-015: Replace hardcoded 'repo' string in enhanced-ado-sync task URL
**User Story**: US-005 | **Satisfies ACs**: AC-US5-04 | **Status**: [x] completed

**Description**: `enhanced-ado-sync.js:133` constructs a task URL with a hardcoded `repo` string instead of using the actual repository name. This produces broken links in ADO work items.

**Implementation Details**:
- Read the repository name from git config (`git remote get-url origin`) or from SpecWeave config
- Replace the hardcoded `'repo'` string with the actual repository name
- Add a fallback to 'unknown-repo' if detection fails, with a warning log

**Test**: Given a repository named "my-project" -> When enhanced-ado-sync builds a task URL -> Then the URL contains "my-project" (not "repo")

**Dependencies**: None

---

### T-016: Fix addTimeRangeFilter WIQL regex corruption
**User Story**: US-004 | **Satisfies ACs**: AC-US4-02, AC-US5-05 | **Status**: [x] completed

**Description**: `ado-hierarchical-sync.ts:192-196` `addTimeRangeFilter` uses a regex to inject time range conditions into WIQL queries. The regex can corrupt the query when the existing WHERE clause contains certain patterns (nested conditions, string literals with keywords, etc.).

**Implementation Details**:
- Replace the regex-based approach with proper WIQL string parsing
- If the query already has a WHERE clause, append with AND
- If the query has no WHERE clause, add one
- Handle both `WHERE` and `where` (case-insensitive)
- Ensure string literals inside the query are not matched by the WHERE detection

**Test**: Given a WIQL query `SELECT ... WHERE [State] = 'Active' ORDER BY ...` -> When addTimeRangeFilter adds a date range -> Then result is `SELECT ... WHERE [State] = 'Active' AND [System.ChangedDate] >= '2026-01-01' ORDER BY ...` (no corruption)

**Dependencies**: None
