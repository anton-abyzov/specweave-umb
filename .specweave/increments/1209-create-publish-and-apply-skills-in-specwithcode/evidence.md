# 1209 research and design evidence

Research date: November 3, 2026. No source edits, branch changes, commits, publishing or installs. Increment 1208 owner remains active.

CLI installed 3.1.17; npm stable verified as 3.1.20. Increment created with session-local `npx --yes --package specweave@3.1.20 specweave create-increment`.

## Source files inspected

- [Skill Studio generation](/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill/src/eval-ui/src/pages/CreateSkillPage.tsx)
- [Generation and placement rules](/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill/src/eval-ui/src/hooks/useCreateSkill.ts)
- [Commit, push and submission](/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill/src/eval-ui/src/components/PublishDrawer.tsx)
- [Queue states](/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill/src/eval-ui/src/submission-queue.ts)
- [Version manifests](/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill-platform/src/lib/submission/publish.ts)
- [Plugin updater boundary](/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill/src/commands/update.ts)
- [Composer Skills](/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/chat/ComposerSkillsPopover.tsx)
- [Settings Skills](/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/settings/ProjectSkillsSettings.tsx)
- [Exact-version apply and readback](/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specwithcode-dev/apps/server/src/project/ProjectSkillsActions.ts)

## Public and historical evidence

- https://verified-skill.com/ checked for current public product claims. Review is distinct from evaluation.
- https://verified-skill.com/queue returned cached content; no current timing claim is made.
- Project knowledge read: submission-queue-backlog.md, 1093-skill-version-metadata.md, 1093-vskill-skill-name-equals-folder.md. October queue observation is historical. Version/name rules cross-checked with current local source.

## Design verification

Headless html_preview checked 390px light/dark and 728px light/dark. Console layout checks showed scrollWidth equal to viewport width, with no console errors. Describe, Review and Apply panels were visually inspected. Fixed an inline radio-label layout found in the Apply panel and rechecked at 390px and 728px. Screenshots: preview-390-dark.png (Review), preview-728-light.png (corrected Apply), beside this file. Decision controls are explicitly local-only and do not submit approval. No live app/browser acceptance is claimed. Implementation tests intentionally not run for this design-only delivery.


## Implementation closure, November 6, 2026

PR #1430 merged as `c8192f8c5599ff9f19d9c636cfd20018293e5ceb`. Reviewed app HEAD: `33978023866594b5feb79f7f7b13b11a20229c61`. Ledger automatic HEAD references belong to the umbrella repository, not the app.

`specweave verify 1209` passed: 31 server tests and 8 web tests. Fresh Sonnet closure review: SHIP, no critical or high findings. Reports: `/Users/antonabyzov/.specwithcode/m4/evidence/1209-final/closure-review.md` and this increment's `reports/verify.json`. Earlier design-only statements above describe November 3, not current implementation status.

Real provider generation, registry staging submission/readback and installed/native acceptance were not attempted. Source and fixture checks do not establish those outcomes. Suggestions remain explicitly deferred. The root-ancestor-loop hardening is tracked in `follow-up.md`.
