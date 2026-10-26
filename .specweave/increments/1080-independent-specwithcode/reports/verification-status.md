# Verification and pending publication

Product head: 078bb6ee6f; templates/site head: 9f8886da0. Fresh-context review: approved after post-format assertion correction.

Passing: 36 instruction template/writer tests; 22 third-party notice generator tests; 8 post-commit runtime/npm packaging tests; 9 helper archive tests; 11 docs tests (2 existing skips); 4 source-terms audit checks. Actual generated inherited notice is intact in server, web, desktop and mobile manifests. CLI production build, docs production build, SEO and headless Chrome verification of /code/ and /code/download/ pass. Browser receipts and screenshots are adjacent.

Full unit coverage attempt after building, with four workers: 10426 tests passed, 20 failed, 77 skipped; 529 files passed, 5 failed, 5 skipped. The three deterministic assertions in require-increment and from-repo-project-root also fail on unchanged base 87fc56226. Remaining failures are Git/handoff timeouts and a POSIX helper-process fixture race. The broad coverage close gate is not satisfied. Do not mark the increment complete or weaken tests.

Full brand audit: same four failing categories on unchanged base c42d2cadd4692deb232b8c848afd6b42c07c9650 and changed tree. Required inherited MIT bytes pass exactly. All scoped identity and licensing checks pass.

PRs pending checks/merge:
- https://github.com/anton-abyzov/specwithcode-dev/pull/786
- https://github.com/anton-abyzov/specweave/pull/2153

Public sanitized snapshot prepared locally at /tmp/swc-public-identity, commit 105ff3bc, based on public main ebd518c7. It has passed mirror private-value checks and the updated test file passed the commit secret scan. It is NOT pushed; do not overwrite a newer public release. Before publishing, fetch both remotes, confirm private PR merged and public main unchanged, then fast-forward push only. Never force-push. Rebuild the snapshot from latest merged private main if either changed. Releases and release tags must remain untouched for this docs/source change.

Source policy and spec are committed on local umbrella branch codex/specwithcode-independent (de4934d4c). The shared umbrella working directory has the new AGENTS.md/CLAUDE.md policy and copied 1080 spec/ledger, preserving all unrelated dirty work. The umbrella has existing unpushed commits owned by other sessions; do not push its whole history as part of this task.

Next: wait for exact-head PR checks; diagnose any failures without taking over other owners' lanes; merge green PRs, publish the sanitized public snapshot with fast-forward only, verify public README/license metadata and live docs deployment. Complete T-03 only after publication; keep increment open until the mandatory coverage gate is resolved.
