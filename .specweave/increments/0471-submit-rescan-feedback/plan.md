# Plan: Submit page rescan feedback

## Overview

Single-file change to `src/app/submit/page.tsx` that threads the discovery `status` field through to the results UI, distinguishing new submissions from rescans of already-verified skills.

## Current State

1. `DiscoveredSkill` interface has only `name` and `path` -- drops the `status` field returned by the API.
2. `handleDiscover` maps `data.skills` into bare `{ name, path }` objects, discarding enrichment data.
3. `handleSubmitAll` builds `SubmissionResult` outcomes but has no concept of the original discovery status.
4. The summary line always reads `"{okCount} submitted"`.
5. All successfully submitted skills show "Track >>" regardless of origin.

## Changes

### C1: Extend DiscoveredSkill interface (AC-US1-01)

Add optional `status` field:

```ts
interface DiscoveredSkill {
  name: string;
  path: string;
  status?: "new" | "verified" | "pending" | "rejected";
}
```

In `handleDiscover`, preserve the field when mapping API response:

```ts
const skills: DiscoveredSkill[] = (data.skills ?? []).map((s: any) => ({
  name: s.name,
  path: s.path,
  status: s.status,
}));
```

### C2: Thread discovery status into SubmissionResult (AC-US1-03)

Add a `discoveryStatus` field to `SubmissionResult` so the results renderer knows which skills were rescans:

```ts
interface SubmissionResult {
  name: string;
  id?: string;
  status?: string;
  error?: string;
  discoveryStatus?: "new" | "verified" | "pending" | "rejected";
}
```

In `handleSubmitAll`, carry `discoveryStatus` from the input `DiscoveredSkill` into each outcome:

```ts
outcomes.push({ name: skill.name, id: sub.id, discoveryStatus: skill.status });
```

Apply the same for skipped/fallback outcomes so the field is always present.

### C3: Rescan-aware summary line (AC-US1-02, AC-US1-04)

Replace the current `{okCount} submitted` summary with logic that counts new vs rescan:

```
newCount    = results with id && discoveryStatus !== "verified"
rescanCount = results with id && discoveryStatus === "verified"
```

Display rules:
- All new (rescanCount=0): `"{newCount} submitted"` (preserves existing behavior)
- All rescans (newCount=0): `"{rescanCount} rescanning"`
- Mixed: `"{newCount} new, {rescanCount} rescanning"`
- Skipped/failed suffixes unchanged.

Skills with `discoveryStatus` of `"rejected"` or `"new"` or `undefined` all count as "new" (AC-US1-04).

### C4: Rescan link label (AC-US1-03)

In the results list, when a result has `id` and `discoveryStatus === "verified"`, render "Rescan >>" instead of "Track >>". Both link to `/submit/{id}`.

## Data Flow

```
API /discover -> data.skills[].status
       |
DiscoveredSkill.status (preserved in handleDiscover)
       |
handleSubmitAll -> SubmissionResult.discoveryStatus (threaded per skill)
       |
Results UI: summary line counts + per-row link label
```

## Risk Assessment

- **Low risk**: All changes confined to one file, no backend changes, no new dependencies.
- **Backward compatible**: If the API returns no `status` field, `discoveryStatus` is `undefined`, and the code falls back to existing "submitted" / "Track >>" behavior.

## No ADR Needed

UI label change threading an existing API field through to the view layer. No architectural decisions required.

## No Domain Skill Delegation

Single-file React change with no component extraction, no new patterns, no design system work. Direct implementation is appropriate.
