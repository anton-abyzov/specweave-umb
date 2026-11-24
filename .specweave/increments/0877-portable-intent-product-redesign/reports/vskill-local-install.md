# vskill 1.1.1 installed locally — T-17

Installed the rebuilt package from `/tmp/vskill-0877-release` commit `0e18781`. `vskill --version` now prints `1.1.1`, and the global installation is a real npm package directory rather than the prior development symlink. The final installation was replaced with published npm vskill 1.1.1 after workflow 34814057433 attempt 2 succeeded. All 758 installed package files match the registry tarball byte-for-byte.

## Backup and installation

Previous version: 1.1.0, linked to `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill`. Rollback package, original package/bin symlinks, metadata, and instructions are in `~/.codex/skill-backups/0877/vskill-1.1.1-local-install/` (directory mode 0700). Both old and new tarballs contain the CLI and Studio UI entrypoints. See `vskill-local-install-manifest.json` for the installed tarball digest.

The first preflight correctly rejected stale compiled output after the nested-scope repair. Rebuilt the CLI and Studio UI, then passed the package preflight (758 entries). Restored the build-generated timestamp-only `agents.json` working-tree change afterward.

Installed with `npm install --global --ignore-scripts --no-audit --no-fund <absolute-tarball-path>` as a defensive lifecycle precaution. The existing vskill `preuninstall.cjs` removes `~/.claude/plugins/cache/specweave` when invoked directly. A disposable npm 10.9.3 uninstall with scripts enabled did not invoke it and preserved the cache sentinel; this is not evidence that ordinary npm 10.9.3 uninstalls execute that script. Verified all 684 existing files/symlinks in that shared SpecWeave plugin cache remained unchanged by content hashes/link targets. No other global skills or user configuration changed.

## Verification

- CLI version: `1.1.1`.
- Rebuilt CLI and Studio; package preflight passed.
- Installed package started its own compiled loopback eval server in an isolated temporary home/project; `/api/health` returned `{ok:true}`.
- Headless Chromium rendered the packaged Skill Studio and fixture skill, with navigation to that skill’s detail route. Script: `vskill-local-install-smoke.py`; screenshot: `artifacts/vskill-installed-1.1.1-studio.png`.

The signed-out UI repeatedly requests optional `/api/v1/account/repos` and gets 401 responses. This pre-existing behavior keeps network-idle waits from settling, so verification uses DOM readiness and explicit content/navigation assertions. It is recorded as a limitation, not repaired or claimed as a fully clean account flow. No model evaluation, account login, publishing, or other paid operation was performed.

Build, preflight, install, and headless smoke output are saved beside this report with the `vskill-local-install-` prefix. This installation is ready for a fresh CLI process; an already-running Skill Studio continues using its old loaded code until restarted. No running user Studio was terminated.

## Final registry verification

Reinstalled `vskill@1.1.1` from the public npm registry with `--ignore-scripts --no-audit --no-fund`, preserving refreshed SpecWeave caches and user settings. Verified all 758 package files against the downloaded registry tarball. Compared with the headlessly tested local build, only the generated timestamp in `agents.json` differs; semantic agent data, CLI implementation, and every Studio asset are identical. No additional account-flow test was claimed. All 626 refreshed SpecWeave plugin/config files remained unchanged. Evidence: `vskill-registry-install-verification.json` and `vskill-registry-install.log`; public tarball preserved under the private backup’s `registry/` directory.
