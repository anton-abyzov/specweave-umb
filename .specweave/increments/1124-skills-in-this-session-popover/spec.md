# Skills in this session popover

## Problem

Anton cannot see, from a thread, which skills that session can use or has used. Settings > Skills lists skills for the project's main checkout (ProjectSkillsService.ts:154 always scans workspaceRoot), not the thread's worktree, and never names the machine. The composer `$` picker shows names only, with no source or version. Nothing records which skills a session invoked.

## Scope

In: a small composer-footer popover in the SpecWithCode web/desktop app showing agent, machine and folder, then the selected agent's skills grouped by source (plugin, user, project, other), each with version (lock, plugin or file version) or "untracked", disabled ones greyed, a "Used in this session" group from Claude Skill tool calls and `$name` tokens, Rescan, and a link to Settings > Skills; `projects.skillsRead` accepting an optional thread `cwd` limited to the project's own folders. Out: fleet pushes (1125), Skill Studio changes (1126), per-turn detection for non-Claude agents.

## Acceptance Criteria

- [ ] AC-01: In a thread, one click on a Skills control in the composer footer opens a popover that names the agent, the machine and the thread folder, and lists that agent's skills grouped by source with each skill's version or "untracked"; disabled skills are marked; a provider discovery failure shows an error state, not an empty list.
- [ ] AC-02: The popover's versions come from the thread's folder (worktree when the thread has one): `projects.skillsRead` takes an optional `cwd` and refuses any path that is not the project's workspace root or one of its thread worktrees.
- [ ] AC-03: Skills the session already used (Claude Skill tool calls, `$name` tokens sent) appear in a "Used in this session" group; Rescan refreshes the list; a link opens Settings > Skills.

## Approach

specweave-studio, worktree ~/.specwithcode/m4/worktrees/specweave-studio/skills-session-1124, branch feat/skills-session-popover from origin/main. New apps/web/src/components/chat/ComposerSkillsPopover.tsx + .logic.ts (+ test) modelled on ContextWindowMeter.tsx; mount with a few lines in ChatComposer.tsx footer (file is far over 1500 lines: add only the mount). Data: selectedProviderSkills (name, scope, enabled, path), projectWorkspace.skills joined by name for versions, useMachineNickname for the machine, claudeSkillInvocation from packages/shared/src/toolActivity.ts for used skills. Contract: optional cwd on ProjectSkillsReadInput (packages/contracts/src/projectSkills.ts), validated in ProjectSkillsService.ts.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01: Composer footer popover, not a header chip or a new Settings page (smallest, always beside the session).
- D-02: "Used" is Claude-only plus `$name` tokens; other agents show "available" only.
### Open
- none

## Tasks

### T-01 Thread cwd for project skills
- AC: AC-02 | Files: specweave-studio/packages/contracts/src/projectSkills.ts, specweave-studio/apps/server/src/project/ProjectSkillsService.ts, specweave-studio/apps/server/src/project/ProjectSkillsService.test.ts, specweave-studio/packages/client-runtime/src/state/projectWorkspace.ts | Test: pnpm --dir specweave-studio exec vitest run apps/server/src/project/ProjectSkillsService.test.ts

### T-02 Composer skills popover
- AC: AC-01, AC-03 | Files: specweave-studio/apps/web/src/components/chat/ComposerSkillsPopover.tsx, specweave-studio/apps/web/src/components/chat/ComposerSkillsPopover.logic.ts, specweave-studio/apps/web/src/components/chat/ComposerSkillsPopover.logic.test.ts, specweave-studio/apps/web/src/components/chat/ChatComposer.tsx | Test: pnpm --dir specweave-studio exec vitest run apps/web/src/components/chat/ComposerSkillsPopover.logic.test.ts && headless Playwright screenshot of the popover

### T-03 Verify and close 1124
- AC: AC-01, AC-02, AC-03 | Files: .specweave/increments/1124-skills-in-this-session-popover/reports/ | Test: specweave verify 1124; fresh-context review; specweave complete 1124
