---
status: completed
project: vskill-platform
---
# 0685 — Fix rescan-published no-op caused by Submission unique key collision

## Context

An adversarial Codex review of in-progress 0673 work found two blocking
defects in `POST /api/v1/admin/rescan-published` (see
`reports/codex-adversarial-review.md` for the verbatim review):

1. **HIGH — rescan no-ops for the common case.** The handler tries to
   insert a *new* `Submission` row per eligible `Skill` via
   `createMany({ skipDuplicates: true })`. But `Submission` has
   `@@unique([repoUrl, skillName])` (schema.prisma:200) and the normal
   publish path **keeps** the original submission row and links it to
   the `Skill` (`Submission.skillId = skill.id`, publish.ts:302-305).
   For any already-published skill that still has its terminal
   submission row, `skipDuplicates: true` silently drops the insert —
   so nothing rescans.
2. **MEDIUM — post-create readback is a new stranded-work failure mode.**
   After `createMany` commits, the handler does
   `findMany({ id: { in: attemptedIds } })` to learn which inserts
   actually won. If that second read fails (Neon timeout / circuit),
   the rows exist in `RECEIVED` but no queue messages get sent and no
   audit events fire. The 500 response looks like total failure, but
   rows are stranded. The route's own eligibility filter excludes
   `RECEIVED`, so retrying the endpoint cannot repair the state — only
   the stale-`RECEIVED` background recovery catches it.

## Goal

`rescan-published` must **actually rescan** every eligible published
skill, and must not strand submissions in `RECEIVED` without queue
messages when a transient DB read fails.

## User Stories

### US-001 — Rescan actually rescans existing published skills

**As** an admin triggering a bulk rescan of published T1/T2 skills,
**I want** every eligible skill to get re-queued for Tier-2 analysis,
**so that** trust scores can be recomputed without me having to manually
reset submission state.

**Acceptance Criteria**

- [x] **AC-US1-01** (Reuse, not insert): Given a published `Skill` whose
  terminal `Submission` row still exists and is linked via
  `Submission.skillId = Skill.id`, when `rescan-published` runs,
  then the route resets that **existing** submission's state to
  `RECEIVED` and enqueues **one** queue message for it. It MUST NOT
  attempt to `createMany` a new submission under the same
  `(repoUrl, skillName)` key.
- [x] **AC-US1-02** (Queue count matches skill count): Given N eligible
  skills (each with a linked terminal submission and not
  in-flight), when the route runs, then exactly N queue messages
  are sent — regardless of whether new rows would have collided
  with the unique key.
- [x] **AC-US1-03** (Orphan skills are logged, not silently dropped):
  Given a `Skill` with no linked `Submission`, when the route
  encounters it, then the route skips it, counts it in an
  `orphanedSkipped` field of the response, and logs a structured
  warning (so ops can investigate) — it MUST NOT attempt a
  `createMany` insert (which would re-introduce the unique-key
  collision risk).
- [x] **AC-US1-04** (Audit trail is produced from reused IDs): When
  existing submissions are reset, a `SubmissionStateEvent` row is
  written for each reused submission with
  `trigger: "rescan-published: trust elevation"`, `actor: "system"`,
  `actorType: "admin"`, `toState: "RECEIVED"`, referencing the reused
  `submissionId`.

### US-002 — Rescan is not stranded by transient DB failures

**As** an admin triggering rescan on a pipeline under load,
**I want** queueing to succeed even if a post-write readback fails,
**so that** submissions aren't left in `RECEIVED` with no queue message
and no way to recover except the stale-`RECEIVED` background sweep.

**Acceptance Criteria**

- [x] **AC-US2-01** (No post-write readback in the primary path): The fix
  removes the `createMany → findMany-by-id` readback pattern entirely
  from the happy path. Since IDs are now known *before* the state
  reset (they come from the `findMany`-by-skillId that locates
  existing submissions), queueing uses those IDs directly. No second
  DB read is required to know what to enqueue.
- [x] **AC-US2-02** (Partial enqueue failures are surfaced, not silently
  stranded): If the bulk `updateMany` succeeds but a queue chunk
  `sendBatch` rejects, the route returns `ok: true` with a per-chunk
  `errors[]` entry (existing behavior, preserved). Audit events are
  still written for all reused submissions so the stuck-`RECEIVED`
  recovery sweep can pick up any orphans.
- [x] **AC-US2-03** (Auth unchanged): `X-Internal-Key` and SUPER_ADMIN
  Bearer paths keep working; no auth regression.

## Out of Scope

- **DO NOT** change `prisma/schema.prisma` — the unique key
  `@@unique([repoUrl, skillName])` on `Submission` stays as-is; Codex
  explicitly recommended against a schema change.
- **DO NOT** change `src/lib/submission/publish.ts` — its contract of
  keeping the terminal submission row and linking it via `skillId` is
  exactly what this fix relies on.
- Integration / failure-mode / contract / parallel / persistence test
  files in the same `__tests__/` folder are owned by two sibling
  testing agents (testing-integration-agent and testing-failure-agent);
  this increment's backend agent only owns `route.test.ts` and
  `route.ts`.

## Success Metrics

- `route.test.ts` suite passes with new reuse + orphan + no-readback
  cases.
- Manual smoke (post-deploy, not in this increment): a dry-run against
  a known-published skill reports `totalMatching > 0`, and a live call
  returns `rescanned == totalMatching` with one queue message per
  rescanned skill.
- The "skipDuplicates silently dropped N rows" pattern no longer
  appears in handler logs for this route.
