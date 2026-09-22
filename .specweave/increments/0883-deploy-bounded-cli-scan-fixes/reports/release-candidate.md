# Release candidate 2.2.4

Source: `fe9db936dae5f865ddc92a5146c6dac423c0882d`, pushed to `codex/0883-bounded-scans-release`. Release PR: https://github.com/anton-abyzov/specweave/pull/1954.

Includes exact heads of fixes #1950 (`cb42dab31`) and #1951 (`26da1f117`), plus deployed stable 2.2.3 and verified delivery fixes from #1952 (`195d147a5`). #1952 was independently squash-merged to develop as `5728b69a0`; verified its tree matched `195d147a5` exactly, then merged that ancestry into the candidate without altering any files. The candidate tree equals tested commit `37e87a713`.

## Validation

Node 22.20.0. Full unit suite: 746 files passed, 16,803 tests passed, 155 pre-existing skips, exit 0. Build, version alignment, skill lint, documentation-reference lint, and bounded-scans CLI harness passed. Publish preflight validated 4,129 tarball entries and clean installed `specweave --version = 2.2.4`.

Installed local tarball at `/tmp/specweave-0883-package/install/node_modules/specweave`; complete bounded-scans harness passed against that installed package. `refresh-plugins` refused a synthetic bare `.specweave` directory with exit 1 in 88 ms; quiet mode returned exit 1 silently in 64 ms. No public publication or deployment proof is claimed yet. Global 2.3 RC installation was preserved.

Scoped umbrella evidence for 0879/0882 was pushed and merged via https://github.com/anton-abyzov/specweave-umb/pull/91, merge `9df72996a598eaa1e184982d40c33401656420ec`.

## Required gate

Ordinary merge of #1950 was rejected by GitHub branch policy. `develop` requires one approving review; the external Claude-review job fails before reviewing code. Await explicit authorization for administrator merge of consolidated PR #1954, or an actual approving review. No override used. Candidate Test & Validate run 35688195434 passed on retry: unit, E2E, smoke, and results. The first attempt hit a source-scan timeout and an LSP timing benchmark threshold; no tests were modified. Nine additional local domain-skill E2E failures reproduced exactly against develop 5728b69a0 with the adjacent vskill checkout (9 failed, 28 passed, 2 skipped), confirming they are baseline failures.

After permission/review: refresh PR head and checks, merge with full exact-head SHA, confirm #1950/#1951 merged, tag merged source `v2.2.4`, push tag and let release.yml publish, then verify npm latest, tarball integrity, clean installation, and both CLI harness and refresh guards against downloaded registry artifact. Record release/deploy run and close increment only after these gates pass.

## Coordinated stable release

The parallel portable-project task (01a0c712-f935-7de2-8285-15fc93773bae, PR #1953) is preparing stable 2.3.0 with explicit release authorization. It agreed to incorporate the complete scan fixes and preserve the newer version. Hold 2.2.4 publication and global installation to avoid replacing the newer release. This increment will independently verify the public 2.3.0 artifact when published; its release acceptance is fulfilled by that newer stable version containing all fixes. No publication proof yet.
