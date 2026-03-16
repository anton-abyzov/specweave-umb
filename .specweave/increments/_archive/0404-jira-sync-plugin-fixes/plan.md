# Plan: JIRA Sync Plugin Critical Fixes (0403)

## Approach

Fix 18 bugs in the `specweave-jira` plugin suite, working from critical to medium priority.
All work scoped to `repositories/anton-abyzov/specweave/plugins/specweave-jira/`.

## Phase 1: Foundation (Critical Infrastructure)

### 1.1 Canonical Metadata Path (US-001)

**Problem**: Three incompatible metadata paths cause silent data loss.

**Approach**:
1. Create `src/shared/metadata-paths.ts` with a single exported constant for the canonical path
2. Add a `readIssueKey(metadata)` helper that checks canonical path first, then falls back to
   legacy paths (`.jira.issue`, `.jira.issueKey`) for backward compatibility
3. Add a `writeIssueKey(metadata, key)` helper that always writes to canonical path
4. Update all 3 affected files to use these helpers
5. Remove the `SPEC-001` placeholder return in `enhanced-jira-sync.js:64` — return `null`/`undefined`
   when no real key exists

**Files to modify**:
- NEW: `src/shared/metadata-paths.ts`
- `enhanced-jira-sync.js`
- `hooks/post-task-completion.sh`
- `jira-spec-commit-sync.ts`

### 1.2 JIRA Deployment Detection (US-002)

**Problem**: Hardcoded `/rest/api/3` breaks all self-hosted JIRA Server/DC instances.

**Approach**:
1. Create `src/shared/jira-client.ts` with deployment detection via `/rest/api/2/serverInfo`
2. Expose `getApiVersion()` → `"2"` (Server/DC) or `"3"` (Cloud)
3. Build API URL helper: `apiUrl(instance, path)` that injects correct version
4. Replace all 4 hardcoded `/rest/api/3` references
5. Update `jira-resource-validator/SKILL.md` to remove the self-hosted hard-block

**Files to modify**:
- NEW: `src/shared/jira-client.ts`
- `jira-spec-sync.ts`
- `jira-epic-sync.ts`
- `jira-status-sync.ts`
- `jira-multi-project-sync.ts`
- `jira-resource-validator/SKILL.md`

## Phase 2: Content and Field Compatibility (High)

### 2.1 Content Format Adapter (US-003)

**Problem**: Wiki markup sent to ADF-only endpoints; plain text comments rejected.

**Approach**:
1. Create `src/shared/content-format.ts` with:
   - `toDescription(content, apiVersion)` → ADF object (v3) or wiki string (v2)
   - `toComment(content, apiVersion)` → ADF comment body (v3) or wiki string (v2)
2. Extract existing wiki-to-ADF conversion logic into shared utility
3. Update epic sync, spec sync, and status sync to use the adapter
4. Adapter selection driven by `getApiVersion()` from Phase 1

**Files to modify**:
- NEW: `src/shared/content-format.ts`
- `jira-epic-sync.ts`
- `jira-spec-sync.ts`
- `jira-status-sync.ts`

### 2.2 Dynamic Epic Link Field (US-004)

**Problem**: Hardcoded `customfield_10014` and no Classic vs Next-gen project detection.

**Approach**:
1. Add `discoverEpicLinkField(instance)` to `jira-client.ts` — queries `/rest/api/*/field`,
   filters for name containing "Epic Link"
2. Add `detectProjectStyle(instance, projectKey)` — checks project response for `style` field
3. Replace hardcoded field references with dynamic lookup
4. Cache field ID per instance in memory (cleared per sync session)

**Files to modify**:
- `src/shared/jira-client.ts` (extend)
- `jira-spec-sync.ts`
- `jira-multi-project-sync.ts`

## Phase 3: Resilience (High)

### 3.1 Pagination Support (US-005, partial)

**Problem**: Search results capped at 50/100 items with no pagination.

**Approach**:
1. Create `src/shared/jira-search.ts` with `searchAllIssues(jql, fields)` that loops
   using `startAt`/`maxResults` until all results fetched
2. Replace direct search calls in `jira-hierarchical-sync.ts`
3. Apply same pattern to any other search calls found during implementation

**Files to modify**:
- NEW: `src/shared/jira-search.ts`
- `jira-hierarchical-sync.ts`

### 3.2 Rate Limit Retry (US-005, partial)

**Problem**: No rate-limit handling anywhere. Bulk operations get throttled silently.

**Approach**:
1. Add retry wrapper to `jira-client.ts` with exponential backoff on HTTP 429
2. Respect `Retry-After` and `X-RateLimit-Remaining` headers
3. Default: 3 retries, base delay 1s, max delay 30s
4. Wrap all outgoing HTTP calls through this client

**Files to modify**:
- `src/shared/jira-client.ts` (extend)

### 3.3 Conflict Resolution (US-006)

**Problem**: Silent "remote-wins" auto-resolve contradicts SKILL.md, causes data loss.

**Approach**:
1. Add `conflictStrategy` config option: `manual` (default), `remote-wins`, `local-wins`
2. When `manual`: detect conflict, write `conflict-report.json`, halt sync with user prompt
3. Remove silent auto-resolve from `jira-spec-sync.ts:447-462`
4. Log conflicts with both local and remote values

**Files to modify**:
- `jira-spec-sync.ts`
- Config schema (if applicable)

## Phase 4: Medium Priority Fixes

### 4.1 Reorganization Detector (US-007)

**Approach**:
1. Fix false positive: compare previous `parent`/Epic Link field values before emitting REPARENTED
2. Implement real handler logic (was a stub): update local hierarchy metadata on REPARENTED

**Files to modify**:
- `reorganization-detector.ts`

### 4.2 Misc Fixes (US-008)

**Approach**:
1. `jira-epic-sync.ts:196`: derive prefix from project key via JIRA API or config
2. `jira-multi-project-sync.ts:115-119`: defer epic creation until after story classification
3. `jira-duplicate-detector.ts:122-130`: return `success: false` on verification failure
4. `scripts/refresh-cache.ts:38`: replace `require.main === module` with
   `import.meta.url === \`file://\${process.argv[1]}\``

**Files to modify**:
- `jira-epic-sync.ts`
- `jira-multi-project-sync.ts`
- `jira-duplicate-detector.ts`
- `scripts/refresh-cache.ts`

## Shared Infrastructure Summary

New shared modules to create:
| Module | Purpose |
|--------|---------|
| `src/shared/metadata-paths.ts` | Canonical metadata path + read/write helpers |
| `src/shared/jira-client.ts` | Deployment detection, API versioning, rate limiting, field discovery |
| `src/shared/content-format.ts` | ADF/wiki format adapter |
| `src/shared/jira-search.ts` | Paginated JQL search |

## Testing Strategy

- Unit tests for each shared module (metadata paths, content format, pagination, rate limiting)
- Integration tests for deployment detection with mocked `/serverInfo` responses
- Regression tests for each individual bug (18 total, one test per bug minimum)
- All tests run via `npx vitest run`

## Risk Mitigation

- Phase 1 (foundation) must complete before Phase 2/3 (they depend on shared client)
- Phase 4 is independent and can run in parallel with Phase 2/3
- Each phase produces a commit so progress is preserved if work is interrupted
