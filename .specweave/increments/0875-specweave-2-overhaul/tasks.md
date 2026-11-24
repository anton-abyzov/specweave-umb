# Tasks: 0875 SpecWeave 2.0 overhaul

### T-01 Audit + design
- AC: AC-01, AC-05 | Files: .specweave/increments/0875-specweave-2-overhaul/reports/** | Test: reports/design-2.0.md and audit-digest.md exist
- [x] done — 17-agent audit, design-2.0.md, v2 templates written 2026-09-02

### T-02 Repo hygiene + security triage
- AC: AC-09, AC-11 | Files: (remote) | Test: strict padded-line scan reports 0 on origin/develop + origin/main x2
- [x] done — PR #1924 merged; PRs #1851-1854/#1746/#1756/platform #60 closed; 28 stale bot branches deleted (backup refs local)

### T-03 Wave 1: vskill Windows sidecar
- AC: AC-08 | Files: vskill scripts/desktop/**, src-tauri/**, .github/workflows/sidecar-smoke.yml | Test: sidecar-smoke.yml green on windows-latest
- [x] done — branch fix/windows-sidecar-boot; run 33627651497 ALL GREEN: sidecar smoke windows-latest/macos-latest/ubuntu-latest + cargo check+test src-tauri (windows-latest). Windows evidence: LISTEN_PORT=56197 after 522 ms, /api/health 200, clean shutdown exit 0

### T-04 Wave 1: security hardening (3 repos)
- AC: AC-09 | Files: .npmrc, .github/workflows/**, scripts/security/**, SECURITY.md, crawl-worker/.env* | Test: supply-chain-scan.yml green; `npm run security:scan` exit 0
- [x] done — sec/hardening branches in all 3 repos (scanner self-test passes; PAT rotation = owner action)

### T-05 Wave 1: hooks rewrite
- AC: AC-03 | Files: specweave plugins/specweave/hooks/**, src/core/hooks/**, bin/specweave.js | Test: npx vitest run tests/unit/hooks; hooks-crossplatform.yml green
- [x] done — codex/2.0-hooks, 9 commits, 295 files, -47.7k lines (248 deleted). 4 exec-form node hooks, run.mjs launcher, schema-valid handlers, JSONL log w/ rotation, hooks-crossplatform.yml. Tests: tsc clean, build ok, hook-smoke 7/7, hooks unit 151/0. Issue #1847 closed (no "decision":"allow" anywhere)

### T-06 Wave 1: limits + quick fixes
- AC: AC-04, AC-11 | Files: specweave src/core/increment/**, src/cli/commands/auto.ts, package.json, src/core/doctor/** | Test: npx vitest run tests/unit/core/increment
- [x] done — codex/2.0-limits-fixes, 12 commits, 81 files. Hard WIP cap gone (advisory only), package.json main removed (PR #1902 intent), doctor reads real version, `specweave gc` + 24h session-start state purge, init .gitignore entries. Tests: tsc clean, build ok, increment/config/cli 3731p/1f (pre-existing)

### T-07 Wave 1: templates + merger
- AC: AC-01, AC-02 | Files: specweave src/templates/**, src/cli/helpers/init/** | Test: npx vitest run tests/unit/cli/helpers/init
- [x] done — branch codex/2.0-templates (4 commits); umbrella smoke 348→98 lines, easychamp 556→305, user content preserved; 1061 tests pass

### T-08 Wave 1: sync collapse
- AC: AC-07 | Files: specweave src/sync/**, src/core/sync/**, src/integrations/**, plugins/specweave/skills/sync/** | Test: npx vitest run tests/unit -t sync
- [x] done — codex/2.0-sync, 15 commits, 403 files. One `specweave sync push|pull|status|setup` surface + single sw:sync skill; queued mode/event queue/duplicate throttles deleted; issue #1925 fixed (projectIds); single GitHub token resolver w/ write-404 translation. Tests: sync 746p/0f (was 807p/4f)

### T-09 Wave 1: task ledger + verify + closure gate + handoff
- AC: AC-05, AC-06 | Files: specweave src/core/tasks/**, src/cli/commands/{task,verify}.ts, src/core/session/** | Test: end-to-end temp-repo script in the builder report
- [x] done — codex/2.0-ledger, 14 commits, 49 files. ledger.jsonl + `specweave task list|next|claim|done|release|block|skip|render|whoami` + `specweave verify` + closure gate on verify.json (old grill/code-review/judge gates now optional evidence) + 1-page handoff. Tests: `npm run e2e:ledger` 19/19, src+increment suites green

### T-10 Wave 1: crawler breadth
- AC: AC-10 | Files: vskill-platform crawl-worker/** | Test: node --test in crawl-worker; crawl-worker-tests.yml
- [x] done — feat/crawl-breadth, 10 commits, 66 files. 0874 merged in; sourcegraph two-phase read; known-key cache; github topic search replaces the dead 90-min loop; one result contract + full heartbeat payload persisted; dead sources removed; crawl-worker-tests.yml. Tests: node --test 183p/0f (was 168p/6f). Deploy = owner action (DEPLOY-NOTES.md)

### T-11 Wave 2: skills consolidation + config 2.0 + doctor + docs
- AC: AC-01, AC-04 | Files: specweave plugins/specweave/skills/**, src/core/config/**, src/core/doctor/**, docs-site/** | Test: skill lint passes; vitest unit green
- [x] done — 7 branches built + merged into release/2.0 @b3d0c23e2. Skills 51->10 core; config 2.0 (-16.4k lines); templates v3 w/ conditional umbrella section; ledger skip/auto-claim/board; standalone vskill skills/; 64 CLI registrations import-verified; docs-site 43 pages written / 47 deleted, `lint:docs-refs` 1744 findings -> 0, Docusaurus build exit 0. Gates: tsc clean, build ok, lint:skills 37 clean, hook-smoke 7/7, e2e:ledger 35/35, unit 16416p/3f, integration 829p/5f (all pre-existing)

### T-12 Wave 3: adversarial review of all branches + fixes
- AC: all | Files: all wave branches | Test: review workflow reports no unrefuted critical/high findings
- [x] done — 146 agents / 15.5M tokens. 7 lenses (correctness, security, cross-platform, upgrade-regression, coverage-loss, dead-references, spec-compliance) -> 69 raw -> 68 unique -> 2 skeptics each -> 14 confirmed / 54 refuted (79% kill rate). All 14 fixed in 3 isolated worktrees, 0 skipped. 3 CRITICAL: (1) run.mjs imported code from a world-writable /tmp cache (PoC executed planted code on every hook) -> moved to ~/.specweave 0700 + lstat/uid check; (2) CRLF/BOM tasks.md parsed as ZERO tasks, killing the whole ledger loop on Windows -> split on /\r?\n/ + BOM strip + CRLF fixtures in e2e; (3) create-increment wrote a status its own validator rejects. Also: /sw:auto could never terminate on an increment with a skipped task

### T-13 Merge, version, publish, install, verify
- AC: AC-12 | Files: specweave develop, vskill main, vskill-platform main | Test: `specweave --version` = 2.0.0 globally; `specweave update` on umbrella yields the 2.0 CLAUDE.md; desktop release CI green incl. Windows smoke
- [x] done — **specweave@2.0.0 PUBLISHED** (npm latest=2.0.0, run 33685537680 green, OIDC trusted publishing, no token/OTP). Took 4 attempts: the new publish preflight blocked 3 of them, each for a real reason (JSON parse of `npm pack --json`, then a wrong array, then npm 12's keyed-object payload shape `{"<pkg>":{files:[]}}` vs npm 10's array). Verified against the LIVE registry: isolated install prints 2.0.0, full loop runs (init/doctor exit 0/create-increment status=active/2 commits past the pre-commit hook/claim/done --run/skip/verify ok acs 2-of-2/complete/handoff in the increment folder/gc). Global install upgraded 1.0.591 -> 2.0.0. `specweave update` on THIS umbrella repo: CLAUDE.md 347 -> 106 lines, all hand-written sections preserved verbatim (incl. both dated Team Lead memories), 22 dead config keys migrated, backups written, `doctor` exit 0. vskill 1.1.0 + vskill-platform pushed to main; desktop-v1.0.63 tagged (build running)

### T-14 Close issues/PRs, memory, Obsidian, video notes
- AC: AC-11 | Files: GitHub, ~/.claude memory, Obsidian inbox | Test: issues #1847 #1925 closed; PR #1902 closed with thanks
- [x] done — #1847 closed (hook output shape fixed + 2 regression guards), #1925 closed (projectIds wired through LifecycleHookDispatcher:227), PR #1902 closed with thanks and credit (its intent shipped; the reply also names the deeper publish-hook hole its bug exposed). Each verified as actually present in 2.0.0 BEFORE closing, not assumed
