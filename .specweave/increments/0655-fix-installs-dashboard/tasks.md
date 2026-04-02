# Tasks: Fix admin installs dashboard

## Phase 1: Schema + Core

### T-001: Add machineHash to Prisma schema and create migration
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-04 | **Status**: [x] completed
**Test Plan**:
- Given the Prisma schema
- When migration is applied
- Then InstallEvent table has nullable machineHash column with index

### T-002: Add hashMachine() and update InstallMeta interface
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed
**Test Plan**:
- Given an IP address
- When hashMachine() is called
- Then it returns a consistent SHA-256 hash using static salt (same hash across days)

### T-003: Update install-tracker upsert to store machineHash
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [x] completed
**Test Plan**:
- Given an InstallMeta with machineHash
- When matchAndIncrementInstall runs
- Then the InstallEvent row includes machineHash

## Phase 2: API Endpoints

### T-004: Update batch install endpoint to pass machineHash
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [x] completed
**Test Plan**:
- Given a POST to /api/v1/skills/installs
- When the request is processed
- Then meta includes machineHash from hashMachine(ip)

### T-005: Update single-skill install endpoint to pass machineHash
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [x] completed
**Test Plan**:
- Given a POST to /api/v1/skills/:owner/:repo/:skill/installs
- When the request is processed
- Then meta includes machineHash from hashMachine(ip)

## Phase 3: Dashboard

### T-006: Update admin stats SQL to use COALESCE for unique machines
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03 | **Status**: [x] completed
**Test Plan**:
- Given the admin stats query
- When executed
- Then unique_machines uses COUNT(DISTINCT COALESCE(machineHash, ipHash))

### T-007: Fix default sort to lastInstallAt descending
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01 | **Status**: [x] completed
**Test Plan**:
- Given the installs page loads
- When no sort is selected
- Then rows are sorted by lastInstallAt descending
