# 1247 history audit: specwithcode-dev and the public mirror

November 6, 2026. Read-only bare mirror clones of both GitHub repositories in `~/Projects/scratch/oss-audit/` (`dev.git`, `pub.git`); the shared checkout was not touched. gitleaks 8 (`--redact`); no secret value appears in this report or in the scan outputs.

## What GitHub holds today

| | `specwithcode-dev` (private) | `specwithcode` (public) |
|---|---|---|
| Commits reachable | 14,368 | 188 |
| Refs | 2,847, of which 1,467 are `refs/pull/*` | 205 |
| Stars, forks | 0, 0 | 4, 0 |
| Open PRs, secrets | 24 open PRs, 11 Actions secrets | none |
| Releases | v1.0.x published here | same releases, mirrored |

The public repository is fed by `scripts/public-mirror/publish.mjs`, run from `release-stage.yml` with the `PUBLIC_MIRROR_RULES` secret. It publishes one scrubbed snapshot commit per release: it drops an `EXCLUDE` list (workflows, `reports/`, fleet runbooks, research notes, brand audits), applies a private replace/deny list (6 replace and 6 deny values, kept at `~/.local/share/specweave/specwithcode-public/rules.json`), and strips upstream names except the MIT copyright line.

## Findings in specwithcode-dev history

1. gitleaks: 291 findings, 153 in vendored `.repos/` (third-party test fixtures) and 138 in SpecWithCode's own files (137 `generic-api-key`, 1 `aws-access-token`). Triage ([triage.md](triage.md)): none is a real secret, so nothing needs rotating. 69 are fake test values, 59 false positives (hashes, version pins, a token alphabet, keybinding names) and 10 public by design (Clerk `pk_live` publishable keys and a CLI OAuth client id). The `aws-access-token` hit is a fake key in a redaction test.
2. Private scrub-list values: 4 of the 6 deny values (values that must never ship) appear in 12, 12, 9 and 4 commits; the 3 replaced private values checked appear in 8, 10 and 12 commits. Counts only; values not printed.
3. Private paths and personal data on the `main` tip: 61 files contain `/Users/antonabyzov` (22 in `apps/web`, 17 in `reports/`), 7 files contain personal email addresses, 70 files under `reports/` (fleet receipts and verification logs). Authors' personal addresses (`@easychamp.com`, `@gmail.com`) are on 7,370 commits.
4. AI attribution: 1,567 commit messages carry a `Co-Authored-By` trailer for an AI tool, and 54 commits are authored by `Claude <noreply@anthropic.com>`. Anton's rule bans this from anything that leaves the machine.
5. T3 Code's full history (Theo Browne, Julius Marminge and about 100 contributors, from February 7, 2026) is reachable from non-main refs; `main` itself starts at `50254ce6e` (October 7, 2026, "0885: establish independent Studio identity"). That history is already public and MIT, so it is not a leak, but it includes a committed `apps/server/.t3/state.sqlite` and a `.pnpm-store` index from upstream.
6. `refs/pull/*`: GitHub keeps every PR head and merge ref read-only. A force-push or `git filter-repo` cannot remove them; only GitHub Support can purge them, one repository at a time. Making `specwithcode-dev` public exposes all 1,467 of them, including the commits in findings 2 to 4, no matter how `main` is rewritten.

## Findings in the public mirror

The mirror tip has 0 files with `/Users/antonabyzov`. gitleaks reports 115 findings (78 `generic-api-key`, 34 `private-key`, 2 `curl-auth-header`, 1 `jwt`), 75 in vendored `.repos/` certificate fixtures; the other 40 are the same test fixtures, false positives and public keys as above. None of the 12 private scrub-list values appears in any of its 188 commits, so its history is clean.

## Recommendation: fresh history in the existing public repository

Do not flip `specwithcode-dev` public, and do not rewrite it. Finding 6 makes a rewrite insufficient, and findings 2 to 4 make the real history unsafe to publish as is.

Instead, make `anton-abyzov/specwithcode` the development repository:

1. Land the license, docs and polish PRs in `specwithcode-dev` first, plus a cleanup PR that removes `reports/`, private paths, personal addresses and scrub-list values from the tree itself, so the source no longer depends on `publish.mjs` to be clean.
2. Commit that cleaned tree on top of the public repository's existing snapshot history as an ordinary commit ("Open source under MIT"). That needs no force-push, keeps the 4 stars and the release URLs that installed apps already poll (`anton-abyzov/specwithcode/releases`), and the history from then on is real development history.
3. Move the CI: copy the workflows, set the 11 Actions secrets and the variables on `specwithcode`, add branch protection, and switch `release-stage.yml` to publish releases there directly. Retire `publish.mjs`.
4. Re-open the 24 open PRs (or the ones still wanted) against `specwithcode`; archive `specwithcode-dev` as the private full-history record.

Rejected: flipping `specwithcode-dev` public (exposes PR refs, the scrub-list values and AI trailers); `git filter-repo` plus a force-push (PR refs survive, and every open PR, worktree and fleet checkout breaks); a brand-new repository (loses the stars and the release URL).
