# Tasks: Scan Findings Deep-Link to Source Code Lines

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started
- `[x]`: Completed
- Model hints: haiku (simple), opus (default)
- TDD: RED (write failing test) -> GREEN (minimal impl) -> REFACTOR

## Phase 1: Data Model + Scanner

### US-001: File-Boundary Mapping in Scanner (P1)

#### T-001: Add `file` field to `ScanFinding` interface
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [ ] not started

**Description**: Add optional `file?: string` field to `ScanFinding` in
`scanner/patterns.ts`.

**AC**: AC-US1-01

**Implementation Details**:
- Add `file?: string` to `ScanFinding` interface
- Ensure existing tests still pass (field is optional)

**Test Plan**:
- **File**: `src/lib/scanner/__tests__/patterns.test.ts`
- **Tests**:
  - **TC-001**: ScanFinding allows optional file field
    - Given a ScanFinding object with `file: "SKILL.md"`
    - When the object is type-checked
    - Then it compiles without error
  - **TC-002**: ScanFinding without file field is valid
    - Given a ScanFinding object without `file`
    - When the object is type-checked
    - Then it compiles without error (backward compat)

**Dependencies**: None
**Status**: [ ] Not Started

---

#### T-002: Implement `buildFileBoundaries` utility
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [ ] not started

**Description**: Create `scanner/github-permalink.ts` with `FileBoundary`
interface and `buildFileBoundaries()` function that maps file paths to 1-based
line ranges in concatenated content.

**AC**: AC-US1-02

**Implementation Details**:
- Define `FileBoundary { file: string; startLine: number; endLine: number }`
- `buildFileBoundaries(files: { path: string; content: string }[])` returns `FileBoundary[]`
- Count newlines in each file's content to determine line ranges
- Lines are 1-based, ranges are inclusive

**Test Plan**:
- **File**: `src/lib/scanner/__tests__/github-permalink.test.ts`
- **Tests**:
  - **TC-003**: Single file returns one boundary 1..N
    - Given files = `[{ path: "SKILL.md", content: "line1\nline2\nline3" }]`
    - When `buildFileBoundaries(files)` is called
    - Then result is `[{ file: "SKILL.md", startLine: 1, endLine: 3 }]`
  - **TC-004**: Two files with correct offsets
    - Given files = `[{ path: "SKILL.md", content: "a\nb" }, { path: "index.js", content: "c\nd\ne" }]`
    - When `buildFileBoundaries(files)` is called
    - Then result is `[{ file: "SKILL.md", startLine: 1, endLine: 2 }, { file: "index.js", startLine: 3, endLine: 5 }]`
  - **TC-005**: Empty file list returns empty array
    - Given files = `[]`
    - When `buildFileBoundaries(files)` is called
    - Then result is `[]`
  - **TC-006**: File with single line (no trailing newline)
    - Given files = `[{ path: "a.md", content: "hello" }]`
    - When `buildFileBoundaries(files)` is called
    - Then result is `[{ file: "a.md", startLine: 1, endLine: 1 }]`

**Dependencies**: None
**Status**: [ ] Not Started

---

#### T-003: Extend `scanContent` with file boundary support
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03, AC-US1-04 | **Status**: [ ] not started

**Description**: Modify `scanContent()` in `scanner/patterns.ts` to accept
optional `fileBoundaries` parameter. When provided, each finding gets `file`
set and `lineNumber` adjusted to file-relative.

**AC**: AC-US1-03, AC-US1-04

**Implementation Details**:
- Add optional second param `fileBoundaries?: FileBoundary[]`
- After finding a match at global lineNumber, look up which boundary contains it
- Set `finding.file = boundary.file`
- Adjust `finding.lineNumber = globalLine - boundary.startLine + 1`
- When `fileBoundaries` is undefined, skip file attribution (backward compat)

**Test Plan**:
- **File**: `src/lib/scanner/__tests__/patterns.test.ts`
- **Tests**:
  - **TC-007**: Finding in first file gets correct file and adjusted line
    - Given content = `"safe\neval(\nmore"` with boundaries `[{ file: "a.md", startLine: 1, endLine: 3 }]`
    - When `scanContent(content, boundaries)` is called
    - Then finding has `file: "a.md"` and `lineNumber: 2`
  - **TC-008**: Finding in second file gets correct file and adjusted line
    - Given content with two files concatenated, finding in second file at global line 5
    - When `scanContent(content, boundaries)` is called
    - Then finding has `file` of second file and `lineNumber` relative to that file
  - **TC-009**: Without boundaries, lineNumber is unchanged (backward compat)
    - Given content with a finding at global line 2
    - When `scanContent(content)` is called (no boundaries)
    - Then finding has no `file` field and `lineNumber: 2`

**Dependencies**: T-001, T-002
**Status**: [ ] Not Started

---

#### T-004: Add `file` to `StoredScanFinding` and wire in `process-submission.ts`
**User Story**: US-001 | **Satisfies ACs**: AC-US1-05, AC-US1-06 | **Status**: [ ] not started

**Description**: Add `file?: string` to `StoredScanFinding`. Update
`process-submission.ts` to build `fileBoundaries` from the fetched file list
and pass them to `runTier1Scan`.

**AC**: AC-US1-05, AC-US1-06

**Implementation Details**:
- Add `file?: string` to `StoredScanFinding` in `submission-store.ts`
- In `process-submission.ts`, build file list: `[{ path: skillPath, content: skillMd }, ...additionalFiles.map((c, i) => ({ path: additionalFilePaths[i], content: c }))]`
- Call `buildFileBoundaries(fileList)` before `runTier1Scan`
- Pass boundaries through to `scanContent` (via extending `runTier1Scan` signature)

**Test Plan**:
- **File**: `src/lib/queue/__tests__/process-submission.test.ts`
- **Tests**:
  - **TC-010**: Stored findings include file field when multi-file scan
    - Given a submission with SKILL.md + index.js
    - When processSubmission runs
    - Then stored scan result findings have `file` populated
  - **TC-011**: Single-file scan findings have file set to skill path
    - Given a submission with only SKILL.md
    - When processSubmission runs
    - Then findings (if any) have `file: "SKILL.md"`

**Dependencies**: T-003
**Status**: [ ] Not Started

---

### US-002: Commit SHA Capture at Scan Time (P1)

#### T-005: Implement `resolveCommitSha` utility
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-04 | **Status**: [ ] not started

**Description**: Add `resolveCommitSha(owner, repo, ref?)` to
`scanner/github-permalink.ts`. Calls GitHub API and returns SHA or null.

**AC**: AC-US2-01, AC-US2-04

**Implementation Details**:
- `GET https://api.github.com/repos/{owner}/{repo}/commits/{ref}` with `Accept: application/vnd.github.sha` header
- Default ref = "HEAD"
- Timeout: 5s
- On error (network, non-200): return null (graceful degradation)

**Test Plan**:
- **File**: `src/lib/scanner/__tests__/github-permalink.test.ts`
- **Tests**:
  - **TC-012**: Returns SHA on successful API call
    - Given fetch returns 200 with SHA text
    - When `resolveCommitSha("owner", "repo")` is called
    - Then returns the SHA string
  - **TC-013**: Returns null on 404
    - Given fetch returns 404
    - When `resolveCommitSha("owner", "repo")` is called
    - Then returns null
  - **TC-014**: Returns null on network error
    - Given fetch throws
    - When `resolveCommitSha("owner", "repo")` is called
    - Then returns null
  - **TC-015**: Returns null on timeout
    - Given fetch times out
    - When `resolveCommitSha("owner", "repo")` is called
    - Then returns null

**Dependencies**: None
**Status**: [ ] Not Started

---

#### T-006: Add `commitSha` to `StoredScanResult` and wire in pipeline
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02, AC-US2-03 | **Status**: [ ] not started

**Description**: Add `commitSha?: string` to `StoredScanResult`. Call
`resolveCommitSha` in `process-submission.ts` and store on scan result.

**AC**: AC-US2-02, AC-US2-03

**Implementation Details**:
- Add `commitSha?: string` to `StoredScanResult` in `submission-store.ts`
- In `process-submission.ts`, after extracting owner/repo from repoUrl, call `resolveCommitSha(owner, repo)`
- Pass resulting SHA to `storeScanResult` payload

**Test Plan**:
- **File**: `src/lib/queue/__tests__/process-submission.test.ts`
- **Tests**:
  - **TC-016**: Scan result includes commitSha when API succeeds
    - Given resolveCommitSha returns "abc1234"
    - When processSubmission runs
    - Then stored scan result has `commitSha: "abc1234"`
  - **TC-017**: Scan completes without commitSha when API fails
    - Given resolveCommitSha returns null
    - When processSubmission runs
    - Then stored scan result has `commitSha: undefined` and scan still succeeds

**Dependencies**: T-005
**Status**: [ ] Not Started

---

#### T-007: Propagate `commitSha` to `UnifiedSecurityReport`
**User Story**: US-002 | **Satisfies ACs**: AC-US2-05 | **Status**: [ ] not started

**Description**: Read `commitSha` from `StoredScanResult` and expose it on
`UnifiedSecurityReport` (via `Tier1Report` or top-level field).

**AC**: AC-US2-05

**Implementation Details**:
- Add `scanCommitSha?: string` to `Tier1Report` in `security-report.ts`
- Populate from `scan.commitSha` in `getUnifiedSecurityReport`
- Downstream pages already have `report.tier1.scanCommitSha` available

**Test Plan**:
- **File**: `src/lib/__tests__/security-report.test.ts`
- **Tests**:
  - **TC-018**: Report includes scanCommitSha from stored scan
    - Given a stored scan result with `commitSha: "abc1234"`
    - When `getUnifiedSecurityReport` is called
    - Then `report.tier1.scanCommitSha` equals "abc1234"

**Dependencies**: T-006
**Status**: [ ] Not Started

---

## Phase 2: Permalink + UI

### US-003: GitHub Permalink Construction (P1)

#### T-008: Implement `buildGitHubPermalink` pure function
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03 | **Status**: [ ] not started

**Description**: Pure function that builds a GitHub blob permalink URL from
owner, repo, commitSha, filePath, and lineNumber.

**AC**: AC-US3-01, AC-US3-02, AC-US3-03

**Implementation Details**:
- Returns `https://github.com/{owner}/{repo}/blob/{sha}/{path}#L{line}`
- When commitSha is null, use "main" as fallback
- When filePath is null, return null

**Test Plan**:
- **File**: `src/lib/scanner/__tests__/github-permalink.test.ts`
- **Tests**:
  - **TC-019**: Full permalink with SHA
    - Given owner="acme", repo="skill", sha="abc1234", file="SKILL.md", line=42
    - When `buildGitHubPermalink(...)` is called
    - Then returns "https://github.com/acme/skill/blob/abc1234/SKILL.md#L42"
  - **TC-020**: Fallback to main when SHA is null
    - Given sha=null
    - When `buildGitHubPermalink(...)` is called
    - Then URL uses "main" instead of SHA
  - **TC-021**: Returns null when file is null
    - Given file=null
    - When `buildGitHubPermalink(...)` is called
    - Then returns null
  - **TC-022**: Handles nested file paths
    - Given file="scripts/setup.sh"
    - When `buildGitHubPermalink(...)` is called
    - Then URL contains "/blob/sha/scripts/setup.sh#L10"

**Dependencies**: None
**Status**: [ ] Not Started

---

#### T-009: Update admin submission detail page with clickable line numbers
**User Story**: US-003 | **Satisfies ACs**: AC-US3-04 | **Status**: [ ] not started

**Description**: Render finding line numbers as `<a>` tags linking to GitHub
permalinks in the admin submission detail page.

**AC**: AC-US3-04

**Implementation Details**:
- Import `buildGitHubPermalink` from `scanner/github-permalink`
- Extract owner/repo from `submission.repoUrl`
- For each finding, build permalink using scan's `commitSha`, finding's `file`, and `lineNumber`
- If permalink is non-null, render as `<a href={link} target="_blank" rel="noopener noreferrer">`
- If null, render as plain text `L{lineNumber}`

**Test Plan**:
- **File**: `src/app/admin/submissions/[id]/__tests__/deep-link.test.tsx`
- **Tests**:
  - **TC-023**: Line number renders as link when permalink data available
    - Given a finding with file="SKILL.md", lineNumber=42, and scan commitSha="abc"
    - When the component renders
    - Then the line number is an `<a>` tag with correct href
  - **TC-024**: Line number renders as plain text when file is missing
    - Given a finding without file field
    - When the component renders
    - Then line number is plain text "L42"

**Dependencies**: T-008, T-004 (for Finding type)
**Status**: [ ] Not Started

---

#### T-010: Update public security report page with clickable findings
**User Story**: US-003 | **Satisfies ACs**: AC-US3-05 | **Status**: [ ] not started

**Description**: If tier1 findings data is surfaced on the public security page,
render line numbers as clickable permalinks.

**AC**: AC-US3-05

**Implementation Details**:
- The public security page currently shows tier1 breakdown but not individual findings
- If/when findings are surfaced, use `buildGitHubPermalink` with `report.tier1.scanCommitSha`
- For now, ensure the data pipeline exposes findings if needed in the future

**Test Plan**:
- **File**: `src/app/skills/[name]/security/__tests__/permalink.test.tsx`
- **Tests**:
  - **TC-025**: Commit SHA link uses scanCommitSha from report
    - Given a report with `tier1.scanCommitSha = "abc1234"`
    - When the commit integrity section renders
    - Then the SHA link points to the correct commit URL

**Dependencies**: T-007, T-008
**Status**: [ ] Not Started

---

### US-004: Normalize Admin Finding Interface (P2)

#### T-011: Replace admin Finding interface with StoredScanFinding
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02 | **Status**: [ ] not started

**Description**: Remove the ad-hoc `Finding` interface from the admin page and
import `StoredScanFinding` from `submission-store.ts`. Update field references.

**AC**: AC-US4-01, AC-US4-02

**Implementation Details**:
- Remove local `Finding` interface from `admin/submissions/[id]/page.tsx`
- Import `StoredScanFinding` from `@/lib/submission-store`
- Update `ScanResult` interface to use `findings: StoredScanFinding[]`
- Update rendering: `finding.pattern` -> `finding.patternId`, `finding.message` -> `finding.context`, `finding.line` -> `finding.lineNumber`
- Add rendering for new fields: `finding.patternName`, `finding.category`, `finding.file`

**Test Plan**:
- **File**: `src/app/admin/submissions/[id]/__tests__/finding-normalization.test.tsx`
- **Tests**:
  - **TC-026**: Finding row renders patternId instead of pattern
    - Given a StoredScanFinding with patternId="CI-001"
    - When the finding row renders
    - Then "CI-001" appears in the pattern code element
  - **TC-027**: Finding row renders patternName
    - Given a StoredScanFinding with patternName="exec() call"
    - When the finding row renders
    - Then "exec() call" appears in the finding message area

**Dependencies**: T-004
**Status**: [ ] Not Started

---

#### T-012: Update admin API mock data to use StoredScanFinding shape
**User Story**: US-004 | **Satisfies ACs**: AC-US4-03 | **Status**: [ ] not started

**Description**: Update mock submissions in `admin/submissions/[id]/route.ts` to
use the `StoredScanFinding` field names.

**AC**: AC-US4-03

**Implementation Details**:
- Change mock finding objects from `{ severity, pattern, message, line }` to
  `{ patternId, patternName, severity, category, match, lineNumber, context, file }`
- Add realistic values for new fields

**Test Plan**:
- **File**: `src/app/api/v1/admin/submissions/[id]/__tests__/route.test.ts`
- **Tests**:
  - **TC-028**: Mock findings use StoredScanFinding shape
    - Given a GET request for sub-001
    - When the response is received
    - Then findings have `patternId`, `patternName`, `lineNumber` fields

**Dependencies**: None
**Status**: [ ] Not Started

---

#### T-013: Backward compatibility for findings without new fields
**User Story**: US-004 | **Satisfies ACs**: AC-US4-04, AC-US4-05 | **Status**: [ ] not started

**Description**: Ensure the finding row component gracefully handles findings
that lack `file`, `commitSha`, `patternName`, or `category` fields (data from
before the migration).

**AC**: AC-US4-04, AC-US4-05

**Implementation Details**:
- Use optional chaining for `finding.file`, `finding.patternName`, `finding.category`
- Fallback rendering: no link when file missing, show patternId if patternName missing
- Test with both old-format and new-format findings

**Test Plan**:
- **File**: `src/app/admin/submissions/[id]/__tests__/finding-normalization.test.tsx`
- **Tests**:
  - **TC-029**: Finding without file renders plain line number
    - Given a finding with lineNumber=42 but no file field
    - When the finding row renders
    - Then line number shows as "L42" (plain text, no link)
  - **TC-030**: Finding without patternName shows patternId
    - Given a finding with patternId="CI-001" but no patternName
    - When the finding row renders
    - Then "CI-001" is shown

**Dependencies**: T-011
**Status**: [ ] Not Started

## Phase 3: Verification

- [ ] [T-014] Run full test suite (`npm test`) and verify all pass
- [ ] [T-015] Verify all acceptance criteria in spec.md are satisfied
- [ ] [T-016] Verify no type errors (`npx tsc --noEmit`)
