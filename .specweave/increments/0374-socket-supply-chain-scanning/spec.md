---
status: completed
---
# 0374 — Socket.dev Supply Chain Scanning

## Overview
Integrate Socket.dev supply chain risk scoring into the vskill-platform verification pipeline. Enriches the existing dependency analyzer with external intelligence for skills that have `package.json` dependencies or reference npm packages in DCI blocks.

## User Stories

### US-001: Socket.dev Dependency Enrichment
**As a** platform operator
**I want** Socket.dev supply chain scores integrated into the verification pipeline
**So that** skills with risky npm dependencies are flagged with broader intelligence than hardcoded typosquat lists

**Acceptance Criteria:**
- [x] AC-US1-01: When a skill has package.json, each dependency is checked against Socket.dev API
- [x] AC-US1-02: Socket scores are blended with local dependency analysis (local * 0.4 + socket * 0.6)
- [x] AC-US1-03: Packages with supplyChain < 0.3 or vulnerability < 0.3 are flagged as "high" severity
- [x] AC-US1-04: Socket API results are cached in KV with 24h TTL
- [x] AC-US1-05: When Socket API is unavailable, pipeline falls back to local-only analysis silently

### US-002: DCI Block Package Extraction
**As a** platform operator
**I want** package names extracted from DCI block install commands
**So that** skills that instruct AI agents to install risky packages are flagged

**Acceptance Criteria:**
- [x] AC-US2-01: DCI blocks with `npm install/i/add` patterns have package names extracted
- [x] AC-US2-02: DCI blocks with `npx` patterns have package names extracted
- [x] AC-US2-03: DCI blocks with `pip/pip3 install` patterns have package names extracted
- [x] AC-US2-04: Extracted npm packages are checked via Socket.dev
- [x] AC-US2-05: Flagged DCI packages reduce the weighted score by 5 points each

### US-003: Stored Results Include Socket Data
**As a** platform operator
**I want** Socket scan data stored in scan results
**So that** I can audit and debug supply chain decisions

**Acceptance Criteria:**
- [x] AC-US3-01: StoredScanResult.dependencyRisk includes socketScore object when available
- [x] AC-US3-02: DCI package check count and flag count are stored in dependencyRisk
