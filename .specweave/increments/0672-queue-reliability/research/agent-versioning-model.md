# Research Agent 2 — Versioning Model Investigator

**Role**: read-only code explorer. Figure out whether multiple Submission rows per `(repoUrl, skillName)` are legitimately tracking different versions of a skill (in which case collapsing them destroys history), or are accidental re-submission duplicates.

---

## 1. How versioning is currently modeled

**`Skill.name` is globally unique** (`prisma/schema.prisma:216`, `@unique`). One canonical row per skill name, with `currentVersion` tracking the latest published semantic version (`schema.prisma:225`).

**`SkillVersion` is the per-version record**, keyed `@@unique([skillId, version])` (`schema.prisma:378`). Fields:
- `version` — semantic (e.g., "1.0.0")
- `contentHash` — SHA-256 of SKILL.md
- `gitSha` — commit hash
- `certifiedAt`
- `content` — full SKILL.md text

**Version semantics are content-diff-driven**, not SKILL.md frontmatter or package.json or git tag:
- First publish → v1.0.0 (`publish.ts:164`)
- Subsequent publish: if `contentHash` differs from `latestVersion.contentHash`, bump patch (1.0.0 → 1.0.1) (`publish.ts:221–238`). If identical, update cert tier + cert score in place without creating a new row (`publish.ts:222–230`).

## 2. How Submissions relate to versions

**Submission is a processing receipt, not a version artifact.**

- **Submission → Skill**: intended one-active-row per `(repoUrl, skillName)` per the new `@@unique` constraint (`schema.prisma:200` — added in 0672). `skillId` is NULL until publication, then populated by `publishSkill()` (`publish.ts:302–308`).
- **Submission → SkillVersion**: no direct FK; SkillVersion is created inside `publishSkill()` if content changed. One Submission produces at most one new SkillVersion (or re-certifies the existing one).

**Critical insight**: a re-submission of the same `(repoUrl, skillName)` does not create a new Submission — it returns the existing row's state via `upsertSubmission` (`upsert.ts:84–99`). That's the whole point of the 0672 P2002 catch pattern.

## 3. Scan-vs-submit split

**Re-scan of the same version creates a NEW Submission row; re-submit returns the EXISTING row.**

- **Re-submit** (CLI user re-runs `vskill install`): `upsertSubmission` catches P2002 on `(repoUrl, skillName)`, fetches the existing Submission, returns its state — no new row (`upsert.ts:86–121`).
- **Re-scan** (admin/cron triggers fresh scan): `/api/v1/admin/rescan-published` explicitly calls `createMany({ skipDuplicates: true })` (`rescan-published/route.ts:166–178`). Creates a fresh Submission row per skill, bypassing upsert dedup because rescans are operational events needing fresh scan results + audit trail.

**Why the split?** User submissions must be idempotent (CLI pollers retry). Admin/cron rescans are one-time operational events that need new audit trails.

## 4. 0672 design fit

The 0672 Track B implementation (`src/lib/submission/upsert.ts`) codifies `@@unique([repoUrl, skillName])` as the uniqueness key for submissions. Comment at `upsert.ts:2-5`:

> "Uses a DB-level unique constraint on (repoUrl, skillName) + P2002 catch pattern... on `created`, writes KV entries. On a P2002 collision, returns the existing row's state without touching KV."

**Does it align with the rest of the system?** Yes.

- The Submission unique constraint collapses duplicate user submissions (same repo, same skill name, potentially submitted multiple times).
- It does NOT prevent multi-version workflows: a new version triggers `publishSkill()` to create a new SkillVersion row; the Submission row is reused (stays linked to the same Skill).
- Scan results are per-Submission (not per-SkillVersion), so admin-triggered re-scans create new Submissions to gather fresh ScanResult rows — via the explicit rescan-published endpoint.

**One edge case**: if a skill publishes v1.0.0, then the repo reverts (content hash changes), a re-submit would P2002 on the same Submission row. `publishSkill` has been linked to Skill once (`publish.ts:304`), so relinking isn't possible. But this is a rare operational scenario.

## 5. `contentHashAtScan` field analysis

**What it is**: SHA-256 of SKILL.md content at scan time, stored on `Submission.contentHashAtScan` (`schema.prisma:195`).

**What it's used for**:
- Tamper detection: prevents submitting identical code twice if the repo is already at that version.
- Version bumping decision: in `publishSkill()`, compares `scan.contentHash` against `latestVersion.contentHash` to decide patch bump vs in-place re-cert (`publish.ts:221`).

**Is it per-version?** Yes:
- Computed once per Submission during tier-1/tier-2 scanning (`process-submission.ts:328`).
- Stored in `ScanResult.contentHash` (same value propagated).
- Not re-computed on re-scans — each new Submission gets its own contentHash.

**BUT (per data analyst): 100 % of prod rows have NULL `contentHashAtScan`.** So the field is defined but not populated at scale. Likely populated only for newer scans (post-instrumentation).

**Example scenario**:
1. Repo at commit A, skillName="foo", SKILL.md hash="abc123"
2. User submits → Submission-1, ScanResult.contentHash="abc123", publishes → SkillVersion-1 (v1.0.0)
3. Repo at commit B, SKILL.md hash="def456"
4. Admin triggers rescan → Submission-2 (new row), ScanResult.contentHash="def456"
5. Publishes → `publishSkill` compares "def456" ≠ "abc123" → creates SkillVersion-2 (v1.0.1)

## 6. Source field & provenance

**`Submission.source` field does not exist** in the schema. Instead there's `isVendor` (boolean) + `vendorOrg` (string) (`schema.prisma:158–159`).

However, the POST endpoint tracks source implicitly via a `source` parameter (`submissions/route.ts:509, 520`) that affects submission priority:
- `source === "cli-auto"` → priority 90 (CI/CD)
- Otherwise (website, CLI) → priority 50
- Bulk/crawler → priority 0

This is priority metadata, not a uniqueness discriminator. Two submissions from different sources for the same `(repoUrl, skillName)` collide at the DB unique constraint (as intended).

## 7. Existing dedup heuristics in the API layer

**No dedup heuristics below `upsertSubmission`**:

- **POST `/api/v1/submissions`** (route.ts:650–677) — single-skill path calls `upsertSubmission` once. `kind: "pending"` → caller retries with same Submission ID. `kind: "created"` → new row made.
- **POST `/api/v1/submissions/bulk`** (batch mode) — requires auth, passes all skills to DB batch; no dedup at this layer — relies on the discovery endpoint having pre-filtered.
- **POST `/api/v1/admin/rescan-published`** — explicitly AVOIDS dedup on Submission creation using `createMany({ skipDuplicates: true })`, allowing fresh rows for rescans.
- **POST `/api/v1/admin/dedup-skills`** — operates on the **Skill** table (not Submission). Groups by `(repoUrl, skillPath)`, deprecates lower-trust losers. Skill-level dedup, not submission-level.

## 8. Recommended true uniqueness key

**Current (0672)**: `@@unique([repoUrl, skillName])` on Submission.

**Recommendation: keep as-is.**

1. **Semantic correctness**: a submission is a user/system request to process a skill at a repo. One active request per skill = correct cardinality.
2. **Version handling**: versions are managed by SkillVersion (`contentHash`-driven bumping), not by collapsing Submissions. Multi-version workflows are explicit: new Submission → new SkillVersion.
3. **Rescan isolation**: rescans need their own Submission rows for audit trail + fresh ScanResults. The rescan endpoint already bypasses Submission dedup intentionally.
4. **Alternative keys considered**:
   - `(repoUrl, skillName, contentHashAtScan)` — would allow multiple submissions of same code. Violates "one active request per skill."
   - `(repoUrl, skillName, version)` — version comes from SkillVersion, not known at submission time. Circular.

**Schema documentation tasks** (separate increment):
- Add a comment to `Submission.contentHashAtScan` clarifying it's for tamper detection + version-bump logic, NOT submission uniqueness.
- Clarify that admin re-scanning must go through `/api/v1/admin/rescan-published` (creates new Submissions), not re-POST to `/api/v1/submissions` (reuses).
- Instrument `contentHashAtScan` on every new submission (closing the 100 % NULL gap).

## Summary

| Aspect | Current Model | Behavior | Evidence |
|---|---|---|---|
| Skill uniqueness | `Skill.name` (global) | one row per name | `schema.prisma:216` |
| Submission uniqueness | `(repoUrl, skillName)` | one active row per skill request | `schema.prisma:200`, `upsert.ts:88` |
| Version storage | `SkillVersion` | `(skillId, version)` semantic rows | `schema.prisma:378` |
| Version source | content-diff | `contentHash` comparison, patch bumps | `publish.ts:221–238` |
| Re-submit same code | returns existing Submission | no new row | `upsert.ts:84–121` |
| Re-scan (admin) | creates new Submission | fresh row for audit/ScanResults | `rescan-published/route.ts:166` |
| `contentHash` scope | per-Submission | SHA-256 of SKILL.md at scan | `process-submission.ts:328`, `publish.ts:213` |
| Dedup at API | `upsertSubmission` only | P2002 catch | `upsert.ts:84` |
