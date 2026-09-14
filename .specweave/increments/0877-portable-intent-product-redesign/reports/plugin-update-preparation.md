# Plugin update preparation (read-only)

No package/plugin installation, removal or config mutation was performed. Parent must confirm npm 2.1.0 is published before applying these steps.

## Current installation

The active Node 22 global package is SpecWeave 2.0.0 at `/Users/antonabyzov/.nvm/versions/node/v22.20.0/lib/node_modules/specweave`. `specweave` resolves to that package. Its package, marketplace and plugin manifests all report 2.0.0.

Codex `sw@specweave` is enabled at user level; `codex plugin list --marketplace specweave --json` reports 2.0.0. Its configured marketplace is a local directory pointing to that global npm package. Active cached plugin: `~/.codex/plugins/cache/specweave/sw/2.0.0`. Hooks: SessionStart, PreToolUse, Stop, PreCompact. Preserve its locally patched `run.mjs`/worker backup before updating.

Claude `sw@specweave` is enabled in user settings and this umbrella's project settings. The user and current-project installed records both report 2.0.0 and share `~/.claude/plugins/cache/specweave/sw/1.0.0`; its actual hooks are the same four. Two other project records (`sw-jobs-umb`, `jobweave-umb`) report 2.0.0 but point to absent cache directory `1.0.591`; those are stale registrations, not additional active hook payloads.

User hooks are separate: Codex `~/.codex/hooks.json` and scripts; Claude user settings contain PreToolUse, SessionStart and UserPromptSubmit; project settings contain PostToolUse. Their contents must remain byte-identical through this focused plugin update.

## Concrete update path after publication

1. Make a private backup under `~/.codex/skill-backups/0877/pre-2.1.0-plugin-update/` (0700), outside all discovery roots. Preserve exact bytes and symlinks for Codex user/project config, Codex hooks.json, Claude user/project settings (including local variants), Claude installed_plugins.json and known_marketplaces.json, current SpecWeave user/project lock files, and both existing sw plugin cache payloads. Record source/backup paths and SHA-256 hashes. Do not place config contents in Git reports.
2. With Node 22 first in PATH, run `npm install -g specweave@2.1.0`. Confirm global package and plugin manifest versions actually changed to 2.1.0 and its hooks.json has exactly SessionStart and Stop before updating consumers.
3. Codex: `codex plugin add sw@specweave --json`. This is the installed CLI's supported installation surface; it has no `plugin update` command. The source is local, so `codex plugin marketplace upgrade` (Git snapshots only) is unnecessary. Check the returned result, then re-run `codex plugin list --marketplace specweave --json` and inspect actual 2.1.0 cache hooks. Reinstalling an existing ID across a version bump was not executed during read-only prep; if add leaves stale content, stop and diagnose before any removal. Do not directly rewrite Codex plugin registration state.
4. Claude: refresh the named local marketplace with `claude plugin marketplace update specweave`, then `claude plugin update sw@specweave --scope user --json` and, from this umbrella root, `claude plugin update sw@specweave --scope project --json`. This targets existing registrations and preserves unrelated plugins. Verify both relevant records and actual installPath contents; cache directory names alone are not evidence of version.
5. Compare backed-up independent hook/config content, inspect exact hook event sets, verify scripts exist, and record installed versions. Do not infer successful activation from npm output alone.

`specweave refresh-plugins --plugin sw --force` is supported, but broader than needed: under this project's `adapters.default=claude`, it refreshes all sw Claude installPath records and also runs lock migrations/stale plugin cleanup/user-to-project migrations. It does not update the native Codex plugin cache. `specweave update` additionally changes project instructions/config, so neither is the preferred focused update here.

## Restart/activation

Claude's actual `plugin update --help` explicitly says restart required. Start a fresh Claude session after updating.

For Codex, official OpenAI documentation says bundled capabilities become available in a new chat or CLI session after installation: https://learn.chatgpt.com/docs/plugins. Use a new task/session after install; do not terminate the current release task. An entire desktop app restart was not established as necessary. Generated local app-server protocol also distinguishes plugin bundle reconciliation from runtime-readiness acknowledgment, so a changed cache alone is insufficient proof that the current running task switched hook definitions.

## Independent vskill release review

Commit `010a49a38093a59cc3ef6d5c79641c235e884477` closes the reviewed HIGH nested deletion issue. The nearest lockfile boundary consistently controls lock read/write, per-agent paths, canonical payload guard and Claude project subprocess cwd. An unreadable or malformed child lock is still an ownership boundary, preventing fallback to an ancestor's install. Source and disposable ownership tests were independently reviewed/run.

`npx vitest run src/lockfile/local-root.test.ts src/commands/__tests__/remove-ownership.test.ts src/commands/__tests__/cleanup-scope.test.ts src/commands/remove.test.ts --maxWorkers=4` under Node 22: 4 files / 33 tests pass (`vskill-final-independent-review-tests.log`).

The npm workflow checks tag/package agreement, uses Node 22, runs the full test suite, builds CLI and Studio, validates the packed artifact and publishes through `npm run release` which forces lifecycle scripts on. Missing or stale build artifacts are rejected before publish. No new release blocker found in this bounded workflow review. Live npm auth/publish outcome remains the release owner's responsibility.
