---
increment: 0732-skill-update-tracking-resolution
title: 0708 follow-up — tracking source resolution + ID format
type: feature
priority: P1
status: completed
created: 2026-04-25T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: 0708 follow-up — tracking source resolution + ID format

## Overview

Two systemic bugs in the 0708 push pipeline went undetected through 0708 + 0727 closure and surfaced only during live production verification on 2026-04-25:

1. **91 first-party `anton-abyzov/vskill/*` skills have `Skill.sourceRepoUrl: null`.** The scanner cron query is `WHERE sourceRepoUrl IS NOT NULL` — every one of these skills is silently skipped on every tick. Root cause: `discovery/resolver.ts` reads only `repository:` from each `SKILL.md` frontmatter (lines 151–152). Plugin-namespaced first-party SKILL.md files don't carry that field; the parent `.claude-plugin/plugin.json` does (Anthropic plugin spec). The resolver never falls back.
2. **UpdateHub Durable Object filter ID-format mismatch.** `update-hub.ts:144` checks `attachment.filter.includes(event.skillId)`. Events carry the DB UUID (`Skill.id`); the public discovery API returns slug IDs (`sk_published_<owner>/<repo>/<skill>`). Live verification: subscribing with the slug ID delivers no events; subscribing with the UUID delivers within ~14 s. The contract is undocumented and untested.

This increment delivers (a) a precedence chain in the resolver that inherits from `plugin.json` and `marketplace.json`, (b) a one-shot idempotent backfill script for the orphaned 91 rows, and (c) a documented + tested skill-ID-format contract for the SSE filter.

**Research-rejected alternatives** (do not revisit): introducing `vskill.lock` (collides with the consumer install lockfile in 0644/0647), using top-level `package.json` (wrong granularity), per-skill sidecar `skill.json` (drift risk), forcing `repository:` into every SKILL.md (91 manual edits + duplicates info already in `plugin.json`).

## Personas

- **Plugin author** — authors a `.claude-plugin/plugin.json` plus N skills under `plugins/<plugin>/skills/<skill>/SKILL.md`. Today, must remember to add `repository:` to every SKILL.md or be silently un-tracked.
- **Platform operator** — runs Prisma + Cloudflare Workers; needs a one-shot, idempotent, dry-runnable backfill to retroactively fix the 91 broken rows without a schema change.
- **Studio client developer** — consumes the public discovery API and the SSE stream; today gets slug IDs from `/api/v1/skills/*` but those don't match the SSE filter expectation, with no documentation explaining why.

## User Stories

### US-001: Plugin-inherited tracking
**Project**: vskill-platform

**As a** vskill plugin author
**I want** my plugin's `repository` field in `.claude-plugin/plugin.json` to automatically register every skill in that plugin for update tracking
**So that** I don't have to add `repository:` to every individual SKILL.md frontmatter

**Acceptance Criteria**:
- [x] **AC-US1-01**: When SKILL.md frontmatter has no `repository:` field, the resolver consults the parent `plugin.json.repository` and uses it for `sourceRepoUrl`.
- [x] **AC-US1-02**: When neither SKILL.md nor `plugin.json` declares `repository`, the resolver consults `.claude-plugin/marketplace.json` and infers the owner from the plugin entry; this is the third (last-resort) fallback.
- [x] **AC-US1-03**: When SKILL.md frontmatter has `branch:` AND `plugin.json.tracking.branch` exists, the SKILL.md value wins (per-skill specificity).
- [x] **AC-US1-04**: The resolver does NOT overwrite `Skill.sourceRepoUrl` for rows where `Skill.resolutionState = "user-locked"` (preserves manual `register-tracking` opt-ins).
- [x] **AC-US1-05**: When a new Skill row is minted at the Skill-row minting sites (`src/app/api/v1/admin/rebuild-index/route.ts` and `src/lib/submission/publish.ts`), it persists `sourceRepoUrl` and `sourceBranch` directly at insert time on the `create` branch — the resolver becomes the fallback, not the only path. (Spec originally named `scanner.ts`, but the actual minting sites are the rebuild-index route and submission publish path; resolver wiring at `resolveSkillSource` consumes the precedence chain for any rows minted before this change.)

### US-002: One-shot backfill for orphaned skills
**Project**: vskill-platform

**As a** platform operator
**I want** a single idempotent backfill operation that resolves `sourceRepoUrl` for every currently-null Skill row
**So that** the 91 broken first-party rows (and any equivalent 3rd-party orphans) are retroactively unblocked without manual SKILL.md edits and without a schema migration

**Acceptance Criteria**:
- [x] **AC-US2-01**: New script `scripts/backfill-source-repo-url.ts` is idempotent — running it twice produces identical state and zero second-run writes.
- [x] **AC-US2-02**: Script supports `--dry-run` printing the proposed updates without writing any rows.
- [x] **AC-US2-03**: For names matching `{owner}/{repo}/{slug}` it sets `sourceRepoUrl="https://github.com/{owner}/{repo}"` and `sourceBranch="main"` when the slug exists in the resolved plugin's `marketplace.json` (or in any plugin entry under that repo's `marketplace.json`). Generic script handles both array-form (`plugins[].skills`) and source-field marketplace plugin layouts (`plugins[].source: "./plugins/<name>"` walked via the GitHub Contents API); targeted `backfill-vskill-source-repo.ts` was the production one-shot for vskill.
- [x] **AC-US2-04**: Script logs a per-skill summary (`resolved` / `skipped` / `failed`), writes counts to stdout, and exits non-zero if any failures.
- [x] **AC-US2-05**: After running once, all 91 `anton-abyzov/vskill/*` skills (verified by direct `SELECT count(*) FROM "Skill" WHERE name LIKE 'anton-abyzov/vskill/%' AND "sourceRepoUrl" IS NULL`) have non-null `sourceRepoUrl`. Equivalent rows for any other plugin author whose skills follow the `{owner}/{repo}/{slug}` pattern are also resolved. Generic script handles both array-form and source-field marketplace plugin layouts; targeted `backfill-vskill-source-repo.ts` was the production one-shot for vskill.

### US-003: Documented + tested skill-ID-format contract
**Project**: vskill-platform

**As a** Studio client developer
**I want** a documented and tested contract for which skill-ID format the SSE `?skills=` filter expects
**So that** I don't waste hours debugging silent event drops caused by passing the wrong ID format

**Acceptance Criteria**:
- [x] **AC-US3-01**: A test exists in `update-hub.test.ts` that fails today and passes after the implementation, exercising the real DO filter (not stubbed) with both UUID and slug-ID inputs.
- [x] **AC-US3-02**: A doc-comment block at the top of `update-hub.ts` (and a one-paragraph entry in the SSE stream route's docstring at `src/app/api/v1/skills/stream/route.ts`) states the chosen contract explicitly: which ID format clients send in `?skills=`, why, and what happens with the other format.
- [x] **AC-US3-03**: An end-to-end integration test (extend the pattern from `vskill/src/eval-ui/src/hooks/__tests__/useSkillUpdates.real-sse.test.ts` shipped on 2026-04-25) proves the chosen path works against a real SSE stream — boots a real http SSE server and asserts the badge appears given the contract-correct ID format.

## Functional Requirements

- **FR-001 (resolver precedence chain)**: `discovery/resolver.ts` reads in order: `SKILL.md.repository` → `plugin.json.repository` → `marketplace.json` owner inference. First non-empty value wins. `branch:` follows the same chain with SKILL.md taking specificity precedence.
- **FR-002 (scanner write-at-discovery)**: `scanner.ts` writes `sourceRepoUrl` and `sourceBranch` onto new `Skill` rows when minting them via `discoverPluginSkills(owner, repo, branch, …)` — context is already in scope (per audit of `scanner.ts:362–389`); just persist it.
- **FR-003 (user-locked guard)**: Both the resolver and the scanner check `Skill.resolutionState` and skip writes when value is `"user-locked"`.
- **FR-004 (backfill script)**: `scripts/backfill-source-repo-url.ts` queries `Skill` for `sourceRepoUrl IS NULL`, parses each `name` as `{owner}/{repo}/{slug}`, fetches `marketplace.json` from `github.com/{owner}/{repo}`, locates the plugin containing the slug, and writes `sourceRepoUrl`/`sourceBranch`. Supports `--dry-run`. Idempotent.
- **FR-005 (US-3 server-side normalization — proposed default)**: At publish time in `src/app/api/v1/internal/skills/publish/route.ts`, before forwarding to the UpdateHub DO, augment the event payload with both `skillId` (UUID — internal) and `skillSlug` (public slug). UpdateHub's filter check accepts a match against either, so clients can subscribe with whichever ID they have.
- **FR-006 (documentation)**: Top-of-file doc comments in `update-hub.ts`, `stream/route.ts`, and `publish-client.ts` describe the ID-format contract with examples.

## Non-Functional Requirements

- **NFR-001 (perf)**: Scanner write-at-discovery adds at most one column per insert — no extra DB round-trips. Resolver fallback adds at most one filesystem read of `plugin.json` per skill per resolution — already cached by the discovery flow.
- **NFR-002 (compatibility)**: Existing `Skill` rows whose `sourceRepoUrl` is already set are not touched (FR-003 guard). The DO filter ID-format change is additive (accept both formats); no breaking change for current Studio client builds.
- **NFR-003 (operator safety)**: Backfill script is dry-runnable, idempotent, logs every action, and exits non-zero on any write failure. No row is silently skipped without a log line.
- **NFR-004 (testability)**: All FRs have TDD tests written before implementation. New AC-US3-03 reuses the real-SSE harness pattern from the 0708 closure work — no new test infrastructure invented.

## Success Criteria

- **SC-001**: After backfill runs in production, `SELECT count(*) FROM "Skill" WHERE name LIKE 'anton-abyzov/vskill/%' AND "sourceRepoUrl" IS NULL` returns `0`.
- **SC-002**: A trivial commit pushed to `anton-abyzov/vskill@main` produces a `skill.updated` SSE frame within ≤2 cron ticks (~20 min) for any client subscribed via slug OR UUID for the affected skill.
- **SC-003**: Vitest skill-update suite grows from 134 to ≥150 tests, all green.
- **SC-004**: A new Studio dev reading the top-of-file comments in `update-hub.ts`/`stream/route.ts` knows within 30 s which ID format to use.

## Out of Scope

- New `vskill.lock` / `vskill.json` / per-skill sidecar files — explicitly rejected (research-cited collision with 0644/0647 + drift risk).
- Mandatory `tracking:` block in `plugin.json` — kept fully optional in v1.
- 0680 Phase-2 manifest API (separate increment).
- Path-scoped scanning (current scanner treats any commit on `main` as a bump for every skill tracking that repo — separate increment).
- `WORKER_SELF_REFERENCE` binding fix — already shipped as commit `665a63c` on 2026-04-25.
- Manual single-row backfill of `appstore` — already done as ops fix; backfill script will now handle 90 more.

## Dependencies

- **0708-skill-update-push-pipeline** — closed; this increment depends on the deployed scanner, outbox, DO, and SSE infrastructure.
- **0727-0708-followup-security-and-dos-hardening** — closed 2026-04-25; security hardening of the same pipeline.
- **0712-0708-followups-scanner-outbox-do-alarm-and-e2e** — separately tracked; non-overlapping (DO alarm timer + broader E2E).
- **0680-registry-versioning-v2-phase1** — author-declared version lives in SKILL.md per its spec; this increment's optional `plugin.json.tracking` block does NOT conflict.

## Open decisions to resolve during planning

1. **Overwrite policy**: Should the resolver overwrite an already-resolved `sourceRepoUrl` if `plugin.json.repository` later changes (e.g. plugin moves repos)? **Proposed**: only when `Skill.resolutionState != "user-locked"`. Captured in AC-US1-04.
2. **Branch precedence**: SKILL.md `branch:` vs `plugin.json.tracking.branch` — **proposed**: SKILL.md wins (per-skill specificity). Captured in AC-US1-03.
3. **US-3 path — server normalization vs client contract**: **proposed default (a) server-side normalization** via FR-005. Cheaper for clients, single source of truth, future-proof. Path (b) — pure client-contract — is the fallback if (a) breaks DO hibernation invariants under load. To be confirmed in plan.md.
4. **Backfill mechanism**: standalone script vs admin endpoint vs Prisma migration. **Proposed**: standalone script under `scripts/` (no schema change, dry-runnable, revertable, no auth surface added). Captured in AC-US2-01..05.
