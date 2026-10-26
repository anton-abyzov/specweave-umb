# Project badge investigation

## Findings

- `apps/web/src/studio/fleet.ts`, old `projectRemoteAttentionAtom`: both fleet and worker `waiting` flags were interpreted as incomplete coverage, even when AsyncResult retained a successful value. Every10-second background refresh could alternate number/partial badge.
- `remoteWorkersAtom` read the entire fleet result. Every fleet poll changed that dependency and could restart per-project worker reads, in addition to their own10-second refresh schedule.
- `SidebarProjectList.tsx` concatenated a plus for partial counts, or substituted a question mark when none were known. This mixed transport freshness and user-action count into one changing text run.
- `shell.css` explicitly hid `.sws-side-row-end` on hover/menu focus. Pointer movement therefore looked like another badge blink, independently of polling.

## Changes

Successful retained observations remain complete during normal refresh. Failed/null/initial observations remain incomplete. Worker readers depend on primitive capability; unchanged fleet transport status causes no dependent re-read. Live numeric counts contain only digits. Incomplete coverage has a static neutral dot with an accessible label and title. Badge and menu have independent reserved spaces; hover/menu focus preserves the count and label geometry.

No artificial delays, count caching, animations or changes to the action classifier. Real count changes and outages remain visible. Shared live stores and providers were untouched by tests.

## Evidence

PR781 head27ab536f69dc0e06877c6518a5d5fc6bfdce1b13. Fresh-context review ship. Focused Node22 tests:76 total (74 sidebar/aggregate/observation plus2 fleet), observation coverage100% of statements/branches/functions/lines. Production web build succeeded through the repository Vite+ runtime; Node22 launches tooling, which selects its separately scoped Node26 build runtime. Standalone web typecheck reports existing TS2883 in `newThreadWorkspaceDefault.ts`, with no changed-file diagnostic.

Headless browser uses real ProjectRow and aggregate with isolated fixtures. Four cases (1280/390 widths, light/dark),96 transitions, zero label movement, count visible during hover, actual offline/cached/synchronizing/unrepresented follower coverage remains explicit. Saved screenshot and receipt alongside this report.

## Deployment investigation

Existing public1.0.88 failed to install on M4 (running1.0.86). Receipt error: preparation exceeded available restart time; old service retained. Timings showed roughly261s initial observation,254s prestate check,257s final check. Current main includes the independently owned update hold/read fixes; use the release entrypoint and verify actual installed versions. This work does not claim the previous release was deployed.
