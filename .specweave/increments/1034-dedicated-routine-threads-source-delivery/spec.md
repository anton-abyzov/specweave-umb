# 1034 Dedicated routine threads source delivery

## Problem
Project routines used the coordinator conversation. Resume the existing staged October 22 implementation and prove dedicated thread execution before source delivery.

## Scope
In: creation defaults, legacy coordinator migration, persistent routine threads, UI navigation, existing Telegram forwarding, ownership fencing, tests and pull request. Out: live provider turns, app merge, release or restart. Complete screenshot sessions owns app integration and release.

## Acceptance Criteria
- [ ] AC-01: A new or legacy project routine launches one dedicated thread and subsequent runs continue it, without waking the coordinator. Archived/deleted routine threads are replaced; explicit worker follow-ups keep their binding.
- [ ] AC-02: Transferred projects cannot restart project-owned routines locally, including after migration or editing. Explicit worker follow-ups preserve existing admission rules.
- [ ] AC-03: Project and Settings routine rows expose their own thread with correct navigation, across desktop/mobile and light/dark headless fixtures.
- [ ] AC-04: Focused tests, production builds and a fresh independent review pass; source is committed and delivered by PR to the app merge owner.

## Approach
Retain the existing worktree and staged changes. Validate server dispatch with isolated in-memory services and production React components with synthetic headless UI fixtures. No live store access or provider spend. Capture evidence in /Users/antonabyzov/.specwithcode/m4/evidence/routine-own-threads-20261023.

## Decisions
- D-01: Existing checkpoint has no increment. This increment records resumed verification and source delivery, not a claim that the original implementation was planned here.
- D-02: Project-owned routines follow project ownership after transfer; explicit worker-bound schedules remain worker-scoped.
- D-03: Source acceptance is separate from installed app acceptance, retained by the merge/release owner.

## Tasks

### T-01 Validate and repair dedicated-thread behavior and UI
- AC: AC-01, AC-02, AC-03 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/routine-own-threads/apps/server/src/scheduledTasks/ScheduledTaskService.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/routine-own-threads/apps/server/src/scheduledTasks/ScheduledTaskAdmission.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/routine-own-threads/apps/server/src/scheduledTasks/ScheduledTaskService.routines.test.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/routine-own-threads/apps/web/src/components/studio/ProjectRoutines.tsx | Test: bash /Users/antonabyzov/.specwithcode/m4/evidence/routine-own-threads-20261023/verify.sh

### T-02 Review and deliver the source PR
- AC: AC-04 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/routine-own-threads/CHANGELOG.md | Test: bash /Users/antonabyzov/.specwithcode/m4/evidence/routine-own-threads-20261023/verify.sh

Verify and close 1034.
