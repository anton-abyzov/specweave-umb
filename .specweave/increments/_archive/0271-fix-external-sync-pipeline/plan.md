# Implementation Plan: Fix External Sync Pipeline

## Overview

Fix three root causes in the external sync pipeline that prevent GitHub issues from being created: missing living docs folder fallback, suppressed errors, and incomplete metadata format checking.

## Architecture

### Affected Components
- `src/sync/sync-coordinator.ts`: `loadUserStoriesForIncrement()` needs deriveFeatureId fallback and spec.md parsing fallback
- `src/sync/external-issue-auto-creator.ts`: `checkExistingIssue()` needs externalLinks format + error logging
- `src/cli/commands/sync-progress.ts`: `checkExistingGitHubIssue()` + `detectActiveIncrement()` need error logging + externalLinks format

### Data Model
No schema changes. The `externalLinks` format in metadata.json already exists (written by SyncCoordinator since v1.0.240). We're adding READ support for this format in two functions that were missing it.

## Implementation Phases

### Phase 1: Fix loadUserStoriesForIncrement (Critical)
1. Add `deriveFeatureId()` import and fallback in `loadUserStoriesForIncrement()`
2. Add spec.md parsing fallback when living docs folder doesn't exist
3. Add warning logs for fallback paths

### Phase 2: Surface suppressed errors
1. Add `this.logger.warn()` to `checkExistingIssue()` catch block
2. Add `logger.warn()` to `checkExistingGitHubIssue()` catch block
3. Add `logger.log()` to `detectActiveIncrement()` catch block

### Phase 3: Fix externalLinks format checking
1. Add `externalLinks.github` checks to `checkExistingIssue()` in ExternalIssueAutoCreator
2. Add `externalLinks.github` checks to `checkExistingGitHubIssue()` in sync-progress.ts

## Testing Strategy

Manual verification against real metadata.json files in the umbrella repo. Run TypeScript compilation to ensure no type errors.

## Technical Challenges

### Challenge 1: Circular dependency with spec.md parsing
**Solution**: Inline regex-based user story parsing (same approach as ExternalIssueAutoCreator) rather than importing living-docs-sync helpers which would create circular deps.
**Risk**: Low - the regex pattern is well-tested in ExternalIssueAutoCreator.
