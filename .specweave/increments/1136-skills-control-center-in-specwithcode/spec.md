# Skills control center in SpecWithCode

## Problem

Settings > Skills and the composer Skills popover only show skills. To change a skill's version, pin it, push it to other machines, or turn a skill or plugin on or off, Anton has to leave SpecWithCode for Skill Studio, the vskill CLI, `claude plugin`, Codex config.toml or `grok plugin`. Each agent does this differently.

## Scope

In: clickable source, registry and versions links; a version section (list versions, install a version, pin, unpin, update to latest); per-agent skill and plugin on/off (Claude skillOverrides and `claude plugin enable|disable`, Codex app-server skills/config/write and config/value/write, Grok `grok plugin enable|disable`); push a version to fleet machines through the merged fleet skills path; "Release in Skill Studio" hand-off link; preview, backup and Undo for writes. Out: native release (bump, push, submit), Grok per-skill toggle, Codex TOML fallback, bulk actions, composer toggles.

## Acceptance Criteria

- [ ] AC-01: In Settings > Skills, a skill's detail and row menu open its source file, its verified-skill.com page and its versions page in the browser.
- [ ] AC-02: The detail shows the installed version, pinned state and available versions; Install, Pin, Unpin and Update to latest run vskill with a fixed argv and the panel shows the new version read back from the lock, or a named refusal.
- [ ] AC-03: Each agent that loads the skill has a switch: Claude edits skillOverrides (comment-preserving, whole-map validated, backed up, hash-checked), Codex writes through its app-server, Grok shows the switch disabled with a reason; plugin skills offer turning the whole plugin off per agent; each change previews first, says when it takes effect, and can be undone.
- [ ] AC-04: "Push to machines" lists fleet machines, installs the chosen version on the checked ones over Connect and shows one result per machine; "Release in Skill Studio" opens the skill in a running or newly started Studio.

## Approach

Worktree ~/.specwithcode/m4/worktrees/specweave-studio/skills-control-center, branch feat/skills-control-center from origin/main. Full design with contract, reasons, per-agent mechanisms and risks: reports/design.md (Design section). New RPC group WsProjectSkillsActionsRpcGroup (skillsVersions, skillsAction, skillsFleetPush, skillsStudioLink) with per-kind scopes; server code in new files under apps/server/src/project/ (keep each under 1500 lines); UI in ProjectSkillsSettings detail sheet and row menu, split into new component files.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01: Native control center for versions, toggles and fleet push; release stays a hand-off to Skill Studio (authoring flow, no --json on submit).
- D-02: Never call `vskill disable` (it uninstalls Claude plugins).
- D-03: Grok per-skill toggle not offered (its ignore list hides the skill, so it could never be turned back on from the UI).
- D-04: A Claude skill switch whose requested file is outranked (a user skill the project's settings.json turns off or on) goes in the repository's settings.local.json, the highest file below managed settings; the preview names the file and says why. The shared project settings.json is never edited.
- D-05: Codex and Claude-plugin writes that land but are overridden by a higher layer are reported as applied with a warning and the real effective state (Undo stays available), not refused after the write.
- D-06: Version writes on a user skill recorded only in the legacy ~/vskill.lock are refused (scope_unsupported): vskill install --global writes ~/.agents/vskill.lock.
- D-07: File-size exception: apps/server/src/ws.ts and packages/contracts/src/rpc.ts were already over 1500 lines; this increment adds only the RPC group wiring lines there (ws.ts +2, rpc.ts +6).
- D-08: Claude plugin skills use the whole-plugin control. Their individual switches are disabled with a reason, because Claude does not honor skillOverrides for plugin skills. Explicitly disabled installed plugins stay visible so they can be re-enabled or undone; an enabled copy wins a namespace collision.
- D-09: Update to latest is bound to the exact version displayed in preview. Registry drift or a missing preview target causes a stale refusal before installation.
### Open
- none

## Tasks

### T-01 Contract, scopes and lock fields
- AC: AC-01, AC-02, AC-03, AC-04 | Files: packages/contracts/src/projectSkills.ts, packages/contracts/src/projectSkillsActions.test.ts, packages/contracts/src/projectWorkspaceRpc.ts, packages/contracts/src/rpc.ts, packages/contracts/src/clientRpcPermissions.ts, packages/client-runtime/src/state/projectWorkspace.ts, apps/server/src/auth/RpcAuthorization.test.ts, apps/server/src/observability/RpcInstrumentation.ts, apps/server/src/project/projectSkillsInventory*.ts, apps/server/src/project/ProjectSkillsService.ts, apps/server/src/provider/ProviderDriver.ts, apps/server/src/provider/Drivers/ClaudeDriver.ts, apps/server/src/provider/Drivers/ClaudeSkills.ts, apps/server/src/provider/Drivers/CodexDriver.ts, apps/server/src/provider/Drivers/GrokDriver.ts | Test: npx vp test run (contracts and server auth tests)

### T-02 Versions and version actions over vskill
- AC: AC-02 | Files: apps/server/src/project/ProjectSkillsActions*.ts | Test: npx vp test run apps/server/src/project/ProjectSkillsActions.test.ts

### T-03 Per-agent skill and plugin toggles
- AC: AC-03 | Files: apps/server/src/project/ClaudeSettingsWrite.ts, apps/server/src/project/ProjectSkillsToggles*.ts | Test: npx vp test run apps/server/src/project/ClaudeSettingsWrite.test.ts apps/server/src/project/ProjectSkillsToggles.test.ts

### T-04 Fleet push and Studio link
- AC: AC-04 | Files: apps/server/src/project/ProjectSkillsFleet*.ts, apps/server/src/ws.ts | Test: npx vp test run apps/server/src/project/ProjectSkillsFleet.test.ts

### T-05 Control center UI
- AC: AC-01, AC-02, AC-03, AC-04 | Files: apps/web/src/components/settings/ProjectSkill*.tsx, apps/web/src/components/settings/ProjectSkill*.ts, apps/web/src/components/chat/ComposerSkillsPopover*.tsx, apps/web/src/routes/settings.skills.tsx | Test: npx vp test run apps/web/src/components/settings/ + headless Playwright screenshots in reports/

### T-06 Verify and close 1136
- AC: AC-01, AC-02, AC-03, AC-04 | Files: .specweave/increments/1136-skills-control-center-in-specwithcode/reports/ | Test: specweave verify 1136; fresh-context review; specweave complete 1136

### T-07 Fix closure review findings
- AC: AC-02, AC-03 | Files: apps/server/src/provider/Drivers/ClaudeSkills.ts, apps/server/src/provider/Drivers/ClaudeSkills.test.ts, apps/server/src/project/ProjectSkillsActions.ts, apps/server/src/project/ProjectSkillsActions.test.ts, apps/server/src/project/ProjectSkillsToggles.ts, apps/server/src/project/ProjectSkillsToggles.test.ts, apps/web/src/components/settings/ProjectSkillActions.logic.ts, apps/web/src/components/settings/ProjectSkillActions.logic.test.ts, apps/web/src/components/settings/ProjectSkillControls.tsx, apps/web/src/components/settings/ProjectSkillControls.test.tsx, packages/contracts/src/projectSkills.ts, packages/contracts/src/projectSkillsActions.test.ts, docs/studio/skills.md | Test: focused provider, action, toggle, contracts and settings regression suites; coverage; typecheck gate and production build

### T-09 Expose re-enable for retained disabled plugins
- AC: AC-03 | Files: apps/web/src/components/settings/ProjectSkillAgentToggles.tsx, apps/web/src/components/settings/ProjectSkillsSettings.test.tsx, README.md, CHANGELOG.md, AGENTS.md | Test: settings component regression tests and headless skills control check

### T-08 Verify release and close 1136
- AC: AC-01, AC-02, AC-03, AC-04 | Files: .specweave/increments/1136-skills-control-center-in-specwithcode/reports/ | Test: fresh-context review; specweave verify 1136; canonical release verification; specweave complete 1136

## Completion continuation

Anton accepted the work in the original session at 2026-10-29T03:56:05Z and requested completion here after its weekly limit prevented further work. Fresh closure review found plugin Undo losing its target, unsupported Claude plugin per-skill switches, and registry drift between version preview and apply. Release 1.0.115 was stopped before publication to address these findings. Preserve disabled installed plugins in management discovery, refuse unsupported per-skill writes, and bind version actions to the version actually previewed. This does not expand the feature scope.
