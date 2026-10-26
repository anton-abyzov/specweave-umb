# 1023 installed acceptance, October 23, 2026

Verdict: installed acceptance and the complete six-file verification passed on October 24, 2026. Earlier failed and partial receipts below are retained as history.

## Repaired-checkout verification

Fresh-context reviewer `/root/review_1023_final` returned PASS: six suites, 83 tests, 6/6 acceptance criteria and 4/4 tasks. No blocking gate remains. Earlier failure text remains quoted below; canonical verification reports now contain PASS.

The existing bound checkout remains clean at `e4c4704933bed7522c995733dd32d6cc28c654e6`. `pptxgenjs` resolves within its local dependency-repair artifact, so no installation or shared-clone mutation was needed. Registry stable `3.1.10` was invoked directly from `/Users/antonabyzov/.npm/_npx/f7e514fbb2d8cccc/node_modules/specweave/bin/specweave.js`, avoiding the prior npx resolution issue. The same six-file verification command passed with Node 22: all six acceptance criteria met and all four tasks done. Fresh final review follows before completion. No release, restart, browser automation or live database access occurred.

## Closure gate result, October 24, 2026

Fresh review is SHIP for acceptance, but completion is held by executable verification. The stable CLI was verified directly as `3.1.9` at `/Users/antonabyzov/.npm/_npx/6f70ac8eac696efd/node_modules/specweave/bin/specweave.js`; the earlier `npx` invocation unexpectedly resolved shared `3.1.7`, so prior statements that it executed the pinned version are corrected here.

The default umbrella verification was stopped by exact owned process IDs because it ran unrelated CLI repository tests. The stable CLI's supported `--cmd` override ran all six original 1023 app test files from the successor checkout. Five suites and 68 tests passed; `apps/server/src/mcp/toolkits/core.test.ts` could not load: `Error: Cannot find package 'pptxgenjs' imported from /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/feat-1009-cursor-settings-design-20261024/apps/server/src/design/export/pptx.ts`.

Full failed output was originally written to (these canonical reports now contain the successful rerun) `/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1023-add-approved-folders-while-project-work-runs/reports/verify.md` and `/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1023-add-approved-folders-while-project-work-runs/reports/verify.json`. Tasks are 4/4 done; increment remains active. No test was removed, dependency tree changed, or completion override used. Next step: the bound checkout owner restores its declared dependencies, then this owner reruns the same six-file verification and completes 1023 if green. No user-only decision remains.

## October 24, 2026 final binding receipt

Fresh-context reviewer `/root/review_1023_close` returned SHIP for 1023 acceptance: bound successor and delivered SHA match, prior AC-06 gate resolved, and 1009 installed acceptance correctly excluded. Completion remains conditional on a green verification report. No remaining user-only gate was identified.

Fresh supported thread read confirms successor `mcp:60e7dc29-bad8-46ca-9230-658631726438` successfully ran in bound worktree `/Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/feat-1009-cursor-settings-design-20261024`, branch `feat/1009-cursor-settings-design-20261024`. Read-only Git confirms current delivered head `e4c4704933bed7522c995733dd32d6cc28c654e6` (not asserted as its initial SHA). PR #664 is merged at `f55a7507e382b189f5e06f0e4c9bfdb333619333`. The previous preparation-only gate is resolved.

Fresh project read confirms revision `20`, approved app folder and registered repository unchanged. Bundle plist reads `1.0.75`; GitHub compare confirms merged #634 `4b7962d9fe678406c2e8df5f99e8341005ed4ece` is an ancestor of `v1.0.75`. PR #634 is merged, all applicable PR gates/security/typecheck checks succeeded; conditional unrelated jobs are skipped. The actual saved folder/repository and successful bound successor satisfy AC-06. This receipt does not claim an independent running-service binary hash or installed acceptance of #664.

No duplicate folder addition, repository mutation, 1009 work, merge, release or restart was performed. CLI checkout is clean. Stable CLI `3.1.9` is used session-locally because shared installed CLI is `3.1.7`. The prior schedule-disable receipt remains valid.

## October 24, 2026 continuation

Fresh `studio_project_read` confirms revision `20`: the approved app folder and repository `dbc4018e-bea3-46a1-826e-dd6ee149c9c7` are both saved, with the original project root preserved. No duplicate folder approval or repository mutation was attempted. The scheduled installed-bundle check reports `installed 1.0.75 contains 4b7962d9`; this is bundle/source-inclusion evidence, not an independent running-service source identity.

Supported `studio_thread_launch` created successor `mcp:60e7dc29-bad8-46ca-9230-658631726438` on inherited `codex` / `gpt-6-astra`, existing increment `1009`, branch `feat/1009-cursor-settings-design-20261024`, registered app repository, upstream `main`, `startFromOrigin: true`. Full original brief, research, ownership boundaries and evidence paths were transferred. The CLI-root parent ceases 1009 implementation and retains 1023 acceptance/closure.

Returned link: [1009 Cursor support and settings design](studio://thread/mcp%3A60e7dc29-bad8-46ca-9230-658631726438).

Readback is still `preparing` with `worktreePath: null`. Actual worktree path and initial SHA remain unconfirmed. T-03/T-04 remain open until preparation succeeds and binding is verified; dispatch alone is not AC-06 completion.

The exact recurring check `scheduled-task:9f5ee796-1796-4053-bbfe-dd7ae7e91aa2` was disabled through `update_scheduled_task`; readback returned `enabled: false`, `nextRunAt: null`. No release, restart, browser, credential or provider mutation occurred. Installed CLI `3.1.7` was older than registry stable `3.1.8`; board inspection used session-local `npx --yes specweave@3.1.8`.

## Current evidence

- `studio_environment_read`: M4 environment `4d73e481-1b03-4ee8-b4c1-87a448431538`, service `1.0.75`.
- `/Applications/SpecWithCode.app/Contents/Info.plist`: bundle `1.0.74`. This does not prove which bundle the running desktop process uses; service and disk bundle versions are separate evidence.
- `studio_project_read`: project `1332065e-795b-4f98-91c4-f114917e53f6`, revision `19`, approved additional folder `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave-studio`, repositories empty. Root remains `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave`.
- Live catalog still reports Cursor disabled, zero models, and generic executable unavailable. No enablement or authenticated request was made.
- Supported repository-only update at revision `19` was rejected without mutation. Exact error:

> Agents cannot change approved folders or repositories themselves; the user decides what agents here can reach. To add a folder, call studio_project_request with action add_folder and folder: the user approves it in a card. Repositories and removing a folder are the user's to change in project settings.

- Exact merged source `4b7962d9fe678406c2e8df5f99e8341005ed4ece` explicitly enforces repository equality in `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave-studio/apps/server/src/mcp/toolkits/project/handlers.ts`. The refusal is expected behavior, not another additive-folder failure.
- The previously owned checkout `/Users/antonabyzov/.specwithcode/m4/worktrees/fix-additive-folder-access` is absent. It was not recreated, restored or cleaned up.

## Fresh review

Native Astra reviewer `/root/review_1023_acceptance` verdict: HOLD. AC-06 explicitly requires a bound 1009 successor as well as installed folder approval. T-03 and T-04 remain open; the existing approved folder alone is insufficient. No verification or completion was asserted.

## Remaining gates

1. User-side Project settings Repositories registration of the verified existing checkout, URL `https://github.com/anton-abyzov/specwithcode-dev.git`, local path `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave-studio`. Chat approval already exists; the installed service requires the user-side settings mutation.
2. Read back registration, then perform the previously authorized app-native successor launch for 1009 and record its actual worktree, branch and initial SHA. No shell worktree or raw database fallback.
3. Record T-03/T-04 evidence, run verification, fresh review and completion. No weakening of AC-06.

## Ownership

1031 remains the separate Claude Code Ultra Code-only settings-consolidation review. Its spec is research/design only and reserves broader layout/consolidation decisions for user review. This worker does not mutate its reports, settings or product files. Cursor-specific research can continue independently; broad shared-settings implementation waits for scope reconciliation.

Complete screenshot sessions retains approved merges and 1.0.76 release. Its owner was notified for current release/install receipts. No release, restart, provider setup or new paid run was performed.


## Completion

`specweave complete 1023-add-approved-folders-while-project-work-runs --yes` exited 0; metadata readback confirms `completed`. Optional tracker hooks found zero user stories and closed zero items; JIRA and ADO emitted missing-credential warnings. No credentials were changed. These warnings did not block local completion.
