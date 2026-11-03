# 1208 Consistent skills counts and agent-scoped settings

## Problem
The composer shows Codex 20 while Settings shows 19, and Claude's button shows 118 while its panel shows 125. Search does not show its match count. Opening Settings loses the composer's agent and location.

## Scope
Reconcile native listings and inventory identities, expose consistent total/enabled/matched counts, preserve agent/machine/project/folder navigation, and label system skills clearly. Ship one specwithcode-dev PR through merge. No release dispatch or live database access.

## Acceptance Criteria
- [ ] AC-01: Composer button, panel and agent-filtered Settings count the same skill identities; evidence lists both inventories and explains differences.
- [ ] AC-02: Open Skills settings preserves the selected provider instance, machine, project and thread folder.
- [ ] AC-03: System skills have their own named section and explanation; unknown origins remain distinguishable.
- [ ] AC-04: Search updates with every keystroke, matches name and full description, and displays matched and total counts; enabled and disabled totals are explicit.
- [ ] AC-05: Focused tests, production builds and fresh-context review pass; PR is merged without dispatching a release.

## Approach
Trace ComposerSkillsPopover, ProjectSkillsSettings and projectSkillsInventory. Reuse inventory identity rules for count reconciliation; preserve native invocation names and copy metadata. Route through validated Settings search fields. Add regression coverage to the existing composer/settings suites and a headless fixture. Record exact evidence and proof limits in reports.

## Decisions
### Defaulted
- Skills are scoped to provider/harness instance, not model name.
- Total includes disabled skills; enabled and filtered counts are labeled separately.
- Rename the system group to System and retain Other only for unknown levels.
### Open
- None.

## Tasks
### T-01 Reconcile skill identities, navigation, labels and live search
- AC: AC-01, AC-02, AC-03, AC-04 | Files: apps/web/src/components/chat/ComposerSkillsPopover.tsx, apps/web/src/components/chat/ComposerSkillsPopover.logic.ts, apps/web/src/components/chat/ComposerSkillsPopover.test.tsx, apps/web/src/components/chat/ComposerSkillsPopover.logic.test.ts, apps/web/src/components/settings/ProjectSkillsSettings.tsx, apps/web/src/components/settings/ProjectSkillsSettings.logic.ts, apps/web/src/components/settings/ProjectSkillsSettings.test.tsx, apps/web/src/components/settings/ProjectSkillsSettings.logic.test.ts, apps/web/src/routes/settings.skills.tsx, apps/server/src/project/projectSkillsInventory.ts, apps/server/src/project/projectSkillsInventory.test.ts , apps/web/tests/skills-counts/, packages/contracts/src/projectSkills.ts, apps/web/src/components/settings/ProjectSkillControls.tsx, apps/web/src/components/settings/ProjectSkillFleetPush.tsx | Test: focused composer, settings and inventory suites

### T-02 Verify and close 1208
- AC: AC-05 | Files: reports/ | Test: production builds, fresh-context review and merged PR receipt
