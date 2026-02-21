# Tasks: Populate Skill Popularity Metrics from APIs

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started
- `[x]`: Completed
- Model hints: haiku (simple), opus (default)

## Phase 1: Core Fetcher

### T-001: Add npmPackage to SkillData type and Prisma schema
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03 | **Status**: [x] completed
**Test**: Given SkillData type -> When inspected -> Then npmPackage is optional string field

**Implementation Details**:
- Add `npmPackage?: string` to `SkillData` interface in `src/lib/types.ts`
- Add `npmPackage String?` to `Skill` model in `prisma/schema.prisma`
- Update seed data: add `npmPackage` to at least 5 skills with realistic package names (e.g., Anthropic skills could use `@anthropic/skill-name`)

**Test Plan**:
- **File**: `src/lib/__tests__/types.test.ts` (type-level check, compile-time)
- **TC-001**: Seed data skills with npmPackage can be assigned to SkillData
  - Given a skill object with npmPackage set
  - When assigned to SkillData typed variable
  - Then TypeScript compiles without error

**Dependencies**: None

---

### T-002: Implement fetchGitHubMetrics with TTL cache [P]
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-03, AC-US1-04, AC-US1-05 | **Status**: [x] completed
**Test**: Given a valid GitHub repo URL -> When fetchGitHubMetrics is called -> Then returns { stars, forks, lastCommitAt }

**Implementation Details**:
- Create `src/lib/popularity-fetcher.ts`
- `parseGitHubUrl(url: string): { owner: string; repo: string } | null` -- handle `github.com`, `www.github.com`, trailing `/`, `.git` suffix
- `fetchGitHubMetrics(repoUrl: string): Promise<{ stars: number; forks: number; lastCommitAt: string | null } | null>`
- TTL cache with `Map<string, { data; ts }>`, default 3600s, configurable via `METRICS_CACHE_TTL_SECONDS`
- Include `Accept: application/vnd.github.v3+json` header
- Include `Authorization: Bearer ${GITHUB_TOKEN}` if env var is set
- 5-second timeout via `AbortController`
- Return `null` on any error (network, 404, 403, rate limit, timeout)

**Test Plan**:
- **File**: `src/lib/__tests__/popularity-fetcher.test.ts`
- **Tests**:
  - **TC-002**: Parses standard GitHub URLs correctly
    - Given `https://github.com/anthropics/skills`
    - When parseGitHubUrl is called
    - Then returns `{ owner: "anthropics", repo: "skills" }`
  - **TC-003**: Parses URLs with .git suffix
    - Given `https://github.com/user/repo.git`
    - When parseGitHubUrl is called
    - Then returns `{ owner: "user", repo: "repo" }`
  - **TC-004**: Returns null for non-GitHub URLs
    - Given `https://gitlab.com/user/repo`
    - When parseGitHubUrl is called
    - Then returns null
  - **TC-005**: Returns null for malformed URLs
    - Given `not-a-url`
    - When parseGitHubUrl is called
    - Then returns null
  - **TC-006**: Fetches stars, forks, lastCommitAt from GitHub API
    - Given a mocked fetch returning `{ stargazers_count: 100, forks_count: 20, pushed_at: "2026-01-01T00:00:00Z" }`
    - When fetchGitHubMetrics is called
    - Then returns `{ stars: 100, forks: 20, lastCommitAt: "2026-01-01T00:00:00Z" }`
  - **TC-007**: Returns null on 404 response
    - Given a mocked fetch returning 404
    - When fetchGitHubMetrics is called
    - Then returns null
  - **TC-008**: Returns null on network error
    - Given a mocked fetch that throws
    - When fetchGitHubMetrics is called
    - Then returns null
  - **TC-009**: Returns cached result on subsequent call within TTL
    - Given a successful first call
    - When called again within TTL
    - Then returns cached data without calling fetch again
  - **TC-010**: Includes Authorization header when GITHUB_TOKEN is set
    - Given GITHUB_TOKEN env var is set
    - When fetchGitHubMetrics is called
    - Then fetch is called with Authorization header

**Dependencies**: None

---

### T-003: Implement fetchNpmDownloads with TTL cache [P]
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-03, AC-US1-05 | **Status**: [x] completed
**Test**: Given a valid npm package name -> When fetchNpmDownloads is called -> Then returns monthly download count

**Implementation Details**:
- Add to `src/lib/popularity-fetcher.ts`
- `fetchNpmDownloads(packageName: string): Promise<number>`
- Call `GET https://api.npmjs.org/downloads/point/last-month/{packageName}`
- Return `downloads` field value, or `0` on any error
- Share the same TTL cache infrastructure as GitHub metrics
- 5-second timeout

**Test Plan**:
- **File**: `src/lib/__tests__/popularity-fetcher.test.ts`
- **Tests**:
  - **TC-011**: Returns download count from npm API
    - Given a mocked fetch returning `{ downloads: 5000 }`
    - When fetchNpmDownloads is called with "@anthropic/skills"
    - Then returns 5000
  - **TC-012**: Returns 0 on 404
    - Given a mocked fetch returning 404
    - When fetchNpmDownloads is called
    - Then returns 0
  - **TC-013**: Returns 0 on network error
    - Given a mocked fetch that throws
    - When fetchNpmDownloads is called
    - Then returns 0
  - **TC-014**: Returns cached result within TTL
    - Given a successful first call
    - When called again within TTL
    - Then returns cached data without fetching again

**Dependencies**: None

---

## Phase 2: Data Layer Integration

### T-004: Implement enrichSkillWithMetrics and wire into data layer
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04 | **Status**: [x] completed
**Test**: Given ENABLE_LIVE_METRICS=true -> When getSkillByName is called -> Then returned skill has enriched metrics

**Implementation Details**:
- Add `enrichSkillWithMetrics(skill: SkillData): Promise<SkillData>` to `popularity-fetcher.ts`
  - Calls `fetchGitHubMetrics(skill.repoUrl)` and `fetchNpmDownloads(skill.npmPackage)` in parallel
  - Merges non-null results: only overwrite `githubStars`/`githubForks`/`lastCommitAt`/`npmDownloads` if fetched value is > 0
  - Preserves existing values if fetcher returns null/0 (AC-US3-03)
- In `src/lib/data.ts`:
  - Import `enrichSkillWithMetrics`
  - In `getSkillByName()`: after finding skill, if `ENABLE_LIVE_METRICS` is truthy, call enrichment
  - In `getSkills()`: if `ENABLE_LIVE_METRICS` is truthy, enrich each skill (using Promise.all for parallelism, but only for first page to avoid API blast)
- Feature flag: `process.env.ENABLE_LIVE_METRICS === "true"`

**Test Plan**:
- **File**: `src/lib/__tests__/popularity-fetcher.test.ts`
- **Tests**:
  - **TC-015**: enrichSkillWithMetrics merges GitHub metrics
    - Given a skill with githubStars: 0 and a mocked fetcher returning stars: 500
    - When enrichSkillWithMetrics is called
    - Then returned skill has githubStars: 500
  - **TC-016**: enrichSkillWithMetrics preserves existing values when fetcher returns null
    - Given a skill with githubStars: 100 and a mocked fetcher returning null
    - When enrichSkillWithMetrics is called
    - Then returned skill still has githubStars: 100
  - **TC-017**: enrichSkillWithMetrics fetches npm downloads when npmPackage is set
    - Given a skill with npmPackage: "@test/pkg" and a mocked npm fetcher returning 8000
    - When enrichSkillWithMetrics is called
    - Then returned skill has npmDownloads: 8000
  - **TC-018**: enrichSkillWithMetrics skips npm fetch when npmPackage is undefined
    - Given a skill without npmPackage
    - When enrichSkillWithMetrics is called
    - Then fetchNpmDownloads is not called

- **File**: `src/lib/__tests__/data.test.ts` (add to existing)
- **Tests**:
  - **TC-019**: getSkillByName enriches when ENABLE_LIVE_METRICS is set
    - Given ENABLE_LIVE_METRICS=true and mocked enrichment
    - When getSkillByName is called
    - Then enrichment function is called on the result
  - **TC-020**: getSkillByName does NOT enrich when ENABLE_LIVE_METRICS is unset
    - Given ENABLE_LIVE_METRICS is undefined
    - When getSkillByName is called
    - Then enrichment function is NOT called

**Dependencies**: T-001, T-002, T-003

---

### T-005: Update seed data with npmPackage values
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03 | **Status**: [x] completed
**Test**: Given seed data -> When loaded -> Then at least 5 skills have npmPackage set

**Implementation Details**:
- Edit `src/lib/seed-data.ts`
- Add `npmPackage` to skills that have real or plausible npm packages:
  - `specweave` -> `specweave`
  - `vitest-skill` -> `vitest`
  - Skills from anthropics -> `@anthropic/skill-name` (plausible)
- Only set npmPackage where it makes sense (not all skills have npm packages)

**Test Plan**:
- **File**: `src/lib/__tests__/popularity-fetcher.test.ts`
- **TC-021**: At least 5 seed skills have npmPackage set
  - Given seed data is imported
  - When filtering skills with npmPackage defined
  - Then count >= 5

**Dependencies**: T-001

---

## Phase 3: UI Updates

### T-006: Hide zero-value metrics on skill detail page
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02 | **Status**: [x] completed
**Test**: Given a skill with githubStars=0 -> When detail page renders -> Then Stars card is not shown

**Implementation Details**:
- Edit `src/app/skills/[name]/page.tsx`
- Wrap Stars StatCard in `{skill.githubStars > 0 && ...}` (currently always shown)
- Wrap Forks StatCard in `{skill.githubForks > 0 && ...}` (currently always shown)
- NPM StatCard already has `{skill.npmDownloads > 0 && ...}` -- no change needed

**Test Plan**:
- Visual verification (server component, hard to unit test)
- **TC-022**: Stars card rendered when githubStars > 0 (manual/visual)
- **TC-023**: Stars card NOT rendered when githubStars === 0 (manual/visual)
- **TC-024**: Forks card NOT rendered when githubForks === 0 (manual/visual)

**Dependencies**: None (can be done in parallel with Phase 1-2)

---

### T-007: Adjust homepage dashboard aggregation to exclude zero metrics
**User Story**: US-004 | **Satisfies ACs**: AC-US4-04, AC-US4-05 | **Status**: [x] completed
**Test**: Given skills with mixed zero/non-zero stars -> When homepage loads -> Then total stars only counts non-zero skills

**Implementation Details**:
- Edit `src/app/page.tsx`
- `totalStars` aggregation: already `reduce` over all skills -- keep as-is (zeros don't inflate since seed data has non-zero values)
- `topByStars` / `topByInstalls` / `topByNpm`: filter to skills with value > 0 before sorting
- This prevents zero-metric skills from appearing in "top" lists

**Test Plan**:
- **TC-025**: Top-by-stars list does not include skills with 0 stars (manual/visual)
- **TC-026**: Trending rows continue to display correctly with seed data

**Dependencies**: None (can be done in parallel)

---

## Phase 4: vskill CLI UX

### T-009: Add install hint footer to `vskill find` output [P]
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04 | **Status**: [x] completed
**Test**: Given `vskill find` runs in non-TTY mode -> When results render -> Then a hint line is appended

**Implementation Details**:
- Locate the find/search command output renderer in `repositories/anton-abyzov/vskill/src/`
- After printing the results table, detect TTY: `process.stdout.isTTY`
- Non-TTY: append `\nTo install: npx skills add <name>` (using first result name as example)
- TTY/interactive: append `\n↑↓ navigate  i install  q quit` footer
- Wire `i` keypress in interactive mode to invoke the add command for the highlighted row
- Skip hint when `--json` flag is active or `--no-hint` is passed

**Test Plan**:
- **File**: `src/__tests__/find-command.test.ts` (vskill CLI)
- **TC-030**: Non-TTY output includes hint line
  - Given stdout is not a TTY
  - When find renders results
  - Then output contains `To install: npx skills add`
- **TC-031**: Hint is suppressed with `--json` flag
  - Given `--json` flag is passed
  - When find renders results
  - Then output does NOT contain hint line
- **TC-032**: Interactive footer contains expected key bindings
  - Given stdout is a TTY
  - When find renders results
  - Then footer contains `i install` and `q quit`

**Dependencies**: None

---

### T-010: Implement skills.sh URL resolver in `vskill add` [P]
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01, AC-US6-02, AC-US6-03, AC-US6-04, AC-US6-05 | **Status**: [x] completed
**Test**: Given `vskill add https://skills.sh/owner/toolkit/skill` -> When add runs -> Then skill is resolved without /.well-known/ probe

**Implementation Details**:
- Create or extend `src/resolvers/url-resolver.ts` in vskill CLI
- `parseSkillsShUrl(input: string): { owner: string; toolkit: string; skill: string } | null`
  - Match `https://skills.sh/{owner}/{toolkit}/{skill}` — exactly 3 path segments required
  - Return null for non-skills.sh URLs (let caller fall through to generic probe)
- In the add command entrypoint: if input is a URL, run through resolver chain before generic probe
- If `parseSkillsShUrl` returns a result, pass structured data directly to install logic
- If incomplete path (1-2 segments), throw descriptive error: `Incomplete skills.sh URL — expected /owner/toolkit/skill`
- Print `Resolving skills.sh URL...` before any network call when input is a URL
- Update the generic `/.well-known/` error message to: `Could not resolve skill at this URL`

**Test Plan**:
- **File**: `src/__tests__/url-resolver.test.ts` (vskill CLI)
- **TC-033**: Parses full skills.sh URL correctly
  - Given `https://skills.sh/softaworks/agent-toolkit/humanizer`
  - When parseSkillsShUrl is called
  - Then returns `{ owner: "softaworks", toolkit: "agent-toolkit", skill: "humanizer" }`
- **TC-034**: Returns null for non-skills.sh URL
  - Given `https://github.com/user/repo`
  - When parseSkillsShUrl is called
  - Then returns null
- **TC-035**: Incomplete path throws descriptive error
  - Given `https://skills.sh/softaworks/agent-toolkit` (missing skill segment)
  - When add command processes this URL
  - Then error message contains `Incomplete skills.sh URL`
- **TC-036**: Generic fallback error message does not mention `/.well-known/skills/index.json`
  - Given an unknown domain URL that fails probe
  - When add command runs
  - Then error message is `Could not resolve skill at this URL`
- **TC-037**: Resolving message is printed before network call
  - Given a skills.sh URL input
  - When add command runs
  - Then `Resolving...` is printed before fetch is called

**Dependencies**: None

---

## Phase 5: Skills.sh Compatibility

### T-011: Research — Reverse-engineer skills.sh install flow and gap analysis [RESEARCH]
**User Story**: US-007 | **Satisfies ACs**: AC-US7-01 | **Status**: [x] completed
**Test**: Given research is complete -> When report is reviewed -> Then all compatibility gaps are documented with actionable recommendations

**Implementation Details**:
- **Deliverable**: Gap analysis report + draft implementation plan
- **Output**: `.specweave/increments/0293-skill-popularity-metrics/reports/skills-sh-compat-analysis.md`
- **Research scope**:
  1. **Agent detection comparison**: vskill uses `which <binary>` (39 agents); skills.sh uses `existsSync(~/.agent-dir/)` (50+ agents) — which is more reliable? Document all agents missing from vskill
  2. **Folder structure comparison**: Both use `.agents/skills/{name}/` canonical dir — verify symlink target paths are identical
  3. **Critical path discrepancy**: vskill uses `.claude/commands/` for Claude Code; skills.sh uses `.claude/skills/` — document migration strategy
  4. **Lock file interop**: Can vskill read `.skill-lock.json`? Should it dual-read for cross-tool visibility in `vskill list`?
  5. **Cross-tool visibility test**: Install via `npx skills add`, check `vskill list` — document what's visible/invisible and why
  6. **Reverse visibility test**: Install via `vskill add`, check `npx skills list` — same
  7. **Document all 50+ agents** from skills.sh `src/agents.ts` and diff against vskill's `src/agents/agents-registry.ts`
- **Draft implementation plan**: For each gap, propose specific code changes with file paths and function signatures

**Test Plan**:
- **TC-040**: Report exists and contains all 7 research sections
- **TC-041**: Report includes agent diff table (skills.sh agents vs vskill agents)
- **TC-042**: Report includes draft implementation plan with file paths

**Dependencies**: None (can start immediately)

---

### T-012: Implement compatibility fixes from T-011 findings
**User Story**: US-007 | **Satisfies ACs**: AC-US7-02, AC-US7-03, AC-US7-04, AC-US7-05 | **Status**: [x] completed
**Test**: Given skills installed by `npx skills` -> When `vskill list` runs -> Then those skills are visible

**Implementation Details** (preliminary, refined by T-011 draft plan):
- **Switch Claude Code path**: Change `localSkillsDir` from `.claude/commands` to `.claude/skills` in `src/agents/agents-registry.ts`
- **Add missing agents**: Add 11+ agents that skills.sh has but vskill doesn't (exact list from T-011 report)
- **Cross-tool visibility**: In `vskill list`, also scan `.skill-lock.json` (skills.sh lock file) for installed skills not in `vskill.lock`
- **Symlink path alignment**: Ensure relative symlink targets match skills.sh format exactly
- **Detection method**: Consider switching from `which` to `existsSync` for agents where binary detection is unreliable (per T-011 findings)

**Test Plan**:
- **File**: `src/__tests__/agents-registry.test.ts` (vskill CLI)
- **TC-043**: Claude Code agent uses `.claude/skills/` as localSkillsDir
  - Given agents registry
  - When claude-code agent is looked up
  - Then localSkillsDir is `.claude/skills`
- **TC-044**: Agent count >= 50
  - Given agents registry
  - When counting all agents
  - Then count >= 50
- **TC-045**: vskill list shows skills from `.skill-lock.json`
  - Given a `.skill-lock.json` with a skill entry
  - When `vskill list` runs
  - Then that skill appears in output
- **TC-046**: Skills installed by vskill are in `.agents/skills/` canonical dir
  - Given a skill installed by vskill add
  - When checking filesystem
  - Then `.agents/skills/{name}/SKILL.md` exists

**Dependencies**: T-011

---

## Phase 6: Verification

### T-008: End-to-end verification and test suite run
**User Story**: All | **Satisfies ACs**: All | **Status**: [x] completed
**Test**: Given all changes -> When full test suite runs -> Then all tests pass

**Implementation Details**:
- Run `npx vitest run` in vskill-platform
- Run `npx next build` to verify no build errors
- Verify TypeScript compiles cleanly with `npx tsc --noEmit`
- Manual check: set `ENABLE_LIVE_METRICS=true` and verify a skill page shows real GitHub metrics (local dev)
- Run vskill CLI test suite: `npm test` in `repositories/anton-abyzov/vskill/`
- Manual check: `vskill find human` shows install hint; `vskill add https://skills.sh/softaworks/agent-toolkit/humanizer` resolves without error

**Test Plan**:
- **TC-027**: All existing tests pass
- **TC-028**: New tests pass with >80% coverage on new files
- **TC-029**: Build succeeds
- **TC-038**: vskill CLI tests for T-009 and T-010 all pass
- **TC-039**: Manual end-to-end: skills.sh URL install resolves correctly
- **TC-047**: Cross-tool: skill installed by `npx skills` visible in `vskill list`
- **TC-048**: Cross-tool: skill installed by `vskill add` visible in `npx skills list`

**Dependencies**: T-001 through T-012
