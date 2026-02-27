# Implementation Plan: Consistent Rejection Handling

## Overview

Three workstreams: (1) extend the platform API to expose rejection status, (2) wire CLI to check and enforce rejection blocks, (3) add Trust Center UI for rejected skills.

## Architecture

### API Extension: `GET /api/v1/blocklist/check`

**File**: `src/app/api/v1/blocklist/check/route.ts`

After the existing `BlocklistEntry` query, add a `Submission.findFirst` query:

```typescript
let rejection = null;
if (name) {
  const sub = await db.submission.findFirst({
    where: {
      skillName: name,
      state: { in: ["REJECTED", "TIER1_FAILED", "DEQUEUED"] },
    },
    orderBy: { updatedAt: "desc" },
    select: {
      skillName: true, state: true, updatedAt: true,
      scanResults: { orderBy: { createdAt: "desc" }, take: 1,
        select: { score: true, tier: true, verdict: true } },
    },
  });
  if (sub) {
    const scan = sub.scanResults[0];
    rejection = {
      skillName: sub.skillName,
      state: sub.state,
      reason: `Verification failed (${sub.state})`,
      score: scan?.score ?? null,
      rejectedAt: sub.updatedAt.toISOString(),
    };
  }
}
return NextResponse.json({
  blocked: !!entry, ...(entry ? { entry } : {}),
  rejected: !!rejection, ...(rejection ? { rejection } : {}),
});
```

### New API: `GET /api/v1/rejections`

**File (new)**: `src/app/api/v1/rejections/route.ts`

Returns paginated list of rejected submissions for the Trust Center tab. Query: `Submission.findMany` with `state IN (REJECTED, TIER1_FAILED, DEQUEUED)`, includes latest `ScanResult` per submission.

### CLI: `checkInstallSafety()`

**File**: `vskill/src/blocklist/blocklist.ts`

New exported function. Single HTTP call to extended API. Graceful fallback to local `checkBlocklist()` on error.

**File**: `vskill/src/blocklist/types.ts`

New types:
```typescript
export interface RejectionInfo {
  skillName: string; state: string; reason: string;
  score: number | null; rejectedAt: string;
}
export interface InstallSafetyResult {
  blocked: boolean; entry?: BlocklistEntry;
  rejected: boolean; rejection?: RejectionInfo;
}
```

### CLI: Install Path Wiring

**File**: `vskill/src/commands/add.ts`

Replace all 5 `checkBlocklist()` calls with `checkInstallSafety()`. Add `printRejectedError()` and `printRejectedWarning()` functions. Pattern at each site:

```typescript
const safety = await checkInstallSafety(skillName);
if (safety.blocked && !opts.force) { printBlockedError(safety.entry!); exit; }
if (safety.blocked && opts.force) { printBlockedWarning(safety.entry!); }
if (safety.rejected && !opts.force) { printRejectedError(safety.rejection!); exit; }
if (safety.rejected && opts.force) { printRejectedWarning(safety.rejection!); }
```

### Trust Center: Rejected Skills Tab

**File**: `src/app/trust/page.tsx` — add third tab to TABS array
**File (new)**: `src/app/trust/RejectedSkillsTab.tsx` — mirrors `BlockedSkillsTab` pattern

### Trust Center: Cross-Reference Badge

**File**: `src/app/trust/BlockedSkillsTab.tsx` — in ExpandedDetail, lazy-fetch rejection status when row expands

## Files Changed

| File | Change | Risk |
|------|--------|------|
| `vskill-platform/src/app/api/v1/blocklist/check/route.ts` | Add Submission rejection query | Low |
| `vskill-platform/src/app/api/v1/rejections/route.ts` | New endpoint | Low |
| `vskill-platform/src/app/trust/page.tsx` | Add third tab | Low |
| `vskill-platform/src/app/trust/RejectedSkillsTab.tsx` | New component | Medium |
| `vskill-platform/src/app/trust/BlockedSkillsTab.tsx` | Rejection cross-reference | Low |
| `vskill/src/blocklist/types.ts` | New types | Low |
| `vskill/src/blocklist/blocklist.ts` | New `checkInstallSafety()` | Medium |
| `vskill/src/commands/add.ts` | Replace 5 call sites | Medium |

## Implementation Phases

### Phase 1: Platform API (US-001)
Extend `blocklist/check` endpoint + new `rejections` endpoint. Foundation for everything else.

### Phase 2: CLI (US-002)
Types, `checkInstallSafety()`, wire into all install paths. Can test against deployed Phase 1.

### Phase 3: Trust Center UI (US-003, US-004)
New tab + cross-reference badge. Independent of CLI work.

## Testing Strategy

- **Platform**: Test extended API returns rejection data alongside blocklist data
- **CLI**: Test `checkInstallSafety()` with mock API responses. Test graceful fallback. Test add command rejection blocking.
- **UI**: Component tests for RejectedSkillsTab rendering and search
