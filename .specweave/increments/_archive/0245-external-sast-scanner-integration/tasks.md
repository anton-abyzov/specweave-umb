# Tasks: 0245 External SAST Scanner Integration

## Phase 1: Database + Storage Foundation

### T-001: Add ExternalScanResult Prisma model
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04 | **Status**: [x] completed
**Test**: Given the Prisma schema → When I add ScanProvider enum, ExternalScanStatus enum, and ExternalScanResult model → Then `prisma migrate dev` succeeds and the model has provider, status, verdict, score, severity counts, findings JSON, githubRunId/Url fields with unique constraint on [skillName, provider]

### T-002: Create KV store module for external scan status
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04 | **Status**: [x] completed
**Test**: Given an ExternalScanSummary → When I call storeExternalScanStatus("my-skill", "semgrep", summary) → Then getExternalScanStatus("my-skill", "semgrep") returns the summary AND getAllExternalScans("my-skill") includes it AND computeOverallVerdict returns PASS when all providers pass

## Phase 2: Webhook + Auth

### T-003: Create webhook authentication module
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01 | **Status**: [x] completed
**Test**: Given a payload and HMAC secret → When I sign it with signPayload() → Then verifyWebhookSignature() returns true AND verifyWebhookSignature with wrong signature returns false AND payloads older than 5 minutes are rejected

### T-004: Create scan results webhook endpoint
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03, AC-US1-04, AC-US1-05 | **Status**: [x] completed
**Test**: Given a valid HMAC-signed scan result payload with provider="semgrep" → When I POST to /api/v1/webhooks/scan-results → Then ExternalScanResult is upserted in DB AND KV is updated AND if criticalCount > 0 then BlocklistEntry is created

## Phase 3: Scanner Runner

### T-005: Create GitHub Actions scanner workflow
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [x] completed
**Test**: Given a repository_dispatch event with repo_owner/repo_name → When the workflow runs → Then it checkouts the target repo, runs semgrep/njsscan/trufflehog with JSON output, and executes parse-and-report.js

### T-006: Create results parser script
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03 | **Status**: [x] completed
**Test**: Given semgrep JSON output with 2 high findings → When parse-and-report.js runs → Then it normalizes to common format { severity, message, file, line, rule } AND computes score 70 (100 - 2*15) AND POSTs to callback URL with HMAC signature

## Phase 4: Dispatch Integration

### T-007: Create external scan dispatch module
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US4-02, AC-US4-03 | **Status**: [x] completed
**Test**: Given a published skill → When dispatchExternalScans() is called → Then GitHub API receives repository_dispatch AND KV has PENDING status for all 3 providers AND calling again within dedup window is a no-op AND dispatch is rate-limited to 100/hour

### T-008: Integrate dispatch into submission pipeline
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed
**Test**: Given a skill that passes Tier 1+2 → When processSubmission publishes it → Then ctx.waitUntil calls dispatchExternalScans AND dispatch failure does not affect submission outcome

## Phase 5: Security APIs + Badges

### T-009: Create security query API
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01 | **Status**: [x] completed
**Test**: Given external scan results in KV for "my-skill" → When GET /api/v1/skills/my-skill/security → Then response includes all provider results with verdict/score AND PENDING scans > 20 min are returned as TIMED_OUT

### T-010: Create per-provider detail API
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02 | **Status**: [x] completed
**Test**: Given semgrep results with 3 findings → When GET /api/v1/skills/my-skill/security/semgrep → Then response includes all 3 findings with severity, rule, message, file, line

### T-011: Create per-provider badge endpoint
**User Story**: US-002 | **Satisfies ACs**: AC-US2-05 | **Status**: [x] completed
**Test**: Given semgrep PASS result → When GET /api/v1/skills/my-skill/badge/semgrep → Then SVG contains "semgrep" label and green (#10B981) color AND FAIL returns red (#EF4444) AND PENDING returns gray (#6B7280)

## Phase 6: UI Pages

### T-012: Create security overview page
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01 | **Status**: [x] completed
**Test**: Given 3 provider results (2 PASS, 1 FAIL) → When navigating to /skills/my-skill/security → Then page shows provider table with color-coded badges AND overall status shows FAIL (worst of all providers)

### T-013: Create per-provider detail page
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02 | **Status**: [x] completed
**Test**: Given semgrep results with findings → When navigating to /skills/my-skill/security/semgrep → Then page shows provider name, version, scan date, verdict badge, score AND findings table with severity colors

### T-014: Update skill detail page with external scan section
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03 | **Status**: [x] completed
**Test**: Given a skill with external scan results → When viewing /skills/my-skill → Then "External Security Scans" section appears below Tier 1/2 results with per-provider status badges AND "View full security report" link

### T-015: Update audits page with external scan columns
**User Story**: US-002 | **Satisfies ACs**: AC-US2-04 | **Status**: [x] completed
**Test**: Given skills with external scan results → When viewing /audits → Then table includes Semgrep, njsscan, Trufflehog columns with verdict badges

## Phase 7: CLI Integration

### T-016: Create platform security check module in CLI
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-05 | **Status**: [x] completed
**Test**: Given platform returns security data → When checkPlatformSecurity("my-skill") is called → Then returns { hasCritical, overallVerdict, providers[], reportUrl } AND returns null on network error

### T-017: Update vskill install to check external scan results
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02, AC-US3-03, AC-US3-04 | **Status**: [x] completed
**Test**: Given a skill with CRITICAL semgrep findings → When running `vskill install owner/repo` → Then prints error with provider names AND prints report URL AND exits with code 1 AND `--force` overrides the block

## Phase 8: Hardening

### T-018: Add admin external scan re-trigger
**User Story**: US-004 | **Satisfies ACs**: AC-US4-05 | **Status**: [x] completed
**Test**: Given a published skill → When admin calls POST /api/v1/admin/scan-external with triggerExternal=true → Then external scans are dispatched AND PENDING status appears in KV

### T-019: Add lazy timeout sweep
**User Story**: US-004 | **Satisfies ACs**: AC-US4-04 | **Status**: [x] completed
**Test**: Given a PENDING scan dispatched 25 minutes ago → When security API reads it → Then status is returned as TIMED_OUT AND KV is updated with TIMED_OUT status
