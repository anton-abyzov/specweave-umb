# Fix M5 Settings Skills installation and packaged vskill availability

## Problem
Settings > Skills refused to install obsidian-brain because it could not resolve vskill. The screenshot records the failure, but no pre-recovery filesystem or desktop PATH inventory exists. A subsequent npm installation is recorded locally and must not be mistaken for evidence of prior absence. Settings depends on a separately installed executable even though the app manages a private Node runtime.

## Scope
In: evidence-based diagnosis, requested skill installation and app inventory verification, managed vskill availability for packaged clean installs and upgrades, focused regression tests, independent review and closure. Out: reading personal vaults, changing auth, restarting the live app or disrupting streaming, unrelated shared work.

## Acceptance Criteria
- [ ] AC-01: Report separates observed original failure, subsequent installation evidence and current desktop discovery; any historical uncertainty is explicit.
- [ ] AC-02: obsidian-brain is installed for the existing requested project scope and visible as installed in the app, without accessing personal vault contents. A read-only functional query may use a tiny synthetic vault, per subsequent user authorization.
- [ ] AC-03: A packaged app with its managed Node runtime can perform Skills installation without a separately global vskill installation, including after an upgrade, with bounded failures and no replacement of user tools.
- [ ] AC-04: Focused regressions exercise managed runtime layout, narrow PATH, existing installation preference, failure propagation and upgrade reuse.
- [ ] AC-05: The actual patch receives independent adversarial review through delegate_task using the live catalog model gpt-6.2-sol; findings are rechecked, required verification passes and the increment closes.

## Approach
The M5 checkout was stale; merge current origin/main preserving all three local commits before final patch review. The current connected-repository install path is SkillUpdateRpc/SkillUpdate, separate from version history actions. Acquisition belongs only in that mutation path; version reads and previews remain read-only. First preserve local evidence and inspect Settings through a background browser. Reuse the existing machine-tool Node/npm discovery and private install conventions for a pinned managed vskill fallback. Keep external vskill precedence, make dependency acquisition part of explicit Skills actions, and exercise the packaged directory layout with isolated fixtures rather than the developer PATH. Record app recovery separately from patch validation. Preserve the shared checkout and other agents' files.

## Decisions
### Asked
- D-01: Reviewer must be ChatGPT 6.2 Sol, for review only (user). Live catalog advertises codex/gpt-6.2-sol.
- D-02: No personal vault access, visible browser or streaming disruption. Subsequent user instruction authorizes read-only functional tests on a synthetic vault, across available configured providers and authorized machines, without fan-out installs or grant changes.
### Defaulted
- D-03: Use a pinned app-private dependency fallback instead of changing user-global npm tools.
- D-04: Preserve uncertainty about the original machine state if no contemporaneous evidence exists.
### Open
- none

## Review
Independent adversarial review: codex/gpt-6.2-sol, explicitly requested. No substitution if unavailable.

## Tasks

### T-01 Diagnose and recover the requested skill
- AC: AC-01, AC-02 | Files: .specweave/increments/1360-fix-m5-settings-skills-installation-and-packaged-vskill-availability/reports/ | Test: app Skills inventory and retained recovery evidence

### T-02 Provide managed vskill for packaged Skills actions
- AC: AC-03, AC-04 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/project/ProjectSkillsActionsCommon.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/ProjectSkillsActions.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/ProjectSkillsActionsRpc.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/ProjectSkillsActions.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/machineTools/vskillTool.ts, repositories/anton-abyzov/specwithcode/apps/server/src/machineTools/vskillTool.test.ts | Test: focused ProjectSkillsActions and vskillTool suites with packaged runtime fixtures

### T-03 Review, verify and close 1360
- AC: AC-05 | Files: .specweave/increments/1360-fix-m5-settings-skills-installation-and-packaged-vskill-availability/reports/ | Test: specweave verify 1360 and independent gpt-6.2-sol patch review

### T-04 Wire the current Settings install path and recheck review findings
- AC: AC-03, AC-04, AC-05 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/project/SkillUpdateRpc.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/SkillUpdateRpc.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/SkillUpdate.test.ts | Test: focused SkillUpdate and SkillUpdateRpc suites, including read/preview no-acquisition and packaged runtime installation

### T-05 Preserve bootstrap failure details at the install boundary
- AC: AC-03, AC-04 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/project/SkillUpdate.ts | Test: focused SkillUpdate and packaged installer tests verify failure outcomes

### T-06 Bound installer process termination
- AC: AC-03, AC-04, AC-05 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/processRunner.ts | Test: packaged installer regression with an npm leader ignoring SIGTERM and immediate retry

### T-07 Fix strict typecheck findings in installer boundary
- AC: AC-03, AC-04, AC-05 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/machineTools/vskillTool.ts, repositories/anton-abyzov/specwithcode/apps/server/src/machineTools/vskillTool.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/SkillUpdateRpc.ts | Test: strict typecheck gate plus focused installer and SkillUpdate suites
