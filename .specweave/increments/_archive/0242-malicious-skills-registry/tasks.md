# Tasks: 0242 — Malicious Skills Registry & Security Audits Dashboard

## Phase 1: Database & API (vskill-platform)

### T-001: Add BlocklistEntry Prisma model and migration
**User Story**: US-002 | **Satisfies ACs**: AC-US2-04 | **Status**: [x] completed
**Test**: Given a new Prisma schema with BlocklistEntry model → When `prisma migrate` runs → Then the table is created with all fields (skillName, contentHash, threatType, severity, reason, evidenceUrls, discoveredAt, discoveredBy, isActive) and indexes on skillName, contentHash, isActive

### T-002: Create GET /api/v1/blocklist endpoint (public)
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03 | **Status**: [x] completed
**Test**: Given blocklist entries exist in DB → When GET /api/v1/blocklist is called → Then response returns all active entries with Cache-Control headers (max-age=300) and ETag; Given no entries → When called → Then returns empty array with count=0

### T-003: Create GET /api/v1/blocklist/check endpoint (public)
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03 | **Status**: [x] completed
**Test**: Given "evil-skill" is blocklisted → When GET /api/v1/blocklist/check?name=evil-skill → Then returns { blocked: true, entry: {...} }; Given "safe-skill" is NOT blocklisted → When called → Then returns { blocked: false }; Given contentHash query → When GET /api/v1/blocklist/check?hash=sha256:abc → Then matches by hash

### T-004: Create POST /api/v1/admin/blocklist endpoint (admin)
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02 | **Status**: [x] completed
**Test**: Given authenticated REVIEWER admin → When POST /api/v1/admin/blocklist with { skillName, threatType, severity, reason } → Then entry is created and returned with 201; Given unauthenticated request → When POST → Then returns 401; Given missing required fields → When POST → Then returns 400

### T-005: Create DELETE /api/v1/admin/blocklist/[id] endpoint (super admin)
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02 | **Status**: [x] completed
**Test**: Given SUPER_ADMIN auth → When DELETE /api/v1/admin/blocklist/{id} → Then entry.isActive set to false (soft delete); Given REVIEWER auth → When DELETE → Then returns 403

### T-006: Create GET /api/v1/audits endpoint (public)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03 | **Status**: [x] completed
**Test**: Given published skills with scan results → When GET /api/v1/audits?sort=score&order=desc&limit=20 → Then returns paginated list with tier1/tier2 verdicts, scores, severity counts, and overall status; Given filter ?status=FAIL → Then only failed skills returned; Given sort ?sort=name → Then alphabetically sorted

### T-007: Seed blocklist with known ClawHub malicious skills
**User Story**: US-002 | **Satisfies ACs**: AC-US2-05 | **Status**: [x] completed
**Test**: Given empty blocklist → When seed script runs → Then at least 20 known-malicious skills are inserted (hightower6eu, Aslaep123, zaycv, aztr0nutzs actors) with correct threat types and evidence URLs

## Phase 2: Frontend Pages (vskill-platform)

### T-008: Create /audits public page with sortable/filterable table
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05 | **Status**: [x] completed
**Test**: Given audits page is loaded → When data fetches from /api/v1/audits → Then table displays columns: #, Skill, Repo, Tier 1 Verdict, Tier 2 Verdict, Score, Status; Given user clicks column header → When clicked → Then table re-sorts; Given user selects FAIL filter → When applied → Then only failed skills shown; Given blocked skill exists → When rendered → Then shown with red BLOCKED badge and visual distinction

### T-009: Create /blocklist public page with malicious skills registry
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-04 | **Status**: [x] completed
**Test**: Given blocklist page is loaded → When data fetches from /api/v1/blocklist → Then table displays: Skill Name, Source, Threat Type, Severity, Reason, Discovered date; Given user clicks row → When expanded → Then evidence links shown; Given 47 entries → When page loads → Then header shows "47 known-malicious skills blocked"

### T-010: Add "Add to Blocklist" action on admin submission detail page
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02 | **Status**: [x] completed
**Test**: Given admin views submission detail for a REJECTED skill → When "Add to Blocklist" button clicked → Then modal appears with pre-filled fields (skillName, repoUrl); Given admin fills reason and threat type and submits → When POST /api/v1/admin/blocklist succeeds → Then success toast shown and button changes to "Blocklisted"

### T-011: Add admin blocklist management page
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02, AC-US2-05 | **Status**: [x] completed
**Test**: Given admin navigates to /admin/blocklist → When page loads → Then all blocklist entries shown in table; Given SUPER_ADMIN clicks deactivate on entry → When confirmed → Then entry is soft-deleted and removed from table

## Phase 3: CLI Integration (vskill)

### T-012: Create blocklist module with API client and local cache
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-03 | **Status**: [x] completed
**Test**: Given blocklist API returns entries → When syncBlocklist() called → Then entries cached to ~/.vskill/blocklist.json with fetchedAt timestamp; Given cache exists and is <1hr old → When checkBlocklist("evil-skill") called → Then uses cache without API call; Given cache is >1hr old → When checkBlocklist() called → Then refreshes from API first; Given API is unreachable → When checkBlocklist() called → Then falls back to cached version

### T-013: Integrate blocklist check into `vskill install` (GitHub path)
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02 | **Status**: [x] completed
**Test**: Given "evil-skill" is blocklisted → When `vskill install owner/evil-skill` → Then installation is refused with error showing threat type and reason, exit code 1; Given "safe-skill" is not blocklisted → When `vskill install owner/safe-skill` → Then proceeds to Tier 1 scan as normal

### T-014: Integrate blocklist check into `vskill install` (plugin path)
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02 | **Status**: [x] completed
**Test**: Given "evil-plugin" is blocklisted → When `vskill install source --plugin evil-plugin` → Then installation is refused; Given "safe-plugin" → When installed → Then proceeds normally

### T-015: Add --force override with prominent warning for blocked skills
**User Story**: US-003 | **Satisfies ACs**: AC-US3-04 | **Status**: [x] completed
**Test**: Given "evil-skill" is blocklisted → When `vskill install owner/evil-skill --force` → Then shows WARNING banner (red, multi-line) explaining the skill is known-malicious, but proceeds with installation; Given --force NOT passed → When blocked skill attempted → Then refuses without option to continue inline

### T-016: Add `vskill blocklist` CLI command (list, sync, check)
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01 | **Status**: [x] completed
**Test**: Given cached blocklist with 20 entries → When `vskill blocklist list` → Then prints formatted table of all entries; When `vskill blocklist sync` → Then fetches from API and updates cache, prints "Synced N entries"; When `vskill blocklist check evil-skill` → Then prints blocked status with details; When `vskill blocklist check safe-skill` → Then prints "Not blocklisted"

## Phase 4: Cross-Platform Scanning

### T-017: Create POST /api/v1/admin/scan-external endpoint
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-04 | **Status**: [x] completed
**Test**: Given REVIEWER admin → When POST /api/v1/admin/scan-external with { repoUrl, skillName } → Then skill is fetched, Tier 1 scanned, result stored with sourceUrl preserved; Given scan result verdict is FAIL → When scan completes → Then skill auto-added to blocklist (AC-US4-03); Given invalid URL → When submitted → Then returns 400

### T-018: Add "Scan External Skill" form to admin dashboard
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01 | **Status**: [x] completed
**Test**: Given admin is on dashboard → When "Scan External Skill" form is filled with GitHub URL and skill name → When submitted → Then loading spinner shows, result appears with verdict badge; Given scan finds critical issues → Then "Add to Blocklist" button appears pre-filled
