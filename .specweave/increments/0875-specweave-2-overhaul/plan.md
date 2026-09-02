# 0875 plan

Concept: `reports/design-2.0.md` (agreed 2.0 concept). Evidence: `reports/audit-digest.md` + `reports/audits/*.md` (17 auditors). Course notes: `reports/course-report.md`. Facts/paths: `reports/context.md`.

## Approach

Three waves of parallel builders in git worktrees (one branch per stream, commit locally, no push), then review, merge, release.

Wave 1 (running; script `reports/build-wave1.js`):
| Stream | Repo / branch | Owns |
|---|---|---|
| vskill-windows | vskill `fix/windows-sidecar-boot` | esbuild JS-API bundler, smoke-sidecar.mjs, sidecar-smoke.yml + rust-windows job, tauri-plugin-log, proc.rs (windows-sys), boot-failure page |
| security-hardening | specweave/vskill/vskill-platform `sec/hardening` | .npmrc, CI --ignore-scripts, disable autofix workflows, supply-chain-scan.yml + scripts/security/scan-payload.mjs, dependabot cooldown, untrack PAT env files, SECURITY.md |
| hooks-rewrite | specweave `codex/2.0-hooks` | hooks.json (4 exec-form entries), hooks/run.mjs launcher, handler output shapes, dead hook systems deleted, hooks-crossplatform.yml |
| limits-and-quick-fixes | specweave `codex/2.0-limits-fixes` | advisory limits, package.json main removal, doctor version check, .gitignore additions, `specweave gc` |
| templates-merger | specweave `codex/2.0-templates` | v2 templates, merger rewrite (delete removed sections, legacy strip, migration note, idempotent), stack detector, AGENTS.md for every project |
| sync-collapse | specweave `codex/2.0-sync` | `specweave sync` verbs, #1925, queue removal, dead modules, one `sw:sync` skill |
| task-ledger-verify | specweave `codex/2.0-ledger` | ledger.jsonl + `specweave task`, `specweave verify`, closure gate, 1-page handoff, do/done/team-lead/handoff skills |
| crawler-breadth | vskill-platform `feat/crawl-breadth` | 0874 merge, sourcegraph two-phase, known-key cache, topic repo search, result contract, tests in CI |

Wave 2 (after wave-1 merge): skills consolidation (delete deprecated/zero-use skills, `sw:review` from grill+code-reviewer+judge-llm, skill lint), config 2.0 migration, doctor 2.0, docs-site updates, standalone vskill skills (sw-task, sw-handoff, sw-increment, sw-do, sw-review).

Wave 3: adversarial review workflow over all diffs (find → refute), fixes, merge to develop/main, version bumps (specweave 2.0.0 major; vskill 1.0.22; desktop 1.0.63), publish, install, `specweave update` on umbrella + sw-easychamp, close issues/PRs, memory + Obsidian notes, video script notes.

## Merge order (specweave)
templates → hooks → limits → ledger → sync (sync deletes skills the ledger stream rewrites only in disjoint dirs; both delete the same stale shell-hook tests — identical deletions merge cleanly). Resolve conflicts preferring the later stream for shared files (bin/specweave.js registrations, hook-router.ts).

## Risks
- Session token limits kill builders mid-flight → resume the workflow (cached results) or rerun single streams.
- Windows changes to src-tauri cannot be compiled locally → rely on the rust-windows CI job before releasing the desktop.
- vskill-platform: release-desktop.sh redeploys the platform from the working tree; diff live vs git before any deploy (see memory project_desktop_release_prod_git_divergence).
- npm publish for vskill needs OTP (skill npm-publish-otp); specweave uses OIDC trusted publishing (tag push).

## Decisions
- Keep spec.md + optional plan.md; tasks.md = definitions; ledger.jsonl = the only mutable state (append-only, merge=union).
- No intent.md file: the Problem section of spec.md is the intent for a solo founder.
- Closure gate = `specweave verify` result (or `--reason`); grill/code-review/judge reports become optional evidence.
- Living docs generation off by default (`livingDocs: false`); ADRs stay hand-written.
- Hooks are accelerators for Claude Code only; the protocol must be complete with files + git + shell.
