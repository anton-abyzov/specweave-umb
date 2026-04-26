---
increment: 0778-platform-pipeline-degraded-banner
title: "Studio Bell — Surface Platform Pipeline Degraded State"
generated: 2026-04-26
source: hand-written
version: "1.0"
status: active
---

# Quality Contract

## Functional Correctness

- All ACs in `spec.md` map to ≥1 test in `tasks.md` (red/green pair).
- `npx vitest run` green for new + touched suites (`api-platform-health`, `usePlatformHealth`, `UpdateBell-degraded`, `UpdateBell`).
- The healthy path of UpdateBell renders identically to today's behavior (regression test in T-007 gates this).

## Code Quality

- No `any` in new TypeScript.
- Reuse `useSWR` (no new SWR primitive).
- Reuse `var(--color-own)` token (no inline hex).
- `reason` string composed by a small helper; never includes raw upstream JSON.

## Cross-Cutting Concerns

- **Performance**: server cache 60s; client SWR 60s; ≤1 extra GET/min/session.
- **Reliability**: 1500ms upstream timeout; safe fallback shape on any error; endpoint NEVER throws to client.
- **Accessibility**: banner `role="status"` + `aria-live="polite"`; bell `aria-label` updates with state.
- **Security**: no user input on the wire; hardcoded upstream URLs; no SSRF surface.

## Closure Gates

- [ ] vitest run clean for affected suites.
- [ ] `tsc --noEmit` clean.
- [ ] `sw:code-reviewer` produces no critical/high/medium findings.
- [ ] `sw:grill` writes `grill-report.json`.
- [ ] `sw:judge-llm` writes report (waived if consent denied).
- [ ] `specweave sync-living-docs 0778-...` exits 0.

## Manual Verification (User Gate)

The user MUST manually verify:

1. With platform healthy (`/api/v1/submissions/stats.degraded` is false), bell + dropdown render exactly as before.
2. With platform degraded (today's actual state — `degraded:true`, oldestActive 31d), launch studio:
   - Bell glyph is amber.
   - Hover tooltip reads "Update checks paused — verified-skill.com crawler is degraded. Your submissions are queued."
   - Click bell → amber banner above the list reads "Platform crawler degraded" + a non-empty reason.
3. Refresh — stays amber until the platform self-heals.
