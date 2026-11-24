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

PR781 head27ab536f69dc0e06877c6518a5d5fc6bfdce1b13. Fresh-context review ship. Focused Node22 tests:76 total (74 sidebar/aggregate/observation plus2 fleet), observation coverage100% of statements/branches/functions/lines. Production web build also passed with Node22.20 explicitly selected for both launcher and Vite subprocess (saved web-build-node22.log). Standalone web typecheck reports existing TS2883 in `newThreadWorkspaceDefault.ts`, with no changed-file diagnostic.

Headless browser uses real ProjectRow and aggregate with isolated fixtures. Four cases (1280/390 widths, light/dark),96 transitions, zero label movement, count visible during hover, actual offline/cached/synchronizing/unrepresented follower coverage remains explicit. Saved screenshot and receipt alongside this report.

## Deployment investigation

Existing public1.0.88 failed to install on M4 (running1.0.86). Receipt error: preparation exceeded available restart time; old service retained. Timings showed roughly261s initial observation,254s prestate check,257s final check. Current main includes the independently owned update hold/read fixes; use the release entrypoint and verify actual installed versions. This work does not claim the previous release was deployed.

## Release-blocker isolation

Concurrent release1.0.89 failed twice in the existing projectWorkspaceModel attention-scope test: its15-second limit expired importing useProjectAttention (React, fleet and connection state) just to call pure helpers. Only completed increment1040 previously owned those helper/test files; no active claim was found. The failed release checkout was preserved untouched.

Extracted unchanged AttentionProjectMember, projectAttentionRoots and expandAttentionProjects into projectAttentionScope.ts; the hook preserves its public exports; the two existing dynamic test imports point at the pure module. All assertions remain intact. Final commit79e5bdbc34a3ed914386fa3b300d17cb6872715a.182 focused tests and Node22 production build pass. Fresh review ship, independently65 scope/model tests passed. Full web suite and final-head CI are separate running checks.

## Full web suite

Node22 full web run:948/949 files and11731/11732 tests passed. Only unrelated Open VSX VSIX import test timed out at15seconds while build/fixture work ran concurrently. Attention scope checks passed. Unchanged isolated Open VSX file rerun:10/10 passed in4.36seconds. Neither its source nor assertions nor timeout were changed. Final headless96-transition check also passed after extraction. This is a first-run timeout plus successful unchanged retry, not a clean first run. Final-head hosted CI and release gates remain required.

## Base integration repair

Hosted Windows server-2 on79e5bdbc failed the pre-existing MCP fan-out projection wait (224 other server files passed). Main had already mergedPR779, whose unchanged Windows server-2 check passed. Brought main into the owned branch, preserving the failed run and all tests. New head9e1e1b0cc00d47fd26034a4c65c3d67bd66b76fb contains the existing non-Git fixture repair; PR diff remains only ten badge/scope files. No failed check was ignored or marked successful.184 focused cases including the MCP integration now pass, and Node22 production web build passes. Final-head hosted CI restarted.
