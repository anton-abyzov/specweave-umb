# Plan — 0372: Trust Center scan findings

## Approach
Surface existing scan findings data (already stored in ScanResult.findings JSON) through the Trust Center UI. No schema or pipeline changes needed.

## Order of execution
1. T-001: FindingsList shared component (foundation for T-004, T-005)
2. T-002: Enrich blocklist check API
3. T-003: Enrich admin rejections API
4. T-004: BlockedSkillsTab UI changes (depends on T-001, T-002)
5. T-005: RejectedSkillsTab UI changes (depends on T-001, T-003)

## Key files
- `src/app/api/v1/blocklist/check/route.ts`
- `src/app/api/v1/admin/rejections/route.ts`
- `src/app/trust/BlockedSkillsTab.tsx`
- `src/app/trust/RejectedSkillsTab.tsx`
- `src/app/trust/FindingsList.tsx` (new)

## Risks
- Findings JSON can be up to 50 items — acceptable for expanded detail lazy-load
- Blocked skills without matching submissions show no findings — expected, only show admin reason
