# Plan — 0312-repos-umbrella-badge

## Approach

1. Add `isUmbrellaManaged?: boolean` to `RepoInfo` in 3 places (types.ts, dashboard-server.ts, ReposPage.tsx)
2. In `scanRepositories()`, after scanning repos, check if the project root has `.specweave/`. If so, for each repo where `hasSpecweave` is false, set `isUmbrellaManaged: true`.
3. Update badge rendering in ReposPage.tsx for the 3-state badge.
4. Update KPI calculation to include umbrella-managed repos.

## Files to Modify

- `repositories/anton-abyzov/specweave/src/dashboard/types.ts` — RepoInfo interface
- `repositories/anton-abyzov/specweave/src/dashboard/server/dashboard-server.ts` — scanRepositories()
- `repositories/anton-abyzov/specweave/src/dashboard/client/src/pages/ReposPage.tsx` — Badge + KPI
- `repositories/anton-abyzov/specweave/src/dashboard/client/src/components/ui/Badge.tsx` — may need "info" variant
