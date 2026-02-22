# Tasks: Repo Health Check for Skill Detail Pages

## Task Notation

- `[T-NNN]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started
- `[x]`: Completed
- Model hints: haiku (simple), opus (default)
- TDD: RED -> GREEN -> REFACTOR for each task

## Phase 1: Infrastructure

### T-001: Add REPO_HEALTH_KV binding
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01 | **Status**: [x] completed
**Test**: Given the platform config -> When wrangler.jsonc is parsed -> Then REPO_HEALTH_KV binding exists

**Description**: Add KV namespace binding for repo health cache.

**Implementation Details**:
- Add `REPO_HEALTH_KV: KVNamespace` to `CloudflareEnv` in `src/lib/env.d.ts`
- Add `REPO_HEALTH_KV` entry in `wrangler.jsonc` `kv_namespaces` array (generate real hex ID via `wrangler kv namespace create REPO_HEALTH_KV`)

**Test Plan**:
- No unit test needed; verified by TypeScript compilation and T-002 tests.

**Dependencies**: None
**Hint**: haiku

---

### T-002: Implement repo-health-store.ts (KV storage layer)
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04 | **Status**: [x] completed
**Test**: Given a RepoHealthResult -> When storeRepoHealth is called -> Then the result is stored in KV with 24h TTL and retrievable via getRepoHealth

**Description**: KV-backed storage module for repo health results, following the `external-scan-store.ts` pattern.

**Implementation Details**:
- Create `src/lib/repo-health-store.ts`
- Define `RepoHealthResult` interface: `{ status: "ONLINE" | "OFFLINE" | "STALE", checkedAt: string, lastCommitAt: string | null }`
- Implement `getKV()` using `getCloudflareContext` + `getWorkerEnv` fallback
- Implement `getRepoHealth(skillName: string): Promise<RepoHealthResult | null>`
- Implement `storeRepoHealth(skillName: string, result: RepoHealthResult): Promise<void>` with 86400s TTL
- Key pattern: `repo-health:{skillName}`

**Test Plan**:
- **File**: `src/lib/__tests__/repo-health-store.test.ts`
- **Tests**:
  - **TC-001**: storeRepoHealth writes to KV with correct key and TTL
    - Given a RepoHealthResult with status ONLINE
    - When storeRepoHealth("my-skill", result) is called
    - Then KV.put is called with key "repo-health:my-skill", JSON payload, and expirationTtl 86400
  - **TC-002**: getRepoHealth returns parsed result when key exists
    - Given KV contains a stored result for "my-skill"
    - When getRepoHealth("my-skill") is called
    - Then the parsed RepoHealthResult is returned with correct fields
  - **TC-003**: getRepoHealth returns null when key does not exist
    - Given KV has no entry for "unknown-skill"
    - When getRepoHealth("unknown-skill") is called
    - Then null is returned

**Dependencies**: T-001
**Hint**: haiku

---

### T-003: Implement repo-health-checker.ts (GitHub API logic) [P]
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03, AC-US1-04, AC-US1-05 | **Status**: [x] completed
**Test**: Given a GitHub repo URL -> When checkRepoHealth is called -> Then it returns ONLINE/OFFLINE/STALE based on API response

**Description**: Pure function that determines repo health by calling the GitHub API.

**Implementation Details**:
- Create `src/lib/repo-health-checker.ts`
- Implement `parseGitHubRepo(repoUrl: string): { owner: string; repo: string } | null`
  - Parse owner/repo from URL, handle trailing slashes, `.git` suffix, tree/blob paths
- Implement `checkRepoHealth(repoUrl: string, githubToken?: string): Promise<RepoHealthResult>`
  - Call `GET https://api.github.com/repos/{owner}/{repo}` with Accept and User-Agent headers
  - If `githubToken` provided, add `Authorization: Bearer {token}` header
  - HTTP 200: check `pushed_at` field; if > 365 days ago return STALE, else ONLINE
  - HTTP 404: return OFFLINE
  - HTTP 403/429 (rate limit) or network error: return OFFLINE
  - Always set `checkedAt` to current ISO timestamp
  - Set `lastCommitAt` from `pushed_at` field (or null if unavailable)

**Test Plan**:
- **File**: `src/lib/__tests__/repo-health-checker.test.ts`
- **Tests**:
  - **TC-004**: parseGitHubRepo extracts owner/repo from standard URL
    - Given "https://github.com/acme/cool-skill"
    - When parseGitHubRepo is called
    - Then { owner: "acme", repo: "cool-skill" } is returned
  - **TC-005**: parseGitHubRepo handles URL with .git suffix
    - Given "https://github.com/acme/cool-skill.git"
    - When parseGitHubRepo is called
    - Then { owner: "acme", repo: "cool-skill" } is returned
  - **TC-006**: parseGitHubRepo handles URL with trailing slash
    - Given "https://github.com/acme/cool-skill/"
    - When parseGitHubRepo is called
    - Then { owner: "acme", repo: "cool-skill" } is returned
  - **TC-007**: parseGitHubRepo returns null for non-GitHub URL
    - Given "https://gitlab.com/acme/cool-skill"
    - When parseGitHubRepo is called
    - Then null is returned
  - **TC-008**: checkRepoHealth returns ONLINE for accessible repo with recent activity
    - Given fetch returns 200 with pushed_at 7 days ago
    - When checkRepoHealth is called
    - Then status is "ONLINE" and lastCommitAt is set
  - **TC-009**: checkRepoHealth returns STALE for repo with old activity
    - Given fetch returns 200 with pushed_at 400 days ago
    - When checkRepoHealth is called
    - Then status is "STALE" and lastCommitAt is set
  - **TC-010**: checkRepoHealth returns OFFLINE for 404 response
    - Given fetch returns 404
    - When checkRepoHealth is called
    - Then status is "OFFLINE" and lastCommitAt is null
  - **TC-011**: checkRepoHealth returns OFFLINE for network error
    - Given fetch throws TypeError
    - When checkRepoHealth is called
    - Then status is "OFFLINE" and lastCommitAt is null
  - **TC-012**: checkRepoHealth includes Authorization header when token provided
    - Given a githubToken is passed
    - When checkRepoHealth is called
    - Then fetch is called with Authorization: Bearer header
  - **TC-013**: checkRepoHealth returns OFFLINE for rate limit (403)
    - Given fetch returns 403
    - When checkRepoHealth is called
    - Then status is "OFFLINE"

**Dependencies**: None (parallelizable with T-002)
**Hint**: opus

---

## Phase 2: API Route

### T-004: Implement GET /api/v1/skills/[name]/repo-health route
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05 | **Status**: [x] completed
**Test**: Given a skill with repoUrl -> When GET /api/v1/skills/{name}/repo-health is called -> Then JSON with status, checkedAt, lastCommitAt is returned

**Description**: Next.js API route that orchestrates cache lookup and live health check.

**Implementation Details**:
- Create `src/app/api/v1/skills/[name]/repo-health/route.ts`
- GET handler:
  1. Decode skill name from params
  2. Look up skill via `getSkillByName(name)` -- if not found, return 404
  3. If skill has no `repoUrl`, return `{ status: "OFFLINE", checkedAt, lastCommitAt: null }`
  4. Check KV cache via `getRepoHealth(name)` -- if hit, return cached result
  5. On cache miss: call `checkRepoHealth(skill.repoUrl, env.GITHUB_TOKEN)`
  6. Store result via `storeRepoHealth(name, result)`
  7. Return result with `Cache-Control: public, max-age=3600`

**Test Plan**:
- **File**: `src/app/api/v1/skills/[name]/repo-health/__tests__/route.test.ts`
- **Tests**:
  - **TC-014**: Returns 404 for nonexistent skill
    - Given no skill with name "nonexistent"
    - When GET /api/v1/skills/nonexistent/repo-health
    - Then response status is 404 with error message
  - **TC-015**: Returns cached result from KV without calling GitHub
    - Given KV has cached ONLINE result for "test-skill"
    - When GET /api/v1/skills/test-skill/repo-health
    - Then cached result is returned and GitHub API is not called
  - **TC-016**: Calls GitHub API on cache miss and stores result
    - Given KV has no cache for "test-skill" and GitHub returns 200
    - When GET /api/v1/skills/test-skill/repo-health
    - Then ONLINE result is returned and stored in KV
  - **TC-017**: Returns OFFLINE when GitHub API returns 404
    - Given KV has no cache and GitHub returns 404
    - When GET /api/v1/skills/test-skill/repo-health
    - Then OFFLINE result is returned
  - **TC-018**: Sets Cache-Control header on success
    - Given a successful response
    - When response headers are checked
    - Then Cache-Control is "public, max-age=3600"
  - **TC-019**: Gracefully handles GitHub API errors
    - Given GitHub API throws network error
    - When GET /api/v1/skills/test-skill/repo-health
    - Then OFFLINE result is returned (not 500)

**Dependencies**: T-002, T-003
**Hint**: opus

---

## Phase 3: Client Component

### T-005: Implement RepoHealthBadge client component [P]
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-06, AC-US1-07 | **Status**: [x] completed
**Test**: Given a skill with repoUrl -> When RepoHealthBadge renders -> Then it shows loading state then status pill

**Description**: `"use client"` component that fetches and displays repo health status.

**Implementation Details**:
- Create `src/app/skills/[name]/RepoHealthBadge.tsx`
- Props: `{ skillName: string; repoUrl: string | undefined }`
- If `repoUrl` is falsy, render nothing (null)
- Use `useState` for status (null | RepoHealthResult) and loading state
- Use `useEffect` to fetch `/api/v1/skills/${encodeURIComponent(skillName)}/repo-health`
- Loading state: render a small gray animated skeleton pill
- Loaded state: render a status pill:
  - ONLINE: green (#10B981), text "ONLINE"
  - OFFLINE: red (#EF4444), text "OFFLINE"
  - STALE: gray (#6B7280), text "STALE"
- Style: match `basePillStyle` from detail page (MONO font, 0.75rem, uppercase, pill shape)
- Error handling: on fetch failure, show nothing (graceful degradation)

**Test Plan**:
- **File**: `src/app/skills/[name]/__tests__/RepoHealthBadge.test.tsx`
- **Tests**:
  - **TC-020**: Renders nothing when repoUrl is undefined
    - Given repoUrl is undefined
    - When component renders
    - Then nothing is rendered (null)
  - **TC-021**: Shows loading skeleton initially
    - Given repoUrl is present and fetch is pending
    - When component renders
    - Then a loading skeleton element is visible
  - **TC-022**: Shows ONLINE pill after successful fetch
    - Given fetch returns { status: "ONLINE" }
    - When component renders and fetch resolves
    - Then green "ONLINE" pill is displayed
  - **TC-023**: Shows OFFLINE pill for OFFLINE status
    - Given fetch returns { status: "OFFLINE" }
    - When component renders and fetch resolves
    - Then red "OFFLINE" pill is displayed
  - **TC-024**: Shows STALE pill for STALE status
    - Given fetch returns { status: "STALE" }
    - When component renders and fetch resolves
    - Then gray "STALE" pill is displayed
  - **TC-025**: Renders nothing on fetch error (graceful degradation)
    - Given fetch throws an error
    - When component renders
    - Then nothing is rendered

**Dependencies**: T-004 (API must exist for integration, but component can be built against mock)
**Hint**: opus

---

### T-006: Integrate RepoHealthBadge into skill detail page
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02 | **Status**: [x] completed
**Test**: Given the skill detail page -> When it renders a skill with repoUrl -> Then the RepoHealthBadge component appears next to the Repository link

**Description**: Import and render `RepoHealthBadge` in the existing skill detail page.

**Implementation Details**:
- Edit `src/app/skills/[name]/page.tsx`
- Import `RepoHealthBadge` from `./RepoHealthBadge`
- In the Repository `MetaRow` section (around line 222-240), add `<RepoHealthBadge skillName={skill.name} repoUrl={skill.repoUrl} />` inline next to the repo link
- Wrap the repo link and badge in a flex container with gap for proper spacing

**Test Plan**:
- Manual verification (server component; integration tested via T-005 and T-014-T-019)
- Verify: page renders without errors, badge appears next to repo link, no SSR blocking

**Dependencies**: T-005
**Hint**: haiku

---

## Phase 4: Verification

### T-007: Run full test suite and verify all ACs
**User Story**: US-001, US-002, US-003 | **Satisfies ACs**: All | **Status**: [x] completed
**Test**: Given all tasks completed -> When full test suite runs -> Then all tests pass with >80% coverage

**Description**: Final verification pass.

**Implementation Details**:
- Run `npm test` in vskill-platform to verify all new tests pass
- Run `npx vitest --coverage` and verify >80% coverage on new files
- Manually verify TypeScript compilation (`npx tsc --noEmit`)
- Walk through each AC in spec.md and mark completed

**Dependencies**: T-001 through T-006
**Hint**: haiku
