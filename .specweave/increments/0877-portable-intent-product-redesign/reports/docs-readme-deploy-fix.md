# T35 — README links in the deployment build

## Confirmed failure

Documentation Build run [34819544079](https://github.com/anton-abyzov/specweave/actions/runs/34819544079), PR1940 head `991f29e0b51c71acaefe4c85ee0a882ca02d825c`, failed in Docusaurus's strict link validation. The workflow checks out the PR merge revision, copies `README.md` into `docs-site/docs/overview/readme.md`, adds frontmatter, and builds (`.github/workflows/docs-build.yml:39–50`). The two relative repository links become broken site routes:

- `README.md:81`: `plugins/specweave/marketplace.json` resolves to `/docs/overview/plugins/specweave/marketplace.json`.
- `README.md:175`: `SECURITY.md` resolves to `/docs/overview/SECURITY.md`.

The Pages deployment workflow repeats the same copy and build (`.github/workflows/deploy-docs.yml:55–66`), so this is a real deployment blocker. It is unrelated to inherited docs unit-test failures. Previous local strict-build verification omitted the generated README, so it did not reproduce the complete workflow; its success does not negate this CI failure.

## Narrow repair

T35 owns only `README.md`. Replace the two relative destinations with their existing, canonical GitHub `develop` URLs. Both files were independently verified through GitHub's Contents API before editing:

- `https://github.com/anton-abyzov/specweave/blob/develop/plugins/specweave/marketplace.json`
- `https://github.com/anton-abyzov/specweave/blob/develop/SECURITY.md`

These URLs remain meaningful both on GitHub and when the README is copied into the site. No change to test assertions, build strictness, link checker, workflow behavior, or dependencies.

## Validation

Isolated worktree `/tmp/specweave-0877-readme`, branch `codex/0877-readme`, based on `991f29e0b`. Dependency directories reuse the existing checkout's installed dependencies.

The macOS reproduction performs the same README copy plus identical frontmatter bytes as the workflow's GNU `sed` command, then runs `PWDEBUG=0 PLAYWRIGHT_HTML_OPEN=never npm --prefix docs-site run build`. No browser is needed for this source URL fix.

- **Red:** same pre-fix build failed locally with exactly the two CI destinations. Evidence: `docs-readme-local-red.log:50–53`; process exit 1. This was executed before changing `README.md`.
- **Green:** after the two URL changes, repeated the complete README copy/frontmatter step and identical strict build; process exit 0. Evidence: `docs-readme-local-green.log` ends with `Generated static files in "build"`. No broken-link or unresolved-Markdown warning remains.
- Parsed the generated `/docs/overview/` HTML: both exact absolute URLs appear as anchor destinations; neither relative destination remains. Confirmed the generated Markdown body is byte-for-byte the current root README after removing the workflow frontmatter.
- `git diff --check` and the normal malware/secret pre-commit scan passed. No test bypass used. No extra unit test was added for two reversible documentation URLs.
- Commit: `dc7db569e` (`0877: fix README links in documentation deployment`), exactly one tracked file changed, two insertions/two deletions. Generated `docs-site/docs/overview/readme.md` is untracked and intentionally excluded from the commit; installed dependency symlinks and built output are not committed.

Fix ready for parent review and cherry-pick. This task did not push, merge, or deploy.

## Separate Claude review failure

[Claude Code Review run34819544001](https://github.com/anton-abyzov/specweave/actions/runs/34819544001) has workflow conclusion **success** and job conclusion **failure** because `.github/workflows/claude-code-review.yml:24` already sets `continue-on-error: true`. The action initialized Claude Code v2.1.270 with model `claude-sonnet-5`, then returned `is_error:true` after 271ms, one turn, `modelUsage:{}`, and zero reported cost. It did not produce a code review or test findings.

An OAuth token was supplied and masked. The action hides the detailed result, and no execution-output artifact is available. The exact authentication, quota, model-access, or service error therefore remains **unknown**; an expired token cannot be asserted from these logs. The prior run34819182126 has the same early-failure signature (259ms, no model usage). The workflow itself is unchanged in this PR. This is an unavailable advisory review, not website build/runtime evidence. Existing independent human-style reviews remain separate evidence.

If this advisory review is repaired later, capture a narrowly redacted error code/message without enabling broad full-output logging, then repair the identified credential or service configuration. No speculative workflow or secret change was made in this task.
