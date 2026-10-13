# 0908 Preserve project names and prepare release

## Problem
Repository-grouped copies of the same project lose a saved custom name when another machine or checkout still has its default folder name. The sidebar then shows owner/repository while the project header shows the saved name. Pending umbrella records also need durable remote backup.

## Scope
In: shared project label derivation, focused regression and browser verification, latest-main release preparation, and reviewed commit/push of pending umbrella records. Out: taking over 0907 machine-handoff implementation, restarting live providers, publishing unfinished work or committing private runtime data.

## Acceptance Criteria
- [ ] AC-01: A single custom project name survives default-named copies across machines and worktrees; repository identity and fork grouping remain unchanged.
- [ ] AC-02: Regression tests, relevant production builds, and a headless rendered check pass for the naming change.
- [ ] AC-03: The naming fix and safe pending umbrella records are committed and pushed, with remote readback and exact remaining foreign-worktree boundaries recorded.
- [ ] AC-04: A concrete next-release candidate is prepared from latest completed source without colliding with the active 0907 release owner; publication state and outstanding gates are explicit.

## Approach
Change packages/client-runtime/src/state/projectGrouping.ts so custom titles are considered separately from repository/display/folder defaults. Retain the existing repository fallback for conflicting custom titles. Preserve grouping keys, physical project refs and fork boundaries. Check the shared label in its actual sidebar consumer.

Use isolated umbrella and product branches codex/project-names-release. Baselines: umbrella 99e16cf4e, Studio 2ef696067. SpecWeave 3.0.14 verified against npm. The chat Improve SpecWithCode release output owns the successor release with 0907; Anton explicitly authorized coordinating one release; the existing owner confirmed tentative version 1.0.10 and inclusion of the reviewed naming fix before freezing. No live installation or service restart is required by this preparation task.

## Tasks

### T-01 Preserve custom names across grouped projects
- AC: AC-01 | Files: repositories/anton-abyzov/specweave-studio/packages/client-runtime/src/state/projectGrouping.ts, repositories/anton-abyzov/specweave-studio/packages/client-runtime/src/state/projectGrouping.test.ts | Test: cd repositories/anton-abyzov/specweave-studio && node node_modules/vite-plus/bin/vp test run packages/client-runtime/src/state/projectGrouping.test.ts

### T-02 Verify rendered labels and production builds
- AC: AC-02 | Files: .specweave/increments/0908-project-names-release/reports | Test: node repositories/anton-abyzov/specweave-studio/scripts/studio-verify/project-names.mjs

### T-03 Preserve and push reviewed pending work
- AC: AC-03 | Files: .specweave/increments/0908-project-names-release/reports/git-state.md, .specweave/increments/0896-hosted-private-skill-publishing/ledger.jsonl, .specweave/increments/0897-free-first-pricing-and-launch, .specweave/increments/0898-team-usage-view, .specweave/project/hub.json, .specweave/state/closure-metrics.json, AGENTS.md, .specweave/reports | Test: git diff --check

### T-04 Prepare the release and record verification
- AC: AC-04 | Files: .specweave/increments/0908-project-names-release/reports/release.md | Test: git diff --check
