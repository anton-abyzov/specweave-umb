# Implementation Plan: Submission rejection detail visibility

> **Companion docs**: spec.md (acceptance criteria, user stories) · ADR-0720-01 (synthetic ScanResult decision)
>
> **Target repo**: `repositories/anton-abyzov/vskill-platform/`

## Overview

Submission status pages render a near-empty shell when `state ∈ {REJECTED, BLOCKED, TIER1_FAILED}` and `scanResult` is `null`. Two classes of rejections produce this state today:

1. **Non-scanner rejections** — blocklist short-circuits in `processSubmission` (`src/lib/queue/process-submission.ts:250`) and `finalize-scan` (`src/app/api/v1/internal/finalize-scan/route.ts:279`), recovery’s "no scan results" path (`src/lib/queue/recovery.ts:120`), admin reject/block, and bulk repo-block. None of these write a `ScanResult` row, so the page has nothing to render under "Scan Results" or "Detailed Findings."
2. **Missing UI fallback** — even when a terminal-state submission has zero scan rows by design (e.g. recovery rejection of a stuck submission), the UI offers no card explaining *why* the submission ended up rejected.

This plan introduces (a) a single helper `writeSyntheticScanResult()` invoked at every non-scanner rejection site and (b) a `RejectionReasonCard` UI fallback that renders from `blockInfo` or the latest terminal `stateHistory` entry when `scanResult` is null. Together they guarantee every terminal submission page surfaces an actionable reason. The change is additive — existing pages with real scan results render unchanged.

## Architecture

```mermaid
flowchart TD
    subgraph Triggers["Rejection triggers"]
        BL[processSubmission early blocklist]
        FS[finalize-scan early blocklist]
        RC[recovery resolveStuckTargetState no-scan]
        AR[admin reject route]
        AB[admin block route]
        RB[admin repo-block route]
    end

    BL --> WS
    FS --> WS
    RC --> WS
    AR --> WS
    AB --> WS
    RB --> WS

    WS["writeSyntheticScanResult(id, kind, reason, ...)"]

    WS --> KV[(KV scan:{id})]
    WS --> DB[(Postgres ScanResult row)]

    KV --> API
    DB --> API
    API["GET /api/v1/submissions/:id<br/>(getSubmissionFull → KV first, DB fallback)"]
    API --> Page["src/app/submit/[id]/page.tsx"]
    Page --> SR["Scan Results section<br/>(unchanged — renders synthetic too)"]
    Page --> RR["RejectionReasonCard<br/>(fallback when scanResult is null)"]
    Page --> FN["FindingsSection<br/>(picks scanResult.findings ?? blockInfo.findings)"]
```

**Data flow**: Rejection trigger → `writeSyntheticScanResult` → KV `scan:{id}` + DB `ScanResult` row → `getSubmissionFull` returns it via the existing path → `/api/v1/submissions/:id` JSON includes it as `scanResult` (no change to API shape) → page renders Scan Results + Findings exactly as it does for scanner-produced rows.

`RejectionReasonCard` is a pure-render fallback layer for the residual case where a terminal submission still has `scanResult === null` (legacy data, write failure). It pulls from `blockInfo` (already in the payload for BLOCKED) or the last terminal `stateHistory` entry message.

## File-Level Changes

| File | Change | Summary |
|---|---|---|
| `src/lib/submission/synthetic-scan-result.ts` | **NEW** | Exports `writeSyntheticScanResult()`; constructs a synthetic `StoredScanResult`, calls existing `storeScanResult()` (KV + DB via `persistScanResultToDb`). Idempotent — checks for existing rows before writing. |
| `src/lib/submission/__tests__/synthetic-scan-result.test.ts` | **NEW** | Vitest unit tests for the helper: shape correctness per `kind`, idempotency, severity/category mapping. |
| `src/lib/queue/process-submission.ts` | edit | After `updateState(id, "BLOCKED", ...)` at line ~250 (early blocklist), call `writeSyntheticScanResult(id, { kind: "blocklist", reason: "Skill is on the blocklist", evidenceUrls: blockEntry.evidenceUrls })`. |
| `src/app/api/v1/internal/finalize-scan/route.ts` | edit | After `updateState(id, "BLOCKED", ...)` at line ~279 (early blocklist), same call as above. |
| `src/lib/queue/recovery.ts` | edit | In `resolveStuckTargetState` no-scan branch (line ~120), call `writeSyntheticScanResult(id, { kind: "recovery-no-scan", reason: "Submission expired without scan results" })` before returning. |
| `src/app/api/v1/admin/submissions/[id]/reject/route.ts` | edit | After successful state transition, call `writeSyntheticScanResult(id, { kind: "admin-reject", reason, severity, patternName: "Admin rejection" })` — only when no prior `ScanResult` row exists. |
| `src/app/api/v1/admin/submissions/[id]/block/route.ts` | edit | Same pattern as reject route, `kind: "admin-block"`. |
| `src/app/api/v1/admin/repo-block/route.ts` | edit | After bulk `updateMany` to BLOCKED (line ~117), iterate `toBlock` and call `writeSyntheticScanResult` for each — only where no prior row exists. |
| `src/app/submit/[id]/RejectionReasonCard.tsx` | **NEW** | Co-located client component. Renders only when `state ∈ {REJECTED, BLOCKED, TIER1_FAILED}` AND `!scanResult`. Pulls from `blockInfo` (preferred) or last terminal `stateHistory[]` entry. |
| `src/app/submit/[id]/page.tsx` | edit | Import + render `<RejectionReasonCard data={data} />` between the BlockInfo block (line ~457) and the Scan Results block (line ~460). |
| `src/app/submit/[id]/__tests__/RejectionReasonCard.test.tsx` | **NEW** | Vitest + React Testing Library tests for the fallback component’s render conditions. |
| `tests/e2e/submission-rejection-visibility.spec.ts` | **NEW** | Playwright E2E covering the AC scenarios: blocklist-rejected submission, admin-rejected submission, recovery-rejected submission all surface findings + reason on the live page. |

## Component Design

### `writeSyntheticScanResult(submissionId, opts)`

```ts
export type SyntheticScanKind =
  | "blocklist"
  | "recovery-no-scan"
  | "admin-reject"
  | "admin-block"
  | "repo-block";

export interface SyntheticScanOptions {
  kind: SyntheticScanKind;
  reason: string;
  evidenceUrls?: string[];
  severity?: "critical" | "high" | "medium";
  patternName?: string;
  concerns?: string[];
  commitSha?: string | null;
  /** Skip if a real or synthetic ScanResult already exists. Default true. */
  skipIfExists?: boolean;
}

export async function writeSyntheticScanResult(
  submissionId: string,
  opts: SyntheticScanOptions,
): Promise<{ written: boolean; reason?: "already-exists" | "missing-submission" }>;
```

Internally it builds a `StoredScanResult` with `tier: 1`, `verdict: "FAIL"`, `score: 0`, `patternsChecked: 0`, `durationMs: 0`, exactly one `StoredScanFinding` carrying the rejection metadata, and the right severity counter set to `1`. Then calls existing `storeScanResult(id, result)` from `kv-store.ts` so KV + DB writes share the same code path the scanner uses.

**Kind defaults table**:

| `kind` | severity | patternName | category | UI label |
|---|---|---|---|---|
| `blocklist` | critical | "Blocklist match" | "policy" | Skill is on the blocklist |
| `recovery-no-scan` | high | "Submission expired" | "lifecycle" | Recovery rejected — no scan results |
| `admin-reject` | high (overridable) | "Admin rejection" | "manual" | Admin rejection |
| `admin-block` | critical (overridable) | "Admin block" | "manual" | Admin block |
| `repo-block` | critical (overridable) | "Repository blocked" | "policy" | Repository-wide block |

**Synthetic finding shape** — satisfies `StoredScanFinding`:

```ts
{
  patternId: `synthetic:${kind}`,
  patternName: opts.patternName ?? defaultsByKind[kind].patternName,
  severity: opts.severity ?? defaultsByKind[kind].severity,
  category: defaultsByKind[kind].category,
  match: opts.reason,
  lineNumber: 0,
  context: (opts.evidenceUrls ?? []).join("\n"),
  file: "SKILL.md",
}
```

`lineNumber: 0` is intentional — the existing FindingsSection groups by file+line and renders 0 as "no specific line", which is correct for synthetic findings. `file: "SKILL.md"` keeps grouping consistent with real findings.

### `RejectionReasonCard` (fallback only)

```tsx
interface Props {
  state: string;
  scanResult: SubmissionResponse["scanResult"];
  blockInfo: SubmissionResponse["blockInfo"];
  stateHistory: SubmissionResponse["stateHistory"];
}
```

Render rules:
1. If `scanResult` is non-null → render nothing (the existing Scan Results block handles it).
2. If `state` is not in `{REJECTED, BLOCKED, TIER1_FAILED}` → render nothing.
3. If `blockInfo` is non-null → already covered by existing BlockInfo block (line 399 in page.tsx) — render nothing.
4. Otherwise: find the most recent `stateHistory[]` entry whose `state` is in the terminal set; render its `message` as the rejection reason in a card visually consistent with the BlockInfo card.

The card matches the styling of the existing BlockInfo block (border, padding, mono font) so the page never looks half-styled in the fallback path.

## Key Decisions

1. **Single helper, called at every rejection site.** Centralises severity/category mapping and KV+DB write ordering. Alternative considered: per-site inline writes — rejected because it scatters the synthetic-shape contract and risks drift between sites.

2. **Reuse `storeScanResult()` from kv-store.ts.** It already handles KV+DB dual-write, TTL, and best-effort DB persistence. No need to introduce a parallel write path.

3. **Idempotency via `skipIfExists` defaulting to true.** Implementation: query `db.scanResult.findFirst({ where: { submissionId } })` before writing. Avoids duplicating findings when admin paths re-run or when blocklist trips after a real scan already produced findings (preserves transparency — admin override of a real scan keeps the original findings visible). The `repo-block` bulk path uses the same flag so retries on idempotent re-calls don’t duplicate.

4. **Synthetic finding mimics scanner output** rather than introducing a new "rejectionReason" field. Why: the page’s `FindingsSection` (line 499) already supports both real findings and `blockInfo.findings`. Reusing `ScanFinding` shape means zero changes to that component. The trade-off — verdict is `FAIL` even for admin actions — is acceptable because the `patternName` ("Admin rejection") makes the human-readable distinction obvious.

5. **`tier: 1, score: 0, patternsChecked: 0`** on synthetic rows. Distinguishes them in DB queries (`patternsChecked === 0` is the cheap discriminator if ever needed for analytics). `durationMs: 0` already meaningfully signals "no scan ran" via the existing UI guard (`scanResult.durationMs > 0` controls the duration display at page.tsx:474).

6. **UI fallback is render-only, no flag.** Backwards-compatible by construction: triggers only when `scanResult` is null. Pages with real or synthetic scan rows render exactly as today. No feature flag, no migration.

7. **Co-located component** at `src/app/submit/[id]/RejectionReasonCard.tsx`. Clean isolation, easy to test, keeps `page.tsx` from growing further. Alternative — inline section in page.tsx — rejected because page.tsx is already 643 lines and approaching the project’s 1500-line limit.

8. **No backfill of legacy submissions.** Legacy REJECTED/BLOCKED submissions without scan rows continue to rely on the UI fallback (`RejectionReasonCard`) to surface their state-history message. Going-forward writes solve the structural problem; backfill is out of scope (tracked as follow-up if analytics need parity).

## Test Strategy

### Unit — Vitest

- `synthetic-scan-result.test.ts`:
  - One test per `kind` validating finding shape, severity counts, and metadata mapping.
  - Idempotency: calling twice with `skipIfExists: true` writes once.
  - Override behaviour: admin paths can supply custom severity/patternName.
  - Missing submission: returns `{ written: false, reason: "missing-submission" }` and does not throw.
- `RejectionReasonCard.test.tsx`:
  - Renders nothing when `scanResult` is non-null.
  - Renders nothing for non-terminal states.
  - Renders `blockInfo.reason` is **not** its job — verify it returns null (BlockInfo block owns that case).
  - Renders the latest terminal `stateHistory[]` message when `scanResult` and `blockInfo` are both null.

### E2E — Playwright

`tests/e2e/submission-rejection-visibility.spec.ts` exercises the full pipeline:
- Submit a known-blocklisted skill → page shows synthetic finding ("Blocklist match") and reason text.
- Admin-reject a submission via API → reload page → finding labeled "Admin rejection" appears.
- Recovery rejection (simulate via direct DB state) → page shows "Submission expired" finding.
- Legacy submission with no scan + no blocklist → `RejectionReasonCard` fallback renders the state-history message.

Coverage gate: 90% (per increment metadata).

## Rollout & Migration

- **No flag, no migration.** Additive only.
- **Existing pages**: unaffected (all rendering paths are conditional on the same data shape they’ve always consumed).
- **Existing data**: legacy REJECTED/BLOCKED submissions without scan rows continue to render via the new `RejectionReasonCard` fallback — they get a non-empty page even without a backfill.
- **Deployment**: standard Cloudflare Workers deploy via `wrangler`. No DB migration needed (`ScanResult` schema unchanged).
- **Rollback**: revert the PR — every change is additive, no schema or contract changes.

## ADR Reference

Decision recorded in **`.specweave/docs/internal/architecture/adr/0720-01-synthetic-scan-result-for-non-scanner-rejections.md`**. Captures the rationale for synthesising a `ScanResult` row rather than introducing a new `rejectionReason` table or extending the `Submission` model.

## Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Synthetic rows pollute scanner-stats queries (`@@index([tier, llmModel, createdAt])`). | Synthetic rows have `llmModel === null` and `patternsChecked === 0` — analytics queries that already filter on `tier === 2` or `llmModel IS NOT NULL` are unaffected. Tier-1 stats queries should add `patternsChecked > 0` filter when they care about real scans (follow-up, not blocking). |
| Admin-rejected submission with a prior real scan loses the real findings. | `skipIfExists: true` default — admin reject/block routes never overwrite an existing row. The original scan’s findings remain visible. |
| Duplicate synthetic rows on retry. | Idempotency check + `skipIfExists` flag. The `repo-block` bulk path uses the same guard. |
| KV write succeeds, DB write fails. | Existing `storeScanResult()` already wraps DB write in `.catch(logDbPersistError("scan", id))` — same best-effort semantics as scanner writes. Page falls back to KV until TTL expires, then to DB (and uses the UI fallback if DB row is also missing). |
