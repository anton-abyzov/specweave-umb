---
increment: 0317-scan-findings-deep-link-source
title: "Scan Findings Deep-Link to Source Code Lines"
type: feature
priority: P1
status: planned
created: 2026-02-22
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Scan Findings Deep-Link to Source Code Lines

## Overview

Make scan finding line numbers clickable GitHub permalinks so reviewers can jump
directly to the offending source line, and show inline code context. This
requires three foundational changes:

1. Track which file each finding belongs to when scanning concatenated multi-file
   content (file-boundary mapping).
2. Capture the commit SHA at scan time via the GitHub API so permalinks point to
   the exact revision that was scanned.
3. Normalize the admin `Finding` interface to align with the scanner's
   `ScanFinding` type, eliminating the divergence between backend and frontend
   models.

## User Stories

### US-001: File-Boundary Mapping in Scanner (P1)
**Project**: vskill-platform

**As a** platform developer
**I want** each `ScanFinding` to include the originating file path
**So that** findings from multi-file scans can be attributed to the correct file

**Acceptance Criteria**:
- [ ] **AC-US1-01**: `ScanFinding` interface gains an optional `file?: string` field
- [ ] **AC-US1-02**: `scanContent()` accepts a new optional `fileBoundaries` parameter mapping line ranges to file paths
- [ ] **AC-US1-03**: When `fileBoundaries` is provided, each finding's `file` is populated and `lineNumber` is adjusted to be file-relative
- [ ] **AC-US1-04**: When `fileBoundaries` is omitted (single-file scan), behavior is unchanged (backward compatible)
- [ ] **AC-US1-05**: `process-submission.ts` builds `fileBoundaries` from the concatenated file list (skillMd + additionalFiles) before calling `runTier1Scan`
- [ ] **AC-US1-06**: `StoredScanFinding` gains an optional `file?: string` field that is persisted to KV

---

### US-002: Commit SHA Capture at Scan Time (P1)
**Project**: vskill-platform

**As a** security reviewer
**I want** the exact commit SHA to be captured when a skill is scanned
**So that** deep links point to the precise revision, not a moving HEAD

**Acceptance Criteria**:
- [ ] **AC-US2-01**: A new utility `resolveCommitSha(owner, repo, branch?)` calls the GitHub API (`GET /repos/{owner}/{repo}/commits/{ref}`) and returns the commit SHA string
- [ ] **AC-US2-02**: `process-submission.ts` calls `resolveCommitSha` during scan and stores the SHA on `StoredScanResult`
- [ ] **AC-US2-03**: `StoredScanResult` interface gains a `commitSha?: string` field
- [ ] **AC-US2-04**: The commit SHA is resilient to API failures (returns `null` on error, scan proceeds)
- [ ] **AC-US2-05**: The resolved SHA is propagated to `UnifiedSecurityReport` so downstream pages can use it for deep links

---

### US-003: GitHub Permalink Construction (P1)
**Project**: vskill-platform

**As a** security reviewer viewing the admin submission detail page
**I want** finding line numbers to be clickable links to the exact GitHub source line
**So that** I can immediately inspect the flagged code in context

**Acceptance Criteria**:
- [ ] **AC-US3-01**: A pure function `buildGitHubPermalink(owner, repo, commitSha, filePath, lineNumber)` returns a `https://github.com/{owner}/{repo}/blob/{sha}/{path}#L{line}` URL
- [ ] **AC-US3-02**: When `commitSha` is unavailable, the function falls back to the default branch name (e.g., `main`)
- [ ] **AC-US3-03**: When `file` is unavailable on a finding, the function returns `null` (no link)
- [ ] **AC-US3-04**: The admin submission detail page renders line numbers as `<a>` tags linking to the permalink, opening in a new tab
- [ ] **AC-US3-05**: The public security report page also renders finding line numbers as clickable permalinks when data is available

---

### US-004: Normalize Admin Finding Interface (P2)
**Project**: vskill-platform

**As a** platform developer
**I want** the admin `Finding` interface to align with `ScanFinding`/`StoredScanFinding`
**So that** there is one canonical finding shape across backend and frontend

**Acceptance Criteria**:
- [ ] **AC-US4-01**: The admin submission detail page's `Finding` interface is replaced with `StoredScanFinding` (imported from `submission-store.ts`)
- [ ] **AC-US4-02**: Field mapping: `pattern` -> `patternId`, `message` -> `context`, `line` -> `lineNumber`, new fields: `patternName`, `category`, `match`, `file`
- [ ] **AC-US4-03**: The mock data in the admin API route uses the `StoredScanFinding` shape
- [ ] **AC-US4-04**: The finding row component renders all available fields: severity badge, patternId, patternName, context, file, lineNumber (as link)
- [ ] **AC-US4-05**: Backward compatibility: findings without `file` or `commitSha` still render correctly (plain text line number, no link)

## Functional Requirements

### FR-001: File Boundary Tracking
The scanner concatenates multiple files (SKILL.md, package.json, scripts, etc.)
into a single string. A `FileBoundary[]` array maps `{ file, startLine, endLine }`
so that when a finding is on global line N, the scanner can determine which file
and file-relative line it belongs to.

### FR-002: Commit SHA Resolution
A single GitHub API call (`GET /repos/{owner}/{repo}/commits/{ref}`) returns the
HEAD SHA of the default branch. This is captured once per scan run and stored on
the scan result record. No token is required for public repos.

### FR-003: Permalink Format
GitHub blob permalinks follow `https://github.com/{owner}/{repo}/blob/{sha}/{path}#L{line}`.
Using a commit SHA (not branch name) ensures the link is immutable.

## Success Criteria

- Every finding from a multi-file scan has a `file` field populated
- Line numbers in admin UI are clickable links to GitHub source
- Commit SHA is persisted per scan result in KV
- Zero breaking changes to existing scan pipeline
- All new code has TDD tests written before implementation

## Out of Scope

- Inline source code preview (showing actual code snippet in the UI)
- GitHub App token management for private repos
- Findings from Tier 2 (LLM-based) scans (they don't produce line numbers)
- External SAST tool findings deep-linking (already handled separately)

## Dependencies

- Existing scanner pipeline (`scanner/patterns.ts`, `scanner/tier1.ts`)
- `process-submission.ts` multi-file fetching
- `submission-store.ts` KV storage types
- Admin submission detail page (`admin/submissions/[id]/page.tsx`)
- Public security report page (`skills/[name]/security/page.tsx`)
