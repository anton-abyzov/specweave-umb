# SpecWeave 2.1.0 local package and native plugins — T-24

**Installed and verified SpecWeave 2.1.0.** Global CLI prints `2.1.0`. Native Codex and every existing Claude `sw@specweave` registration now resolve to actual 2.1.0 cache contents with exactly **SessionStart** and **Stop**. PreToolUse and PreCompact are absent from those current cache manifests.

## Package and backup

Installed from the rebuilt `/tmp/specweave-0877-root` source at `8052b9bd9`. Release preflight passed with 4125 packaged entries, including CLI, dashboard, runtime modules, and plugin manifests. The tarball manifest/digest is in `specweave-local-install-manifest.json`. The final installation was then replaced with the published npm registry package after trusted publication succeeded (workflow run 34816047820). All 4125 installed package files match the downloaded registry tarball byte-for-byte; its SHA-256 also exactly matches the tested local tarball. See `specweave-registry-install-verification.json`.

Private rollback directory: `/Users/antonabyzov/.codex/skill-backups/0877/pre-2.1.0-plugin-update/`, mode 0700. `before.tar.gz` (15,370,152 bytes, mode 0600) preserves 19 original paths, including the complete global 2.0.0 package/dependencies, bin link, original Codex/Claude sw caches and registries/configs. A supplemental archive preserves the other two projects’ settings. `ROLLBACK.md` explains exact package restoration without overwriting later unrelated configuration changes. The old locally patched Codex hook implementation is preserved in the archive.

Installation used `npm install --global --ignore-scripts --no-audit --no-fund <built-tarball>` as a defensive lifecycle precaution. The existing vskill `preuninstall.cjs` removes the shared SpecWeave cache when invoked directly, but a disposable npm 10.9.3 uninstall with scripts enabled did not invoke it and preserved the cache sentinel. This is not evidence that ordinary npm 10.9.3 uninstalls execute that script.

## Native updates

- Codex: `codex plugin add sw@specweave --json`; subsequent native list reports 2.1.0 enabled. Actual cache: `~/.codex/plugins/cache/specweave/sw/2.1.0`.
- Claude: `claude plugin marketplace update specweave`, then `claude plugin update sw@specweave --scope user --json -y` and scoped project updates from the three existing registered project directories: `specweave-umb`, `sw-jobs-umb`, and `jobweave-umb`. The latter two had broken registrations pointing to missing `sw/1.0.591`; both are repaired. All four records now point to `~/.claude/plugins/cache/specweave/sw/2.1.0`.
- Independent Codex/Claude configuration and hook files are byte-identical to backup, including the two additional projects’ settings. All five unrelated Claude plugin registration entries remain identical.

The four actual cached hook invocations (SessionStart and Stop in each harness cache) exit 0 without stderr against a disposable fixture. Both SessionStart invocations discover its pending lightweight intent. No model calls.

## Installed dashboard verification

Started the installed compiled dashboard package against the real `specweave-umb` project, with browser opening and server hook execution disabled. Headless Chromium loaded the board, concrete populated cards, and live workspace connection. All requests were read-only; non-GET/browser external requests were blocked by the verification harness. No intent or ledger writes, no model calls, no page errors, no failed HTTP requests.

The final registry-package capture reported 257 items (17 backlog, 6 active, 1 blocked, 14 review, 219 done) and 3219/3633 tasks complete. These are local file projections at capture time; they are not fabricated completion or verification. Native log polling is supported for the implemented adapters; this does not claim automatic coverage of every harness or model.

Screenshot: `artifacts/installed-dashboard-real-project.png`. Repro script and output: `specweave-local-install-dashboard-smoke.py` / `.log`. Native update and hook smoke evidence are saved alongside this report.

**Activation:** use a fresh Codex session and restart Claude to ensure loaded plugin runtimes use the updated caches; Claude’s native command explicitly reports a restart is required. The current skill catalog points to sw 2.1.0, which does not establish that every running hook process has reloaded. Restart an already-running dashboard to load the installed code. No user session was terminated.

Final registry reinstallation used the same defensive lifecycle flag and an anonymous public-registry config. All 626 refreshed plugin/config files remained unchanged. The populated real-project screenshot was refreshed from the published installed package; `specweave-registry-dashboard-smoke.log` records zero page errors, HTTP failures, mutation requests, and model calls.
