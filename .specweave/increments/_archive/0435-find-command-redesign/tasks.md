---
increment: 0435-find-command-redesign
title: "Redesign vskill find command with install counts"
generated_by: sw:test-aware-planner
by_user_story:
  US-VPL-002:
    tasks: [T-001, T-002, T-003]
    acs: [AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04]
  US-VSK-001:
    tasks: [T-004, T-005, T-006, T-007]
    acs: [AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05]
total_tasks: 7
completed_tasks: 7
---

# Tasks: Redesign vskill find command with install counts

## User Story: US-VPL-002 - Install counts in search API response

**Project**: vskill-platform
**Linked ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04
**Tasks**: 3 total, 3 completed

---

### T-001: Extend SearchIndexEntry and SearchResult types with vskillInstalls

**User Story**: US-VPL-002
**Satisfies ACs**: AC-US2-03, AC-US2-04
**Status**: [x] completed

**Test Plan**:
- **Given** the `SearchIndexEntry` type in `src/lib/search-index.ts`
- **When** the type is updated and `INDEX_VERSION` is bumped from 4 to 5
- **Then** `SearchIndexEntry` includes a `vskillInstalls: number` field and `INDEX_VERSION === 5`

- **Given** the `SearchResult` type in `src/lib/search.ts`
- **When** the type is updated
- **Then** `SearchResult` includes a `vskillInstalls: number` field with default 0 for backward compatibility

- **Given** the `SearchShardQueueMessage.entry` type in `src/lib/queue/types.ts`
- **When** updated
- **Then** it includes `vskillInstalls?: number` to mirror `SearchIndexEntry`

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill-platform/src/lib/search-index.test.ts`
   - `INDEX_VERSION should be 5`: Assert exported constant equals 5
   - `SearchIndexEntry should include vskillInstalls`: Type-level check via compiled build
   - **Coverage Target**: 90%

2. **Unit**: `repositories/anton-abyzov/vskill-platform/src/lib/search.test.ts`
   - `SearchResult should include vskillInstalls field`: Assert field presence and default 0
   - **Coverage Target**: 90%

**Implementation**:
1. In `repositories/anton-abyzov/vskill-platform/src/lib/search-index.ts`:
   - Add `vskillInstalls: number` to `SearchIndexEntry` interface
   - Change `export const INDEX_VERSION = 4` to `export const INDEX_VERSION = 5`
2. In `repositories/anton-abyzov/vskill-platform/src/lib/search.ts`:
   - Add `vskillInstalls: number` to `SearchResult` type
   - Add `vskillInstalls: number` to `SkillSearchRow` type
3. In `repositories/anton-abyzov/vskill-platform/src/lib/queue/types.ts`:
   - Add `vskillInstalls?: number` to `SearchShardQueueMessage.entry`
4. Run `npx vitest run` in vskill-platform to confirm no type errors

---

### T-002: Propagate vskillInstalls through buildSearchIndex and edge search path

**User Story**: US-VPL-002
**Satisfies ACs**: AC-US2-01, AC-US2-03
**Status**: [x] completed

**Test Plan**:
- **Given** `buildSearchIndex()` in `src/lib/search-index.ts`
- **When** it runs against a mocked Prisma result that includes `vskillInstalls`
- **Then** each shard entry written to KV contains `vskillInstalls` matching the DB value

- **Given** `searchSkillsEdge()` in `src/lib/search.ts` receives a KV entry with `vskillInstalls: 1200`
- **When** it maps the entry to a `SearchResult`
- **Then** the result has `vskillInstalls: 1200`

- **Given** a KV entry missing `vskillInstalls` (old shard format)
- **When** `searchSkillsEdge()` maps it
- **Then** `vskillInstalls` defaults to `0`

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill-platform/src/lib/search-index.test.ts`
   - `buildSearchIndex should include vskillInstalls in shard entries`: Mock Prisma `findMany` returning `[{ vskillInstalls: 500, ... }]`, assert KV write contains `vskillInstalls: 500`
   - **Coverage Target**: 90%

2. **Unit**: `repositories/anton-abyzov/vskill-platform/src/lib/search.test.ts`
   - `searchSkillsEdge should map vskillInstalls from KV entry`: Mock KV shard returning entry with `vskillInstalls: 1200`, assert result has `vskillInstalls: 1200`
   - `searchSkillsEdge should default vskillInstalls to 0 when absent`: Mock entry without field, assert result has `vskillInstalls: 0`
   - **Coverage Target**: 90%

**Implementation**:
1. In `buildSearchIndex()`, add `vskillInstalls: true` to the Prisma `select` clause
2. In the shard entry construction (both name-shard and author-shard loops), add `vskillInstalls: skill.vskillInstalls ?? 0`
3. In `searchSkillsEdge()` `resultSlice.map()`, add `vskillInstalls: entry.vskillInstalls ?? 0`
4. Audit `processSubmission` in `submission-store.ts` to confirm `vskillInstalls` is included in `SearchShardQueueMessage.entry` construction
5. Run `npx vitest run` in vskill-platform

---

### T-003: Add vskillInstalls to Postgres search paths and blocklist

**User Story**: US-VPL-002
**Satisfies ACs**: AC-US2-02
**Status**: [x] completed

**Test Plan**:
- **Given** a search query handled by `searchSkills()` (Postgres path)
- **When** the tsvector SQL query runs and maps results
- **Then** each `SearchResult` includes `vskillInstalls` read from the `Skill` table

- **Given** a search query falling back to the ILIKE path in `searchSkills()`
- **When** results are mapped
- **Then** each result includes `vskillInstalls` with default 0 for null values

- **Given** `searchBlocklistEntries()` returning blocked results
- **When** results are mapped to `SearchResult`
- **Then** each blocked result has `vskillInstalls: 0` for type consistency

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill-platform/src/lib/search.test.ts`
   - `searchSkills Postgres path should include vskillInstalls`: Mock `$queryRaw` returning rows with `vskillInstalls: 42`, assert result has `vskillInstalls: 42`
   - `searchSkills ILIKE fallback should include vskillInstalls`: Assert same behavior for ILIKE path
   - `searchBlocklistEntries should return vskillInstalls 0`: Assert blocked results have `vskillInstalls: 0`
   - Update existing `should NOT include excluded fields` assertion to expect `vskillInstalls` as an included field
   - **Coverage Target**: 90%

**Implementation**:
1. In `searchSkills()` tsvector SQL query SELECT list, add `"vskillInstalls"`
2. In `searchSkills()` ILIKE fallback SQL query SELECT list, add `"vskillInstalls"`
3. In `resultRows.map()` block, add `vskillInstalls: row.vskillInstalls ?? 0`
4. In `searchBlocklistEntries()` return mapping, add `vskillInstalls: 0`
5. Run `npx vitest run` in vskill-platform; confirm all search tests pass
6. Run TypeScript build `npx tsc --noEmit` to confirm no type errors

---

## User Story: US-VSK-001 - Flat install-sorted search results

**Project**: vskill
**Linked ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05
**Tasks**: 4 total, 0 completed

---

### T-004: Add formatInstalls utility and update SkillSearchResult type

**User Story**: US-VSK-001
**Satisfies ACs**: AC-US1-05
**Status**: [x] completed

**Test Plan**:
- **Given** `formatInstalls(0)` is called
- **When** the function runs
- **Then** it returns `"0"`

- **Given** `formatInstalls(1200)` is called
- **When** the function runs
- **Then** it returns `"1.2K"`

- **Given** `formatInstalls(1000)` is called
- **When** the function runs
- **Then** it returns `"1K"` (no trailing decimal)

- **Given** `formatInstalls(3400000)` is called
- **When** the function runs
- **Then** it returns `"3.4M"`

- **Given** `searchSkills()` in `client.ts` receives an API response with `vskillInstalls: 500`
- **When** results are mapped
- **Then** `SkillSearchResult.vskillInstalls === 500`

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill/src/utils/output.test.ts`
   - `formatInstalls(0) should return "0"`: Assert exact string
   - `formatInstalls(999) should return "999"`: Assert exact string
   - `formatInstalls(1000) should return "1K"`: Assert no ".0" suffix
   - `formatInstalls(1200) should return "1.2K"`: Assert decimal present
   - `formatInstalls(1000000) should return "1M"`: Assert no ".0" suffix
   - `formatInstalls(3400000) should return "3.4M"`: Assert decimal present
   - **Coverage Target**: 95%

2. **Unit**: `repositories/anton-abyzov/vskill/src/api/client.test.ts`
   - `searchSkills should map vskillInstalls from API response`: Mock API returning `vskillInstalls: 500`, assert result field equals 500
   - `searchSkills should handle missing vskillInstalls as undefined`: Mock API omitting field, assert result field is undefined
   - **Coverage Target**: 90%

**Implementation**:
1. In `repositories/anton-abyzov/vskill/src/utils/output.ts`, add exported `formatInstalls(count: number): string` function per plan spec
2. In `repositories/anton-abyzov/vskill/src/api/client.ts`:
   - Add `vskillInstalls?: number` to `SkillSearchResult` interface
   - In `searchSkills()` response mapping, add `vskillInstalls: s.vskillInstalls != null ? Number(s.vskillInstalls) : undefined`
3. Run `npx vitest run` in vskill repo

---

### T-005: Change default limit from 50 to 15

**User Story**: US-VSK-001
**Satisfies ACs**: AC-US1-03
**Status**: [x] completed

**Test Plan**:
- **Given** a user runs `vskill find typescript` without `--limit`
- **When** `searchSkills()` in `client.ts` is called
- **Then** the API request is sent with `limit=15`

- **Given** the `--limit` option description in `src/index.ts`
- **When** user runs `vskill find --help`
- **Then** the help text shows "default 15"

- **Given** the API returns `hasMore: true`
- **When** results are rendered
- **Then** the footer shows `Use --limit N for more`

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill/src/commands/find.test.ts`
   - `find command should use default limit of 15`: Mock client, assert `searchSkills` called with `limit: 15`
   - `find command should show hasMore hint when hasMore is true`: Mock response with `hasMore: true`, assert output contains `Use --limit N for more`
   - `find command should not show hasMore hint when hasMore is false`: Mock response with `hasMore: false`, assert hint absent
   - **Coverage Target**: 90%

**Implementation**:
1. In `repositories/anton-abyzov/vskill/src/api/client.ts`, change `const limit = options?.limit ?? 50` to `const limit = options?.limit ?? 15`
2. In `repositories/anton-abyzov/vskill/src/index.ts`, update `--limit` option description to `"Max results to return (default 15)"`
3. In `repositories/anton-abyzov/vskill/src/commands/find.ts`, add footer logic: when `hasMore` is true, append `Use --limit N for more` line
4. Run `npx vitest run` in vskill repo

---

### T-006: Rewrite findCommand TTY output to flat install-sorted list

**User Story**: US-VSK-001
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-04
**Status**: [x] completed

**Test Plan**:
- **Given** two results with `vskillInstalls: 100` and `vskillInstalls: 500`
- **When** `findCommand()` renders TTY output
- **Then** the result with 500 installs appears first (sorted by installs DESC)

- **Given** two results with equal `vskillInstalls` values
- **When** `findCommand()` sorts them
- **Then** the result with higher relevance score appears first (tiebreaker)

- **Given** a TTY terminal and a result with `repoUrl: "https://github.com/owner/repo"` and `name: "my-skill"`
- **When** the result is rendered
- **Then** the first line shows `owner/repo@my-skill  1.2K installs` and the second line shows `  https://github.com/owner/repo` as a clickable OSC 8 link

- **Given** a blocked result with `isBlocked: true`, `severity: "critical"`, `threatType: "credential-theft"`
- **When** rendered in TTY output
- **Then** it shows `owner/repo@skill  BLOCKED  critical | credential-theft` instead of install count

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill/src/commands/find.test.ts`
   - `findCommand should sort results by vskillInstalls descending`: Provide unsorted mock results, assert output order
   - `findCommand should use relevance score as tiebreaker for equal installs`: Two results same installs, higher score first
   - `findCommand should render owner/repo@skill-name format`: Assert formatted name in output
   - `findCommand should render install count in human format`: Assert "1.2K installs" in output for 1200 installs
   - `findCommand TTY should render clickable URL on second line`: Assert URL line present with OSC 8 escape if TTY
   - `findCommand should render blocked threat info instead of installs`: Assert "BLOCKED  critical | credential-theft" for blocked results
   - `findCommand should remove marketplace grouping headers`: Assert "Plugin Marketplace:" absent from output
   - **Coverage Target**: 90%

**Implementation**:
1. In `repositories/anton-abyzov/vskill/src/commands/find.ts`:
   - Remove `extractBaseRepo()`, `buildRow()`, `formatRepo()` functions and marketplace grouping logic
   - Remove `table()` import if no longer used in find.ts
   - Add `formatSkillId(repoUrl, name)` helper per plan spec
   - Sort: non-blocked results by `vskillInstalls` DESC then score DESC, blocked results appended last
   - Implement two-line TTY render: line 1 = bold `owner/repo@skill-name  X installs`, line 2 = `  URL` with OSC 8 link
   - For blocked results: line 1 = `owner/repo@skill-name  BLOCKED  severity | threatType`
2. Run `npx vitest run` in vskill repo; run `npx tsc --noEmit`

---

### T-007: Implement non-TTY tab-separated output and JSON vskillInstalls

**User Story**: US-VSK-001
**Satisfies ACs**: AC-US1-05
**Status**: [x] completed

**Test Plan**:
- **Given** stdout is not a TTY (piped output)
- **When** `findCommand()` renders results
- **Then** each line is tab-separated `name\trepo\tinstalls` with no ANSI codes and no table headers

- **Given** `--json` flag is passed
- **When** results are rendered
- **Then** JSON output includes a `vskillInstalls` field for each result

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill/src/commands/find.test.ts`
   - `findCommand non-TTY should output tab-separated lines`: Mock `process.stdout.isTTY = false`, assert output format `name\trepo\tinstalls`
   - `findCommand non-TTY should not include ANSI escape codes`: Assert no `\x1b[` in non-TTY output
   - `findCommand --json should include vskillInstalls field`: Mock results with `vskillInstalls: 42`, assert JSON output has `vskillInstalls: 42`
   - `findCommand --json should default vskillInstalls to 0 when undefined`: Assert field defaults to 0 in JSON
   - **Coverage Target**: 90%

**Implementation**:
1. In `repositories/anton-abyzov/vskill/src/commands/find.ts`:
   - For non-TTY path: output tab-separated lines `${result.name}\t${repoSlug}\t${result.vskillInstalls ?? 0}` with no ANSI
   - For `--json` path: ensure `vskillInstalls` is included in each serialized result object (defaults to 0 if undefined)
2. Run full test suite: `npx vitest run` in vskill repo
3. Run `npx tsc --noEmit` in vskill repo to confirm no type errors
