# Implementation Plan: Fix GitHub Sync Links and AC Comments

## Overview

Three targeted fixes in the `specweave-github` plugin to correct broken URLs, missing AC comments, and hardcoded branch references. All changes are in existing files -- no new files needed.

## Architecture

### Affected Components

1. **`plugins/specweave-github/lib/github-feature-sync.ts`** (GitHubFeatureSync)
   - Add default branch detection via GitHub API
   - Pass detected branch to UserStoryIssueBuilder instead of hardcoded `'develop'`

2. **`plugins/specweave-github/lib/user-story-issue-builder.ts`** (UserStoryIssueBuilder)
   - Receive and use detected branch for all URL generation
   - Fix Links section to use increment-relative paths instead of living docs paths

3. **`plugins/specweave-github/lib/user-story-content-builder.ts`** (UserStoryContentBuilder)
   - Replace hardcoded `develop` branch with detected/configurable branch

4. **`plugins/specweave-github/lib/github-ac-comment-poster.ts`** (postACProgressComments)
   - Fix `parseIssueLinks()` to read from metadata.json instead of spec.md frontmatter

5. **`plugins/specweave/hooks/v2/handlers/ac-sync-dispatcher.sh`** (AC Sync Dispatcher)
   - Verify it passes correct paths and config to the sync module

### Data Flow

```
AC completed in spec.md
  → task-ac-sync-guard updates spec.md
  → post-tool-use.sh triggers ac-sync-dispatcher.sh
  → ac-sync-dispatcher.sh reads metadata.json for US issue links
  → ac-progress-sync.ts calls postACProgressComments()
  → parseIssueLinks() reads metadata.json (FIXED: was reading spec.md)
  → gh issue comment posts to correct issue
```

## Implementation Phases

### Phase 1: Default Branch Detection (US-001)

**File**: `github-feature-sync.ts`

Add `detectDefaultBranch()` method that calls:
```typescript
const result = await execFileNoThrow('gh', [
  'api', `repos/${owner}/${repo}`, '--jq', '.default_branch'
], { env: this.getGhEnv() });
```

Cache the result as an instance property. Pass to `UserStoryIssueBuilder` constructor via `repoInfo.branch`.

**File**: `user-story-issue-builder.ts`

Already accepts `branch` via `repoInfo.branch` -- just needs the caller to pass the detected value instead of `'develop'`.

**File**: `user-story-content-builder.ts`

Replace all hardcoded `develop` occurrences with a configurable branch parameter. Add `branch` parameter to `buildIssueBody()` or detect from the same API.

### Phase 2: Fix AC Comment Posting (US-002)

**File**: `github-ac-comment-poster.ts`

Replace `parseIssueLinks()` implementation:
- OLD: Parses `userStories:` YAML block from spec.md frontmatter (never populated)
- NEW: Reads `metadata.json` from the same increment folder as spec.md
  - Derive path: `path.join(path.dirname(specPath), 'metadata.json')`
  - Support both formats:
    - Old: `metadata.github.issues[].userStory` + `.number`
    - New: `metadata.externalLinks.github.issues[US-XXX].issueNumber`

### Phase 3: Fix Links Section (US-003)

**File**: `user-story-issue-builder.ts`

In `buildBody()` Links section (lines 517-551):
- Feature Spec link: Point to increment spec.md instead of living docs FEATURE.md
  - `/.specweave/increments/{incrementId}/spec.md` (always exists in target repo)
- User Story File link: Point to increment spec.md with an anchor for the US section
  - `/.specweave/increments/{incrementId}/spec.md#us-NNN-title`
- Increment link: Already correct (points to increment folder)

## Testing Strategy

- Unit tests for `parseIssueLinks()` with metadata.json format
- Unit tests for default branch detection
- Unit tests for link generation with different branch/repo combinations
- Manual verification against GitHub issue #1207

## Technical Challenges

### Challenge 1: Metadata.json path derivation
**Solution**: `parseIssueLinks()` currently only receives spec.md content. Change to also accept the spec path so we can derive the metadata.json sibling path.
**Risk**: Low -- the metadata.json is always in the same folder as spec.md.

### Challenge 2: Backward compatibility of link format
**Solution**: Existing issues may have old-format links. This only affects newly-synced or re-synced issues -- existing issues won't break.
**Risk**: Low -- links are regenerated on every sync.

### Challenge 3: GitHub API rate limits for branch detection
**Solution**: Cache the default branch for the lifetime of a sync session (one API call per `syncFeatureToGitHub` invocation).
**Risk**: Negligible -- one extra API call per feature sync.
