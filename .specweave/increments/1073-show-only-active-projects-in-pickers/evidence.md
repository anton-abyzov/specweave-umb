# 1073 delivery evidence

October 25, 2026. Source head: `20d0eee6c28865976eafea559f435d128879eab9`. Worktree: `/Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/feat-active-only-project-pickers`. Branch: `feat/active-only-project-pickers`. Base: `b323adb74913af51a4ce710f6e4e558b335ebf1b`.

## Verified locally

- 258 focused tests across 17 picker/shared/mobile files pass with Node 22.20.0. Receipt: `/Users/antonabyzov/.specwithcode/m4/evidence/1073-active-pickers/focused-tests.log`.
- `node node_modules/typescript/bin/tsc --noEmit --project apps/web/tsconfig.json` exits 0. Receipt: `/Users/antonabyzov/.specwithcode/m4/evidence/1073-active-pickers/web-tsc.log`. A pre-existing Effect schema-decoder suggestion in the capacity fixture is emitted; it is not a failure.
- 24 headless Code Review interactions pass at 1280×844 and 390×844 in light/dark. Active choices retain three distinct same-remote checkouts with machine/path labels. Archived, automated, scratch and personal selected contexts remain disabled; alternate selections route to the exact environment/project identity. No horizontal overflow or page errors. Receipts: `/Users/antonabyzov/.specwithcode/m4/evidence/1073-active-pickers/headless-checks.json`, `/Users/antonabyzov/.specwithcode/m4/evidence/1073-active-pickers/headless-check.log`. Screenshots are the named files in that JSON.
- The source fixture uses the actual Code Review compact menu imported by the route and the actual narrow filters menu, with only synthetic project data and an icon-asset atom stub. No live app state, provider turn or credentials. Initial built-in preview ran headlessly; its automation host became unavailable with an explicit shell fallback message. The standalone verifier launches with `headless: true`, sets `PWDEBUG=0`, `PLAYWRIGHT_HTML_OPEN=never` and writes evidence to files. No HTML reporter or headed browser was used.
- `git diff --check` passes. No full builds, broad tests or toolchain installations. Existing dependency links resolve to worktree packages.

## Exact commands

Runtime: `/Users/antonabyzov/.nvm/versions/node/v22.20.0/bin/node`.

Focused test inputs: `/Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/feat-active-only-project-pickers/packages/client-runtime/src/state/projectPicker.test.ts`, `/Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/feat-active-only-project-pickers/apps/web/src/studio/projectListVisibility.test.ts`, `/Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/feat-active-only-project-pickers/apps/web/src/components/pullRequest/pullRequestProjectFilter.logic.test.ts`, `/Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/feat-active-only-project-pickers/apps/web/src/components/pullRequest/PullRequestListFilters.test.tsx`, `/Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/feat-active-only-project-pickers/apps/web/src/components/chat/DraftHeroHeadline.test.tsx`, `/Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/feat-active-only-project-pickers/apps/web/src/components/chat/DraftMachinePicker.test.tsx`, `/Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/feat-active-only-project-pickers/apps/web/src/components/threadMove.logic.test.ts`, `/Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/feat-active-only-project-pickers/apps/web/src/components/settings/settingsScopeAxis.test.ts`, `/Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/feat-active-only-project-pickers/apps/web/src/components/settings/MessagingSettings.test.tsx`, `/Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/feat-active-only-project-pickers/apps/web/src/components/Sidebar.projectScopeMenu.test.ts`, `/Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/feat-active-only-project-pickers/apps/web/src/components/studio/StudioOverview.test.tsx`, `/Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/feat-active-only-project-pickers/apps/web/src/components/CommandPalette.logic.test.ts`, `/Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/feat-active-only-project-pickers/apps/mobile/src/features/home/homeThreadList.test.ts`, `/Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/feat-active-only-project-pickers/apps/mobile/src/features/settings/settings-environment-filter.logic.test.ts`, `/Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/feat-active-only-project-pickers/apps/mobile/src/features/settings/settings-environment-filter.test.ts`, `/Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/feat-active-only-project-pickers/apps/mobile/src/features/settings/scheduledTaskDraft.test.ts`. Run with `node node_modules/vite-plus/bin/vp test run` followed by those inputs from this worktree, with `PWDEBUG=0 PLAYWRIGHT_HTML_OPEN=never`.

Fixture server: `node node_modules/vite-plus/bin/vp dev --config apps/web/tests/active-project-pickers/vite.config.ts`. This owned server listens on 5873. Server log: `/Users/antonabyzov/.specwithcode/m4/evidence/1073-active-pickers/fixture-server.log`.

Browser verifier: `node apps/web/tests/active-project-pickers/verify.mjs /Users/antonabyzov/.specwithcode/m4/evidence/1073-active-pickers`. Existing `PLAYWRIGHT_MODULE` is `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave-studio/node_modules/.pnpm/playwright-core@1.60.0/node_modules/playwright-core`; `STUDIO_TEST_CHROMIUM` is `/Users/antonabyzov/.specwithcode/m4/tools/chrome-headless-shell/mac-arm64/154.0.8037.92/chrome-headless-shell`.

## Remaining delivery gates

Fresh exact-head adversarial review, pushed PR CI including Platform tests summary, coordinated merge and the sole Schedule Mac and mobile release path. After release: verify installed bundle/service/assets, run actual installed headless Code Review dropdown behavior with supported app access, then verify/review/complete 1073. Current installed 1.0.76 is pre-fix and not claimed as acceptance.

## Verify and close 1073

T-05 remains open until installed acceptance. This record distinguishes source tests, CI, merge, release and installed behavior.

## Review repair and current source gate

PR: https://github.com/anton-abyzov/specwithcode-dev/pull/710. Current head: `6932fc3fc5f1f30004ad4fb4b50f398a83731a10`.

Fresh review at `8523e1732221e5fdd2a52c16ce1585ed46eb5f5b` returned FIX: an archived matching native destination could expose a machine then fall through to an unrelated active project; an excluded persisted native project left Start enabled but ineffective. Both were repaired in `6932fc3fc5f1f30004ad4fb4b50f398a83731a10`. Machine options and execution now use the same eligible matching catalog and refuse unmatched destinations without moving the draft. The native composer names unavailable context, explains why and disables Start. Seventeen native selection tests include the exact archived/automated matching App plus unrelated Billing reproduction.

The unscoped `specweave verify` unexpectedly inherited the umbrella broad-suite command; its exact owned process tree was stopped. No other session was stopped. The corrected scoped verify used `--cmd` overrides for the same 17 focused test files and apps/web tsc. Both commands exited 0. Overall verification remains exit 1 because ACs/tasks are deliberately open for review, CI and installed acceptance, not because source checks failed. Receipt: `/Users/antonabyzov/.specwithcode/m4/evidence/1073-active-pickers/increment-verify.log`. Future closure must retain those `--cmd` overrides rather than run the umbrella suite.

The normal first commit hook made and removed its own backup stash before the prohibition was detected. Subsequent repair commit used `VP_GIT_HOOKS=0` after explicitly formatting the four changed files; no stash command was issued manually and no other worktree's dirty work was touched.

## Round 2 repair and final candidate

Current exact head: `627a3dc962db8b705345c3a90e2768911ff91b87`. Fresh R2 at `6932fc3fc5f1f30004ad4fb4b50f398a83731a10` returned FIX. The repaired native dispatcher now resolves the entire eligible target catalog so an authoritative repository match outranks earlier weak basename/title matches. Code Review decorates active choices and the retained inactive selection together, so same-name current context has machine/path identity and the exact decorated object remains disabled in both controls. Both reproductions have focused regressions; the browser matrix also now covers the inactive same-name checkout.

Current receipts: 253 focused tests in17files pass in `/Users/antonabyzov/.specwithcode/m4/evidence/1073-active-pickers/focused-tests.log`; 32 targeted R2 regression tests pass in `/Users/antonabyzov/.specwithcode/m4/evidence/1073-active-pickers/r2-review-tests.log`; apps/web tsc exits0 in `/Users/antonabyzov/.specwithcode/m4/evidence/1073-active-pickers/web-tsc.log`; 24 headless responsive checks pass in `/Users/antonabyzov/.specwithcode/m4/evidence/1073-active-pickers/headless-checks.json`. The scoped SpecWeave verification report predates the last two added regression cases; its source commands passed but open delivery tasks/ACs correctly prevented increment closure.

Fresh R3 review record requested at `/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1073-show-only-active-projects-in-pickers/reports/review-627a3dc962-r3.md`. CI and Platform tests summary must be green at this exact head before handoff for merge. Sole release path remains Schedule Mac and mobile release; actual installed headless acceptance remains assigned here after release.

## T-08 resumed after server restart

Current head: `20d0eee6c28865976eafea559f435d128879eab9`, PR https://github.com/anton-abyzov/specwithcode-dev/pull/710. R3's high explicit-deleted-draft retarget and medium resumed-deleted-draft/routine-default findings are repaired. Missing explicit native keys resolve unavailable rather than selecting another sole scope. The last live project is retained only for matching-key display context; missing-catalog feedback blocks new Start/build. Scoped routine defaults retain the selected inactive member, and only All projects uses the first eligible default.

The server restart cancelled the old private fixture process and interrupted its headless run. Resumed only the existing owned T-08 worktree and claim; no takeover. Recreated the fixture server on owned loopback5873, reran all24headless cases successfully, and captured with animations disabled. Prior258focused tests remained file-backed and passed; a fresh apps/web tsc exited0 after resumption. The installed CLI now reports3.1.9 versus registry stable3.1.10; the session-local3.1.10 invocation remains in use. No shared installation was changed.

R4 fresh exact-head source review is requested at `/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1073-show-only-active-projects-in-pickers/reports/review-20d0eee6c2-r4.md`. Merge readiness still requires SHIP naming this head plus required CI including Platform tests summary. The completion owner retains merge and the sole release path. No release dispatch from this thread. After release, this writer runs actual installed headless Code Review acceptance and closes1073 when its gates pass.

## CI type repair at 5b4726daed

PR #710 head `5b4726daedba9f2632ad260fbb0a77f963280e44` corrects all 15 newly diagnosed type errors from run `40171293927`. Native test fixtures now spread the complete contract defaults; shared NodeNext imports use `.js` extensions. No baseline changes.

Focused checks: 258 tests across 17 files passed; apps/web tsc exited 0. Logs: `/Users/antonabyzov/.specwithcode/m4/evidence/1073-active-pickers/ci-fix-focused-tests.log` and `/Users/antonabyzov/.specwithcode/m4/evidence/1073-active-pickers/ci-fix-web-tsc.log`. R4 exact-head review started in a fresh subagent; required CI, coordinated merge/release and installed Code Review acceptance remain open. Prior R4 on `20d0eee6c2` was cancelled by restart and produced no review.

## Merged source and machine-identity follow-up

PR #710 merged as `d582aa8fb6147f3f8c007a8d3ca75d51c258619d` from `5b4726daedba9f2632ad260fbb0a77f963280e44`. All exact-head CI passed, including typecheck and Platform tests summary. R4 source SHIP record: `/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1073-show-only-active-projects-in-pickers/reports/review-5b4726daed-r4.md`.

R4 retained a medium native machine-identity/recovery finding after deletion of the selected machine's final project. Follow-up PR #715 at `a10974456f93dcbfc74bf430a265305cf040c96d`, branch `fix/native-draft-machine-context`, preserves explicit machine context and uses its saved label; a sole alternative remains selectable. 83 tests in four focused files and apps/web tsc passed. Evidence: `/Users/antonabyzov/.specwithcode/m4/evidence/1073-active-pickers/r4-medium-tests.log` and `/Users/antonabyzov/.specwithcode/m4/evidence/1073-active-pickers/r4-medium-web-tsc.log`. Fresh R5 and exact-head CI are pending.

Release owner now targets 1.0.81 because 1.0.79 and 1.0.80 were already published. Installed app still reports 1.0.76 at this readback; 1.0.81 release does not yet exist. No release was dispatched by this implementation thread. Actual installed headless Code Review acceptance and Verify and close 1073 remain open.

## Follow-up exact-head review and required CI

R5 source SHIP, zero findings, at `a10974456f93dcbfc74bf430a265305cf040c96d`: `/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1073-show-only-active-projects-in-pickers/reports/review-a10974456f-r5.md`. All three required checks passed on PR #715. Platform tests run `40185506558` still has Windows web and Windows server 2/3/4 in progress at this readback; Platform tests summary is not yet available. Existing merge owner received exact head, report and pending summary gate. Snapshot: `/Users/antonabyzov/.specwithcode/m4/evidence/1073-active-pickers/pr715-required-pass.json`. Installed app remains 1.0.76; v1.0.81 is not published.

## Follow-up merged, installed gate retained

PR #715 merged as squash `7d740d544292e7290dfda3d04e16c96a8e35a34b` from R5 SHIP head `a10974456f93dcbfc74bf430a265305cf040c96d`. GitHub readback confirms all checks pass/skip, including successful Platform tests summary. Receipt: `/Users/antonabyzov/.specwithcode/m4/evidence/1073-active-pickers/pr715-merged.json`. Together with PR #710 squash `d582aa8fb6147f3f8c007a8d3ca75d51c258619d`, this is assigned to the existing release owner's 1.0.81. This worker did not dispatch a release.

T-04 source delivery is complete; T-05 remains open. The release owner will wake this implementation owner after M4 installs 1.0.81. Then perform actual installed headless Code Review dropdown acceptance, scoped SpecWeave verification, fresh closure review and completion. No installed acceptance or increment closure is claimed by the merge receipt.

## 1.0.81 published; installed acceptance pending

Release run `40188521599` succeeded. Tag `v1.0.81` is `2885931d5c4c68850419f1be6de7b405de1cf1fb` and contains both #710 and #715 according to the release owner's compare API readback (behind 0). Release receipt: `/Users/antonabyzov/.specwithcode/m4/evidence/release-1081-20261025/RECEIPT-run-40188521599.md`. M4 application readback still reports 1.0.76. The existing release owner's install gate will wake this owner when M4 installs 1.0.81. T-05 remains open for actual installed headless Code Review acceptance, scoped verification, fresh closure review and completion. No duplicate release or install watcher was started.

## Installed 1.0.85 acceptance

Installed production Code Review behavior passes ten headless desktop/narrow cases on a fresh private store using the actual installed bundle. Main entry and Code Review route asset hashes match app.asar and the live 8319 service. Both same-remote checkout registrations remain distinct; active-only choices and retained disabled excluded selection are verified. Full scope and commands: `/Users/antonabyzov/.specwithcode/m4/evidence/1073-active-pickers/installed-1.0.85/ACCEPTANCE.md`. This is installed-byte acceptance against synthetic private metadata, not live catalog, GitHub-account or mounted RN acceptance. No live project was reclassified, no provider turn was sent, and no restart or duplicate release was dispatched.

Installed package/source identity: 1.0.85 / `d9a2e72ce34fe6236d858034dc9441914dbf9877`. Release receipt `/Users/antonabyzov/.specwithcode/m4/evidence/release-1085-20261025/RECEIPT-run-40222940554.md`; update receipt `/Users/antonabyzov/.specwithcode/m4/updates/receipts/update-1.0.85-20261025T190246517161Z.json`. The release receipt correctly distinguishes the successful local release from the duplicate CI run's drafts-stage failure.

## October 27, 2026 closure resumption

All ten tasks were already recorded done; no duplicate task completion was appended. The October 25 fresh closure review is SHIP with zero findings at `/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1073-show-only-active-projects-in-pickers/reports/review-installed-1.0.85-close.md`. Actual installed 1.0.85 acceptance remains the ten retained headless cases documented above.

The workspace has since been restored to original branch `feat/active-only-project-pickers` at `5b4726daedba9f2632ad260fbb0a77f963280e44`, clean and without its dependency symlinks. Closure does not treat that older checkout as the follow-up source head. The exact follow-up source and installed release evidence remain bound separately. The original scoped source verification was preserved at `/Users/antonabyzov/.specwithcode/m4/evidence/1073-active-pickers/installed-1.0.85/source-verify-20261025.json`.

Installed CLI 3.1.14 versus registry stable 3.1.15: used session-local `npx -y specweave@3.1.15`. Fresh scoped verification passes by validating all retained source/installed receipts with `/Users/antonabyzov/.specwithcode/m4/evidence/1073-active-pickers/installed-1.0.85/verify-retained.py`; no current live acceptance or fresh source test execution is inferred. Latest canonical verify reports PASS, 10/10 tasks, 5/5 ACs. A new read-only fresh-context final review is requested at `/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1073-show-only-active-projects-in-pickers/reports/review-final-close-20261027.md` before completion.
