---
increment: 0821-studio-check-updates-batching
title: "Studio Check-Updates Batching"
type: bug
priority: P1
status: active
created: 2026-05-01
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Studio Check-Updates Batching

## Overview

Skill Studio fires `POST /api/v1/skills/check-updates` from two paths in `src/eval-ui/src/api.ts` (`checkSkillUpdates` at line 920 and `resolveInstalledSkillIds` at line 987). Both paths send the entire installed-skill list as a single batch.

The platform handler at `vskill-platform/src/app/api/v1/skills/check-updates/route.ts:139` enforces `MAX_BATCH_SIZE = 100` and returns:

```json
{"error":"Maximum 100 skills per request"}
```

with HTTP 400 when the batch is larger.

A user with 230 installed skills (visible in Studio header as `Claude Code (12 . 12 . 50)` — counts include marketplace plugins) gets the 400 logged in the browser console as `Failed to load resource: the server responded with a status of 400 (Bad Request)`. The reconcile tracking (`AC-US5-09` not-tracked dot) silently degrades to "no tracking state" until the user has < 100 skills.

**Root cause** — neither studio call site batches the request. Both build a single `skills: [...]` body from the full input array.

**Fix** — chunk the input into batches of `≤100` in both call sites, fire the batches in parallel (`Promise.all`), and merge the results before returning. The platform handler stays unchanged; `MAX_BATCH_SIZE` is an intentional protection. No SSE/proxy changes required (proxy is path-only and forwards bodies verbatim, see `src/eval-server/platform-proxy.ts:139`).

## User Stories

### US-001: Batch checkSkillUpdates in Studio API client (P1)
**Project**: vskill

**As a** Studio user with more than 100 installed skills
**I want** the reconcile call to succeed without a 400 in the console
**So that** the not-tracked dot (AC-US5-09) and update bell stay accurate at any installed-skill scale

**Acceptance Criteria**:
- [x] **AC-US1-01**: `api.checkSkillUpdates(skillIds)` in `src/eval-ui/src/api.ts` chunks `skillIds` into groups of `≤100` before calling `/api/v1/skills/check-updates`.
- [x] **AC-US1-02**: When `skillIds.length ≤ 100`, the function makes exactly one fetch (no behavioral change for the common case).
- [x] **AC-US1-03**: When `skillIds.length > 100`, the function makes `Math.ceil(length / 100)` fetches concurrently via `Promise.all` and concatenates the `results` arrays in input order before returning.
- [x] **AC-US1-04**: A single chunk failing (non-OK response or thrown error) does NOT fail the whole call — that chunk contributes an empty result slice; successful chunks still merge. Mirrors the existing single-call `if (!res.ok) return [];` graceful-degradation contract.
- [x] **AC-US1-05**: A unit test in `src/eval-ui/src/api.test.ts` exercises the 230-skill case: it asserts exactly 3 fetch calls (chunks of 100, 100, 30) and the merged result preserves order.
- [x] **AC-US1-06**: A unit test asserts the 100-skill case fires exactly 1 fetch call (boundary condition).
- [x] **AC-US1-07**: A unit test asserts that when the first chunk's mock rejects but the second resolves, the function returns the second chunk's results (partial degradation).

---

### US-002: Batch resolveInstalledSkillIds in Studio API client (P1)
**Project**: vskill

**As a** Studio user with more than 100 installed skills
**I want** UUID/slug resolution to succeed for ALL my installed skills, not just the first 100
**So that** the SSE subscription filter (AC-US3-01) covers every skill and updates are not silently lost above 100

**Acceptance Criteria**:
- [x] **AC-US2-01**: `api.resolveInstalledSkillIds(skills)` in `src/eval-ui/src/api.ts` chunks `skills` into groups of `≤100` before calling `/api/v1/skills/check-updates`.
- [x] **AC-US2-02**: Chunked fetches run concurrently via `Promise.all`; the function still returns one entry per input skill, in input order, and the `byName` lookup correctly resolves UUID/slug across all chunks.
- [x] **AC-US2-03**: When a chunk fails (non-OK or throws), every input skill in that chunk degrades to `{ plugin, skill }` with no `uuid`/`slug`, matching the existing single-call fallback. Other chunks still contribute enriched results.
- [x] **AC-US2-04**: A unit test in `src/eval-ui/src/api.test.ts` exercises the 230-skill case: asserts 3 fetch calls and that all 230 input skills appear in the result with correct plugin/skill identifiers.
- [x] **AC-US2-05**: A unit test asserts the 100-skill boundary case fires exactly 1 fetch call.

---

### US-003: Shared chunking helper to keep call sites DRY (P2)
**Project**: vskill

**As a** future maintainer adding a third `/check-updates` caller
**I want** one well-tested chunking helper rather than two ad-hoc loops
**So that** the 100-cap discipline cannot regress the next time someone copy-pastes the call site

**Acceptance Criteria**:
- [x] **AC-US3-01**: A module-private helper `chunkArray<T>(arr: T[], size: number): T[][]` lives at the top of `src/eval-ui/src/api.ts` (file-internal, not exported), used by both US-001 and US-002.
- [x] **AC-US3-02**: The helper handles edge cases: empty input → `[]`; input length equal to `size` → one chunk; input length less than `size` → one chunk; input length exactly N×size → N chunks of `size`.
- [x] **AC-US3-03**: A unit test covers the four edge cases in AC-US3-02 plus the 230-element case (returns `[100, 100, 30]`-length chunks).
- [x] **AC-US3-04**: The constant `CHECK_UPDATES_BATCH_SIZE = 100` is declared once at module scope with a comment pointing to `vskill-platform/src/app/api/v1/skills/check-updates/route.ts:139` (the platform `MAX_BATCH_SIZE` it mirrors).

## Functional Requirements

### FR-001: Client-side chunk size mirrors platform cap
The studio chunk size MUST be `100`, matching `MAX_BATCH_SIZE` at `vskill-platform/src/app/api/v1/skills/check-updates/route.ts:139`. If the platform cap changes, the studio constant must be updated in lockstep — the comment at the constant declaration is the authoritative pointer.

### FR-002: Parallel fetches, ordered merge
Chunked fetches run via `Promise.all` so latency stays close to a single round-trip. Result merging preserves input order (slice concatenation in chunk order, which is input order).

### FR-003: Per-chunk graceful degradation
A failing chunk does NOT fail the whole call. The existing graceful-fallback semantics (`checkSkillUpdates` returns `[]`, `resolveInstalledSkillIds` returns un-enriched entries) apply per-chunk so a single transient failure on one batch doesn't blank out the whole reconcile.

### FR-004: No protocol or proxy changes
The platform endpoint, the eval-server proxy at `src/eval-server/platform-proxy.ts`, and the SSE stream contract are unchanged. This is a client-only fix.

## Success Criteria

- With 230 installed skills, the browser console no longer shows `Failed to load resource: the server responded with a status of 400 (Bad Request)` for `/api/v1/skills/check-updates`.
- `curl -X POST http://localhost:3157/api/v1/skills/check-updates -H 'content-type: application/json' -d '{"skills":[...100 entries...]}'` returns 200 (already passes; sanity check).
- All new unit tests in `src/eval-ui/src/api.test.ts` pass: `npx vitest run src/eval-ui/src/api.test.ts`.
- The full vitest suite still passes: `npx vitest run`.
- Manual studio reload with > 100 installed skills shows network panel making 2+ `check-updates` requests, all with status 200, and the not-tracked dots populate correctly across all skills.

## Out of Scope

- Platform-side `MAX_BATCH_SIZE` increase — the cap is intentional protection against abuse and KV cache key bloat.
- Changing the SSE stream subscription filter format.
- Adding retry/backoff for individual chunks (graceful degradation already exists; add only if observed failures justify it).
- Refactoring `useSkillUpdates.ts` reconciliation lifecycle — chunking happens entirely inside the API client; the hook sees the same merged result shape it always did.
- Updating the CLI `checkUpdates()` in `src/api/client.ts` — that path is invoked by `vskill outdated` against ≤100 skills per run today; if it ever crosses 100 we'll batch separately.

## Dependencies

- Existing `fetchWith5xxRetry` helper in `src/eval-ui/src/api.ts` (consumed by both call sites).
- Existing platform handler at `vskill-platform/src/app/api/v1/skills/check-updates/route.ts:139` (unchanged; documents the cap).
- Existing eval-server proxy at `src/eval-server/platform-proxy.ts:139` (unchanged; forwards bodies verbatim).
- Vitest harness already wired in `src/eval-ui/src/api.test.ts` (mirrored test patterns exist for fetch-mocked API client functions).
