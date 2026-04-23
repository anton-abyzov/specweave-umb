---
increment: 0680-registry-versioning-v2-phase1
title: Registry Versioning v2 — Phase 1 (server-side author-declared SemVer)
type: feature
priority: P1
status: completed
created: 2026-04-23T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Registry Versioning v2 — Phase 1 (server-side author-declared SemVer)

## Problem Statement

The verified-skill.com registry auto-patch-bumps every submission in `src/lib/submission/publish.ts:210-284`. There is no way for authors to declare `1.0.0 → 2.0.0`, no protection against duplicate or backward versions, and no publisher attribution on version rows. Worse, the integrity hash covers only `SKILL.md` — `scripts/**` and `references/**` can change silently, a real supply-chain gap. The completed companion increment `0584-skill-versioning` shipped the CLI-side algorithms (full-file SHA-256, deterministic `path\0content\n` concat, frontmatter extraction, three-way resolveVersion priority). This increment **completes the loop on the server** so the registry honours the contract the CLI already speaks.

## Goals

- Let authors declare intended semver in SKILL.md frontmatter and have the server record it verbatim (not overwrite with auto-bump) when the skill opts in via `versioningMode="author"`.
- Keep today's auto-patch-bump path untouched for existing skills (`versioningMode="auto"` default).
- Reject duplicate and backward versions at the API boundary with HTTP 409 (immutability invariant).
- Mirror the CLI `0584` hashing algorithm byte-for-byte on the server so `scripts/**` mutations are detected.
- Attribute every version to its publisher (`publishedBy`).
- Land all schema changes additively — zero breaking change to existing data.
- Provide an idempotent admin backfill endpoint to populate new columns on historical `SkillVersion` rows.

## Relationship to 0584-skill-versioning (completed)

| Concern | 0584 (shipped, CLI side) | 0680 (this increment, server side) |
|---|---|---|
| Full-file SHA-256 with sorted `path\0content\n` | `source-fetcher.ts` | `src/lib/integrity/tree-hash.ts` (new) — same bytes in, same bytes out |
| Frontmatter `version:` extraction | `vskill` resolveVersion | `src/lib/frontmatter-parser.ts` (new) |
| CRLF → LF, BOM trim | CLI normalization helpers | Same normalization re-applied server-side |
| Precedence (frontmatter wins) | Already in CLI | Honoured via `versioningMode="author"` branch |
| Auto-patch-bump on change | Already in CLI (US-004 of 0584) | Preserved via `versioningMode="auto"` branch |

**Do not re-spec CLI work.** If a concern lives in 0584's spec, it is not in scope here.

## User Stories

### US-001: Server frontmatter-aware publish with versioningMode flag (P1)
**Project**: vskill-platform

**As a** skill author publishing to verified-skill.com
**I want** the server to honour the semantic version I declared in my SKILL.md frontmatter (and reject duplicate or backward versions)
**So that** I control my skill's version story — breaking changes bump the major, and the registry enforces SemVer immutability on my behalf.

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given an existing skill with `versioningMode="auto"` (the schema default for every skill created before or during this migration), When a submission is published, Then the current patch-auto-bump pipeline in `publish.ts` executes unchanged AND all 9 tests in `src/lib/__tests__/skill-version-creation.test.ts` still pass with no modifications.
- [x] **AC-US1-02**: Given a skill with `versioningMode="author"` AND a submission whose SKILL.md contains YAML frontmatter with `version: 1.2.0` (a valid SemVer string), When the submission is published, Then a new `SkillVersion` row is persisted with `version="1.2.0"`, `major=1`, `minor=2`, `patch=0`, and `bumpSource="frontmatter"`.
- [x] **AC-US1-03**: Given a skill with `versioningMode="author"` AND a prior `SkillVersion` row at `version="1.2.0"`, When a submission with frontmatter `version: 1.2.0` is published again, Then the API responds HTTP 409 with a JSON body containing `error.code="VERSION_DUPLICATE"` and no new `SkillVersion` row is created.
- [x] **AC-US1-04**: Given a skill with `versioningMode="author"` AND a prior `SkillVersion` row at `version="1.0.0"`, When a submission with frontmatter `version: 0.9.0` is published, Then the API responds HTTP 409 with `error.code="VERSION_MONOTONICITY_VIOLATION"` and no new `SkillVersion` row is created.
- [x] **AC-US1-05**: Given a skill with `versioningMode="author"` AND a submission with no `version:` field in frontmatter OR with an invalid value (e.g. `"not-semver"`), When published, Then the server falls back to the existing auto-patch-bump path and records `bumpSource="auto-patch"` (keeping `version:` optional in Phase 1 per plan non-goal).

---

### US-002: Server-side treeHash parity with CLI (close supply-chain gap) (P1)
**Project**: vskill-platform

**As a** registry operator responsible for integrity
**I want** the server-computed `treeHash` on each `SkillVersion` to cover every file in the skill bundle (SKILL.md, scripts/**, references/**) using the exact algorithm the vskill CLI uses
**So that** a malicious actor cannot mutate `scripts/install.sh` without producing a different hash on the server — closing the gap where today only SKILL.md is hashed.

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given two submissions for the same skill where SKILL.md body is byte-identical but `scripts/setup.sh` differs by one character, When both are published (under either `versioningMode`), Then the two resulting `SkillVersion.treeHash` values differ.
- [x] **AC-US2-02**: Given the same skill bundle hashed by both the vskill CLI (from `0584` `source-fetcher.ts`) and by the new `src/lib/integrity/tree-hash.ts`, When both produce a full hex SHA-256, Then the two hex strings are byte-identical (same sort order: case-sensitive ascending by path; same concat format: `path\0content\n` per file; same normalization: CRLF→LF, UTF-8 BOM trimmed; same output: full 64-character hex, not truncated).
- [x] **AC-US2-03**: Given a skill bundle with files at varying nesting depths (e.g. `SKILL.md`, `scripts/a.sh`, `scripts/sub/deep.sh`, `references/docs/guide.md`), When `treeHash` is computed, Then every file is included, sorted by full path, and the output is stable across repeated runs on identical input.

---

### US-003: Publisher attribution on every new version row (P1)
**Project**: vskill-platform

**As a** registry operator auditing who published what
**I want** every new `SkillVersion` row to carry the user ID of the author who triggered the publish
**So that** we can trace yank/deprecate decisions (Phase 2), rate-limit bad actors, and answer "who published 1.4.2?" without joining through the `Submission` table at query time.

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given a submission with `userId="user_abc123"` in the existing `kv-store.ts:69` payload, When `publish.ts` creates a new `SkillVersion` row (under either `versioningMode`), Then `SkillVersion.publishedBy="user_abc123"` is persisted on that row.
- [x] **AC-US3-02**: Given a submission that somehow lacks a `userId` (defensive edge), When `publish.ts` attempts to create a new `SkillVersion` row, Then the publish fails with a server-side validation error (no anonymous publishes in the new path) AND no partial row is written.

---

### US-004: Admin backfill endpoint for historical version rows (P1)
**Project**: vskill-platform

**As a** registry operator rolling out Phase 1 to production
**I want** an internal-auth-gated admin endpoint that populates the new columns (`major`, `minor`, `patch`, `distTags.latest`, best-effort `treeHash`) on every pre-existing `SkillVersion` and `Skill` row
**So that** I can flip the schema on without an offline data migration step, and run the backfill safely multiple times during rollout.

**Acceptance Criteria**:
- [x] **AC-US4-01**: Given the backfill endpoint `POST /api/v1/admin/backfill-versions` is called with a valid internal-auth token (via `hasInternalAuth()` from `src/lib/internal-auth.ts`), When invoked against a database containing N historical `SkillVersion` rows with non-null `version` strings (e.g. `"1.4.2"`), Then every row has `major`, `minor`, `patch` populated to match the parsed `version` (e.g. `major=1, minor=4, patch=2`).
- [x] **AC-US4-02**: Given the backfill endpoint is called, When it completes, Then every `Skill` row with at least one historical `SkillVersion` has `distTags` set to a JSON object containing `{"latest": "<skill.currentVersion>"}` (using the existing `currentVersion` column as the truth source for the latest tag).
- [x] **AC-US4-03**: Given the backfill endpoint has been called once and completed successfully, When it is called a second time with no intervening data changes, Then the response indicates zero rows modified AND every column value is byte-identical to the first run (idempotency).
- [x] **AC-US4-04**: Given the backfill endpoint runs, When it computes `treeHash` for a historical row whose original `scripts/**` content is unreachable (e.g. content only cached as a single `contentHash`), Then it writes `treeHash = <existing contentHash>` as a fallback AND sets `bumpSource = "legacy-backfill"` so Phase 2 consumers can distinguish precise from imprecise hashes.
- [x] **AC-US4-05**: Given the endpoint is called without a valid internal-auth token, When the request arrives, Then the response is HTTP 401 (or 403 per existing `hasInternalAuth` semantics) AND no rows are modified.

---

### US-005: Additive schema evolution with migration safety (P1)
**Project**: vskill-platform

**As a** registry operator running `prisma migrate deploy` in production
**I want** the new schema columns (`Skill.versioningMode`, `Skill.distTags`, `Skill.latestStable`, `SkillVersion.major/minor/patch/prerelease/buildMetadata/treeHash/manifest/releaseNotes/declaredBump/bumpSource/yanked/yankedAt/yankReason/deprecated/deprecationMsg/publishedBy/immutable`) and the new `DistTagEvent` model to land without breaking existing reads, writes, or row counts
**So that** the rollout is reversible via a forward-only disable (flip every skill back to `versioningMode="auto"`) without data loss.

**Acceptance Criteria**:
- [x] **AC-US5-01**: Given the production schema prior to this increment and the generated migration SQL at `prisma/migrations/{ts}_versioning_v2_phase1/migration.sql`, When the SQL is reviewed, Then every column addition is nullable OR has a safe default (`versioningMode` default `"auto"`, `distTags` default `"{}"`, `yanked`/`deprecated`/`immutable` defaults per plan, all new nullable `SkillVersion` columns nullable without default) AND the migration contains no `DROP` or `ALTER COLUMN ... NOT NULL` statements against existing columns.
- [x] **AC-US5-02**: Given the migration is applied to a database containing N `Skill` rows and M `SkillVersion` rows, When `SELECT COUNT(*)` is executed on both tables after the migration, Then the counts equal the pre-migration N and M exactly (no rows lost, none created).
- [x] **AC-US5-03**: Given the new `DistTagEvent` model, When a row is created (e.g. by a Phase 2 dist-tag endpoint, or by the Phase 1 backfill when it initializes `distTags.latest`), Then the row contains `id` (uuid), `skillId`, `tag`, `version`, `actor`, and `createdAt`, and the table is indexed on `(skillId, tag, createdAt DESC)` per the plan.
- [x] **AC-US5-04**: Given the migration has been applied and zero skills have been flipped to `versioningMode="author"`, When an arbitrary submission is published through the existing pipeline, Then the behavior is observationally identical to pre-migration (same `SkillVersion.version` value written, same response shape, same status code) — the only new columns populated are `treeHash` and `publishedBy`, both of which are additive.

## Functional Requirements

### FR-001: versioningMode branching in publish pipeline
`publish.ts` MUST read `skill.versioningMode` after the existing skill lookup and branch BEFORE the version-computation block at `publish.ts:210-284`. The `"auto"` branch re-uses the existing code path verbatim. The `"author"` branch invokes `parseFrontmatter(skillMdContent)` → extracts `version` → validates SemVer → checks monotonicity against the most recent non-yanked `SkillVersion` → writes the declared version OR returns HTTP 409.

### FR-002: frontmatter-parser module
`src/lib/frontmatter-parser.ts` (new) exports a function that accepts a SKILL.md file body as string, parses YAML frontmatter via `js-yaml` with an allowlist (only `version`, `title`, `name`, `description`, `tags` are read — all other fields ignored for Phase 1), and returns `{ version?: string }`. Invalid SemVer returns `version: undefined`. Malformed YAML returns `{}` without throwing.

### FR-003: tree-hash module
`src/lib/integrity/tree-hash.ts` (new) exports a function that accepts an array of `{ path: string, content: Buffer | string }` entries, sorts by path (case-sensitive ascending), normalizes each content (strip UTF-8 BOM, convert CRLF to LF), concatenates as `path\0content\n` per file, and returns the full 64-character hex SHA-256 digest. Byte-for-byte compatible with the vskill CLI `source-fetcher.ts` algorithm shipped in 0584.

### FR-004: Monotonicity enforcement
A declared version is valid iff it is strictly greater (by SemVer precedence per semver.org §11) than the maximum `version` string across all non-yanked `SkillVersion` rows for that skill. Failure modes return HTTP 409 with structured error codes: `VERSION_DUPLICATE` (equal to existing) and `VERSION_MONOTONICITY_VIOLATION` (less than existing). Pre-release ordering (1.0.0-alpha < 1.0.0) follows semver.org.

### FR-005: Backfill endpoint contract
`POST /api/v1/admin/backfill-versions` accepts no body (or an optional `{"dryRun": boolean}`), is gated by `hasInternalAuth()`, returns `{"scanned": number, "updated": number, "skipped": number, "errors": Array<{skillId, reason}>}`, and MUST be idempotent (repeated calls on stable data produce zero `updated`). Modelled on `backfill-slugs/route.ts`.

## Success Criteria

- All 9 tests in `src/lib/__tests__/skill-version-creation.test.ts` still pass unchanged after the migration (regression guard on the default `"auto"` path).
- Prisma migration applies cleanly in CI with zero row-count delta on `Skill` and `SkillVersion`.
- New Vitest suites `frontmatter-parser.test.ts`, `tree-hash.test.ts`, and the new `publish.ts` branch tests cover 100% of ACs in this spec, with coverage ≥ 90% on new code.
- Backfill endpoint, invoked twice on the same production snapshot, produces byte-identical column values (idempotency).
- Zero submissions that previously succeeded begin failing (because `versioningMode` defaults to `"auto"` for every existing skill).

## Out of Scope (explicit non-goals for Phase 1)

- CLI range install grammar (`vskill install foo@^1.2.0`) — **Phase 2**
- Lockfile v2 + `vskill audit` — **Phase 2**
- `POST /api/v1/skills/.../yank`, `POST /deprecate`, `PUT /dist-tags/:tag` endpoints — **Phase 2**
- `GET /api/v1/skills/.../resolve` + manifest API — **Phase 2**
- LLM-based diff-classifier (advisory bump suggestions) — **Phase 2**
- R2 content migration for `SkillVersion.content` — **Phase 3**
- Requiring `version:` in frontmatter for new skills (stays optional in Phase 1) — **Phase 3**
- Admin dist-tag management UI — **Phase 2+**

## Dependencies

- **Prior-art (completed)**: `0584-skill-versioning` — CLI hashing algorithm, frontmatter extractor, resolveVersion priority chain. This increment MUST mirror that algorithm byte-for-byte on the server.
- **Existing modules reused**:
  - `hasInternalAuth()` from `src/lib/internal-auth.ts` (backfill auth gate)
  - `verifyUserAccessToken()` from `src/lib/auth.ts:64-100` (publisher identity)
  - `getKV()` + `SUBMISSIONS_KV` from `src/lib/submission/kv-store.ts:34-43` (manifest KV for Phase 2)
  - `backfill-slugs/route.ts:34-50` (template for backfill endpoint)
- **New dependency**: `js-yaml` (~50 KB). Server-only — MUST NOT be bundled into the Cloudflare Worker. Only the allowlisted fields (`version`, `title`, `name`, `description`, `tags`) are read; custom YAML tags are not executed (security).
- **Downstream consumers (Phase 2, blocked on this)**: yank/deprecate/dist-tags endpoints, `/resolve` API, range install grammar. None of these are built in this increment.

## Technical Notes

### Architecture Decisions (deferred to plan.md ADRs)

- **versioningMode flag vs. per-submission opt-in**: deferred to architect — plan choice is per-skill flag (`Skill.versioningMode`) so the publisher's mode is stable across submissions for that skill.
- **treeHash algorithm**: MUST match 0584 CLI (full hex SHA-256, sorted paths, `path\0content\n`, CRLF→LF, BOM trim). Non-negotiable — spec-level constraint, not an architect decision.
- **distTags as JSON column vs. separate table**: plan choice is JSON on `Skill` for Phase 1 (fewer joins, simpler read path). `DistTagEvent` captures the audit log separately.
- **Backfill-at-migration vs. separate endpoint**: endpoint chosen so operator controls timing and can re-run idempotently.

### Edge Cases

- **Skill bundle with only SKILL.md (no scripts, no references)**: `treeHash` still computed over the single file; AC-US2-03 covers stability.
- **SKILL.md with no frontmatter block at all**: `parseFrontmatter` returns `{}`; `versioningMode="author"` falls back to auto-patch-bump per AC-US1-05.
- **SKILL.md with frontmatter version `"2.1.0-rc.1"` (pre-release)**: valid SemVer; monotonicity checked via semver.org §11 precedence rules. Parsed into `major=2, minor=1, patch=0, prerelease="rc.1"`.
- **Concurrent publishes for the same skill** (two submissions arriving within ms of each other, both declaring `version: 1.5.0`): the later write loses on the unique `(skillId, version)` constraint and the server returns HTTP 409 with `VERSION_DUPLICATE`. Which one wins is determined by DB ordering (existing behavior, no new guarantee).
- **Historical `SkillVersion` rows with non-SemVer `version` strings** (e.g. `"v1.0"` or `""`): backfill skips them, records an entry in `errors[]`, and does not block subsequent rows. Operator can fix manually.
- **Skill flipped from `"auto"` to `"author"` mid-lifecycle**: next publish in `"author"` mode must declare a version strictly greater than the skill's current `currentVersion` — monotonicity unchanged by the flip.

### Non-Functional Requirements

- **Performance**: `treeHash` computation completes in under 50ms for skill bundles up to 50 files (matching 0584 SLO).
- **Security**: `js-yaml` used with allowlisted field reads only (no custom-tag execution). Backfill endpoint gated by `hasInternalAuth()`. Monotonicity enforcement prevents publisher-spoofed rollbacks.
- **Compatibility**: Migration is forward-only but rollout is reversible — setting every `Skill.versioningMode` back to `"auto"` restores pre-increment behavior without touching data.
- **Observability**: Every HTTP 409 response emits a structured log entry with `skillId`, `declaredVersion`, `existingMaxVersion`, `errorCode` for post-mortem.

## Risks

| Risk | Probability | Impact | Severity | Mitigation |
|------|-------------|--------|----------|------------|
| `js-yaml` accidentally pulled into Cloudflare Worker bundle, blows 1MB limit | 0.3 | 6 | 1.8 | Import only from server-side route handlers; add a bundle-size check in CI per the 0673 deploy-runbook pattern |
| `treeHash` algorithm drifts from CLI version → CLI thinks skill changed when it didn't (or vice versa) | 0.25 | 7 | 1.75 | AC-US2-02 is a cross-implementation byte-equality test; ship a shared test vector committed in both 0584 and 0680 repos |
| Backfill on prod DB runs slow (N+1 reads) and times out at Cloudflare 30s gateway | 0.35 | 4 | 1.4 | Architect to paginate or batch in plan.md; idempotency (AC-US4-03) means operator can chunk safely |
| Author accidentally declares `version: 999.0.0` then cannot walk back | 0.4 | 3 | 1.2 | Phase 2 yank endpoint covers this; Phase 1 documents immutability as a known trade-off |
| Historical rows with corrupt `version` strings break backfill | 0.2 | 3 | 0.6 | AC-US4-05 + `errors[]` response — skip and report, never fail the whole run |

## Implementation Notes (informational — not prescriptive)

The architect will resolve these in `plan.md`. Listed here so the planner has visibility:

- Where exactly in `publish.ts:210-284` the `versioningMode` branch is placed.
- Whether `parseFrontmatter` shares code with vskill CLI via a workspace package or is an independent reimplementation (plan default: independent, with AC-US2-02 as the correctness bridge).
- Prisma index strategy for the new `(skillId, major, minor, patch)` and `(skillId, yanked, createdAt DESC)` composite indexes at schema-level.
- Pagination strategy for the backfill endpoint (offset? cursor? chunked by createdAt?).
