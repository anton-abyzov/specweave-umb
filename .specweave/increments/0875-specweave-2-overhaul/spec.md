# 0875: SpecWeave 2.0 overhaul

## Problem

SpecWeave's instruction files, hooks, config and skill surface grew for a year without pruning. The 328-line CLAUDE.md template and 460-line AGENTS.md template contradict the Anthropic AI-Native SDLC playbook (under one page; procedures in skills; hard rules in hooks), every plugin hook is `bash -c` (dead on native Windows), the closure pipeline blocks on three review reports that only 33% of real increments ever produced, and a hard WIP cap makes every project permanently "non-compliant". Skill Studio (vskill desktop) fails to boot on Windows because the sidecar bundle is truncated by a cmd.exe shim. A supply-chain payload was injected through CI autofix workflows in July 2026 and the enablers are still in place. Anton works on 9 projects with several agents/subscriptions in parallel and needs a minimal, tool-agnostic loop with a handoff artifact.

## Scope

In: specweave (templates, merger, hooks, ledger/task/verify CLI, closure gate, WIP cap removal, sync collapse, dead-code removal, config 2.0, doctor, skills consolidation), vskill (Windows sidecar fix, logging, CI smoke, security), vskill-platform (security, crawler breadth), umbrella CLAUDE.md regeneration, release of specweave 2.0.0 + vskill + desktop.
Out: intent.md as a separate artifact, evals suite, guards config (2.1), Jira/ADO features beyond push/close.

## Acceptance criteria

- [ ] AC-01 CLAUDE.md and AGENTS.md templates are under one page (managed block ≤ 90 lines), show the tasks.md and ledger line formats, contain no bash-only syntax, and AGENTS.md is generated for every project.
- [ ] AC-02 `specweave update` on a 1.x install (SW:META or legacy file) produces a 2.0 file with all user content preserved, removed sections deleted, a one-time migration note, and is idempotent on a second run (unit + umbrella smoke).
- [ ] AC-03 Plugin hooks are exec-form node commands (no `bash -c`), emit schema-valid JSON for every event, Stop drives only the auto loop, timeouts are ≤ 60 s, and the launcher passes on ubuntu/windows/macos CI.
- [ ] AC-04 No hard WIP cap anywhere: 10 active increments produce one advisory note and no error; `revert-wip-limit` and TYPE_LIMITS are gone.
- [ ] AC-05 `specweave task next|claim|done|skip|release|list|render` + `ledger.jsonl` (append-only, merge=union, BOM/CRLF tolerant) work from any tool; `specweave verify` writes reports/verify.json; `specweave complete` gates on it (or `--reason`, `--all --reason`) and no longer requires grill/code-review/judge reports.
- [ ] AC-06 Handoff doc is ≤ 1 page with agent id, ledger table, next step, decisions, uncommitted-work pointer; single location `increments/<id>/handoff.md`.
- [ ] AC-07 Sync surface is `specweave sync push|pull|status|setup` + one `sw:sync` skill; issue #1925 fixed; queued mode and zero-importer modules removed.
- [ ] AC-08 Skill Studio Windows: sidecar bundle built via esbuild JS API, `node --check` + runtime smoke in build scripts and CI (windows/macos/ubuntu green), real per-OS log directory shown and written, Windows process control implemented.
- [ ] AC-09 Security: committed `.npmrc` ignore-scripts in all three repos, CI installs with `--ignore-scripts`, autofix agent workflows disabled, supply-chain scan workflow on every PR, PAT env files untracked, dependabot cooldown.
- [ ] AC-10 Crawler: sourcegraph stream unblocked, known-key cache, topic-based GitHub repo search, dead sources removed, crawl-worker tests run in CI.
- [ ] AC-11 PR #1902 intent applied (no `main` field), PR #1924 merged, poisoned PRs/branches closed, issues #1847/#1925 closed with the release.
- [ ] AC-12 Plugin skills reduced to the 10-skill core with no `name:` frontmatter, `sw:review` merged from grill/code-reviewer/judge-llm, skill lint passing; standalone vskill skills published.
- [ ] AC-13 specweave 2.0.0 published (OIDC), installed globally, `specweave update` run on the umbrella producing the 2.0 CLAUDE.md; vskill + desktop released with the Windows fix and the Windows smoke job green.

## Approach

See `plan.md` (waves, merge order, risks) and `reports/design-2.0.md` (agreed concept, rev 2 after the judge panel). Evidence: `reports/audit-digest.md`.

## Open questions

- PAT rotation for the crawl-worker env files can only be done by the owner (GitHub settings); the release will untrack the files and request rotation.
- Parallels license is expired; Windows verification runs on GitHub Actions only.
