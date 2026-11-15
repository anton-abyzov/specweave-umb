# specweave umbrella

Work is planned as SpecWeave increments in `.specweave/increments/NNNN-slug/` (`spec.md`, `ledger.jsonl`). `specweave pickup` prints the next task; the sw-* skills carry the loop (plan, do, review, done, handoff).

## Rules

- Nested repos live under `repositories/anton-abyzov/<repo>/`. Commit inside the nested repo, then the umbrella. Task `Files` are written from the umbrella root (`repositories/anton-abyzov/specwithcode/apps/server/...`).
- The app has one repository and one checkout: `repositories/anton-abyzov/specwithcode`. `specwithcode-dev` is retired; never recreate it.
- Nothing new goes directly in `~/Projects/github`. Scratch and logs: `~/.specwithcode/m4/scratch/<date>-<task>/`. Evidence: the increment's `reports/`, else `~/.specwithcode/m4/evidence/<topic>/`. Old evidence: `/Volumes/SanDisk APFS/Archive/specwithcode/`.
- A scratch copy of a repository is yours to remove once its PR merges or closes. Before removing any folder, check no thread is bound to it (`specweave-studio db query`). Never symlink another checkout's `node_modules`.
- Usage readings never stop work here: no handoff at any threshold (owner's rule, October 10, 2026).
- Merge green PRs, release, deploy and verify without asking. Ask before discarding work that exists nowhere else, and for data migrations, auth changes and payment flows. `claude-review` and `E2E Live (nightly)` never block.
- Releases: `bash scripts/release/release.sh status|ship|verify|cleanup <track>`; runbook `.specweave/release/README.md`. App releases: `bash scripts/release/request-release.sh --by "<thread>"` in the app repository; never pick or dispatch a version.
- Waits: never hold a call on CI or a registry for more than 540s; use `bash scripts/release/ci-wait.sh` (exit 2 means call again).
- SpecWithCode is an independent product: never market it as a fork, keep third-party notices and existing license grants, add no project-wide license grant.
- Files stay under 1,500 lines. Use Node 22 and SpecWeave 3.1.21 or newer.

## Commands

| Action | Command |
|---|---|
| Build | `npm --prefix repositories/anton-abyzov/specweave run build && npm --prefix repositories/anton-abyzov/vskill run build && npm --prefix repositories/anton-abyzov/vskill-platform run build` |
| Test | `npm --prefix repositories/anton-abyzov/specweave run test:unit:fast && npm --prefix repositories/anton-abyzov/vskill test && npm --prefix repositories/anton-abyzov/vskill-platform test` |
| Lint | `npm --prefix repositories/anton-abyzov/specweave run lint:skills && npm --prefix repositories/anton-abyzov/specweave run lint:docs-refs && npm --prefix repositories/anton-abyzov/vskill run lint:skills-spec` |
| Fleet checkout safety | `python3 scripts/fleet-project-sync.py --self-test` |
| Handoff verifier | `python3 -m unittest discover -s tests -p test_handoff_evidence.py` |
| Release tooling | `python3 scripts/release/timing.py --self-test && bash scripts/release/release-self-test.sh` |

The platform has no ESLint command; never claim a clean platform lint run.
