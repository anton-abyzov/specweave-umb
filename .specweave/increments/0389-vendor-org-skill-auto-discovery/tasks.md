# Tasks: Vendor org skill auto-discovery and import

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started
- `[x]`: Completed
- Model hints: haiku (simple), opus (default)

## Phase 1: Crawl-Worker Source Module

### US-001: Automated vendor org repo enumeration (P1)
### US-005: Pipeline integration via bulk submissions (P1)

#### T-001: Create vendor-org-discovery.js crawl source

**User Story**: US-001, US-005 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05, AC-US1-06, AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04
**Status**: [x] Completed

**Description**: Create `crawl-worker/sources/vendor-org-discovery.js` — the main crawl source module that enumerates all public repos from vendor orgs and discovers SKILL.md files. Follows the `github-sharded.js` pattern exactly.

**Implementation Details**:
1. Define `VENDOR_ORGS` constant array: `["anthropics", "openai", "google-gemini", "google"]` (matching `vendor-detect.js` pattern)
2. Implement `createTokenRotator(tokensStr)` — round-robin token rotation from `GITHUB_TOKENS` env var
3. Implement `computeDelay(remaining, resetEpoch)` — adaptive delay based on `x-ratelimit-remaining` header
4. Implement `listOrgRepos(org, getToken)`:
   - Paginated `GET /orgs/{org}/repos?type=public&per_page=100&sort=updated`
   - Skip repos where `fork === true` or `stargazers_count === 0`
   - Token rotation on each request
5. Implement `scanRepoTree(owner, repo, defaultBranch, getToken)`:
   - `GET /repos/{owner}/{repo}/git/trees/{defaultBranch}?recursive=1`
   - Filter tree entries for blobs ending in `/SKILL.md` or equal to `SKILL.md`
   - Exclude paths inside agent config dirs (inline regex: `/(?:^|\/)\.(?:claude|cursor|trae|windsurf|aider|continue|codeium|codex|copilot|roo|cline|sourcegraph|tabnine|supermaven|gemini|amazonq|opencode|aide|devin|warp|bolt|replit|agents?|vscode|idea|zed|devcontainer)\//i`)
6. Implement `export default async function crawl(config)`:
   - Extract `githubTokens`, `platformUrl`, `internalKey`, `batchSize` from config
   - Create `InlineSubmitter(platformUrl, internalKey, batchSize || 15)`
   - For each org: list repos → scan trees → `submitter.add()` for each discovered skill
   - Call `submitter.flush()` at end
   - Return `{ totalDiscovered, totalSubmitted, errors, orgBreakdown, durationMs }`
7. Add 60s backoff on 403/429 responses with one retry

**Test Plan**:
- **File**: `crawl-worker/__tests__/vendor-org-discovery.test.js`
- **Tests**:
  - **TC-001**: Discovers SKILL.md files from vendor org repos
    - Given a mock GitHub API returning 2 repos for "anthropics" org with 3 SKILL.md files
    - When crawl(config) is called
    - Then totalDiscovered equals 3 and InlineSubmitter.add was called 3 times with correct repo objects
  - **TC-002**: Skips fork repos during enumeration
    - Given a mock API returning repos where 1 has `fork: true`
    - When crawl(config) is called
    - Then the fork repo is not tree-scanned
  - **TC-003**: Skips zero-star repos during enumeration
    - Given a mock API returning repos where 1 has `stargazers_count: 0`
    - When crawl(config) is called
    - Then the zero-star repo is not tree-scanned
  - **TC-004**: Excludes SKILL.md inside agent config directories
    - Given a repo tree containing `.claude/skills/foo/SKILL.md` and `plugins/bar/SKILL.md`
    - When scanRepoTree is called
    - Then only `plugins/bar/SKILL.md` is returned
  - **TC-005**: Rotates tokens across API calls
    - Given config with `githubTokens: "token1,token2"`
    - When multiple API calls are made
    - Then Authorization headers alternate between token1 and token2
  - **TC-006**: Applies adaptive delay on low rate limit remaining
    - Given API response with `x-ratelimit-remaining: 10`
    - When computeDelay is called
    - Then delay is > 0ms
  - **TC-007**: Backs off on 403/429 and retries once
    - Given API returning 429 on first call, 200 on retry
    - When listOrgRepos is called
    - Then the retry succeeds after 60s backoff
  - **TC-008**: Handles paginated org repo listing
    - Given org with 150 repos (2 pages)
    - When listOrgRepos is called
    - Then all 150 repos are returned via Link header pagination
  - **TC-009**: Returns correct stats object matching scheduler contract
    - Given a successful crawl run
    - When crawl completes
    - Then return has totalDiscovered, totalSubmitted, errors, orgBreakdown, durationMs
  - **TC-010**: Submits via InlineSubmitter with correct repo shape
    - Given discovered skill at `plugins/foo/skills/bar/SKILL.md` in `anthropics/claude-plugins-official`
    - When submitter.add is called
    - Then repo object has `{ fullName, repoUrl, skillName: "bar", skillPath: "plugins/foo/skills/bar/SKILL.md", source: "vendor-org-discovery" }`

**Dependencies**: None

---

#### T-002: Register vendor-org-discovery in scheduler and server

**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03
**Status**: [x] Completed

**Description**: Add `vendor-org-discovery` to the scheduler's timeout/cooldown maps and server's valid sources array.

**Implementation Details**:
1. In `crawl-worker/scheduler.js`:
   - Add to `SOURCE_TIMEOUTS`: `"vendor-org-discovery": 30 * 60 * 1000` (30 min)
   - Add to `SOURCE_COOLDOWNS`: `"vendor-org-discovery": 6 * 60 * 60 * 1000` (6 hours)
2. In `crawl-worker/server.js`:
   - Add `"vendor-org-discovery"` to `VALID_SOURCES` array

**Test Plan**:
- **File**: `crawl-worker/__tests__/scheduler-registration.test.js`
- **Tests**:
  - **TC-011**: vendor-org-discovery has 30-min timeout in SOURCE_TIMEOUTS
    - Given scheduler.js is imported
    - When SOURCE_TIMEOUTS is inspected
    - Then `vendor-org-discovery` equals `1800000`
  - **TC-012**: vendor-org-discovery has 6-hour cooldown in SOURCE_COOLDOWNS
    - Given scheduler.js is imported
    - When SOURCE_COOLDOWNS is inspected
    - Then `vendor-org-discovery` equals `21600000`
  - **TC-013**: vendor-org-discovery is in VALID_SOURCES
    - Given server.js is imported
    - When VALID_SOURCES is inspected
    - Then it includes `"vendor-org-discovery"`

**Dependencies**: T-001

---

## Phase 2: Platform-Side Admin Endpoint

### US-004: Admin on-demand discovery endpoint (P2)
### US-002: Deduplication and force-rescan (P1)

#### T-003: Create platform-side vendor-org-discovery.ts

**User Story**: US-002, US-004 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US4-04
**Status**: [x] Completed

**Description**: Create `src/lib/crawler/vendor-org-discovery.ts` — platform-side discovery logic for the admin endpoint. Uses `TokenRotator` from `github-discovery.ts`, dedup via `discovery-dedup.ts`, and `VENDOR_ORGS` from `trusted-orgs.ts`.

**Implementation Details**:
1. Import `TokenRotator` from `./github-discovery`
2. Import `VENDOR_ORGS` from `../trust/trusted-orgs`
3. Import `hasBeenDiscovered`, `markDiscovered`, `logDiscoveryRun` from `./discovery-dedup`
4. Import `isAgentConfigPath` from `../skill-path-validation`
5. Implement `listOrgRepos(org, headers)` — paginated `GET /orgs/{org}/repos?type=public&per_page=100&sort=updated`, skip forks and zero-star
6. Implement `scanRepoTree(owner, repo, headers)` — Trees API, filter SKILL.md, exclude agent config paths via `isAgentConfigPath`
7. Implement `runVendorOrgDiscovery(options)`:
   - Options: `{ orgs?: string[], force?: boolean, dryRun?: boolean, env: DiscoveryEnv }`
   - Create `TokenRotator` from env
   - For each org: list repos → scan trees → dedup check via `hasBeenDiscovered`
   - If not dedup'd (or `force: true`): submit via `WORKER_SELF_REFERENCE` or internal `POST /api/v1/submissions/bulk`
   - If `dryRun: true`: skip submission, just count
   - Mark discovered via `markDiscovered` with source `"vendor-org-discovery"`
   - Log run via `logDiscoveryRun`
   - Return `{ candidatesFound, newSubmissions, skippedDedup, skippedFiltered, orgBreakdown, durationMs }`

**Test Plan**:
- **File**: `src/lib/crawler/__tests__/vendor-org-discovery.test.ts`
- **Tests**:
  - **TC-014**: Discovers skills from vendor org repos
    - Given mocked GitHub API returning repos with SKILL.md files for anthropics org
    - When runVendorOrgDiscovery is called
    - Then candidatesFound reflects total SKILL.md files found
  - **TC-015**: Deduplicates against DiscoveryRecord
    - Given a skill already in DiscoveryRecord (hasBeenDiscovered returns true)
    - When runVendorOrgDiscovery is called without force
    - Then skippedDedup is incremented and skill is not submitted
  - **TC-016**: Force mode bypasses dedup
    - Given a skill already in DiscoveryRecord
    - When runVendorOrgDiscovery is called with force: true
    - Then the skill IS submitted despite existing record
  - **TC-017**: Dry run mode skips submissions
    - Given discovered skills
    - When runVendorOrgDiscovery is called with dryRun: true
    - Then no submissions are created and newSubmissions equals 0
  - **TC-018**: Marks discovered skills via markDiscovered
    - Given a new skill is submitted successfully
    - When runVendorOrgDiscovery completes
    - Then markDiscovered is called with source "vendor-org-discovery"
  - **TC-019**: Logs discovery run via logDiscoveryRun
    - Given a completed discovery run
    - When runVendorOrgDiscovery finishes
    - Then logDiscoveryRun is called with correct stats
  - **TC-020**: Filters specific orgs when provided
    - Given orgs option is `["anthropics"]`
    - When runVendorOrgDiscovery is called
    - Then only anthropics org is scanned (not openai, google, etc.)
  - **TC-021**: Excludes agent config paths via isAgentConfigPath
    - Given a repo tree with `.claude/skills/foo/SKILL.md`
    - When scanRepoTree is called
    - Then the path is excluded

**Dependencies**: None (parallel with T-001)

---

#### T-004: Create admin endpoint route for vendor-org discovery

**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04
**Status**: [x] Completed

**Description**: Create `src/app/api/v1/admin/discovery/vendor-orgs/route.ts` — Next.js API route for on-demand vendor discovery.

**Implementation Details**:
1. Export `async function POST(request: NextRequest)`
2. Auth: check `hasInternalAuth(request)` OR `requireRole(request, "SUPER_ADMIN")`
3. Parse optional body: `{ orgs?: string[], force?: boolean, dryRun?: boolean }`
4. Call `runVendorOrgDiscovery({ orgs, force, dryRun, env })`
5. Return JSON response with `{ ok, candidatesFound, newSubmissions, skippedDedup, skippedFiltered, orgBreakdown, durationMs }`
6. Wrap in try/catch: 500 on errors with `{ error: "Vendor org discovery failed" }`

**Test Plan**:
- **File**: `src/app/api/v1/admin/discovery/vendor-orgs/__tests__/route.test.ts`
- **Tests**:
  - **TC-022**: Rejects unauthenticated requests
    - Given a request with no auth headers
    - When POST is called
    - Then response is 401/403
  - **TC-023**: Accepts internal key auth
    - Given a request with valid X-Internal-Key header
    - When POST is called
    - Then discovery runs and returns 200
  - **TC-024**: Accepts SUPER_ADMIN JWT auth
    - Given a request with valid SUPER_ADMIN JWT
    - When POST is called
    - Then discovery runs and returns 200
  - **TC-025**: Passes orgs filter to discovery
    - Given body `{ orgs: ["anthropics"] }`
    - When POST is called
    - Then runVendorOrgDiscovery receives orgs: ["anthropics"]
  - **TC-026**: Passes force and dryRun flags
    - Given body `{ force: true, dryRun: true }`
    - When POST is called
    - Then runVendorOrgDiscovery receives force: true, dryRun: true
  - **TC-027**: Returns correct response shape
    - Given a successful discovery run
    - When POST returns
    - Then response includes ok, candidatesFound, newSubmissions, skippedDedup, skippedFiltered, orgBreakdown, durationMs

**Dependencies**: T-003

---

#### T-005: Register vendor-orgs in SOURCE_FUNCTIONS map

**User Story**: US-004 | **Satisfies ACs**: AC-US4-05
**Status**: [x] Completed

**Description**: Register `"vendor-orgs"` as a valid source in `src/lib/crawler/github-discovery.ts` `SOURCE_FUNCTIONS` map.

**Implementation Details**:
1. Import `runVendorOrgDiscovery` from `./vendor-org-discovery`
2. Add `"vendor-orgs"` entry to `SOURCE_FUNCTIONS` map
3. The function should wrap `runVendorOrgDiscovery` to match the existing `(headers, seen) => Promise<DiscoveredRepo[]>` signature

**Test Plan**:
- **File**: `src/lib/crawler/__tests__/github-discovery.test.ts` (extend existing)
- **Tests**:
  - **TC-028**: vendor-orgs is a valid source in SOURCE_FUNCTIONS
    - Given github-discovery.ts VALID_SOURCES export
    - When inspected
    - Then it includes "vendor-orgs"

**Dependencies**: T-003

---

## Phase 3: Deployment Configuration

### US-003: Scheduled execution on VM-2 (P1)

#### T-006: Update VM-2 deployment config

**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-04
**Status**: [x] Completed

**Description**: Update VM-2's env configuration to include `vendor-org-discovery` in `ASSIGNED_SOURCES`.

**Implementation Details**:
1. Update `crawl-worker/.env.vm2` (or deployment config) to add `vendor-org-discovery` to `ASSIGNED_SOURCES`
2. Verify the current `ASSIGNED_SOURCES` for VM-2 includes: `github-graphql-check`, `sourcegraph`, `submission-scanner` — add `vendor-org-discovery` to this list
3. Document in the PR that VM-2 deploy is required after merge

**Test Plan**:
- **Tests**:
  - **TC-029**: Manual verification — VM-2 ASSIGNED_SOURCES includes vendor-org-discovery
    - Given VM-2 .env file
    - When ASSIGNED_SOURCES is read
    - Then it contains "vendor-org-discovery"

**Dependencies**: T-001, T-002

---

## Phase 4: Integration Testing

#### T-007: End-to-end integration test

**User Story**: US-001, US-002, US-005 | **Satisfies ACs**: AC-US5-03
**Status**: [x] Completed

**Description**: Verify the full flow: vendor-org-discovery → InlineSubmitter → bulk submissions → processSubmission → VENDOR_APPROVED → PUBLISHED.

**Test Plan**:
- **File**: `crawl-worker/__tests__/vendor-org-e2e.test.js`
- **Tests**:
  - **TC-030**: Full pipeline: discovery to published
    - Given mocked GitHub API for anthropics org with 1 repo and 1 SKILL.md
    - When crawl(config) is called with a mock platform server
    - Then InlineSubmitter POSTs to /api/v1/submissions/bulk with correct payload shape including repoUrl, skillName, skillPath
  - **TC-031**: No duplicates on consecutive runs
    - Given a first crawl run that discovers 3 skills
    - When a second crawl run executes
    - Then InlineSubmitter.add is called 0 times (dedup at platform level handles this)
  - **TC-032**: Handles empty vendor org gracefully
    - Given an org with 0 public repos
    - When crawl processes that org
    - Then orgBreakdown shows 0 skills and no errors

**Dependencies**: T-001, T-002
