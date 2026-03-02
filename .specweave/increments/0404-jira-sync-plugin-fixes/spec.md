---
status: ready_for_review
---
# Spec: JIRA Sync Plugin Critical Fixes (0403)

## Overview

The JIRA sync plugin suite (`specweave-jira`) has 18 bugs identified via grill report,
ranging from data integrity failures to complete feature breakage on self-hosted JIRA
instances. This increment addresses all bugs grouped by priority.

---

## CRITICAL Priority

### US-001: Consistent Metadata Path for JIRA Issue Keys

**As a** SpecWeave user syncing tasks to JIRA,
**I want** all plugin files to read/write the JIRA issue key from one canonical metadata path,
**so that** auto-sync, commit sync, and manual sync all work together without silent data loss.

**Context**: Three incompatible metadata paths exist:
- `enhanced-jira-sync.js:64` reads/writes `.jira.issue`
- `hooks/post-task-completion.sh:99` reads `.jira.issue`
- `jira-spec-commit-sync.ts:87` reads `.jira.issueKey`
- The system actually writes `.external_sync.jira.issueKey`

**Acceptance Criteria**:
- [x] AC-US1-01: All plugin files use `.external_sync.jira.issueKey` as the single canonical path
- [x] AC-US1-02: A shared constant/utility defines the canonical path (no string literals scattered)
- [x] AC-US1-03: Backward-compatible migration reads old paths (`.jira.issue`, `.jira.issueKey`) and writes canonical path
- [x] AC-US1-04: `enhanced-jira-sync.js:64` no longer returns placeholder `SPEC-001` as real data

---

### US-002: Self-Hosted JIRA Server Compatibility

**As a** user running JIRA Server or Data Center (self-hosted),
**I want** the plugin to detect my JIRA deployment type and use the correct API version,
**so that** API calls don't 404 on my instance.

**Context**: All API calls hardcode `/rest/api/3` (Cloud-only). JIRA Server uses `/rest/api/2`.
Additionally, `jira-resource-validator/SKILL.md:62-66` hard-blocks self-hosted despite code supporting it.

**Acceptance Criteria**:
- [x] AC-US2-01: Plugin auto-detects JIRA deployment type (Cloud vs Server/DC) via `/rest/api/2/serverInfo`
- [x] AC-US2-02: API version (`/rest/api/2` vs `/rest/api/3`) is selected based on detected deployment type
- [x] AC-US2-03: All 4 files with hardcoded `/rest/api/3` are updated to use the dynamic version
- [x] AC-US2-04: `jira-resource-validator/SKILL.md` removes the hard-block on self-hosted JIRA
- [x] AC-US2-05: Wiki markup is used for API v2 (Server), ADF for API v3 (Cloud)

---

## HIGH Priority

### US-003: Correct Content Format Per API Version

**As a** user syncing specs/epics to JIRA,
**I want** descriptions and comments to use the correct format (ADF for Cloud, wiki markup for Server),
**so that** formatting is preserved and API calls succeed.

**Context**:
- `jira-epic-sync.ts:277`, `jira-spec-sync.ts:369` send wiki markup to ADF-only API v3
- `jira-status-sync.ts:137` sends plain text comment body instead of ADF

**Acceptance Criteria**:
- [x] AC-US3-01: A format adapter converts content to ADF (v3/Cloud) or wiki markup (v2/Server) based on detected API version
- [x] AC-US3-02: Epic descriptions use correct format
- [x] AC-US3-03: Spec descriptions use correct format
- [x] AC-US3-04: Status sync comments use ADF format for Cloud, wiki for Server
- [x] AC-US3-05: Existing wiki-to-ADF conversion is extracted into a shared utility

---

### US-004: Dynamic Epic Link Field Detection

**As a** user with a customized JIRA instance,
**I want** the plugin to discover my Epic Link custom field ID dynamically,
**so that** epic linking works regardless of JIRA configuration.

**Context**:
- `jira-spec-sync.ts:542` hardcodes `customfield_10014` for Epic Link
- `jira-multi-project-sync.ts:258` uses `parent` field (Next-gen) vs Classic `customfield_10014`
- No detection of project type (Next-gen vs Classic)

**Acceptance Criteria**:
- [x] AC-US4-01: Plugin queries `/rest/api/*/field` to discover the Epic Link field ID at startup
- [x] AC-US4-02: Plugin detects Next-gen vs Classic project style and uses `parent` or custom field accordingly
- [x] AC-US4-03: `customfield_10014` is no longer hardcoded anywhere
- [x] AC-US4-04: Field ID is cached per JIRA instance to avoid repeated lookups

---

### US-005: Pagination and Rate Limiting for JIRA API

**As a** user with large JIRA projects,
**I want** API calls to handle pagination and rate limits correctly,
**so that** searches return complete results and bulk operations don't get throttled.

**Context**:
- `jira-hierarchical-sync.ts:225` has no pagination (50/100 item cap)
- No rate-limit retry anywhere in the plugin suite

**Acceptance Criteria**:
- [x] AC-US5-01: All JQL search calls paginate through full result sets using `startAt`/`maxResults`
- [x] AC-US5-02: A shared HTTP client wrapper implements exponential backoff retry on 429 responses
- [x] AC-US5-03: Rate limit headers (`X-RateLimit-Remaining`, `Retry-After`) are respected
- [x] AC-US5-04: Pagination is tested with mock responses exceeding default page size

---

### US-006: Safe Conflict Resolution

**As a** user syncing bidirectionally with JIRA,
**I want** conflicts to be surfaced for manual resolution (not silently auto-resolved),
**so that** I don't lose local changes without knowing.

**Context**: `jira-spec-sync.ts:447-462` auto-resolves all conflicts as "remote-wins" silently,
contradicting SKILL.md guidance which recommends user intervention.

**Acceptance Criteria**:
- [x] AC-US6-01: Conflicts are detected and reported to the user with both local and remote values
- [x] AC-US6-02: Default resolution strategy is configurable (`remote-wins`, `local-wins`, `manual`)
- [x] AC-US6-03: Silent auto-resolve is removed; `manual` is the default strategy
- [x] AC-US6-04: Conflict report is written to a file when conflicts are detected

---

## MEDIUM Priority

### US-007: Reorganization Detector Reliability

**As a** user relying on JIRA issue reorganization detection,
**I want** the detector to correctly identify real reparenting events and execute handlers,
**so that** my local hierarchy stays in sync with JIRA changes.

**Context**:
- `reorganization-detector.ts:318-358` handler is a stub (logs success, does nothing)
- `reorganization-detector.ts:225-248` emits false REPARENTED events on any issue update

**Acceptance Criteria**:
- [x] AC-US7-01: REPARENTED event fires only when `parent` or Epic Link field actually changes
- [x] AC-US7-02: Reorganization handler executes real hierarchy update logic (not a stub)
- [x] AC-US7-03: False positive rate for REPARENTED events is zero for non-parent-changing updates

---

### US-008: Misc Bug Fixes (Prefix, Empty Epics, Verify, ESM)

**As a** developer using the JIRA sync plugin,
**I want** miscellaneous bugs fixed,
**so that** the plugin behaves correctly in edge cases.

**Context**:
- `jira-epic-sync.ts:196` hardcodes `FS-` prefix assumption
- `jira-multi-project-sync.ts:115-119` creates empty epics for all projects before classification
- `jira-duplicate-detector.ts:122-130` returns `success: true` on verification failure
- `scripts/refresh-cache.ts:38` uses `require.main` in ESM (throws ReferenceError)

**Acceptance Criteria**:
- [x] AC-US8-01: Epic sync derives project prefix from actual project key, not hardcoded `FS-`
- [x] AC-US8-02: Multi-project sync only creates epics for projects that have classified stories
- [x] AC-US8-03: Duplicate detector returns `success: false` when verification fails
- [x] AC-US8-04: `refresh-cache.ts` uses ESM-compatible entry point detection (`import.meta.url`)
