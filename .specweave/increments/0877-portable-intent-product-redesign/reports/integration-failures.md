# Integration failure audit and fix

Source commit: `2776db874c37f493bd28bbbb9cd0f9e57ad04a4d` in `/tmp/specweave-0877-sync` (SpecWeave 2.0.3 base). No version bump or remote tracker writes in this lane.

## Proven defect

`ExternalChangePuller` caught authentication, transport and provider errors and returned an empty array. `specweave sync pull` then printed “No external changes”, indistinguishable from a successful empty fetch. If one provider failed while another succeeded, callers could not distinguish incomplete data.

The new regression suite initially produced six failures and two passes; see `sync-pull-regressions-before-fix.log`.

## Changed behavior

- A complete successful fetch retains the existing `ExternalChange[]` return type.
- An incomplete fetch throws `ExternalPullError` with successful changes, failed providers and completed providers. Successful changes stay sorted by date. Provider error messages use the existing credential scrubber.
- The CLI prints failed providers, retains and labels successful partial results, and exits nonzero. It never prints “No external changes” after a provider failure.
- Explicit configured GitHub owner/repository takes precedence over the checkout remote. Missing GitHub target is an actionable failure rather than an empty success.
- These paths do not write synchronization cursors or checkpoints. Regression tests and a real built CLI smoke check verify that project files remain unchanged, so an incomplete pull cannot advance local state.

## Validation

Node 22.20.0, no browser or remote provider writes:

- Final targeted run: 4 files, 27 tests passed (`sync-pull-tests.log`).
- Broader sync suite: 51 files, 894 tests passed (`sync-pull-broad-tests.log`). Two additional target-routing/error aggregation tests were added afterward and passed in the final targeted run; production implementation was unchanged.
- Targeted coverage: 93.18% lines, 91.08% statements, 76.03% branches, 84.78% functions across the two changed source files (`sync-pull-coverage.log`).
- TypeScript compilation and full `npm run build` passed (`sync-pull-build.log`).
- Built CLI smoke test in a disposable project with GitHub enabled but no target/remote: exit 1, explicit missing-target error, no empty-success text, all project file hashes unchanged (`sync-pull-cli-smoke.json`).
- `git diff --check` and precommit security checks passed.

## Integration decision and limits

Keep GitHub, Jira and Azure DevOps as optional enterprise adapters. They remain useful for existing team accountability and tracker context; they must not be the authoritative store for agent progress or block local intent tracking. This fix makes an existing failure mode visible without adding another adapter layer.

This patch does not redesign conflict resolution, retry policy, tracker field mapping or pagination. Existing provider fetch limits remain. The smoke check proves local error reporting and non-mutation; it does not claim live authentication or successful remote synchronization was exercised. Parent release work owns versioning, integration and deployment.
