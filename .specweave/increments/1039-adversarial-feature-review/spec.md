# 1039 Adversarial feature review

## Problem

Recent SpecWithCode features were implemented in separate lanes. Settings, machine handoff, fallback, Aide, project navigation, reports, highlighting and notifications now interact. Anton requested native Codex GPT-6.1-Sol at Ultra effort to find reproducible bugs and bounded simplifications without disturbing retained owners.

## Scope

In: read-only source and evidence review beginning with settings/options and handoff; recent feature and open PR interaction inventory; concrete path:line findings, isolated reproductions, deduplication against existing gates, bounded repair plans routed to retained owners. Product changes require an existing authorized writer binding and an ownership check first.

Out: broad rewrites, project registration changes, ad-hoc worktrees/clones, settings writes, grants, credentials, paid/provider turns, waking held 1011, merge, release, restart or installed acceptance. Approved app checkout `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave-studio` is read-only in this thread. The CLI checkout is not the app repository.

## Acceptance Criteria

- [ ] AC-01: Record native provider/model/effort, stable CLI receipt, app HEAD/main SHA, PR heads and retained owners; separate source, CI and installed proof.
- [ ] AC-02: Review settings/options and handoff against 1031, 1006, 0967 and 0968 evidence. Every surviving defect cites an absolute source path, line, concrete failing state and reproduction or explicit plausible label.
- [ ] AC-03: Inventory and review fallback constraints, Aide isolation, navigation, reports/Markdown/code, notifications and lifecycle interactions. Distinguish implemented source, open PRs and unresolved acceptance.
- [ ] AC-04: Independently re-verify findings, deduplicate existing work and record behavior-preserving repair plans. Only safe bound, unowned repairs may be implemented; otherwise deliver concrete findings to retained owners and preserve registration gates.
- [ ] AC-05: Publish prioritized results with file-backed checks, fresh-context review, explicit coordinator/integration delivery and honest remaining gates.
- [ ] AC-06: Every surviving high defect has an independently reviewed repair at its exact source head before closure. Source repair, CI, integration and installed acceptance remain separate gates.

## Approach

Use verified npm stable CLI `3.1.7` at `/Users/antonabyzov/.npm/_npx/e8cd97fc4977f3e2/node_modules/.bin/specweave`. Initial app checkout HEAD is `bc3fabf56778cb4fe90a64e485bc8ada97e2695d`; GitHub and local origin/main agree at `f4ff1b4bcfb4692ca152fcd4616de65e5873dcb9`. Read main and explicit PR heads through Git objects. Detached checkout bytes are not main. Record moving heads when checked.

Current closure uses verified session-local CLI `3.1.8`; the initial `3.1.7` receipt above is historical.

Read project knowledge and increments. Use fresh native GPT-6.1-Sol Ultra subagents for disjoint lenses; the primary reviewer reopens cited lines and runs bounded isolated reproductions. Browser automation must use headless true, `PWDEBUG=0`, `PLAYWRIGHT_HTML_OPEN=never`, reporter open never, and file captures. Never access live database files directly. Preserve owner worktrees and dirty files; no stash or branch switch.

## Decisions

### Asked
- D-01: Anton requested GPT-6.1-Sol Ultra review and bounded evidence-led simplifications.

### Defaulted
- D-02: Preserve 1031 Claude Code UltraCode design ownership and 0972/0975 local Opus high requirements. This review does not replace those methods.
- D-03: Without app repository registration/writer binding, review and route patches. No registration bypass or editing the detached app checkout.
- D-04: Complete screenshot sessions retains integration, merge, release and installed acceptance. This review cannot close their runtime gates.

### Open
- Current registration is in place, but this review thread has no app writer binding. Retained bound owners deliver source repairs; medium F-05/F-06 and integration/installed gates stay with them.

## Tasks

### T-01 Record baseline and owners
- AC: AC-01 | Files: /Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1039-adversarial-feature-review/reports/baseline.md | Test: test -s /Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1039-adversarial-feature-review/reports/baseline.md

### T-02 Review settings and handoff
- AC: AC-02 | Files: /Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1039-adversarial-feature-review/reports/settings-handoff.md | Test: test -s /Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1039-adversarial-feature-review/reports/settings-handoff.md

### T-03 Review fallback, Aide and lifecycle
- AC: AC-03 | Files: /Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1039-adversarial-feature-review/reports/fallback-aide-lifecycle.md | Test: test -s /Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1039-adversarial-feature-review/reports/fallback-aide-lifecycle.md

### T-04 Review presentation, navigation and notifications
- AC: AC-03 | Files: /Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1039-adversarial-feature-review/reports/presentation-navigation-notifications.md | Test: test -s /Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1039-adversarial-feature-review/reports/presentation-navigation-notifications.md

### T-05 Reproduce, triage and deliver repairs
- AC: AC-04 | Files: /Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1039-adversarial-feature-review/reports/findings.md, /Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1039-adversarial-feature-review/reports/delivery.md | Test: test -s /Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1039-adversarial-feature-review/reports/findings.md

### T-06 Review retained owner repair candidates
- AC: AC-06 | Files: /Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1039-adversarial-feature-review/reports/repair-gates.md, /Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1039-adversarial-feature-review/reports/aide-candidate-review.md | Test: test -s /Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1039-adversarial-feature-review/reports/repair-gates.md

### T-07 Verify and close 1039
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06 | Files: /Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1039-adversarial-feature-review/reports/review.md, /Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1039-adversarial-feature-review/reports/review.html | Test: specweave verify 1039-adversarial-feature-review
