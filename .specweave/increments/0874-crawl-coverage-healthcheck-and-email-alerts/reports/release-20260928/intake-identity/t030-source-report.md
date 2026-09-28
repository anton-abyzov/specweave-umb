# 0874 T030 — canonical submission intake collisions

Source candidate: `05f9bb6ef6a25026c3cf35f0b63b62bebdb0c4cb`, draft PR79, based on merged T029 `1e8058fbab6afe37864d5b882bb8d3552eef1349`. Four files; no schema, crawler, deployment, or production data edits. Worktree: `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/0874-intake-identity`.

## Confirmed cause

A natural scheduled VM3 retry logged a database uniqueness failure on `sourceType`, `sourceId`, and `artifactPath`. A guarded read-only PostgreSQL transaction found the active canonical index and exactly one matching existing PUBLISHED submission. Its stable source ID and artifact path match, as does the actual skill path; the incoming URL differs. The linked Skill is PUBLIC and tenantless. No raw repository identity, path, credentials, or skill content were exported. The immutable row-ID hash is `7821b066b63a6920b563d8c2cc71461e231b2c4a6f1531991a487de29075de02`.

The source only recognized the legacy URL/name constraint, so this legitimate canonical duplicate remained an error. The crawler correctly retained the unacknowledged discovery; its acceptance/checkpoint logic was not changed.

## Repair

Recognize only exact known identity constraints. Resolve a complete canonical tuple before the legacy index, including when both indexes can collide. Validate every canonical field and the case-preserving artifact path. Legacy fallback permits historical nullable fields only when populated fields, URL/name, and path agree; it never backfills identity. Public tenantless Skills can be reused regardless of original author; private/tenant-linked or unrelated unlinked user-owned records cannot return a duplicate receipt or trigger a rescan.

Keep published/rejected/blocked/pending lifecycle behavior. Orphan repair cannot attach a private or tenant Skill through the new canonical path. Repeated record-deletion races get one bounded create retry, then throw a retryable error. Bulk intake therefore returns a per-item error under HTTP200 instead of falsely settling an empty-ID pending result.

## Evidence

- Corrected regression baseline, Node22.23.2 on unmodified789f product source: 46 failing /12 passing new tests. Includes the actual bulk route with the actual upsert.
- Frozen candidate full suite, Node22.20: 6,044 passed /14 existing skips;638 files passed /4 skipped.
- Independent contract, Node22.23.2:229 passed /1 existing opt-in database skip. Twelve independent actual-source identity/scope/lifecycle probes also pass. Root independently ran the three changed test files:79 passed.
- Integrated full typecheck remains exit2:314 diagnostics, exactly matching retained T029 baseline after only position and exact checkout-prefix normalization. No new diagnostics; typecheck is not green.
- Initial full test attempt under ambient Node26 failed29 tests on environment contracts. Retained separately; no expectations were weakened for it.
- Frozen Worker build on explicit Node22.23.2 and queue-health build contract passed. Artifact/input hashes and the exact generated-counts version drift are recorded; the owned generated file was restored and all four source hashes remain unchanged.
- Independent reviewer report: `/Users/antonabyzov/.codex/visualizations/2026/09/28/01a0e6ab-6a15-7a40-923e-04ea3fd64426/cc-work-continuation/0874/t030-parity-review.md`.

## Boundaries and pending release proof

No manual intake submission, synthetic production replay, database repair, cache flush, backfill, checkpoint edit, reset, or crawler restart occurred. Crawler/scanner IDs stayed `0c47dfee…` /`2633c121…` during diagnostic reads. Source/CI review does not establish the live retry has recovered: merge, Worker rollout, and natural scheduled retry/readback remain parent-owned release gates. Historical loss/error counters must remain intact.

The earlier `pending-github-read.json` incorrectly derived `public:false` from a403 response. It is retained as a failed diagnostic, not visibility evidence. Corrected `pending-github-read-classified.json` records visibility unknown (`null`), rate-limit remaining0 and reset2026-09-28T22:53:07Z. No private/deleted repository conclusion or further GitHub retry follows from it. The first checkpoint diagnostic used the wrong key and the first DB query used the unmapped table name; both failed attempts are retained and superseded by explicitly corrected receipts.
