# 1242 Show available and used skills in coordinator windows

## Problem
The coordinator composer supports slash skill invocation but gives no discoverable inventory before typing. Users cannot distinguish skills available to a coordinator or worker from skills evidenced in a particular run.

## Scope
Coordinator inventory and run usage visibility, scoped to harness instance, machine and working directory. Preserve 1208 count/search semantics and 1209 authoring changes. No automatic skill installation or invocation. No release dispatch from this thread.

## Acceptance Criteria
- [ ] AC-01: Before sending, the coordinator exposes its available skills with enabled/off counts and search, scoped to its selected provider instance, machine and folder.
- [ ] AC-02: Worker availability is clearly scoped to the selected worker context; unavailable remote discovery is shown as unknown, never as zero or the coordinator inventory.
- [ ] AC-03: Run usage displays only evidence associated with that run; availability, explicit request and observed usage are distinct, and missing telemetry is unknown.
- [ ] AC-04: Existing authoring and count/filter behavior remains intact; shared-file integration occurs only after 1209 lands.
- [ ] AC-05: Focused tests, headless evidence, exact-head Sonnet 5.5 review, green applicable CI and the user manual UI check precede acceptance; merged work is handed to the designated dispatcher.

## Approach
Reuse read-only inventory/catalog helpers used by ComposerSkillsPopover and resolveProviderSkillsForCwd. Build coordinator-specific presentation and usage derivation separately. CoordinatorComposer already receives provider snapshot and cwd; CoordinatorRunActivity renders run-scoped activity. Inspect their parent context and existing usage evidence before wiring. Do not edit ComposerSkillsPopover.tsx, ProjectSkillsSettings.tsx or shared skills contracts while 1209 owns them. Do not edit its worktree. Add only explicitly allocated coordinator files; reconcile ownership before widening allocation.

## Decisions
### Defaulted
- Available does not mean applied. Show observed usage only where run evidence supports it; otherwise Unknown.
- Harness instance, machine and directory define inventory, not model family alone.
- One release dispatcher owns publication: Release all platforms in 3 hours. Preserve its slot and merge freeze.
### Open
- Shared integration waits for 1209 landing. Manual UI acceptance remains pending until the user checks the implementation.

## Tasks
### T-01 Build coordinator-specific inventory and usage presentation
- AC: AC-01, AC-02, AC-03 | Files: apps/web/src/components/studio/CoordinatorSkills.tsx, apps/web/src/components/studio/CoordinatorSkills.test.tsx, apps/web/src/studio/coordinatorSkills.ts, apps/web/src/studio/coordinatorSkills.test.ts | Test: focused web tests and web typecheck

### T-02 Integrate after shared ownership is released
- AC: AC-01, AC-02, AC-03, AC-04 | Files: apps/web/src/components/studio/CoordinatorComposer.tsx, apps/web/src/components/studio/CoordinatorRunActivity.tsx, apps/web/src/components/studio/ProjectCoordinatorDetails.tsx | Test: coordinator integration tests and headless fixture; reconcile additional parent files before editing

### T-03 Verify and close 1242
- AC: AC-04, AC-05 | Files: reports/evidence.md | Test: focused tests, headless screenshots, Sonnet 5.5 review, applicable hosted CI, manual UI acceptance, specweave verify 1242, fresh-context review, specweave complete 1242
