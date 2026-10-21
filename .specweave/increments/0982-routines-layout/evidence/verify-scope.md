# 0982 verify scope (October 21, 2026)

The first verify (17:56Z) ran the umbrella's testing.commands, which test other repositories:
specweave `test:unit:fast` (39 failures, mostly pre-compact hook timeouts at 5000 ms under load),
vskill (axe "already running", FindSkillsPalette sessionStorage) and vskill-platform. 0982 changed
none of them; its code lives only in anton-abyzov/specwithcode-dev apps/web.

The scoped verify (SpecWeave 3.1.5, `--cmd`) runs 0982's own required checks at the released source
b3648d70059 (v1.0.66, contains #542 515d3d7186), in ~/.specwithcode/m4/worktrees/routines-layout-verify:
- release identity: HEAD is b3648d70059 and 515d3d7186 is its ancestor;
- the repo's typecheck gate for apps/web (scripts/studio-verify/typecheck-gate.sh, as CI runs it; plain
  `npx tsc` resolved a global compiler and failed TS2883 in unrelated newThreadWorkspaceDefault.ts
  because the --ignore-scripts install skipped `effect-tsgo patch`);
- vp test on apps/web/src/studio, components/studio, components/settings: 221 files, 2,366 tests;
- vp lint on the changed files;
- headless fixture checks (verify-headless.sh): routines-layout-check, settings-presentation
  routines-check, 0980 routines-check. Evidence: ~/.specwithcode/m4/evidence/routines-layout/verify-1.0.66/.

Limits: rendering and action checks use fictional fixtures; installed proof is artifact identity
(byte-identical CSS, strings in the installed client, live index asset name), not an authenticated
live routines UI. No real routine was run, enabled, paused or deleted; no live SQLite access.

## Close review round 1 (October 21, 2026)

A fresh-context review blocked on two points:
- AC-01's 84 px figure did not match the 1440 px side pane (97-98 px). See spec D-05: the AC now states both measured limits, and PR #575 adds an 84 px assertion for the two-column Project settings dialog.
- The dark manager captures were unreadable. The checks toggled `.dark` while useTheme's inline startup background stayed light. PR #575 fixes `setDark` and the fixture background.

Final run: the PR #575 checks (CHECKS=~/.specwithcode/m4/worktrees/routines-check-dark/apps/web/tests) against the b3648d70059 fixtures, with the fixture's 3-line body-background change applied (fixture-diff-vs-b3648d70059.patch). All three checks pass. Evidence: verify-1.0.66-final/.
The installed-1.0.66/installed-*.png files are fixture renders that use the installed CSS, not live UI captures.
Known follow-ups (not in scope, not blocking): a wrapped meta line can start with a stray "·"; the manager's loading and empty strings still say "scheduled tasks"; webhook routines count as "active" in the pane header; there is no rendered proof that "New routine" preselects the project (only the href and search parsing are tested).
PR #575 merged as b9f93f5f4b (squash). The closing verify ran the merged checks (the worktree's apps/web/tests matches b9f93f5f4b, which is an ancestor of origin/main). Evidence: verify-1.0.66-close/.
