---
increment: 0420-vendor-skill-freshness
title: "Vendor Skill Freshness"
test_mode: TDD
by_user_story:
  US-001: [T-001, T-002]
  US-002: [T-003]
---

# Tasks: Vendor Skill Freshness

## User Story: US-001 — Vendor skills bypass discovery dedup

**Linked ACs**: AC-US1-01, AC-US1-02
**Tasks**: 2 total, 2 completed

### T-001: Write failing tests for vendor dedup bypass (TDD RED)

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02
**Status**: [x] completed

**Test Plan**:
- **Given** a candidate with `source: "vendor-orgs"` and `hasBeenDiscovered` returns true
- **When** `runGitHubDiscovery` processes it via `processRepo`
- **Then** the candidate is NOT skipped and is submitted via WORKER_SELF_REFERENCE

- **Given** a candidate with `source: "github-code"` and `hasBeenDiscovered` returns true
- **When** `runGitHubDiscovery` processes it via `processRepo`
- **Then** the candidate IS skipped (dedup preserved for non-vendor)

**Test Cases**:
1. **Unit**: `src/lib/crawler/__tests__/github-discovery.test.ts`
   - TC-VENDOR-01: `vendor-orgs candidates bypass dedup even when hasBeenDiscovered returns true`
   - TC-VENDOR-02: `non-vendor candidates still respect dedup when hasBeenDiscovered returns true`
   - **Coverage Target**: 90%

**Implementation**:
1. Add two new tests to existing `github-discovery.test.ts`
2. Mock `discoverFromVendorOrgs` source to return a vendor candidate
3. Set `mockHasBeenDiscovered.mockResolvedValue(true)` to simulate already-discovered
4. Assert WORKER_SELF_REFERENCE.fetch IS called for vendor-orgs source
5. Assert WORKER_SELF_REFERENCE.fetch IS NOT called for github-code source

**Dependencies**: None

---

### T-002: Implement vendor dedup bypass in processRepo (TDD GREEN)

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02
**Status**: [x] completed

**Test Plan**:
- **Given** tests from T-001 are failing
- **When** the conditional is added to `processRepo`
- **Then** all tests pass (both new and existing)

**Implementation**:
1. In `src/lib/crawler/github-discovery.ts`, `processRepo` function (~line 765)
2. Add conditional: `const isVendorSource = candidate.source === "vendor-orgs";`
3. Change dedup check: `if (!isVendorSource && await hasBeenDiscovered(...)) { skip }`
4. Run `npx vitest run src/lib/crawler/__tests__/github-discovery.test.ts`
5. Verify all existing tests still pass

**Dependencies**: T-001

---

## User Story: US-002 — Vendor discovery runs on cron schedule

**Linked ACs**: AC-US2-01, AC-US2-02
**Tasks**: 1 total, 1 completed

### T-003: Add vendor-orgs to cron hourly discovery sources

**User Story**: US-002
**Satisfies ACs**: AC-US2-01, AC-US2-02
**Status**: [x] completed

**Test Plan**:
- **Given** the cron scheduled handler fires at minute :00
- **When** `runGitHubDiscovery` is called
- **Then** `sources` includes both `"npm"` and `"vendor-orgs"`

**Implementation**:
1. In `scripts/build-worker-entry.ts`, line 136
2. Change `sources: ["npm"]` to `sources: ["npm", "vendor-orgs"]`
3. Rebuild worker entry to verify no syntax errors

**Dependencies**: T-002 (dedup bypass must be in place before cron runs vendor-orgs)
