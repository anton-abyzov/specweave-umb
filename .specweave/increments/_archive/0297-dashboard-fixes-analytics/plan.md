# Plan: 0297 Dashboard Bug Fixes & Analytics

## Phase 1: Critical Bug Fixes (US-001, US-002)
1. Create `ErrorBoundary` React component
2. Wrap `App.tsx` routes with ErrorBoundary
3. Fix navigate to preserve project query params in IncrementsPage
4. Create reusable `useProjectNavigate` hook for consistent navigation
5. Rebuild dashboard client

## Phase 2: Analytics Tracking Verification (US-003)
1. Audit where `trackCommand`/`trackSkill`/`trackAgent` are called
2. Verify implicit calls (team-lead → do) are tracked
3. Wire tracking into any missing execution paths
4. Test by running commands and checking events.jsonl

## Phase 3: Documentation (US-004, US-005)
1. Add Dashboard section to README with feature descriptions
2. Add analytics guide to public docs
3. Update YouTube tutorial script

## Key Files
- `src/dashboard/client/src/App.tsx` - Route wrapping
- `src/dashboard/client/src/components/ui/ErrorBoundary.tsx` - New
- `src/dashboard/client/src/pages/IncrementsPage.tsx` - Navigate fix
- `src/dashboard/client/src/hooks/useProjectNavigate.ts` - New
- `src/core/analytics/analytics-collector.ts` - Tracking audit
- `docs-site/docs/` - Public docs
- `docs-site/docs/guides/youtube-tutorial-script.md` - YouTube script
