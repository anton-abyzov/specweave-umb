# Implementation Plan: Scan Findings Deep-Link to Source Code Lines

## Overview

Three layers of changes: scanner data model enrichment (file attribution +
commit SHA), a permalink utility, and UI updates across admin and public pages.
All changes are additive; existing interfaces gain optional fields only.

## Architecture

### Components

- **`scanner/patterns.ts`**: Extended `ScanFinding` with optional `file` field;
  `scanContent()` gains `fileBoundaries` parameter for file-relative line mapping
- **`scanner/github-permalink.ts`** (new): `resolveCommitSha()` GitHub API call
  and `buildGitHubPermalink()` pure URL builder
- **`submission-store.ts`**: `StoredScanFinding` and `StoredScanResult` gain
  `file` and `commitSha` fields respectively
- **`queue/process-submission.ts`**: Builds `FileBoundary[]` from concatenated
  files, calls `resolveCommitSha()`, passes both into scan pipeline and storage
- **`security-report.ts`**: Propagates `commitSha` to `UnifiedSecurityReport`
- **Admin UI** (`admin/submissions/[id]/page.tsx`): Normalized `Finding` type,
  clickable line numbers
- **Public UI** (`skills/[name]/security/page.tsx`): Clickable line numbers where
  data is available

### Data Model Changes

**`ScanFinding`** (patterns.ts):
```typescript
export interface ScanFinding {
  patternId: string;
  patternName: string;
  severity: PatternSeverity;
  category: PatternCategory;
  match: string;
  lineNumber: number;
  context: string;
  file?: string;        // NEW — originating file path
}
```

**`StoredScanFinding`** (submission-store.ts):
```typescript
export interface StoredScanFinding {
  // ... existing fields ...
  file?: string;        // NEW — persisted file path
}
```

**`StoredScanResult`** (submission-store.ts):
```typescript
export interface StoredScanResult {
  // ... existing fields ...
  commitSha?: string;   // NEW — commit SHA at scan time
}
```

**`UnifiedSecurityReport`** (security-report.ts):
```typescript
// latestCommitSha already exists; reuse for tier1/tier2 SHA
// Add scanCommitSha for the internal scan's captured SHA
```

### New Module: `scanner/github-permalink.ts`

```typescript
export interface FileBoundary {
  file: string;
  startLine: number;  // 1-based inclusive
  endLine: number;    // 1-based inclusive
}

export function buildFileBoundaries(
  files: { path: string; content: string }[]
): FileBoundary[];

export async function resolveCommitSha(
  owner: string,
  repo: string,
  ref?: string,
): Promise<string | null>;

export function buildGitHubPermalink(
  owner: string,
  repo: string,
  commitSha: string | null,
  filePath: string | null,
  lineNumber: number,
): string | null;
```

### API Contracts

No new API routes. Existing routes return enriched data (additional optional
fields on findings and scan results). The admin detail API response gains
`commitSha` on scan results and `file` on findings.

## Technology Stack

- **Language**: TypeScript (ESM, `.js` import extensions)
- **Runtime**: Cloudflare Workers (Next.js on OpenNext)
- **Testing**: Vitest, TDD (RED-GREEN-REFACTOR)
- **APIs**: GitHub REST API v3 (`/repos/{owner}/{repo}/commits/{ref}`)

## Architecture Decisions

### ADR-1: File-Boundary Mapping (Option A — chosen)

**Decision**: Extend `scanContent()` with an optional `fileBoundaries` parameter
rather than scanning files individually and merging results.

**Rationale**: Minimal API surface change. Single pass over content is more
efficient. Cross-file patterns (if ever added) still work. The boundary array
is built once in `process-submission.ts` from the file list it already has.

**Alternatives considered**: (B) Scan each file separately and tag results —
requires more changes to `runTier1Scan` and loses single-pass efficiency.

### ADR-2: Commit SHA via API Call

**Decision**: Call `GET /repos/{owner}/{repo}/commits/{ref}` once at scan time.

**Rationale**: We already make GitHub API calls during `fetchRepoFiles()`.
One additional call is negligible. The SHA is captured at the exact moment of
scanning, not at publish time, ensuring accuracy.

**Alternative considered**: Extract SHA from raw.githubusercontent.com headers —
unreliable, not documented.

### ADR-3: Normalize Finding Interface

**Decision**: Replace the ad-hoc admin `Finding` type with `StoredScanFinding`
from `submission-store.ts`.

**Rationale**: Single source of truth for finding shape. Eliminates field
name mismatches (`pattern` vs `patternId`, `line` vs `lineNumber`). The mock
data in the API route also gets updated to match.

## Implementation Phases

### Phase 1: Data Model + Scanner (US-001, US-002)
- Add `file` to `ScanFinding` and `StoredScanFinding`
- Add `commitSha` to `StoredScanResult`
- Implement `FileBoundary` builder and `scanContent` file attribution
- Implement `resolveCommitSha`
- Wire into `process-submission.ts`

### Phase 2: Permalink + UI (US-003, US-004)
- Implement `buildGitHubPermalink`
- Update admin submission detail page (normalize Finding, render links)
- Update public security report page (render links where data available)

## Testing Strategy

TDD enforced. Every function gets a failing test written first.

- **Unit tests**: `scanContent` with file boundaries, `buildFileBoundaries`,
  `resolveCommitSha` (mocked fetch), `buildGitHubPermalink` (pure function)
- **Integration test**: `process-submission` builds boundaries and passes SHA
  through to `storeScanResult`
- **Component tests**: Admin finding row renders `<a>` tag with correct href;
  falls back to plain text when data unavailable

## Technical Challenges

### Challenge 1: Line Number Adjustment
When content from multiple files is concatenated, global line N must be
translated to file-relative line M. Off-by-one errors are likely.

**Solution**: `buildFileBoundaries` assigns 1-based `startLine`/`endLine` ranges.
Binary search or linear scan through boundaries converts global -> local.
Thorough TDD with multi-file fixtures catches edge cases.

**Risk**: Low. The mapping is deterministic and testable.

### Challenge 2: GitHub API Rate Limits
Unauthenticated GitHub API calls are limited to 60/hour.

**Solution**: `resolveCommitSha` is called once per submission, not per finding.
With current submission volume this is well within limits. Returns `null` on
failure; scan still succeeds without a permalink SHA.

**Risk**: Low. Graceful degradation already designed in.
