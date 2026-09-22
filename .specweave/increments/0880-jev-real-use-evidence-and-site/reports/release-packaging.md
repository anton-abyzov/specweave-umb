# npm release packaging audit

## Finding

The `npm@12.0.2` warning `"bin[specweave]" script name bin/specweave.js was invalid and removed` is misleading for this package. The original `./bin/specweave.js` path is valid. npm normalizes it to `bin/specweave.js`, emits the warning on a changed string, then assigns the normalized value back to `pkg.bin[base]`. It does not delete the mapping in this branch.

Verified against the **actual npm12.0.2 distribution** downloaded from the official registry. Running its bundled `@npmcli/package-json/lib/normalize.js` on the SpecWeave mapping produced:

```json
{
  "name": "specweave",
  "version": "2.2.3",
  "bin": { "specweave": "bin/specweave.js" }
}
```

The warning was returned simultaneously. Current upstream source shows the same behavior at lines64–67: https://raw.githubusercontent.com/npm/package-json/main/lib/normalize.js . The official package.json docs define bin as command-name → local-file mapping: https://docs.npmjs.com/files/package.json/ . Exact npm distribution: https://registry.npmjs.org/npm/-/npm-12.0.2.tgz .

## Publication state

GitHub run35682396681 explicitly logged at **2026-09-22T03:17:43.439Z**: `Your package is being processed and may take a few minutes to become available.` It then printed `+ specweave@2.2.3`. That establishes upload acceptance, not public registry availability.

Registry probes at03:19:52Z and03:23:14Z returned404 for the exact version. The first package-wide manifest still showed latest2.2.2. Therefore, these probes cannot prove the published2.2.3 manifest or installed registry package. The root agent owns subsequent readiness checks and final installation.

## Local installability proof

The built `0880-release` checkout was packed with npm, its **actual tarball package.json** inspected, then installed into a fresh temporary project with dependency lifecycle scripts disabled. The generated `node_modules/.bin/specweave` command ran successfully and printed `2.2.3`. This proves local candidate installability, not public registry availability. No package was published or tag changed by this lane.

## Hardening patch

Commit `267edec84` adds:

- Actual tarball metadata validation plus clean install and CLI invocation to the existing publish preflight. File presence alone no longer passes the gate.
- A post-publish gate that waits at most40 registry attempts,15s apart, verifies exact package/version/bin metadata, downloads and verifies the published tarball integrity, then clean-installs and invokes the linked command. GitHub release/success steps run only after it passes.
- Exact npm12.0.2 pin instead of unbounded `npm@latest`.
- Nine unit tests covering missing/normalized bin mappings, wrong identity, missing manifest,404 processing, bounded failure and missing integrity.

Validation: all9 release tests passed; `git diff --check` exits0; clean install smoke passed. Existing2.2.3 tag remains untouched. No evidence from this warning alone justifies publishing2.2.4.

## Final public verification and follow-up fixes

At03:25:28UTC the exact version manifest became200 with `bin.specweave = bin/specweave.js`. The canonical tarball URL still returned cached404 after the cache-busted URL had propagated. Additional commits `5e9cd4abc` and `4f70b8de1` add bounded retries for tarball availability separately from metadata, retry transient transport failures, and use a unique query per attempt to bypass stale negative CDN responses. Integrity is still checked against the registry digest after download; corrupt bytes never qualify as ready.

The same follow-up removes direct `.cmd` execution on Windows. npm is launched through Node and its CLI JavaScript path; the installed command shim must exist, and Windows executes the declared installed entry through Node. Unix runs the linked CLI directly. Native Windows execution was not available in this session, so Windows support is source-reviewed rather than empirically verified.

Fresh public check completed successfully at03:27UTC: `node scripts/release/verify-package-install.mjs --published 2.2.3` downloaded the registry artifact, verified its digest and packed manifest, installed it into a new temporary project, and printed **`[install-check] packed bin preserved; clean installed specweave --version = 2.2.3`**. Final release unit suite: **12/12 tests passed**, including separate manifest/tarball propagation, bounded retries, transport failure and integrity rejection. Root independently installed the same version globally and holds the final machine-install receipt.

Independent review of site commit `ea14b5b56` and Chromium CI commit `1c4136000`: no actionable findings. The candidate-link regression was rerun under Node22 and passed (new canonical candidate route succeeds; missing candidate and external routes fail). CI installs Chromium before the unit suite that includes the navigation regression, with headless environment flags and the existing Node22 setup.

## Interrupted download review follow-up

Independent review found that HTTP200 headers could precede a body-read socket failure, outside the retry boundary. T-12 commit `a1d13ede8` moves JSON/body consumption inside that boundary and restores the tarball request's60-second timeout (metadata retains15 seconds). Integrity comparison remains outside retries, so corrupted complete downloads fail immediately. New tests use real `ReadableStream` errors for mid-body TypeError and AbortError, followed by a valid response, plus an interrupted manifest body. Final release tests: **15/15 passed**.
