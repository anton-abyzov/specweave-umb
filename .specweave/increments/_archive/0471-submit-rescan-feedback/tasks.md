---
increment: 0471-submit-rescan-feedback
generated_by: sw:test-aware-planner
by_user_story:
  US-001: [T-001, T-002, T-003, T-004]
---

# Tasks: Submit page rescan feedback

## User Story: US-001 - Rescan-aware submission feedback

**Linked ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04
**Tasks**: 4 total, 4 completed

---

### T-001: Extend DiscoveredSkill interface to include status field

**User Story**: US-001
**Satisfies ACs**: AC-US1-01
**Status**: [x] completed

**Test Plan**:
- **Given** the discover endpoint returns skills with a `status` field (`"new"`, `"verified"`, `"pending"`, `"rejected"`)
- **When** `handleDiscover` maps `data.skills` into `DiscoveredSkill[]`
- **Then** each item preserves its `status` value (not dropped as before)

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill-platform/src/app/submit/page.test.tsx`
   - `discoveredSkillPreservesVerifiedStatus()`: mock discover API returning `status: "verified"`, assert resulting state has `status: "verified"` on the skill
   - `discoveredSkillPreservesNewStatus()`: same for `status: "new"`
   - `discoveredSkillUndefinedStatusWhenMissing()`: API response with no `status` field results in `status: undefined`
   - **Coverage Target**: 90%

**Implementation**:
1. Add `status?: "new" | "verified" | "pending" | "rejected"` to `DiscoveredSkill` interface in `page.tsx`
2. In `handleDiscover`, change the mapping to explicitly carry the status: `{ name: s.name, path: s.path, status: s.status }` instead of the current bare `data.skills ?? []` spread

---

### T-002: Thread discoveryStatus through SubmissionResult

**User Story**: US-001
**Satisfies ACs**: AC-US1-03
**Status**: [x] completed

**Test Plan**:
- **Given** discovered skills with a known `status` (e.g., `"verified"`)
- **When** `handleSubmitAll` processes the batch API response and builds `outcomes`
- **Then** each `SubmissionResult` carries the originating skill's `discoveryStatus`

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill-platform/src/app/submit/page.test.tsx`
   - `submissionResultCarriesVerifiedDiscoveryStatus()`: skill with `status: "verified"` results in outcome with `discoveryStatus: "verified"`
   - `submissionResultCarriesUndefinedWhenStatusMissing()`: skill with no `status` results in `discoveryStatus: undefined`
   - `skippedOutcomeCarriesDiscoveryStatus()`: skipped skill still gets `discoveryStatus` threaded through
   - **Coverage Target**: 90%

**Implementation**:
1. Add `discoveryStatus?: "new" | "verified" | "pending" | "rejected"` to `SubmissionResult` interface
2. In `handleSubmitAll`, update each `outcomes.push(...)` call to include `discoveryStatus: skill.status`:
   - Successful: `{ name: skill.name, id: sub.id, discoveryStatus: skill.status }`
   - Skipped: `{ name: skill.name, status: skip.reason === "verified" ? "already-verified" : "skipped", discoveryStatus: skill.status }`
   - Fallback: `{ name: skill.name, status: "skipped", discoveryStatus: skill.status }`
3. Also carry `discoveryStatus: s.status` in the error and non-ok response paths

---

### T-003: Rescan-aware summary line

**User Story**: US-001
**Satisfies ACs**: AC-US1-02, AC-US1-04
**Status**: [x] completed

**Test Plan**:
- **Given** a results array with a known mix of `id`-bearing outcomes and their `discoveryStatus`
- **When** the summary line is computed
- **Then** it reads "N submitted" (all new/undefined), "M rescanning" (all verified), or "N new, M rescanning" (mixed)

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill-platform/src/app/submit/page.test.tsx`
   - `summaryAllNew()`: 3 results with `id` and `discoveryStatus: "new"` renders "3 submitted"
   - `summaryAllRescan()`: 2 results with `id` and `discoveryStatus: "verified"` renders "2 rescanning"
   - `summaryMixed()`: 2 new + 1 verified renders "2 new, 1 rescanning"
   - `summaryRejectedCountsAsNew()`: `discoveryStatus: "rejected"` is counted as new (AC-US1-04)
   - `summaryUndefinedCountsAsNew()`: `discoveryStatus: undefined` is counted as new (backward compat)
   - **Coverage Target**: 95%

**Implementation**:
1. Replace the `okCount` derivation with two separate counts:
   - `rescanCount = results.filter((r) => r.id && r.discoveryStatus === "verified").length`
   - `newCount = results.filter((r) => r.id && r.discoveryStatus !== "verified").length`
2. Build the summary label:
   - `newCount === 0` only: `"{rescanCount} rescanning"`
   - `rescanCount === 0` only: `"{newCount} submitted"` (existing behavior)
   - Mixed: `"{newCount} new, {rescanCount} rescanning"`
3. Replace `{okCount} submitted` in JSX with the new `{submittedLabel}`
4. Keep `skippedCount` and `failCount` suffix logic unchanged
5. Derive `okCount = newCount + rescanCount` for the "View Queue" button guard

---

### T-004: Show "Rescan >>" link label for verified skill results

**User Story**: US-001
**Satisfies ACs**: AC-US1-03
**Status**: [x] completed

**Test Plan**:
- **Given** a result row where `r.id` is set
- **When** `r.discoveryStatus === "verified"`
- **Then** the link reads "Rescan >>" instead of "Track >>"; both link to `/submit/{id}`

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill-platform/src/app/submit/page.test.tsx`
   - `trackLinkShownForNewSkill()`: result with `id` and `discoveryStatus: "new"` renders link text "Track >>"
   - `rescanLinkShownForVerifiedSkill()`: result with `id` and `discoveryStatus: "verified"` renders link text "Rescan >>"
   - `trackLinkShownWhenDiscoveryStatusUndefined()`: `discoveryStatus: undefined` renders "Track >>" (backward compat)
   - All variants link to `/submit/{id}` with no href difference
   - **Coverage Target**: 90%

**Implementation**:
1. In the result row JSX, change the `r.id` branch to:
   ```tsx
   <a href={`/submit/${r.id}`} style={{ color: "var(--text-muted)", textDecoration: "none", fontSize: "0.75rem" }}>
     {r.discoveryStatus === "verified" ? "Rescan" : "Track"} {">>"}
   </a>
   ```
