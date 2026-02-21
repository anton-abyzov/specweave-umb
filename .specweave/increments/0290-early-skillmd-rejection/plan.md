# Implementation Plan: Reject submissions early when SKILL.md is missing

## Overview

Add a lightweight SKILL.md existence check to the `POST /api/v1/submissions` endpoint. The check runs a single HTTP HEAD/GET against `raw.githubusercontent.com` to verify the file exists before creating any submission record. This avoids wasting queue capacity and KV writes for repos that will inevitably be rejected.

## Architecture

### Components
- **`checkSkillMdExists()`** in `src/lib/scanner.ts`: New exported function that performs a lightweight existence check against raw.githubusercontent.com for a given repo URL and optional skill path. Tries main, then master branch. Returns boolean.
- **`POST /api/v1/submissions` route**: Integrates the pre-check after validation/dedup but before `createSubmission()`. Only for non-internal requests.

### Data Flow (updated)

```
POST /api/v1/submissions
  1. Auth + rate limiting (unchanged)
  2. Body validation (unchanged)
  3. Dedup check (unchanged)
  4. ** NEW: checkSkillMdExists(repoUrl, skillPath) **
     - 404 → return 422 immediately
     - Network error → proceed (fail-open)
     - 200 → proceed
  5. createSubmission() (unchanged)
  6. Queue/process (unchanged)
```

### API Contract Change

**New 422 response** from `POST /api/v1/submissions`:
```json
{
  "error": "No SKILL.md found",
  "details": ["No SKILL.md found at the expected path in the repository. Add a SKILL.md manifest to your repo before submitting."]
}
```

## Technology Stack

- **Language/Framework**: TypeScript, Next.js 15 (App Router)
- **Testing**: Vitest with ESM mocking (`vi.hoisted()` + `vi.mock()`)

**Architecture Decisions**:
- **Fail-open on network errors**: If the GitHub fetch fails, we let the submission through rather than blocking legitimate submissions. The existing check in `processSubmission` will catch it.
- **No caching**: SKILL.md status can change between submissions. Caching adds complexity for minimal benefit given the check is fast (~200ms).
- **Separate function from `fetchSkillContent`**: `fetchSkillContent` returns the full content (string). We only need existence (boolean), and we want to be able to use HEAD requests or short-circuit on status code without reading the body.
- **Keep `processSubmission` check**: The queue consumer also calls `processSubmission` directly. Removing the check there would create a gap for queue-based processing.

## Implementation Phases

### Phase 1: Core
1. Add `checkSkillMdExists()` to `src/lib/scanner.ts`
2. Write unit tests for `checkSkillMdExists()` (mocking fetch)
3. Integrate into `POST /api/v1/submissions` route
4. Write integration tests for the 422 rejection path

### Phase 2: Verification
5. Run full test suite to ensure no regressions
6. Verify existing SKILL.md-missing test in `process-submission.test.ts` still passes

## Testing Strategy

- **Unit tests** for `checkSkillMdExists()`: mock global `fetch`, test 200/404/timeout/network-error paths
- **Route integration tests**: verify 422 response for missing SKILL.md, verify pass-through on network errors, verify internal requests bypass check

## Technical Challenges

### Challenge 1: Branch detection
The repo could use `main` or `master` as default branch. `fetchSkillContent()` already handles this by trying both.
**Solution**: Same approach -- try main first, then master. Return false only if both return 404.

### Challenge 2: Rate limiting from GitHub
Raw.githubusercontent.com is CDN-backed and doesn't count against API rate limits. HEAD/GET requests to it are lightweight.
**Risk**: Low. Fall back to fail-open if anything goes wrong.
